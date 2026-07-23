"""
Rosetta orchestrator: the five-agent pipeline.

  Harvester -> ConflictDetector -> BlastRadiusAnalyzer -> ReconciliationBroker -> Writer

The multi-agent-with-a-router shape mirrors what has been winning agent
hackathons (LORE's router + 8 agents, DocSync's Detector/Writer/Reviewer).

Common commands:
  python -m rosetta.orchestrator --demo              narrated offline walkthrough
  python -m rosetta.orchestrator --report            read-only JSON report
  python -m rosetta.orchestrator --report --export all --out-dir exports
  python -m rosetta.orchestrator --apply             write canonical terms back
"""
from __future__ import annotations

import argparse
import os
import json
from datetime import datetime, timezone

from .broker import apply_proposal, draft_proposal, proposal_diff
from .datahub_client import RosettaDataHub
from .detector import detect_conflicts
from . import exporter
from . import impact as impact_mod


def run_scan(dh: RosettaDataHub) -> list:
    definitions = dh.harvest_metric_definitions()          # Harvester
    for d in definitions:
        d.source_urns = list(dict.fromkeys(d.source_urns))
    conflicts = detect_conflicts(definitions)              # Detector
    for c in conflicts:                                    # Blast-radius analyzer
        downstream = set()
        merged = {"nodes": {}, "edges": []}
        for d in c.definitions:
            downstream.update(dh.downstream_assets(d))
            g = dh.impact_graph(d)
            for n in g["nodes"]:
                merged["nodes"][n["id"]] = n
            merged["edges"].extend(g["edges"])
        c.blast_radius = max(c.blast_radius, len(downstream))
        c.impacted_assets = sorted(downstream)
        # dedupe edges
        seen_e = set()
        edges = []
        for e in merged["edges"]:
            key = (e["source"], e["target"])
            if key not in seen_e:
                seen_e.add(key)
                edges.append(e)
        c.impact_graph = {"nodes": list(merged["nodes"].values()), "edges": edges}
    return conflicts


def build_report(conflicts: list) -> dict:
    conflict_dicts = []
    for c in conflicts:
        cd = c.to_dict()
        cd["impact"] = impact_mod.estimate_conflict_impact(cd)
        proposal = draft_proposal(c)
        cd["proposed_reconciliation"] = proposal_diff(c, proposal)
        conflict_dicts.append(cd)

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_conflicts": len(conflicts),
            "critical": sum(c.severity == "critical" for c in conflicts),
            "high": sum(c.severity == "high" for c in conflicts),
            "assets_at_risk": sum(c.blast_radius for c in conflicts),
        },
        "conflicts": conflict_dicts,
    }
    report["summary"]["impact"] = impact_mod.portfolio_impact(report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Rosetta semantic consistency agent")
    parser.add_argument("--demo", action="store_true",
                        help="Narrated, offline, zero-config walkthrough of the pipeline.")
    parser.add_argument("--pace", type=float, default=0.0,
                        help="Seconds between demo steps (for recording video).")
    parser.add_argument("--report", action="store_true",
                        help="Read-only: print a conflict report as JSON.")
    parser.add_argument("--apply", action="store_true",
                        help="Write reconciled canonical terms back to DataHub.")
    parser.add_argument("--offline", action="store_true",
                        help="Use seed data; no live DataHub connection needed.")
    parser.add_argument("--live", action="store_true",
                        help="Force live mode: connect to DATAHUB_GMS_URL and "
                             "read/write the real graph (errors if unreachable).")
    parser.add_argument("--check-connection", action="store_true",
                        help="Print whether a live DataHub is reachable, then exit.")
    parser.add_argument("--export", default=None,
                        help="Export report: json | csv | md | html | all")
    parser.add_argument("--out", default=None, help="Write JSON report to this file.")
    parser.add_argument("--out-dir", default="exports",
                        help="Directory for --export all (default: exports/).")
    args = parser.parse_args()

    import sys

    # Connection check: quick, explicit, for demos and CI.
    if args.check_connection:
        dh = RosettaDataHub()
        if dh.live:
            print(f"LIVE  -> connected to DataHub at {dh.gms_url}")
        else:
            url = os.environ.get("DATAHUB_GMS_URL")
            if url:
                print(f"DEMO  -> DATAHUB_GMS_URL={url} is set but unreachable; "
                      f"would use the bundled demo graph.")
            else:
                print("DEMO  -> no DATAHUB_GMS_URL set; using the bundled demo graph.")
        return

    # Demo mode: narrated, offline, no flags needed beyond --demo.
    if args.demo:
        from .demo import print_demo
        result = print_demo(pace=args.pace)
        if args.export:
            _do_export(result["report"], args.export, args.out_dir)
        return

    if args.offline or (args.report and not args.apply and not args.live):
        dh = RosettaDataHub.__new__(RosettaDataHub)
        dh._lineage_cache = None
    else:
        dh = RosettaDataHub()

    if args.live and not dh.live:
        print(
            "ERROR: --live requested but no reachable DataHub at "
            f"{os.environ.get('DATAHUB_GMS_URL') or '(DATAHUB_GMS_URL unset)'}.\n"
            "Start one with `datahub docker quickstart` and set "
            "DATAHUB_GMS_URL=http://localhost:8080, or drop --live to use the "
            "demo graph.",
            file=sys.stderr,
        )
        raise SystemExit(2)

    # Mode banner (to stderr so it never pollutes the JSON on stdout).
    print(
        f"[Rosetta] mode={dh.mode.upper()}"
        + (f" gms={dh.gms_url}" if dh.live else " (bundled demo graph)"),
        file=sys.stderr,
    )

    conflicts = run_scan(dh)
    report = build_report(conflicts)

    output = json.dumps(report, indent=2)
    if args.out:
        with open(args.out, "w") as f:
            f.write(output)
    print(output)

    if args.export:
        _do_export(report, args.export, args.out_dir)

    if args.apply:
        for c in conflicts:
            proposal = draft_proposal(c)
            print(f"\nProposing canonical term '{proposal.display_name}' "
                  f"-> approvers: {proposal.approvers}")
            audit = apply_proposal(dh, proposal)
            print(json.dumps(audit, indent=2))


def _do_export(report: dict, fmt: str, out_dir: str) -> None:
    if fmt.lower() == "all":
        paths = exporter.export_all(report, out_dir=out_dir)
        print("\nExported:")
        for p in paths:
            print(f"  - {p}")
    else:
        content = exporter.export(report, fmt)
        path = f"{out_dir.rstrip('/')}/rosetta_report.{fmt.lower()}"
        import os
        os.makedirs(out_dir, exist_ok=True)
        with open(path, "w") as f:
            f.write(content)
        print(f"\nExported: {path}")


if __name__ == "__main__":
    main()
