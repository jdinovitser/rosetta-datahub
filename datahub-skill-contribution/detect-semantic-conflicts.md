# DataHub Skill: Detect Semantic Conflicts

**Skill ID:** `detect-semantic-conflicts`  
**Category:** Data Quality / Semantic Governance  
**Agent:** Rosetta — Semantic Consistency Agent  
**Status:** Contribution-ready (Build with DataHub Hackathon 2026)

---

## Overview

Rosetta is a five-agent pipeline that detects when different teams assign incompatible meanings to the same metric in a DataHub catalog, traces the blast radius through the lineage graph, proposes a canonical `GlossaryTerm`, and generates a validated, human-approved write plan — without touching any underlying data.

**One sentence:** Rosetta is a linter for meaning across the DataHub metadata graph.

---

## Problem it solves

When multiple teams independently define the same business concept — `billing_amount`, `active_users`, `revenue` — DataHub's graph accumulates conflicting `GlossaryTerm` entries. Reports agree on numbers but disagree on what those numbers mean. AI pipelines trained on tagged datasets inherit the ambiguity silently.

Rosetta makes this visible and proposable.

---

## Skill API

### Input — `MetricDefinition` records from DataHub

```python
@dataclass
class MetricDefinition:
    name: str
    display_name: str
    domain: str               # e.g. "finance", "clinical_team"
    owner: str                # DataHub owner URN
    definition_text: str      # human-readable meaning
    sql_logic: str            # computation expression
    source_urns: list[str]    # downstream dataset URNs
    term_urn: str             # urn:li:glossaryTerm:...
```

Harvest via:

```python
from rosetta.datahub_client import RosettaDataHub
dh = RosettaDataHub()   # reads DATAHUB_GMS_URL + DATAHUB_GMS_TOKEN
defs = dh.harvest_metric_definitions()
```

### Detection — `detect_conflicts`

```python
from rosetta.detector import detect_conflicts

conflicts = detect_conflicts(defs)
# Returns List[Conflict]
```

Each `Conflict` has:
- `metric` — the metric name (or `"metricA~metricB"` for synonyms)
- `kind` — `"silent_contradiction"` | `"hidden_synonym"`
- `severity` — `"critical"` | `"high"` | `"medium"` | `"low"`
- `blast_radius` — count of downstream assets affected
- `confidence` — 0.0–1.0 detection confidence
- `definitions` — the conflicting `MetricDefinition` records

### Reconciliation — `draft_proposal`

```python
from rosetta.broker import draft_proposal, generate_write_plan

proposal = draft_proposal(conflict)
write_plan = generate_write_plan(proposal)
# write_plan.operations: list of upsert / attach / deprecate DataHub ops
# write_plan.planId: SHA-256-derived hash used to tie approval to plan
```

### Approval enforcement

```python
from rosetta.broker import ApprovalToken, apply_proposal

token = ApprovalToken(
    plan_id=proposal.plan_id,
    conflict_id=proposal.term_id,
    approved_at="2026-07-31T12:00:00Z",
    mode="live",
)
result = apply_proposal(dh, proposal, token)
# Raises ValueError if token is missing, stale, or mismatched
```

---

## Conflict types detected

| Type | Description | Example |
|---|---|---|
| `silent_contradiction` | Same name, different definitions or SQL | `billing_amount`: clinical includes meds; finance subtracts discounts |
| `hidden_synonym` | Different names, logically identical computation | `active_users` vs `monthly_active_users` |

---

## Five agents

| # | Agent | Role |
|---|---|---|
| 1 | Harvester | Reads GlossaryTerm and lineage metadata from DataHub via Metadata API |
| 2 | Conflict Detector | Runs name similarity + logic similarity to classify conflicts |
| 3 | Blast-Radius Analyzer | Walks downstream lineage transitively; scores severity by asset count |
| 4 | Reconciliation Broker | Drafts canonical definition; computes plan hash; identifies approvers |
| 5 | Writer | Generates validated write plan; in Connected Mode executes after approval |

---

## Write plan schema

```json
{
  "mode": "demo | live",
  "status": "validated_not_executed | executed | partially_verified",
  "planId": "<16-char SHA-256 prefix>",
  "metric": "Billing Amount",
  "approval": {
    "required": true,
    "approved": true,
    "approvedAt": "2026-07-31T12:00:00.000000+00:00"
  },
  "operations": [
    {
      "sequence": 1,
      "action": "upsert_glossary_term",
      "targetEntityType": "GlossaryTerm",
      "targetUrn": "urn:li:glossaryTerm:billing_amount",
      "payload": { "name": "Billing Amount", "definition": "...", "termSource": "rosetta-canonical" },
      "validationStatus": "passed",
      "executionStatus": "not_executed"
    },
    {
      "sequence": 2,
      "action": "attach_term_to_asset",
      "targetEntityType": "Dataset",
      "targetUrn": "urn:li:dataset:...",
      "payload": { "termUrn": "urn:li:glossaryTerm:billing_amount" },
      "validationStatus": "passed",
      "executionStatus": "not_executed"
    },
    {
      "sequence": 3,
      "action": "deprecate_term",
      "targetEntityType": "GlossaryTerm",
      "targetUrn": "urn:li:glossaryTerm:billing_amount_v2",
      "payload": { "deprecated": true, "deprecationNote": "Superseded by canonical term..." },
      "validationStatus": "passed",
      "executionStatus": "not_executed"
    }
  ],
  "evidence": {
    "affectedAssets": 12,
    "deprecatedTerms": 4,
    "approvers": ["urn:li:corpGroup:finance_team", "urn:li:corpGroup:clinical_team"]
  }
}
```

---

## Safety guarantees

1. **No data access** — Rosetta reads only metadata URNs and GlossaryTerm definitions, never underlying row data.
2. **Explicit approval required** — `apply_proposal` raises `ValueError` if called without a valid `ApprovalToken`.
3. **Plan-hash binding** — The approval token is tied to the exact `planId`; a modified plan invalidates it.
4. **Demo Mode isolation** — Demo Mode tokens carry `mode="demo"` and are rejected by the write-back route even if a live GMS URL later appears.
5. **Single-use token** — The approval token is consumed on execution and cannot be reused.

---

## Environment variables

| Variable | Required | Description |
|---|---|---|
| `DATAHUB_GMS_URL` | Connected Mode | e.g. `http://localhost:8080` |
| `DATAHUB_GMS_TOKEN` | Optional | Bearer token for authenticated DataHub instances |

---

## Demo

The hosted demo runs entirely offline against the official Build with DataHub Hackathon 2026 healthcare dataset (55,500 synthetic patient records). No credentials or DataHub instance required.

```bash
python -m rosetta.demo          # terminal output
python webapp/app.py            # web UI at http://localhost:5000
```

---

## References

- [DataHub Metadata API](https://datahubproject.io/docs/api/rest/)
- [DataHub GlossaryTerm documentation](https://datahubproject.io/docs/generated/metamodel/entities/glossaryterm/)
- [Build with DataHub Hackathon 2026](https://datahubproject.io/hackathon)
