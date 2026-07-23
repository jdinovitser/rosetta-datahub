"""
Impact estimator: turns a raw blast radius into a "so what" the judges feel.

Winning hackathon demos don't stop at "found 3 conflicts" -- they quantify the
cost of NOT fixing them. Rosetta estimates:
  - decision surface: how many dashboards/models a wrong number silently feeds
  - review hours saved: hand-reconciling a metric across N assets is ~0.5h each
  - a plain-English risk sentence a VP can read

All coefficients live here so they're easy to tune per org.
"""
from __future__ import annotations

# Rough, defensible coefficients (documented so judges see the assumptions).
HOURS_PER_ASSET_MANUAL = 0.5          # analyst time to trace + fix one asset by hand
BLENDED_ANALYST_RATE_USD = 90.0       # fully-loaded hourly cost


def _asset_kind(urn: str) -> str:
    if ":dashboard:" in urn or ":chart:" in urn:
        return "dashboard"
    if ":mlModel:" in urn or ":mlFeatureTable:" in urn:
        return "model"
    return "dataset"


def estimate_conflict_impact(conflict_dict: dict) -> dict:
    """Attach an impact block to a conflict's serialized form."""
    assets = conflict_dict.get("impacted_assets") or sorted(
        {u for d in conflict_dict["definitions"] for u in d["affected_assets"]}
    )
    kinds: dict[str, int] = {}
    for u in assets:
        k = _asset_kind(u)
        kinds[k] = kinds.get(k, 0) + 1

    blast = conflict_dict.get("blast_radius", len(assets))
    hours = round(blast * HOURS_PER_ASSET_MANUAL, 1)
    dollars = round(hours * BLENDED_ANALYST_RATE_USD)

    decision_assets = kinds.get("dashboard", 0) + kinds.get("model", 0)
    risk = (
        f"A wrong '{conflict_dict['metric']}' silently feeds {decision_assets} "
        f"decision surface(s) ({kinds.get('dashboard', 0)} dashboards, "
        f"{kinds.get('model', 0)} models) across "
        f"{len(conflict_dict['definitions'])} teams."
    )
    return {
        "impacted_assets": blast,
        "asset_breakdown": kinds,
        "manual_reconciliation_hours": hours,
        "estimated_manual_cost_usd": dollars,
        "risk_statement": risk,
    }


def portfolio_impact(report: dict) -> dict:
    """Roll conflict-level impact up to a headline number."""
    total_hours = 0.0
    total_assets = 0
    for c in report.get("conflicts", []):
        imp = c.get("impact") or estimate_conflict_impact(c)
        total_hours += imp["manual_reconciliation_hours"]
        total_assets += imp["impacted_assets"]
    return {
        "total_impacted_assets": total_assets,
        "total_manual_hours_avoided": round(total_hours, 1),
        "estimated_cost_avoided_usd": round(total_hours * BLENDED_ANALYST_RATE_USD),
    }
