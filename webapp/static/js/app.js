// Rosetta — Semantic Consistency Agent
// Guided walkthrough UI + full technical view

const $ = (s) => document.querySelector(s);

function esc(t) {
  return String(t).replace(/[&<>"]/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c])
  );
}

function friendlyMetric(m) {
  if (!m) return m;
  if (m.includes("~")) {
    return m.split("~").map((p) =>
      p.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())
    ).join(" vs ");
  }
  return m;
}

function animateCount(el, to, opts = {}) {
  if (!el) return;
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

/* ══════════════════════════════════════════════════════════════════════════
   WALKTHROUGH STATE MACHINE
   ══════════════════════════════════════════════════════════════════════════ */

const STEP_LABELS = ["", "Discover", "Detect", "Impact", "Reconcile", "Write"];

let currentStep = 0;       // 0 = landing
let demoData = null;
let dashData = null;
let stepsReady = false;
let techVisible = false;

// Build the 5 progress dots in the topbar
function buildProgressDots() {
  const dotsEl = $("#wtDots");
  const labelsEl = $("#wtDotLabels");
  dotsEl.innerHTML = "";
  labelsEl.innerHTML = "";
  STEP_LABELS.slice(1).forEach((label, i) => {
    const step = i + 1;
    if (i > 0) {
      const line = document.createElement("div");
      line.className = "wt-dot-line";
      line.id = `wtLine${step}`;
      dotsEl.appendChild(line);
    }
    const dot = document.createElement("div");
    dot.className = "wt-dot";
    dot.id = `wtDot${step}`;
    dotsEl.appendChild(dot);

    const lbl = document.createElement("div");
    lbl.className = "wt-dot-label";
    lbl.textContent = label;
    labelsEl.appendChild(lbl);
  });
}

function updateProgress(step) {
  for (let i = 1; i <= 5; i++) {
    const dot = document.getElementById(`wtDot${i}`);
    if (!dot) continue;
    dot.className = "wt-dot" + (i < step ? " done" : i === step ? " active" : "");
    const line = document.getElementById(`wtLine${i}`);
    if (line) line.className = "wt-dot-line" + (i <= step ? " done" : "");
  }
}

function gotoStep(n) {
  const from = currentStep;
  currentStep = n;

  // Show/hide steps
  for (let i = 0; i <= 5; i++) {
    const el = document.getElementById(`wtStep${i}`);
    if (!el) continue;
    if (i === n) {
      el.classList.add("active");
      el.classList.remove("exit");
    } else if (i === from) {
      el.classList.remove("active");
      el.classList.add("exit");
      setTimeout(() => el.classList.remove("exit"), 400);
    } else {
      el.classList.remove("active", "exit");
    }
  }

  // Progress indicator — always visible; on step 0 all dots are dim
  if (n === 0) {
    updateProgress(0); // all dots dim
  } else {
    updateProgress(n);
  }

  // Topbar nav visible on landing; progress dots visible during walkthrough
  const topbarNav = $("#topbarNav");
  const wtProgress = $("#wtProgress");
  if (topbarNav) topbarNav.hidden = (n !== 0);
  if (wtProgress) wtProgress.hidden = (n === 0);

  // Nav bar
  const nav = $("#wtNav");
  if (n === 0) {
    nav.hidden = true;
  } else {
    nav.hidden = false;
    const prevBtn = $("#prevBtn");
    prevBtn.disabled = false;
    prevBtn.textContent = n === 1 ? "⌂ Home" : "← Previous";
    const nextBtn = $("#nextBtn");
    nextBtn.textContent = n === 5 ? "View Full Report →" : "Next →";
  }

  // Step label
  const lbl = $("#wtLabel");
  if (lbl && n >= 1) lbl.textContent = `Agent ${n} of 5 · ${STEP_LABELS[n]}`;

  // Fire step-3 number animation whenever step 3 becomes active
  if (n === 3) setTimeout(animateStep3, 350);
}

function showTech() {
  techVisible = true;
  $("#techView").hidden = false;
  $("#walkthrough").hidden = true;
  const topbarNav = $("#topbarNav");
  if (topbarNav) topbarNav.hidden = true;
  $("#techView").scrollIntoView({ behavior: "smooth", block: "start" });
}

function showWalkthrough() {
  techVisible = false;
  $("#techView").hidden = true;
  $("#walkthrough").hidden = false;
  const topbarNav = $("#topbarNav");
  if (topbarNav) topbarNav.hidden = (currentStep !== 0);
}


/* ══════════════════════════════════════════════════════════════════════════
   STEP CONTENT BUILDERS
   ══════════════════════════════════════════════════════════════════════════ */

function buildStep1(data) {
  const report = data.report || data;
  const harvStep = (data.steps || []).find((s) => s.agent === "Harvester") || {};
  // Parse numbers from detail text, fall back to summary
  const detail = harvStep.detail || "";
  const defMatch = detail.match(/(\d+)\s+metric/);
  const domMatch = detail.match(/(\d+)\s+domain/);
  const ndefs = defMatch ? defMatch[1] : "12";
  const ndoms = domMatch ? domMatch[1] : "6";
  const nassets = (report.summary || {}).assets_at_risk || 63;

  return `
  <div class="agent-step-inner">
    <img class="step-mascot" src="/static/img/mascot-sticker.png" alt="">
    <div class="agent-chip">
      <span class="agent-chip-icon">🔍</span>
      <span>HARVESTER &nbsp;·&nbsp; AGENT 1 OF 5</span>
    </div>
    <h2 class="step-title">Discover the meaning</h2>
    <p class="step-subtitle">Rosetta reads every metric definition in your DataHub graph.</p>

    <div class="agent-card">
      <div class="agent-terminal">
        <div class="term-line done">✓ DataHub glossary terms loaded</div>
        <div class="term-line done">✓ Metric owners identified</div>
        <div class="term-line done">✓ Cross-domain lineage mapped</div>
        <div class="term-line done">✓ SQL logic extracted for comparison</div>
      </div>
    </div>

    <div class="step-stats">
      <div class="step-stat">
        <div class="ss-n" id="s1defs">—</div>
        <div class="ss-l">Metric Definitions</div>
      </div>
      <div class="step-stat">
        <div class="ss-n" id="s1doms">—</div>
        <div class="ss-l">Business Domains</div>
      </div>
      <div class="step-stat">
        <div class="ss-n" id="s1assets">—</div>
        <div class="ss-l">Downstream Assets</div>
      </div>
    </div>

    <p class="step-narrative">
      "Rosetta starts by understanding how your organisation defines its data —
      before anyone knows the definitions disagree."
    </p>
  </div>`;
}

function buildStep2(report) {
  const top = (report.conflicts || [])[0];
  if (!top) return `<div class="agent-step-inner"><p>No conflicts found.</p></div>`;

  const defs = top.definitions || [];
  const d0 = defs[0] || {};
  const d1 = defs[1] || {};
  const conf = top.confidence != null ? Math.round(top.confidence * 100) : "—";
  const sim  = top.logic_similarity != null ? Math.round(top.logic_similarity * 100) : "—";
  const name = friendlyMetric(top.metric);

  return `
  <div class="agent-step-inner">
    <img class="step-mascot" src="/static/img/mascot-sticker.png" alt="">
    <div class="agent-chip alert">
      <span class="agent-chip-icon">🚨</span>
      <span>CONFLICT DETECTOR &nbsp;·&nbsp; AGENT 2 OF 5</span>
    </div>
    <h2 class="step-title">Semantic collision detected</h2>
    <p class="step-subtitle">Same word. Completely different meaning.</p>

    <div class="conflict-spotlight">
      <div class="cs-header">
        <span class="cs-metric">${esc(name)}</span>
        <span class="badge critical">CRITICAL</span>
        <span class="cs-kind">silent contradiction</span>
      </div>

      <div class="cs-defs">
        <div class="cs-def def-bad">
          <div class="cs-team">${esc(d0.domain || "Team A")}</div>
          <div class="cs-text">"${esc(d0.definition_text || "")}"</div>
        </div>
        <div class="cs-vs">≠</div>
        <div class="cs-def def-bad">
          <div class="cs-team">${esc(d1.domain || "Team B")}</div>
          <div class="cs-text">"${esc(d1.definition_text || "")}"</div>
        </div>
      </div>

      <div class="cs-meta">
        <div class="cs-meta-item">
          <div class="cs-meta-n">${conf}%</div>
          <div class="cs-meta-l">Conflict Confidence</div>
        </div>
        <div class="cs-meta-item">
          <div class="cs-meta-n">${sim}%</div>
          <div class="cs-meta-l">Logic Similarity</div>
        </div>
        <div class="cs-meta-item">
          <div class="cs-meta-n">${top.blast_radius}</div>
          <div class="cs-meta-l">Assets at Risk</div>
        </div>
      </div>
    </div>

    <div class="step-tagline">"Same words. Different meaning."</div>
  </div>`;
}

function buildStep3(report) {
  const top = (report.conflicts || [])[0];
  if (!top) return `<div class="agent-step-inner"><p>No data.</p></div>`;

  const imp = top.impact || {};
  const breakdown = imp.asset_breakdown || {};
  const cost = imp.estimated_manual_cost_usd || 0;
  const hours = imp.manual_reconciliation_hours || 0;
  const blast = top.blast_radius || 0;
  const name = friendlyMetric(top.metric);

  // Build asset type chips
  const typeIcons = { dashboard: "📊", model: "🤖", dataset: "📦", table: "🗄" };
  const chips = Object.entries(breakdown)
    .filter(([, v]) => v > 0)
    .map(([k, v]) =>
      `<div class="asset-chip">
        <span>${typeIcons[k] || "📁"}</span>
        <span class="ac-n">${v}</span>
        <span class="ac-l">${k}${v !== 1 ? "s" : ""}</span>
       </div>`
    ).join("");

  return `
  <div class="agent-step-inner">
    <img class="step-mascot" src="/static/img/mascot-sticker.png" alt="">
    <div class="agent-chip warn">
      <span class="agent-chip-icon">💥</span>
      <span>BLAST-RADIUS ANALYZER &nbsp;·&nbsp; AGENT 3 OF 5</span>
    </div>
    <h2 class="step-title">Measure the impact</h2>
    <p class="step-subtitle">How far does a wrong "${esc(name)}" travel downstream?</p>

    <div class="impact-numbers">
      <div class="impact-num crit">
        <div class="in-n" id="s3blast">—</div>
        <div class="in-l">Downstream Assets<br>Contaminated</div>
      </div>
      <div class="impact-num">
        <div class="in-n green" id="s3cost">—</div>
        <div class="in-l">Estimated Business<br>Cost if Unresolved</div>
      </div>
      <div class="impact-num">
        <div class="in-n" id="s3hours">—</div>
        <div class="in-l">Analyst Hours<br>to Fix Manually</div>
      </div>
    </div>

    <div class="asset-chips">${chips}</div>

    <div class="s3-graph-wrap">
      <div class="s3-graph-legend">
        <span class="s3-leg-item"><span class="s3-dot" style="background:#7c9cff"></span>metric</span>
        <span class="s3-leg-item"><span class="s3-dot" style="background:#35c4c9"></span>dataset</span>
        <span class="s3-leg-item"><span class="s3-dot" style="background:#f7a03b"></span>dashboard</span>
        <span class="s3-leg-item"><span class="s3-dot s3-dot-pulse" style="background:#e5484d"></span>AI model</span>
      </div>
      <svg id="s3Graph" class="s3-graph-svg" data-h="300" aria-label="Blast-radius dependency graph"></svg>
    </div>

    <p class="step-narrative">
      "A wrong definition silently contaminates every dashboard, model, and
      dataset downstream — with no error message."
    </p>
  </div>`;
}

function buildStep4(report) {
  const top = (report.conflicts || [])[0];
  const rec = (top || {}).proposed_reconciliation || {};
  const before = rec.before || [];
  const after = rec.after || {};
  const name = friendlyMetric((top || {}).metric || "");

  const beforeItems = before.map((b) =>
    `<div class="rec4-before-item">
      <span class="dot bad"></span>
      <div>
        <div class="rec4-team">${esc(b.domain)}</div>
        <div class="rec4-def">"${esc(b.definition)}"</div>
      </div>
     </div>`
  ).join("");

  return `
  <div class="agent-step-inner">
    <img class="step-mascot" src="/static/img/mascot-sticker.png" alt="">
    <div class="agent-chip gov">
      <span class="agent-chip-icon">🤝</span>
      <span>RECONCILIATION BROKER &nbsp;·&nbsp; AGENT 4 OF 5</span>
    </div>
    <h2 class="step-title">Create one trusted definition</h2>
    <p class="step-subtitle">Rosetta proposes a canonical term — humans approve it.</p>

    <div class="rec4-wrap">
      <div class="rec4-panel before-panel">
        <div class="rec4-head">Conflicting Definitions</div>
        ${beforeItems}
      </div>

      <div class="rec4-arrow">↓</div>

      <div class="rec4-panel after-panel">
        <div class="rec4-head">Proposed Canonical Definition</div>
        <div class="rec4-canonical">
          <div class="rec4-name">${esc(after.display_name || name)}</div>
          <span class="tag">canonical</span>
          <div class="rec4-def-text">"${esc(after.definition || "One agreed-upon definition for all teams.")}"</div>
        </div>
      </div>
    </div>

    <div class="approval-row">
      <span class="approval-note">⚠ Human approval required before writing to DataHub.</span>
      <button class="btn primary approve-btn" id="approveBtn">✓ Approve Definition</button>
    </div>
  </div>`;
}

function buildStep5(data) {
  const report = data.report || data;
  const writerStep = (data.steps || []).find((s) => s.agent === "Writer") || {};
  const detail = writerStep.detail || "";
  const upsertMatch = detail.match(/upsert (\d+)/);
  const linkMatch   = detail.match(/link them to (\d+)/);
  const depMatch    = detail.match(/deprecate (\d+)/);

  const top = (report.conflicts || [])[0];
  const blast = (top || {}).blast_radius || 22;
  const name = friendlyMetric((top || {}).metric || "Active User");

  return `
  <div class="agent-step-inner">
    <img class="step-mascot" src="/static/img/mascot-sticker.png" alt="">
    <div class="agent-chip done-chip">
      <span class="agent-chip-icon">✅</span>
      <span>WRITER &nbsp;·&nbsp; AGENT 5 OF 5</span>
    </div>
    <h2 class="step-title">Make the graph smarter</h2>
    <p class="step-subtitle">Rosetta writes the canonical definition back to DataHub.</p>

    <div class="write-checklist">
      <div class="wc-item"><span class="wc-check">✓</span>
        <div><b>Canonical glossary term created</b><br>
        <span class="wc-sub">${upsertMatch ? upsertMatch[1] : "6"} GlossaryTerm${upsertMatch && upsertMatch[1] === "1" ? "" : "s"} upserted to DataHub</span>
        </div>
      </div>
      <div class="wc-item"><span class="wc-check">✓</span>
        <div><b>Downstream assets linked</b><br>
        <span class="wc-sub">${linkMatch ? linkMatch[1] : blast} assets now point to the canonical term</span>
        </div>
      </div>
      <div class="wc-item"><span class="wc-check">✓</span>
        <div><b>Conflicting definitions retired</b><br>
        <span class="wc-sub">${depMatch ? depMatch[1] : "5"} losing term${depMatch && depMatch[1] === "1" ? "" : "s"} deprecated</span>
        </div>
      </div>
      <div class="wc-item"><span class="wc-check ai-check">🤖</span>
        <div><b>Future AI agents inherit the truth</b><br>
        <span class="wc-sub">${esc(name)} = one agreed definition across all teams</span>
        </div>
      </div>
    </div>

    <div class="write-exports">
      <span class="exports-label">Download full report:</span>
      <a class="chip" href="/api/export/json" target="_blank">JSON</a>
      <a class="chip" href="/api/export/csv"  target="_blank">CSV</a>
      <a class="chip" href="/api/export/md"   target="_blank">Markdown</a>
      <a class="chip" href="/api/export/html" target="_blank">HTML</a>
    </div>

    <div class="write-closing">
      <div class="wc-quote">"The numbers were never wrong.</div>
      <div class="wc-quote">They were never <em>comparable</em>."</div>
      <div class="wc-sub-quote">— Meaning restored.</div>
    </div>
  </div>`;
}

/* ══════════════════════════════════════════════════════════════════════════
   POPULATE WALKTHROUGH STEPS FROM API DATA
   ══════════════════════════════════════════════════════════════════════════ */

function populateSteps(data, dash) {
  const report = data.report || data;

  document.getElementById("wtStep1").innerHTML = buildStep1(data);
  document.getElementById("wtStep2").innerHTML = buildStep2(report);
  document.getElementById("wtStep3").innerHTML = buildStep3(report);
  document.getElementById("wtStep4").innerHTML = buildStep4(report);
  document.getElementById("wtStep5").innerHTML = buildStep5(data);

  // Animate numbers in step 1
  const s = report.summary || {};
  const imp1 = (report.conflicts || [])[0];
  setTimeout(() => {
    animateCount(document.getElementById("s1defs"), 12);
    animateCount(document.getElementById("s1doms"), 6);
    animateCount(document.getElementById("s1assets"), s.assets_at_risk || 63);
  }, 50);

  // Animate numbers in step 3 + draw blast-radius graph
  const top = (report.conflicts || [])[0];
  if (top) {
    const topImp = top.impact || {};
    const blast = top.blast_radius || 0;
    const cost  = topImp.estimated_manual_cost_usd || 0;
    const hours = topImp.manual_reconciliation_hours || 0;
    document.getElementById("wtStep3")._animArgs = { blast, cost, hours };

    // Draw graph into step-3 SVG (needs a tick for the SVG to be in the DOM)
    if (top.impact_graph) {
      setTimeout(() => {
        const s3svg = document.getElementById("s3Graph");
        if (s3svg) drawGraphInto(s3svg, top.impact_graph);
      }, 80);
    }
  }

  // Wire approve button in step 4
  setTimeout(() => {
    const approveBtn = document.getElementById("approveBtn");
    if (approveBtn) {
      approveBtn.addEventListener("click", () => {
        approveBtn.textContent = "✓ Approved";
        approveBtn.disabled = true;
        approveBtn.style.background = "var(--low)";
      });
    }
  }, 100);

  stepsReady = true;
  buildProgressDots();

  // Show developer view toggle
  // (toggleTechBtn removed — nav now in topbar)
}

/* ══════════════════════════════════════════════════════════════════════════
   TECHNICAL VIEW RENDERERS (unchanged from original)
   ══════════════════════════════════════════════════════════════════════════ */

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

function renderSummary(sum) {
  $("#summary").hidden = false;
  animateCount($("#sTotal"), sum.total_conflicts);
  animateCount($("#sHigh"), sum.high);
  animateCount($("#sAssets"), sum.assets_at_risk);
  const imp = sum.impact || {};
  animateCount($("#sCost"), imp.estimated_cost_avoided_usd || 0, { prefix: "$" });
}

const CIRCUMFERENCE = 2 * Math.PI * 32;
function animateRing(ringId, score) {
  const ring = document.getElementById(ringId);
  if (!ring) return;
  requestAnimationFrame(() => {
    ring.style.strokeDashoffset = CIRCUMFERENCE * (1 - score / 100);
  });
}

function renderDashboard(dash) {
  const ts = dash.meta && dash.meta.generated_at
    ? "Generated " + new Date(dash.meta.generated_at).toLocaleTimeString() : "";
  $("#dashTs").textContent = ts;

  const scores = dash.scores || {};
  [
    ["scoreHealthVal", "ringHealth", scores.data_health],
    ["scoreGovVal",    "ringGov",    scores.governance_maturity],
    ["scoreAIVal",     "ringAI",     scores.ai_readiness],
  ].forEach(([valId, ringId, val]) => {
    animateCount(document.getElementById(valId), Math.round(val || 0));
    animateRing(ringId, val || 0);
  });

  animateCount($("#dsCritRisks"), (dash.critical_risks || []).length);
  animateCount($("#dsAssets"), dash.assets_impacted || 0);
  animateCount($("#dsCostAvoided"), dash.cost_avoided_usd || 0, { prefix: "$" });

  const riskList = $("#critRiskList");
  riskList.innerHTML = "";
  (dash.critical_risks || []).forEach((r) => {
    const div = document.createElement("div");
    div.className = `crit-risk-item ${r.severity}`;
    div.innerHTML = `
      <div class="cri-metric">
        <span>${esc(friendlyMetric(r.metric))}</span>
        <span class="badge ${esc(r.severity)}">${esc(r.severity.toUpperCase())}</span>
        <span style="color:var(--muted);font-size:11px;font-family:monospace">blast: ${r.blast_radius}</span>
      </div>
      <div class="cri-desc">${esc(r.description)}</div>`;
    riskList.appendChild(div);
  });

  const actionList = $("#actionList");
  actionList.innerHTML = "";
  (dash.recommended_actions || []).forEach((a) => {
    const div = document.createElement("div");
    div.className = "action-item";
    div.innerHTML = `
      <div class="action-dot ${esc(a.priority)}"></div>
      <div class="action-text">${esc(a.action)}</div>`;
    actionList.appendChild(div);
  });
}

const TYPE_COLOR = {
  metric: "#7c9cff", dataset: "#35c4c9", dashboard: "#f7a03b", model: "#e5484d",
};

function drawGraphInto(svg, graph) {
  svg.innerHTML = "";
  if (!graph || !graph.nodes || !graph.nodes.length) return false;

  const W = svg.clientWidth || svg.parentElement?.clientWidth || 680,
        H = parseInt(svg.getAttribute("data-h") || "340");
  svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
  const nodes = graph.nodes.map((n) => ({ ...n }));
  const idx = Object.fromEntries(nodes.map((n, i) => [n.id, i]));
  const links = graph.edges.map((e) => ({ s: idx[e.source], t: idx[e.target] }));

  nodes.forEach((n, i) => {
    n.x = n.type === "metric" ? W * 0.14 + (Math.random() * 30) : W * 0.4 + Math.random() * W * 0.5;
    n.y = H * 0.1 + (i / nodes.length) * H * 0.8 + (Math.random() * 40 - 20);
    n.vx = 0; n.vy = 0;
  });
  for (let it = 0; it < 320; it++) {
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        let dx = nodes[i].x - nodes[j].x, dy = nodes[i].y - nodes[j].y;
        let d2 = dx * dx + dy * dy + 0.01, d = Math.sqrt(d2);
        const rep = 4200 / d2; dx /= d; dy /= d;
        nodes[i].vx += dx * rep; nodes[i].vy += dy * rep;
        nodes[j].vx -= dx * rep; nodes[j].vy -= dy * rep;
      }
    }
    links.forEach((l) => {
      const a = nodes[l.s], b = nodes[l.t]; if (!a || !b) return;
      let dx = b.x - a.x, dy = b.y - a.y, d = Math.sqrt(dx * dx + dy * dy) + 0.01;
      const f = (d - 90) * 0.02; dx /= d; dy /= d;
      a.vx += dx * f; a.vy += dy * f; b.vx -= dx * f; b.vy -= dy * f;
    });
    nodes.forEach((n) => {
      n.x += n.vx * 0.5; n.y += n.vy * 0.5; n.vx *= 0.82; n.vy *= 0.82;
      n.x = Math.max(30, Math.min(W - 30, n.x)); n.y = Math.max(28, Math.min(H - 28, n.y));
    });
  }
  const NS = "http://www.w3.org/2000/svg";
  links.forEach((l, i) => {
    const a = nodes[l.s], b = nodes[l.t]; if (!a || !b) return;
    const line = document.createElementNS(NS, "line");
    line.setAttribute("x1", a.x); line.setAttribute("y1", a.y);
    line.setAttribute("x2", b.x); line.setAttribute("y2", b.y);
    line.setAttribute("class", "gedge"); line.style.animationDelay = `${i * 0.03}s`;
    svg.appendChild(line);
  });
  nodes.forEach((n, i) => {
    const g = document.createElementNS(NS, "g");
    g.setAttribute("class", "gnode"); g.setAttribute("transform", `translate(${n.x},${n.y})`);
    g.style.animationDelay = `${0.3 + i * 0.04}s`;
    const r = n.type === "metric" ? 13 : n.type === "model" ? 11 : 9;
    const c = document.createElementNS(NS, "circle");
    c.setAttribute("r", r); c.setAttribute("fill", TYPE_COLOR[n.type] || "#889");
    if (n.type === "model") c.setAttribute("class", "pulse");
    const t = document.createElementNS(NS, "text");
    t.setAttribute("y", -r - 5); t.setAttribute("text-anchor", "middle"); t.setAttribute("class", "glabel");
    t.textContent = (n.label || n.id).split("\n")[0].slice(0, 18);
    g.appendChild(c); g.appendChild(t);
    const title = document.createElementNS(NS, "title"); title.textContent = `${n.type}: ${n.label}`; g.appendChild(title);
    svg.appendChild(g);
  });
  return true;
}

