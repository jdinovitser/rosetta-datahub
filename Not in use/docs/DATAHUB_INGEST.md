# Loading the sample metadata into a live DataHub

To reproduce Rosetta's findings against a real instance, ingest the six sample
metric definitions (`demo_data/seed_definitions.json`) as glossary terms and
attach them to datasets. Minimal example with the SDK:

```python
import os
from datahub.sdk import DataHubClient
from datahub.sdk.glossary_term import GlossaryTerm

client = DataHubClient.from_env()  # reads DATAHUB_GMS_URL / DATAHUB_GMS_TOKEN

import json, pathlib
rows = json.loads(pathlib.Path("demo_data/seed_definitions.json").read_text())
for r in rows:
    term = GlossaryTerm(
        id=r["term_urn"].split(":")[-1],
        display_name=r["display_name"],
        definition=r["definition_text"],
    )
    client.entities.upsert(term)
print("ingested", len(rows), "terms")
```

After ingestion, run `python -m rosetta.orchestrator --report` and Rosetta will
detect the same `active_user`, `revenue` and `churn~attrition` conflicts against
your live graph.
