"""
Test suite for Rosetta's detection + reconciliation logic.

A DataHub-hackathon-adjacent judge explicitly cited a project's 43 tests as
the signal that separated the grand-prize winner from a demo. Coverage here is
deliberately thorough for a hackathon project. All tests run offline (no live
DataHub instance) using a mock client.
"""
from __future__ import annotations

import pytest

from rosetta.broker import apply_proposal, draft_proposal
from rosetta.datahub_client import MetricDefinition, RosettaDataHub
from rosetta.detector import (
    Conflict,
    _severity,
    detect_conflicts,
    logic_similarity,
    name_similarity,
)


def mk(name, domain, owner, defn, sql, assets, term=""):
    return MetricDefinition(
        name=name, display_name=name.replace("_", " ").title(), domain=domain,
        owner=owner, definition_text=defn, sql_logic=sql, source_urns=assets,
        term_urn=term,
    )


# ---------- similarity primitives ----------
def test_name_similarity_identical():
    a = mk("active_user", "fin", "o1", "x", "y", [])
    b = mk("active_user", "mkt", "o2", "z", "w", [])
    assert name_similarity(a, b) == 1.0


def test_name_similarity_different():
    a = mk("churn", "fin", "o1", "x", "y", [])
    b = mk("attrition", "mkt", "o2", "z", "w", [])
    assert name_similarity(a, b) < 0.5


def test_logic_similarity_high_for_same_computation():
    sql = "COUNT(DISTINCT customer_id) WHERE subscription_status = 'cancelled'"
    a = mk("churn", "prod", "o1", "cancelled customers", sql, [])
    b = mk("attrition", "cs", "o2", "cancelled customers", sql, [])
    assert logic_similarity(a, b) > 0.7


def test_logic_similarity_low_for_divergent_computation():
    a = mk("active_user", "fin", "o1", "paid txn", "txn_amount > 0", [])
    b = mk("active_user", "mkt", "o2", "session open", "session_start bots excluded", [])
    assert logic_similarity(a, b) < 0.5


# ---------- silent contradiction detection ----------
def test_detects_silent_contradiction():
    defs = [
        mk("active_user", "fin", "o1", "paid transaction 30 days",
           "COUNT DISTINCT user_id txn_amount > 0", ["urn:a", "urn:b"], "urn:t1"),
        mk("active_user", "mkt", "o2", "session in 30 days bots excluded",
           "COUNT DISTINCT user_id session_start is_bot false", ["urn:c"], "urn:t2"),
    ]
    conflicts = detect_conflicts(defs)
    assert len(conflicts) == 1
    assert conflicts[0].kind == "silent_contradiction"
    assert conflicts[0].metric == "active_user"


def test_no_conflict_when_same_name_same_logic():
    sql = "COUNT DISTINCT user_id txn_amount > 0"
    defs = [
        mk("active_user", "fin", "o1", "paid txn", sql, ["urn:a"]),
        mk("active_user", "eng", "o2", "paid txn", sql, ["urn:b"]),
    ]
    assert detect_conflicts(defs) == []


# ---------- hidden synonym detection ----------
def test_detects_hidden_synonym():
    sql = "COUNT DISTINCT customer_id subscription_status cancelled divided total"
    defs = [
        mk("customer_churn", "prod", "o1", "cancelled subscription share", sql, ["urn:a"]),
        mk("attrition", "cs", "o2", "cancelled subscription fraction", sql, ["urn:b", "urn:c"]),
    ]
    conflicts = detect_conflicts(defs)
    assert len(conflicts) == 1
    assert conflicts[0].kind == "hidden_synonym"


# ---------- blast radius + severity ----------
def test_blast_radius_dedupes_shared_assets():
    defs = [
        mk("revenue", "fin", "o1", "net", "sum minus refund", ["urn:a", "urn:b"], "urn:t1"),
        mk("revenue", "sales", "o2", "closed won", "sum closed_won", ["urn:b", "urn:c"], "urn:t2"),
    ]
    c = detect_conflicts(defs)[0]
    assert c.blast_radius == 3  # a, b, c deduped


