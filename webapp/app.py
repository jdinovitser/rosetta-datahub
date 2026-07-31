"""
Rosetta web app — the hosted, testable demo the judges click.

A tiny Flask server that:
  - serves a themed single-page UI (webapp/templates/index.html)
  - runs the narrated five-agent demo on demand      GET  /api/demo
  - runs a read-only scan and returns a report        GET  /api/scan
  - exports the last report as json/csv/md/html        GET  /api/export/<fmt>
  - returns executive intelligence dashboard           GET  /api/dashboard

It runs with ZERO configuration against DataHub sample data provided through
the official Build with DataHub Agent Hackathon resources. If you set
DATAHUB_GMS_URL and DATAHUB_GMS_TOKEN, the /api/scan endpoint will talk to
your live DataHub instance instead.

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

import urllib.request
import urllib.error
from flask import Flask, Response, jsonify, render_template, request, session

from rosetta import exporter
from rosetta.broker import ApprovalToken, Proposal, apply_proposal
from rosetta.datahub_client import RosettaDataHub, _HAS_SDK
from rosetta.demo import run_demo
from rosetta.healthcare_demo import run_healthcare_demo
from rosetta.fiction_retail_demo import run_fiction_retail_demo
from rosetta.orchestrator import build_report, run_scan
from rosetta.intelligence import compute_executive_dashboard

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.environ.get("SESSION_SECRET", "rosetta-dev-secret")

# Cache the most recent report + proposals so export and write-back have something to serve.
_LAST_REPORT: dict = {}
_LAST_PROPOSALS: list = []
_LAST_APPROVAL_TOKEN: dict | None = None  # set by /api/approve, consumed by /api/write-back


def _active_gms_url() -> str:
    """Return the DataHub GMS URL from session (user-entered) or env var."""
    return session.get("datahub_gms_url") or os.environ.get("DATAHUB_GMS_URL", "")


def _active_token() -> str:
    """Return the DataHub token from session or env var."""
    return session.get("datahub_token") or os.environ.get("DATAHUB_GMS_TOKEN", "")


@app.route("/")
def index():
    live = bool(_active_gms_url()) and _HAS_SDK
    return render_template("index.html", live_mode=live)


@app.route("/api/datahub-connect", methods=["POST"])
def api_datahub_connect():
    """Store DataHub credentials in session and verify connectivity."""
    data = request.get_json(force=True) or {}
    gms_url = (data.get("gms_url") or "").rstrip("/")
    token = (data.get("token") or "").strip()

    if not gms_url:
        return jsonify({"ok": False, "error": "GMS URL is required."}), 400

    # Quick connectivity check — hit the /health endpoint (no auth needed).
    try:
        req = urllib.request.Request(
            f"{gms_url}/health",
            headers={"Authorization": f"Bearer {token}"} if token else {},
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            if resp.status not in (200, 204):
                raise ValueError(f"Unexpected status {resp.status}")
    except urllib.error.URLError as exc:
        return jsonify({"ok": False, "error": f"Cannot reach {gms_url}: {exc.reason}"}), 400
    except Exception as exc:  # noqa: BLE001
        return jsonify({"ok": False, "error": str(exc)}), 400

    # Persist in session so the scan endpoints can use them.
    session["datahub_gms_url"] = gms_url
    session["datahub_token"] = token
    return jsonify({"ok": True, "gms_url": gms_url})


@app.route("/api/demo")
def api_demo():
    """Full narrated walkthrough (offline, zero-config)."""
    global _LAST_REPORT, _LAST_PROPOSALS
    result = run_demo()
    _LAST_REPORT = result["report"]
    _LAST_PROPOSALS = result.get("proposals", [])
    return jsonify(result)


@app.route("/api/fiction-retail-scan")
def api_fiction_retail_scan():
    """Five-agent pipeline on the real Fiction Retail E-Commerce dataset."""
    global _LAST_REPORT, _LAST_PROPOSALS
    result = run_fiction_retail_demo()
    _LAST_REPORT = result["report"]
    _LAST_PROPOSALS = result.get("proposals", [])
    return jsonify(result)


@app.route("/api/healthcare-scan")
def api_healthcare_scan():
    """Five-agent pipeline on the real DataHub healthcare sample dataset."""
    global _LAST_REPORT, _LAST_PROPOSALS
    result = run_healthcare_demo()
    _LAST_REPORT = result["report"]
    _LAST_PROPOSALS = result.get("proposals", [])
    return jsonify(result)


@app.route("/api/approve", methods=["POST"])
def api_approve():
    """Create an approval token for the current write plan.

    Demo Mode:      creates token, returns plan_id + approved_at; no DataHub
                    write ever follows — approval is for the validated plan only.
    Connected Mode: creates token so /api/write-back can validate it before
                    executing.  Token is plan-specific and single-use.
    """
    global _LAST_APPROVAL_TOKEN
    if not _LAST_PROPOSALS:
        return jsonify({"ok": False, "error": "No scan results. Run a scan first."}), 400

    p_dict  = _LAST_PROPOSALS[0]
    plan_id = p_dict.get("plan_id", "")
    if not plan_id:
        return jsonify({"ok": False, "error": "Plan ID not available. Re-run the scan."}), 400

    from datetime import datetime, timezone
    approved_at = datetime.now(timezone.utc).isoformat()
    mode = "live" if _active_gms_url() else "demo"

    _LAST_APPROVAL_TOKEN = {
        "plan_id":     plan_id,
        "conflict_id": p_dict.get("term_id", ""),
        "approved_at": approved_at,
        "mode":        mode,
    }
    return jsonify({"ok": True, "plan_id": plan_id, "approved_at": approved_at, "mode": mode})


@app.route("/api/write-back", methods=["POST"])
def api_write_back():
    """Apply the top-conflict proposal to a live DataHub instance.

    Requires an explicit approval token (from /api/approve) whose plan_id
    matches the current proposal.  Demo Mode is blocked here even if somehow
    a token were present, because there is no live GMS URL.
    """
    global _LAST_APPROVAL_TOKEN
    if not _LAST_PROPOSALS:
        return jsonify({"ok": False, "error": "No scan results to write back. Run a scan first."}), 400

    if not _LAST_APPROVAL_TOKEN:
        return jsonify({
            "ok": False,
            "error": (
                "Execution blocked: explicit approval is required for this write plan. "
                "Click 'Approve & Generate Write Plan' first."
            ),
        }), 403

    gms_url = _active_gms_url()
    token   = _active_token()
    if not gms_url:
        return jsonify({"ok": False, "error": "No live DataHub connection. Use Connect DataHub first."}), 400
    if not _HAS_SDK:
        return jsonify({"ok": False, "error": "DataHub SDK not available in this environment."}), 500

    # Belt-and-suspenders: block Demo Mode tokens even if a GMS URL appears later
    if _LAST_APPROVAL_TOKEN.get("mode") == "demo":
        return jsonify({
            "ok": False,
            "error": "Execution blocked: this approval was issued in Demo Mode and cannot authorise a live write.",
        }), 403

    p_dict = _LAST_PROPOSALS[0]
    proposal = Proposal(
        term_id=p_dict["term_id"],
        display_name=p_dict["display_name"],
        canonical_definition=p_dict["canonical_definition"],
        approvers=p_dict.get("approvers", []),
        deprecated_terms=p_dict.get("deprecated_terms", []),
        affected_assets=p_dict.get("affected_assets", []),
        plan_id=p_dict.get("plan_id", ""),
    )

    approval = ApprovalToken(
        plan_id=_LAST_APPROVAL_TOKEN["plan_id"],
        conflict_id=_LAST_APPROVAL_TOKEN["conflict_id"],
        approved_at=_LAST_APPROVAL_TOKEN["approved_at"],
        mode=_LAST_APPROVAL_TOKEN.get("mode", "live"),
    )

    os.environ["DATAHUB_GMS_URL"] = gms_url
    if token:
        os.environ["DATAHUB_GMS_TOKEN"] = token

    try:
        dh = RosettaDataHub()
        result = apply_proposal(dh, proposal, approval)
        _LAST_APPROVAL_TOKEN = None   # single-use: consumed after execution
        return jsonify({"ok": True, "result": result})
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 403
    except Exception as exc:  # noqa: BLE001
        return jsonify({"ok": False, "error": str(exc)}), 500


@app.route("/api/scan")
def api_scan():
    """Read-only scan. Uses live DataHub if configured, else hackathon sample data."""
    global _LAST_REPORT, _LAST_PROPOSALS
    gms_url = _active_gms_url()
    token = _active_token()
    if gms_url and _HAS_SDK:
        # Temporarily inject session creds so RosettaDataHub picks them up.
        os.environ["DATAHUB_GMS_URL"] = gms_url
        if token:
            os.environ["DATAHUB_GMS_TOKEN"] = token
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


@app.route("/api/dashboard")
def api_dashboard():
    """Executive Data Intelligence Dashboard — scores + prioritised actions."""
    report = _LAST_REPORT or run_demo()["report"]
    return jsonify(compute_executive_dashboard(report))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
