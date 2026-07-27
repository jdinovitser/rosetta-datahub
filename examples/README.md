# Rosetta — Sample Outputs

These files are real outputs from a single Rosetta scan against the built-in seed dataset.  
No setup required — judges can evaluate report quality without running any code.

## Files

| File | Format | Description |
|------|--------|-------------|
| [`rosetta_report.json`](rosetta_report.json) | JSON | Full machine-readable report — conflicts, AI explanations, blast-radius graphs, proposed reconciliations, impact metrics |
| [`rosetta_report.csv`](rosetta_report.csv) | CSV | Flat summary row per conflict — ideal for spreadsheet review or BI import |
| [`rosetta_report.md`](rosetta_report.md) | Markdown | Human-readable audit report with tables — renders on GitHub |
| [`rosetta_report.html`](rosetta_report.html) | HTML | Self-contained stakeholder report — open in any browser, no server needed |

## What the scan found

| Metric | Severity | Blast Radius | Confidence | Est. Cost if Unresolved |
|--------|----------|-------------|------------|------------------------|
| `active_user` | 🔴 CRITICAL | 22 assets | 93.3% | $990 |
| `customer_ltv` | 🟠 HIGH | 12 assets | 100% | $540 |
| `conversion_rate` | 🟠 HIGH | 11 assets | 92.0% | $495 |
| `arr` | 🟡 MEDIUM | 6 assets | 95.2% | $270 |
| `revenue` | 🟡 MEDIUM | 6 assets | 92.1% | $270 |
| `customer_churn~attrition` | 🟡 MEDIUM | 6 assets | 80.8% | $270 |

**Total:** 6 conflicts · 63 downstream assets at risk · **$2,835 estimated cost avoided** · 31.5 analyst-hours saved

## Notable findings

**`active_user` (CRITICAL)** — Finance and Marketing share the name "Monthly Active Users" but compute it differently:
- Finance: `COUNT(DISTINCT user_id) WHERE txn_amount > 0 AND event_date >= CURRENT_DATE - 30`  
- Marketing: `COUNT(DISTINCT user_id) WHERE session_start >= CURRENT_DATE - 30 AND is_bot = false`

Result: the CFO and CMO report numbers that are irreconcilably different — 22 downstream assets (11 dashboards, 4 ML models) inherit the contradiction silently.

**`customer_ltv` (HIGH, 0% logic overlap)** — Finance projects a 5-year discounted gross margin; Data Science sums historical invoices. Zero shared logic. The LTV predictor ML model trains on whichever definition it happened to ingest first.

**`customer_churn~attrition` (hidden synonym)** — Product calls it "Churn Rate"; Customer Success calls it "Customer Attrition." Logic similarity: 77%. These are the same metric under different names — Rosetta flags the duplication so the glossary can be collapsed to one canonical term.

## AI Readiness scores from this scan

```
Data Health Score:       47 / 100
Governance Maturity:     34 / 100
AI Readiness Score:      26 / 100  ← ML models training on semantically inconsistent features
```

A score of 26/100 on AI Readiness means ML pipelines in this environment are at material risk of training on contradictory feature definitions — without any error or warning from the platform.