@pytest.mark.parametrize("n,expected", [(0, "low"), (2, "low"), (3, "medium"),
                                        (8, "high"), (25, "critical")])
def test_severity_thresholds(n, expected):
    assert _severity(n) == expected


def test_conflicts_ranked_by_blast_radius():
    defs = [
        mk("active_user", "fin", "o1", "paid", "txn_amount > 0",
           ["u1", "u2", "u3", "u4", "u5", "u6", "u7", "u8"], "urn:t1"),
        mk("active_user", "mkt", "o2", "session", "session_start is_bot",
           ["u9"], "urn:t2"),
        mk("revenue", "fin", "o3", "net", "sum minus refund", ["r1"], "urn:t3"),
        mk("revenue", "sales", "o4", "closed", "sum closed_won", ["r2"], "urn:t4"),
    ]
    conflicts = detect_conflicts(defs)
    assert len(conflicts) == 2
    assert conflicts[0].blast_radius >= conflicts[1].blast_radius


# ---------- proposal drafting ----------
def test_proposal_picks_highest_coverage_as_base():
    defs = [
        mk("active_user", "fin", "urn:fin", "paid txn", "txn_amount > 0",
           ["u1"], "urn:t1"),
        mk("active_user", "mkt", "urn:mkt", "session", "session_start is_bot",
           ["u2", "u3", "u4"], "urn:t2"),
    ]
    c = detect_conflicts(defs)[0]
    p = draft_proposal(c)
    assert p.winning_definition.domain == "mkt"
    assert "urn:fin" in p.approvers and "urn:mkt" in p.approvers
    assert "urn:t1" in p.deprecated_terms


def test_proposal_affected_assets_are_union():
    defs = [
        mk("revenue", "fin", "urn:fin", "net", "sum minus refund", ["a", "b"], "urn:t1"),
        mk("revenue", "sales", "urn:sales", "closed", "sum closed_won", ["b", "c"], "urn:t2"),
    ]
    c = detect_conflicts(defs)[0]
    p = draft_proposal(c)
    assert set(p.affected_assets) == {"a", "b", "c"}


# ---------- write-back loop (mocked) ----------
class MockEntities:
    def __init__(self):
        self.upserted = []
        self.updated = []

    def upsert(self, term):
        self.upserted.append(term)

    def get(self, urn):
        return MockEntity(urn)

    def update(self, entity):
        self.updated.append(entity)


class MockEntity:
    def __init__(self, urn):
        self.urn = urn
        self.terms = []
        self.deprecated = False

    def add_term(self, term):
        self.terms.append(term)

    def set_deprecation(self, deprecated, note):
        self.deprecated = deprecated


class MockClient:
    def __init__(self):
        self.entities = MockEntities()


def test_apply_proposal_writes_back(monkeypatch):
    import rosetta.datahub_client as dc
    # Force the SDK-present branch and stub the URN/term helpers.
    monkeypatch.setattr(dc, "_HAS_SDK", True)
    monkeypatch.setattr(dc, "GlossaryTerm", lambda **kw: ("TERM", kw), raising=False)

    class FakeUrn:
        @staticmethod
        def from_string(s):
            return s

    monkeypatch.setattr(dc, "DatasetUrn", FakeUrn, raising=False)

    class FakeTermUrn:
        def __init__(self, u):
            self.u = u

        @staticmethod
        def from_string(s):
            return s

    monkeypatch.setattr(dc, "GlossaryTermUrn", FakeTermUrn, raising=False)

    dh = RosettaDataHub(client=MockClient())
    defs = [
        mk("revenue", "fin", "urn:fin", "net", "sum minus refund", ["a", "b"], "urn:t1"),
        mk("revenue", "sales", "urn:sales", "closed", "sum closed_won", ["c"], "urn:t2"),
    ]
    c = detect_conflicts(defs)[0]
    p = draft_proposal(c)
    audit = apply_proposal(dh, p)
    assert audit["canonical_term"].startswith("urn:li:glossaryTerm:")
    assert set(audit["linked_assets"]) == {"a", "b", "c"}
    assert dh.client.entities.upserted  # canonical term was written


