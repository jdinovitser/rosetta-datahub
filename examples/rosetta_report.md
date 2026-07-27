# Rosetta Semantic Consistency Report

_Generated at 2026-07-27T19:38:40.971262+00:00_

## Summary

- **Total conflicts:** 6
- **Critical:** 1
- **High:** 2
- **Downstream assets at risk:** 63
- **Est. manual reconciliation cost avoided:** $2,835 (31.5 analyst-hours)

## Conflicts

### 1. `active_user` — silent_contradiction (CRITICAL)

> 'Monthly Active Users' (finance) and 'Monthly Active Users' (marketing) share a name but compute differently (logic overlap 13%).

**AI Explanation**

- **Finding:** 'Active User' has 2 incompatible definitions across finance and marketing — same name, different computation.
- **Evidence:** Logic similarity 13%, confidence 93%. Definitions: finance: "Users who completed at least one paid transaction in the trailing 30 day…"; marketing: "Any user with a session or app open in the last 30 days, bots excluded u…". Governance signals: marketing: definition stale (last updated 2024-03-02).
- **Impact:** CRITICAL severity. 22 downstream assets are at risk. A wrong 'Active User' silently feeds 15 decision surface(s) (11 dashboards, 4 models) across 2 teams.
- **Recommendation:** Escalate immediately: align finance and marketing leadership on a single canonical definition for 'Active User'. Freeze dependent pipelines until resolved. Rosetta can write the canonical GlossaryTerm to DataHub automatically.

- **Blast radius:** 22 downstream assets
- **Confidence:** 0.933 · **Est. cost if unreconciled:** $990
- **Risk:** A wrong 'Active User' silently feeds 15 decision surface(s) (11 dashboards, 4 models) across 2 teams.
- **Logic similarity:** 0.133 · **Name similarity:** 1.0

| Domain | Owner | Definition | Computation |
| --- | --- | --- | --- |
| finance | urn:li:corpGroup:finance-analytics | Users who completed at least one paid transaction in the trailing 30 days. | `COUNT(DISTINCT user_id) WHERE txn_amount > 0 AND event_date >= CURRENT_DATE - 30` |
| marketing | urn:li:corpGroup:growth-marketing | Any user with a session or app open in the last 30 days, bots excluded upstream by the safety pipeline. | `COUNT(DISTINCT user_id) WHERE session_start >= CURRENT_DATE - 30 AND is_bot = false` |

### 2. `arr` — silent_contradiction (MEDIUM)

> 'Annual Recurring Revenue' (finance) and 'Annual Recurring Revenue' (sales) share a name but compute differently (logic overlap 10%).

**AI Explanation**

- **Finding:** 'ARR' has 2 incompatible definitions across finance and sales — same name, different computation.
- **Evidence:** Logic similarity 10%, confidence 95%. Definitions: finance: "Sum of all active subscription MRR annualized, excluding one-time fees a…"; sales: "Total contract value of all active annual deals, including upsells and e…". Governance signals: sales: definition stale (last updated 2023-09-27).
- **Impact:** MEDIUM severity. 6 downstream assets are at risk. A wrong 'ARR' silently feeds 3 decision surface(s) (3 dashboards, 0 models) across 2 teams.
- **Recommendation:** Open a data governance ticket for 'ARR'. Draft a canonical definition incorporating both teams' intent and circulate for sign-off in the next governance review cycle.

- **Blast radius:** 6 downstream assets
- **Confidence:** 0.952 · **Est. cost if unreconciled:** $270
- **Risk:** A wrong 'ARR' silently feeds 3 decision surface(s) (3 dashboards, 0 models) across 2 teams.
- **Logic similarity:** 0.097 · **Name similarity:** 1.0

