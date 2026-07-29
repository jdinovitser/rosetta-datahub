# Rosetta Semantic Consistency Report

_Generated at 2026-07-21T15:37:57.478432+00:00_

## Summary

- **Total conflicts:** 3
- **Critical:** 0
- **High:** 1
- **Downstream assets at risk:** 24
- **Est. manual reconciliation cost avoided:** $1,080 (12.0 analyst-hours)

## Conflicts

### 1. `active_user` — silent_contradiction (HIGH)

> 'Monthly Active Users' (finance) and 'Monthly Active Users' (marketing) share a name but compute differently (logic overlap 13%).

- **Blast radius:** 12 downstream assets
- **Confidence:** 0.933 · **Est. cost if unreconciled:** $540
- **Risk:** A wrong 'active_user' silently feeds 8 decision surface(s) (7 dashboards, 1 models) across 2 teams.
- **Logic similarity:** 0.133 · **Name similarity:** 1.0

| Domain | Owner | Definition | Computation |
| --- | --- | --- | --- |
| finance | urn:li:corpGroup:finance-analytics | Users who completed at least one paid transaction in the trailing 30 days. | `COUNT(DISTINCT user_id) WHERE txn_amount > 0 AND event_date >= CURRENT_DATE - 30` |
| marketing | urn:li:corpGroup:growth-marketing | Any user with a session or app open in the last 30 days, bots excluded upstream by the safety pipeline. | `COUNT(DISTINCT user_id) WHERE session_start >= CURRENT_DATE - 30 AND is_bot = false` |

### 2. `revenue` — silent_contradiction (MEDIUM)

> 'Net Revenue' (finance) and 'Revenue' (sales) share a name but compute differently (logic overlap 16%).

- **Blast radius:** 6 downstream assets
- **Confidence:** 0.921 · **Est. cost if unreconciled:** $270
- **Risk:** A wrong 'revenue' silently feeds 3 decision surface(s) (3 dashboards, 0 models) across 2 teams.
- **Logic similarity:** 0.158 · **Name similarity:** 1.0

| Domain | Owner | Definition | Computation |
| --- | --- | --- | --- |
| finance | urn:li:corpGroup:finance-analytics | Gross bookings minus refunds and chargebacks, recognized in the period. | `SUM(booking_amount) - SUM(refund_amount) - SUM(chargeback_amount)` |
| sales | urn:li:corpGroup:sales-ops | Total value of closed-won deals booked in the period, before refunds. | `SUM(booking_amount) WHERE stage = 'closed_won'` |

### 3. `customer_churn~attrition` — hidden_synonym (MEDIUM)

> 'Churn Rate' and 'Customer Attrition' appear to be the same metric under different names (logic overlap 77%).

- **Blast radius:** 6 downstream assets
- **Confidence:** 0.808 · **Est. cost if unreconciled:** $270
- **Risk:** A wrong 'customer_churn~attrition' silently feeds 4 decision surface(s) (4 dashboards, 0 models) across 2 teams.
- **Logic similarity:** 0.769 · **Name similarity:** 0.0

| Domain | Owner | Definition | Computation |
| --- | --- | --- | --- |
| product | urn:li:corpGroup:product-analytics | Share of paying customers who cancelled their subscription in the period. | `COUNT(DISTINCT customer_id) WHERE subscription_status = 'cancelled' / COUNT(DISTINCT customer_id)` |
| customer_success | urn:li:corpGroup:customer-success | Fraction of paying customers who cancelled their subscription during the period. | `COUNT(DISTINCT customer_id) WHERE subscription_status = 'cancelled' / COUNT(DISTINCT customer_id)` |
