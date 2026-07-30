# Rosetta — 3-Minute Demo Script
### DataHub Agent Hackathon · Enterprise AI Data Intelligence Track

---

## The story in six beats

> **Three teams. One metric. Three different answers.**
> Rosetta finds the disagreement.
> It traces every downstream asset the conflict has already poisoned.
> It proposes the one definition that resolves it.
> A human approves. Rosetta writes the fix to DataHub.
> The graph is consistent. The conflict is gone — permanently.

Anchor every sentence you say back to one of these six beats.

---

## How to read this

| Column | Meaning |
|--------|---------|
| **SAY** | Speak these words exactly (or close to it) |
| **SCREEN** | What is visible on screen at that moment |
| **DO** | What to click |

Pacing: ~140 words/min. Total script ≈ 420 spoken words = **~3:00 flat.**

---

## THE SCRIPT

### OPENING HOOK (0:00 – 0:28)

| ⏱ | SAY | SCREEN | DO |
|---|-----|--------|----|
| **0:00** | *"Right now, inside your DataHub, three teams are answering the same question with three completely different numbers — and every single one of them is confident they're right."* | Landing page. Dark hero, Rosetta mascot, bold headline **"Your teams define the same metric differently."** | Open app. Let the headline breathe. |
| **0:09** | *"No alerts. No errors. The pipeline is green. The numbers are just… quietly wrong."* | Same screen. | Pause. |
| **0:14** | *"In this dataset alone: 1,215 negative billing amounts hiding in the revenue mart — twenty-eight and a half million dollars of corrupted data. And eight hundred and thirty-two patient ages that go up to two hundred and eighty-five — a research model is training on this right now."* | Scroll slightly to show the dataset cards. | Point to the **🏥 Healthcare** card. |
| **0:26** | *"This is Rosetta — an AI data steward that finds the conflict, traces the damage, and writes the fix straight back to DataHub."* | Gesture to the **"AI data steward"** subtitle line. | — |

---

### BEAT 1 — Teams define a metric differently (0:28 – 0:48)

| ⏱ | SAY | SCREEN | DO |
|---|-----|--------|----|
| **0:28** | *"Let's run it on fifty-five thousand real patient records."* | Top nav visible: **🏥 Healthcare Scan**. | Click **🏥 Healthcare Scan** in the top nav. Progress bar appears: DISCOVER · DETECT · IMPACT · RECONCILE · WRITE. |
| **0:33** | *"Agent one — the Harvester. It reads every metric definition in the DataHub graph."* | **Step 1 · HARVESTER · AGENT 1 OF 5.** Title: **"Discover the meaning."** Four terminal lines tick to done: ✓ DataHub glossary terms loaded / ✓ Metric owners identified / ✓ Cross-domain lineage mapped / ✓ SQL logic extracted for comparison. | Watch the terminal lines tick. |
| **0:40** | *"Nine metric definitions. Three business domains. Sixty-three downstream assets already in the graph."* | Three stats animate up: **Metric Definitions / Business Domains / Downstream Assets.** | Point to each number as it lands. |
| **0:46** | *"It understands how your organisation defines its data — before anyone knows the definitions disagree."* | Bottom quote fades in: *"Rosetta starts by understanding how your organisation defines its data — before anyone knows the definitions disagree."* | Click **Next →**. |

---

### BEAT 2 — Rosetta discovers the conflict (0:48 – 1:38)

| ⏱ | SAY | SCREEN | DO |
|---|-----|--------|----|
| **0:50** | *"Agent two — the Conflict Detector. Semantic collision detected."* | **Step 2 · CONFLICT DETECTOR · AGENT 2 OF 5.** Title: **"Semantic collision detected."** Subtitle: **"Same word. Completely different meaning."** | — |
| **0:55** | *"'Billing Amount.' Clinical records any charge from the EHR — including reversals. Finance expects only validated positive amounts. Both teams call it the same thing. It means opposite things."* | The **CRITICAL · silent contradiction** spotlight card shows two team definitions side by side with **≠** between them. | Point to the left definition (Clinical), then the ≠, then the right (Finance). |
| **1:08** | *"Conflict confidence: eighty-eight percent. Logic similarity: twelve percent. Twelve downstream assets already carrying that error."* | Three stats: **Conflict Confidence % / Logic Similarity % / Assets at Risk.** | Point to each badge. |
| **1:16** | *"Rosetta found this with no LLM — pure structural graph analysis."* | Bottom tagline: **"Same words. Different meaning."** | Click **Next →**. |

