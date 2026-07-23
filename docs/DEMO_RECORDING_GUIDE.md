# Recording the <3 minute demo video

Judges require a public YouTube/Vimeo video under 3 minutes showing the project in action.

## Setup before recording
1. `python webapp/app.py` and open http://localhost:5000 (or your deployed URL).
2. Full-screen the browser. Have `DEMO_SCRIPT.md` open on a second screen.
3. Optional cinematic terminal reveal: `python -m rosetta.orchestrator --demo --pace 0.6`

## Shot list (matches docs/DEMO_SCRIPT.md, ~3:00)
- **0:00–0:20** Cold open. Show two dashboards with different MAU numbers. VO: "Both are right. Both are wrong."
- **0:20–1:05** Open the Rosetta app. Click **Run the five-agent demo**. The pipeline animates: Harvester → Detector lights up `active_user` forking into two definitions across 12 assets.
- **1:05–1:50** Point at the Reconciliation Broker step: one canonical definition drafted, routed to the real owners from DataHub ownership.
- **1:50–2:35** Show the Writer step (upsert + link 12 assets + deprecate loser). Click an **Export** chip to download the HTML/JSON report — proof of a real artifact.
- **2:35–3:00** `pytest -q` → 32 passed. Show the `detect-semantic-conflicts` skill file. Tagline: "Rosetta doesn't just answer questions. It makes sure your whole company is asking the same one."

## Tips
- Keep under 2:50 to be safe.
- Record 1080p. Enable public visibility. Paste the link into SUBMISSION.md and the Devpost form.