| Domain | Owner | Definition | Computation |
| --- | --- | --- | --- |
| finance | urn:li:corpGroup:finance-analytics | Sum of all active subscription MRR annualized, excluding one-time fees and professional services. | `SUM(monthly_subscription_amount * 12) WHERE subscription_status = 'active' AND revenue_type = 'recurring'` |
| sales | urn:li:corpGroup:sales-ops | Total contract value of all active annual deals, including upsells and expansion revenue booked in period. | `SUM(contract_value) WHERE deal_type = 'annual' AND stage = 'closed_won' AND contract_status = 'active'` |

### 3. `conversion_rate` — silent_contradiction (HIGH)

> 'Conversion Rate' (marketing) and 'Conversion Rate' (product) share a name but compute differently (logic overlap 16%).

**AI Explanation**

- **Finding:** 'Conversion Rate' has 2 incompatible definitions across marketing and product — same name, different computation.
- **Evidence:** Logic similarity 16%, confidence 92%. Definitions: marketing: "Percentage of website visitors who completed any tracked goal (signup, p…"; product: "Percentage of trial users who converted to a paid plan within 14 days of…".
- **Impact:** HIGH severity. 11 downstream assets are at risk. At least one ML model trains on this data — a wrong definition corrupts model signals silently. A wrong 'Conversion Rate' silently feeds 7 decision surface(s) (5 dashboards, 2 models) across 2 teams.
- **Recommendation:** Schedule a cross-team definition review for 'Conversion Rate' within this sprint. Propose one canonical term, notify all 11 asset owners, and deprecate the conflicting variant.

- **Blast radius:** 11 downstream assets
- **Confidence:** 0.92 · **Est. cost if unreconciled:** $495
- **Risk:** A wrong 'Conversion Rate' silently feeds 7 decision surface(s) (5 dashboards, 2 models) across 2 teams.
- **Logic similarity:** 0.16 · **Name similarity:** 1.0

| Domain | Owner | Definition | Computation |
| --- | --- | --- | --- |
| marketing | urn:li:corpGroup:growth-marketing | Percentage of website visitors who completed any tracked goal (signup, purchase, or trial) in the session. | `COUNT(DISTINCT goal_completions) / COUNT(DISTINCT sessions) * 100` |
| product | urn:li:corpGroup:product-analytics | Percentage of trial users who converted to a paid plan within 14 days of signup. | `COUNT(DISTINCT user_id WHERE subscription_start <= trial_start + 14) / COUNT(DISTINCT trial_user_id) * 100` |

### 4. `customer_ltv` — silent_contradiction (HIGH)

> 'Customer Lifetime Value' (finance) and 'LTV' (data_science) share a name but compute differently (logic overlap 0%).

**AI Explanation**

- **Finding:** 'Customer LTV' has 2 incompatible definitions across finance and data_science — same name, different computation.
- **Evidence:** Logic similarity 0%, confidence 100%. Definitions: finance: "Predicted gross margin a single account will generate over a five-year h…"; data_science: "Historical dollars collected from each customer since signup. No project…". Governance signals: finance: handles sensitive/PII data; data_science: no owner assigned — stewardship unclear; data_science: not registered in the business glossary; data_science: handles sensitive/PII data; data_science: definition stale (last updated 2023-11-02).
- **Impact:** HIGH severity. 12 downstream assets are at risk. At least one ML model trains on this data — a wrong definition corrupts model signals silently. A wrong 'Customer LTV' silently feeds 8 decision surface(s) (5 dashboards, 3 models) across 2 teams.
- **Recommendation:** Schedule a cross-team definition review for 'Customer LTV' within this sprint. Propose one canonical term, notify all 12 asset owners, and deprecate the conflicting variant.

- **Blast radius:** 12 downstream assets
- **Confidence:** 1.0 · **Est. cost if unreconciled:** $540
- **Risk:** A wrong 'Customer LTV' silently feeds 8 decision surface(s) (5 dashboards, 3 models) across 2 teams.
- **Logic similarity:** 0.0 · **Name similarity:** 1.0

