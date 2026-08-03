# Write Plan Reference

GraphQL mutations and CLI patterns for executing a semantic conflict remediation plan in DataHub.

All mutations on this page require the `Manage Glossaries` privilege, or the `Edit Entity Glossary Terms` privilege for asset attachment operations. Verify the user has the required permissions before executing.

---

## Operation 1: Upsert the canonical GlossaryTerm

### Create a new canonical term

```bash
datahub graphql --query 'mutation {
  createGlossaryTerm(input: {
    id: "<CANONICAL_TERM_ID>"
    name: "<CANONICAL_DISPLAY_NAME>"
    description: "<CANONICAL_DEFINITION_TEXT>"
  }) {
    urn
  }
}'
```

`id` becomes the URN path component: `urn:li:glossaryTerm:<id>`. Use a stable, slug-like value (lowercase, hyphens). Do not include spaces or special characters.

### Update an existing term's definition

```bash
datahub graphql --query 'mutation {
  updateDescription(input: {
    resourceUrn: "urn:li:glossaryTerm:<CANONICAL_TERM_ID>"
    description: "<CANONICAL_DEFINITION_TEXT>"
  })
}'
```

### Add a source reference (documentation URL)

```bash
datahub graphql --query 'mutation {
  addLink(input: {
    resourceUrn: "urn:li:glossaryTerm:<CANONICAL_TERM_ID>"
    linkDetails: {
      url: "<DOCUMENTATION_URL>"
      label: "Canonical definition source"
    }
  })
}'
```

### Verification read

```bash
datahub get --urn "urn:li:glossaryTerm:<CANONICAL_TERM_ID>"
# Expect: glossaryTermInfo.definition matches the approved canonical text
# Expect: glossaryTermInfo.name matches the approved canonical name
```

---

## Operation 2: Attach the canonical term to affected assets

### Batch attach (preferred — works for single or multiple assets)

```bash
datahub graphql --query 'mutation {
  batchAddTerms(input: {
    termUrns: ["urn:li:glossaryTerm:<CANONICAL_TERM_ID>"]
    resources: [
      { resourceUrn: "urn:li:dataset:<PLATFORM>,<NAME>,<ENV>" },
      { resourceUrn: "urn:li:chart:(<PLATFORM>,<CHART_ID>)" },
      { resourceUrn: "urn:li:dashboard:(<PLATFORM>,<DASHBOARD_ID>)" }
    ]
  })
}'
```

For large asset sets (> 50), split into batches of 50 and execute sequentially. Present progress after each batch.

### Field-level attachment (if needed)

```bash
datahub graphql --query 'mutation {
  batchAddTerms(input: {
    termUrns: ["urn:li:glossaryTerm:<CANONICAL_TERM_ID>"]
    resources: [{
      resourceUrn: "urn:li:dataset:<PLATFORM>,<NAME>,<ENV>"
      subResourceType: DATASET_FIELD
      subResource: "<FIELD_PATH>"
    }]
  })
}'
```

Note: Field-level attachment is outside the primary scope of this skill. If field-level coverage is needed, use `/datahub-enrich` after completing the entity-level remediation.

### Verification read

```bash
datahub get --urn "urn:li:dataset:<ID>"
# Expect: response includes "glossaryTerms" containing "urn:li:glossaryTerm:<CANONICAL_TERM_ID>"
```

---

## Operation 3: Deprecate losing terms

### Batch deprecation (preferred)

```bash
datahub graphql --query 'mutation {
  batchUpdateDeprecation(input: {
    resources: [
      { resourceUrn: "urn:li:glossaryTerm:<LOSING_TERM_ID_1>" },
      { resourceUrn: "urn:li:glossaryTerm:<LOSING_TERM_ID_2>" }
    ]
    deprecated: true
    note: "Superseded by urn:li:glossaryTerm:<CANONICAL_TERM_ID>. The canonical definition is: <ONE_LINE_SUMMARY>"
  })
}'
```

The `note` field should include:

1. The canonical URN (machine-readable pointer)
2. A one-line summary of the canonical definition (human-readable)

### Verification read

```bash
datahub get --urn "urn:li:glossaryTerm:<LOSING_TERM_ID>"
# Expect: deprecation.deprecated == true
# Expect: deprecation.note contains the canonical URN
```

---

## Reversing a deprecation (if needed after verification failure)

```bash
datahub graphql --query 'mutation {
  updateDeprecation(input: {
    urn: "urn:li:glossaryTerm:<TERM_ID>"
    deprecated: false
  })
}'
```

Use this only when a write-verification failure requires rolling back a deprecation operation. Present the rollback to the user before executing.

---

## Permissions required

| Operation | Required privilege |
| --------- | ------------------ |
| Create GlossaryTerm | `Manage Glossaries` |
| Update term description | `Manage Glossaries` |
| Attach term to entity | `Edit Entity Glossary Terms` (on the target entity) |
| Deprecate GlossaryTerm | `Manage Glossaries` |

If a mutation fails with a permissions error, report the required privilege and stop. Do not retry with different parameters.