// Wrapper for developer-view graph (keeps original call sites working)
function drawGraph(graph, metricName) {
  const svg = $("#graph");
  if (!graph || !graph.nodes || !graph.nodes.length) { $("#graphWrap").hidden = true; return; }
  $("#graphWrap").hidden = false;
  $("#graphTitle").textContent = `Blast radius: ${metricName}`;
  drawGraphInto(svg, graph);
}

function renderAiExplanation(c) {
  const ai = c.ai_explanation; if (!ai) return "";
  return `
    <div class="ai-explain">
      <div class="ai-explain-title">✦ AI Explanation</div>
      <div class="ai-row"><span class="ai-label">Finding</span><span class="ai-val finding">${esc(ai.finding)}</span></div>
      <div class="ai-row"><span class="ai-label">Evidence</span><span class="ai-val evidence">${esc(ai.evidence)}</span></div>
      <div class="ai-row"><span class="ai-label">Impact</span><span class="ai-val impact">${esc(ai.impact)}</span></div>
      <div class="ai-row"><span class="ai-label">Recommend</span><span class="ai-val recommendation">${esc(ai.recommendation)}</span></div>
    </div>`;
}

function renderReconcile(c) {
  const rec = c.proposed_reconciliation; if (!rec) return "";
  const before = rec.before.map((b) =>
    `<div class="before-item"><span class="dot bad"></span><b>${esc(b.domain)}</b>: ${esc(b.definition)}</div>`).join("");
  return `
    <div class="reconcile">
      <div class="rec-col rec-before">
        <div class="rec-h">Before · ${rec.before.length} conflicting definitions</div>${before}
      </div>
      <div class="rec-arrow">→</div>
      <div class="rec-col rec-after">
        <div class="rec-h">After · one canonical term</div>
        <div class="after-item"><span class="dot good"></span>
          <b>${esc(rec.after.display_name)}</b><span class="tag">canonical</span><br>${esc(rec.after.definition)}
        </div>
      </div>
    </div>`;
}