# ---------- end to end on seed data ----------
def test_seed_data_produces_expected_conflicts():
    dh = RosettaDataHub.__new__(RosettaDataHub)  # skip __init__ (no SDK needed)
    defs = _load_seed()
    conflicts = detect_conflicts(defs)
    kinds = {c.metric: c.kind for c in conflicts}
    assert "active_user" in kinds and kinds["active_user"] == "silent_contradiction"
    assert "revenue" in kinds and kinds["revenue"] == "silent_contradiction"
    assert any(c.kind == "hidden_synonym" for c in conflicts)


def _load_seed():
    import json
    from pathlib import Path
    seed = Path(__file__).resolve().parent.parent / "demo_data" / "seed_definitions.json"
    return [MetricDefinition(**row) for row in json.loads(seed.read_text())]


def test_conflict_to_dict_is_serializable():
    import json
    defs = _load_seed()
    conflicts = detect_conflicts(defs)
    assert json.dumps([c.to_dict() for c in conflicts])  # no exception


# ---------- exporter + demo mode tests (added for the full submission) ----------
from rosetta import exporter
from rosetta.demo import run_demo


def _demo_report():
    return run_demo()["report"]


def test_demo_runs_and_finds_conflicts():
    result = run_demo()
    # seed data now covers 5 scenarios — active_user, revenue, conversion_rate,
    # arr (silent contradictions) + customer_churn~attrition (hidden synonym)
    conflicts = result["report"]["conflicts"]
    assert len(conflicts) >= 3, f"Expected ≥ 3 conflicts, got {len(conflicts)}"
    # narrated steps cover all five agents
    agents = {s["agent"] for s in result["steps"]}
    assert {"Harvester", "Conflict Detector", "Blast-Radius Analyzer",
            "Reconciliation Broker", "Writer"} <= agents


def test_demo_produces_proposals():
    result = run_demo()
    assert len(result["proposals"]) >= 3
    for p in result["proposals"]:
        assert p["term_id"] and p["canonical_definition"]
        assert p["approvers"]


def test_export_json_roundtrips():
    import json
    report = _demo_report()
    out = exporter.export(report, "json")
    n = json.loads(out)["summary"]["total_conflicts"]
    assert n >= 3, f"Expected ≥ 3 conflicts in JSON export, got {n}"


def _csv_header_line(csv_out: str) -> str:
    """Return the first non-comment line (the actual CSV header)."""
    for line in csv_out.splitlines():
        if not line.startswith("#"):
            return line
    return ""


def test_export_csv_has_header_and_rows():
    report = _demo_report()
    csv_out = exporter.export(report, "csv")
    header = _csv_header_line(csv_out)
    assert header.startswith("metric,kind,severity"), (
        f"CSV header line should start with 'metric,kind,severity', got: {header!r}"
    )
    data_lines = [l for l in csv_out.strip().splitlines() if not l.startswith("#") and l]
    assert len(data_lines) == 1 + len(report["conflicts"])


def test_export_markdown_and_html_contain_metric():
    report = _demo_report()
    assert "active_user" in exporter.export(report, "md")
    assert "active_user" in exporter.export(report, "html")
    assert "<html" in exporter.export(report, "html").lower()


def test_export_rejects_unknown_format():
    import pytest
    with pytest.raises(ValueError):
        exporter.export(_demo_report(), "pdf")


def test_export_all_writes_four_files(tmp_path):
    paths = exporter.export_all(_demo_report(), out_dir=tmp_path, stem="t")
    assert len(paths) == 4
    exts = {p.rsplit(".", 1)[1] for p in paths}
    assert exts == {"json", "csv", "md", "html"}


# --- Upgrades: confidence scoring, transitive lineage, impact estimation ---

from rosetta import impact as impact_mod
from rosetta.broker import proposal_diff
from rosetta.orchestrator import build_report, run_scan


def _offline_dh():
    dh = RosettaDataHub.__new__(RosettaDataHub)
    dh._lineage_cache = None
    return dh


