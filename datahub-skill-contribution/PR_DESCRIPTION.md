# Pull Request

## Title

```
feat: add datahub-semantic-conflicts skill for cross-team glossary term reconciliation
```

---

## Description

### The governance problem

DataHub catalogs accumulate semantic drift over time. Different teams independently create `GlossaryTerm` entities for the same business concept — `revenue`, `active_users`, `conversion_rate` — but with incompatible definitions: different time windows, different population filters, different computation methods. Downstream reports appear to agree on numbers but are silently measuring different things. Talk-to-data AI agents trained on these tagged datasets inherit the ambiguity without warning.

There is currently no skill in this repository that helps an agent detect, quantify, and safely resolve this class of problem.

### What this skill adds

`datahub-semantic-conflicts` is a seven-step workflow skill that covers the full arc from read-only discovery through human-approved remediation:

1. **Define scope** — term name, domain, parent node, or full catalog.
2. **Collect definitions** — harvest `GlossaryTerm` definition text, ownership, and structured properties.
3. **Detect conflicts** — classify each candidate pair as a *silent contradiction* (same name, incompatible logic), *hidden synonym* (different names, equivalent logic), or *minor variant*.
4. **Measure blast radius** — find every entity tagged with the conflicting terms, trace downstream lineage, and score severity by total exposure.
5. **Recommend a canonical definition** — select the highest-coverage base, draft unified text, and identify approvers from DataHub ownership metadata.
6. **Prepare a dry-run remediation plan** — upsert the canonical term, attach it to affected assets, deprecate losing terms — displayed in full before any action is taken.
7. **Execute and verify** — mutations run only after explicit human approval; each write is followed by a read-back to confirm persistence.

### Why it is reusable

The skill is a pure DataHub workflow. It uses only standard DataHub primitives — `datahub search`, `datahub get`, `datahub lineage`, `datahub graphql` mutations (`batchAddTerms`, `batchUpdateDeprecation`, `createGlossaryTerm`) — against the standard `GlossaryTerm` entity and its aspects. It works with any DataHub instance regardless of catalog size or source platform. Examples in the skill use generic business concepts (`revenue`, `active_users`, `session_count`).

### How DataHub context and lineage are used

- **GlossaryTerm aspects** (`glossaryTermInfo`, `ownership`, `parentNodes`) provide definition text and stakeholder identification.
- **`scrollAcrossEntities` with `glossaryTerms` filter** finds every entity carrying a conflicting term.
- **`datahub lineage --direction downstream`** traces the blast radius from tagged entities to their downstream consumers.
- **`batchAddTerms`, `batchUpdateDeprecation`, `createGlossaryTerm`** are the only mutations used, matching patterns already established in `datahub-enrich`.

### Safety controls

| Control | Implementation |
| ------- | -------------- |
| Read-only discovery | Steps 1–5 contain no mutations |
| Explicit approval gate | Step 6 displays the full dry-run plan and requires a literal "yes" before Step 7 runs |
| No deletion | Only `batchUpdateDeprecation` (reversible); terms are never deleted |
| Post-write verification | After every mutation in Step 7, the entity is re-read and per-operation status (`verified` / `failed` / `unavailable`) is reported |
| Input validation | Shell metacharacters and malformed URNs are rejected before any CLI call |
| Permissions check | Required privileges documented; mutations fail-stop on a permissions error |

### Validation performed

The contribution was validated locally against the upstream repo's exact linting configuration (`.markdownlint-cli2.yaml` rules reproduced from `main`):

```
markdownlint-cli2 SKILL.md README.md references/*.md templates/*.md
```

Result: **0 errors, 0 warnings** across all six files.

---

## Files

```
skills/datahub-semantic-conflicts/
├── SKILL.md                              # Main skill — 7-step workflow
├── README.md                             # Quick-reference overview
├── references/
│   ├── detection-patterns.md             # Conflict classification and similarity heuristics
│   └── write-plan-reference.md           # GraphQL mutations reference (upsert, attach, deprecate)
└── templates/
    ├── conflict-report.template.md       # Conflict report output format
    └── remediation-plan.template.md      # Dry-run plan output format
```

---

## Checklist

- [x] `feat:` prefix on PR title (minor version bump)
- [x] All files in `skills/datahub-semantic-conflicts/`
- [x] `SKILL.md` has valid YAML frontmatter (`name`, `description`, `user-invocable`, `min-cli-version`, `allowed-tools`)
- [x] `README.md` present
- [x] No inline HTML (MD033 off, but none used)
- [x] No hardcoded project-specific URNs, names, or demo scenarios
- [x] Follows enrich/lineage skill patterns for MCP vs. CLI guidance
- [x] Explicit disambiguation table (Not This Skill)
- [x] Explicit Multi-Agent Compatibility section
- [x] Assumptions, Inputs, Outputs, Limitations, Failure States documented
- [x] Markdownlint passes with upstream config
