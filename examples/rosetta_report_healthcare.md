# Rosetta Semantic Consistency Report

_Generated at 2026-08-04T17:17:46.304307+00:00_

## Summary

- **Total conflicts:** 5
- **Critical:** 1
- **High:** 2
- **Downstream assets at risk:** 585
- **Est. manual reconciliation cost avoided:** $26,325 (292.5 analyst-hours)

## Conflicts

### 1. `test_results~test_results_clean` — silent_contradiction (MEDIUM)

> 'Test Results' (clinical_team) and 'Test Results (Normalized)' (research_team) share a name but compute differently (logic overlap 20%).

**AI Explanation**

- **Finding:** 'Test Results vs Test Results Clean' has 2 incompatible definitions across clinical_team and research_team — same name, different computation.
- **Evidence:** Logic similarity 20%, confidence 90%. Definitions: clinical_team: "Lab or diagnostic test outcome as recorded at point of care. Values: 'No…"; research_team: "Standardized diagnostic outcome for research queries. Values: 'normal',…". Governance signals: clinical_team: definition stale (last updated 2023-07-14); research_team: definition stale (last updated 2024-06-01).
- **Impact:** MEDIUM severity. 555 downstream assets are at risk. A wrong 'Test Results vs Test Results Clean' silently feeds 0 decision surface(s) (0 dashboards, 0 models) across 2 teams.
- **Recommendation:** Open a data governance ticket for 'Test Results vs Test Results Clean'. Draft a canonical definition incorporating both teams' intent and circulate for sign-off in the next governance review cycle.

- **Blast radius:** 555 downstream assets
- **Confidence:** 0.902 · **Est. cost if unreconciled:** $24,975
- **Risk:** A wrong 'Test Results vs Test Results Clean' silently feeds 0 decision surface(s) (0 dashboards, 0 models) across 2 teams.
- **Logic similarity:** 0.196 · **Name similarity:** 1.0

| Domain | Owner | Definition | Computation |
| --- | --- | --- | --- |
| clinical_team | urn:li:corpGroup:clinical-team | Lab or diagnostic test outcome as recorded at point of care. Values: 'Normal', 'Abnormal', 'Inconclusive' (raw mixed-case from the EMR system). Used in clinical outcome tracking. | `SELECT test_results FROM raw_patients` |
| research_team | urn:li:corpGroup:research-team | Standardized diagnostic outcome for research queries. Values: 'normal', 'abnormal', 'inconclusive' (lowercase, trimmed). Defined as test_results_clean in staging_patients. mart_demographics uses the non-normalized column — joins against this field across tables produce case-mismatch failures. | `SELECT test_results_clean FROM staging_patients` |

### 2. `patient_age` — silent_contradiction (HIGH)

> 'Patient Age' (clinical_team) and 'Patient Age' (research_team) share a name but compute differently (logic overlap 18%).

**AI Explanation**

- **Finding:** 'Patient Age' has 2 incompatible definitions across clinical_team and research_team — same name, different computation.
- **Evidence:** Logic similarity 18%, confidence 91%. Definitions: clinical_team: "Patient age in years as reported by the admitting system. Stored as-is f…"; research_team: "Age of the patient at time of admission, in years. Valid range is 0–120.…". Governance signals: clinical_team: handles sensitive/PII data; clinical_team: definition stale (last updated 2023-09-05); research_team: handles sensitive/PII data; research_team: definition stale (last updated 2024-05-12).
- **Impact:** HIGH severity. 8 downstream assets are at risk. A wrong 'Patient Age' silently feeds 0 decision surface(s) (0 dashboards, 0 models) across 2 teams.
- **Recommendation:** Schedule a cross-team definition review for 'Patient Age' within this sprint. Propose one canonical term, notify all 8 asset owners, and deprecate the conflicting variant.

- **Blast radius:** 8 downstream assets
- **Confidence:** 0.91 · **Est. cost if unreconciled:** $360
- **Risk:** A wrong 'Patient Age' silently feeds 0 decision surface(s) (0 dashboards, 0 models) across 2 teams.
- **Logic similarity:** 0.179 · **Name similarity:** 1.0