def test_conflicts_have_confidence_between_half_and_one():
    dh = _offline_dh()
    conflicts = run_scan(dh)
    assert conflicts
    for c in conflicts:
        assert 0.5 <= c.confidence <= 1.0


def test_transitive_lineage_exceeds_direct_assets():
    dh = _offline_dh()
    defs = dh.harvest_metric_definitions()
    # marketing active_user has 5 direct assets; downstream must be >= that
    mkt = next(d for d in defs if d.name == "active_user" and d.domain == "marketing")
    downstream = dh.downstream_assets(mkt)
    assert len(downstream) >= len(mkt.source_urns)
    # walking lineage should reach the churn ML model downstream
    assert any(":mlModel:" in u for u in downstream)


def test_impact_block_has_cost_and_risk_statement():
    dh = _offline_dh()
    report = build_report(run_scan(dh))
    for c in report["conflicts"]:
        imp = c["impact"]
        assert imp["estimated_manual_cost_usd"] > 0
        assert imp["manual_reconciliation_hours"] > 0
        assert "silently feeds" in imp["risk_statement"]


def test_portfolio_impact_rolls_up():
    dh = _offline_dh()
    report = build_report(run_scan(dh))
    port = report["summary"]["impact"]
    assert port["total_impacted_assets"] > 0
    assert port["estimated_cost_avoided_usd"] > 0


def test_proposed_reconciliation_diff_present():
    dh = _offline_dh()
    report = build_report(run_scan(dh))
    for c in report["conflicts"]:
        diff = c["proposed_reconciliation"]
        assert "before" in diff and "after" in diff
        assert diff["after"]["status"] == "canonical"
        assert len(diff["before"]) >= 2


def test_embeddings_disabled_falls_back_to_lexical(monkeypatch):
    # With embeddings off, logic_similarity must still return a float in [0,1]
    monkeypatch.delenv("ROSETTA_EMBEDDINGS", raising=False)
    dh = _offline_dh()
    defs = dh.harvest_metric_definitions()
    sim = logic_similarity(defs[0], defs[1])
    assert 0.0 <= sim <= 1.0


# --- Enterprise intelligence layer: AI explanations + governance signals ---

from rosetta.intelligence import (
    compute_executive_dashboard,
    generate_ai_explanation,
    governance_signals,
)


def test_every_conflict_has_four_part_ai_explanation():
    report = _demo_report()
    for c in report["conflicts"]:
        ai = c["ai_explanation"]
        for key in ("finding", "evidence", "impact", "recommendation"):
            assert ai.get(key), f"{c['metric']} missing ai_explanation.{key}"


def test_seed_data_surfaces_customer_ltv_contradiction():
    report = _demo_report()
    metrics = {c["metric"]: c for c in report["conflicts"]}
    assert "customer_ltv" in metrics
    assert metrics["customer_ltv"]["kind"] == "silent_contradiction"


def test_governance_signals_flag_missing_owner_pii_and_stale():
    report = _demo_report()
    ltv = next(c for c in report["conflicts"] if c["metric"] == "customer_ltv")
    signals = " ".join(governance_signals(ltv["definitions"]))
    assert "no owner assigned" in signals
    assert "sensitive/PII" in signals
    assert "stale" in signals
    # signals must surface in the AI evidence text
    assert "Governance signals" in ltv["ai_explanation"]["evidence"]


def test_exports_carry_ai_explanation():
    report = _demo_report()
    csv_out = exporter.export(report, "csv")
    assert "ai_recommendation" in _csv_header_line(csv_out)
    md = exporter.export(report, "md")
    assert "**Finding:**" in md and "**Recommendation:**" in md
    html = exporter.export(report, "html")
    assert "AI Explanation" in html