---

### BEAT 3 — It traces the downstream impact (1:20 – 1:58)

| ⏱ | SAY | SCREEN | DO |
|---|-----|--------|----|
| **1:22** | *"Agent three — the Blast-Radius Analyzer. How far does a wrong billing_amount travel downstream?"* | **Step 3 · BLAST-RADIUS ANALYZER · AGENT 3 OF 5.** Title: **"Measure the impact."** | Watch three numbers animate. |
| **1:28** | *"Twelve downstream assets contaminated. Twenty-eight million dollars estimated cost if left unresolved. Eighty-plus analyst hours to fix this by hand."* | Three large numbers: **Downstream Assets Contaminated / Estimated Business Cost if Unresolved / Analyst Hours to Fix Manually.** | Point to each number in sequence. |
| **1:36** | *"Dashboards, AI models, datasets — all of them. The red pulsing nodes are AI models training on this right now."* | Asset chips (📊 dashboards / 🤖 models / 📦 datasets) appear. Blast-radius dependency graph renders — red pulsing nodes = AI models. | Trace from the metric node (blue) outward to the red pulsing AI model nodes. |
| **1:46** | *"No error message. No alert. Just wrong answers, quietly shipped downstream."* | Bottom quote: *"A wrong definition silently contaminates every dashboard, model, and dataset downstream — with no error message."* | Click **Next →**. |

---

### BEAT 4 — It recommends a canonical definition (1:50 – 2:22)

| ⏱ | SAY | SCREEN | DO |
|---|-----|--------|----|
| **1:52** | *"Agent four — the Reconciliation Broker. Create one trusted definition."* | **Step 4 · RECONCILIATION BROKER · AGENT 4 OF 5.** Title: **"Create one trusted definition."** Subtitle: **"Rosetta proposes a canonical term — humans approve it."** | — |
| **1:57** | *"On the left: the three conflicting definitions. On the right: what Rosetta proposes."* | **Before panel** — "Conflicting Definitions": three team definitions listed. Arrow ↓. **After panel** — "Proposed Canonical Definition" with **canonical** tag. | Point left (conflicting), then arrow, then right (canonical). |
| **2:06** | *"One definition. Merges clinical, finance, and research intent. Zero ambiguity."* | Canonical definition text visible in the after panel. | — |
| **2:10** | *"And here's the key: Rosetta will not touch DataHub without a human sign-off. Three operations — and every one waits for this button."* | **"WRITES TO DATAHUB ON APPROVAL"** callout: 📝 Canonical GlossaryTerm created / 🔗 N downstream assets linked / 🗑 Conflicting definitions deprecated. Warning: **"⚠ Human approval required — Rosetta will not write without it."** Button: **✓ Approve & Write to DataHub.** | Point to each of the three operations. |
| **2:20** | *"Approved."* | Approve button highlighted. | Click **✓ Approve & Write to DataHub**. |

---

### BEAT 5 — It writes the fix back to DataHub (2:22 – 2:42)

| ⏱ | SAY | SCREEN | DO |
|---|-----|--------|----|
| **2:24** | *"Agent five — the Writer. Make the graph smarter."* | **Step 5 · WRITER · AGENT 5 OF 5.** Title: **"Make the graph smarter."** Demo mode shows: **DEMO MODE — Connect DataHub above and approve to write this for real.** | — |
| **2:28** | *"Canonical glossary term ready to create. Twelve downstream assets identified for linking. Five conflicting definitions flagged for retirement."* | Three checklist items with ✓: **Canonical glossary term ready to create** / **Downstream assets identified** / **Conflicting definitions flagged for retirement.** | Point to each checklist row. |
| **2:36** | *"And the fourth: future AI agents inherit the truth. One agreed definition — across every team, every model, every dashboard."* | Fourth item: 🤖 **Future AI agents inherit the truth.** | Point to the robot icon row. |

