---
name: datahub-semantic-conflicts
description: |
  Use this skill when the user wants to find inconsistent or conflicting GlossaryTerm definitions across teams, detect when the same business concept has been defined differently in different parts of the catalog, identify redundant or near-duplicate terms, measure how many downstream assets are exposed to the ambiguity, and prepare a canonical term reconciliation. Triggers on: "find conflicting glossary terms", "detect inconsistent metric definitions", "our teams define revenue differently", "check if our glossary is consistent", "which datasets are affected by this ambiguous term", "normalize our glossary", "reconcile conflicting metric definitions", "find semantic drift", "hidden synonyms", "glossary cleanup", "term deduplication", or any request to audit, compare, or resolve disagreements across GlossaryTerm definitions.
user-invocable: true
min-cli-version: 1.4.0
allowed-tools: Bash(datahub *)
---

# DataHub Semantic Conflict Detection

You are an expert DataHub metadata governance analyst. Your role is to help the user find and resolve semantic conflicts in their DataHub GlossaryTerm catalog — cases where the same business concept has been defined differently by different teams, or where different term names have been used for the same concept — and to prepare safe, human-approved remediation plans.

This skill operates in two phases:

- **Discovery phase (Steps 1–5):** Fully read-only. Collects definitions, detects conflicts, measures blast radius, and builds a canonical recommendation. No DataHub entities are modified.
- **Remediation phase (Steps 6–7):** Optional. Requires explicit human approval before any mutation. Applies only the operations the user has confirmed. Always re-reads after writing to verify persistence.

---

## Multi-Agent Compatibility

This skill is designed to work across multiple coding agents (Claude Code, Cursor, Codex, Copilot, Gemini CLI, Windsurf, and others).

**What works everywhere:**

- The full discovery and conflict-detection workflow (Steps 1–5)
- Blast radius analysis via DataHub lineage
- Conflict reporting and canonical recommendations
- All metadata reads via MCP tools or DataHub CLI
- Remediation plan preparation and display

**Claude Code-specific features** (other agents can safely ignore these):

- `allowed-tools` in the YAML frontmatter above
- `Task(subagent_type="datahub-skills:metadata-searcher")` for delegated bulk term lookups — only when resolving more than 20 distinct term URNs in parallel. For smaller lookups, execute inline. **Fallback instructions are provided inline** for agents that cannot dispatch sub-agents.

**Reference file paths:** Shared references are in `../shared-references/` relative to this skill's directory. Skill-specific references are in `references/` and templates in `templates/`.

---

## Not This Skill

| If the user wants to...                                         | Use this instead    |
| --------------------------------------------------------------- | ------------------- |
| Update a single known GlossaryTerm with a known value           | `/datahub-enrich`   |
| Search for entities or browse the catalog by keyword            | `/datahub-search`   |
| Explore upstream/downstream dependencies for a specific entity  | `/datahub-lineage`  |
| Create data quality assertions or manage incidents              | `/datahub-quality`  |
| Set up the DataHub CLI or configure credentials                 | `/datahub-setup`    |

**Key boundaries:** This skill is for **comparing definitions across teams** to find semantic inconsistencies ("do we all mean the same thing by `revenue`?"). Use `/datahub-enrich` when the user already knows exactly what change to make to a single term. Use `/datahub-lineage` for pure upstream/downstream traversal on a specific entity.

---

## Safety Boundaries

This skill follows a strict read-first, approve-before-write policy.

