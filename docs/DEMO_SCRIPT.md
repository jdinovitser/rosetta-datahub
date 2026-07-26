# Rosetta — 3-Minute Demo Video Script

Judges watch fast and may stop at 3:00. Hook in the first 20 seconds, show the
write-back loop by 2:30, land the tagline.

---

**[0:00–0:20] The hook — the silent failure**
> "Here are two executive dashboards. Same company, same month. Finance says we
> have 2.1 million monthly active users. Marketing says 3.4 million. Both are
> 'correct.' Both are wrong to somebody. This is the silent failure mode that
> breaks every talk-to-data agent — and nobody has fixed it in open source."

*(Screen: two dashboards side by side with different MAU numbers.)*

**[0:20–1:05] The scan**
> "Rosetta is a linter for meaning. It reads your entire DataHub graph — glossary
> terms, column descriptions, ownership, and the actual SQL behind each metric —
> through the MCP Server."

*(Screen: run `python -m rosetta.orchestrator --report`. Graph view lights up;
"active_user" forks into two definitions across finance and marketing, flagged red.)*

> "It found three conflicts. The worst: 'active user' is defined two different
> ways across twelve downstream assets and one ML feature table. Ranked by
> blast radius, because a conflict on your board deck matters more than one on a
> scratch table."

**[1:05–1:50] The reconciliation**
> "Rosetta drafts a canonical definition from the highest-coverage variant, then
> routes it to the actual owners it pulled from DataHub ownership metadata."

*(Screen: Slack/PR message to finance + marketing owners. One clicks Approve.)*

> "A human approves. Nothing is silently overwritten."

**[1:50–2:35] The write-back loop — the part that matters**
> "On approval, Rosetta writes back: it upserts the canonical glossary term,
> links it to all twelve affected assets, and deprecates the losing definition —
> without deleting history."

*(Screen: refresh DataHub. The canonical term now appears on every asset;
the old finance term shows a Deprecated badge.)*

> "The graph is now permanently smarter. The next analyst, and the next agent,
> inherit one agreed answer."

**[2:35–3:00] Proof + tagline**
> "It's a five-agent pipeline, thirty-two passing tests, Apache 2.0, and it ships
> as a reusable DataHub Skill any agent can call."

*(Screen: `pytest` green; the skill file.)*

> "Rosetta doesn't just answer questions. It makes sure your whole company is
> asking the same one."

*(End card: repo URL + "Built on DataHub".)*
