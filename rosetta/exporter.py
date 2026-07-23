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


def to_json(report: dict) -> str:
    return json.dumps(report, indent=2)


def to_csv(report: dict) -> str:
    buf = io.StringIO()
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
        ]
    )
    for c in report.get("conflicts", []):
        domains = " | ".join(d["domain"] for d in c["definitions"])
        owners = " | ".join(d["owner"] for d in c["definitions"])
        imp = c.get("impact", {})
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
    return "\n".join(lines)


_SEV_COLOR = {
    "critical": "#e5484d",
    "high": "#f76808",
    "medium": "#ffb224",
    "low": "#30a46c",
}


def to_html(report: dict) -> str:
    s = report.get("summary", {})
    cards = []
    for c in report.get("conflicts", []):
        color = _SEV_COLOR.get(c["severity"], "#8b8b8b")
        rows = "".join(
            f"<tr><td>{d['domain']}</td><td class='mono'>{d['owner']}</td>"
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
  <footer>Rosetta · the linter for meaning across your DataHub graph · Apache-2.0</footer>
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
