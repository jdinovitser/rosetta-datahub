"""
Healthcare data source for Rosetta.

Reads DataHub sample data supplied through the official Build with DataHub
Agent Hackathon resources (healthcare.db) directly from SQLite — no DataHub
instance required. Rosetta converts the supplied metadata and scenarios into a
reproducible local evaluation graph. No real patient or personal information
is used. Returns MetricDefinition objects that feed the existing five-agent
Rosetta pipeline unchanged.

Pipeline topology (from add_lineage.py):
    raw_patients → staging_patients → mart_billing
                                    → mart_demographics
    Views: v_staging_from_raw, v_billing_from_staging, v_demographics_from_staging

Ownership (from add_metadata.py):
    clinical_team  → raw_patients, staging_patients
    finance_team   → mart_billing
    research_team  → mart_demographics
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .datahub_client import MetricDefinition

_DB_PATH = Path(__file__).resolve().parent.parent / "demo_data" / "healthcare.db"

# DataHub-style URNs for the healthcare pipeline tables
_PLATFORM = "sqlite"
_ENV = "PROD"
_URN = {
    "raw":     f"urn:li:dataset:(urn:li:dataPlatform:{_PLATFORM},healthcare.raw_patients,{_ENV})",
    "staging": f"urn:li:dataset:(urn:li:dataPlatform:{_PLATFORM},healthcare.staging_patients,{_ENV})",
    "billing": f"urn:li:dataset:(urn:li:dataPlatform:{_PLATFORM},healthcare.mart_billing,{_ENV})",
    "demo":    f"urn:li:dataset:(urn:li:dataPlatform:{_PLATFORM},healthcare.mart_demographics,{_ENV})",
    "v_stg":   f"urn:li:dataset:(urn:li:dataPlatform:{_PLATFORM},healthcare.v_staging_from_raw,{_ENV})",
    "v_bill":  f"urn:li:dataset:(urn:li:dataPlatform:{_PLATFORM},healthcare.v_billing_from_staging,{_ENV})",
    "v_demo":  f"urn:li:dataset:(urn:li:dataPlatform:{_PLATFORM},healthcare.v_demographics_from_staging,{_ENV})",
}

# Lineage: each table/view → its immediate downstream consumers
_DOWNSTREAM: dict[str, list[str]] = {
    _URN["raw"]:     [_URN["staging"], _URN["v_stg"]],
    _URN["staging"]: [_URN["billing"], _URN["demo"], _URN["v_bill"], _URN["v_demo"]],
    _URN["v_stg"]:   [_URN["staging"]],
    _URN["v_bill"]:  [_URN["billing"]],
    _URN["v_demo"]:  [_URN["demo"]],
    _URN["billing"]: [],
    _URN["demo"]:    [],
}


@dataclass
class _Stats:
    """Real quality counts read from the SQLite database."""
    total: int
    neg_billing: int
    null_names: int
    bad_ages: int
    date_swaps: int
    neg_los: int
    age_min: int
    age_max: int
    avg_bill_positive: float
    neg_bill_sum: float
    conditions: int
    insurers: int


def _read_stats(conn: sqlite3.Connection) -> _Stats:
    def q(sql: str) -> Any:
        return conn.execute(sql).fetchone()[0]

    return _Stats(
        total=q("SELECT COUNT(*) FROM raw_patients"),
        neg_billing=q("SELECT COUNT(*) FROM raw_patients WHERE CAST(billing_amount AS REAL) < 0"),
        null_names=q("SELECT COUNT(*) FROM raw_patients WHERE name IS NULL"),
        bad_ages=q("SELECT COUNT(*) FROM raw_patients WHERE CAST(age AS INTEGER) < 0 OR CAST(age AS INTEGER) > 120"),
        date_swaps=q("SELECT COUNT(*) FROM raw_patients WHERE date_of_admission > discharge_date"),
        neg_los=q("SELECT COUNT(*) FROM mart_billing WHERE CAST(length_of_stay_days AS REAL) < 0"),
        age_min=q("SELECT MIN(CAST(age AS INTEGER)) FROM raw_patients"),
        age_max=q("SELECT MAX(CAST(age AS INTEGER)) FROM raw_patients"),
        avg_bill_positive=q("SELECT ROUND(AVG(CAST(billing_amount AS REAL)),2) FROM raw_patients WHERE CAST(billing_amount AS REAL) > 0") or 0,
        neg_bill_sum=q("SELECT ROUND(SUM(ABS(CAST(billing_amount AS REAL))),2) FROM mart_billing WHERE CAST(billing_amount AS REAL) < 0") or 0,
        conditions=q("SELECT COUNT(DISTINCT medical_condition) FROM raw_patients"),
        insurers=q("SELECT COUNT(DISTINCT insurance_provider) FROM raw_patients"),
    )


def _pct(n: int, total: int) -> str:
    return f"{n / total * 100:.1f}%"


def build_metric_definitions(s: _Stats) -> list[MetricDefinition]:
    """
    Return one MetricDefinition per (metric, team) pair — each representing
    how that team defines and computes the metric. The Conflict Detector then
    compares definitions across teams to find silent contradictions.
    """
    return [

        # ── 1. billing_amount — CRITICAL ────────────────────────────────────
        # clinical_team records any value; finance_team requires positive-only.
        # 1,215 negative values have already propagated into mart_billing.
        MetricDefinition(
            name="billing_amount",
            display_name="Billing Amount",
            domain="clinical_team",
            owner="urn:li:corpGroup:clinical-team",
            definition_text=(
                "Total charge for services rendered, recorded verbatim from the "
                "source system. No range constraint — accepted as-is, including "
                "negative values that may represent credits or data entry errors."
            ),
            sql_logic="SELECT billing_amount FROM raw_patients",
            source_urns=[_URN["raw"], _URN["staging"]],
            term_urn="urn:li:glossaryTerm:clinical.billing_amount",
            tags=["pii", "pipeline_stage"],
            last_modified="2024-01-15",
        ),
        MetricDefinition(
            name="billing_amount",
            display_name="Billing Amount",
            domain="finance_team",
            owner="urn:li:corpGroup:finance-team",
            definition_text=(
                "Revenue recognized for services rendered. Must always be positive — "
                "negative values indicate data entry errors and must be rejected "
                "before reaching financial reporting. Used in revenue dashboards "
                "and insurance reconciliation."
            ),
            sql_logic="SELECT billing_amount FROM mart_billing WHERE billing_amount > 0",
            source_urns=[_URN["billing"]],
            term_urn="urn:li:glossaryTerm:finance.billing_amount",
            tags=["critical", "pipeline_stage"],
            last_modified="2024-03-20",
        ),

        # ── 2. length_of_stay — HIGH ─────────────────────────────────────────
        # staging passes date-swapped rows through; mart_billing computes LOS
        # from the same swapped values → 277 rows with negative LOS.
        MetricDefinition(
            name="length_of_stay",
            display_name="Length of Stay",
            domain="clinical_team",
            owner="urn:li:corpGroup:clinical-team",
            definition_text=(
                "Number of days between admission and discharge, computed directly "
                "from source timestamps. Negative values possible when source "
                "admission and discharge dates are transposed."
            ),
            sql_logic="SELECT julianday(discharge_date) - julianday(date_of_admission) AS length_of_stay FROM staging_patients",
            source_urns=[_URN["staging"]],
            term_urn="urn:li:glossaryTerm:clinical.length_of_stay",
            tags=["pipeline_stage"],
            last_modified="2023-11-01",
        ),
        MetricDefinition(
            name="length_of_stay",
            display_name="Length of Stay",
            domain="finance_team",
            owner="urn:li:corpGroup:finance-team",
            definition_text=(
                "Billable inpatient days. Defined as discharge_date minus "
                "date_of_admission in whole days. Must be a positive integer — "
                "used to calculate per-diem billing rates and insurance claims."
            ),
            sql_logic="SELECT length_of_stay_days FROM mart_billing WHERE length_of_stay_days > 0",
            source_urns=[_URN["billing"]],
            term_urn="urn:li:glossaryTerm:finance.length_of_stay",
            tags=["critical"],
            last_modified="2024-02-10",
        ),

        # ── 3. patient_age — HIGH ────────────────────────────────────────────
        # Raw source has ages from -88 to 285. Staging passes them through.
        # Research team assumes valid range 0–120 for cohort analysis.
        MetricDefinition(
            name="patient_age",
            display_name="Patient Age",
            domain="clinical_team",
            owner="urn:li:corpGroup:clinical-team",
            definition_text=(
                "Patient age in years as reported by the admitting system. "
                "Stored as-is from the source; no range validation at ingestion. "
                f"Current range in raw data: {s.age_min} to {s.age_max} years."
            ),
            sql_logic="SELECT age FROM raw_patients",
            source_urns=[_URN["raw"], _URN["staging"]],
            term_urn="urn:li:glossaryTerm:clinical.patient_age",
            tags=["pii", "pipeline_stage"],
            last_modified="2023-09-05",
        ),
        MetricDefinition(
            name="patient_age",
            display_name="Patient Age",
            domain="research_team",
            owner="urn:li:corpGroup:research-team",
            definition_text=(
                "Age of the patient at time of admission, in years. Valid range "
                "is 0–120. Values outside this range are biologically impossible "
                "and must be excluded from cohort studies, survival analysis, "
                "and demographic reporting."
            ),
            sql_logic="SELECT age FROM mart_demographics WHERE age BETWEEN 0 AND 120",
            source_urns=[_URN["demo"]],
            term_urn="urn:li:glossaryTerm:research.patient_age",
            tags=["pii", "pipeline_stage"],
            last_modified="2024-05-12",
        ),

        # ── 4. patient_name — MEDIUM ─────────────────────────────────────────
        # 555 NULL names in raw propagate through to mart_demographics.
        # Research needs non-NULL names for cohort identity tracking.
        MetricDefinition(
            name="patient_name",
            display_name="Patient Name",
            domain="clinical_team",
            owner="urn:li:corpGroup:clinical-team",
            definition_text=(
                "Full name of the patient as provided at admission. "
                "May be NULL for anonymous, walk-in, or incomplete intake records. "
                "NULL is a valid source value indicating an unidentified patient."
            ),
            sql_logic="SELECT name FROM raw_patients",
            source_urns=[_URN["raw"], _URN["staging"]],
            term_urn="urn:li:glossaryTerm:clinical.patient_name",
            tags=["pii"],
            last_modified="2023-08-20",
        ),
        MetricDefinition(
            name="patient_name",
            display_name="Patient Name",
            domain="research_team",
            owner="urn:li:corpGroup:research-team",
            definition_text=(
                "Required patient identifier for cohort membership tracking. "
                "Must be non-NULL — anonymous records cannot be included in "
                "longitudinal studies or outcome analysis."
            ),
            sql_logic="SELECT name FROM mart_demographics WHERE name IS NOT NULL",
            source_urns=[_URN["demo"]],
            term_urn="urn:li:glossaryTerm:research.patient_name",
            tags=["pii"],
            last_modified="2024-04-01",
        ),

        # ── 5. test_results — MEDIUM (hidden synonym) ────────────────────────
        # staging_patients adds test_results_clean (lowercase normalized).
        # mart_demographics uses the raw test_results column (mixed case).
        # Same concept, two different representations — hidden synonym.
        MetricDefinition(
            name="test_results~test_results_clean",
            display_name="Test Results",
            domain="clinical_team",
            owner="urn:li:corpGroup:clinical-team",
            definition_text=(
                "Lab or diagnostic test outcome as recorded at point of care. "
                "Values: 'Normal', 'Abnormal', 'Inconclusive' (raw mixed-case "
                "from the EMR system). Used in clinical outcome tracking."
            ),
            sql_logic="SELECT test_results FROM raw_patients",
            source_urns=[_URN["raw"], _URN["billing"]],
            term_urn="urn:li:glossaryTerm:clinical.test_results",
            tags=["pipeline_stage"],
            last_modified="2023-07-14",
        ),
        MetricDefinition(
            name="test_results~test_results_clean",
            display_name="Test Results (Normalized)",
            domain="research_team",
            owner="urn:li:corpGroup:research-team",
            definition_text=(
                "Standardized diagnostic outcome for research queries. "
                "Values: 'normal', 'abnormal', 'inconclusive' (lowercase, trimmed). "
                "Defined as test_results_clean in staging_patients. "
                "mart_demographics uses the non-normalized column — joins against "
                "this field across tables produce case-mismatch failures."
            ),
            sql_logic="SELECT test_results_clean FROM staging_patients",
            source_urns=[_URN["staging"], _URN["demo"]],
            term_urn="urn:li:glossaryTerm:research.test_results_clean",
            tags=["pipeline_stage"],
            last_modified="2024-06-01",
        ),
    ]


def _transitive_downstream(start_urns: list[str]) -> set[str]:
    """Walk the lineage graph transitively from the given URN(s)."""
    seen: set[str] = set()
    frontier = list(start_urns)
    while frontier:
        node = frontier.pop()
        for child in _DOWNSTREAM.get(node, []):
            if child not in seen:
                seen.add(child)
                frontier.append(child)
    return seen


def _label(urn: str) -> str:
    """Short human label for a URN."""
    name = urn.split(",")[-2] if "," in urn else urn
    return name.split(".")[-1] if "." in name else name


def _kind(urn: str) -> str:
    if "dataset" in urn:
        tbl = urn.split(",")[-2].split(".")[-1] if "," in urn else ""
        if "mart" in tbl:   return "dashboard"
        if "view" in tbl or tbl.startswith("v_"): return "dashboard"
        return "dataset"
    return "dataset"


class HealthcareDataSource:
    """
    Drop-in replacement for RosettaDataHub backed by the real healthcare SQLite DB.

    Implements the same interface used by run_scan() and demo.py:
        harvest_metric_definitions() → list[MetricDefinition]
        downstream_assets(defn)      → set[str]
        impact_graph(defn)           → {"nodes": [...], "edges": [...]}
    """

    def __init__(self) -> None:
        if not _DB_PATH.exists():
            raise FileNotFoundError(
                f"healthcare.db not found at {_DB_PATH}. "
                "Download from: https://github.com/datahub-project/static-assets/tree/main/datasets/healthcare"
            )
        conn = sqlite3.connect(str(_DB_PATH))
        self._stats = _read_stats(conn)
        conn.close()
        self._definitions = build_metric_definitions(self._stats)

    # ── public stats for the demo narration ─────────────────────────────────
    @property
    def stats(self) -> _Stats:
        return self._stats

    # ── Harvester ────────────────────────────────────────────────────────────
    def harvest_metric_definitions(self) -> list[MetricDefinition]:
        for d in self._definitions:
            d.source_urns = list(dict.fromkeys(d.source_urns))
        return self._definitions

    # ── Blast-radius: transitive downstream walk ─────────────────────────────
    def downstream_assets(self, defn: MetricDefinition) -> set[str]:
        return _transitive_downstream(defn.source_urns)

    # ── Impact graph: metric origin → downstream nodes ──────────────────────
    def impact_graph(self, defn: MetricDefinition) -> dict:
        origin_id = f"metric::{defn.name}::{defn.domain}"
        nodes: dict[str, dict] = {
            origin_id: {"id": origin_id,
                        "label": f"{defn.display_name}\n({defn.domain})",
                        "type": "metric"}
        }
        edges: list[dict] = []
        seen: set[str] = set()
        frontier = list(defn.source_urns)

        for u in frontier:
            if u not in nodes:
                nodes[u] = {"id": u, "label": _label(u), "type": _kind(u)}
            edges.append({"source": origin_id, "target": u})
            seen.add(u)

        while frontier:
            node = frontier.pop()
            for child in _DOWNSTREAM.get(node, []):
                if child not in nodes:
                    nodes[child] = {"id": child, "label": _label(child), "type": _kind(child)}
                key = (node, child)
                edges.append({"source": node, "target": child})
                if child not in seen:
                    seen.add(child)
                    frontier.append(child)

        # dedupe edges
        seen_e: set[tuple] = set()
        deduped = []
        for e in edges:
            k = (e["source"], e["target"])
            if k not in seen_e:
                seen_e.add(k)
                deduped.append(e)

        return {"nodes": list(nodes.values()), "edges": deduped}
