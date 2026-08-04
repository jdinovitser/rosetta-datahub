# Rosetta Semantic Consistency Report

_Generated at 2026-08-04T17:17:49.176405+00:00_

## Summary

- **Total conflicts:** 2
- **Critical:** 1
- **High:** 0
- **Downstream assets at risk:** 1871
- **Est. manual reconciliation cost avoided:** $84,195 (935.5 analyst-hours)

## Conflicts

### 1. `discount_pct` — silent_contradiction (CRITICAL)

> 'Discount Percentage' (commerce_team) and 'Discount Percentage' (marketing_team) share a name but compute differently (logic overlap 18%).

**AI Explanation**

- **Finding:** 'Discount Pct' has 2 incompatible definitions across commerce_team and marketing_team — same name, different computation.
- **Evidence:** Logic similarity 18%, confidence 91%. Definitions: commerce_team: "Decimal fraction discount applied to a line item at checkout. Range: 0.0…"; marketing_team: "Integer percentage discount authored in campaign management tools. Range…". Governance signals: commerce_team: definition stale (last updated 2024-02-14); marketing_team: definition stale (last updated 2023-11-30).
- **Impact:** CRITICAL severity. 371 downstream assets are at risk. A wrong 'Discount Pct' silently feeds 0 decision surface(s) (0 dashboards, 0 models) across 2 teams.
- **Recommendation:** Escalate immediately: align commerce_team and marketing_team leadership on a single canonical definition for 'Discount Pct'. Freeze dependent pipelines until resolved. In Connected Mode, Rosetta can execute a human-approved remediation plan and verify the resulting metadata where supported.

- **Blast radius:** 371 downstream assets
- **Confidence:** 0.909 · **Est. cost if unreconciled:** $16,695
- **Risk:** A wrong 'Discount Pct' silently feeds 0 decision surface(s) (0 dashboards, 0 models) across 2 teams.
- **Logic similarity:** 0.182 · **Name similarity:** 1.0

| Domain | Owner | Definition | Computation |
| --- | --- | --- | --- |
| commerce_team | urn:li:corpGroup:commerce-team | Decimal fraction discount applied to a line item at checkout. Range: 0.0 (no discount) to 1.0 (100% off). Used to compute net revenue: unit_price × quantity × (1 − discount_pct). Values outside 0–1 indicate a unit-convention error. | `SELECT discount_pct FROM order_items WHERE discount_pct BETWEEN 0.0 AND 1.0` |
| marketing_team | urn:li:corpGroup:marketing-team | Integer percentage discount authored in campaign management tools. Range: 0 (no discount) to 100 (free). A value of 20 means 20% off. Stored as-is from the promotions authoring system — no fractional conversion applied. | `SELECT discount_pct FROM promotions` |

### 2. `order_status~shipment_state` — silent_contradiction (MEDIUM)

> 'Order Status' (commerce_team) and 'Shipment State' (logistics_team) share a name but compute differently (logic overlap 21%).

**AI Explanation**

- **Finding:** 'Order Status vs Shipment State' has 2 incompatible definitions across commerce_team and logistics_team — same name, different computation.
- **Evidence:** Logic similarity 21%, confidence 89%. Definitions: commerce_team: "Lifecycle state of an order as tracked by the commerce platform. Current…"; logistics_team: "Current state of a shipment in the carrier pipeline. Current distinct va…". Governance signals: commerce_team: definition stale (last updated 2023-08-10); logistics_team: definition stale (last updated 2024-01-22).
- **Impact:** MEDIUM severity. 1500 downstream assets are at risk. A wrong 'Order Status vs Shipment State' silently feeds 0 decision surface(s) (0 dashboards, 0 models) across 2 teams.
- **Recommendation:** Open a data governance ticket for 'Order Status vs Shipment State'. Draft a canonical definition incorporating both teams' intent and circulate for sign-off in the next governance review cycle.

- **Blast radius:** 1500 downstream assets
- **Confidence:** 0.893 · **Est. cost if unreconciled:** $67,500
- **Risk:** A wrong 'Order Status vs Shipment State' silently feeds 0 decision surface(s) (0 dashboards, 0 models) across 2 teams.
- **Logic similarity:** 0.214 · **Name similarity:** 1.0

| Domain | Owner | Definition | Computation |
| --- | --- | --- | --- |
| commerce_team | urn:li:corpGroup:commerce-team | Lifecycle state of an order as tracked by the commerce platform. Current distinct values: 9. Used for customer-facing status pages, SLA reporting, and order management dashboards. Source of truth for order state. | `SELECT order_status FROM orders` |
| logistics_team | urn:li:corpGroup:logistics-team | Current state of a shipment in the carrier pipeline. Current distinct values: 3. Used for carrier tracking, warehouse SLAs, and delivery exception reporting. Independently updated from order_status — an order may be marked Delivered while a shipment shows In Transit. | `SELECT shipment_state FROM shipments` |


---

## Data Provenance

- **Dataset:** Fiction Retail E-Commerce dataset (fiction_retail.db — 150,000 orders across 10 tables)
- **Source URL:** Not established — developer notes describe this as a Kaggle dataset; not independently confirmed from repository history
- **Statement:** Generated in DEMO MODE. Rosetta queries this file read-only.
- **Rosetta-constructed:** MetricDefinition pairs (rosetta/fiction_retail_source.py), DataHub URN lineage graph, Glossary term URNs, Team ownership URNs, Severity scores, Canonical proposals (rosetta/broker.py)
- **Not established:** Original source URL; License; Whether data is synthetic
- **Scenario:** Retail: Supplementary scenario
- **Full provenance:** `DATA_PROVENANCE.md`
