# Contributing Rosetta to the DataHub Skills Registry

This guide explains how to submit the `detect-semantic-conflicts` skill to the official DataHub skills registry.

---

## What you're contributing

**Skill:** `detect-semantic-conflicts`  
**Capability:** Five-agent semantic conflict detection and write-plan generation for DataHub metadata graphs.  
**Demo data:** Official Build with DataHub Hackathon 2026 healthcare dataset (55,500 synthetic patient records, no real PII).

---

## Pre-submission checklist

- [ ] All 100 tests pass: `pytest tests/ -q`
- [ ] Skill description file updated: `datahub-skill-contribution/detect-semantic-conflicts.md`
- [ ] `DEMO_CHECKLIST.md` reviewed and accurate
- [ ] `examples/input-manifest.json` covers all demo databases with SHA-256 checksums
- [ ] No secrets, credentials, or real PII in any file
- [ ] Demo runs offline with zero config: `python webapp/app.py`
- [ ] Approval enforcement verified: `apply_proposal` raises `ValueError` without a valid token

---

## Repository preparation

1. Ensure the repo is public: `github.com/<your-org>/rosetta-datahub`
2. Tag the submission commit:
   ```bash
   git tag v1.0.0-hackathon
   git push origin v1.0.0-hackathon
   ```
3. Confirm the README introduces Rosetta in one sentence (the linter for meaning).

---

## Files to include in the PR

| File | Purpose |
|---|---|
| `datahub-skill-contribution/detect-semantic-conflicts.md` | Skill specification |
| `datahub-skill-contribution/CONTRIBUTION_GUIDE.md` | This file |
| `DEMO_CHECKLIST.md` | Demo recording sequence |
| `rosetta/` | Full agent implementation |
| `tests/test_rosetta.py` | 100 tests including approval safety and post-write verification tests |
| `examples/input-manifest.json` | Data provenance and checksums |

---

## Skill metadata for the registry

```yaml
skill_id: detect-semantic-conflicts
display_name: "Detect Semantic Conflicts"
author: rosetta-datahub
version: 1.0.0
category: data-quality
tags:
  - semantic-governance
  - glossary
  - lineage
  - conflict-detection
  - data-quality
  - ai-readiness
datahub_version: ">=0.12.0"
python_version: ">=3.10"
entry_point: rosetta.detector.detect_conflicts
demo_url: "https://rosetta-datahub.replit.app"
source_url: "https://github.com/<your-org>/rosetta-datahub"
description: >
  Five-agent pipeline that detects when teams assign incompatible meanings to the
  same metric in DataHub, traces blast radius through lineage, proposes a canonical
  GlossaryTerm, enforces human approval, and generates a machine-readable write plan.
```

---

## Testing the skill in isolation

```bash
# 1. Install deps
pip install -r requirements.txt

# 2. Run detection on seed data (offline)
python -c "
from rosetta.datahub_client import RosettaDataHub
from rosetta.detector import detect_conflicts
dh = RosettaDataHub()
defs = dh.harvest_metric_definitions()
conflicts = detect_conflicts(defs)
print(f'{len(conflicts)} conflicts found')
for c in conflicts:
    print(f'  {c.metric} [{c.kind}] severity={c.severity}')
"

# 3. Run full test suite
pytest tests/ -q

# 4. Run web demo
python webapp/app.py
# Open http://localhost:5000, click "Run the five-agent demo"
```

---

## Notes for reviewers

- The detection algorithm is **entirely deterministic** — no LLM calls, no external APIs in Demo Mode.
- The `plan_id` is a SHA-256-derived hash of the exact operations proposed, so an approval token cannot authorize a modified plan.
- Rosetta never reads row-level data — only metadata URNs and GlossaryTerm definitions.
- The healthcare dataset is the official Build with DataHub Hackathon 2026 sample. The retail dataset is a supplementary scenario not affiliated with the hackathon.
