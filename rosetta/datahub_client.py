"""
Rosetta's read/write facade over DataHub.

This module talks to a REAL DataHub instance through the official acryl-datahub
Python SDK when one is configured, and falls back to the bundled demo graph
(demo_data/*.json) when no instance is reachable. That dual mode is deliberate:

  * Judges / users with a live DataHub (`datahub docker quickstart`) get genuine
    reads from the metadata graph and genuine write-back of canonical glossary
    terms. Nothing is faked.
  * The hosted demo and the unit tests run anywhere, with no warehouse, because
    they transparently fall back to the reproducible seed graph.

Rosetta reads context (glossary terms, column descriptions, lineage, ownership)
and WRITES BACK canonical glossary terms + deprecation notes. The write-back
loop is the point: the agent does useful work today, and the context platform
underneath gets richer every time it runs.

Configuration (all optional; absence => demo mode):
    DATAHUB_GMS_URL     e.g. http://localhost:8080   (turns on LIVE mode)
    DATAHUB_GMS_TOKEN   personal access token, if your instance requires auth
    ROSETTA_FORCE_DEMO  set to "1" to force demo mode even if a URL is present

SDK calls used (all from the official DataHub Python SDK):
    DataHubClient.from_env()                       -> modern entity client
    DataHubGraph(DatahubClientConfig(server=...))  -> GraphQL + read-modify-write
    client.entities.upsert(GlossaryTerm(...))      -> write canonical term
    client.entities.get(DatasetUrn(...))           -> read a dataset
    dataset.add_term(GlossaryTermUrn(...))          -> attach a term
    graph.execute_graphql(query=...)               -> read glossary + lineage
"""
from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

log = logging.getLogger("rosetta.datahub")

# --- Lazy SDK import ---------------------------------------------------------
# Imported lazily so unit tests and the hosted demo run without the SDK present.
try:
    from datahub.sdk import DataHubClient, DatasetUrn, GlossaryTermUrn
    from datahub.sdk.glossary_term import GlossaryTerm
    from datahub.ingestion.graph.client import DatahubClientConfig, DataHubGraph

    _HAS_SDK = True
except Exception:  # pragma: no cover - only in envs without the SDK installed
    _HAS_SDK = False
    DataHubClient = object  # type: ignore
    DatasetUrn = object  # type: ignore
    GlossaryTermUrn = object  # type: ignore
    GlossaryTerm = object  # type: ignore
    DatahubClientConfig = object  # type: ignore
    DataHubGraph = object  # type: ignore

_DATA_DIR = Path(__file__).resolve().parent.parent / "demo_data"


@dataclass
class MetricDefinition:
    """One team's understanding of a business metric."""

    name: str  # normalized name, e.g. "active_user"
    display_name: str  # raw label as it appears, e.g. "Monthly Active Users"
    domain: str  # owning domain, e.g. "finance"
    owner: str  # DataHub owner URN or team id
    definition_text: str  # human definition (glossary or column desc)
    sql_logic: str = ""  # inferred computation from historical SQL
    source_urns: list[str] = field(default_factory=list)  # assets that use it
    term_urn: str = ""  # existing glossary term URN, if any


def _live_url() -> str | None:
    """Return the configured GMS URL if LIVE mode should be used, else None."""
    if os.environ.get("ROSETTA_FORCE_DEMO") == "1":
        return None
    return os.environ.get("DATAHUB_GMS_URL") or None


