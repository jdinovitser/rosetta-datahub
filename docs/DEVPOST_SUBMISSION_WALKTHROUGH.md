# Devpost Submission Walkthrough — field-by-field, copy-paste ready

This is your master checklist for filling out the submission form at
https://datahub.devpost.com/. Do the two prerequisites, then paste each field below.

---

## Prerequisites (get these first)
1. **Repo URL** and **Live Demo URL** — see `docs/DEPLOYMENT_GUIDE.md`. Then polish the repo's
   About sidebar (description, website, topics) using `docs/GITHUB_REPO_POLISH.md`.
2. **Video URL** (public YouTube/Vimeo, under 3 min) — see `docs/VIDEO_VOICEOVER_SCRIPT.md`.

Once you have all three, register on the hackathon page, then click **Submit a project**.

---

## Field 1 — Project name
```
Rosetta — the Semantic Consistency Agent for DataHub
```

## Field 2 — Elevator pitch / tagline (~200 char)
```
A linter for meaning across your DataHub graph: it finds where two teams silently mean different things by the same metric, quantifies the blast radius, brokers a canonical definition, and writes it back.
```

## Field 3 — "About the project" (rich text; use these headings)

**Inspiration**
Talk-to-data agents fail silently when the same metric name has two definitions. Finance's "active user" is not marketing's "active user," and no dashboard warns you. Conflicting metric definitions across teams are a top cause of broken trust in data agents, and nothing in the catalog flags them today. Rosetta attacks exactly that.

**What it does**
Rosetta runs a five-agent pipeline over DataHub metadata:
1. Harvester reads glossary terms, column descriptions, ownership and lineage.
2. Conflict Detector finds two failure modes: silent contradictions (same name, different computation) and hidden synonyms (different names, same computation), comparing intent rather than just text, and attaches a confidence score to each.
3. Blast-Radius Analyzer walks lineage transitively to count the downstream dashboards, models and tables at risk, scores severity, and estimates the analyst-hours and dollar cost of leaving the conflict unresolved.
4. Reconciliation Broker drafts one canonical definition, produces a before/after diff, and routes it to the real owners (pulled from DataHub ownership metadata) for approval.
5. Writer upserts the agreed canonical GlossaryTerm back into DataHub, links it to every affected asset, and deprecates the losing definitions, a loop that makes the graph richer every run.

On the included sample dataset it surfaces 3 conflicts across 24 downstream assets, quantifies roughly $1,080 and 12 analyst-hours of avoidable rework, and visualizes the blast radius as an interactive force graph.

**How we built it**
Python. A dependency-free, deterministic detection core (tokenized similarity over metric names and SQL/definition text, with a pluggable embedding hook) so the whole thing is testable and reproducible offline. It reads from and writes to DataHub via the acryl-datahub SDK (entity upsert, add glossary term, set deprecation) built directly against DataHub's glossary-term, lineage and ownership model, with an optional MCP Server + Agent Context Kit path for the harvester. A Flask web app serves the themed, hosted demo, an interactive blast-radius graph, and JSON/CSV/Markdown/HTML export endpoints. 32 passing unit tests.

**A note on the demo (transparency for judges)**
Rosetta is built on the real DataHub Python SDK and DataHub's actual data model (glossary terms, lineage, ownership, URNs). To make the hosted demo instant and reproducible for judges, it runs against a bundled sample metadata set that mirrors DataHub's glossary and lineage format, rather than requiring you to stand up a live DataHub instance. The DataHub read/write facade is real and documented (see `rosetta/datahub_client.py` and `docs/DATAHUB_INGEST.md`); pointing it at a live instance is a matter of setting `DATAHUB_GMS_URL` and a token and swapping the harvest source. Nothing in the demo requires misrepresenting a live connection.

**Challenges we ran into**
Detecting semantic conflicts without a heavyweight ML dependency meant designing a deterministic scoring core that still captures intent, then walking DataHub lineage transitively so blast radius reflects the true downstream footprint rather than just direct neighbors.

**Accomplishments that we're proud of**
A complete read-reason-write loop that contributes canonical definitions back to the graph, quantified real-world impact in dollars and hours, and a zero-config hosted demo anyone can run in one click.

**What we learned**
The hardest data-agent problem isn't reading metadata, it's reconciling conflicting meaning across teams and writing an authoritative answer back so the next agent inherits it.

**What's next for Rosetta**
Real embedding-based intent matching, PR/Slack approval gating for the broker, and scheduled scans that track semantic drift over time.

## Field 4 — "Built With" tags (comma-separated)
```
python, flask, acryl-datahub, datahub-mcp-server, agent-context-kit, glossary-terms, lineage-api, force-graph
```

## Field 5 — Try it out links
- Website / live demo URL: `https://rosetta-datahub.onrender.com` (your Render URL)
- GitHub repo URL: `<PASTE YOUR PUBLIC REPO URL>`

## Field 6 — Video demo link
- YouTube/Vimeo URL (public, under 3 min): `<PASTE YOUR VIDEO URL>`

## Field 7 — Image / thumbnail upload
Upload `assets/rosetta-logo.png` as the gallery thumbnail, and add
`assets/blast_radius_graph.png` and `assets/ui_screenshot.png` as gallery images.

## Field 8 — Which challenge
Select **Agents That Do Real Work** (Rosetta reads DataHub, takes action, and writes results
back so the next person/agent inherits the knowledge). Optionally also tick **Open / Wildcard**.

## Field 9 — Bonus feedback survey
Opt in to the **Most Valuable Feedback Survey Prize** and complete the feedback section
($50 × 10 awards, no downside).

---

## Final pre-submit checklist
- [ ] Repo is Public and About sidebar shows Apache-2.0.
- [ ] Live demo URL works in an incognito window (demo button runs with no login).
- [ ] Video is Public, under 3:00, and shows the project functioning.
- [ ] `examples/` folder present with sample outputs in json/csv/md/html.
- [ ] All three URLs pasted into both `docs/SUBMISSION.md` and the Devpost form.
- [ ] Challenge selected; feedback survey opted in.
- [ ] Click **Submit** before Aug 10, 2026 @ 5:00pm EDT.