| Domain | Owner | Definition | Computation |
| --- | --- | --- | --- |
| clinical_team | urn:li:corpGroup:clinical-team | Patient age in years as reported by the admitting system. Stored as-is from the source; no range validation at ingestion. Current range in raw data: -88 to 285 years. | `SELECT age FROM raw_patients` |
| research_team | urn:li:corpGroup:research-team | Age of the patient at time of admission, in years. Valid range is 0–120. Values outside this range are biologically impossible and must be excluded from cohort studies, survival analysis, and demographic reporting. | `SELECT age FROM mart_demographics WHERE age BETWEEN 0 AND 120` |

### 3. `patient_name` — silent_contradiction (MEDIUM)

> 'Patient Name' (clinical_team) and 'Patient Name' (research_team) share a name but compute differently (logic overlap 21%).

**AI Explanation**

- **Finding:** 'Patient Name' has 2 incompatible definitions across clinical_team and research_team — same name, different computation.
- **Evidence:** Logic similarity 21%, confidence 90%. Definitions: clinical_team: "Full name of the patient as provided at admission. May be NULL for anony…"; research_team: "Required patient identifier for cohort membership tracking. Must be non-…". Governance signals: clinical_team: handles sensitive/PII data; clinical_team: definition stale (last updated 2023-08-20); research_team: handles sensitive/PII data; research_team: definition stale (last updated 2024-04-01).
- **Impact:** MEDIUM severity. 6 downstream assets are at risk. A wrong 'Patient Name' silently feeds 0 decision surface(s) (0 dashboards, 0 models) across 2 teams.
- **Recommendation:** Open a data governance ticket for 'Patient Name'. Draft a canonical definition incorporating both teams' intent and circulate for sign-off in the next governance review cycle.

- **Blast radius:** 6 downstream assets
- **Confidence:** 0.895 · **Est. cost if unreconciled:** $270
- **Risk:** A wrong 'Patient Name' silently feeds 0 decision surface(s) (0 dashboards, 0 models) across 2 teams.
- **Logic similarity:** 0.211 · **Name similarity:** 1.0

| Domain | Owner | Definition | Computation |
| --- | --- | --- | --- |
| clinical_team | urn:li:corpGroup:clinical-team | Full name of the patient as provided at admission. May be NULL for anonymous, walk-in, or incomplete intake records. NULL is a valid source value indicating an unidentified patient. | `SELECT name FROM raw_patients` |
| research_team | urn:li:corpGroup:research-team | Required patient identifier for cohort membership tracking. Must be non-NULL — anonymous records cannot be included in longitudinal studies or outcome analysis. | `SELECT name FROM mart_demographics WHERE name IS NOT NULL` |

### 4. `billing_amount` — silent_contradiction (CRITICAL)

> 'Billing Amount' (clinical_team) and 'Billing Amount' (finance_team) share a name but compute differently (logic overlap 23%).

**AI Explanation**

- **Finding:** 'Billing Amount' has 2 incompatible definitions across clinical_team and finance_team — same name, different computation.
- **Evidence:** Logic similarity 23%, confidence 88%. Definitions: clinical_team: "Total charge for services rendered, recorded verbatim from the source sy…"; finance_team: "Revenue recognized for services rendered. Must always be positive — nega…". Governance signals: clinical_team: handles sensitive/PII data; clinical_team: definition stale (last updated 2024-01-15); finance_team: definition stale (last updated 2024-03-20).
- **Impact:** CRITICAL severity. 12 downstream assets are at risk. A wrong 'Billing Amount' silently feeds 0 decision surface(s) (0 dashboards, 0 models) across 2 teams.
- **Recommendation:** Escalate immediately: align clinical_team and finance_team leadership on a single canonical definition for 'Billing Amount'. Freeze dependent pipelines until resolved. In Connected Mode, Rosetta can execute a human-approved remediation plan and verify the resulting metadata where supported.

