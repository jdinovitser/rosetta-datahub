# DataHub Skill: Detect Semantic Conflicts

**Skill ID:** `detect-semantic-conflicts`  
**Category:** Data Quality / Semantic Governance  
**Agent:** Rosetta — Semantic Consistency Agent  
**Status:** Contribution-ready (Build with DataHub Hackathon 2026)

---

## Overview

Rosetta is a five-agent pipeline that detects when different teams assign incompatible meanings to the same metric in a DataHub catalog, traces the blast radius through the lineage graph, proposes a canonical `GlossaryTerm`, enforces human approval, and — in Connected Mode — executes the approved write plan and independently verifies each write persisted.

**One sentence:** Rosetta is a linter for meaning across the DataHub metadata graph.

---

## Problem it solves

When multiple teams independently define the same business concept — `billing_amount`, `active_users`, `revenue` — DataHub's graph accumulates conflicting `GlossaryTerm` entries. Reports agree on numbers but disagree on what those numbers mean. AI pipelines trained on tagged datasets inherit the ambiguity silently.

Rosetta makes this visible, proposable, and — with approval — resolvable in the graph.

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
- `confidence` — 0.0–1.0 detection confidence (deterministic, no LLM)
- `definitions` — the conflicting `MetricDefinition` records

### Reconciliation — `draft_proposal`

```python
from rosetta.broker import draft_proposal, generate_write_plan

proposal = draft_proposal(conflict)
write_plan = generate_write_plan(proposal)
# write_plan["operations"]: list of upsert / attach / deprecate DataHub ops
# write_plan["planId"]: 16-char SHA-256 prefix used to tie approval to this exact plan
```

### Approval enforcement

```python
from rosetta.broker import ApprovalToken, apply_proposal

token = ApprovalToken(
    plan_id=proposal.plan_id,    # must match SHA-256 hash of this exact plan
    conflict_id=proposal.term_id,
    approved_at="2026-07-31T12:00:00Z",
    mode="live",                 # "demo" tokens are rejected by the write-back route
)
result = apply_proposal(dh, proposal, token)
# Raises ValueError if token is missing, stale, or mismatched
# Raises ValueError if mode == "demo"
```

### Post-write verification

```python
from rosetta.broker import verify_proposal

verification = verify_proposal(dh, proposal, result)
# Returns VerificationResult with:
#   .status         — VERIFIED | PARTIALLY_VERIFIED | VERIFICATION_FAILED | VERIFICATION_UNAVAILABLE
#   .total_checks   — number of entities re-read
#   .passed_checks  — number confirmed to match the plan
#   .checks         — list of VerificationCheck (one per entity re-read)
```

Each `VerificationCheck` has:
- `operation_type` — `"upsert_glossary_term"` | `"attach_term_to_asset"` | `"deprecate_term"`
- `target_urn` — the DataHub entity URN that was re-read
- `expected_state` — what the approved plan specified
- `observed_state` — what was read back from DataHub
- `status` — `"verified"` | `"failed"` | `"unavailable"`
- `reason` — plain-English explanation
- `verified_at` — ISO-8601 UTC timestamp of the re-read

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
| 2 | Conflict Detector | Runs name similarity + logic similarity; fully deterministic, no LLM |
| 3 | Blast-Radius Analyzer | Walks downstream lineage transitively; scores severity by asset count |
| 4 | Reconciliation Broker | Drafts canonical definition; computes SHA-256 plan hash; identifies approvers |
| 5 | Writer | **Demo Mode:** generates and validates the proposed write plan — nothing is executed. **Connected Mode:** executes only after valid `ApprovalToken` tied to the exact plan hash, then re-reads each entity to verify state was applied. |

---

## Write plan schema (Demo Mode output)

In Demo Mode, `generate_write_plan()` always returns `"status": "validated_not_executed"`. No DataHub entity is modified.

```json
{
  "mode": "demo",
  "status": "validated_not_executed",
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

## Post-write verification schema (Connected Mode response)

After execution, `/api/write-back` returns a separate `verification` object. A successful write-API response is **not** treated as proof of persistence; each entity is re-read independently.

```json
{
  "status": "VERIFIED",
  "totalChecks": 5,
  "passedChecks": 5,
  "checks": [
    {
      "operationType": "upsert_glossary_term",
      "targetUrn": "urn:li:glossaryTerm:billing_amount",
      "expectedState": "GlossaryTerm exists with name 'Billing Amount'",
      "observedState": "exists; definition: 'CANONICAL DEFINITION of Billing Amount...'",
      "status": "verified",
      "reason": "GlossaryTerm exists with matching canonical definition",
      "verifiedAt": "2026-08-03T12:00:00+00:00"
    }
  ]
}
```

**Overall verification status values:**

| Status | Meaning |
|---|---|
| `VERIFIED` | Every sampled entity was re-read and matched the plan |
| `PARTIALLY_VERIFIED` | At least one entity matched; at least one failed or was unreadable |
| `VERIFICATION_FAILED` | At least one entity contradicted the expected state; none matched |
| `VERIFICATION_UNAVAILABLE` | No read-back method could execute (SDK not installed, exception on every read) |

---

## Safety guarantees

1. **No data access** — Rosetta reads only metadata URNs and GlossaryTerm definitions, never underlying row data.
2. **Explicit approval required** — `apply_proposal` raises `ValueError` if called without a valid `ApprovalToken`.
3. **Plan-hash binding** — The approval token is tied to the exact `planId` (SHA-256 of term_id + definition + sorted assets + deprecated terms, first 16 hex chars). A modified plan invalidates the token.
4. **Demo Mode isolation** — Demo Mode tokens carry `mode="demo"` and are rejected by the write-back route even if a live GMS URL later appears. The Demo Mode step-5 screen always shows **VALIDATED · NOT EXECUTED** and never implies a DataHub write occurred.
5. **Single-use token** — The approval token is consumed on execution and cannot be reused.
6. **Independent verification** — Verification re-reads DataHub directly; it never infers success from the write-API response code.

---

## Environment variables

| Variable | Required | Description |
|---|---|---|
| `DATAHUB_GMS_URL` | Connected Mode | e.g. `http://localhost:8080` |
| `DATAHUB_GMS_TOKEN` | Optional | Bearer token for authenticated DataHub instances |

---

## Demo

The hosted demo runs entirely offline against the **official Build with DataHub Hackathon 2026 healthcare dataset** (55,500 synthetic patient records, no real PII). The retail scan is a supplementary scenario and is not part of the official hackathon dataset. No credentials or DataHub instance required.

```bash
python -m rosetta.demo          # terminal output
python webapp/app.py            # web UI at http://localhost:5000
```

---

## References

- [DataHub Metadata API](https://datahubproject.io/docs/api/rest/)
- [DataHub GlossaryTerm documentation](https://datahubproject.io/docs/generated/metamodel/entities/glossaryterm/)
- [Build with DataHub Hackathon 2026](https://datahubproject.io/hackathon)
