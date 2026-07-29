# What's in this repo

```
rosetta/
├── rosetta/                     the agent package
│   ├── datahub_client.py        read/write facade over the DataHub SDK
│   ├── detector.py              conflict detection (silent contradiction + hidden synonym)
│   ├── broker.py                reconciliation broker + writer
│   ├── demo.py                  narrated, zero-config demo mode
│   ├── exporter.py              json / csv / markdown / html exporters
│   └── orchestrator.py          CLI: --demo --report --apply --export
├── webapp/                      hosted demo the judges click
│   ├── app.py                   Flask server + /api/demo /api/scan /api/export
│   ├── templates/index.html     themed single-page UI
│   └── static/                  css, js, logo + favicon
├── examples/                    sample outputs (report, reconciled term, exports)
├── demo_data/seed_definitions.json   6 conflicting metrics across 5 domains
├── skills/detect-semantic-conflicts.md   reusable DataHub Skill (OSS bonus)
├── assets/                      logo, icon, architecture diagram, UI screenshot
├── docs/                        SETUP, SUBMISSION, DEMO scripts, checklists
├── tests/                       32 passing unit tests
├── LICENSE                      Apache-2.0
├── Dockerfile / render.yaml / Procfile / .replit   one-click deploy configs
└── requirements*.txt / pyproject.toml
```
