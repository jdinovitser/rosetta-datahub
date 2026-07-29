# Rosetta — Full Setup Guide

Rosetta runs in two modes:

| Mode | Needs | What it does |
|---|---|---|
| **Demo mode** (default) | Nothing but Python | Runs the whole 5-agent pipeline on bundled seed data. This is what the hosted demo URL serves. |
| **Live mode** | A DataHub instance + token | Reads your real graph and writes canonical terms back. |

You can win the hackathon demo with **Demo mode only** — no external accounts required. Live mode is for judges who want to point Rosetta at real metadata.

---
## 1. Run locally (Demo mode, zero config)
```bash
git clone <your-repo-url> && cd rosetta
pip install -r requirements-demo.txt
python webapp/app.py            # open http://localhost:5000
# or the terminal walkthrough:
python -m rosetta.orchestrator --demo
```

## 2. Deploy the hosted demo (pick one)
- **Replit**: import the repo. The included `.replit` runs `python webapp/app.py`. Click **Run**, then **Deploy** to get a public URL.
- **Render**: "New > Blueprint", point at the repo; `render.yaml` is preconfigured.
- **Docker**: `docker build -t rosetta . && docker run -p 5000:5000 rosetta`
- **Any host**: `gunicorn --chdir webapp app:app --bind 0.0.0.0:$PORT`

---
## 3. Live mode — connect a real DataHub

### 3a. Get a DataHub instance
Fastest options:
- **DataHub Cloud (Acryl) trial** — sign up at https://datahub.com, then Settings > Access Tokens.
- **Self-host with the CLI quickstart:**
  ```bash
  python -m pip install "acryl-datahub[datahub-rest]"
  datahub docker quickstart        # boots DataHub at http://localhost:9002 (GMS on :8080)
  ```
  Then create a Personal Access Token in the UI: **Settings > Access Tokens > Generate**.

### 3b. Point Rosetta at it
```bash
export DATAHUB_GMS_URL="http://localhost:8080"      # or your Cloud GMS URL
export DATAHUB_GMS_TOKEN="<your personal access token>"

python -m rosetta.orchestrator --report            # read-only scan of the live graph
python -m rosetta.orchestrator --apply             # write canonical terms back
```
When these env vars are set, the web app's **Read-only scan** button and `/api/scan` talk to your live instance automatically (the top-right badge switches to **LIVE DATAHUB**).

### 3c. Load the demo metadata into your instance (optional)
So you have conflicting metrics to detect on a fresh instance, ingest the sample glossary terms / datasets from `demo_data/seed_definitions.json` using the DataHub Python SDK or a recipe. See `docs/DATAHUB_INGEST.md`.

---
## 4. MCP Server + Agent Context Kit (optional, for the live agent loop)

Rosetta's Harvester can pull context through DataHub's **MCP Server** instead of direct SDK calls.

1. Install the context kit:
   ```bash
   pip install datahub-agent-context
   ```
2. Configure the MCP server (from DataHub docs) with your GMS URL + token. A typical MCP client config entry:
   ```json
   {
     "mcpServers": {
       "datahub": {
         "command": "datahub-mcp",
         "env": {
           "DATAHUB_GMS_URL": "http://localhost:8080",
           "DATAHUB_GMS_TOKEN": "<token>"
         }
       }
     }
   }
   ```
3. Swap `RosettaDataHub.harvest_metric_definitions()` to call the MCP tools (search + get glossary terms + lineage). The method is isolated precisely so this is a one-function change; the rest of the pipeline is unchanged.

---
## 5. Run the tests
```bash
pip install pytest
pytest -q          # 32 passed
```
