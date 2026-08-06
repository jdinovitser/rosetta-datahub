# Rosetta — 3-Minute Demo Script
**DataHub Agent Hackathon 2026 · Enterprise AI Data Intelligence Track**

---

## How to read this

| Column | Meaning |
|--------|---------|
| **SAY** | Speak these words (or close). Natural delivery beats perfect recitation. |
| **DO** | Exact click / gesture at that moment. Every label matches what is on screen. |

**Pacing:** ~140 words/min · Total SAY ≈ 420 words = 3:00 flat.
**Start state:** App open. Landing page visible. No walkthrough running.

---

## THE SCRIPT

| ⏱ | SAY | DO |
|----|-----|----|
| **0:00** | *"Your CFO just reported revenue to the board."* | Landing page open. Headline visible: **One metric. Two meanings. Silent chaos.** Pause one beat. |
| **0:04** | *"Two teams in DataHub define `billing_amount` differently — and neither one knows it. Clinical counts every charge, reversals and all. Finance strips them out. The disagreement lives in the metadata. Every pipeline says green."* | Point to the **DEMO MODE · OFFICIAL HACKATHON SAMPLE DATA** badge in the topbar. |
| **0:15** | *"1,215 rows in your downstream mart are negative. Twenty-eight million dollars of affected transaction value. No alert fired. No check failed. Nothing."* | Scroll to reveal the **CRITICAL CONFLICT DETECTED** problem card. |
| **0:23** | *"DataHub's own hackathon sample data — fifty-five thousand synthetic patient records. And this is Rosetta."* | Point to the card: **1,215 bad rows · $28.48M affected transaction value in sample data**. |
| **0:29** | *"Five specialized agents. One connected pipeline. Built natively on DataHub."* | Point to the agent row below: **Harvester · Detector · Blast Radius · Broker · Writer**. |
| **0:35** | *"Let's run it."* | Click **🏥 Healthcare Scan** in the topbar. *(Do NOT click "▶ Demo" or the hero button — those run a different scenario.)* |
| | | |
| **0:39** | *"Before Rosetta accuses anything, it reads everything — every GlossaryTerm, every SQL expression, every owner, every lineage edge across the full graph."* | **Step 1** appears. Four terminal lines tick: ✓ DataHub glossary terms loaded · ✓ Metric owners identified · ✓ Cross-domain lineage mapped · ✓ SQL logic extracted for comparison. |
| **0:49** | *"Ten metric definitions. Six business domains. Five hundred and eighty-five downstream assets in scope — before a single conflict flag is raised."* | Stats animate: **10** Metric Definitions · **6** Business Domains · **585** Downstream Assets. |
| **0:56** | *"Now watch."* | Click **Next →**. |
| | | |
| **0:58** | *"There it is."* | **Step 2** fills the screen. **🚨 CONFLICT DETECTOR · AGENT 2 OF 5** chip appears. Pause two full beats on the conflict card — let judges read the SQL. |
| **1:02** | *"`billing_amount`. Two teams. Two completely different calculations. Clinical: total charge from the EHR, reversals included. Finance: validated positive amounts only. Same metric name. No one ever compared them."* | Point to the **CRITICAL** badge, then to the two definition boxes — **clinical_team** SQL on the left, **finance_team** SQL on the right. |
| **1:12** | *"Twenty-three percent logic overlap — they agree on almost nothing. Eighty-eight percent confidence this conflict is real, not noise."* | Point to the three stat tiles: **88%** Conflict Confidence · **23%** Logic Similarity · **12** Assets at Risk. |
| **1:19** | *"Five conflicts total. Rosetta ranked them. This is the worst. How far has it already spread?"* | Let the tagline *"Same words. Different meaning."* hold. Click **Next →**. |
| | | |
| **1:23** | *"Everywhere."* | **Step 3** appears. **💥 BLAST-RADIUS ANALYZER · AGENT 3 OF 5** chip. Pause one beat. |
| **1:26** | *"Twelve downstream assets contaminated. Six datasets. mart_billing is the epicenter — and it has been quietly feeding every model and report downstream with a number that was never agreed on."* | Point to the three stat numbers: **12** Downstream Assets Contaminated · **$540** Est. Business Cost · **6.0** Analyst Hours. Point to the **📦 6 datasets** chip. |
| **1:37** | *"The real cost isn't the six hundred dollars. It's every decision that was made on this data."* | Let the dependency graph hold. Click **Next →**. |
| | | |
| **1:46** | *"Agent four doesn't just flag the problem. It closes it."* | **Step 4** appears. **🤝 RECONCILIATION BROKER · AGENT 4 OF 5** chip. |
| **1:49** | *"Clinical's definition. Finance's definition. One canonical GlossaryTerm that makes both intents true — a single source of truth for the entire pipeline."* | Point to the **Conflicting Definitions** panel: clinical_team vs finance_team. Then point to the **Proposed Canonical Definition** panel: **Billing Amount** with the **canonical** tag. |
| **1:58** | *"The write operations are already generated: one GlossaryTerm upserted, twelve assets tagged, five conflicting variants deprecated."* | Point to the **PROPOSED DATAHUB WRITE OPERATIONS** section: 📝 Canonical GlossaryTerm proposed · 🔗 12 downstream assets identified · 🗑 Conflicting definitions flagged. |
| **2:06** | *"But Rosetta will not touch DataHub until a human says so. Approval is enforced in code. The token is bound to the SHA-256 hash of this exact plan — change one byte, you need new approval."* | Point to **⚠ Human approval required — Rosetta will not write without it.** Pause one full beat. |
| **2:14** | *"Approved."* | Click **✓ Approve & Generate Write Plan**. Click **Next →**. |
| | | |
| **2:17** | *"Agent five — the Writer."* | **Step 5** appears. **✅ WRITER · AGENT 5 OF 5** chip. |
| **2:20** | *"Validated."* | Point to the **VALIDATED · NOT EXECUTED** badge. Pause. |
| **2:22** | *"Not executed. Every check passed. Human approval is on record. DataHub is untouched — waiting."* | Point to the status table inside the **Write plan generated & validated** box. |
| **2:30** | *"Five GlossaryTerms ready to write. Twelve assets queued for alignment. Five conflicting definitions flagged for retirement."* | Point to the three checklist items. |
| **2:37** | *"Machine-readable JSON — inspectable by any engineer, auditable by any stakeholder, submittable the moment you're ready."* | Click **▶ Machine-readable plan (JSON)** to expand it. Show the JSON panel briefly. |
| **2:43** | *"Every scan ships a full audit trail: JSON, CSV, Markdown, and a self-contained HTML report."* | Point to the export chips: **View Write Plan** · **Download JSON** · **Download Audit Report**. |
| **2:49** | *"In Connected Mode, these exact operations go to DataHub — and Rosetta re-reads every entity to confirm the write landed. No silent changes. Ever."* | Pause one beat on the VALIDATED · NOT EXECUTED badge. |
| **2:55** | *"Let's see what changed."* | Click **See the result →**. Page returns to the landing page and smooth-scrolls to the before/after section. |
| **2:57** | *"Before: three teams, three definitions, 1,215 bad rows."* | Let the **Three teams. Three definitions. One conflict resolved.** section hold on screen. Pause one beat. |
| **2:59** | *"After: one source of truth."* | Hold. Pause. |
| **3:01** | *"And a CFO who can trust the numbers."* | Hold. Let it land. |
| **3:04** | — | End. |