1. **Discovery is always read-only.** Steps 1–5 never mutate any DataHub entity.
2. **No mutation without explicit confirmation.** Step 6 presents a complete dry-run plan. Step 7 executes only after the user types an explicit "yes" or equivalent confirmation. Do not infer consent from prior conversation.
3. **Deprecation is reversible; deletion is not.** This skill never deletes GlossaryTerms — it deprecates them. Deprecated terms remain queryable and can be un-deprecated.
4. **Verify after writing.** After every write in Step 7, re-read the entity from DataHub to confirm the mutation persisted. A successful API response is not treated as proof.
5. **Input validation.** Reject shell metacharacters (`` ` ``, `$`, `|`, `;`, `&`, `>`, `<`) in any user-supplied term name or URN before passing to CLI. Reject malformed URNs (must match `urn:li:glossaryTerm:<id>`).

---

## Step 1: Define the Scope

Ask the user (or infer from their request) what to analyse:

| Scope | How to resolve |
| ----- | -------------- |
| Specific term name | `datahub search "<name>" --where "entity_type = glossary_term" --limit 10` |
| DataHub domain | `datahub search "*" --where "entity_type = glossary_term AND domain = <domain_urn>" --limit 100` |
| Glossary node / parent | `datahub search "*" --where "entity_type = glossary_term AND parentNode = <node_urn>" --limit 100` |
| All terms | `datahub search "*" --where "entity_type = glossary_term" --limit 200` |

If the result set is larger than 200 terms, warn the user and ask them to narrow the scope (by domain or parent node). Analysing very large term sets can be slow and produces noisy output.

Confirm the resolved scope before proceeding: display the count and a sample of term names.

---

## Step 2: Collect Candidate Definitions

For each GlossaryTerm in scope, fetch its full definition record:

```bash
datahub get --urn "urn:li:glossaryTerm:<TERM_ID>"
```

Extract and record:

| Field | Location in response |
| ----- | -------------------- |
| Term name | `glossaryTermInfo.name` |
| Definition text | `glossaryTermInfo.definition` |
| Source reference | `glossaryTermInfo.sourceRef` |
| Owning teams / users | `ownership.owners[*].owner.{urn, type}` |
| Parent node | `parentNodes.nodes[*].node.urn` |
| Structured properties | `structuredProperties.properties[*]` |

If `glossaryTermInfo.definition` is empty or missing, note it as **undefined** — a term with no definition cannot be compared and is flagged as a metadata gap, not a conflict.

**Grouping by concept:** Before comparing, group terms by their normalised concept name:

1. Lowercase the name.
2. Replace hyphens, spaces, and underscores with a single space.
3. Remove trailing plurals (`s`, `es`) if the stem is the same.
4. Group terms whose normalised names are identical or within Levenshtein distance 1.

Each group whose normalised name appears more than once across different owning teams, domains, or parent nodes is a **candidate conflict group** for Step 3.

---

## Step 3: Detect Semantic Conflicts

For each candidate conflict group, compare every definition pair. Classify each pair as one of three conflict types:

### Conflict types

| Type | Pattern | Action required |
| ---- | ------- | --------------- |
| **Silent contradiction** | Same or near-same concept name; definitions or SQL/logic are mutually incompatible | Yes — must reconcile before downstream consumers produce inconsistent results |
| **Hidden synonym** | Different concept names; definitions are equivalent or near-equivalent | Yes — consolidation opportunity; neither is wrong but having both clutters the glossary |
| **Minor variant** | Same concept name; definitions differ only in wording, not semantics | Low priority — suggest canonical wording but not urgent |

### Comparison checklist

For each definition pair, check:

- [ ] **Name similarity** — Are the normalised concept names identical or near-identical?
- [ ] **Scope alignment** — Do both definitions cover the same entities (users, transactions, revenue)?
- [ ] **Temporal window** — Do both use the same time window (7-day, 30-day, rolling, calendar)?
- [ ] **Inclusion/exclusion criteria** — Do both include or exclude the same subsets (e.g. trial users, internal accounts, voided transactions)?
- [ ] **Computation alignment** — If SQL or formula fragments are present, do they produce the same result set?

**Examples:**

```
# Silent contradiction
Term A  "active_users"  owner: analytics  "Users who started at least one session in the last 7 days"
Term B  "active_users"  owner: product    "Users who completed at least one purchase in the last 30 days"
→ Incompatible scope and temporal window. Classify: SILENT_CONTRADICTION, severity: critical

# Hidden synonym
Term A  "monthly_active_users"  owner: growth      "Users with at least one session in the past 30 calendar days"
Term B  "mau"                   owner: engineering  "Count of distinct user_id values with an event row in the last 30 days"
→ Near-identical semantics under different names. Classify: HIDDEN_SYNONYM

# Minor variant
Term A  "conversion_rate"  owner: marketing  "Percentage of users who complete a purchase after clicking an ad"
Term B  "conversion_rate"  owner: sales      "Percentage of users who complete a purchase after clicking an ad, calculated daily"
→ Same semantics, minor wording difference. Classify: MINOR_VARIANT
```

Assign a **severity**:

| Severity | Condition |
| -------- | --------- |
| `critical` | Incompatible definitions on a term with > 20 downstream assets |
| `high` | Incompatible definitions on a term with 5–20 downstream assets |
| `medium` | Incompatible definitions on a term with 1–5 downstream assets, or any hidden synonym |
| `low` | Minor variant or undefined term with no downstream assets |

Report all findings before proceeding. If no conflicts are found, tell the user and stop — do not proceed to later steps.

---

## Step 4: Measure Blast Radius

For each conflict group with severity `critical` or `high`, measure how many assets carry the ambiguous definition.

### Find entities tagged with each conflicting term

```bash
# GraphQL — find all entities using a GlossaryTerm
datahub graphql --query '
query {
  scrollAcrossEntities(input: {
    types: [DATASET, CHART, DASHBOARD, DATA_JOB, ML_PRIMARY_KEY, ML_FEATURE]
    query: "*"
    orFilters: [{
      and: [{
        field: "glossaryTerms"
        values: ["urn:li:glossaryTerm:<TERM_ID>"]
        condition: EQUAL
      }]
    }]
    count: 200
  }) {
    total
    searchResults { entity { urn type } }
  }
}
'
```

### Traverse downstream lineage from tagged assets

For each tagged dataset, trace downstream consumers:

```bash
datahub lineage --urn "urn:li:dataset:<ID>" --direction downstream --max-hops 5
```

Count and deduplicate across all traversals. Record:

- Direct tagged assets (term appears on the entity itself)
- Indirect downstream assets (inherit the ambiguity through lineage)
- Asset type breakdown (datasets, charts, dashboards, ML models)

### Blast radius summary

Present the result as a table before proceeding:

| Term | Direct assets | Downstream assets | Total exposure | Severity |
| ---- | ------------- | ----------------- | -------------- | -------- |
| `active_users` (analytics) | 4 | 18 | 22 | high |
| `active_users` (product) | 2 | 9 | 11 | high |

---

## Step 5: Build the Canonical Recommendation

For each conflict group that the user wants to resolve:

### Select the canonical base

Choose the definition with the **highest total downstream exposure** as the starting base. This minimises the number of assets that need re-tagging. If coverage is equal, prefer the definition from the team closest to the authoritative data source (warehouse over application, ingestion pipeline over BI layer).

Present the choice to the user: "I recommend using Team A's definition as the base because it covers 22 downstream assets vs. Team B's 11. Here are both definitions — do you agree?"

### Draft the canonical definition

Combine the strongest elements:

- Use the scope, temporal window, and inclusion/exclusion criteria from the base definition.
- Incorporate any precision or caveats present in the other definitions that do not contradict the base.
- Add a `sourceRef` citing the canonical owner or a linked documentation URL if available.

Show the draft to the user and ask for edits before generating the write plan.

### Identify approvers

Collect the union of all `ownership.owners` across every term in the conflict group. These are the stakeholders who must approve the reconciliation. List them:

```
Approvers:
  - urn:li:corpGroup:analytics_team  (owns active_users v1)
  - urn:li:corpGroup:product_team    (owns active_users v2)
```

Ask the user to confirm they have obtained (or will obtain) approval from these owners before proceeding to execution.

---

## Step 6: Prepare the Remediation Plan (dry-run)

Generate the complete operation sequence and display it to the user **before asking for confirmation**. Never execute until the user has reviewed and explicitly approved this plan.

### Operation types

| # | Operation | What it does |
| - | --------- | ------------ |
| 1 | `upsert_canonical_term` | Create or update the winning GlossaryTerm with the agreed canonical definition |
| 2 | `attach_term_to_assets` | Add the canonical term to every directly-tagged asset that currently has a conflicting term |
| 3 | `deprecate_losing_terms` | Mark non-canonical terms as deprecated with a note pointing to the canonical URN |

### Dry-run plan format

Present the plan in this structure:

```
Remediation plan — dry run (nothing has been executed)
═══════════════════════════════════════════════════════

Canonical term:  urn:li:glossaryTerm:active_users_canonical
  Action:        CREATE or UPDATE
  Name:          Active Users
  Definition:    <agreed canonical definition text>
  Source ref:    <documentation URL if available>

Operations (6 total):
  [1/6] upsert_canonical_term
        Target: urn:li:glossaryTerm:active_users_canonical
        Payload: { name, definition, sourceRef }

  [2/6] attach_term_to_asset
        Target: urn:li:dataset:(urn:li:dataPlatform:snowflake,analytics.user_events,PROD)
        Payload: add urn:li:glossaryTerm:active_users_canonical

  ... (remaining attach operations)

  [5/6] deprecate_losing_term
        Target: urn:li:glossaryTerm:active_users_v1
        Payload: { deprecated: true, note: "Superseded by urn:li:glossaryTerm:active_users_canonical" }

  [6/6] deprecate_losing_term
        Target: urn:li:glossaryTerm:active_users_v2
        Payload: { deprecated: true, note: "Superseded by urn:li:glossaryTerm:active_users_canonical" }

Approvers who should sign off before execution:
  - urn:li:corpGroup:analytics_team
  - urn:li:corpGroup:product_team
```

After displaying the plan, ask:

> "Do you want to apply this remediation plan? Type **yes** to proceed, **no** to cancel, or describe any changes you want to make first."

**Do not proceed until you receive an explicit affirmative response.** If the user requests changes, update the plan and show the revised dry-run before asking again.

---

## Step 7: Execute and Verify

Execute only after receiving explicit approval from Step 6.

### Execute in sequence

#### Operation 1 — Upsert the canonical term

If the canonical term does not yet exist, create it:

```bash
datahub graphql --query 'mutation {
  createGlossaryTerm(input: {
    id: "<CANONICAL_TERM_ID>"
    name: "<CANONICAL_NAME>"
    description: "<CANONICAL_DEFINITION>"
  }) { urn }
}'
```

If it already exists, update its description:

```bash
datahub graphql --query 'mutation {
  updateDescription(input: {
    resourceUrn: "urn:li:glossaryTerm:<CANONICAL_TERM_ID>"
    description: "<CANONICAL_DEFINITION>"
  })
}'
```

#### Operation 2 — Attach the canonical term to affected assets

Use `batchAddTerms` for efficiency. If the asset set is larger than 50, split into batches:

```bash
datahub graphql --query 'mutation {
  batchAddTerms(input: {
    termUrns: ["urn:li:glossaryTerm:<CANONICAL_TERM_ID>"]
    resources: [
      { resourceUrn: "urn:li:dataset:<ID1>" },
      { resourceUrn: "urn:li:dataset:<ID2>" }
    ]
  })
}'
```

#### Operation 3 — Deprecate losing terms

```bash
datahub graphql --query 'mutation {
  batchUpdateDeprecation(input: {
    resources: [
      { resourceUrn: "urn:li:glossaryTerm:<LOSING_TERM_ID_1>" },
      { resourceUrn: "urn:li:glossaryTerm:<LOSING_TERM_ID_2>" }
    ]
    deprecated: true
    note: "Superseded by urn:li:glossaryTerm:<CANONICAL_TERM_ID>. See canonical definition for the agreed meaning."
  })
}'
```

### Verify each write

After each operation, re-read the target entity and confirm the expected state was applied. Do not infer success from the mutation response code alone.

```bash
# Verify canonical term definition
datahub get --urn "urn:li:glossaryTerm:<CANONICAL_TERM_ID>"
# Confirm: glossaryTermInfo.definition matches the approved canonical text

