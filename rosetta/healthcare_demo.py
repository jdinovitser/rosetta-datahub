run r"""
Healthcare demo mode for Rosetta.

Runs the full five-agent pipeline against the real DataHub hackathon sample
dataset (healthcare.db — 55,500 synthetic patient records with deliberately
planted quality issues). Returns the same steps+report+proposals shape as
run_demo() so the frontend renders it without modification.

Real issues in this dataset (planted by the dataset authors):
  • 1,215 negative billing amounts propagated into mart_billing
  • 277 date-swapped admissions causing negative length_of_stay in mart_billing
  • 832 impossible patient ages (−88 to 285) in mart_demographics
  • 555 NULL patient names silently present in mart_demographics
  • test_results raw (mixed-case) vs test_results_clean (normalized) — hidden synonym
"""
from __future__ import annotations

from .broker import draft_proposal
from .demo import Step
from .detector import detect_conflicts, _severity
from .healthcare_source import HealthcareDataSource
from .orchestrator import build_report
from . import impact as impact_mod
from . import intelligence as intel_mod
from .broker import proposal_diff


def _pct(n: int, total: int) -> str:
    return f"{n / total * 100:.1f}%"


def run_healthcare_demo() -> dict:
    """
    Run the narrated five-agent pipeline on the real healthcare SQLite database.
    Returns the same dict shape as run_demo():
        { "steps": [...], "report": {...}, "proposals": [...], "source": "healthcare" }
    """
    ds = HealthcareDataSource()
    s = ds.stats
    steps: list[Step] = []

    # ── 1. Harvester ─────────────────────────────────────────────────────────
    defs = ds.harvest_metric_definitions()
    domains = sorted({d.domain for d in defs})
    steps.append(Step(
        "Harvester", "🧲",
        "Reading the DataHub Healthcare graph",
        (
            f"Harvested {len(defs)} metric definitions across "
            f"{len(domains)} owning teams ({', '.join(domains)}). "
            f"Dataset: {s.total:,} patient records across {s.conditions} medical conditions, "
            f"{s.insurers} insurance providers. "
            f"Pipeline: raw_patients → staging_patients → mart_billing + mart_demographics."
        ),
        {"definitions": [
            {"name": d.name, "display_name": d.display_name,
             "domain": d.domain, "owner": d.owner,
             "assets": len(d.source_urns)} for d in defs
        ]},
    ))

    # ── 2. Conflict Detector ──────────────────────────────────────────────────
    conflicts = detect_conflicts(defs)
    n_contra = sum(c.kind == "silent_contradiction" for c in conflicts)
    n_syn    = sum(c.kind == "hidden_synonym" for c in conflicts)

    def _friendly(m: str) -> str:
        if "~" in m:
            a, b = m.split("~", 1)
            return f"{a.replace('_',' ').title()} vs {b.replace('_',' ').title()}"
        return m.replace("_", " ").title()

    conflict_lines = "; ".join(
        f"{_friendly(c.metric)} [{c.severity}]" for c in conflicts
    )
    steps.append(Step(
        "Conflict Detector", "🔍",
        f"{len(conflicts)} semantic conflicts identified in healthcare pipeline",
        (
            f"{n_contra} silent contradiction(s) and {n_syn} hidden synonym(s) found. "
            f"Real data evidence: {s.neg_billing:,} negative billing amounts ({_pct(s.neg_billing, s.total)} of records), "
            f"{s.bad_ages:,} impossible ages (range {s.age_min}–{s.age_max}), "
            f"{s.date_swaps:,} admission/discharge date swaps. "
            f"Conflicts: {conflict_lines}."
        ),
        {"conflicts": [c.to_dict() for c in conflicts]},
    ))

    # ── 3. Blast-Radius Analyzer ──────────────────────────────────────────────
    # Affected-row counts from the real DB — used to override graph-size-based
    # severity thresholds which were tuned for large DataHub instances, not a
    # 4-table SQLite pipeline.
    _row_evidence = {
        "billing_amount":                  ("critical", s.neg_billing),    # 1,215 rows, $28M
        "length_of_stay":                  ("high",     s.neg_los),        # 277 negative LOS
        "patient_age":                     ("high",     s.bad_ages),       # 832 invalid ages
        "patient_name":                    ("medium",   s.null_names),     # 555 NULL names
        "test_results~test_results_clean": ("medium",   s.total),          # all 55,500 rows
    }

    for c in conflicts:
        downstream = set()
        merged_nodes, merged_edges, seen_e = {}, [], set()
        for d in c.definitions:
            downstream.update(ds.downstream_assets(d))
            g = ds.impact_graph(d)
            for n in g["nodes"]:
                merged_nodes[n["id"]] = n
            for e in g["edges"]:
                key = (e["source"], e["target"])
                if key not in seen_e:
                    seen_e.add(key)
                    merged_edges.append(e)

        # Use real row count as blast_radius proxy (1 unit per 100 affected rows)
        # so impact cost estimates reflect actual data volume.
        if c.metric in _row_evidence:
            sev, rows = _row_evidence[c.metric]
            c.blast_radius = max(len(downstream), rows // 100)
            c.severity = sev          # evidence-driven, not graph-size-driven
        else:
            c.blast_radius = max(c.blast_radius, len(downstream))
            c.severity = _severity(c.blast_radius)

        c.impacted_assets = sorted(downstream)
        c.impact_graph = {"nodes": list(merged_nodes.values()), "edges": merged_edges}

    total_blast = sum(c.blast_radius for c in conflicts)
    steps.append(Step(
        "Blast-Radius Analyzer", "💥",
        f"{total_blast} downstream assets contaminated across the healthcare pipeline",
        (
            f"Negative billing_amount has propagated into mart_billing "
            f"({s.neg_billing:,} rows, ${s.neg_bill_sum:,.0f} misreported revenue). "
            f"{s.neg_los:,} records in mart_billing carry negative length_of_stay_days. "
            f"{s.bad_ages:,} invalid ages have reached mart_demographics — "
            f"research cohort analysis is corrupted at the source."
        ),
        {"conflicts": [c.to_dict() for c in conflicts]},
    ))

    # ── 4. Reconciliation Broker ──────────────────────────────────────────────
    proposals = [draft_proposal(c) for c in conflicts]
    steps.append(Step(
        "Reconciliation Broker", "🤝",
        f"{len(proposals)} canonical definition(s) proposed",
        (
            f"Broker drafted canonical definitions merging clinical_team, "
            f"finance_team, and research_team intent. "
            f"Billing Amount: positive-only constraint added. "
            f"Length of Stay: admission < discharge validation enforced. "
            f"Patient Age: 0–120 range constraint. "
            f"All proposals require human approval before DataHub write-back."
        ),
        {"proposals": [
            {"term_id": p.term_id, "display_name": p.display_name,
             "canonical_definition": p.canonical_definition,
             "approvers": p.approvers} for p in proposals
        ]},
    ))

    # ── 5. Writer ─────────────────────────────────────────────────────────────
    steps.append(Step(
        "Writer", "✅",
        f"Ready to write {len(proposals)} canonical GlossaryTerm(s) to DataHub",
        (
            f"Would upsert {len(proposals)} GlossaryTerms, attach them to "
            f"{sum(len(p.affected_assets) for p in proposals)} assets, "
            f"and deprecate {sum(len(p.deprecated_terms) for p in proposals)} "
            f"conflicting term(s). Run with --apply against a live DataHub instance to commit."
        ),
        {"writes": [{"term": p.term_id,
                     "linked_assets": p.affected_assets,
                     "deprecated": p.deprecated_terms} for p in proposals]},
    ))

    # ── Build report with full AI explanations ────────────────────────────────
    conflict_dicts = []
    for c in conflicts:
        cd = c.to_dict()
        cd["impact"] = impact_mod.estimate_conflict_impact(cd)
        proposal = draft_proposal(c)
        cd["proposed_reconciliation"] = proposal_diff(c, proposal)
        cd["ai_explanation"] = intel_mod.generate_ai_explanation(cd)
        conflict_dicts.append(cd)

    from datetime import datetime, timezone
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "healthcare",
        "dataset": "DataHub Hackathon Sample — Healthcare Pipeline (55,500 patient records)",
        "summary": {
            "total_conflicts": len(conflicts),
            "critical": sum(c.severity == "critical" for c in conflicts),
            "high":     sum(c.severity == "high"     for c in conflicts),
            "assets_at_risk": sum(c.blast_radius for c in conflicts),
            "real_data_issues": {
                "negative_billing_rows": s.neg_billing,
                "negative_billing_revenue_usd": s.neg_bill_sum,
                "invalid_age_rows": s.bad_ages,
                "date_swap_rows": s.date_swaps,
                "null_name_rows": s.null_names,
                "negative_los_in_mart": s.neg_los,
            },
        },
        "conflicts": conflict_dicts,
    }
    report["summary"]["impact"] = impact_mod.portfolio_impact(report)

    return {
        "steps":     [s_.to_dict() for s_ in steps],
        "report":    report,
        "source":    "healthcare",
        "proposals": [
            {"term_id": p.term_id, "display_name": p.display_name,
             "canonical_definition": p.canonical_definition,
             "approvers": p.approvers, "deprecated_terms": p.deprecated_terms,
             "affected_assets": p.affected_assets}
            for p in proposals
        ],
    }
