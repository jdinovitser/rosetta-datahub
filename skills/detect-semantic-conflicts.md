# DataHub Skill: detect-semantic-conflicts

> A reusable [DataHub Skill](https://docs.datahub.com/docs/dev-guides/agent-context/skills)
> that teaches any agent to find metrics that are defined inconsistently across
> the graph, rank them by lineage blast radius, and propose a canonical
> definition to write back.

## When to use this skill

Use this skill when a user asks any of:
- "Do we define <metric> consistently across teams?"
- "Why do two dashboards report different numbers for the same metric?"
- "Audit our glossary for conflicting or duplicate definitions."

## Inputs the skill needs from DataHub (via MCP Server / Agent Context Kit)

1. All glossary terms and their definitions.
2. Column-level descriptions and the SQL/queries that populate each metric
   (parse historical queries to infer real computation).
3. Ownership for each definition (to route approvals).
4. Downstream lineage for each asset (to compute blast radius).

## Procedure

1. **Harvest** every candidate metric definition.
2. **Detect** two conflict types:
   - *Silent contradiction*: same name, divergent computation.
   - *Hidden synonym*: different name, identical computation.
3. **Rank** by downstream blast radius (dashboards + models + datasets affected).
4. **Draft** a canonical definition using the highest-coverage variant as base.
5. **Route** the proposal to the owners of every conflicting definition.
6. **Write back** on approval: upsert the canonical `GlossaryTerm`, attach it to
   every affected asset, and mark losing terms `deprecated` (relationships are
   preserved, so nothing breaks).

## Write operations used

- `client.entities.upsert(GlossaryTerm(...))`
- `dataset.add_term(GlossaryTermUrn(...))` then `client.entities.update(dataset)`
- `term.set_deprecation(deprecated=True, note=...)`

## Safety

- Never write without human approval from at least one affected owner.
- Deprecate rather than delete: preserve history and existing associations.
- Always leave an audit trail (who approved, when, which variant won).
