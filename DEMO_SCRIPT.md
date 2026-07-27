# Rosetta — 3-Minute Demo Script
### DataHub Agent Hackathon · Enterprise AI Data Intelligence Track

---

## How to read this

| Column | Meaning |
|--------|---------|
| **SAY** | Speak these words exactly (or close to it) |
| **DO** | What to click / show on screen at that moment |

Pacing: ~140 words/min. Total script ≈ 410 spoken words = **~3:00 flat.**

---

## THE SCRIPT

| ⏱ | SAY | DO |
|---|-----|----|
| **0:00** | *"Your CFO just told investors you have 2.1 million active users."* | Open app. Landing page visible — Rosetta hero title, three problem cards. |
| **0:05** | *"Your CMO told the board you have 3.8 million."* | Hover slowly over the "AI Models Fail Silently" card. |
| **0:10** | *"Both of them pulled from DataHub. Both of them are right — by their own definition."* | Let the screen breathe. Slow mouse. |
| **0:17** | *"And neither of them knows the other exists."* | Pause 1 second on the landing hero. |
| **0:20** | *"This is the silent data crisis hiding inside every enterprise data platform. This is Rosetta."* | Gesture toward the screen. |
| | | |
| **0:26** | *"Rosetta is a five-agent pipeline built natively on DataHub."* | Point to the five progress dots at the top — DISCOVER · DETECT · IMPACT · RECONCILE · WRITE. |
| **0:31** | *"It reads your entire graph, finds where two teams silently disagree on meaning, maps how far that disagreement travels downstream — and writes the truth back."* | Slowly scroll the landing page down to show the problem cards. Scroll back up. |
| **0:42** | *"Let's run it."* | Click **"Run Rosetta Demo"** button. |
| | | |
| **0:44** | *"Agent one — the Harvester — reads the DataHub graph in seconds."* | Step 1 appears. Watch the three numbers animate up. |
| **0:50** | *"Twelve metric definitions. Six business domains. Sixty-three downstream assets — dashboards, datasets, Snowflake tables, ML models."* | Point to each stat as it lands: 12 · 6 · 63. |
| **0:58** | *"Now watch what the Conflict Detector finds."* | Click **Next →**. |
| | | |
| **1:02** | *"Agent two surfaces a critical conflict immediately."* | Step 2 fills the screen — the Active User spotlight card. |
| **1:06** | *"'Monthly Active Users.' Finance versus Marketing. Same name. Completely different computation."* | Point to the Finance definition on the left. Then the Marketing definition on the right. Then the ≠ in the middle. |
| **1:14** | *"Finance counts users who completed a paid transaction in the last 30 days. Marketing counts any session or app open — bots excluded."* | Let the card sit. Don't click yet. |
| **1:22** | *"These two numbers will never agree. Rosetta's confidence this is a real conflict: ninety-three percent."* | Point to the confidence badge at the bottom of the card. |
| **1:28** | *"It found five more: ARR split between Finance and Sales. Conversion Rate split between Marketing and Product. Customer LTV — Finance versus Data Science — zero percent logic overlap. Six conflicts. One data platform. Zero warnings — until now."* | Scroll slightly so the conflict-count badge is visible. |
| **1:40** | *(no words — let the moment land)* | Click **Next →**. |
| | | |
| **1:42** | *"Agent three maps the blast radius."* | Step 3: three giant numbers begin animating up. |
| **1:46** | *"That single 'Active User' conflict — twenty-two downstream assets contaminated."* | Point to the **22** as it animates to its final value. |
| **1:50** | *"Look at the dependency graph."* | Point to the network graph below the numbers as nodes appear. |
| **1:53** | *"Eleven executive dashboards. Four production ML models. The investor reporting dashboard. The board pack. The churn predictor — all computing on a lie. Silently. No error."* | Slowly trace the graph with your cursor from the metric node outward to the red model nodes. |
| **2:02** | *"The AI Readiness score for this DataHub instance: twenty-six out of a hundred. Because when ML models train on semantically inconsistent features, they don't crash — they just learn the wrong thing."* | Nothing to click — let the graph and numbers speak. |
| **2:12** | *"Across all six conflicts: sixty-three assets, thirty-one analyst-hours, two thousand eight hundred dollars — avoidable."* | Point to the cost and hours numbers. Click **Next →**. |
| | | |
| **2:18** | *"Agent four — the Reconciliation Broker — proposes a canonical definition."* | Step 4: before-panel and after-panel visible. |
| **2:23** | *"It merges both teams' intent: 'Any user with at least one meaningful interaction — paid transaction or verified session — in the trailing 30 days, bots excluded.'"* | Point to the after-panel — the green canonical definition text. |
| **2:30** | *"Human approval required before anything changes."* | Point to the Approve button. Pause one beat. |
| **2:33** | *"Approved."* | Click **Approve**. Watch it turn green. Click **Next →**. |
| | | |
| **2:36** | *"Agent five — the Writer — pushes the canonical GlossaryTerm directly back to DataHub."* | Step 5: checklist items tick off one by one. |
| **2:41** | *"Stale definition flagged. Downstream asset owners notified. Conflict resolved."* | Point to each checklist item as it completes. |
| **2:46** | *"Every scan produces a full audit trail — JSON, CSV, Markdown, and a self-contained HTML report. Sample outputs for all four are in the repository's* `examples/` *folder."* | Click **Developer View**. Show the export bar: JSON · CSV · Markdown · HTML. Click one — show the download. |
| | | |
| **2:54** | *"Rosetta doesn't replace your data governance process. It gives it teeth."* | Return to the landing page. Hero title fills the screen. |
| **2:58** | *"The numbers were never wrong."* | Pause. |
| **3:00** | *"They were never comparable."* | Fade or cut. |

---

## 📋 Numbers cheat sheet · for Q&A

| What judges will ask | Answer |
|----------------------|--------|
| How many conflicts? | **6** (1 critical · 2 high · 3 medium) |
| Total assets at risk | **63** |
| Worst conflict | **active_user** — Finance vs Marketing |
| Blast radius of worst | **22 assets** (11 dashboards, 4 ML models) |
| Confidence on worst | **93.3%** |
| Customer LTV logic overlap | **0%** — Finance vs Data Science |
| AI Readiness score | **26 / 100** |
| Governance Maturity | **34 / 100** |
| Est. cost avoided | **$2,835** across all 6 conflicts |
| Analyst-hours avoided | **31.5 hrs** |
| Does it need a live DataHub? | No — runs fully offline on seed data |
| Can it write back to real DataHub? | Yes — swap seed loader for live client |

---

## 🎬 Recording checklist

- [ ] Browser at **1920 × 1080**, zoom **110%**
- [ ] Run the demo once before recording so data is cached (faster transitions)
- [ ] Record audio separately, sync in post (kills keyboard + click noise)
- [ ] Move mouse **slowly and deliberately** — fast mouse looks nervous
- [ ] Zoom browser to **150%** during graph reveal (Step 3) for visual impact
- [ ] Use the **90-Second Judge Demo** button as B-roll (auto-advances with no clicks)
- [ ] Finish on the landing page hero — clean final frame for the thumbnail
