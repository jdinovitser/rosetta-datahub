"""
Rosetta AI Intelligence layer.

Business-friendly metric naming rules
--------------------------------------
Known acronyms (all-caps): ARR, LTV, MRR, CLV, NPS, DAU, WAU, MAU, CAC, ARPU, ROI, GMV
Tilde-joined synonyms: customer_churn~attrition → "Customer Churn vs Customer Attrition"


Generates the structured explanation and executive dashboard that transforms
raw conflict data into enterprise-grade decision intelligence.

Each conflict gets:
  Finding    — what Rosetta discovered (one clear sentence)
  Evidence   — the data backing the finding (similarity scores, definitions)
  Impact     — downstream blast radius and business risk in plain English
  Recommendation — the concrete next action for the data governance team

The Executive Dashboard aggregates across all conflicts into three strategic
scores (Data Health, Governance Maturity, AI Readiness) plus prioritized
recommended actions — the summary a Chief Data Officer needs in 30 seconds.
"""
from __future__ import annotations

# Definitions untouched since before this date are flagged stale. Fixed (not
# "today - N days") so the offline demo and tests stay deterministic.
STALE_BEFORE = "2025-08-01"

# Known business acronyms that must stay all-caps when building display names.
_ACRONYMS = {"arr", "ltv", "mrr", "clv", "nps", "dau", "wau", "mau", "cac", "arpu", "roi", "gmv"}


def _friendly_metric(raw: str) -> str:
    """Convert an internal metric identifier to a business-readable label.

    Examples:
        active_user              → Active User
        arr                      → ARR
        customer_ltv             → Customer LTV
        customer_churn~attrition → Customer Churn vs Customer Attrition
    """
    if "~" in raw:
        parts = raw.split("~", 1)
        return f"{_friendly_metric(parts[0])} vs {_friendly_metric(parts[1])}"
    words = raw.replace("-", "_").split("_")
    return " ".join(w.upper() if w.lower() in _ACRONYMS else w.capitalize() for w in words)


def governance_signals(definitions: list[dict]) -> list[str]:
    """
    Extract governance red flags from a conflict's definitions: missing
    ownership, sensitive-data tags, stale metadata, and undocumented terms.
    These are real DataHub metadata signals (ownership, tags, lastModified,
    glossary membership) — the evidence layer behind the AI explanation.
    """
    signals: list[str] = []
    for d in definitions:
        dom = d.get("domain", "?")
        if not d.get("owner"):
            signals.append(f"{dom}: no owner assigned — stewardship unclear")
        if not d.get("term_urn"):
            signals.append(f"{dom}: not registered in the business glossary")
        tags = d.get("tags") or []
        if any(t in ("pii", "sensitive") for t in tags):
            signals.append(f"{dom}: handles sensitive/PII data")
        lm = d.get("last_modified") or ""
        if lm and lm < STALE_BEFORE:
            signals.append(f"{dom}: definition stale (last updated {lm})")
    return signals


# ── Per-conflict AI explanation ──────────────────────────────────────────────

