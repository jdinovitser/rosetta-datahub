# Rosetta — Contest Demo Script · 8/3
### DataHub Agent Hackathon · Enterprise AI Data Intelligence Track
Rosetta Contest Demo Script
DataHub Agent Hackathon — Enterprise AI Data Intelligence Track

Target Length: ~3 minutes

Time	What I Say	What I Show / Do
0:00	"This is Rosetta running against the healthcare dataset provided for the DataHub Agent Hackathon."	Open Rosetta landing page. Show healthcare demo and $28,478,287 impact number.
0:05	"Rosetta found a problem that traditional data-quality checks miss: the data was valid, but the meaning was not."	Pause on impact number.
0:15	"The clinical team and finance team both use billing_amount, but they define it differently. Clinical includes all source charges. Finance expects validated positive revenue."	Show competing definitions.
0:25	"Both definitions make sense on their own. But once they feed dashboards, reports, and AI systems, the organization no longer has one version of the truth."	Show downstream impact.
0:35	"In this dataset, that disagreement represents $28.4 million in billing value. No pipeline failed. No alert fired. The data moved successfully — the meaning did not."	Highlight impact.
0:50	"This is why we built Rosetta."	Transition into app.
Rosetta Overview
Time	What I Say	What I Show / Do
0:55	"Rosetta is a semantic consistency agent for DataHub. It discovers conflicting definitions, measures their impact, proposes a resolution, and creates a governed write plan."	Show five-agent workflow.
1:10	"This healthcare demonstration analyzes 55,500 synthetic patient records through five agents: Discover, Detect, Impact, Reconcile, and Write."	Start Healthcare Scan.
Agent 1 — Harvester
Time	What I Say	What I Show / Do
1:20	"The Harvester builds context from the DataHub graph — collecting definitions, ownership, schemas, lineage, and SQL logic."	Show Agent 1 loading metadata.
1:32	"Rosetta first understands how teams define their data before looking for disagreement."	Move to Agent 2.
Agent 2 — Conflict Detector
Time	What I Say	What I Show / Do
1:40	"The Conflict Detector found five conflicts in this environment."	Show conflict list.
1:45	"Here is the highest-impact example: billing amount."	Open billing conflict.
1:50	"Rosetta compares the definitions, SQL logic, constraints, and ownership context to identify where the meaning breaks."	Show evidence/confidence.
2:00	"This is explainable analysis from the DataHub graph — not a black-box answer."	Move to Agent 3.
Agent 3 — Blast Radius Analyzer
Time	What I Say	What I Show / Do
2:05	"The Blast-Radius Analyzer shows that the problem is not isolated."	Open lineage graph.
2:10	"It traces downstream assets and identifies where this definition is already being used."	Show affected datasets, dashboards, models.
2:20	"A semantic conflict becomes a business risk when it reaches decisions and AI systems."	Move to Agent 4.
Agent 4 — Reconciliation Broker
Time	What I Say	What I Show / Do
2:25	"The Reconciliation Broker creates a proposed canonical definition using the competing definitions and supporting evidence."	Show proposed definition.
2:35	"Rosetta does not overwrite metadata automatically. The owner reviews and approves the change."	Show approval button.
2:45	"Once approved, Rosetta creates the exact DataHub write plan."	Click approve.
Agent 5 — Writer
Time	What I Say	What I Show / Do
2:50	"The Writer produces a validated plan: create the canonical glossary term, connect impacted assets, and retire conflicting definitions."	Show write plan and VALIDATED badge.
3:00	"In Connected Mode, this approved plan can be executed against DataHub, giving future users and agents a trusted definition to inherit."	Show final screen.
Closing Line
Time	What I Say	What I Show / Do
3:10	"Rosetta helps organizations move from discovering conflicting meaning to governing the resolution."	Final tagline.
3:15	"Because data quality tells you whether numbers are valid. Rosetta helps ensure everyone agrees on what those numbers mean."	End screen.
