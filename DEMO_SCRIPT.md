# Rosetta — 3-Minute Demo Script
**DataHub Agent Hackathon 2026 · Enterprise AI Data Intelligence Track**

---

## How to read this

| Column | Meaning |
|--------|---------|
| **SAY** | Speak these words (or close). Natural delivery beats perfect recitation. |
| **DO** | Exact click / gesture at that moment. Every element name matches what's on screen. |

**Pacing:** ~140 words/min · Total SAY ≈ 420 words = 3:00 flat.  
**Start state:** App open at `https://rosetta-datahub.replit.app` · Landing page visible · No walkthrough running.

---

## THE SCRIPT

| ⏱ | SAY | DO |
|----|-----|----|
| **0:00** | *"Your CFO just reported twenty-eight and a half million dollars of revenue to the board."* | Landing page open. Hero visible — **One metric. Two meanings. Silent chaos.** Let it sit for one beat. |
| **0:05** | *"But inside your DataHub, clinical and finance define `billing_amount` differently. Clinical records every charge from the EHR — reversals included. Finance expects only validated, positive amounts. Nobody flags the disagreement. Every pipeline is green."* | Point to the **DEMO MODE · OFFICIAL HACKATHON SAMPLE DATA** badge in the topbar. |
| **0:17** | *"The result: 1,215 negative billing entries sitting in your downstream mart. Twenty-eight and a half million dollars. No alert. No error. Just wrong answers — shipped quietly."* | Scroll down slightly to reveal the **CRITICAL CONFLICT DETECTED** problem card. |
| **0:25** | *"This is the official hackathon dataset — fifty-five thousand synthetic patient records. This is Rosetta."* | Point to the problem card: **1,215 bad rows · $28.48M affected transaction value in sample data**. |
| **0:31** | *"A five-agent semantic linter, built natively on DataHub."* | Point to the five agent names below the card: **Harvester · Detector · Blast Radius · Broker · Writer**. |
| **0:36** | *"Let's run it."* | Click **"Run the five-agent demo"** button. |
| | | |
| **0:40** | *"Agent one — the Harvester. It reads your entire DataHub graph: glossary terms, metric owners, SQL logic, cross-domain lineage."* | **Step 1** appears. Four terminal lines tick off: ✓ DataHub glossary terms loaded · ✓ Metric owners identified · ✓ Cross-domain lineage mapped · ✓ SQL logic extracted for comparison. |
| **0:49** | *"Ten metric definitions. Three owning teams: clinical, finance, research. Five hundred and eighty-five downstream assets already in scope."* | Stats animate up: **10 Metric Definitions · 6 Business Domains · 585 Downstream Assets**. |
| **0:55** | *"Now watch what the Detector finds."* | Click **Next →**. |
| | | |
| **0:58** | *"Agent two — the Conflict Detector. Five semantic conflicts. All backed by real row counts from the database."* | **Step 2** fills the screen. **CRITICAL** badge appears on the lead conflict card. |
| **1:03** | *"The worst: `billing_amount`. Clinical computes it as base charge plus medication. Finance subtracts discounts instead. Twenty-three percent logic overlap — meaning they agree on almost nothing."* | Point to the two SQL definitions side by side on the conflict card. |
| **1:13** | *"Detection confidence: eighty-eight point four percent. No LLM — pure structural graph analysis."* | Point to the **confidence** badge on the card. |
| **1:18** | *"This isn't a typo. It's a fundamental disagreement about what revenue means — and every downstream system has been picking a side at random."* | Point to the tagline beneath the card: **"Same words. Different meaning."** Pause. |
| **1:26** | *"Five conflicts found. One critical, two high. Next — how far has it spread?"* | Click **Next →**. |
| | | |
| **1:29** | *"Agent three — the Blast-Radius Analyzer."* | **Step 3** appears. Blast-radius number begins to animate. |
| **1:32** | *"The `billing_amount` conflict alone reaches twelve downstream assets. mart_billing is carrying those 1,215 negative rows. mart_demographics is carrying 832 impossible patient ages — including ages of negative eighty-eight — because clinical and research never agreed on a valid-range constraint."* | Point to the blast-radius counter as it lands on **12**. Point to the narrative text below it. |
| **1:45** | *"Every dashboard, model, and regulatory report downstream of those marts is building on a foundation that never agreed on what the numbers mean."* | Let the screen hold. |
| **1:51** | *"AI Readiness: red."* | Click **Next →**. |
| | | |
| **1:54** | *"Agent four — the Reconciliation Broker. It merges clinical, finance, and research intent into one canonical definition."* | **Step 4** appears. Before-and-after panels visible. |
| **2:01** | *"Positive amounts only. Post-adjudication. The constraint is now explicit in the GlossaryTerm."* | Point to the **canonical** definition in the right panel. |
| **2:06** | *"And it generates the exact DataHub write operations: upsert the GlossaryTerm, attach it to every affected asset, deprecate the conflicting variants."* | Point to the **PROPOSED DATAHUB WRITE OPERATIONS** panel: `upsert_glossary_term` · `attach_term_to_asset` · `deprecate_term`. |
| **2:14** | *"Nothing executes yet. Approval is enforced in code — the token is bound to the SHA-256 hash of this exact plan. Change the plan, you need new approval."* | Point to the **✓ Approve & Generate Write Plan** button. Pause one beat. |
| **2:20** | *"Approved."* | Click **✓ Approve & Generate Write Plan**. Click **Next →**. |
| | | |
| **2:23** | *"Agent five — the Writer. Five GlossaryTerms to upsert. Fifteen assets to tag. Five conflicting variants to deprecate."* | **Step 5** appears. Write plan renders. |
| **2:30** | *"In Demo Mode —"* | Point prominently to the **VALIDATED · NOT EXECUTED** badge. |
| **2:32** | *"— validated, not executed. The plan is machine-readable, inspectable, and ready for a human to submit."* | Let badge hold. |
| **2:37** | *"In Connected Mode, Rosetta submits these exact operations to your DataHub instance — then re-reads every affected entity to verify the write was applied. No silent changes. Approval is tied to the hash."* | Click **⊙ Technical View** in the navbar. |
| **2:45** | *"Every scan produces a full audit trail — JSON, CSV, Markdown, and a self-contained HTML report."* | Point to the export buttons. Click one to show it. |
| | | |
| **2:50** | *"Data quality tells us whether the numbers are valid."* | Navigate back to the landing page hero. |
| **2:54** | *"Rosetta helps ensure everyone agrees on what those numbers mean."* | Pause. Hold on the hero. |
| **3:00** | — | End. |

