# Running Rosetta against a live DataHub

Rosetta works in two modes, automatically:

| Mode | When | What happens |
|------|------|--------------|
| **DEMO** | no `DATAHUB_GMS_URL`, or it is unreachable | Reads the bundled, reproducible graph in `demo_data/`. Writes are dry-run (logged, not sent). This is what the hosted demo runs. |
| **LIVE** | `DATAHUB_GMS_URL` points at a reachable DataHub | Reads glossary terms + lineage from the real graph over the official SDK, and writes canonical terms **back** into DataHub. |

The exact same agent pipeline runs in both modes. Nothing is faked in LIVE mode;
nothing requires a warehouse in DEMO mode.

---

## 1. Start a DataHub instance

```bash
python3 -m pip install --upgrade acryl-datahub
datahub docker quickstart          # DataHub UI at http://localhost:9002
```

(Needs Docker with ~8GB RAM. If you can't run Docker locally, GitHub Codespaces
works in the browser.)

## 2. Point Rosetta at it

```bash
export DATAHUB_GMS_URL="http://localhost:8080"
export DATAHUB_GMS_TOKEN="<personal access token>"   # only if auth is enabled
```

Confirm the connection:

```bash
python -m rosetta.orchestrator --check-connection
# LIVE  -> connected to DataHub at http://localhost:8080
```

## 3. Seed the sample metadata (one command)

This ingests the six sample metric definitions as glossary terms, the datasets
they annotate, and the lineage edges between them, so Rosetta's blast-radius
walk has real downstream assets to traverse:

```bash
python scripts/ingest_seed_to_datahub.py
```

## 4. Read the real graph

```bash
python -m rosetta.orchestrator --report --live
```

Rosetta detects the same `active_user`, `revenue`, and `churn ~ attrition`
conflicts, but now the definitions, lineage, and blast radius come from your
live DataHub instance.

## 5. Write canonical definitions back (the loop that compounds)

```bash
python -m rosetta.orchestrator --apply --live
```

For each conflict, Rosetta upserts the reconciled canonical glossary term via
`client.entities.upsert(GlossaryTerm(...))` and links it to the affected
datasets. Open the term in the DataHub UI (`http://localhost:9002`) and you'll
see the canonical definition Rosetta wrote.

---

## What the SDK calls are

All calls use the official `acryl-datahub` Python SDK:

| Purpose | Call |
|---------|------|
| Connect / probe | `DataHubGraph(DatahubClientConfig(server=...))`, `.test_connection()` |
| Read glossary terms | `graph.execute_graphql(query=...)` over `searchAcrossEntities(types: [GLOSSARY_TERM])` |
| Walk downstream lineage | `graph.execute_graphql(...)` over `scrollAcrossLineage(direction: DOWNSTREAM)` |
| Write canonical term | `client.entities.upsert(GlossaryTerm(id, display_name, definition))` |
| Attach term to dataset | `client.entities.get(DatasetUrn)` → `dataset.add_term(GlossaryTermUrn)` → `client.entities.update(dataset)` |

The implementation is in [`rosetta/datahub_client.py`](../rosetta/datahub_client.py).
