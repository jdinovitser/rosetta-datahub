# Rosetta — 3-Minute Demo Script
### DataHub Agent Hackathon · Enterprise AI Data Intelligence Track

---

## How to read this

| Column | Meaning |
|--------|---------|
| **SAY** | Speak these words exactly (or close to it) |
| **DO** | What to click / show on screen at that moment |

Pacing: ~140 words/min. Total script ≈ 415 spoken words = **~3:00 flat.**

---

## THE SCRIPT

| ⏱ | SAY | DO |
|---|-----|----|
| **0:00** | *"Your CFO just reported revenue to the board."* | Open app. Landing page visible — Rosetta hero, three problem cards. |
| **0:04** | *"But the revenue mart has 1,215 negative billing amounts hiding inside it — twenty-eight and a half million dollars of corrupted data."* | Point to the "$28M Hidden in Plain Sight" problem card. |
| **0:12** | *"Meanwhile, your research team is training a patient-risk model on ages that go up to two hundred and eighty-five."* | Point to the "AI Models Train on Corrupt Data" card. |
| **0:18** | *"No errors. No alerts. Just wrong answers — quietly shipped."* | Let the screen breathe. |
| **0:22** | *"This is what semantic inconsistency looks like in healthcare data. And it's happening inside your DataHub — right now."* | Pause on the hero title. |
| **0:28** | *"This is Rosetta."* | Gesture to the screen. |
| | | |
| **0:30** | *"Rosetta is a five-agent pipeline built natively on DataHub."* | Point to the five progress dots — DISCOVER · DETECT · IMPACT · RECONCILE · WRITE. |
| **0:35** | *"It reads your entire graph, finds where teams silently disagree on meaning, maps how far that disagreement has already spread — and writes the truth back."* | Point to each dot in sequence. |
| **0:45** | *"Let's run it on the real DataHub hackathon healthcare dataset — fifty-five thousand patient records."* | Click **🏥 Live Healthcare Data**. |
| | | |
| **0:48** | *"Agent one — the Harvester — reads the DataHub graph."* | Step 1 appears. Watch numbers animate. |
| **0:53** | *"Nine metric definitions. Three owning teams: clinical, finance, research. The pipeline flows from raw patients through staging into two downstream marts — billing and demographics."* | Point to each stat as it lands. |
| **1:00** | *"Now watch what the Conflict Detector finds."* | Click **Next →**. |
| | | |
| **1:03** | *"Agent two finds five semantic conflicts — all backed by real rows in the database."* | Step 2 fills the screen. |
| **1:08** | *"'Billing Amount' — clinical team versus finance team. Clinical records any charge from the EHR, including reversals. Finance expects only validated positive amounts. The disagreement has already landed 1,215 negative rows in the billing mart."* | Point to the billing_amount conflict card. |
| **1:18** | *"'Patient Age' — clinical versus research. Same source column. Research adds a valid-range constraint: zero to a hundred and twenty. Clinical doesn't. Result: eight hundred and thirty-two impossible ages in the demographics mart — and they're training models on this."* | Point to the patient_age conflict card. |
| **1:30** | *"Rosetta found all five conflicts. Confidence on the critical one: eighty-eight percent. No LLM — pure structural graph analysis."* | Point to the confidence badge. |
| **1:38** | *(no words — let it land)* | Click **Next →**. |
| | | |
| **1:40** | *"Agent three maps the blast radius."* | Step 3: three numbers animate up. |
| **1:44** | *"The billing_amount conflict alone reaches twelve downstream assets."* | Point to the blast-radius number. |
| **1:47** | *"Look at the dependency graph — raw patients feeds staging, which feeds both marts. Every downstream dashboard, every model, every regulatory report pulling from mart_billing is carrying that twenty-eight million dollar error."* | Trace the graph from the metric node outward to the red downstream nodes. |
| **1:58** | *"AI Readiness score for this pipeline: we're in the red."* | Let the graph and numbers speak. Click **Next →**. |
| | | |
| **2:04** | *"Agent four — the Reconciliation Broker — proposes a canonical definition."* | Step 4: before/after panels appear. |
| **2:09** | *"It merges clinical, finance, and research intent into one: 'Net validated charge for a patient encounter — positive amounts only, post-adjudication, USD.' Adds the constraint. Removes the ambiguity."* | Point to the green canonical definition in the after-panel. |
| **2:18** | *"Human approval required before anything changes."* | Point to the Approve button. Pause one beat. |
| **2:21** | *"Approved."* | Click **Approve**. Click **Next →**. |
| | | |
| **2:24** | *"Agent five — the Writer — pushes the canonical GlossaryTerm back to DataHub."* | Step 5: checklist items tick off. |
| **2:29** | *"Stale definition flagged. All three team owners notified. Conflict resolved. mart_billing and mart_demographics are now protected by the canonical constraint."* | Point to each checklist item as it completes. |
| **2:37** | *"Every scan produces a full audit trail — JSON, CSV, Markdown, and a self-contained HTML report ready for compliance review."* | Click **Developer View**. Show export bar. Click one — show the download. |
| | | |
| **2:46** | *"Rosetta doesn't require a live DataHub to run. This demo ran entirely offline on a real sample dataset — fifty-five thousand records, real planted defects, real propagated errors."* | Return to landing hero. |
| **2:54** | *"The data was never malicious."* | Pause. |
| **2:57** | *"It just meant different things to different teams."* | Fade or cut. |

---

## 📋 Numbers cheat sheet · for Q&A

| What judges will ask | Answer |
|----------------------|--------|
| What dataset is this? | DataHub hackathon healthcare sample — 55,500 synthetic patient records |
| How many conflicts? | **5** (1 critical · 2 high · 2 medium) |
| Worst conflict | **billing_amount** — clinical vs finance |
| Evidence for worst | **1,215 negative billing rows** · **$28,478,287 misreported revenue** in mart_billing |
| Blast radius of worst | **12 assets** (scales from 1,215 affected rows) |
| Confidence on worst | **88%** — structural graph analysis, no LLM |
| Patient age issue | **832 impossible ages** (−88 to 285) reaching mart_demographics |
| Date swap issue | **277 negative length_of_stay values** in mart_billing from admission/discharge swap |
| NULL names | **555 NULL patient names** — research cohort tracking broken |
| Total assets at risk | **585** (scaled from real row counts) |
| Does it need a live DataHub? | No — runs fully offline. Click **🏥 Live Healthcare Data** on the landing page |
| Can it write back to real DataHub? | Yes — swap the SQLite source for the live DataHub client; the five agents are unchanged |
| How is severity set? | Evidence-driven: row count and dollar impact, not just graph size |
| Is anything AI-generated? | No LLM in the pipeline — deterministic graph traversal + structural analysis |

---

## 🎬 Recording checklist

- [ ] Browser at **1920 × 1080**, zoom **110%**
- [ ] Click **🏥 Live Healthcare Data** (not "Run Rosetta Demo") — this tells the real story
- [ ] Run the scan once before recording so the DB is warm (faster transitions)
- [ ] Record audio separately, sync in post (kills keyboard + click noise)
- [ ] Move mouse **slowly and deliberately** — fast mouse looks nervous
- [ ] Zoom browser to **150%** during graph reveal (Step 3) for visual impact
- [ ] Use the **🎯 90-Second Judge Demo** button as B-roll (auto-advances, no clicks needed)
- [ ] Finish on the landing page hero — clean final frame for the thumbnail