| Domain | Owner | Definition | Computation |
| --- | --- | --- | --- |
| finance | urn:li:corpGroup:finance-analytics | Predicted gross margin a single account will generate over a five-year horizon, discounted to present value. | `SUM(projected_margin * discount_factor) OVER five_year_horizon` |
| data_science |  | Historical dollars collected from each customer since signup. No projection, no discounting. | `SUM(invoice_amount) GROUP BY customer_id` |

### 5. `revenue` — silent_contradiction (MEDIUM)

> 'Net Revenue' (finance) and 'Revenue' (sales) share a name but compute differently (logic overlap 16%).

**AI Explanation**

- **Finding:** 'Revenue' has 2 incompatible definitions across finance and sales — same name, different computation.
- **Evidence:** Logic similarity 16%, confidence 92%. Definitions: finance: "Gross bookings minus refunds and chargebacks, recognized in the period."; sales: "Total value of closed-won deals booked in the period, before refunds.". Governance signals: sales: definition stale (last updated 2025-01-19).
- **Impact:** MEDIUM severity. 6 downstream assets are at risk. A wrong 'Revenue' silently feeds 3 decision surface(s) (3 dashboards, 0 models) across 2 teams.
- **Recommendation:** Open a data governance ticket for 'Revenue'. Draft a canonical definition incorporating both teams' intent and circulate for sign-off in the next governance review cycle.

- **Blast radius:** 6 downstream assets
- **Confidence:** 0.921 · **Est. cost if unreconciled:** $270
- **Risk:** A wrong 'Revenue' silently feeds 3 decision surface(s) (3 dashboards, 0 models) across 2 teams.
- **Logic similarity:** 0.158 · **Name similarity:** 1.0

| Domain | Owner | Definition | Computation |
| --- | --- | --- | --- |
| finance | urn:li:corpGroup:finance-analytics | Gross bookings minus refunds and chargebacks, recognized in the period. | `SUM(booking_amount) - SUM(refund_amount) - SUM(chargeback_amount)` |
| sales | urn:li:corpGroup:sales-ops | Total value of closed-won deals booked in the period, before refunds. | `SUM(booking_amount) WHERE stage = 'closed_won'` |

### 6. `customer_churn~attrition` — hidden_synonym (MEDIUM)

> 'Churn Rate' and 'Customer Attrition' appear to be the same metric under different names (logic overlap 77%).

**AI Explanation**

- **Finding:** 'Customer Churn' and 'Attrition' are duplicate metrics across product and customer_success — same logic, different names.
- **Evidence:** Logic similarity 77%, confidence 81%. Definitions: product: "Share of paying customers who cancelled their subscription in the period…"; customer_success: "Fraction of paying customers who cancelled their subscription during the…".
- **Impact:** MEDIUM severity. 6 downstream assets are at risk. A wrong 'Customer Churn vs Attrition' silently feeds 4 decision surface(s) (4 dashboards, 0 models) across 2 teams.
- **Recommendation:** Open a data governance ticket for 'Customer Churn vs Attrition'. Draft a canonical definition incorporating both teams' intent and circulate for sign-off in the next governance review cycle.

- **Blast radius:** 6 downstream assets
- **Confidence:** 0.808 · **Est. cost if unreconciled:** $270
- **Risk:** A wrong 'Customer Churn vs Attrition' silently feeds 4 decision surface(s) (4 dashboards, 0 models) across 2 teams.
- **Logic similarity:** 0.769 · **Name similarity:** 0.0

| Domain | Owner | Definition | Computation |
| --- | --- | --- | --- |
| product | urn:li:corpGroup:product-analytics | Share of paying customers who cancelled their subscription in the period. | `COUNT(DISTINCT customer_id) WHERE subscription_status = 'cancelled' / COUNT(DISTINCT customer_id)` |
| customer_success | urn:li:corpGroup:customer-success | Fraction of paying customers who cancelled their subscription during the period. | `COUNT(DISTINCT customer_id) WHERE subscription_status = 'cancelled' / COUNT(DISTINCT customer_id)` |