# Verify an asset attachment
datahub get --urn "urn:li:dataset:<ID>"
# Confirm: glossaryTerms includes urn:li:glossaryTerm:<CANONICAL_TERM_ID>

# Verify deprecation
datahub get --urn "urn:li:glossaryTerm:<LOSING_TERM_ID>"
# Confirm: deprecation.deprecated == true
```

### Verification status per operation

Report one of three statuses for each operation:

| Status | Meaning |
| ------ | ------- |
| `verified` | Re-read confirmed the expected state is present |
| `failed` | Re-read returned a contradicting or missing state |
| `unavailable` | Read call failed (network error, permissions, timeout) — cannot confirm either way |

### Overall result

| Overall status | Condition |
| -------------- | --------- |
| `VERIFIED` | All operations verified |
| `PARTIALLY_VERIFIED` | At least one verified; at least one failed or unavailable |
| `VERIFICATION_FAILED` | At least one failed; none verified |
| `VERIFICATION_UNAVAILABLE` | Every re-read was unavailable; no confirmation possible |

Present the verification summary and, for any `failed` operations, describe what was observed vs. expected.

---

## No Conflicts Found

If Step 3 finds no conflicts, report the clean state clearly:

> "No semantic conflicts found in the scoped term set. All N terms have consistent definitions across teams."

Optionally note any terms with **missing definitions** (empty `glossaryTermInfo.definition`) as a metadata completeness issue to address via `/datahub-enrich`.

---

## Assumptions and Prerequisites

- DataHub instance is reachable and credentials are configured (`DATAHUB_GMS_URL`, optionally `DATAHUB_GMS_TOKEN`).
- GlossaryTerms carry human-readable `definition` text. Terms with no definition text cannot be semantically compared and are flagged as a metadata gap.
- Ownership metadata is present on terms. Approver identification requires `ownership.owners` to be populated.
- Lineage edges are ingested for datasets to support blast radius calculation. Partial lineage coverage produces a lower-bound blast radius estimate.
- The user (or an authorised human) reviews and explicitly confirms all remediation plans before execution.

---

## Inputs

| Input | Source | Required |
| ----- | ------ | -------- |
| Scope (term name, domain, parent node, or "all") | User request | Yes |
| Canonical definition text | User-reviewed draft from Step 5 | Required for execution |
| Explicit approval | User confirmation in Step 6 | Required for execution |

---

## Outputs

| Output | Format |
| ------ | ------ |
| Conflict report | Markdown table — conflict type, affected terms, severity, blast radius |
| Canonical recommendation | Term name, draft definition, approvers list |
| Remediation plan | Numbered operation list (dry-run) — see Step 6 template |
| Verification summary | Per-operation status table — see Step 7 |

Use `templates/conflict-report.template.md` and `templates/remediation-plan.template.md` for output formatting.

---

## Limitations

- **Definition-only comparison.** This skill compares human-readable definition text and any SQL/formula fragments present in structured properties. It cannot execute queries against underlying databases to verify whether two definitions produce identical result sets.
- **No automated merge.** The canonical definition is drafted from existing text and shown to the user for review. Final wording always requires human approval.
- **Blast radius is a lower bound.** Lineage coverage depends on what has been ingested. Assets without lineage edges are not counted.
- **Field-level term usage.** This skill attaches the canonical term at the entity level. Field-level term associations (column-level GlossaryTerm tags) require a separate pass with `/datahub-enrich` using `subResourceType: DATASET_FIELD`.
- **Indirect consumers.** Downstream lineage traversal (`--max-hops 5`) may miss consumers further than 5 hops from the tagged asset. Increase `--max-hops` manually if the lineage graph is known to be deeper.

---

## Failure States

| Failure | Response |
| ------- | -------- |
| `datahub search` returns 0 results for a named term | Confirm the term name and try a broader search. Suggest browsing via `/datahub-search`. |
| Term has no definition text | Flag as a metadata gap. Do not attempt comparison. Suggest adding a definition via `/datahub-enrich`. |
| `glossaryTermInfo` aspect missing from `datahub get` output | The entity exists but has no term metadata. Flag and skip. |
| Lineage traversal returns empty (no downstream assets) | Report blast radius of 0. The conflict is still valid; it just has no current downstream exposure. |
| `batchAddTerms` mutation fails | Do not proceed to the next operation. Report the error, present the partial state, and ask the user how to proceed. Do not retry automatically. |
| Re-read after write returns the old state | Report `failed` verification. Do not retry automatically. Ask the user to inspect the DataHub instance directly. |
| Permissions error on write | Report the error and the required permission (`MANAGE_GLOSSARIES` or `EDIT_ENTITY_GLOSSARY_TERMS`). Do not retry. |
