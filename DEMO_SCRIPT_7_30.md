# Rosetta — Contest Demo Script · 7/30
### DataHub Agent Hackathon · Enterprise AI Data Intelligence Track

---

## THE STORY

A hospital system. Three teams. One metric. Three incompatible definitions.
**$28,478,287** in misreported revenue sitting in the billing mart.
**832 impossible patient ages** — some as high as 285 — feeding a live AI model.
**277 negative inpatient days** because admission and discharge were defined backwards.

No errors. No alerts. Every pipeline green.

**Rosetta finds all five conflicts in seconds. Traces every poisoned downstream asset.
Proposes the fix. Waits for a human to approve. Then — in Connected Mode — writes the truth back to DataHub.**

---

## BEFORE YOU OPEN THE APP

**Presence.** Slow down to 70% of your normal speaking pace. Every number is a punch — give it room to land.

**Mouse discipline.** Park the cursor when you're talking. Move it only when you're pointing. Fast mouse reads as nervous.

**The approve button is your climax.** Build tension to it. Pause two full seconds before you click.

**The closing quote is on screen at Step 5.** Read it aloud. Then stop talking. Let silence hold.

---

## THE SCRIPT

---

### 0:00 — THE HOOK

*The problem should land before anyone knows what Rosetta is.*

| ⏱ | SAY | SCREEN | DO |
|---|-----|--------|----|
| **0:00** | *"Twenty-eight million, four hundred and seventy-eight thousand dollars."* | Landing page. Dark hero. Mascot. Bold headline: **"Your teams define the same metric differently."** | Open app. Stand still. Say nothing else for two seconds. |
| **0:06** | *"That's not a budget. That's corrupted revenue sitting in this hospital's billing mart right now — because the clinical team and the finance team define 'billing amount' differently. No pipeline failed. No alert fired. The data just quietly disagrees with itself."* | Same hero. | Pause. Let it settle. |
| **0:17** | *"Meanwhile, the research team is training a patient-risk model on ages that go up to two hundred and eighty-five. Same source column. No range constraint on their side. Eight hundred and thirty-two impossible ages — and the model is learning from every one of them."* | Scroll down slightly — 🏥 Healthcare dataset card comes into view. | Point to the card. |
| **0:26** | *"Five conflicts. Fifty-five thousand records in the hackathon sample dataset. No errors anywhere in the pipeline."* | Healthcare card. | Pause. |
| **0:30** | *"This is Rosetta."* | Gesture to the mascot and the headline. | — |
| **0:32** | *"Five agents. One pipeline. It reads the DataHub graph, finds every place teams silently disagree on meaning, maps exactly how far the damage has already spread — and writes the canonical fix straight back."* | — | Click **🏥 Healthcare Scan** in the top nav. Progress bar fires: **DISCOVER · DETECT · IMPACT · RECONCILE · WRITE** |

---

### 0:38 — AGENT 1 · HARVESTER
*"Before you can fix a conflict, you have to understand what everyone agreed to."*

| ⏱ | SAY | SCREEN | DO |
|---|-----|--------|----|
| **0:38** | *"Agent one — the Harvester."* | **HARVESTER · AGENT 1 OF 5** chip. Title: **"Discover the meaning."** Subtitle: "Rosetta reads every metric definition in your DataHub graph." | Watch the terminal tick. |
| **0:41** | *"It reads everything — glossary terms, dataset schemas, lineage edges, ownership, SQL logic. Every way every team has ever defined a metric."* | Terminal lines tick done: ✓ DataHub glossary terms loaded · ✓ Metric owners identified · ✓ Cross-domain lineage mapped · ✓ SQL logic extracted for comparison | Point to each line as it ticks. |
| **0:48** | *"Ten metric definitions. Three clinical and business teams. Five hundred eighty-five downstream assets mapped across the lineage graph. Before a single conflict has been found."* | Three stats count up: **Metric Definitions · Business Domains · Downstream Assets** | Let the numbers land. |
| **0:54** | *"Rosetta understands how your organisation defines its data — before anyone knows the definitions disagree."* | Quote appears: *"Rosetta starts by understanding how your organisation defines its data — before anyone knows the definitions disagree."* | Click **Next →** |

---

### 0:57 — AGENT 2 · CONFLICT DETECTOR
*"Same word. Completely different meaning."*