---

## 📋 Numbers cheat sheet — for Q&A

| Judges will ask | Answer |
|----------------|--------|
| What dataset? | DataHub hackathon healthcare sample — 55,500 synthetic patient records, published on GitHub |
| How many conflicts? | 5 (1 critical · 2 high · 2 medium) |
| Worst conflict | `billing_amount` — clinical vs finance |
| Evidence for worst | 1,215 negative billing rows · $28,478,288 affected transaction value in mart_billing |
| Blast radius of worst | 12 downstream assets |
| Confidence on worst | 88.4% — structural graph analysis, no LLM |
| Second conflict | `patient_age` — clinical vs research · 832 impossible ages (−88 to 285) in mart_demographics · blast radius 8 |
| Third conflict | `length_of_stay` — 277 negative LOS records from admission/discharge date swap · blast radius 4 |
| Other conflicts | `test_results` (medium, blast 555) · `patient_name` (medium, blast 6) |
| Total assets at risk | 585 |
| What does Writer do? | Upserts 5 GlossaryTerms, attaches them to 15 assets, deprecates 5 conflicting variants |
| Does it need live DataHub? | No — runs fully offline. Runs on the hackathon sample dataset in Demo Mode |
| Can it write to real DataHub? | Yes — Connected Mode reads from your instance, executes the approved plan, verifies with read-back |
| How is severity set? | Evidence-driven: row counts and dollar impact, not just graph topology |
| Any AI / LLM in the pipeline? | No — deterministic graph traversal and structural analysis throughout |
| What is VALIDATED · NOT EXECUTED? | The plan passed all checks and is ready to submit. In Demo Mode it is never submitted. In Connected Mode, submission requires the same approval token. |

---

## 🎬 Recording checklist

- [ ] Browser at **1920 × 1080**, zoom **110%**
- [ ] Do a dry run first — DB warms up, animations are snappier on second run
- [ ] Record audio separately; sync in post (eliminates keyboard and click noise)
- [ ] Move mouse **slowly and deliberately** — fast mouse reads as nervous
- [ ] At Step 2, **pause 2 seconds** on the conflict card before speaking — let judges read it
- [ ] At Step 3, consider bumping browser to **125% zoom** for the blast-radius number reveal
- [ ] At Step 4, **pause before clicking Approve** — the beat of hesitation makes the governance point land
- [ ] After clicking Approve, wait for Step 5 to fully render before pointing to VALIDATED · NOT EXECUTED
- [ ] Close on the **landing page hero** — clean final frame, strong thumbnail
- [ ] Finish with silence after the last line — don't talk over the fade

---

## 🗺 Navigation map — what's on screen where

| What you say you'll click | Exact label on screen |
|--------------------------|----------------------|
| "Run the five-agent demo" | **Run the five-agent demo** (large primary button, hero section) |
| Healthcare demo from problem card | **Run Healthcare Demo ›** (smaller button inside CRITICAL CONFLICT DETECTED card) |
| Next between steps | **Next →** (bottom-right of each step panel) |
| Approve | **✓ Approve & Generate Write Plan** (Step 4) |
| Technical View | **⊙ Technical View** (navbar, fourth item) |
| Connect DataHub | **Connect DataHub** (topbar, left of the DEMO MODE badge) |
