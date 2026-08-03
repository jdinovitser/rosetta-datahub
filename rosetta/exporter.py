"""
Rosetta result exporters.

Turns a conflict report (the dict returned by orchestrator.build_report) and
reconciliation audit records into downloadable artifacts:

  - JSON  : machine-readable, the source of truth
  - CSV   : one row per conflict, opens in any spreadsheet
  - Markdown : a human-readable report for a PR description or wiki
  - HTML  : a standalone, styled report judges can open in a browser

Every exporter returns a string and can optionally write to a path. The web
app and the CLI both call these so the "export & download" behaviour is
identical everywhere.
"""
from __future__ import annotations

import csv
import io
import json
from datetime import datetime, timezone
from pathlib import Path


_DEMO_PROVENANCE: dict[str, dict] = {
    "healthcare": {
        "scenario_label": "Healthcare: Official hackathon data",
        "generator": "Rosetta — https://github.com/jdinovitser/rosetta-datahub",
        "demo_mode": True,
        "dataset": "DataHub sample data supplied through the official Build with DataHub Agent Hackathon resources (healthcare.db)",
        "source_url": "https://github.com/datahub-project/static-assets/tree/main/datasets/healthcare",
        "git_commit_added": "ab334aaa3e72e2accf7b110f6325c0012e6501ff",
        "statement": "Generated in DEMO MODE against official hackathon sample data. Rosetta queries this file read-only. No real patient or personal information is used.",
        "rosetta_constructed": [
            "MetricDefinition pairs (rosetta/healthcare_source.py)",
            "DataHub URN lineage graph (_DOWNSTREAM dict)",
            "Glossary term URNs (urn:li:glossaryTerm:*)",
            "Team ownership URNs (urn:li:corpGroup:*)",
            "Severity scores and blast-radius overrides",
            "Canonical proposals (rosetta/broker.py)",
        ],
        "not_established": [
            "License of the source dataset",
            "Whether anomalies were intentionally planted or naturally present in the source",
        ],
        "full_provenance": "DATA_PROVENANCE.md",
    },
    "fiction_retail": {
        "scenario_label": "Retail: Supplementary scenario",
        "generator": "Rosetta — https://github.com/jdinovitser/rosetta-datahub",
        "demo_mode": True,
        "dataset": "Fiction Retail E-Commerce dataset (fiction_retail.db — 150,000 orders across 10 tables)",
        "source_url": "Not established — developer notes describe this as a Kaggle dataset; not independently confirmed from repository history",
        "git_commit_added": "e8690934dbd5ffc0ff45eb91f923fd255d28bab1",
        "statement": "Generated in DEMO MODE. Rosetta queries this file read-only.",
        "rosetta_constructed": [
            "MetricDefinition pairs (rosetta/fiction_retail_source.py)",
            "DataHub URN lineage graph",
            "Glossary term URNs",
            "Team ownership URNs",
            "Severity scores",
            "Canonical proposals (rosetta/broker.py)",
        ],
        "not_established": [
            "Original source URL",
            "License",
            "Whether data is synthetic",
        ],
        "full_provenance": "DATA_PROVENANCE.md",
    },
}

_LIVE_PROVENANCE = {
    "generator": "Rosetta — https://github.com/jdinovitser/rosetta-datahub",
    "demo_mode": False,
    "statement": "Generated against a live DataHub instance. Data source is the connected DataHub graph.",
    "rosetta_constructed": [
        "Conflict analysis (rosetta/detector.py)",
        "Blast-radius walk (rosetta/orchestrator.py)",
        "Canonical proposals (rosetta/broker.py)",
    ],
}


def _provenance_for(report: dict) -> dict:
    return _DEMO_PROVENANCE.get(report.get("source", ""), _LIVE_PROVENANCE)


def to_json(report: dict) -> str:
    out = dict(report)
    out["rosetta_provenance"] = _provenance_for(report)
    return json.dumps(out, indent=2)