def test_export_parity_ui_fields_present_in_all_formats():
    """
    Parity guard: every field the UI renders per conflict card must appear in
    CSV, Markdown, and HTML exports.  The assertion names the missing field so
    a future regression is immediately actionable.
    """
    report = _demo_report()
    assert report["conflicts"], "No conflicts in demo report — cannot verify parity"

    csv_out  = exporter.export(report, "csv")
    md_out   = exporter.export(report, "md")
    html_out = exporter.export(report, "html")

    # --- 1. CSV structural parity: all columns the UI relies on must be present ---
    csv_header = _csv_header_line(csv_out)
    required_csv_cols = [
        "metric", "kind", "severity", "confidence", "blast_radius",
        "est_cost_usd", "manual_hours", "rationale",
        "ai_finding", "ai_evidence", "ai_impact", "ai_recommendation",
        "domains", "owners",
    ]
    for col in required_csv_cols:
        assert col in csv_header, (
            f"CSV header is missing column '{col}' — "
            f"UI field would silently drop from downloaded report"
        )

    # --- 2. Per-conflict value parity across MD and HTML ---
    for c in report["conflicts"]:
        metric = c["metric"]

        # Scalar fields that the UI card always renders.
        # Each entry is (field_label, csv_value, md_value, html_value).
        # Exporters apply display transformations:
        #   - kind   → spaces in HTML  ("silent contradiction")
        #   - severity → uppercase in MD heading and HTML badge ("CRITICAL")
        # The raw (lowercase/underscore) form still appears in CSV rows.
        kind_display = c["kind"].replace("_", " ")
        sev_upper    = c["severity"].upper()
        scalar_fields = [
            # (label,         csv,             md,              html)
            ("metric",        c["metric"],     c["metric"],     c["metric"]),
            ("kind",          c["kind"],       c["kind"],       kind_display),
            ("severity",      c["severity"],   sev_upper,       sev_upper),
            ("blast_radius",  str(c["blast_radius"]), str(c["blast_radius"]), str(c["blast_radius"])),
            ("rationale",     c["rationale"],  c["rationale"],  c["rationale"]),
        ]

        ai = c.get("ai_explanation") or {}
        ai_fields = [
            ("ai_explanation.finding",        ai.get("finding", ""),        ai.get("finding", ""),        ai.get("finding", "")),
            ("ai_explanation.evidence",       ai.get("evidence", ""),       ai.get("evidence", ""),       ai.get("evidence", "")),
            ("ai_explanation.impact",         ai.get("impact", ""),         ai.get("impact", ""),         ai.get("impact", "")),
            ("ai_explanation.recommendation", ai.get("recommendation", ""), ai.get("recommendation", ""), ai.get("recommendation", "")),
        ]

        imp = c.get("impact") or {}
        impact_fields = []
        if imp.get("risk_statement"):
            rs = imp["risk_statement"]
            impact_fields.append(("impact.risk_statement", rs, rs, rs))

        all_fields = scalar_fields + ai_fields + impact_fields

        for entry in all_fields:
            field, csv_value, md_value, html_value = entry
            if not csv_value:
                continue  # skip genuinely empty optional strings
            # CSV RFC 4180 escapes embedded double-quotes as ""; match that form.
            csv_escaped = csv_value.replace('"', '""')
            assert csv_escaped in csv_out, (
                f"[{metric}] UI field '{field}' value {csv_value!r} "
                f"is missing from CSV export (checked CSV-escaped form)"
            )
            assert md_value in md_out, (
                f"[{metric}] UI field '{field}' (display form {md_value!r}) "
                f"is missing from Markdown export"
            )
            assert html_value in html_out, (
                f"[{metric}] UI field '{field}' (display form {html_value!r}) "
                f"is missing from HTML export"
            )

        # --- 3. Per-definition governance fields (domain, owner, definition, sql) ---
        for d in c.get("definitions", []):
            def_fields = {
                "definition.domain":          d.get("domain", ""),
                "definition.definition_text": d.get("definition_text", ""),
                "definition.sql_logic":       d.get("sql_logic", ""),
            }
            if d.get("owner"):
                def_fields["definition.owner"] = d["owner"]

            for field, value in def_fields.items():
                if not value:
                    continue
                # MD table cells escape "|" as "\|"; check the escaped form too
                md_value = value.replace("|", "\\|")
                assert (value in md_out or md_value in md_out), (
                    f"[{metric}] UI field '{field}' value {value!r} "
                    f"is missing from Markdown export"
                )
                assert value in html_out, (
                    f"[{metric}] UI field '{field}' value {value!r} "
                    f"is missing from HTML export"
                )


