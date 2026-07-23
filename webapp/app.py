"""
Rosetta web app — the hosted, testable demo the judges click.

A tiny Flask server that:
  - serves a themed single-page UI (webapp/templates/index.html)
  - runs the narrated five-agent demo on demand      GET  /api/demo
  - runs a read-only scan and returns a report        GET  /api/scan
  - exports the last report as json/csv/md/html        GET  /api/export/<fmt>

It runs with ZERO configuration (uses the offline seed data) so anyone can
open the deployed URL and click "Run Demo". If you set DATAHUB_GMS_URL and
DATAHUB_GMS_TOKEN, the /api/scan endpoint will talk to your live instance
instead of the seed data.

Run locally:   python webapp/app.py       ->  http://localhost:5000
On Replit:     the .replit file runs this automatically.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Make the `rosetta` package importable when run from anywhere.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from flask import Flask, Response, jsonify, render_template

from rosetta import exporter
from rosetta.datahub_client import RosettaDataHub, _HAS_SDK
from rosetta.demo import run_demo
from rosetta.orchestrator import build_report, run_scan

app = Flask(__name__, static_folder="static", template_folder="templates")

# Cache the most recent report so the export endpoints have something to serve.
_LAST_REPORT: dict = {}


@app.route("/")
def index():
    live = bool(os.environ.get("DATAHUB_GMS_URL")) and _HAS_SDK
    return render_template("index.html", live_mode=live)


@app.route("/api/demo")
def api_demo():
    """Full narrated walkthrough (offline, zero-config)."""
    global _LAST_REPORT
    result = run_demo()
    _LAST_REPORT = result["report"]
    return jsonify(result)


@app.route("/api/scan")
def api_scan():
    """Read-only scan. Uses live DataHub if configured, else seed data."""
    global _LAST_REPORT
    if os.environ.get("DATAHUB_GMS_URL") and _HAS_SDK:
        dh = RosettaDataHub()
    else:
        dh = RosettaDataHub.__new__(RosettaDataHub)
    conflicts = run_scan(dh)
    report = build_report(conflicts)
    _LAST_REPORT = report
    return jsonify(report)


@app.route("/api/export/<fmt>")
def api_export(fmt: str):
    report = _LAST_REPORT or run_demo()["report"]
    try:
        content = exporter.export(report, fmt)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    ext = fmt.lower()
    return Response(
        content,
        mimetype=exporter.content_type(fmt),
        headers={
            "Content-Disposition": f'attachment; filename="rosetta_report.{ext}"'
        },
    )


@app.route("/health")
def health():
    return jsonify({"status": "ok", "live_datahub": bool(os.environ.get("DATAHUB_GMS_URL"))})


@app.route("/api/graph")
def api_graph():
    """Return the blast-radius graph for the highest-severity conflict."""
    report = _LAST_REPORT or run_demo()["report"]
    conflicts = report.get("conflicts", [])
    if not conflicts:
        return jsonify({"nodes": [], "edges": []})
    return jsonify({"metric": conflicts[0]["metric"],
                    "graph": conflicts[0].get("impact_graph", {})})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
