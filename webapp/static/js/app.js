// Rosetta web UI: runs the pipeline, animates it, and paints an interactive
// blast-radius lineage graph so judges SEE a wrong metric contaminate the org.
const $ = (s) => document.querySelector(s);

function esc(t) {
  return String(t).replace(/[&<>"]/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
}

/* ---------- pipeline steps ---------- */
function renderSteps(steps) {
  const ol = $("#steps");
  ol.innerHTML = "";
  steps.forEach((s, i) => {
    const li = document.createElement("li");
    li.className = "step";
    li.style.animationDelay = `${i * 0.22}s`;
    li.innerHTML = `
      <div class="ic">${esc(s.icon)}</div>
      <div>
        <div class="agent">${esc(s.agent)}</div>
        <div class="title">${esc(s.title)}</div>
        <div class="detail">${esc(s.detail)}</div>
      </div>`;
    ol.appendChild(li);
  });
}

/* ---------- animated counters ---------- */
function animateCount(el, to, opts = {}) {
  const dur = 1100, start = performance.now(), from = 0;
  const pre = opts.prefix || "", suf = opts.suffix || "";
  function tick(now) {
    const p = Math.min(1, (now - start) / dur);
    const eased = 1 - Math.pow(1 - p, 3);
    const val = Math.round(from + (to - from) * eased);
    el.textContent = pre + val.toLocaleString() + suf;
    if (p < 1) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}

function renderSummary(sum) {
  $("#summary").hidden = false;
  animateCount($("#sTotal"), sum.total_conflicts);
  animateCount($("#sHigh"), sum.high);
  animateCount($("#sAssets"), sum.assets_at_risk);
  const imp = sum.impact || {};
  animateCount($("#sCost"), imp.estimated_cost_avoided_usd || 0, { prefix: "$" });
}

/* ---------- interactive blast-radius graph (no dependencies) ---------- */
const TYPE_COLOR = {
  metric: "#7c9cff", dataset: "#35c4c9", dashboard: "#f7a03b", model: "#e5484d",
};
const TYPE_ICON = { metric: "◆", dataset: "▦", dashboard: "▤", model: "✦" };

function drawGraph(graph, metricName) {
  const svg = $("#graph");
  svg.innerHTML = "";
  if (!graph || !graph.nodes || !graph.nodes.length) {
    $("#graphWrap").hidden = true;
    return;
  }
  $("#graphWrap").hidden = false;
  $("#graphTitle").textContent = `Blast radius: ${metricName}`;

  const W = svg.clientWidth || 640, H = 380;
  svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
  const nodes = graph.nodes.map((n) => ({ ...n }));
  const idx = Object.fromEntries(nodes.map((n, i) => [n.id, i]));
  const links = graph.edges.map((e) => ({ s: idx[e.source], t: idx[e.target] }));

  // seed positions: metrics on the left, spread the rest
  nodes.forEach((n, i) => {
    n.x = n.type === "metric" ? W * 0.14 + (Math.random() * 30)
                              : W * 0.4 + Math.random() * W * 0.5;
    n.y = H * 0.1 + (i / nodes.length) * H * 0.8 + (Math.random() * 40 - 20);
    n.vx = 0; n.vy = 0;
  });

  // quick force sim
  for (let it = 0; it < 320; it++) {
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        let dx = nodes[i].x - nodes[j].x, dy = nodes[i].y - nodes[j].y;
        let d2 = dx * dx + dy * dy + 0.01, d = Math.sqrt(d2);
        const rep = 4200 / d2;
        dx /= d; dy /= d;
        nodes[i].vx += dx * rep; nodes[i].vy += dy * rep;
        nodes[j].vx -= dx * rep; nodes[j].vy -= dy * rep;
      }
    }
    links.forEach((l) => {
      const a = nodes[l.s], b = nodes[l.t];
      let dx = b.x - a.x, dy = b.y - a.y, d = Math.sqrt(dx * dx + dy * dy) + 0.01;
      const f = (d - 90) * 0.02; dx /= d; dy /= d;
      a.vx += dx * f; a.vy += dy * f; b.vx -= dx * f; b.vy -= dy * f;
    });
    nodes.forEach((n) => {
      n.x += n.vx * 0.5; n.y += n.vy * 0.5; n.vx *= 0.82; n.vy *= 0.82;
      n.x = Math.max(30, Math.min(W - 30, n.x));
      n.y = Math.max(28, Math.min(H - 28, n.y));
    });
  }

  const NS = "http://www.w3.org/2000/svg";
  // edges
  links.forEach((l, i) => {
    const a = nodes[l.s], b = nodes[l.t];
    const line = document.createElementNS(NS, "line");
    line.setAttribute("x1", a.x); line.setAttribute("y1", a.y);
    line.setAttribute("x2", b.x); line.setAttribute("y2", b.y);
    line.setAttribute("class", "gedge");
    line.style.animationDelay = `${i * 0.03}s`;
    svg.appendChild(line);
  });
  // nodes
  nodes.forEach((n, i) => {
    const g = document.createElementNS(NS, "g");
    g.setAttribute("class", "gnode");
    g.setAttribute("transform", `translate(${n.x},${n.y})`);
    g.style.animationDelay = `${0.3 + i * 0.04}s`;
    const r = n.type === "metric" ? 13 : n.type === "model" ? 11 : 9;
    const c = document.createElementNS(NS, "circle");
    c.setAttribute("r", r);
    c.setAttribute("fill", TYPE_COLOR[n.type] || "#889");
    if (n.type === "model") c.setAttribute("class", "pulse");
    const t = document.createElementNS(NS, "text");
    t.setAttribute("y", -r - 5);
    t.setAttribute("text-anchor", "middle");
    t.setAttribute("class", "glabel");
    t.textContent = (n.label || n.id).split("\n")[0].slice(0, 18);
    g.appendChild(c); g.appendChild(t);
    const title = document.createElementNS(NS, "title");
    title.textContent = `${n.type}: ${n.label}`;
    g.appendChild(title);
    svg.appendChild(g);
  });
}

/* ---------- reconciliation reveal ---------- */
function renderReconcile(c) {
  const rec = c.proposed_reconciliation;
  if (!rec) return "";
  const before = rec.before.map((b) =>
    `<div class="before-item"><span class="dot bad"></span>
       <b>${esc(b.domain)}</b>: ${esc(b.definition)}</div>`).join("");
  return `
    <div class="reconcile">
      <div class="rec-col rec-before">
        <div class="rec-h">Before · ${rec.before.length} conflicting definitions</div>
        ${before}
      </div>
      <div class="rec-arrow">→</div>
      <div class="rec-col rec-after">
        <div class="rec-h">After · one canonical term</div>
        <div class="after-item"><span class="dot good"></span>
          <b>${esc(rec.after.display_name)}</b>
          <span class="tag">canonical</span><br>
          ${esc(rec.after.definition)}
        </div>
      </div>
    </div>`;
}

/* ---------- conflicts ---------- */
let CURRENT = [];
function renderConflicts(conflicts) {
  CURRENT = conflicts;
  const wrap = $("#conflicts");
  wrap.innerHTML = "";
  conflicts.forEach((c, ci) => {
    const rows = c.definitions.map((d) =>
      `<tr><td>${esc(d.domain)}</td><td class="mono">${esc(d.owner)}</td>
       <td>${esc(d.definition_text)}</td>
       <td class="mono">${esc(d.sql_logic)}</td></tr>`).join("");
    const imp = c.impact || {};
    const conf = c.confidence != null ? `${Math.round(c.confidence * 100)}%` : "—";
    const div = document.createElement("div");
    div.className = `conflict ${c.severity}`;
    div.innerHTML = `
      <div class="chead">
        <span class="metric">${esc(c.metric)}</span>
        <span class="badge ${c.severity}">${c.severity.toUpperCase()}</span>
        <span class="kind">${esc(c.kind.replace(/_/g, " "))}</span>
        <span class="blast">blast: <b>${c.blast_radius}</b></span>
        <span class="conf">confidence <b>${conf}</b></span>
        <button class="viz-btn" data-ci="${ci}">◆ Visualize</button>
      </div>
      <div class="rationale">${esc(c.rationale)}</div>
      ${imp.risk_statement ? `<div class="risk">⚠ ${esc(imp.risk_statement)}
         &nbsp;·&nbsp; est. cost if unreconciled <b>$${(imp.estimated_manual_cost_usd||0).toLocaleString()}</b></div>` : ""}
      <table class="defs">
        <thead><tr><th>Domain</th><th>Owner</th><th>Definition</th><th>Computation</th></tr></thead>
        <tbody>${rows}</tbody>
      </table>
      ${renderReconcile(c)}`;
    wrap.appendChild(div);
  });
  wrap.querySelectorAll(".viz-btn").forEach((b) =>
    b.addEventListener("click", () => {
      const c = CURRENT[+b.dataset.ci];
      drawGraph(c.impact_graph, c.metric);
      $("#graphWrap").scrollIntoView({ behavior: "smooth", block: "center" });
    }));
  // auto-visualize the top conflict
  if (conflicts[0] && conflicts[0].impact_graph)
    drawGraph(conflicts[0].impact_graph, conflicts[0].metric);
}

/* ---------- run ---------- */
async function run(endpoint) {
  const btnA = $("#runDemo"), btnB = $("#runScan");
  btnA.disabled = btnB.disabled = true;
  $("#steps").innerHTML = `<li class="empty">Running the pipeline…</li>`;
  try {
    const res = await fetch(endpoint);
    const data = await res.json();
    const report = data.report || data;
    if (data.steps) renderSteps(data.steps);
    else $("#steps").innerHTML = `<li class="empty">Scan complete. See findings →</li>`;
    renderSummary(report.summary);
    renderConflicts(report.conflicts);
    $("#exportBar").hidden = false;
  } catch (e) {
    $("#steps").innerHTML = `<li class="empty">Error: ${esc(e.message)}</li>`;
  } finally {
    btnA.disabled = btnB.disabled = false;
  }
}

$("#runDemo").addEventListener("click", () => run("/api/demo"));
$("#runScan").addEventListener("click", () => run("/api/scan"));
