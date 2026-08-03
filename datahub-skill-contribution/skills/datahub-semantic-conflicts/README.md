# datahub-semantic-conflicts

Detect and resolve semantic conflicts in your DataHub GlossaryTerm catalog — cases where the same business concept has been defined differently by different teams, or where different term names have been applied to equivalent concepts.

## What it does

1. **Collects** GlossaryTerm definitions scoped to a name, domain, parent node, or the entire catalog.
2. **Detects** three conflict types: silent contradictions (same name, incompatible definitions), hidden synonyms (different names, equivalent definitions), and minor variants.
3. **Measures blast radius** by finding every entity tagged with the conflicting terms and tracing downstream lineage.
4. **Recommends** a canonical definition and identifies the approvers from DataHub ownership metadata.
5. **Prepares a dry-run remediation plan** — upsert the canonical term, attach it to affected assets, deprecate losing terms — and waits for explicit human approval.
6. **Executes** only after approval, then re-reads each entity to verify the write persisted.

## Safety model

- Steps 1–5 are fully read-only. No DataHub entity is modified during discovery.
- Execution requires an explicit "yes" from the user after reviewing the dry-run plan.
- Terms are deprecated (reversible), never deleted.
- Every write is followed by a read-back verification.

## Trigger phrases

> "find conflicting glossary terms", "detect inconsistent metric definitions", "our teams define revenue differently", "check if our glossary is consistent", "which datasets are affected by this ambiguous term", "normalize our glossary", "reconcile conflicting metric definitions", "find semantic drift", "hidden synonyms", "glossary cleanup", "term deduplication"

## Prerequisites

- DataHub CLI installed and `DATAHUB_GMS_URL` configured (see `/datahub-setup`).
- GlossaryTerms have `definition` text. Terms without definitions are flagged as metadata gaps.
- Ownership metadata populated on terms (for approver identification).
- Lineage ingested for datasets (for blast radius calculation).

## References

- [`references/detection-patterns.md`](references/detection-patterns.md) — conflict classification and similarity comparison guidance
- [`references/write-plan-reference.md`](references/write-plan-reference.md) — GraphQL mutations for term upsert, asset attachment, and deprecation
- [`../shared-references/datahub-cli-reference.md`](../shared-references/datahub-cli-reference.md) — DataHub CLI command reference

## Templates

- [`templates/conflict-report.template.md`](templates/conflict-report.template.md) — Conflict report output format
- [`templates/remediation-plan.template.md`](templates/remediation-plan.template.md) — Remediation plan dry-run output format

## Related skills

| Skill | When to use instead |
| ----- | ------------------- |
| `/datahub-enrich` | You already know the exact change to make to a single term |
| `/datahub-search` | You want to find entities by keyword, not compare definitions |
| `/datahub-lineage` | You want to trace lineage from a specific entity, not audit term consistency |
| `/datahub-quality` | You want to create data quality assertions or manage incidents |