---

## 📋 Numbers cheat sheet — for Q&A

| Judges will ask | Answer |
|----------------|--------|
| What dataset? | DataHub hackathon healthcare sample — 55,500 synthetic patient records, published on GitHub |
| How many conflicts? | 5 (1 critical · 2 high · 2 medium) |
| Worst conflict | `billing_amount` — clinical vs finance |
| Evidence | 1,215 negative billing rows · $28,478,288 affected transaction value in mart_billing |
| Blast radius of `billing_amount` | 12 downstream assets (6 datasets) |
| Confidence on `billing_amount` | 88% (0.884) — structural graph analysis, no LLM |
| Logic similarity | 23% (they agree on almost nothing) |
| Second conflict | `patient_age` — clinical vs research · 832 impossible ages (−88 to 285) · blast 8 · 91% conf |
| Third conflict | `length_of_stay` — 277 date-swapped LOS records · blast 4 · 94% conf |
| Other conflicts | `test_results` (medium, blast 555, 90% conf) · `patient_name` (medium, blast 6) |
| Total assets at risk | 585 |
| What does Writer produce? | 5 GlossaryTerms prepared, 12 assets for linking, 5 conflicting variants flagged — machine-readable JSON write plan |
| What is VALIDATED · NOT EXECUTED? | Plan passed all checks and is ready to submit. Demo Mode never submits it. Connected Mode requires the same approval token. |
| Can it write to real DataHub? | Yes — Connected Mode executes the approved plan and re-reads every entity to verify. |
| Any LLM in the pipeline? | No — deterministic structural graph analysis throughout. |
| How is CRITICAL set? | Evidence-driven: 1,215 negative rows and $28.48M impact, not just graph topology. |

