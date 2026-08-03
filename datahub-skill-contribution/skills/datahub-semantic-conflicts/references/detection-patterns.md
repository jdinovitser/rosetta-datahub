# Semantic Conflict Detection Patterns

Reference for classifying and scoring GlossaryTerm definition conflicts in DataHub.

---

## Conflict classification

### Silent contradiction

Two or more terms share the same (or near-same) concept name but have incompatible definitions. Consumers cannot use both safely — they will silently produce different numbers for the "same" metric.

**Common patterns:**

| Axis | Example mismatch |
| ---- | ---------------- |
| Temporal window | "last 7 days" vs. "last 30 days" for the same activity metric |
| Inclusion criteria | "all users" vs. "paying users only" for an engagement metric |
| Calculation method | "distinct count" vs. "session count" for a user activity metric |
| Scope boundary | "per account" vs. "per user" for a revenue metric |
| NULL handling | "NULL treated as 0" vs. "NULL excluded" for an aggregation |

**Action:** Resolve with a canonical definition. Severity depends on blast radius.

### Hidden synonym

Two or more terms have different concept names but equivalent (or near-equivalent) semantics. No consumer is misled, but the glossary is cluttered, and cross-team reports cannot reference a shared term.

**Common patterns:**

| Pattern | Example |
| ------- | ------- |
| Abbreviation vs. full name | `mau` and `monthly_active_users` |
| Team-specific naming | `revenue` (finance) and `total_sales` (operations) with identical formulas |
| Versioned names without version differences | `conversion_rate_v2` and `conversion_rate` with the same definition |
| Domain-prefixed duplicates | `product.active_users` and `growth.active_users` with matching semantics |

**Action:** Consolidate under one canonical name. Deprecate the lower-coverage term. Severity is typically medium.

### Minor variant

Two or more terms share the same concept name and have semantically equivalent definitions that differ only in wording, capitalization, or punctuation.

**Common patterns:**

| Pattern | Example |
| ------- | ------- |
| Sentence case vs. noun phrase | "Users who placed an order" vs. "A user that has placed at least one order" |
| Present tense vs. past tense | "Revenue generated" vs. "Revenue that is generated" |
| Precision difference | "orders in the current quarter" vs. "orders in the current quarter (calendar, UTC)" |

**Action:** Standardise wording. Low priority unless the term is high-traffic. No deprecation required — one term can be updated to match the other.

---

## Name normalisation algorithm

Before grouping terms for comparison:

1. Lowercase: `Active Users` → `active users`
2. Normalise separators (hyphens, underscores, dots → single space): `active_users` → `active users`
3. Remove common prefixes that add no semantic meaning: `total`, `count of`, `number of`
4. Strip version suffixes: `_v1`, `_v2`, `_2024`, `_new`, `_old`, `_legacy`
5. Collapse plural (`users` → `user`, `sessions` → `session`, `orders` → `order`)

Two terms whose normalised names are **identical** or within **Levenshtein distance 1** are placed in the same comparison group.

---

## Definition similarity heuristics

These are guides for agent reasoning — not formal algorithms. The agent should apply judgment.

### Temporal window check

Extract time-range language from both definitions:

- Look for: `last N days`, `past N days`, `previous N days`, `rolling N-day`, `calendar month`, `current quarter`, `YTD`
- If both definitions mention a time range and the ranges differ → **temporal window mismatch** (strong contradiction signal)
- If one definition mentions a range and the other does not → **scope ambiguity** (weaker signal; ask the user to clarify)

### Scope and inclusion check

Extract population or filter language:

- Look for: `paying users`, `trial users`, `internal accounts`, `active subscriptions`, `completed orders`, `voided`, `refunded`, `cancelled`
- If both definitions mention population filters and the filters differ → **inclusion criteria mismatch** (strong contradiction signal)

### Computation logic check

If structured properties or description text includes SQL, formulas, or pseudocode:

- Extract the key aggregation function: `COUNT(DISTINCT ...)`, `SUM(...)`, `AVG(...)`, `RATIO(...)`
- Extract the key filter predicate: `WHERE status = 'completed'`, `WHERE event_type IN (...)`
- Compare aggregation function and predicate — differences at either level indicate a **computation mismatch**

---

## Severity scoring

| Severity | Criteria | Recommended urgency |
| -------- | -------- | ------------------- |
| `critical` | Silent contradiction with > 20 total downstream assets | Address before next reporting cycle |
| `high` | Silent contradiction with 5–20 downstream assets | Address within the quarter |
| `medium` | Silent contradiction with < 5 downstream assets, or any hidden synonym | Address in next glossary review |
| `low` | Minor variant, or undefined term with no downstream assets | Address when convenient |

Severity is re-evaluated after blast radius is measured (Step 4). Initial classification in Step 3 uses estimated impact.

---

## Confidence levels

When reporting a conflict, include a confidence level based on evidence quality:

| Confidence | Basis |
| ---------- | ----- |
| High | Definitions contain explicit, contradicting factual claims (different time windows, different filter predicates) |
| Medium | Definitions are ambiguous — one is more general than the other, or key terms are undefined |
| Low | Definitions are in different languages/styles; similarity cannot be determined from text alone |

For low-confidence pairs, present both definitions to the user and ask them to adjudicate rather than asserting a conflict type.