class RosettaDataHub:
    """Read/write facade over DataHub for the Rosetta agents.

    Attributes
    ----------
    live : bool
        True if connected to a real DataHub instance; False if using seed data.
    gms_url : str | None
        The GMS URL in use when live, else None.
    """

    # Class-level defaults so instances built via __new__() (used in tests to
    # skip network setup) still have well-defined attributes.
    live: bool = False
    gms_url: "str | None" = None
    client = None
    _graph = None
    _lineage_cache: "dict | None" = None

    def __init__(self, client: "DataHubClient | None" = None) -> None:
        self.gms_url: str | None = None
        self.live: bool = False
        self.client = None
        self._graph = None
        self._lineage_cache: dict | None = None

        if client is not None:
            # Explicit client (used by tests and advanced callers).
            self.client = client
            self.live = True
            return

        url = _live_url()
        if url and _HAS_SDK:
            # Silence urllib3's connection-retry chatter during the probe; a
            # clean single warning from us is enough if the server is down.
            logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
            try:
                token = os.environ.get("DATAHUB_GMS_TOKEN")
                # Fail fast (short timeout, no retry storm) so that if the
                # instance is not up we fall back to the demo graph quickly
                # and quietly instead of hanging on retries.
                cfg = DatahubClientConfig(
                    server=url,
                    token=token,
                    timeout_sec=5,
                    retry_max_times=0,
                )
                self._graph = DataHubGraph(cfg)
                self._graph.test_connection()
                self.client = DataHubClient.from_env()
                self.gms_url = url
                self.live = True
                log.info("Rosetta connected to LIVE DataHub at %s", url)
            except Exception as exc:  # pragma: no cover - network dependent
                log.warning(
                    "DATAHUB_GMS_URL=%s set but connection failed (%s). "
                    "Falling back to demo graph.",
                    url,
                    exc,
                )
                self.live = False
        elif url and not _HAS_SDK:  # pragma: no cover
            log.warning(
                "DATAHUB_GMS_URL is set but acryl-datahub is not installed. "
                "Run `pip install acryl-datahub`. Falling back to demo graph."
            )

    # ---------------------------------------------------------------- helpers
    @property
    def mode(self) -> str:
        return "live" if self.live else "demo"

    # ---------------------------------------------------------------- READ
    def harvest_metric_definitions(self) -> list[MetricDefinition]:
        """Pull candidate metric definitions from the graph (Harvester agent).

        LIVE: queries DataHub's GraphQL API for glossary terms and their
        parent nodes / linked datasets, mapping each into a MetricDefinition.
        DEMO: seeds from demo_data/seed_definitions.json for a reproducible run.
        """
        if self.live and self._graph is not None:
            try:
                return self._harvest_live()
            except Exception as exc:  # pragma: no cover - network dependent
                log.warning("Live harvest failed (%s); using seed data.", exc)
        return self._harvest_seed()

    def _harvest_seed(self) -> list[MetricDefinition]:
        raw = json.loads((_DATA_DIR / "seed_definitions.json").read_text())
        return [MetricDefinition(**row) for row in raw]

    def _harvest_live(self) -> list[MetricDefinition]:  # pragma: no cover
        """Read glossary terms from a real DataHub via GraphQL.

        Each glossary term becomes a candidate MetricDefinition. The datasets
        that reference the term (via the term's relationships) become its
        source_urns, so the blast-radius walk has real anchors.
        """
        query = """
        query rosettaHarvest($start: Int!, $count: Int!) {
          searchAcrossEntities(
            input: { types: [GLOSSARY_TERM], query: "*", start: $start, count: $count }
          ) {
            total
            searchResults {
              entity {
                urn
                ... on GlossaryTerm {
                  properties { name description }
                  domain { domain { urn properties { name } } }
                  relationships(input: { types: ["TermedWith"], direction: INCOMING, start: 0, count: 100 }) {
                    relationships { entity { urn } }
                  }
                }
              }
            }
          }
        }
        """
        out: list[MetricDefinition] = []
        start, count = 0, 50
        while True:
            res = self._graph.execute_graphql(
                query=query, variables={"start": start, "count": count}
            )
            block = (res or {}).get("searchAcrossEntities", {})
            results = block.get("searchResults", []) or []
            for r in results:
                ent = r.get("entity", {}) or {}
                props = ent.get("properties") or {}
                name = props.get("name") or ent.get("urn", "").split(":")[-1]
                dom = (((ent.get("domain") or {}).get("domain") or {}).get("properties") or {})
                rels = ((ent.get("relationships") or {}).get("relationships") or [])
                source_urns = [
                    (x.get("entity") or {}).get("urn")
                    for x in rels
                    if (x.get("entity") or {}).get("urn")
                ]
                out.append(
                    MetricDefinition(
                        name=self._normalize(name),
                        display_name=name,
                        domain=dom.get("name", "unknown"),
                        owner="",
                        definition_text=props.get("description", "") or "",
                        source_urns=source_urns,
                        term_urn=ent.get("urn", ""),
                    )
                )
            total = block.get("total", 0)
            start += count
            if start >= total or not results:
                break
        return out

    @staticmethod
    def _normalize(name: str) -> str:
        return name.strip().lower().replace(" ", "_").replace("-", "_")

    def blast_radius(self, defn: MetricDefinition) -> int:
        """Count downstream assets impacted by a definition by walking lineage."""
        return len(self.downstream_assets(defn))

    def downstream_assets(self, defn: MetricDefinition) -> list[str]:
        """Transitive set of downstream assets from every asset using this defn.

        LIVE: uses DataHub lineage (GraphQL scrollAcrossLineage) per source urn.
        DEMO: walks the seed lineage graph in demo_data/lineage.json.
        """
        if self.live and self._graph is not None:
            try:
                return self._downstream_live(defn)
            except Exception as exc:  # pragma: no cover - network dependent
                log.warning("Live lineage failed (%s); using seed graph.", exc)
        return self._downstream_seed(defn)

    def _downstream_seed(self, defn: MetricDefinition) -> list[str]:
        graph = self._lineage_graph()
        seen: set[str] = set()
        frontier = list(defn.source_urns)
        while frontier:
            node = frontier.pop()
            for child in graph.get(node, []):
                if child not in seen:
                    seen.add(child)
                    frontier.append(child)
        for u in defn.source_urns:
            seen.add(u)
        return sorted(seen)

    def _downstream_live(self, defn: MetricDefinition) -> list[str]:  # pragma: no cover
        """Walk downstream lineage in a real DataHub instance via GraphQL."""
        query = """
        query rosettaLineage($urn: String!) {
          scrollAcrossLineage(
            input: { urn: $urn, direction: DOWNSTREAM, count: 200,
                     query: "*", searchFlags: { skipCache: true } }
          ) {
            searchResults { entity { urn } }
          }
        }
        """
        seen: set[str] = set()
        for src in defn.source_urns:
            frontier = [src]
            local_seen = {src}
            while frontier:
                node = frontier.pop()
                res = self._graph.execute_graphql(query=query, variables={"urn": node})
                results = ((res or {}).get("scrollAcrossLineage") or {}).get(
                    "searchResults", []
                ) or []
                for r in results:
                    child = ((r.get("entity") or {}).get("urn"))
                    if child and child not in local_seen:
                        local_seen.add(child)
                        seen.add(child)
                        frontier.append(child)
        for u in defn.source_urns:
            seen.add(u)
        return sorted(seen)

    def _lineage_graph(self) -> dict:
        if self._lineage_cache is not None:
            return self._lineage_cache
        path = _DATA_DIR / "lineage.json"
        if path.exists():
            raw = json.loads(path.read_text())
            self._lineage_cache = {k: v for k, v in raw.items() if not k.startswith("_")}
        else:  # pragma: no cover
            self._lineage_cache = {}
        return self._lineage_cache

    def impact_graph(self, defn: MetricDefinition) -> dict:
        """Build a typed node/edge graph of everything a wrong definition
        contaminates, for visualization. Uses downstream_assets under the hood,
        so it reflects live lineage in LIVE mode and the seed graph in DEMO."""
        # Build adjacency from the authoritative downstream set so live + demo
        # both produce a connected graph rooted at the metric.
        graph = self._lineage_graph() if not self.live else self._live_adjacency(defn)
        nodes: dict[str, dict] = {}
        edges: list[dict] = []

        origin_id = f"metric::{defn.name}::{defn.domain}"
        nodes[origin_id] = {
            "id": origin_id,
            "label": f"{defn.display_name}\n({defn.domain})",
            "type": "metric",
        }

        def kind(urn: str) -> str:
            if ":dashboard:" in urn or ":chart:" in urn:
                return "dashboard"
            if ":mlModel:" in urn or ":mlFeatureTable:" in urn:
                return "model"
            return "dataset"

        def short(urn: str) -> str:
            if ":dashboard:" in urn or ":chart:" in urn:
                inner = urn.split("(", 1)[-1].rstrip(")")
                parts = [p for p in inner.split(",") if p]
                return parts[-1].split(".")[-1] if parts else urn
            if ":mlModel:" in urn:
                inner = urn.split("(", 1)[-1].rstrip(")")
                parts = [p for p in inner.split(",") if p]
                return parts[1] if len(parts) > 1 else parts[-1]
            inner = urn.split("(", 1)[-1].rstrip(")")
            parts = [p for p in inner.split(",") if p]
            table = parts[1] if len(parts) > 1 else inner
            return table.split(".")[-1]

        seen: set[str] = set()
        frontier = []
        for u in defn.source_urns:
            nodes.setdefault(u, {"id": u, "label": short(u), "type": kind(u)})
            edges.append({"source": origin_id, "target": u})
            frontier.append(u)
            seen.add(u)
        while frontier:
            node = frontier.pop()
            for child in graph.get(node, []):
                nodes.setdefault(child, {"id": child, "label": short(child), "type": kind(child)})
                edges.append({"source": node, "target": child})
                if child not in seen:
                    seen.add(child)
                    frontier.append(child)
        return {"nodes": list(nodes.values()), "edges": edges}

    def _live_adjacency(self, defn: MetricDefinition) -> dict:  # pragma: no cover
        """Flat one-hop adjacency (source -> downstream) for live visualization."""
        downstream = self._downstream_live(defn)
        # Attach all downstream nodes directly under their source for a simple,
        # correct (if shallow) visual; deep topology is preserved by the counts.
        adj: dict[str, list[str]] = {}
        for src in defn.source_urns:
            adj[src] = [d for d in downstream if d not in defn.source_urns]
        return adj

    # ---------------------------------------------------------------- WRITE
    def write_canonical_term(
        self, term_id: str, display_name: str, definition: str
    ) -> str:
        """Upsert the agreed canonical glossary term back into DataHub.

        LIVE: real write via client.entities.upsert(GlossaryTerm(...)).
        DEMO: no-op that returns the URN it *would* have written, so the
              orchestrator's --apply dry-run path works without an instance.
        """
        urn = f"urn:li:glossaryTerm:{term_id}"
        if not self.live:
            log.info("[demo] would upsert canonical term %s", urn)
            return urn
        if not _HAS_SDK or self.client is None:  # pragma: no cover
            raise RuntimeError("SDK required to write to DataHub.")
        term = GlossaryTerm(id=term_id, display_name=display_name, definition=definition)
        self.client.entities.upsert(term)
        log.info("[live] upserted canonical term %s into DataHub", urn)
        return urn

    def attach_term_to_assets(self, term_urn: str, asset_urns: Iterable[str]) -> None:
        """Link the canonical term to every affected dataset."""
        if not self.live:
            log.info("[demo] would attach %s to assets", term_urn)
            return
        if not _HAS_SDK or self.client is None:  # pragma: no cover
            raise RuntimeError("SDK required to write to DataHub.")
        for urn in asset_urns:  # pragma: no cover - network dependent
            dataset = self.client.entities.get(DatasetUrn.from_string(urn))
            dataset.add_term(GlossaryTermUrn(term_urn))
            self.client.entities.update(dataset)

    def deprecate_conflicting_term(self, term_urn: str, note: str) -> None:
        """Mark a losing definition deprecated. Deprecated terms remain in the
        system and keep their relationships, so nothing breaks; they just stop
        being the recommended vocabulary."""
        if not self.live:
            log.info("[demo] would deprecate %s (%s)", term_urn, note)
            return
        if not _HAS_SDK or self.client is None:  # pragma: no cover
            raise RuntimeError("SDK required to write to DataHub.")
        term = self.client.entities.get(GlossaryTermUrn.from_string(term_urn))  # pragma: no cover
        term.set_deprecation(deprecated=True, note=note)
        self.client.entities.update(term)