---

## 🗺 Exact label map — what's on screen where

| What the script says | Exact text on screen |
|---------------------|----------------------|
| Start the demo | **🏥 Healthcare Scan** — topbar, top-right *(use this one)* |
| Alt start | **🏥 Scan Healthcare** — dataset cards section |
| Alt start | **Run Healthcare Demo ›** — inside the CRITICAL CONFLICT DETECTED card |
| ⚠️ Do NOT use | **▶ Demo** or **Run the five-agent demo** — these run the active-user scenario, not billing_amount |
| Next between steps | **Next →** (bottom-right of each step panel) |
| Step 1 chip | 🔍 **HARVESTER · AGENT 1 OF 5** |
| Step 1 title | **Discover the meaning** |
| Step 1 stats | **10** Metric Definitions · **6** Business Domains · **585** Downstream Assets |
| Step 2 chip | 🚨 **CONFLICT DETECTOR · AGENT 2 OF 5** |
| Step 2 title | **Semantic collision detected** |
| Step 2 stats | **88%** Conflict Confidence · **23%** Logic Similarity · **12** Assets at Risk |
| Step 3 chip | 💥 **BLAST-RADIUS ANALYZER · AGENT 3 OF 5** |
| Step 3 title | **Measure the impact** |
| Step 3 stats | **12** Downstream Assets Contaminated · **$540** Est. Business Cost · **6.0** Analyst Hours |
| Step 3 asset chips | 📦 **6 datasets** |
| Step 4 chip | 🤝 **RECONCILIATION BROKER · AGENT 4 OF 5** |
| Step 4 title | **Create one trusted definition** |
| Step 4 approve button | **✓ Approve & Generate Write Plan** |
| Step 5 chip | ✅ **WRITER · AGENT 5 OF 5** |
| Step 5 title | **Write plan approved and validated** |
| Step 5 badge | **VALIDATED · NOT EXECUTED** |
| Step 5 checklist | 5 GlossaryTerms prepared · **12** assets for linking · 5 terms flagged |
| Step 5 JSON toggle | **▶ Machine-readable plan (JSON)** |
| Step 5 final button | **See the result →** (scrolls home to the before/after section) |
| Technical View (optional) | **⊙ Technical View** (navbar, 4th item) |

---

## 🎬 Recording checklist

- [ ] Browser at **1920 × 1080**, zoom **110%**
- [ ] Do one dry run first — DB warms up, animations are snappier on the second run
- [ ] Record audio separately; sync in post (eliminates keyboard and click noise)
- [ ] Move mouse **slowly and deliberately** — fast mouse reads as nervous
- [ ] At Step 2, **pause 2 seconds** on the conflict card before speaking — let judges read the SQL
- [ ] At Step 3, consider bumping browser to **125%** zoom for the blast-radius number reveal
- [ ] At Step 4, **pause one full beat before clicking Approve** — the hesitation makes the governance point land
- [ ] After clicking Approve, wait for Step 5 to fully render before pointing to VALIDATED · NOT EXECUTED
- [ ] Expand the JSON panel on Step 5 — it signals technical depth to judges
- [ ] Close on the **landing page hero** — clean final frame, good thumbnail
- [ ] Finish with silence after the last line — don't talk over the fade