def to_csv(report: dict) -> str:
    buf = io.StringIO()
    prov = _provenance_for(report)
    buf.write("# ROSETTA PROVENANCE\n")
    buf.write(f"# Dataset: {prov.get('dataset', 'Live DataHub scan')}\n")
    buf.write(f"# Source URL: {prov.get('source_url', 'Connected DataHub instance')}\n")
    buf.write(f"# Statement: {prov['statement']}\n")
    buf.write(f"# Rosetta-constructed: {'; '.join(prov.get('rosetta_constructed', []))}\n")
    if prov.get("not_established"):
        buf.write(f"# Not established: {'; '.join(prov['not_established'])}\n")
    buf.write(f"# Scenario: {prov.get('scenario_label', 'Live DataHub scan')}\n")
    buf.write(f"# Full provenance: {prov.get('full_provenance','DATA_PROVENANCE.md')}\n")
    buf.write("#\n")
    writer = csv.writer(buf)
    writer.writerow(
        [
            "metric",
            "kind",
            "severity",
            "confidence",
            "blast_radius",
            "est_cost_usd",
            "manual_hours",
            "logic_similarity",
            "name_similarity",
            "domains",
            "owners",
            "rationale",
            "ai_finding",
            "ai_evidence",
            "ai_impact",
            "ai_recommendation",
        ]
    )
    for c in report.get("conflicts", []):
        domains = " | ".join(d["domain"] for d in c["definitions"])
        owners = " | ".join(d["owner"] or "UNASSIGNED" for d in c["definitions"])
        imp = c.get("impact", {})
        ai = c.get("ai_explanation", {})
        writer.writerow(
            [
                c["metric"],
                c["kind"],
                c["severity"],
                c.get("confidence", ""),
                c["blast_radius"],
                imp.get("estimated_manual_cost_usd", ""),
                imp.get("manual_reconciliation_hours", ""),
                c["logic_similarity"],
                c["name_similarity"],
                domains,
                owners,
                c["rationale"],
                ai.get("finding", ""),
                ai.get("evidence", ""),
                ai.get("impact", ""),
                ai.get("recommendation", ""),
            ]
        )
    return buf.getvalue()


def to_markdown(report: dict) -> str:
    s = report.get("summary", {})
    lines = [
        "# Rosetta Semantic Consistency Report",
        "",
        f"_Generated at {report.get('generated_at', 'n/a')}_",
        "",
        "## Summary",
        "",
        f"- **Total conflicts:** {s.get('total_conflicts', 0)}",
        f"- **Critical:** {s.get('critical', 0)}",
        f"- **High:** {s.get('high', 0)}",
        f"- **Downstream assets at risk:** {s.get('assets_at_risk', 0)}",
        f"- **Est. manual reconciliation cost avoided:** "
        f"${s.get('impact', {}).get('estimated_cost_avoided_usd', 0):,} "
        f"({s.get('impact', {}).get('total_manual_hours_avoided', 0)} analyst-hours)",
        "",
        "## Conflicts",
        "",
    ]
    for i, c in enumerate(report.get("conflicts", []), 1):
        lines.append(f"### {i}. `{c['metric']}` — {c['kind']} ({c['severity'].upper()})")
        lines.append("")
        lines.append(f"> {c['rationale']}")
        lines.append("")
        ai = c.get("ai_explanation", {})
        if ai:
            lines.append("**AI Explanation**")
            lines.append("")
            lines.append(f"- **Finding:** {ai.get('finding', '')}")
            lines.append(f"- **Evidence:** {ai.get('evidence', '')}")
            lines.append(f"- **Impact:** {ai.get('impact', '')}")
            lines.append(f"- **Recommendation:** {ai.get('recommendation', '')}")
            lines.append("")
        lines.append(
            f"- **Blast radius:** {c['blast_radius']} downstream assets"
        )
        lines.append(
            f"- **Confidence:** {c.get('confidence', 'n/a')} · "
            f"**Est. cost if unreconciled:** "
            f"${c.get('impact', {}).get('estimated_manual_cost_usd', 0):,}"
        )
        if c.get("impact", {}).get("risk_statement"):
            lines.append(f"- **Risk:** {c['impact']['risk_statement']}")
        lines.append(
            f"- **Logic similarity:** {c['logic_similarity']} · "
            f"**Name similarity:** {c['name_similarity']}"
        )
        lines.append("")
        lines.append("| Domain | Owner | Definition | Computation |")
        lines.append("| --- | --- | --- | --- |")
        for d in c["definitions"]:
            defn = d["definition_text"].replace("|", "\\|")
            sql = d["sql_logic"].replace("|", "\\|")
            lines.append(f"| {d['domain']} | {d['owner']} | {defn} | `{sql}` |")
        lines.append("")
    prov = _provenance_for(report)
    lines += [
        "",
        "---",
        "",
        "## Data Provenance",
        "",
        f"- **Dataset:** {prov.get('dataset', 'Live DataHub scan')}",
        f"- **Source URL:** {prov.get('source_url', 'Connected DataHub instance')}",
        f"- **Statement:** {prov['statement']}",
        f"- **Rosetta-constructed:** {', '.join(prov.get('rosetta_constructed', []))}",
    ]
    if prov.get("not_established"):
        lines.append(f"- **Not established:** {'; '.join(prov['not_established'])}")
    lines += [
        f"- **Scenario:** {prov.get('scenario_label', 'Live DataHub scan')}",
        f"- **Full provenance:** `{prov.get('full_provenance','DATA_PROVENANCE.md')}`",
        "",
    ]
    return "\n".join(lines)