def generate_ai_explanation(conflict_dict: dict) -> dict:
    """
    Return a Finding → Evidence → Impact → Recommendation block for one conflict.

    This is deterministic (no LLM needed) so the offline demo is reproducible
    and the structure is identical whether running against seed data or a live
    DataHub instance.
    """
    kind = conflict_dict["kind"]
    metric = conflict_dict["metric"]
    severity = conflict_dict["severity"]
    definitions = conflict_dict["definitions"]
    blast = conflict_dict.get("blast_radius", 0)
    imp = conflict_dict.get("impact", {})
    logic_sim = conflict_dict.get("logic_similarity", 0)
    confidence = conflict_dict.get("confidence", 0)

    domains = [d["domain"] for d in definitions]

    # ── Finding ──────────────────────────────────────────────────────────────
    if kind == "silent_contradiction":
        friendly = _friendly_metric(metric)
        finding = (
            f"'{friendly}' has {len(domains)} incompatible definitions across "
            f"{' and '.join(domains)} — same name, different computation."
        )
    else:  # hidden_synonym
        parts = metric.split("~", 1)
        name_a = _friendly_metric(parts[0])
        name_b = _friendly_metric(parts[1]) if len(parts) > 1 else _friendly_metric(metric)
        finding = (
            f"'{name_a}' and '{name_b}' are duplicate metrics across "
            f"{' and '.join(domains)} — same logic, different names."
        )

    # ── Evidence ─────────────────────────────────────────────────────────────
    def_snippets = "; ".join(
        f"{d['domain']}: \"{d['definition_text'][:72].rstrip()}…\""
        if len(d["definition_text"]) > 72 else f"{d['domain']}: \"{d['definition_text']}\""
        for d in definitions
    )
    signals = governance_signals(definitions)
    evidence = (
        f"Logic similarity {logic_sim:.0%}, confidence {confidence:.0%}. "
        f"Definitions: {def_snippets}."
        + (f" Governance signals: {'; '.join(signals)}." if signals else "")
    )

    # ── Impact ───────────────────────────────────────────────────────────────
    ai_note = ""
    if any(":mlModel:" in u or ":mlFeature" in u
           for d in definitions for u in d.get("affected_assets", [])):
        ai_note = " At least one ML model trains on this data — a wrong definition corrupts model signals silently."

    impact = (
        f"{severity.upper()} severity. {blast} downstream assets are at risk.{ai_note} "
        + (imp.get("risk_statement", "") or "")
    )

    # ── Recommendation ───────────────────────────────────────────────────────
    friendly_name = _friendly_metric(metric)
    if severity == "critical":
        rec = (
            f"Escalate immediately: align {' and '.join(domains)} leadership on a single "
            f"canonical definition for '{friendly_name}'. Freeze dependent pipelines until "
            f"resolved. In Connected Mode, Rosetta can execute a human-approved remediation plan and verify the resulting metadata where supported."
        )
    elif severity == "high":
        rec = (
            f"Schedule a cross-team definition review for '{friendly_name}' within this sprint. "
            f"Propose one canonical term, notify all {blast} asset owners, and deprecate "
            f"the conflicting variant."
        )
    elif severity == "medium":
        rec = (
            f"Open a data governance ticket for '{friendly_name}'. Draft a canonical definition "
            f"incorporating both teams' intent and circulate for sign-off in the next "
            f"governance review cycle."
        )
    else:
        rec = (
            f"Document the distinction between '{friendly_name}' definitions in the DataHub "
            f"glossary. Consider merging into one canonical term at the next quarterly "
            f"governance review."
        )

    return {
        "finding": finding,
        "evidence": evidence,
        "impact": impact,
        "recommendation": rec,
    }


# ── Executive Dashboard ──────────────────────────────────────────────────────

