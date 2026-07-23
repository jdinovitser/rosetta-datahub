# Devpost Submission Checklist

- [ ] **Public repo** pushed (GitHub/GitLab).
- [ ] **Apache-2.0 LICENSE** file at repo root (included). On GitHub, confirm the About sidebar shows "Apache-2.0".
- [ ] **Live testable URL** deployed (Replit/Render/Docker). Verify "Run the five-agent demo" works in an incognito window.
- [ ] **README** with clear setup instructions (included).
- [ ] **Text description** — copy from `docs/SUBMISSION.md` into the Devpost fields.
- [ ] **Demo video** < 3 min, public on YouTube/Vimeo (see `docs/DEMO_RECORDING_GUIDE.md`). Link added.
- [ ] **examples/ folder** with sample outputs (included: report + reconciled term + exports in json/csv/md/html).
- [ ] **Tests pass**: `pytest -q` → 32 passed.
- [ ] **Bonus OSS**: `skills/detect-semantic-conflicts.md` reusable DataHub Skill.
- [ ] Paste URLs into `docs/SUBMISSION.md` placeholders.

## The six judging criteria — how Rosetta scores
1. **Use of DataHub** — reads glossary/lineage/ownership, writes canonical terms back (upsert, add_term, deprecate).
2. **Technical Execution** — 5-agent pipeline, 26 tests, hosted app, 4 export formats.
3. **Originality** — targets conflicting metric definitions, the pain a judge called unsolved; not a re-run of prior winners.
4. **Real-World Usefulness** — silent metric contradictions are a top cause of broken trust in data.
5. **Submission Quality** — themed UI, diagram, samples, docs, video.
6. **Bonus OSS** — reusable skill contribution.
