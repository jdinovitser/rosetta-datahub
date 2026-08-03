# Remediation Plan — Dry Run

> **Nothing has been executed.** This plan requires explicit approval before any DataHub entity is modified.

**Conflict:** <!-- concept name -->
**Canonical term URN:** `urn:li:glossaryTerm:<CANONICAL_TERM_ID>`
**Total operations:** <!-- N -->
**Approvers:**
<!-- List each approver URN -->
- `urn:li:corpGroup:<GROUP>` — owns `urn:li:glossaryTerm:<TERM_ID>`

---

## Canonical term

| Field | Value |
| ----- | ----- |
| **URN** | `urn:li:glossaryTerm:<CANONICAL_TERM_ID>` |
| **Name** | <!-- canonical display name --> |
| **Definition** | <!-- canonical definition text --> |
| **Source ref** | <!-- documentation URL, if available --> |
| **Action** | <!-- CREATE (new term) or UPDATE (existing term) --> |

---

## Operations

### 1 of N — Upsert canonical term

```
Action:   CREATE or UPDATE
Target:   urn:li:glossaryTerm:<CANONICAL_TERM_ID>
Payload:  name = "<NAME>"
          definition = "<DEFINITION>"
```

### 2 of N — Attach canonical term to assets

```
Action:   batchAddTerms
Term:     urn:li:glossaryTerm:<CANONICAL_TERM_ID>
Assets:
  - urn:li:dataset:(urn:li:dataPlatform:<PLATFORM>,<NAME>,<ENV>)
  - urn:li:chart:(<PLATFORM>,<CHART_ID>)
  - ... (<N> assets total)
```

### N-1 of N — Deprecate losing term

```
Action:   batchUpdateDeprecation
Targets:
  - urn:li:glossaryTerm:<LOSING_TERM_ID_1>
  - urn:li:glossaryTerm:<LOSING_TERM_ID_2>
Note:     "Superseded by urn:li:glossaryTerm:<CANONICAL_TERM_ID>"
```

---

## What this plan does NOT do

- Does not delete any GlossaryTerm (deprecation is reversible)
- Does not remove existing term associations from assets (only adds the canonical term)
- Does not modify underlying data or column values
- Does not affect downstream lineage edges

---

## Approval prompt

> Do you want to apply this remediation plan?
> Type **yes** to proceed, **no** to cancel, or describe any changes you want to make first.