def compute_executive_dashboard(report: dict) -> dict:
    """
    Compute the three strategic scores and supporting data for the
    Executive Data Intelligence Dashboard.

    Scores are in [0, 100].  All coefficients are documented so the demo
    story is defensible to a technical audience.
    """
    conflicts = report.get("conflicts", [])
    summary = report.get("summary", {})
    total = summary.get("total_conflicts", 0)
    critical = summary.get("critical", 0)
    high = summary.get("high", 0)
    medium = sum(1 for c in conflicts if c.get("severity") == "medium")

    # ── Data Health Score ────────────────────────────────────────────────────
    # 100 = no conflicts; heavy penalty for critical (broken trust), lighter for lower severities
    data_health = max(0, 100 - critical * 18 - high * 10 - medium * 5 - (total - critical - high - medium) * 2)

    # ── Governance Maturity Score ────────────────────────────────────────────
    # Reflects: are terms documented? owned? consistent?
    # Silent contradictions are a stronger governance failure than synonyms.
    contradictions = sum(1 for c in conflicts if c.get("kind") == "silent_contradiction")
    synonyms = sum(1 for c in conflicts if c.get("kind") == "hidden_synonym")
    # governance red flags across all conflicted definitions (missing owners,
    # unregistered glossary terms, sensitive data, stale definitions)
    all_signals = [
        s for c in conflicts for s in governance_signals(c.get("definitions", []))
    ]
    missing_owners = sum("no owner" in s for s in all_signals)
    stale_defs = sum("stale" in s for s in all_signals)
    sensitive = sum("sensitive/PII" in s for s in all_signals)
    gov_maturity = max(0, 100 - contradictions * 6 - synonyms * 4 - critical * 4
                       - high * 2 - missing_owners * 8 - stale_defs * 3 - sensitive * 2)
    gov_maturity = min(gov_maturity, 88)  # realistic cap: governance is never "perfect"

    # ── AI Readiness Score ───────────────────────────────────────────────────
    # AI pipelines fail silently when metric definitions are wrong.
    # Critical conflicts involving ML assets receive the heaviest penalty.
    ml_conflicts = sum(
        1 for c in conflicts
        if any(":mlModel:" in u or ":mlFeature" in u
               for d in c.get("definitions", []) for u in d.get("affected_assets", []))
    )
    ai_readiness = max(0, 100 - critical * 22 - high * 12 - ml_conflicts * 8 - medium * 4)

    # ── Assets Impacted ──────────────────────────────────────────────────────
    assets_impacted = summary.get("assets_at_risk", 0)
    impact_summary = summary.get("impact", {})

    # ── Critical Risks ───────────────────────────────────────────────────────
    critical_risks = []
    for c in conflicts:
        if c.get("severity") in ("critical", "high"):
            ai_exp = c.get("ai_explanation", {})
            critical_risks.append({
                "metric": c["metric"],
                "severity": c["severity"],
                "blast_radius": c.get("blast_radius", 0),
                "description": ai_exp.get("finding") or c.get("rationale", ""),
                "recommendation": ai_exp.get("recommendation", ""),
            })

    # ── Recommended Actions ──────────────────────────────────────────────────
    actions = []
    if critical > 0:
        actions.append({
            "priority": "critical",
            "action": f"Resolve {critical} critical semantic conflict(s) to prevent AI model corruption and executive reporting errors.",
        })
    if high > 0:
        actions.append({
            "priority": "high",
            "action": f"Review {high} high-severity metric definition(s) with cross-functional data owners this sprint.",
        })
    if synonyms > 0:
        actions.append({
            "priority": "medium",
            "action": f"Consolidate {synonyms} hidden synonym pair(s) into single canonical GlossaryTerms to reduce data duplication.",
        })
    if missing_owners > 0:
        actions.append({
            "priority": "high",
            "action": f"Assign owners to {missing_owners} unowned metric definition(s) — unclear stewardship blocks every reconciliation.",
        })
    if sensitive > 0:
        actions.append({
            "priority": "high",
            "action": f"Audit {sensitive} conflicted definition(s) touching sensitive/PII data for governance and compliance exposure.",
        })
    if stale_defs > 0:
        actions.append({
            "priority": "medium",
            "action": f"Refresh {stale_defs} stale metric definition(s) not updated since {STALE_BEFORE}.",
        })
    actions.append({
        "priority": "low",
        "action": "Enable automated Rosetta scans on every DataHub ingestion to catch new conflicts at the source.",
    })
    if ai_readiness < 60:
        actions.insert(0, {
            "priority": "critical",
            "action": "Pause AI/ML deployments that depend on conflicted metrics until definitions are canonicalized.",
        })

    return {
        "scores": {
            "data_health": data_health,
            "governance_maturity": gov_maturity,
            "ai_readiness": ai_readiness,
        },
        "critical_risks": critical_risks,
        "assets_impacted": assets_impacted,
        "cost_avoided_usd": impact_summary.get("estimated_cost_avoided_usd", 0),
        "recommended_actions": actions,
        "meta": {
            "total_conflicts": total,
            "critical": critical,
            "high": high,
            "generated_at": report.get("generated_at", ""),
        },
    }
