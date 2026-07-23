"""
Rosetta demo mode.

A self-contained, narrated walkthrough of the five-agent pipeline that runs
with zero external dependencies (no DataHub instance, no LLM keys). It uses the
seed data in demo_data/ and emits a structured list of "steps" so both the CLI
(pretty printed, optionally with typewriter pacing) and the web app (streamed
to the browser) can render the exact same story.

This is what the judges see in the <3 minute video and what runs when they
click "Run Demo" on the hosted app.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field

from .broker import draft_proposal
from .datahub_client import RosettaDataHub
from .detector import detect_conflicts
from .orchestrator import build_report


@dataclass
class Step:
    agent: str          # which of the 5 agents is speaking
    icon: str           # emoji / glyph for quick scan
    title: str          # short headline
    detail: str         # the narrated line
    payload: dict = field(default_factory=dict)  # structured data for the UI

    def to_dict(self) -> dict:
        return {
            "agent": self.agent,
            "icon": self.icon,
            "title": self.title,
            "detail": self.detail,
            "payload": self.payload,
        }


def _seed_dh() -> RosettaDataHub:
    # Build a client that only uses the offline seed harvester (no live conn).
    dh = RosettaDataHub.__new__(RosettaDataHub)
    dh._lineage_cache = None
    return dh


def run_demo() -> dict:
    """Run the full narrated demo and return steps + final report + proposals."""
    dh = _seed_dh()
    steps: list[Step] = []

    # 1. Harvester
    defs = dh.harvest_metric_definitions()
    for d in defs:
        d.source_urns = list(dict.fromkeys(d.source_urns))
    steps.append(
        Step(
            "Harvester", "🧲", "Reading the DataHub graph",
            f"Harvested {len(defs)} metric definitions across "
            f"{len({d.domain for d in defs})} domains "
            f"({', '.join(sorted({d.domain for d in defs}))}).",
            {"definitions": [
                {"name": d.name, "display_name": d.display_name,
                 "domain": d.domain, "owner": d.owner,
                 "assets": len(d.source_urns)} for d in defs]},
        )
    )

    # 2. Conflict Detector
    conflicts = detect_conflicts(defs)
    steps.append(
        Step(
            "Conflict Detector", "🔍", "Comparing meaning, not just names",
            f"Found {len(conflicts)} semantic conflicts: "
            f"{sum(c.kind=='silent_contradiction' for c in conflicts)} silent "
            f"contradiction(s) and "
            f"{sum(c.kind=='hidden_synonym' for c in conflicts)} hidden synonym(s).",
            {"conflicts": [c.to_dict() for c in conflicts]},
        )
    )
    for c in conflicts:
        if c.kind == "silent_contradiction":
            steps.append(
                Step(
                    "Conflict Detector", "⚠️",
                    f"Silent contradiction: {c.metric}",
                    c.rationale,
                    {"metric": c.metric, "severity": c.severity},
                )
            )
        else:
            steps.append(
                Step(
                    "Conflict Detector", "🔗",
                    f"Hidden synonym: {c.metric}",
                    c.rationale,
                    {"metric": c.metric, "severity": c.severity},
                )
            )

    # 3. Blast-radius analyzer (walk downstream lineage transitively)
    for c in conflicts:
        downstream = set()
        merged_nodes, merged_edges, seen_e = {}, [], set()
        for d in c.definitions:
            downstream.update(dh.downstream_assets(d))
            g = dh.impact_graph(d)
            for n in g["nodes"]:
                merged_nodes[n["id"]] = n
            for e in g["edges"]:
                key = (e["source"], e["target"])
                if key not in seen_e:
                    seen_e.add(key)
                    merged_edges.append(e)
        c.blast_radius = max(c.blast_radius, len(downstream))
        c.impacted_assets = sorted(downstream)
        c.impact_graph = {"nodes": list(merged_nodes.values()), "edges": merged_edges}
    total_blast = sum(c.blast_radius for c in conflicts)
    steps.append(
        Step(
            "Blast-Radius Analyzer", "💥", "Walking downstream lineage",
            f"{total_blast} downstream assets are affected. "
            f"Highest impact: '{conflicts[0].metric}' hits "
            f"{conflicts[0].blast_radius} assets ({conflicts[0].severity}).",
            {"ranked": [{"metric": c.metric, "blast": c.blast_radius,
                         "confidence": c.confidence,
                         "severity": c.severity} for c in conflicts]},
        )
    )

    # 4. Reconciliation Broker
    proposals = []
    for c in conflicts:
        p = draft_proposal(c)
        proposals.append(p)
        steps.append(
            Step(
                "Reconciliation Broker", "🤝",
                f"Drafting canonical definition: {p.display_name}",
                f"Proposed one canonical definition. Routing to "
                f"{len(p.approvers)} owner(s) for approval: "
                f"{', '.join(p.approvers)}.",
                {"term_id": p.term_id, "display_name": p.display_name,
                 "canonical_definition": p.canonical_definition,
                 "approvers": p.approvers,
                 "deprecated_terms": p.deprecated_terms,
                 "affected_assets": p.affected_assets},
            )
        )

    # 5. Writer (dry-run in demo)
    steps.append(
        Step(
            "Writer", "✍️", "Writing canonical terms back to DataHub (dry-run)",
            f"Would upsert {len(proposals)} canonical GlossaryTerm(s), link them "
            f"to {sum(len(p.affected_assets) for p in proposals)} assets, and "
            f"deprecate {sum(len(p.deprecated_terms) for p in proposals)} losing "
            f"term(s). Run with --apply against a live instance to commit.",
            {"writes": [{"term": p.term_id,
                         "linked_assets": p.affected_assets,
                         "deprecated": p.deprecated_terms} for p in proposals]},
        )
    )

    report = build_report(conflicts)
    return {
        "steps": [s.to_dict() for s in steps],
        "report": report,
        "proposals": [
            {"term_id": p.term_id, "display_name": p.display_name,
             "canonical_definition": p.canonical_definition,
             "approvers": p.approvers, "deprecated_terms": p.deprecated_terms,
             "affected_assets": p.affected_assets}
            for p in proposals
        ],
    }


# ANSI colours for a nice terminal demo
_C = {"cyan": "\033[36m", "yellow": "\033[33m", "red": "\033[31m",
      "green": "\033[32m", "grey": "\033[90m", "bold": "\033[1m",
      "reset": "\033[0m"}


def print_demo(pace: float = 0.0) -> dict:
    """Pretty-print the narrated demo to the terminal.

    `pace` adds a delay (seconds) between steps for a cinematic reveal in the
    recorded video. Set 0 for instant output (default, CI-friendly)."""
    result = run_demo()
    print(f"\n{_C['bold']}{_C['cyan']}  ROSETTA — Semantic Consistency Agent{_C['reset']}")
    print(f"{_C['grey']}  the linter for meaning across your DataHub graph{_C['reset']}\n")
    for s in result["steps"]:
        print(f"{_C['bold']}{s['icon']}  [{s['agent']}]{_C['reset']} {s['title']}")
        print(f"    {_C['grey']}{s['detail']}{_C['reset']}\n")
        if pace:
            time.sleep(pace)
    sm = result["report"]["summary"]
    print(f"{_C['bold']}{_C['green']}  Done.{_C['reset']} "
          f"{sm['total_conflicts']} conflicts · {sm['assets_at_risk']} assets at risk\n")
    return result


if __name__ == "__main__":
    import sys
    pace = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0
    print_demo(pace)
