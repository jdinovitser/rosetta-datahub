"""
Fiction-Retail demo mode for Rosetta.

Runs the full five-agent pipeline against the Fiction Retail
E-Commerce dataset (fiction_retail.db — 150,000 orders across 10 tables
with deliberately planted quality issues). Returns the same
steps+report+proposals shape as run_demo() so the frontend renders it
without modification.

Real issue in this dataset:
  • discount_pct unit-convention conflict:
      – marketing_team stores promotion discounts as integer percent (5–30)
      – commerce_team / analytics expect decimal fraction (0.0–1.0)
      – 37,161 order_items rows carry the integer-percent values
      – downstream net-revenue calculations are 5–30× wrong for those rows

  • order_status / shipment_state hidden synonym:
      – same delivery lifecycle tracked by two teams under different names
        and value sets, causing silent mismatches in cross-team dashboards
"""
from __future__ import annotations

from .broker import draft_proposal
from .demo import Step
from .detector import detect_conflicts, _severity
from .fiction_retail_source import FictionRetailDataSource
from .orchestrator import build_report
from . import impact as impact_mod
from . import intelligence as intel_mod
from .broker import proposal_diff


def _pct(n: int, total: int) -> str:
    return f"{n / total * 100:.1f}%"


def run_fiction_retail_demo() -> dict:
    """
    Run the narrated five-agent pipeline on the fiction-retail SQLite database.
    Returns the same dict shape as run_demo():
        { "steps": [...], "report": {...}, "proposals": [...], "source": "fiction_retail" }
    """
    ds = FictionRetailDataSource()
    s = ds.stats
    steps: list[Step] = []

    # ── 1. Harvester ─────────────────────────────────────────────────────────
    defs = ds.harvest_metric_definitions()
    domains = sorted({d.domain for d in defs})
    steps.append(Step(
        "Harvester", "🧲",
        "Reading the Fiction-Retail DataHub graph",
        (
            f"Harvested {len(defs)} metric definitions across "
            f"{len(domains)} owning teams ({', '.join(domains)}). "
            f"Dataset: {s.total_orders:,} orders, {s.total_items:,} line items, "
            f"{s.total_customers:,} customers, {s.total_products:,} products "
            f"across 10 interconnected tables. "
            "Pipeline: customers + promotions → orders → order_items + shipments + returns."
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
    n_syn    = sum(c.kind == "hidden_synonym"       for c in conflicts)

    def _friendly(m: str) -> str:
        if "~" in m:
            a, b = m.split("~", 1)
            return f"{a.replace('_', ' ').title()} vs {b.replace('_', ' ').title()}"
        return m.replace("_", " ").title()

    conflict_lines = "; ".join(
        f"{_friendly(c.metric)} [{c.severity}]" for c in conflicts
    )
    steps.append(Step(
        "Conflict Detector", "🔍",
        f"{len(conflicts)} semantic conflicts identified in retail pipeline",
        (
            f"{n_contra} silent contradiction(s) and {n_syn} hidden synonym(s) found. "
            f"Real data evidence: {s.bad_discount_rows:,} order line items have "
            f"discount_pct values of {s.disc_min:.0f}–{s.disc_max:.0f} "
            f"(integer percent) instead of 0.0–1.0 (decimal fraction) — "
            f"affecting {s.bad_discount_orders:,} orders "
            f"({_pct(s.bad_discount_orders, s.total_orders)} of all orders). "
            f"Conflicts: {conflict_lines}."
        ),
        {"conflicts": [c.to_dict() for c in conflicts]},
    ))

    # ── 3. Blast-Radius Analyzer ──────────────────────────────────────────────
    # Use affected-row counts from the real DB to size blast radius.
    _row_evidence = {
        "discount_pct":                ("critical", s.bad_discount_rows),   # 37,161 rows
        "order_status~shipment_state": ("medium",   s.total_orders),        # all 150,000 orders
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

        if c.metric in _row_evidence:
            sev, rows = _row_evidence[c.metric]
            c.blast_radius = max(len(downstream), rows // 100)
            c.severity = sev
        else:
            c.blast_radius = max(c.blast_radius, len(downstream))
            c.severity = _severity(c.blast_radius)

        c.impacted_assets = sorted(downstream)
        c.impact_graph = {"nodes": list(merged_nodes.values()), "edges": merged_edges}

    total_blast = sum(c.blast_radius for c in conflicts)
    steps.append(Step(
        "Blast-Radius Analyzer", "💥",
        f"{total_blast} downstream assets contaminated across the retail pipeline",
        (
            f"discount_pct unit mismatch has propagated into {s.bad_discount_rows:,} "
            f"order line items — ${s.bad_discount_revenue:,.0f} in gross merchandise "
            f"value is being discounted at {s.disc_min:.0f}–{s.disc_max:.0f}× "
            "the intended rate in revenue models. "
            f"Order-status / shipment-state synonym means {s.total_orders:,} orders "
            "appear in two irreconcilable lifecycle systems."
        ),
        {"conflicts": [c.to_dict() for c in conflicts]},
    ))

    # ── 4. Reconciliation Broker ──────────────────────────────────────────────
    proposals = [draft_proposal(c) for c in conflicts]
    steps.append(Step(
        "Reconciliation Broker", "🤝",
        f"{len(proposals)} canonical definition(s) proposed",
        (
            f"Broker drafted canonical definitions merging commerce_team, "
            f"marketing_team, and logistics_team intent. "
            "Discount Percentage: standardize on decimal fraction 0.0–1.0; "
            "migration script converts existing integer-percent rows. "
            "Order/Shipment status: unified lifecycle glossary with explicit "
            "field-to-field mapping table. "
            "All proposals require human approval before DataHub write-back."
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
            "conflicting term(s). Run with --apply against a live DataHub instance to commit."
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
        "source": "fiction_retail",
        "dataset": "Fiction Retail E-Commerce (150,000 orders, 10 tables)",
        "summary": {
            "total_conflicts": len(conflicts),
            "critical": sum(c.severity == "critical" for c in conflicts),
            "high":     sum(c.severity == "high"     for c in conflicts),
            "assets_at_risk": sum(c.blast_radius for c in conflicts),
            "real_data_issues": {
                "bad_discount_rows": s.bad_discount_rows,
                "bad_discount_orders": s.bad_discount_orders,
                "bad_discount_revenue_usd": s.bad_discount_revenue,
                "discount_integer_range": f"{s.disc_min:.0f}–{s.disc_max:.0f}",
                "status_synonym_orders": s.total_orders,
            },
        },
        "conflicts": conflict_dicts,
    }
    report["summary"]["impact"] = impact_mod.portfolio_impact(report)

    return {
        "steps":     [s_.to_dict() for s_ in steps],
        "report":    report,
        "source":    "fiction_retail",
        "proposals": [
            {"term_id": p.term_id, "display_name": p.display_name,
             "canonical_definition": p.canonical_definition,
             "approvers": p.approvers, "deprecated_terms": p.deprecated_terms,
             "affected_assets": p.affected_assets}
            for p in proposals
        ],
    }