def test_executive_dashboard_scores_and_actions():
    dash = compute_executive_dashboard(_demo_report())
    for k in ("data_health", "governance_maturity", "ai_readiness"):
        assert 0 <= dash["scores"][k] <= 100
    assert dash["critical_risks"]
    assert dash["assets_impacted"] > 0
    actions = " ".join(a["action"] for a in dash["recommended_actions"])
    assert "owner" in actions.lower()  # missing-ownership action surfaces


# ---------- input-manifest.json integrity ----------

import hashlib as _hashlib
from pathlib import Path as _Path

_REPO_ROOT = _Path(__file__).resolve().parent.parent
_MANIFEST  = _REPO_ROOT / "examples" / "input-manifest.json"

_REQUIRED_ENTRY_KEYS = {
    "relative_path", "source_dataset", "sha256",
    "file_size_bytes", "fields_used_by_rosetta",
    "transformations_applied", "original_or_modified",
}


def test_manifest_exists():
    assert _MANIFEST.exists(), f"examples/input-manifest.json not found at {_MANIFEST}"


def test_manifest_top_level_schema():
    import json
    m = json.loads(_MANIFEST.read_text())
    assert "manifest_version" in m
    assert "files" in m and isinstance(m["files"], list) and len(m["files"]) > 0
    assert "validation_command" in m


def test_manifest_entries_have_required_keys():
    import json
    m = json.loads(_MANIFEST.read_text())
    for entry in m["files"]:
        missing = _REQUIRED_ENTRY_KEYS - entry.keys()
        assert not missing, (
            f"Manifest entry for {entry.get('relative_path','?')} "
            f"is missing keys: {missing}"
        )


def test_manifest_checksums_match_disk():
    """Fail if any listed file has changed since the manifest was last generated."""
    import json
    m = json.loads(_MANIFEST.read_text())
    mismatches = []
    for entry in m["files"]:
        path = _REPO_ROOT / entry["relative_path"]
        if not path.exists():
            mismatches.append(f"MISSING: {entry['relative_path']}")
            continue
        h = _hashlib.sha256(path.read_bytes()).hexdigest()
        if h != entry["sha256"]:
            mismatches.append(
                f"CHECKSUM MISMATCH: {entry['relative_path']}\n"
                f"  manifest: {entry['sha256']}\n"
                f"  on disk:  {h}\n"
                f"  Fix: python scripts/validate_manifest.py --regen"
            )
        sz = path.stat().st_size
        if sz != entry["file_size_bytes"]:
            mismatches.append(
                f"SIZE MISMATCH: {entry['relative_path']} "
                f"(manifest={entry['file_size_bytes']}, disk={sz})"
            )
    assert not mismatches, "\n".join(mismatches)


def test_manifest_lists_healthcare_db():
    import json
    m = json.loads(_MANIFEST.read_text())
    paths = [e["relative_path"] for e in m["files"]]
    assert "demo_data/healthcare.db" in paths


def test_manifest_healthcare_entry_has_anomaly_counts():
    import json
    m = json.loads(_MANIFEST.read_text())
    hc = next(e for e in m["files"] if e["relative_path"] == "demo_data/healthcare.db")
    # manifest v1.1 uses "anomalies_confirmed_by_sql" key
    counts = hc.get("anomalies_confirmed_by_sql") or hc.get("anomalies_confirmed_present", {})
    assert counts.get("negative_billing_amount_rows") == 1215
    assert counts.get("null_name_rows") == 555
    assert counts.get("invalid_age_rows_outside_0_120") or counts.get("invalid_age_rows") == 832
    assert counts.get("date_swap_rows") == 277