_SEV_COLOR = {
    "critical": "#e5484d",
    "high": "#f76808",
    "medium": "#ffb224",
    "low": "#30a46c",
}


def to_html(report: dict) -> str:
    prov = _provenance_for(report)
    scenario_label = prov.get("scenario_label", "Live DataHub scan")
    s = report.get("summary", {})
    cards = []
    for c in report.get("conflicts", []):
        color = _SEV_COLOR.get(c["severity"], "#8b8b8b")
        ai = c.get("ai_explanation", {})
        ai_block = ""
        if ai:
            ai_block = (
                "<div class='ai'><div class='ai-t'>AI Explanation</div>"
                f"<div class='ai-r'><b>Finding</b><span>{ai.get('finding','')}</span></div>"
                f"<div class='ai-r'><b>Evidence</b><span>{ai.get('evidence','')}</span></div>"
                f"<div class='ai-r'><b>Impact</b><span>{ai.get('impact','')}</span></div>"
                f"<div class='ai-r'><b>Recommendation</b><span>{ai.get('recommendation','')}</span></div>"
                "</div>"
            )
        rows = "".join(
            f"<tr><td>{d['domain']}</td><td class='mono'>{d['owner'] or '⚠ unassigned'}</td>"
            f"<td>{d['definition_text']}</td>"
            f"<td class='mono'>{d['sql_logic']}</td></tr>"
            for d in c["definitions"]
        )
        cards.append(
            f"""
            <div class="card">
              <div class="card-head">
                <span class="metric">{c['metric']}</span>
                <span class="badge" style="background:{color}">{c['severity'].upper()}</span>
                <span class="kind">{c['kind'].replace('_',' ')}</span>
                <span class="blast">blast radius: <b>{c['blast_radius']}</b></span>
              </div>
              <p class="rationale">{c['rationale']}</p>
              {ai_block}
              <table>
                <thead><tr><th>Domain</th><th>Owner</th><th>Definition</th><th>Computation</th></tr></thead>
                <tbody>{rows}</tbody>
              </table>
              <div class="sims">logic similarity {c['logic_similarity']} ·
                name similarity {c['name_similarity']} ·
                confidence {c.get('confidence', 'n/a')} ·
                est. cost ${c.get('impact', {}).get('estimated_manual_cost_usd', 0):,}</div>
            </div>"""
        )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Rosetta Semantic Consistency Report</title>