| ⏱ | SAY | SCREEN | DO |
|---|-----|--------|----|
| **0:57** | *"Agent two — the Conflict Detector."* | **CONFLICT DETECTOR · AGENT 2 OF 5** chip. Title: **"Semantic collision detected."** Subtitle: **"Same word. Completely different meaning."** | — |
| **1:01** | *"It found five conflicts. Here is the worst one."* | **CRITICAL · silent contradiction** badge. Metric spotlight card animates in. | — |
| **1:05** | *"'Billing Amount.'"* | Metric name **billing_amount** in the card header. | Point to the metric name. Pause. |
| **1:07** | *"Clinical: 'Total charge for services rendered — recorded verbatim from the source system. No filtering.'"* | Left definition panel — clinical_team. | Point to the left panel. |
| **1:13** | *"Finance: 'Revenue recognized for services rendered. Must always be positive — negative values indicate a data error.'"* | Right definition panel — finance_team. **≠** symbol between them. | Point to the ≠, then the right panel. |
| **1:19** | *"Both teams are correct by their own definition. And the billing mart is wrong by both of them."* | Both panels side by side. | Pause. |
| **1:24** | *"Confidence: eighty-eight percent. Logic similarity: twenty-three percent. Twelve downstream assets already carrying this error."* | Three stat badges: **88% Conflict Confidence · 23% Logic Similarity · 12 Assets at Risk** | Point to each badge. |
| **1:31** | *"No LLM. Pure structural graph analysis."* | Tagline: **"Same words. Different meaning."** | Click **Next →** |

---

### 1:34 — AGENT 3 · BLAST-RADIUS ANALYZER
*"The damage is never local."*

| ⏱ | SAY | SCREEN | DO |
|---|-----|--------|----|
| **1:34** | *"Agent three — the Blast-Radius Analyzer."* | **BLAST-RADIUS ANALYZER · AGENT 3 OF 5** chip. Title: **"Measure the impact."** Subtitle: **"How far does a wrong billing_amount travel downstream?"** | Watch the three numbers animate. |
| **1:40** | *"Twelve downstream assets — contaminated."* | **12** — Downstream Assets Contaminated — counts up. | Point. |
| **1:43** | *"Twenty-eight million dollars — estimated cost if this goes unresolved."* | **$28M+** — Estimated Business Cost if Unresolved — counts up. | Point. |
| **1:47** | *"Eighty-plus analyst hours — to untangle it by hand."* | **80+** — Analyst Hours to Fix Manually — counts up. | Point. |
| **1:51** | *"Now look at the graph."* | Blast-radius dependency graph renders. Legend: 🔵 metric · 🩵 dataset · 🟠 dashboard · 🔴 AI model (pulsing) | — |
| **1:53** | *"The red pulsing nodes — those are AI models. Training. Right now. On this definition."* | Red pulsing nodes in the graph. | Trace slowly from the billing_amount metric node outward to the red AI model nodes. |
| **2:00** | *"No error message. No alert. Just wrong answers — quietly shipped to every downstream consumer."* | Quote: *"A wrong definition silently contaminates every dashboard, model, and dataset downstream — with no error message."* | Pause. Click **Next →** |

---

### 2:04 — AGENT 4 · RECONCILIATION BROKER
*"One definition. Human approved. Not a byte written without it."*

| ⏱ | SAY | SCREEN | DO |
|---|-----|--------|----|
| **2:04** | *"Agent four — the Reconciliation Broker."* | **RECONCILIATION BROKER · AGENT 4 OF 5** chip. Title: **"Create one trusted definition."** Subtitle: **"Rosetta proposes a canonical term — humans approve it."** | — |
| **2:08** | *"On the left — every conflicting definition. Everything that's been true for each team, in isolation."* | **Before panel** — "Conflicting Definitions" — clinical and finance definitions with red dots. | Point left. |
| **2:13** | *"On the right — what Rosetta proposes."* | Arrow ↓. **After panel** — "Proposed Canonical Definition" — green canonical tag. | Point right. |
| **2:16** | *"'Net validated charge for a patient encounter — positive amounts only, post-adjudication, USD.' One definition. Both teams. Zero ambiguity."* | Canonical definition text in the after panel. | Read it slowly. |
| **2:22** | *"And here is the principle that makes Rosetta safe to deploy in production."* | **"WRITES TO DATAHUB ON APPROVAL"** callout appears below. | Point to the callout header. |
| **2:26** | *"It will not write a single byte to DataHub without a human sign-off. Three operations are listed — and every one of them is waiting for this button."* | Three ops listed: 📝 Canonical GlossaryTerm created · 🔗 12 downstream assets linked · 🗑 Conflicting definitions deprecated. Warning: **"⚠ Human approval required — Rosetta will not write without it."** Button: **✓ Approve & Write to DataHub** | Trace each operation slowly. |
| **2:35** | *"This is the moment."* | Button. | Make eye contact with the camera or the judges. Two full seconds of silence. Then click **✓ Approve & Write to DataHub**. |

---

### 2:38 — AGENT 5 · WRITER
*"The graph is now consistent."*