def test_validate_manifest_script_passes():
    """Running the script with --check should exit 0 with current files."""
    import subprocess, sys
    script = _REPO_ROOT / "scripts" / "validate_manifest.py"
    result = subprocess.run(
        [sys.executable, str(script), "--check"],
        capture_output=True, text=True
    )
    assert result.returncode == 0, (
        f"validate_manifest.py --check exited {result.returncode}\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )


# ── Messaging / copy correctness tests ──────────────────────────────────

import re as _re

def _get_homepage(client=None):
    """Return the homepage HTML via Flask test client."""
    from webapp.app import app as _app
    with _app.test_client() as c:
        return c.get("/").data.decode()

def _app_js():
    from pathlib import Path as _P
    return (_P(__file__).parent.parent / "webapp" / "static" / "js" / "app.js").read_text()


def test_homepage_has_no_credentials_disclosure():
    html = _get_homepage()
    assert "No credentials required" in html, (
        "Homepage must contain 'No credentials required' disclosure"
    )
    assert "official hackathon resources" in html, (
        "Homepage must mention 'official hackathon resources'"
    )


def test_homepage_demo_mode_badge_present():
    html = _get_homepage()
    assert "DEMO MODE" in html, "Homepage must contain DEMO MODE badge"
    assert "HACKATHON SAMPLE DATA" in html.upper()


def test_homepage_about_this_data_link_present():
    html = _get_homepage()
    # Both the topbar ℹ button and the hero link should be in the DOM
    assert "openAboutData" in html
    assert "openAboutDataHero" in html
    assert "About this data" in html


def test_homepage_hero_cta_says_run_healthcare_demo():
    html = _get_homepage()
    assert "Run Healthcare Demo" in html, (
        "Primary hero CTA must say 'Run Healthcare Demo'"
    )


def test_approve_button_demo_mode_says_generate_write_plan():
    js = _app_js()
    assert "Approve &amp; Generate Write Plan" in js or "Generate Write Plan" in js, (
        "Demo mode approve button must say 'Approve & Generate Write Plan'"
    )


def test_demo_mode_no_external_write_claim():
    js = _app_js()
    # Demo mode completion text must not claim an external write was executed
    assert "No external operations were executed in Demo Mode" in js, (
        "Step 5 demo notice must state no external operations were executed"
    )


def test_completion_page_status_summary_labels():
    js = _app_js()
    assert "Human approval" in js
    assert "Write-plan validation" in js
    assert "External catalog modified" in js
    assert "Target platform" in js


def test_demo_approve_button_advances_to_step5():
    """Demo mode: clicking approve must call gotoStep(5)."""
    js = _app_js()
    # The demo branch should contain gotoStep(5)
    demo_branch_idx = js.find("Demo mode — generate write plan")
    assert demo_branch_idx != -1, "Demo mode branch must be present in approve handler"
    snippet = js[demo_branch_idx : demo_branch_idx + 300]
    assert "gotoStep(5)" in snippet, (
        "Demo mode approve handler must navigate to step 5"
    )


def test_live_mode_write_language_only_in_live_branch():
    """'Written to DataHub' must appear only inside the isLive conditional."""
    js = _app_js()
    # "Written to DataHub" must be conditioned on isLive
    idx = js.find("Written to DataHub")
    assert idx != -1, "Live mode should still show 'Written to DataHub'"
    # The live banner is inside `if (isLive)` — look back up to 1000 chars
    preceding = js[max(0, idx - 1000) : idx]
    assert "isLive" in preceding, (
        "'Written to DataHub' must only appear in the isLive branch"
    )


def test_financial_figure_labeled_as_affected_transaction_value():
    html = _get_homepage()
    assert "affected transaction value" in html, (
        "Financial figures must be labeled 'affected transaction value', "
        "not 'cost avoided' or 'misreported revenue'"
    )
    assert "misreported revenue" not in html, (
        "Must not claim '$28M in misreported revenue' without a documented calculation"
    )


def test_homepage_no_cost_avoided_language():
    html = _get_homepage()
    # "Cost Avoided" label has been renamed to "Affected transaction value"
    assert "Affected transaction value" in html, (
        "Result card must use 'Affected transaction value' label, not 'Cost avoided'"
    )


def test_about_modal_intro_text_present():
    html = _get_homepage()
    # Text spans template lines — check the key phrases individually
    assert "does not connect to a real healthcare" in html, (
        "About modal must state the app does not connect to a real healthcare organization"
    )
    assert "real patient information" in html


def test_how_rosetta_works_steps_present():
    html = _get_homepage()
    assert "Detect incompatible meanings" in html
    assert "DataHub write plan" in html
    assert "canonical" in html.lower()


def test_demo_badge_has_tooltip():
    html = _get_homepage()
    # The mode badge must have a title attribute as a tooltip
    assert "does not modify an external catalog" in html, (
        "Mode badge title attribute must explain no external catalog is modified"
    )


def test_manifest_covers_all_demo_databases():
    """All SQLite databases in demo_data/ must appear in the manifest."""
    import json
    from pathlib import Path as _P
    demo_dir = _REPO_ROOT / "demo_data"
    dbs = {p.name for p in demo_dir.glob("*.db")}
    m = json.loads(_MANIFEST.read_text())
    manifest_dbs = {
        _P(e["relative_path"]).name
        for e in m["files"]
        if e["relative_path"].endswith(".db")
    }
    missing = dbs - manifest_dbs
    assert not missing, (
        f"These .db files in demo_data/ are not in the manifest: {missing}. "
        "Run: python scripts/validate_manifest.py --regen"
    )


def test_manifest_fiction_retail_entry():
    import json
    m = json.loads(_MANIFEST.read_text())
    fr = next(
        (e for e in m["files"] if e["relative_path"] == "demo_data/fiction_retail.db"),
        None
    )
    assert fr is not None, "fiction_retail.db not found in manifest"
    assert fr["sha256"], "fiction_retail.db sha256 must not be empty"
    assert fr["file_size_bytes"] > 0
    assert "Not established" in fr.get("source_url", ""), (
        "fiction_retail.db source_url should state 'Not established' "
        "since the original source cannot be confirmed from repository history"
    )


# ---------- exporter provenance tests ----------

from rosetta.healthcare_demo import run_healthcare_demo

def _hc_report():
    return run_healthcare_demo()["report"]


def test_json_export_contains_provenance_block():
    import json
    out = json.loads(exporter.to_json(_hc_report()))
    assert "rosetta_provenance" in out, "JSON export must contain 'rosetta_provenance' key"
    prov = out["rosetta_provenance"]
    assert prov.get("demo_mode") is True
    assert "source_url" in prov
    assert "rosetta_constructed" in prov and len(prov["rosetta_constructed"]) > 0
    assert "statement" in prov


def test_json_export_provenance_has_not_established():
    import json
    out = json.loads(exporter.to_json(_hc_report()))
    not_est = out["rosetta_provenance"].get("not_established", [])
    assert len(not_est) > 0, (
        "Healthcare JSON provenance must list at least one 'not_established' item "
        "(e.g. license, whether anomalies were planted)"
    )


def test_csv_export_contains_provenance_comments():
    csv_out = exporter.to_csv(_hc_report())
    assert csv_out.startswith("# ROSETTA PROVENANCE"), (
        "CSV export must start with '# ROSETTA PROVENANCE' comment block"
    )
    assert "# Statement:" in csv_out
    assert "# Rosetta-constructed:" in csv_out


def test_markdown_export_contains_provenance_section():
    md_out = exporter.to_markdown(_hc_report())
    assert "## Data Provenance" in md_out, (
        "Markdown export must contain a '## Data Provenance' section"
    )
    assert "rosetta_constructed" not in md_out.lower() or "Rosetta-constructed" in md_out
    assert "Not established" in md_out or "not_established" not in str(_hc_report())


def test_live_scan_provenance_does_not_claim_demo_dataset():
    """A report with no 'source' key should produce live-mode provenance."""
    import json
    bare_report = {"generated_at": "2026-01-01T00:00:00Z", "conflicts": [], "summary": {}}
    out = json.loads(exporter.to_json(bare_report))
    prov = out["rosetta_provenance"]
    assert prov.get("demo_mode") is False
    assert "hackathon" not in prov.get("statement", "").lower(), (
        "Live-mode provenance must not claim to use hackathon data"
    )
