#!/usr/bin/env python3
"""
Load Rosetta's sample metadata into a LIVE DataHub instance.

This is the one command that turns an empty `datahub docker quickstart` into a
graph Rosetta can scan for real. It ingests the six sample metric definitions
(demo_data/seed_definitions.json) as glossary terms, the datasets they annotate,
and the lineage edges between them (demo_data/lineage.json) so that Rosetta's
blast-radius walk has real downstream assets to traverse.

Usage
-----
    export DATAHUB_GMS_URL="http://localhost:8080"
    export DATAHUB_GMS_TOKEN="<personal access token, if auth is enabled>"
    python scripts/ingest_seed_to_datahub.py

Then verify and run Rosetta against the live graph:

    python -m rosetta.orchestrator --check-connection
    python -m rosetta.orchestrator --report --live
    python -m rosetta.orchestrator --apply  --live      # writes canonical terms back
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "demo_data"


def _require_env() -> str:
    url = os.environ.get("DATAHUB_GMS_URL")
    if not url:
        sys.exit(
            "DATAHUB_GMS_URL is not set. Start DataHub with "
            "`datahub docker quickstart` then run:\n"
            "  export DATAHUB_GMS_URL=http://localhost:8080"
        )
    return url


def main() -> None:
    url = _require_env()
    token = os.environ.get("DATAHUB_GMS_TOKEN")

    # Imported here so the script gives a friendly message if the SDK is missing.
    try:
        from datahub.emitter.mcp import MetadataChangeProposalWrapper
        from datahub.emitter.rest_emitter import DatahubRestEmitter
        from datahub.metadata.schema_classes import (
            DatasetPropertiesClass,
            GlossaryTermInfoClass,
            UpstreamClass,
            UpstreamLineageClass,
            DatasetLineageTypeClass,
        )
    except Exception as exc:  # pragma: no cover
        sys.exit(f"acryl-datahub not installed ({exc}).\n  pip install acryl-datahub")

    emitter = DatahubRestEmitter(gms_server=url, token=token)

    rows = json.loads((DATA / "seed_definitions.json").read_text())
    lineage = {
        k: v
        for k, v in json.loads((DATA / "lineage.json").read_text()).items()
        if not k.startswith("_")
    }

    # 1) Glossary terms (one per team's definition).
    n_terms = 0
    for r in rows:
        term_urn = r.get("term_urn") or f"urn:li:glossaryTerm:{r['name']}_{r['domain']}"
        mcp = MetadataChangeProposalWrapper(
            entityUrn=term_urn,
            aspect=GlossaryTermInfoClass(
                name=r["display_name"],
                definition=r["definition_text"] or r["display_name"],
                termSource="INTERNAL",
            ),
        )
        emitter.emit(mcp)
        n_terms += 1

    # 2) Datasets referenced anywhere (as sources or lineage nodes).
    all_urns: set[str] = set()
    for r in rows:
        all_urns.update(r.get("source_urns", []))
    for parent, children in lineage.items():
        all_urns.add(parent)
        all_urns.update(children)
    dataset_urns = [u for u in all_urns if u.startswith("urn:li:dataset:")]
    for urn in dataset_urns:
        name = urn.split("(", 1)[-1].rstrip(")").split(",")
        display = name[1] if len(name) > 1 else urn
        emitter.emit(
            MetadataChangeProposalWrapper(
                entityUrn=urn,
                aspect=DatasetPropertiesClass(name=display, description="Seeded by Rosetta"),
            )
        )

    # 3) Lineage edges (parent -> child) so downstream walks have real paths.
    n_edges = 0
    downstream_of: dict[str, list[str]] = {}
    for parent, children in lineage.items():
        for child in children:
            downstream_of.setdefault(child, []).append(parent)
    for child, parents in downstream_of.items():
        if not child.startswith("urn:li:dataset:"):
            continue
        ups = [
            UpstreamClass(dataset=p, type=DatasetLineageTypeClass.TRANSFORMED)
            for p in parents
            if p.startswith("urn:li:dataset:")
        ]
        if not ups:
            continue
        emitter.emit(
            MetadataChangeProposalWrapper(
                entityUrn=child, aspect=UpstreamLineageClass(upstreams=ups)
            )
        )
        n_edges += len(ups)

    print(
        f"Ingested into {url}:\n"
        f"  glossary terms : {n_terms}\n"
        f"  datasets       : {len(dataset_urns)}\n"
        f"  lineage edges  : {n_edges}\n\n"
        "Next:\n"
        "  python -m rosetta.orchestrator --check-connection\n"
        "  python -m rosetta.orchestrator --report --live"
    )


if __name__ == "__main__":
    main()