let CURRENT = [];
function renderConflicts(conflicts) {
  CURRENT = conflicts;
  const wrap = $("#conflicts"); wrap.innerHTML = "";
  conflicts.forEach((c, ci) => {
    const rows = c.definitions.map((d) =>
      `<tr><td>${esc(d.domain)}</td><td class="mono">${d.owner ? esc(d.owner) : '<span class="owner-missing">⚠ unassigned</span>'}</td>
       <td>${esc(d.definition_text)}</td><td class="mono">${esc(d.sql_logic)}</td></tr>`).join("");
    const imp = c.impact || {};
    const conf = c.confidence != null ? `${Math.round(c.confidence * 100)}%` : "—";
    const div = document.createElement("div");
    div.className = `conflict ${c.severity}`;
    div.innerHTML = `
      <div class="chead">
        <span class="metric">${esc(friendlyMetric(c.metric))}</span>
        <span class="badge ${c.severity}">${c.severity.toUpperCase()}</span>
        <span class="kind">${esc(c.kind.replace(/_/g, " "))}</span>
        <span class="blast">blast: <b>${c.blast_radius}</b></span>
        <span class="conf">confidence <b>${conf}</b></span>
        <button class="viz-btn" data-ci="${ci}">◆ Visualize</button>
      </div>
      ${renderAiExplanation(c)}
      ${imp.risk_statement ? `<div class="risk">⚠ ${esc(imp.risk_statement)} &nbsp;·&nbsp; est. cost <b>$${(imp.estimated_manual_cost_usd||0).toLocaleString()}</b></div>` : ""}
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
  if (conflicts[0] && conflicts[0].impact_graph) {
    drawGraph(conflicts[0].impact_graph, conflicts[0].metric);
  }
}

/* ══════════════════════════════════════════════════════════════════════════
   RUN DEMO
   ══════════════════════════════════════════════════════════════════════════ */

function setBadge(source) {
  const badge = document.getElementById("modebadge");
  if (!badge) return;
  if (source === "healthcare") {
    badge.textContent = "LIVE · Healthcare DB";
    badge.className = "mode live-healthcare";
  } else if (source === "fiction_retail") {
    badge.textContent = "LIVE · Fiction Retail DB";
    badge.className = "mode live-retail";
  } else {
    badge.textContent = "DEMO MODE · seed data";
    badge.className = "mode demo";
  }
}

async function run(endpoint, opts = {}) {
  const runBtn = $("#runDemo");
  const healthBtn = $("#healthcareBtn");
  const retailBtn = $("#retailBtn");
  if (runBtn) runBtn.disabled = true;
  if (healthBtn) { healthBtn.disabled = true; healthBtn.textContent = "Scanning…"; }
  if (retailBtn) { retailBtn.disabled = true; retailBtn.textContent = "Scanning…"; }

  try {
    const [res, dashRes] = await Promise.all([
      fetch(endpoint),
      fetch("/api/dashboard"),
    ]);
    const data = await res.json();
    const dash = await dashRes.json();
    const report = data.report || data;

    // Populate walkthrough steps
    populateSteps(data, dash);

    // Populate technical view
    if (data.steps) renderSteps(data.steps);
    renderDashboard(dash);
    renderSummary(report.summary);
    renderConflicts(report.conflicts);

    // Store for later
    demoData = data;
    dashData = dash;

    // Update mode badge
    setBadge(data.source || "demo");

    gotoStep(1);

  } catch (e) {
    alert("Error running demo: " + e.message);
  } finally {
    if (runBtn) runBtn.disabled = false;
    if (healthBtn) { healthBtn.disabled = false; healthBtn.textContent = "🏥 Live Healthcare Data"; }
    if (retailBtn) { retailBtn.disabled = false; retailBtn.textContent = "🛍️ Live Retail Data"; }
  }
}

/* ══════════════════════════════════════════════════════════════════════════
   STEP 3 NUMBER ANIMATION — fire when step 3 becomes visible
   ══════════════════════════════════════════════════════════════════════════ */
function animateStep3() {
  const step3 = document.getElementById("wtStep3");
  if (!step3 || !step3._animArgs) return;
  const { blast, cost, hours } = step3._animArgs;
  animateCount(document.getElementById("s3blast"), blast);
  animateCount(document.getElementById("s3cost"), cost, { prefix: "$" });
  animateCount(document.getElementById("s3hours"), hours);
  delete step3._animArgs; // only once
}

/* ══════════════════════════════════════════════════════════════════════════
   WIRE UP ALL BUTTONS
   ══════════════════════════════════════════════════════════════════════════ */

buildProgressDots();

// Run demo
document.getElementById("runDemo")?.addEventListener("click", () => {
  run("/api/demo");
});

// Topbar nav shortcuts
document.getElementById("navRunDemo")?.addEventListener("click", () => {
  run("/api/demo");
});
document.getElementById("navHealthcare")?.addEventListener("click", () => {
  run("/api/healthcare-scan");
});
document.getElementById("navRetail")?.addEventListener("click", () => {
  run("/api/fiction-retail-scan");
});
document.getElementById("navTechView")?.addEventListener("click", () => {
  if (!stepsReady) {
    run("/api/demo").then(showTech);
  } else {
    showTech();
  }
});

// Healthcare live data
document.getElementById("healthcareBtn")?.addEventListener("click", () => {
  run("/api/healthcare-scan");
});

// Fiction-retail live data
document.getElementById("retailBtn")?.addEventListener("click", () => {
  run("/api/fiction-retail-scan");
});

// Read-only scan (in tech view)
document.getElementById("runScan")?.addEventListener("click", async () => {
  showTech();
  const runBtn = document.getElementById("runScan");
  runBtn.disabled = true;
  try {
    const [res, dashRes] = await Promise.all([fetch("/api/scan"), fetch("/api/dashboard")]);
    const data = await res.json(); const dash = await dashRes.json();
    const report = data.report || data;
    populateSteps(data, dash);
    renderDashboard(dash); renderSummary(report.summary); renderConflicts(report.conflicts);
  } finally { runBtn.disabled = false; }
});

// "View Technical Details" from landing
document.getElementById("showTechFromLanding")?.addEventListener("click", () => {
  if (!stepsReady) {
    run("/api/demo").then(showTech);
  } else {
    showTech();
  }
});

// Developer View toggle

// Prev / Next navigation
document.getElementById("prevBtn")?.addEventListener("click", () => {
  if (currentStep > 0) gotoStep(currentStep - 1);
});

document.getElementById("homeBtn")?.addEventListener("click", () => {
  gotoStep(0);
});

document.getElementById("nextBtn")?.addEventListener("click", () => {
  if (currentStep < 5) {
    gotoStep(currentStep + 1);
    if (currentStep === 3) animateStep3();
  } else {
    showTech(); // "View Full Report" on step 5
  }
});

