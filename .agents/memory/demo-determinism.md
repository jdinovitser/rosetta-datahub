---
name: Demo determinism
description: Why Rosetta's AI explanation and executive scoring layers are deterministic
---
Rule: keep every narrative/scoring layer (AI explanations, executive dashboard scores, governance signals) deterministic — template-based text, fixed constants (e.g. a hardcoded stale-date cutoff instead of "today - N days"), no LLM calls in the offline path.

**Why:** The hackathon demo must be reproducible on every run, exports must match the UI, and the test suite asserts on generated text. Time-relative logic or LLM output would make tests flaky and demo runs inconsistent.

**How to apply:** When enriching findings or scores, add constants documented in `rosetta/intelligence.py` rather than clock-based or model-based logic. Score coefficient tuning matters for the story — scores near 0 read as "broken app" to judges; keep worst-case demo scores in a plausible 35–70 band.
