<p align="center">
  <img src="webapp/static/img/rosetta-mascot-dark.png" alt="Rosetta" width="120">
</p>

<h3 align="center">A linter for <em>meaning</em> across your DataHub graph.</h3>

<p align="center">
Rosetta finds where two teams silently mean different things by the same metric,
quantifies the blast radius, brokers a canonical definition, and writes it back into DataHub.
</p>

<p align="center"><b>License:</b> Apache-2.0 · <b>Tests:</b> 38 passing · <b>Built for:</b> Build with DataHub — The Agent Hackathon</p>

---

## The problem
Talk-to-data agents fail **silently** when one metric name has two definitions. Finance's `active_user` (paid transactors) is not marketing's `active_user` (sessions). No dashboard warns you. Rosetta catches it.

## From official DataHub sample data to semantic governance

Each step below is labelled by what produced it.

| Step | What happens | Source |
|------|-------------|--------|
| **1 · Official hackathon dataset** | 55,500 synthetic patient records across `raw_patients`, `staging_patients`, `mart_billing`, `mart_demographics`, and 3 normalisation views. Data anomalies present at source. Rosetta never writes to the database. | 🔵 Official dataset |
| **2 · DataHub-compatible metadata graph** | Rosetta assigns DataHub URNs to every table, authors one `MetricDefinition` per (metric, team) pair, builds a lineage edge graph, and assigns `urn:li:glossaryTerm:*` and `urn:li:corpGroup:*` URNs — identical structures to a live DataHub instance. | 🟣 DataHub metadata structures · 🩵 Rosetta's analysis |
| **3 · Rosetta semantic analysis** | `detect_conflicts()` compares each definition pair by name similarity and logic similarity. Identifies *silent contradictions* (same name, incompatible logic) and *hidden synonyms* (different names, equivalent logic). Fully deterministic — no LLM. | 🩵 Rosetta's analysis |
| **4 · Conflict evidence** | Bad-row counts queried directly from the hackathon DB at scan time: 1,215 negative billing rows ($28.4 M misreported), 832 invalid ages, 277 date-swapped LOS records, 555 null names. Rosetta scores severity from these counts. | 🔵 Official dataset · 🩵 Rosetta's analysis |
| **5 · Downstream lineage traversal** | Rosetta walks the lineage graph to find every dataset, dashboard, and ML model carrying contaminated values. Demo mode uses Rosetta's DataHub-style graph of the hackathon pipeline. Live mode calls DataHub's lineage API directly. | 🟣 DataHub metadata structures · 🩵 Rosetta's analysis |
| **6 · Human-approved write plan** | After human approval, Rosetta generates `MetadataChangeProposal` operations: upsert a canonical `GlossaryTerm`, attach it to every affected asset, deprecate conflicting terms. Demo mode shows the plan without submitting it. | 🟢 Rosetta's proposed output |

> **Demo data:** This demonstration uses DataHub sample data supplied through the official Build with DataHub Agent Hackathon resources. No real patient or personal information is used. See [`DATA_PROVENANCE.md`](DATA_PROVENANCE.md) for the full component-level provenance table.

## The five-agent pipeline

<p align="center">
  <img src="webapp/static/img/architecture.png" alt="Architecture diagram" width="700">
</p>

1. **Harvester** — reads glossary terms, column descriptions, ownership, lineage.
2. **Conflict Detector** — finds *silent contradictions* (same name, different logic) and *hidden synonyms* (different names, same logic) by comparing intent, not text.
3. **Blast-Radius Analyzer** — walks lineage to count downstream assets at risk, scores severity.
4. **Reconciliation Broker** — drafts one canonical definition, routes to the real owners.
5. **Writer** — upserts the canonical GlossaryTerm, links every affected asset, deprecates losers. *The loop that compounds.*

## Quick start (zero config)
```bash
pip install -r requirements.txt
python webapp/app.py            # open http://localhost:5000  → click "Run the five-agent demo"
# or the terminal walkthrough:
python -m rosetta.orchestrator --demo
```

## CLI
```bash
python -m rosetta.orchestrator --demo                       # narrated demo (hackathon sample data)
python -m rosetta.orchestrator --report                     # read-only JSON report
python -m rosetta.orchestrator --report --export all        # write json/csv/md/html to exports/
python -m rosetta.orchestrator --apply                      # write canonical terms back (live)
```

## Live DataHub (optional)
```bash
export DATAHUB_GMS_URL="http://localhost:8080"
export DATAHUB_GMS_TOKEN="<personal access token>"
python -m rosetta.orchestrator --report      # scans your real graph
```

## Tests
```bash
pytest -q      # 38 passed
```

## Data provenance
See [`DATA_PROVENANCE.md`](DATA_PROVENANCE.md) for a complete, source-verified table of every component in the healthcare demonstration — what came from the hackathon dataset, what Rosetta constructed, and what remains not established.

---
*Rosetta doesn't just answer questions. It makes sure your whole company is asking the same one.*
