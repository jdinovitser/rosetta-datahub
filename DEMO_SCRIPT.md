# Rosetta — 3-Minute Demo Script
### DataHub Agent Hackathon · Enterprise AI Data Intelligence Track

---

## The story in six beats

> **Teams define a metric differently.**
> Rosetta discovers the conflict.
> It traces the downstream impact.
> It recommends a canonical definition.
> It writes the fix back to DataHub.
> The metadata graph is now consistent.

Anchor every sentence you say back to one of these six beats.

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
| **0:00** | *"Your CFO just reported revenue to the board."* | Open app. Landing page visible — dark hero, Rosetta mascot, bold headline "Your teams define the same metric differently", AI steward one-liner, agent pipeline animation. |
| **0:04** | *"But the revenue mart has 1,215 negative billing amounts hiding inside it — twenty-eight and a half million dollars of corrupted data."* | Scroll slightly to show the dataset cards section. |
| **0:12** | *"Meanwhile, your research team is training a patient-risk model on ages that go up to two hundred and eighty-five."* | Point to the Healthcare dataset card. |
| **0:18** | *"No errors. No alerts. Just wrong answers — quietly shipped."* | Let the screen breathe. |
| **0:22** | *"This is what semantic inconsistency looks like in healthcare data. And it's happening inside your DataHub — right now."* | Pause on the hero headline. |
| **0:28** | *"This is Rosetta — an AI data steward that automatically detects, explains, and repairs semantic inconsistencies in DataHub."* | Gesture to the AI steward one-liner on screen. |
| | | |
| **0:33** | *"Five agents. One pipeline. Fully integrated with DataHub."* | Point to the five agent nodes — Harvester, Detector, Blast Radius, Broker, Writer. |
| **0:38** | *"It reads your entire graph, finds where teams silently disagree on meaning, maps how far that disagreement has already spread — and writes the truth back."* | Point to each node in sequence. |
| **0:45** | *"Let's run it on the real DataHub hackathon healthcare dataset — fifty-five thousand patient records."* | Click **🏥 Healthcare Scan** in the top nav. Progress dots appear: DISCOVER · DETECT · IMPACT · RECONCILE · WRITE. |
| | | |
| **— BEAT 1: Teams define a metric differently —** | | |
| **0:48** | *"Agent one — the Harvester — reads the DataHub graph."* | Step 1 appears. Watch numbers animate. |
| **0:53** | *"Nine metric definitions. Three owning teams: clinical, finance, research. The same words — used completely differently."* | Point to each stat as it lands. |
| **1:00** | *"Now watch what the Conflict Detector finds."* | Click **Next →**. |
| | | |
| **— BEAT 2: Rosetta discovers the conflict —** | | |
| **1:03** | *"Agent two finds five semantic conflicts — all backed by real rows in the database."* | Step 2 fills the screen. |
| **1:08** | *"'Billing Amount' — clinical team versus finance team. Clinical records any charge from the EHR, including reversals. Finance expects only validated positive amounts. The disagreement has already landed 1,215 negative rows in the billing mart."* | Point to the billing_amount conflict card. |
| **1:18** | *"'Patient Age' — clinical versus research. Same source column. Research adds a valid-range constraint: zero to a hundred and twenty. Clinical doesn't. Result: eight hundred and thirty-two impossible ages — and they're training models on this."* | Point to the patient_age conflict card. |
| **1:30** | *"Rosetta found all five conflicts. Confidence on the critical one: eighty-eight percent. No LLM — pure structural graph analysis."* | Point to the confidence badge. |
| **1:38** | *(no words — let it land)* | Click **Next →**. |
| | | |
| **— BEAT 3: It traces the downstream impact —** | | |
| **1:40** | *"Agent three maps the blast radius."* | Step 3: three numbers animate up. |
| **1:44** | *"The billing_amount conflict alone reaches twelve downstream assets."* | Point to the blast-radius number. |
| **1:47** | *"Raw patients feeds staging, which feeds both marts. Every downstream dashboard, every model, every regulatory report is carrying that twenty-eight million dollar error."* | Trace the graph from the metric node outward to the red downstream nodes. |
| **1:58** | *"AI Readiness score for this pipeline: we're in the red."* | Let the graph speak. Click **Next →**. |
| | | |
| **— BEAT 4: It recommends a canonical definition —** | | |
| **2:04** | *"Agent four — the Reconciliation Broker — proposes a canonical definition."* | Step 4: before/after panels appear. |
| **2:09** | *"It merges clinical, finance, and research intent into one: 'Net validated charge for a patient encounter — positive amounts only, post-adjudication, USD.' One definition. Zero ambiguity."* | Point to the green canonical definition in the after-panel. |
| **2:18** | *"But Rosetta won't touch DataHub without a human sign-off."* | Point to the 'WRITES TO DATAHUB ON APPROVAL' callout — three operations listed. |
| **2:21** | *"Approved."* | Click **✓ Approve & Write to DataHub**. |
| | | |
| **— BEAT 5: It writes the fix back to DataHub —** | | |
| **2:24** | *"Agent five — the Writer — pushes the canonical GlossaryTerm back to DataHub."* | Step 5 appears. |
| **2:29** | *"Canonical term created. Twenty-two downstream assets linked. Conflicting definitions deprecated."* | Point to each checklist item. |
| | | |
| **— BEAT 6: The metadata graph is now consistent —** | | |
| **2:35** | *"mart_billing and mart_demographics are now protected by the canonical constraint. The graph is consistent. The conflict is resolved — permanently."* | Let the screen breathe on the final step. |
| **2:42** | *"Every scan produces a full audit trail — JSON, CSV, Markdown, and a self-contained HTML report ready for compliance review."* | Point to the export chips. Click one to show the download. |
| | | |
| **2:50** | *"Rosetta doesn't require a live DataHub to run. This demo ran entirely offline on a real sample dataset."* | Click **⌂ Home** in the top-right to return to the landing page. |
| **2:56** | *"The data was never malicious."* | Pause. |
| **2:58** | *"It just meant different things to different teams."* | Fade or cut on the hero headline. |

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
| Does it need a live DataHub? | No — runs fully offline. Click **🏥 Healthcare Scan** in the top nav. To use a live instance, click **Connect DataHub** → use the free Acryl demo at demo.datahubproject.io (~60 sec to get a token) |
| Can it run on retail data? | Yes — click **🛍️ Retail Scan** for the Fiction Retail e-commerce dataset (150,000 orders, discount unit-convention conflict) |
| Can it write back to real DataHub? | Yes — Connect DataHub, run a scan, approve in Step 4, and Rosetta writes the canonical GlossaryTerm, links assets, and deprecates conflicting terms live |
| How is severity set? | Evidence-driven: row count and dollar impact, not just graph size |
| Is anything AI-generated? | No LLM in the pipeline — deterministic graph traversal + structural analysis |

---

## 🎬 Recording checklist

- [ ] Browser at **1920 × 1080**, zoom **110%**
- [ ] Click **🏥 Healthcare Scan** in the top nav (not **▶ Run Demo** — the healthcare scan tells the real story)
- [ ] Run the scan once before recording so the DB is warm (faster transitions)
- [ ] Record audio separately, sync in post (kills keyboard + click noise)
- [ ] Move mouse **slowly and deliberately** — fast mouse looks nervous
- [ ] Zoom browser to **150%** during graph reveal (Step 3) for visual impact
- [ ] Finish on the landing page hero (click **⌂ Home**) — clean final frame for the thumbnail