- **Blast radius:** 12 downstream assets
- **Confidence:** 0.884 · **Est. cost if unreconciled:** $540
- **Risk:** A wrong 'Billing Amount' silently feeds 0 decision surface(s) (0 dashboards, 0 models) across 2 teams.
- **Logic similarity:** 0.233 · **Name similarity:** 1.0

| Domain | Owner | Definition | Computation |
| --- | --- | --- | --- |
| clinical_team | urn:li:corpGroup:clinical-team | Total charge for services rendered, recorded verbatim from the source system. No range constraint — accepted as-is, including negative values that may represent credits or data entry errors. | `SELECT billing_amount FROM raw_patients` |
| finance_team | urn:li:corpGroup:finance-team | Revenue recognized for services rendered. Must always be positive — negative values indicate data entry errors and must be rejected before reaching financial reporting. Used in revenue dashboards and insurance reconciliation. | `SELECT billing_amount FROM mart_billing WHERE billing_amount > 0` |

### 5. `length_of_stay` — silent_contradiction (HIGH)

> 'Length of Stay' (clinical_team) and 'Length of Stay' (finance_team) share a name but compute differently (logic overlap 12%).

**AI Explanation**

- **Finding:** 'Length Of Stay' has 2 incompatible definitions across clinical_team and finance_team — same name, different computation.
- **Evidence:** Logic similarity 12%, confidence 94%. Definitions: clinical_team: "Number of days between admission and discharge, computed directly from s…"; finance_team: "Billable inpatient days. Defined as discharge_date minus date_of_admissi…". Governance signals: clinical_team: definition stale (last updated 2023-11-01); finance_team: definition stale (last updated 2024-02-10).
- **Impact:** HIGH severity. 4 downstream assets are at risk. A wrong 'Length Of Stay' silently feeds 0 decision surface(s) (0 dashboards, 0 models) across 2 teams.
- **Recommendation:** Schedule a cross-team definition review for 'Length Of Stay' within this sprint. Propose one canonical term, notify all 4 asset owners, and deprecate the conflicting variant.

- **Blast radius:** 4 downstream assets
- **Confidence:** 0.939 · **Est. cost if unreconciled:** $180
- **Risk:** A wrong 'Length Of Stay' silently feeds 0 decision surface(s) (0 dashboards, 0 models) across 2 teams.
- **Logic similarity:** 0.122 · **Name similarity:** 1.0

| Domain | Owner | Definition | Computation |
| --- | --- | --- | --- |
| clinical_team | urn:li:corpGroup:clinical-team | Number of days between admission and discharge, computed directly from source timestamps. Negative values possible when source admission and discharge dates are transposed. | `SELECT julianday(discharge_date) - julianday(date_of_admission) AS length_of_stay FROM staging_patients` |
| finance_team | urn:li:corpGroup:finance-team | Billable inpatient days. Defined as discharge_date minus date_of_admission in whole days. Must be a positive integer — used to calculate per-diem billing rates and insurance claims. | `SELECT length_of_stay_days FROM mart_billing WHERE length_of_stay_days > 0` |


---

## Data Provenance

- **Dataset:** DataHub sample data supplied through the official Build with DataHub Agent Hackathon resources (healthcare.db)
- **Source URL:** https://github.com/datahub-project/static-assets/tree/main/datasets/healthcare
- **Statement:** Generated in DEMO MODE against official hackathon sample data. Rosetta queries this file read-only. No real patient or personal information is used.
- **Rosetta-constructed:** MetricDefinition pairs (rosetta/healthcare_source.py), DataHub URN lineage graph (_DOWNSTREAM dict), Glossary term URNs (urn:li:glossaryTerm:*), Team ownership URNs (urn:li:corpGroup:*), Severity scores and blast-radius overrides, Canonical proposals (rosetta/broker.py)
- **Not established:** License of the source dataset; Whether anomalies were intentionally planted or naturally present in the source
- **Scenario:** Healthcare: Official hackathon data
- **Full provenance:** `DATA_PROVENANCE.md`
