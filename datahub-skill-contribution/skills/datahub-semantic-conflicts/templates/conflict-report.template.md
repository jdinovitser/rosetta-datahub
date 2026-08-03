# Semantic Conflict Report

**Scope:** <!-- term name, domain, or "all" -->
**Terms analysed:** <!-- N -->
**Conflicts found:** <!-- N -->
**Generated:** <!-- ISO-8601 date -->

---

## Summary

| Severity | Count |
| -------- | ----- |
| Critical | <!-- N --> |
| High | <!-- N --> |
| Medium | <!-- N --> |
| Low | <!-- N --> |

---

## Conflicts

<!-- Repeat this block for each conflict group -->

### <!-- Concept name -->

**Type:** <!-- SILENT_CONTRADICTION | HIDDEN_SYNONYM | MINOR_VARIANT -->
**Severity:** <!-- critical | high | medium | low -->
**Confidence:** <!-- High | Medium | Low -->

| | Term A | Term B |
| --- | --- | --- |
| **URN** | `urn:li:glossaryTerm:<ID_A>` | `urn:li:glossaryTerm:<ID_B>` |
| **Owner** | <!-- team/user --> | <!-- team/user --> |
| **Definition** | <!-- text --> | <!-- text --> |
| **Mismatch** | <!-- what differs: temporal window, scope, formula, etc. --> | |

**Blast radius:**

| Term | Direct assets | Downstream assets | Total |
| ---- | ------------- | ----------------- | ----- |
| `<ID_A>` | <!-- N --> | <!-- N --> | <!-- N --> |
| `<ID_B>` | <!-- N --> | <!-- N --> | <!-- N --> |

**Recommended action:** <!-- One sentence: reconcile, consolidate, or standardise wording -->

---

## Terms with missing definitions

<!-- List terms with no definition text -->

| URN | Name | Owner |
| --- | ---- | ----- |
| <!-- urn --> | <!-- name --> | <!-- owner --> |

_These terms cannot be compared semantically. Add definitions via `/datahub-enrich`._

---

## No conflicts

<!-- Use this section if no conflicts were found; delete the Conflicts section above -->

All <!-- N --> terms in scope have consistent definitions across teams. No reconciliation is required.

<!-- Optionally list any terms with missing definitions as a metadata completeness issue -->
