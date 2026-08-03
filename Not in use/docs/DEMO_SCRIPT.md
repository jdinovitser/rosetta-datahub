# Rosetta — 3-Minute Demo Video Script

Judges watch fast and may stop at 3:00. Hook in the first 20 seconds, show the
approval and write-plan loop by 2:30, land the tagline.

---

**[0:00–0:20] The hook — the silent failure**
>Here are two executive dashboards. Same company, same month.
>Finance reports 2.1 million monthly active users. Marketing reports 3.4 million.
>Both numbers are technically correct based on their definitions. But they cannot both represent the same business metric.
>This semantic drift is the silent failure mode behind unreliable analytics and AI agents.
>

*(Screen: two dashboards side by side with different MAU numbers.)*

**[0:20–1:05] The scan**
"Rosetta is a linter for meaning. 
It analyzes your DataHub metadata graph — glossary terms, ownership, lineage, and metric logic — 
and finds where teams have different definitions hiding behind the same names."

*(Screen: run `python -m rosetta.orchestrator --report`. Graph view lights up;
"active_user" forks into two definitions across finance and marketing, flagged red.)*

> "It found five conflicts. The worst: 'billing amount' is defined two different
> ways across twelve downstream assets. Ranked by
> blast radius, because a conflict on your board deck matters more than one on a
> scratch table."

**[1:05–1:50] The reconciliation**
> "Rosetta drafts a canonical definition from the highest-coverage variant, then
> routes it to the actual owners it pulled from DataHub ownership metadata."

*(Screen: the proposed canonical definition and approvers list.)*

> "A human approves. Nothing is silently overwritten."

**[1:50–2:35] The write plan — validated and ready**
> "On approval, Rosetta generates a machine-readable write plan: upsert the
> canonical GlossaryTerm, link it to all twelve affected assets, deprecate the
> losing definition. The plan is validated and shown in full — in Demo Mode,
> nothing is executed against an external catalog."

*(Screen: the VALIDATED · NOT EXECUTED badge, the operations panel with URNs, the
Copy/Download JSON buttons.)*

> "In Connected Mode, Rosetta executes this exact plan — and then re-reads every
> entity from DataHub to confirm the state was applied correctly, not just that
> the API accepted the request."

**[2:35–3:00] Proof + tagline**
> "It's a five-agent pipeline, one hundred passing tests, Apache 2.0, and it ships
> as a reusable DataHub Skill any agent can call."

*(Screen: `pytest` green; the skill file.)*

Because AI agents are only as reliable as the metadata behind them. 
Rosetta doesn't just answer questions. 
It makes sure your whole company is asking the same one.

*(End card: repo URL + "Built on DataHub".)*
