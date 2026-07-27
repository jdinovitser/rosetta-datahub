# Rosetta — 3-Minute Demo Script
### DataHub Agent Hackathon · Enterprise AI Data Intelligence Track

---

> **Speaker notes format:**  
> `[ACTION]` = what's on screen / what you click  
> *Italics* = suggested spoken words  
> ⏱ timestamps are cumulative

---

## 0:00 – 0:22 · THE HOOK

`[SCREEN: Black. Then slowly fade up the Rosetta landing page.]`

*"Your CFO just told investors you have 2.1 million active users.*

*Your CMO told the board you have 3.8 million.*

*Both of them pulled from DataHub. Both of them are right — by their own definition.*

*And neither of them knows the other exists."*

`[PAUSE 1 second]`

*"This is the silent data crisis hiding inside every enterprise data platform. And this is Rosetta."*

---

## 0:22 – 0:45 · WHAT ROSETTA IS

`[SCREEN: Landing page — three problem cards visible]`

*"Rosetta is a five-agent semantic consistency pipeline built natively on DataHub.*

*It reads every metric definition in your graph, finds where two teams silently mean different things by the same word, quantifies exactly how far that wrong definition travels downstream — and then writes the truth back.*

*No manual audits. No spreadsheets. No governance tickets that go nowhere.*

*Let's run it."*

---

## 0:45 – 1:05 · AGENT 1 — HARVESTER

`[CLICK: "Run Rosetta Demo" — walkthrough advances to Step 1]`

*"Agent one — the Harvester — reads your entire DataHub graph in seconds.*

*In our demo environment: twelve distinct metric definitions across six business domains — Finance, Marketing, Sales, Product, Data Science, and Customer Success.*

*Sixty-three downstream assets. Dashboards, datasets, Snowflake tables, ML models.*

*Now watch what the Conflict Detector finds."*

`[CLICK: Next →]`

---

## 1:05 – 1:35 · AGENT 2 — CONFLICT DETECTOR

`[SCREEN: Step 2 — Active User conflict card fills the screen]`

*"Agent two surfaces the first critical conflict immediately.*

*'Monthly Active Users.' Finance and Marketing. Same name. Completely different computation.*

*Finance counts users who completed a paid transaction in the last 30 days.*

*Marketing counts any session or app open — bots excluded — in the last 30 days.*

*These two numbers will never agree. They are measuring fundamentally different things.*

*Rosetta's confidence that this is a real conflict: ninety-three percent.*

*And it found five more like this — ARR defined differently by Finance and Sales. Conversion Rate split between Marketing and Product. Customer LTV calculated in completely opposite ways by Finance and Data Science — zero percent logic overlap.*

*Six conflicts. One data platform. Zero warnings — until now."*

`[CLICK: Next →]`

---

## 1:35 – 2:00 · AGENT 3 — BLAST-RADIUS ANALYZER

`[SCREEN: Step 3 — three giant numbers animate up: 22 / $990 / 11hrs, graph renders]`

*"Agent three maps the blast radius.*

*That single 'Active User' conflict — twenty-two downstream assets contaminated. Look at the dependency graph: eleven executive dashboards. Four production ML models. The investor reporting dashboard. The board pack. The churn predictor.*

*Every one of them is computing on a lie — silently, with no error.*

*The AI readiness score for this DataHub instance: twenty-six out of a hundred. Because when your ML models train on semantically inconsistent features, they don't crash — they just learn the wrong thing.*

*Across all six conflicts: sixty-three assets at risk. Thirty-one analyst-hours to reconcile manually. Two thousand, eight hundred and thirty-five dollars in avoidable cost — just for this scan."*

`[CLICK: Next →]`

---

## 2:00 – 2:30 · AGENTS 4 & 5 — RECONCILE + WRITE

`[SCREEN: Step 4 — Before/After reconciliation panel]`

*"Agent four — the Reconciliation Broker — proposes a canonical definition.*

*It merges both team's intent: 'Any user with at least one meaningful interaction — paid transaction or verified session — in the trailing 30 days, bots excluded.'*

*One definition. Both teams' logic preserved. Human approval required before anything changes.*

`[CLICK: "Approve" button]`

*Approved.*

`[CLICK: Next →]`

`[SCREEN: Step 5 — write checklist completes, exports appear]`

*"Agent five — the Writer — pushes the canonical GlossaryTerm directly back to DataHub.*

*The stale definition is flagged. Downstream asset owners are notified. The conflict is resolved.*

*And because this is DataHub — the fix propagates to every asset that inherits from it."*

---

## 2:30 – 2:50 · THE EXPORTS

`[CLICK: Developer View — show the export bar: JSON · CSV · Markdown · HTML]`

*"Every scan produces a full audit trail — structured JSON for downstream pipelines, CSV for your data governance team, a rendered Markdown report for your GitHub repo, and a self-contained HTML report for stakeholders who will never touch a terminal.*

*Sample outputs for all four formats are in the repository's* `examples/` *folder — judges can evaluate quality without running a line of code."*

---

## 2:50 – 3:00 · CLOSE

`[SCREEN: Back to landing — ROSETTA hero title]`

*"Rosetta doesn't replace your data governance process.*

*It gives it teeth.*

*The numbers were never wrong.*

*They were never comparable.*

*Rosetta makes them both."*

`[FADE TO BLACK]`

---

## 📋 Key Numbers Cheat Sheet
*(for ad-lib or Q&A)*

| Stat | Value |
|------|-------|
| Conflicts found | **6** (1 critical, 2 high, 3 medium) |
| Downstream assets at risk | **63** |
| Active User blast radius | **22 assets** (11 dashboards, 4 ML models) |
| Confidence on top conflict | **93.3%** |
| AI Readiness score | **26 / 100** |
| Governance Maturity score | **34 / 100** |
| Est. cost avoided (full scan) | **$2,835** |
| Analyst-hours avoided | **31.5 hrs** |
| Active User: Finance defines it as | Paid transaction in last 30 days |
| Active User: Marketing defines it as | Any session or app open in last 30 days |
| Customer LTV logic overlap | **0%** (Finance vs Data Science) |
| ARR confidence | **95.2%** |

---

## 🎬 Recommended Screen Recording Flow

```
1. Open app → landing page visible (progress dots dim, hero title)
2. Click "Run Rosetta Demo"
3. Step 1 loads → numbers animate (12 defs / 6 domains / 63 assets)
4. Click Next → Step 2: conflict spotlight, let it breathe 10 seconds
5. Click Next → Step 3: numbers animate, graph renders — ZOOM IN on graph
6. Click Next → Step 4: show before/after, click Approve button
7. Click Next → Step 5: checklist ticks, closing quote
8. Click "Developer View" → pan across dashboard scores, show export bar
9. Click JSON export → show the file download
10. Return to landing for closing shot
```

**Recording tips:**
- Use 1920×1080, 60fps if possible
- Slow your mouse — deliberate movements look more confident on screen
- Record audio separately and sync in post (eliminates keyboard/click noise)
- Zoom to 110% in browser for better readability
- The Judge Demo (90-second auto-play) is great for B-roll

---

## 🏆 One-Line Pitch (for the submission form)

> *Rosetta is a five-agent DataHub pipeline that finds where teams silently define the same metric differently, maps the downstream blast radius across dashboards and ML models, brokers a canonical definition, and writes it back — turning invisible semantic debt into a solvable governance problem.*