---

### BEAT 6 — The graph is consistent (2:38 – 3:00)

| ⏱ | SAY | SCREEN | DO |
|---|-----|--------|----|
| **2:40** | *"Every scan produces a full audit trail — JSON, CSV, Markdown, and a self-contained HTML report, ready for compliance review."* | Export chips: **JSON / CSV / Markdown / HTML.** | Click one chip to show the download. |
| **2:48** | *"The closing line Rosetta puts on every report:"* | Closing quote appears: **"The numbers were never wrong. They were never comparable."** — *Meaning restored.* | Let the screen breathe. |
| **2:54** | *"That's Rosetta. Five agents. One pipeline. The metadata graph is now consistent."* | — | Click **⌂ Home** to return to the landing page. |
| **2:58** | *"It just meant different things to different teams."* | Hero headline: **"Your teams define the same metric differently."** | Fade or cut on the headline. |

---

## 📋 Numbers cheat sheet · for Q&A

| What judges will ask | Answer |
|----------------------|--------|
| What dataset is this? | DataHub hackathon healthcare sample — 55,500 synthetic patient records |
| How many conflicts? | **5** (1 critical · 2 high · 2 medium) |
| Worst conflict | **billing_amount** — clinical vs finance |
| Evidence for worst | **1,215 negative billing rows** · **$28,478,287 misreported revenue** in mart_billing |
| Blast radius of worst | **12 assets** (dashboards, models, datasets, tables) |
| Confidence on worst | **88%** — structural graph analysis, no LLM |
| Logic similarity | **12%** — the two definitions barely overlap |
| Patient age issue | **832 impossible ages** (−88 to 285) reaching mart_demographics |
| Date swap issue | **277 negative length_of_stay values** in mart_billing from admission/discharge swap |
| NULL names | **555 NULL patient names** — research cohort tracking broken |
| Total assets at risk | **585** (scaled from real row counts) |
| Does it need a live DataHub? | No — runs fully offline. Click **🏥 Healthcare Scan** in the top nav. For live: click **Connect DataHub** → use the free Acryl demo at demo.datahubproject.io (~60 sec to get a token) |
| Can it run on retail data? | Yes — click **🛍️ Retail Scan** for the Fiction Retail e-commerce dataset (150,000 orders, discount unit-convention conflict) |
| Can it write back to real DataHub? | Yes — Connect DataHub, run a scan, approve in Step 4, and Rosetta writes the canonical GlossaryTerm, links assets, and deprecates conflicting terms live |
| How is severity set? | Evidence-driven: row count and dollar impact, not just graph size |
| Is anything AI-generated? | No LLM in the pipeline — deterministic graph traversal + structural analysis |
| What does Step 5 show in demo mode? | A simulated checklist of what *would* be written. Connect a live DataHub to see the real write confirmed. |

---

## 🎬 Recording checklist

- [ ] Browser at **1920 × 1080**, zoom **110%**
- [ ] Click **🏥 Healthcare Scan** in the top nav (not **▶ Run Demo** — the healthcare scan tells the real story)
- [ ] Run the scan once before recording so the DB is warm (faster transitions)
- [ ] Record audio separately, sync in post (kills keyboard + click noise)
- [ ] Move mouse **slowly and deliberately** — fast mouse looks nervous
- [ ] Zoom browser to **150%** during Step 3 graph reveal for visual impact on the blast-radius graph
- [ ] On Step 4, pause **2 full seconds** on the "WRITES TO DATAHUB ON APPROVAL" callout before clicking Approve
- [ ] Finish on the landing page hero (click **⌂ Home**) — clean final frame for the thumbnail
