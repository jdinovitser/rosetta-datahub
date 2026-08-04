# Rosetta — Example Outputs

These files are **pre-generated artifacts** from Rosetta's five-agent pipeline.  
Judges can evaluate output quality without running the code.

---

## Files

| File | Scenario | Format | What it shows |
|------|----------|--------|---------------|
| [`rosetta_report_healthcare.json`](rosetta_report_healthcare.json) | Healthcare · Official hackathon data | JSON | Full structured report: conflicts, AI explanations, blast-radius, remediation plans, provenance |
| [`rosetta_report_healthcare.csv`](rosetta_report_healthcare.csv) | Healthcare · Official hackathon data | CSV | Flat table of every conflict — metric, severity, domains, SQL logic, similarity scores, cost estimate |
| [`rosetta_report_healthcare.md`](rosetta_report_healthcare.md) | Healthcare · Official hackathon data | Markdown | Human-readable narrative report with evidence and recommendations |
| [`rosetta_report_healthcare.html`](rosetta_report_healthcare.html) | Healthcare · Official hackathon data | HTML | Self-contained styled report — open in any browser |
| [`rosetta_report_retail.json`](rosetta_report_retail.json) | Retail · Supplementary scenario | JSON | Same pipeline, different domain — order-status and revenue conflicts |
| [`rosetta_report_retail.csv`](rosetta_report_retail.csv) | Retail · Supplementary scenario | CSV | — |
| [`rosetta_report_retail.md`](rosetta_report_retail.md) | Retail · Supplementary scenario | Markdown | — |
| [`rosetta_report_retail.html`](rosetta_report_retail.html) | Retail · Supplementary scenario | HTML | — |

---

## What each format contains

### JSON
The canonical machine-readable output. Each conflict record includes:
- `metric` — the conflicting business term
- `severity` — `CRITICAL` / `HIGH` / `MEDIUM`
- `kind` — conflict type (e.g. `aggregation_logic`, `inclusion_rule`)
- `definitions` — each domain's definition, owner, and SQL logic
- `blast_radius` — number of downstream assets exposed through DataHub lineage
- `logic_similarity` / `name_similarity` — semantic distance scores
- `confidence` — detection confidence
- `ai_explanation` — finding, evidence, impact, and recommendation
- `remediation_plan` — proposed canonical definition and governed action steps
- `provenance` — scenario label, dataset source, generation timestamp

### CSV
One row per conflict. Designed for spreadsheet review or bulk analysis by judges.

### Markdown
Narrative report suitable for reading in GitHub or any Markdown viewer.

### HTML
Open `rosetta_report_healthcare.html` directly in a browser — no server needed.  
Dark-themed, fully self-contained (no CDN dependencies).

---

## Data provenance

**Healthcare scenario** — uses the official DataHub Agent Hackathon sample dataset  
(55,500 synthetic patient records published on GitHub). No real patient data.

**Retail scenario** — a supplementary fictional dataset created for demonstration.

Both scenarios run in **Demo Mode**: findings are `VALIDATED · NOT EXECUTED`.  
No DataHub credentials are required or used.

---

## Regenerating

```bash
python -c "
from rosetta.healthcare_demo import run_healthcare_demo
from rosetta.fiction_retail_demo import run_fiction_retail_demo
from rosetta import exporter
from pathlib import Path

for name, runner in [('healthcare', run_healthcare_demo), ('retail', run_fiction_retail_demo)]:
    report = runner()['report']
    for fmt in ['json', 'csv', 'md', 'html']:
        Path(f'examples/rosetta_report_{name}.{fmt}').write_text(exporter.export(report, fmt))
"
```