| ⏱ | SAY | SCREEN | DO |
|---|-----|--------|----|
| **2:38** | *"Agent five — the Writer."* | **WRITER · AGENT 5 OF 5** chip. Title: **"Make the graph smarter."** | — |
| **2:39** | *"This is Demo Mode. The plan is validated — but not executed. That badge tells you exactly what Rosetta would do if you connected a live DataHub and clicked Approve."* | **VALIDATED · NOT EXECUTED** status badge visible below the write plan. | Point directly to the badge. Pause. |
| **2:41** | *"Canonical glossary term — ready."* | ✓ **Canonical glossary term ready to create** | Point. |
| **2:43** | *"Twelve downstream assets — identified for linking."* | ✓ **Downstream assets identified** | Point. |
| **2:45** | *"Five conflicting definitions — flagged for retirement."* | ✓ **Conflicting definitions flagged for retirement** | Point. |
| **2:47** | *"And every AI model downstream — will inherit the correct definition going forward."* | 🤖 **Future AI agents inherit the truth** | Point to the robot row. |
| **2:51** | *"Full audit trail — one click. JSON, CSV, Markdown, HTML."* | Export chips: **JSON · CSV · Markdown · HTML** | Click one to trigger the download. |
| **2:55** | *"And on every report Rosetta generates — this line."* | Closing quote fades in: **"The numbers were never wrong."** | Pause. |
| **2:58** | *(read from the screen, slowly)* **"The numbers were never wrong. They were never comparable."** | **"They were never comparable."** *— Meaning restored.* | Read it. Then say nothing. Hold for two seconds. |
| **3:02** | — | Click **⌂ Home**. Hero headline: **"Your teams define the same metric differently."** | Fade or cut on the headline. |

---

## 📋 Q&A Cheat Sheet — have these cold

| What judges will ask | Your answer |
|----------------------|-------------|
| What dataset is this? | Official Build with DataHub hackathon sample data — 55,500 synthetic patient records. No real patient or personal information is used. |
| How many conflicts found? | **5** — 1 critical, 2 high, 2 medium |
| What is the critical conflict? | **billing_amount** — clinical records all charges including reversals; finance requires positive amounts only |
| How many bad rows? | **1,215 negative billing rows** · **$28,478,287** in misreported revenue in mart_billing |
| Blast radius of the critical conflict? | **12 assets** — datasets, dashboards, AI models. **585 total assets at risk** across all five conflicts |
| Conflict confidence? | **88.4%** — structural graph analysis, zero LLM |
| Logic similarity? | **23.3%** — the two definitions share almost nothing structurally |
| What about patient ages? | **832 impossible ages** (−88 to 285) — clinical has no range constraint, research requires 0–120. A model is training on this |
| Length of stay? | **277 negative inpatient days** in mart_billing — finance defined LOS as discharge minus admission in whole days without direction; clinical computed it the other way |
| NULL patient names? | **555 NULL names** — clinical allows NULL for anonymous patients; research requires non-NULL for cohort tracking. Research cohort is silently broken |
| Does it need a live DataHub? | **No.** Runs locally against DataHub sample data provided for the hackathon. Click **🏥 Healthcare Scan** anytime. For live: **Connect DataHub** → use Acryl demo at demo.datahubproject.io (token in ~60 sec) |
| How is severity ranked? | Evidence-driven — row count × dollar impact × blast radius. Not manually assigned |
| Any LLM in the pipeline? | **None.** Fully deterministic structural graph traversal. Works offline. Always reproducible. No hallucination risk |
| Can it write back for real? | Yes — connect a live DataHub, approve in Step 4, and Rosetta upserts the canonical GlossaryTerm, links downstream assets, and deprecates conflicting terms. Live |
| What does demo-mode Step 5 show? | The exact write plan — what *would* be executed. Connect DataHub to see it run for real |
| Why human-in-the-loop? | Production safety. Rosetta proposes — humans decide. Nothing touches the catalog without explicit approval |
| What's next? | Salesforce Data Cloud connector, AI Model Launch Readiness scenario, scheduled conflict monitoring with drift alerts |

---

## 🎬 Recording checklist

- [ ] Browser at **1920 × 1080**, zoom **110%**
- [ ] Use **🏥 Healthcare Scan** — not **▶ Run Demo**. The healthcare scan has every real number
- [ ] **Warm run first** — click through once before recording so the DB is warm and all transitions are instant
- [ ] **Record audio separately**, sync in post — eliminates all keyboard and click noise
- [ ] **Mouse discipline** — park the cursor when talking. Move only when pointing at a specific element
- [ ] **Step 3** — zoom browser to **150%** right before clicking Next →. The pulsing red AI model nodes hit hardest at full size
- [ ] **Step 4 approve button** — pause at least **2 full seconds** before clicking. Silence here is your most powerful tool
- [ ] **Step 5 closing quote** — read both lines aloud from the screen, then hold silence for 2 seconds before clicking Home
- [ ] **Final frame** — cut on the hero headline. Clean, bookends the opening

---

*"The numbers were never wrong. They were never comparable."*
*— Meaning restored.*
