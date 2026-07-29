# Devpost Submission — copy/paste ready

## Project name
**Rosetta — the Semantic Consistency Agent for DataHub**

## Elevator pitch (one line)
A linter for *meaning* across your DataHub graph: it finds where two teams silently mean different things by the same metric, quantifies the blast radius, brokers a canonical definition, and writes it back.

## Inspiration
Talk-to-data agents fail silently when the same metric name has two definitions. Finance's "active user" is not marketing's "active user," and no dashboard warns you. A DataHub hackathon judge from Pinterest publicly called conflicting metric definitions across teams the unsolved problem behind trustworthy data agents. Rosetta attacks exactly that.

## What it does
Rosetta runs a five-agent pipeline over DataHub metadata:
1. **Harvester** reads glossary terms, column descriptions, ownership and lineage.
2. **Conflict Detector** finds two failure modes: *silent contradictions* (same name, different computation) and *hidden synonyms* (different names, same computation) by comparing intent, not just text.
3. **Blast-Radius Analyzer** walks lineage to count the downstream dashboards, models and tables at risk, and scores severity.
4. **Reconciliation Broker** drafts one canonical definition and routes it to the real owners (pulled from DataHub ownership metadata) for approval.
5. **Writer** upserts the agreed canonical GlossaryTerm back into DataHub, links it to every affected asset, and deprecates the losing definitions — a loop that makes the graph richer every run.

## How we built it
Python. A dependency-free, deterministic detection core (tokenized Jaccard similarity over metric names + SQL/definition text, with a pluggable embedding hook) so the whole thing is testable and reproducible offline. Read/write to DataHub via the `acryl-datahub` SDK (`entities.upsert`, `add_term`, `set_deprecation`), with an optional MCP Server + Agent Context Kit path for the harvester. A Flask web app serves the themed, hosted demo and JSON/CSV/Markdown/HTML export endpoints. 32 passing unit tests.

## What's in the box
- Hosted, zero-config demo (click "Run the five-agent demo").
- CLI: `--demo`, `--report`, `--apply`, `--export {json,csv,md,html,all}`.
- Reusable DataHub Skill `detect-semantic-conflicts` (OSS contribution).
- `examples/` with sample conflict report, reconciled term, and exported artifacts in every format.

## Technologies
Python, Flask, acryl-datahub SDK, DataHub MCP Server / Agent Context Kit, DataHub GlossaryTerm & Lineage APIs.

## What's next
Real embedding-based intent matching, PR/Slack approval gating, scheduled scans that track semantic drift over time.

## Try it
- Live demo: **<PASTE YOUR DEPLOYED URL>**
- Repo: **<PASTE YOUR REPO URL>**
- Video: **<PASTE YOUR YOUTUBE/VIMEO URL>**