<style>
  :root{{--bg:#0a0f1f;--panel:#111a30;--line:#22304f;--cyan:#22d3ee;--text:#e6edf7;--muted:#8ea0c0}}
  *{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--text);
    font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;padding:32px}}
  h1{{font-size:26px;margin:0 0 4px}} .sub{{color:var(--muted);margin-bottom:24px}}
  .stats{{display:flex;gap:16px;flex-wrap:wrap;margin-bottom:28px}}
  .stat{{background:var(--panel);border:1px solid var(--line);border-radius:12px;
    padding:16px 22px;min-width:150px}}
  .stat .n{{font-size:30px;font-weight:700;color:var(--cyan)}}
  .stat .l{{color:var(--muted);font-size:13px;text-transform:uppercase;letter-spacing:.04em}}
  .card{{background:var(--panel);border:1px solid var(--line);border-radius:14px;
    padding:20px 22px;margin-bottom:18px}}
  .card-head{{display:flex;align-items:center;gap:14px;flex-wrap:wrap;margin-bottom:8px}}
  .metric{{font-size:18px;font-weight:700;font-family:ui-monospace,SFMono-Regular,Menlo,monospace}}
  .badge{{color:#0a0f1f;font-weight:700;font-size:12px;padding:3px 10px;border-radius:20px}}
  .kind{{color:var(--muted)}} .blast{{margin-left:auto;color:var(--muted)}}
  .rationale{{color:var(--text);opacity:.9;margin:6px 0 14px}}
  .ai{{border:1px solid var(--line);border-left:3px solid var(--cyan);border-radius:10px;
    padding:12px 14px;margin:0 0 14px;background:rgba(34,211,238,.04)}}
  .ai-t{{color:var(--cyan);font-size:11px;font-weight:700;text-transform:uppercase;
    letter-spacing:.08em;margin-bottom:8px}}
  .ai-r{{display:flex;gap:10px;font-size:13px;margin-bottom:6px}}
  .ai-r b{{flex:0 0 110px;color:var(--muted);font-weight:600}}
  .ai-r span{{flex:1}}
  table{{width:100%;border-collapse:collapse;font-size:14px}}
  th,td{{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top}}
  th{{color:var(--muted);font-weight:600;font-size:12px;text-transform:uppercase}}
  .mono{{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12.5px;color:#a9c7ff}}
  .sims{{color:var(--muted);font-size:12px;margin-top:10px}}
  footer{{color:var(--muted);font-size:12px;margin-top:30px}}
</style></head><body>
  <h1>Rosetta — Semantic Consistency Report</h1>
  <div class="sub">Generated {report.get('generated_at','n/a')}</div>
  <div class="stats">
    <div class="stat"><div class="n">{s.get('total_conflicts',0)}</div><div class="l">Conflicts</div></div>
    <div class="stat"><div class="n">{s.get('critical',0)}</div><div class="l">Critical</div></div>
    <div class="stat"><div class="n">{s.get('high',0)}</div><div class="l">High</div></div>
    <div class="stat"><div class="n">{s.get('assets_at_risk',0)}</div><div class="l">Assets at risk</div></div>
  </div>
  {''.join(cards)}
  <footer>Rosetta · the linter for meaning across your DataHub graph · Apache-2.0<br>
  <small style="color:var(--muted);font-size:11px">Scenario: {scenario_label} · {prov.get('statement','')}</small></footer>
</body></html>"""


_EXPORTERS = {
    "json": (to_json, "application/json"),
    "csv": (to_csv, "text/csv"),
    "md": (to_markdown, "text/markdown"),
    "html": (to_html, "text/html"),
}


def export(report: dict, fmt: str) -> str:
    fmt = fmt.lower()
    if fmt not in _EXPORTERS:
        raise ValueError(f"Unknown format '{fmt}'. Choose from {list(_EXPORTERS)}.")
    return _EXPORTERS[fmt][0](report)


def content_type(fmt: str) -> str:
    return _EXPORTERS[fmt.lower()][1]


def export_all(report: dict, out_dir: str | Path = "exports", stem: str | None = None) -> list[str]:
    """Write every supported format to out_dir. Returns the list of paths."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    if stem is None:
        stem = "rosetta_report_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    written = []
    for fmt in _EXPORTERS:
        path = out / f"{stem}.{fmt}"
        path.write_text(export(report, fmt))
        written.append(str(path))
    return written
