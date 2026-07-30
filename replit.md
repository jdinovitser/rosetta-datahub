# Rosetta — Enterprise AI Data Intelligence

A five-agent semantic consistency engine for DataHub. Finds where teams silently define the same metric differently, quantifies blast radius, brokers a canonical definition, and writes it back.

## How to run

```
python webapp/app.py   # → http://localhost:5000
```

The app runs **fully offline** (zero config, zero API keys) against DataHub sample data provided through the official Build with DataHub Agent Hackathon resources (`demo_data/`). Set `DATAHUB_GMS_URL` and `DATAHUB_GMS_TOKEN` to connect to a live DataHub instance.

## Stack

- **Backend**: Python 3.10, Flask
- **Frontend**: Vanilla JS + SVG (no npm, no bundler)
- **Demo data**: `demo_data/seed_definitions.json`, `demo_data/lineage.json`
- **Port**: 5000

## Project structure

```
rosetta/               Core five-agent pipeline
  orchestrator.py      Pipeline coordinator (Harvester→Writer)
  detector.py          Semantic conflict detection (Jaccard / embeddings)
  broker.py            Reconciliation Broker + Writer
  impact.py            Blast-radius → business cost estimator
  intelligence.py      AI explanations + Executive Dashboard scoring
  demo.py              Offline narrated walkthrough
  exporter.py          JSON / CSV / Markdown / HTML exporters
  datahub_client.py    DataHub SDK client (offline fallback)

webapp/
  app.py               Flask routes (/, /api/demo, /api/scan, /api/dashboard, /api/export/*, /api/graph)
  templates/index.html Single-page UI
  static/css/style.css Dark enterprise theme
  static/js/app.js     Pipeline animation, dashboard, blast-radius graph

demo_data/
  seed_definitions.json  10 metric definitions → 5 conflicts (offline demo)
  lineage.json           Downstream lineage graph

tests/                 32 pytest tests (all passing)
docs/                  SETUP, DEMO_SCRIPT, DEPLOYMENT_GUIDE, etc.
```

## Key API endpoints

| Endpoint | What it does |
|---|---|
| `GET /api/demo` | Full narrated five-agent walkthrough |
| `GET /api/scan` | Read-only scan (live DataHub or hackathon sample data) |
| `GET /api/dashboard` | Executive Data Intelligence Dashboard (scores + actions) |
| `GET /api/export/<fmt>` | Export last report as `json`, `csv`, `md`, or `html` |
| `GET /api/graph` | Blast-radius graph for top conflict |
| `GET /health` | Service status |

## Demo experience flow

**Problem** → **Discovery** → **Intelligence** → **Resolution**

1. Hero explains the enterprise stakes (silent AI failures, exec report disagreements)
2. Click "Run the five-agent demo" — pipeline animates through all 5 agents
3. Executive Dashboard appears with Data Health / Governance Maturity / AI Readiness scores
4. Each conflict card shows AI Explanation (Finding → Evidence → Impact → Recommendation)
5. Reconciliation view shows before/after canonical term proposal
6. Blast-radius graph visualizes downstream contamination

## Tests

```
pytest -q    # 32 passed
```

## User preferences

- Keep offline demo mode working at all times
- Preserve the five-agent pipeline architecture
- Preserve all existing API endpoints and export formats
- Do not replace Flask with another framework
