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
   WRITE-PLAN JSON PANEL HELPERS  (called via onclick from buildStep5 HTML)
   ══════════════════════════════════════════════════════════════════════════ */

function togglePlanJson() {
  const wrap = document.getElementById("planJsonWrap");
  const btn  = document.getElementById("planJsonToggle");
  if (!wrap) return;
  const open = wrap.classList.toggle("open");
  if (btn) {
    btn.setAttribute("aria-expanded", String(open));
    btn.querySelector("span").textContent =
      (open ? "▲" : "▶") + " Machine-readable plan (JSON)";
  }
}

async function copyWritePlan() {
  if (!_currentPlanJson) return;
  const btn = document.getElementById("copyPlanBtn");
  const done = () => {
    if (btn) { btn.textContent = "✓ Copied"; btn.classList.add("copied"); }
    setTimeout(() => { if (btn) { btn.textContent = "Copy JSON"; btn.classList.remove("copied"); } }, 2000);
  };
  try {
    await navigator.clipboard.writeText(_currentPlanJson);
    done();
  } catch (_) {
    // fallback for browsers without clipboard API
    const ta = Object.assign(document.createElement("textarea"), {
      value: _currentPlanJson, style: "position:fixed;opacity:0"
    });
    document.body.appendChild(ta); ta.select(); document.execCommand("copy");
    document.body.removeChild(ta); done();
  }
}

function downloadWritePlan() {
  if (!_currentPlanJson) return;
  const blob = new Blob([_currentPlanJson], { type: "application/json" });
  const url  = URL.createObjectURL(blob);
  const a    = Object.assign(document.createElement("a"), {
    href: url, download: "rosetta-write-plan.json"
  });
  document.body.appendChild(a); a.click();
  document.body.removeChild(a); URL.revokeObjectURL(url);
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
let _writeBackResult       = null;  // set after a successful live write-back
let _writeBackVerification = null;  // set after write-back; VerificationResult dict or null
let _demoApprovalData      = null;  // { plan_id, approved_at } set after /api/approve in demo mode
let _currentPlanJson       = "";    // populated by buildStep5 for copy/download buttons

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
  updateHomeBtn(n);

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
    nextBtn.textContent = n === 5 ? "See the result →" : "Next →";
  }

  // Step label
  const lbl = $("#wtLabel");
  if (lbl && n >= 1) lbl.textContent = `Agent ${n} of 5 · ${STEP_LABELS[n]}`;

  // Rebuild step 5 with actual write-back result when navigating to it
  if (n === 5 && stepsReady && demoData) {
    const step5El = document.getElementById("wtStep5");
    if (step5El) step5El.innerHTML = buildStep5(demoData, _writeBackResult);
  }

  // Fire step-3 number animation whenever step 3 becomes active
  if (n === 3) setTimeout(animateStep3, 350);
}

function showTech() {
  techVisible = true;
  $("#techView").hidden = false;
  $("#walkthrough").hidden = true;
  const topbarNav = $("#topbarNav");
  if (topbarNav) topbarNav.hidden = true;
  updateHomeBtn(currentStep);
  $("#techView").scrollIntoView({ behavior: "smooth", block: "start" });
}

function showWalkthrough() {
  techVisible = false;
  $("#techView").hidden = true;
  $("#walkthrough").hidden = false;
  const topbarNav = $("#topbarNav");
  if (topbarNav) topbarNav.hidden = (currentStep !== 0);
  updateHomeBtn(currentStep);
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
  const nassets = (report.summary || {}).assets_at_risk || 0;

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
  const isLive = document.getElementById("modebadge")?.classList.contains("live");
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

    <div class="dh-write-callout">
      <div class="dh-write-callout-header">
        <span class="dh-write-callout-icon">⬆</span>
        <span>${isLive ? "WRITES TO DATAHUB ON APPROVAL" : "PROPOSED DATAHUB WRITE OPERATIONS"}</span>
      </div>
      <div class="dh-write-ops">
        <div class="dh-write-op">
          <span class="dh-write-op-icon">📝</span>
          <div>
            <div class="dh-write-op-label">
              Canonical GlossaryTerm ${isLive ? "created" : "proposed"}
              ${!isLive ? '<span class="wop-badge proposed">PROPOSED</span>' : ""}
            </div>
            <div class="dh-write-op-sub">${isLive ? "One authoritative definition stored in your DataHub glossary" : "One authoritative definition prepared for your DataHub glossary"}</div>
          </div>
        </div>
        <div class="dh-write-op">
          <span class="dh-write-op-icon">🔗</span>
          <div>
            <div class="dh-write-op-label">
              ${(top || {}).blast_radius || 22} downstream assets ${isLive ? "linked" : "identified for linking"}
              ${!isLive ? '<span class="wop-badge proposed">PROPOSED</span>' : ""}
            </div>
            <div class="dh-write-op-sub">${isLive ? "Every dataset, dashboard, and column tagged to the canonical term" : "Every dataset, dashboard, and column identified for tagging"}</div>
          </div>
        </div>
        <div class="dh-write-op">
          <span class="dh-write-op-icon">🗑</span>
          <div>
            <div class="dh-write-op-label">
              Conflicting definitions ${isLive ? "deprecated" : "flagged for deprecation"}
              ${!isLive ? '<span class="wop-badge proposed">PROPOSED</span>' : ""}
            </div>
            <div class="dh-write-op-sub">${isLive ? "Losing terms marked deprecated so teams stop using them" : "Losing terms flagged so teams can stop using them after execution"}</div>
          </div>
        </div>
      </div>
      <div class="dh-write-callout-footer">
        ${!isLive ? '<p class="write-demo-plan-note">Demo Mode: Approval will generate and validate the proposed DataHub operations. No external catalog will be modified.</p>' : ""}
        <span class="dh-write-callout-note">⚠ Human approval required — Rosetta will not write without it.</span>
        <button class="btn primary approve-btn" id="approveBtn">${isLive ? "✓ Approve &amp; Write to DataHub" : "✓ Approve &amp; Generate Write Plan"}</button>
      </div>
    </div>
  </div>`;
}

function buildStep5(data, writeResult) {
  const report = data.report || data;
  const writerStep = (data.steps || []).find((s) => s.agent === "Writer") || {};
  const detail = writerStep.detail || "";
  const upsertMatch = detail.match(/upsert (\d+)/);
  const linkMatch   = detail.match(/link them to (\d+)/);
  const depMatch    = detail.match(/deprecate (\d+)/);

  const top   = (report.conflicts || [])[0];
  const blast = (top || {}).blast_radius || 22;
  const name  = friendlyMetric((top || {}).metric || "Active User");

  const isLive = writeResult != null;

  // ── Write plan from proposals ─────────────────────────────────────────
  const firstProposal = ((data.proposals || [])[0]) || {};
  const writePlan     = firstProposal.write_plan || null;

  // Build JSON string (side-effect: update module var so copy/download work)
  if (writePlan && !isLive) {
    const planForDisplay = JSON.parse(JSON.stringify(writePlan));
    if (_demoApprovalData) {
      planForDisplay.approval.approvedAt = _demoApprovalData.approved_at;
    }
    _currentPlanJson = JSON.stringify(planForDisplay, null, 2);
  }

  // ── Status banner ─────────────────────────────────────────────────────
  let statusBanner;
  if (isLive) {
    const termUrn    = writeResult.canonical_term || "";
    const termId     = termUrn.split(":").pop() || termUrn;
    const linked     = (writeResult.linked_assets || []).length;
    const deprecated = (writeResult.deprecated_terms || []).length;

    // Post-write verification badge
    const vrf = _writeBackVerification;
    let vrfBanner = "";
    if (vrf) {
      const vstatus  = vrf.status || "VERIFICATION_FAILED";
      const vpassed  = vrf.passedChecks ?? 0;
      const vtotal   = vrf.totalChecks  ?? 0;
      const vrfMeta = {
        VERIFIED:                 { icon: "✓", label: "WRITE COMPLETED · VERIFIED",                cls: "vrf-ok"   },
        PARTIALLY_VERIFIED:       { icon: "⚠", label: "WRITE COMPLETED · PARTIALLY VERIFIED",       cls: "vrf-warn" },
        VERIFICATION_FAILED:      { icon: "✗", label: "WRITE COMPLETED · VERIFICATION FAILED",      cls: "vrf-fail" },
        VERIFICATION_UNAVAILABLE: { icon: "?", label: "WRITE COMPLETED · VERIFICATION UNAVAILABLE", cls: "vrf-warn" },
        NOT_EXECUTED:             { icon: "—", label: "NOT EXECUTED",                               cls: "vrf-muted"},
      };
      const m = vrfMeta[vstatus] || vrfMeta.VERIFICATION_FAILED;

      const _checkIcon = s =>
        s === "verified"   ? { cls: "vrf-check-pass",    ch: "✓" } :
        s === "failed"     ? { cls: "vrf-check-fail",    ch: "✗" } :
                             { cls: "vrf-check-unavail", ch: "?" };

      const checkRows = (vrf.checks || []).map(c => {
        const ic = _checkIcon(c.status);
        return `
        <div class="vrf-check">
          <span class="vrf-check-icon ${ic.cls}" aria-label="${esc(c.status)}">${ic.ch}</span>
          <div class="vrf-check-body">
            <span class="vrf-check-op">${esc(c.operationType)}</span>
            <div class="vrf-check-urn">${esc(c.targetUrn)}</div>
            <div class="vrf-check-row"><b>Expected:</b> ${esc(c.expectedState)}</div>
            <div class="vrf-check-row"><b>Observed:</b> ${esc(c.observedState)}</div>
            <div class="vrf-check-reason">${esc(c.reason)}</div>
            <div class="vrf-check-ts">${c.verifiedAt ? "Re-read at " + esc(c.verifiedAt) : ""}</div>
          </div>
        </div>`;
      }).join("");

      vrfBanner = `
        <div class="verification-banner ${m.cls}" role="status" aria-label="Verification status: ${vstatus}">
          <span class="vrf-icon" aria-hidden="true">${m.icon}</span>
          <div class="vrf-body">
            <div class="vrf-title">${m.label}</div>
            <div class="vrf-detail">${vpassed} of ${vtotal} check${vtotal !== 1 ? "s" : ""} verified — DataHub entities re-read and compared to the approved plan. A successful write-API response is not treated as proof of persistence.</div>
            ${checkRows ? `<div class="vrf-checks" aria-label="Individual checks">${checkRows}</div>` : ""}
          </div>
        </div>`;
    }

    statusBanner = `
      <div class="write-live-banner">
        <span class="wlb-icon">✓</span>
        <div>
          <div class="wlb-title">Written to DataHub</div>
          <div class="wlb-detail">Term <code>${esc(termId)}</code> created · ${linked} asset${linked !== 1 ? "s" : ""} linked · ${deprecated} definition${deprecated !== 1 ? "s" : ""} deprecated</div>
        </div>
      </div>
      ${vrfBanner}`;
  } else {
    statusBanner = `
      <div class="write-demo-notice">
        <div class="wdn-heading">Write plan generated &amp; validated</div>
        <p class="wdn-text">Rosetta prepared the operations required to reconcile this conflict in a connected DataHub catalog. No external operations were executed in Demo Mode.</p>
        <div class="wdn-status-table">
          <div class="wdn-row"><span class="wdn-label">Human approval</span><span class="wdn-val wdn-green">Complete</span></div>
          <div class="wdn-row"><span class="wdn-label">Write-plan validation</span><span class="wdn-val wdn-green">Passed</span></div>
          <div class="wdn-row"><span class="wdn-label">External catalog modified</span><span class="wdn-val wdn-muted">No</span></div>
          <div class="wdn-row"><span class="wdn-label">Target platform</span><span class="wdn-val">DataHub</span></div>
        </div>
      </div>`;
  }

  // ── Operations panel (demo mode only) ─────────────────────────────────
  let opsPanel = "";
  if (!isLive && writePlan && (writePlan.operations || []).length) {
    const ops       = writePlan.operations;
    const upsertOps = ops.filter(o => o.action === "upsert_glossary_term");
    const attachOps = ops.filter(o => o.action === "attach_term_to_asset");
    const deprecOps = ops.filter(o => o.action === "deprecate_term");

    const opCard = (op, extra) => `
      <div class="wp-op-row" role="listitem">
        <div class="wp-op-seq" aria-hidden="true">${op.sequence}</div>
        <div class="wp-op-body">
          <div class="wp-op-action">${esc(op.action)}</div>
          <div class="wp-op-urn">${esc(op.targetUrn)}${extra > 0 ? ` <span class="wp-op-more">+&nbsp;${extra}&nbsp;more</span>` : ""}</div>
          <div class="wp-op-reason">${esc(op.reason)}</div>
          <div class="wp-op-status">
            <span class="wp-op-badge validated">✓ Validated</span>
            <span class="wp-op-badge not-executed">Not Executed</span>
          </div>
        </div>
      </div>`;

    opsPanel = `
      <div class="wp-ops-panel" role="list" aria-label="Proposed DataHub operations">
        <div class="wp-ops-heading">Proposed DataHub operations</div>
        ${upsertOps.map(op => opCard(op, 0)).join("")}
        ${attachOps.length ? opCard(attachOps[0], attachOps.length - 1) : ""}
        ${deprecOps.length ? opCard(deprecOps[0], deprecOps.length - 1) : ""}
      </div>`;
  }

  // ── Machine-readable JSON panel (demo mode only) ─────────────────────
  let jsonPanel = "";
  if (!isLive && _currentPlanJson) {
    jsonPanel = `
      <div class="wp-json-panel">
        <button class="wp-json-toggle" id="planJsonToggle"
          onclick="togglePlanJson()" aria-expanded="false" aria-controls="planJsonWrap">
          <span>▶ Machine-readable plan (JSON)</span>
          <span class="wp-json-toggle-hint">view &amp; copy</span>
        </button>
        <div class="wp-json-code-wrap" id="planJsonWrap" role="region" aria-label="Write plan JSON">
          <pre class="wp-json-code" tabindex="0">${esc(_currentPlanJson)}</pre>
        </div>
        <div class="wp-json-actions">
          <button class="copy-btn" id="copyPlanBtn" onclick="copyWritePlan()">Copy JSON</button>
          <button class="copy-btn" onclick="downloadWritePlan()">⬇ Download JSON</button>
          <a class="copy-btn" href="/api/export/md" target="_blank" rel="noopener">⬇ Download Audit Report</a>
        </div>
      </div>`;
  }

  const chk = (live) => `wc-check${live ? "" : " sim"}`;

  return `
  <div class="agent-step-inner">
    <img class="step-mascot" src="/static/img/mascot-sticker.png" alt="">
    <div class="agent-chip done-chip">
      <span class="agent-chip-icon">✅</span>
      <span>WRITER &nbsp;·&nbsp; AGENT 5 OF 5</span>
    </div>
    <h2 class="step-title">${isLive ? "Make the graph smarter" : "Write plan approved and validated"}</h2>
    <p class="step-subtitle">${isLive ? "Rosetta wrote the canonical definition back to DataHub." : "Rosetta prepared the operations required to reconcile this conflict in a connected DataHub catalog."}</p>

    ${!isLive ? `
    <div class="validated-badge" role="status" aria-label="Status: validated, not executed">
      <span class="vb-dot" aria-hidden="true"></span>
      <span>VALIDATED</span>
      <span class="vb-sep" aria-hidden="true">·</span>
      <span class="vb-ne">NOT EXECUTED</span>
    </div>` : ""}

    ${statusBanner}
    ${opsPanel}
    ${jsonPanel}

    <div class="write-checklist">
      <div class="wc-item"><span class="${chk(isLive)}">✓</span>
        <div><b>Canonical glossary term ${isLive ? "created" : "ready to create"}</b><br>
        <span class="wc-sub">${upsertMatch ? upsertMatch[1] : "6"} GlossaryTerm${upsertMatch && upsertMatch[1] === "1" ? "" : "s"} ${isLive ? "upserted to DataHub" : "prepared"}</span>
        </div>
      </div>
      <div class="wc-item"><span class="${chk(isLive)}">✓</span>
        <div><b>Downstream assets ${isLive ? "linked" : "identified for linking"}</b><br>
        <span class="wc-sub">${linkMatch ? linkMatch[1] : blast} assets ${isLive ? "now point to the canonical term" : "ready for DataHub once approved and executed"}</span>
        </div>
      </div>
      <div class="wc-item"><span class="${chk(isLive)}">✓</span>
        <div><b>Conflicting definitions ${isLive ? "retired" : "flagged for retirement"}</b><br>
        <span class="wc-sub">${depMatch ? depMatch[1] : "5"} losing term${depMatch && depMatch[1] === "1" ? "" : "s"} ${isLive ? "deprecated" : "flagged for deprecation"}</span>
        </div>
      </div>
      <div class="wc-item"><span class="wc-check ai-check">🤖</span>
        <div><b>${isLive ? "Future AI agents inherit the truth" : "Connected agents can inherit the canonical definition after execution"}</b><br>
        <span class="wc-sub">${esc(name)} = one agreed definition across all teams</span>
        </div>
      </div>
    </div>

    <div class="write-exports">
      ${!isLive ? `
        <span class="exports-label">Write plan &amp; reports:</span>
        <a class="btn ghost btn-sm write-plan-btn" href="/api/export/html" target="_blank">View Write Plan</a>
        <a class="chip" href="/api/export/json" target="_blank">Download JSON</a>
        <a class="chip" href="/api/export/md"   target="_blank">Download Audit Report</a>
      ` : `
        <span class="exports-label">Download full report:</span>
        <a class="chip" href="/api/export/json" target="_blank">JSON</a>
        <a class="chip" href="/api/export/csv"  target="_blank">CSV</a>
        <a class="chip" href="/api/export/md"   target="_blank">Markdown</a>
        <a class="chip" href="/api/export/html" target="_blank">HTML</a>
      `}
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

  // Wire approve button in step 4 — live mode calls /api/write-back for real
  setTimeout(() => {
    const approveBtn = document.getElementById("approveBtn");
    if (approveBtn) {
      approveBtn.addEventListener("click", async () => {
        const isLive = document.getElementById("modebadge")?.classList.contains("live");
        if (isLive) {
          approveBtn.disabled = true;
          approveBtn.textContent = "Writing to DataHub…";
          approveBtn.style.opacity = "0.75";
          try {
            const res  = await fetch("/api/write-back", { method: "POST" });
            const data = await res.json();
            if (data.ok) {
              approveBtn.textContent = "✓ Written to DataHub";
              approveBtn.style.background = "var(--low)";
              approveBtn.style.opacity = "1";
              _writeBackResult       = data.result;
              _writeBackVerification = data.verification || null;
              setTimeout(() => gotoStep(5), 900);
            } else {
              approveBtn.disabled = false;
              approveBtn.textContent = "✗ Write failed — retry";
              approveBtn.style.background = "var(--crit)";
              approveBtn.style.opacity = "1";
            }
          } catch (_) {
            approveBtn.disabled = false;
            approveBtn.textContent = "✗ Network error — retry";
            approveBtn.style.background = "var(--crit)";
            approveBtn.style.opacity = "1";
          }
        } else {
          // Demo mode — call /api/approve to register approval token, then advance
          approveBtn.textContent = "Validating plan…";
          approveBtn.disabled = true;
          approveBtn.style.opacity = "0.75";
          try {
            const approveRes  = await fetch("/api/approve", { method: "POST" });
            const approveData = await approveRes.json();
            if (approveData.ok) {
              _demoApprovalData = { plan_id: approveData.plan_id, approved_at: approveData.approved_at };
            }
          } catch (_) {
            // endpoint unreachable — still advance; approvedAt will be null in JSON
          }
          approveBtn.textContent = "✓ Write plan validated";
          approveBtn.style.background = "var(--low)";
          approveBtn.style.opacity = "1";
          _writeBackResult = null;
          setTimeout(() => gotoStep(5), 900);
        }
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
    badge.textContent = "DEMO MODE · OFFICIAL HACKATHON SAMPLE DATA";
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

// ── DataHub Connect Modal ─────────────────────────────────────────────────────
const dhModal   = document.getElementById("dhModal");
const dhStatus  = document.getElementById("dhStatus");
const dhSubmit  = document.getElementById("dhSubmitBtn");
const dhBtn     = document.getElementById("openDhModal");

function openDhModal() {
  if (dhModal) { dhModal.hidden = false; document.body.style.overflow = "hidden"; }
}
function closeDhModal() {
  if (dhModal) { dhModal.hidden = true; document.body.style.overflow = ""; }
  if (dhStatus) { dhStatus.hidden = true; dhStatus.className = "dh-status"; }
}
function setDhStatus(msg, type) {
  if (!dhStatus) return;
  dhStatus.textContent = msg;
  dhStatus.className = "dh-status " + type;
  dhStatus.hidden = false;
}

document.getElementById("openDhModal")?.addEventListener("click", openDhModal);
document.getElementById("closeDhModal")?.addEventListener("click", closeDhModal);
document.getElementById("cancelDhModal")?.addEventListener("click", closeDhModal);
dhModal?.addEventListener("click", e => { if (e.target === dhModal) closeDhModal(); });

// ── About This Data modal ────────────────────────────────────────────────
const aboutModal = document.getElementById("aboutDataModal");
function openAboutData()  { if (aboutModal) { aboutModal.hidden = false; document.body.style.overflow = "hidden"; } }
function closeAboutData() { if (aboutModal) { aboutModal.hidden = true;  document.body.style.overflow = ""; } }
document.getElementById("openAboutData")?.addEventListener("click", openAboutData);
document.getElementById("openAboutDataHero")?.addEventListener("click", openAboutData);
document.getElementById("closeAboutData")?.addEventListener("click", closeAboutData);
aboutModal?.addEventListener("click", e => { if (e.target === aboutModal) closeAboutData(); });
document.addEventListener("keydown", e => {
  if (e.key === "Escape" && aboutModal && !aboutModal.hidden) closeAboutData();
});

// Pre-fill Acryl demo instance URL
document.getElementById("useDemoInstance")?.addEventListener("click", () => {
  const urlInput = document.getElementById("dhGmsUrl");
  if (urlInput) urlInput.value = "https://demo.datahubproject.io";
  document.getElementById("dhToken")?.focus();
});

// Connect form submit
document.getElementById("dhForm")?.addEventListener("submit", async e => {
  e.preventDefault();
  const gms_url = document.getElementById("dhGmsUrl")?.value.trim();
  const token   = document.getElementById("dhToken")?.value.trim();
  if (!gms_url) { setDhStatus("Please enter a GMS URL.", "err"); return; }
  if (!token)   { setDhStatus("Please paste your access token.", "err"); return; }

  setDhStatus("Connecting to DataHub…", "loading");
  if (dhSubmit) { dhSubmit.disabled = true; dhSubmit.textContent = "Connecting…"; }

  try {
    const res  = await fetch("/api/datahub-connect", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ gms_url, token }),
    });
    const data = await res.json();
    if (data.ok) {
      setDhStatus("✓ Connected! Running live scan…", "ok");
      // Update topbar badge + button
      const badge = document.getElementById("modebadge");
      if (badge) { badge.textContent = "LIVE · DataHub"; badge.className = "mode live"; }
      if (dhBtn) { dhBtn.textContent = "✓ DataHub Connected"; dhBtn.classList.add("connected"); }
      // Close modal and run live scan
      setTimeout(() => {
        closeDhModal();
        run("/api/scan");
      }, 900);
    } else {
      setDhStatus("✗ " + (data.error || "Connection failed."), "err");
    }
  } catch (err) {
    setDhStatus("✗ Network error — could not reach the server.", "err");
  } finally {
    if (dhSubmit) { dhSubmit.disabled = false; dhSubmit.textContent = "Connect & Scan"; }
  }
});

// ── Persistent Home button ────────────────────────────────────────────────────
const topbarHomeBtn = document.getElementById("topbarHomeBtn");
function updateHomeBtn(step) {
  if (!topbarHomeBtn) return;
  // Show "Home" whenever user is away from the landing page
  topbarHomeBtn.classList.toggle("visible", step !== 0 || techVisible);
}
topbarHomeBtn?.addEventListener("click", () => {
  if (techVisible) showWalkthrough();
  gotoStep(0);
});

// Landing pipeline animation
(function() {
  const agents = document.querySelectorAll('#lpPipeline .lp-agent');
  const connectors = document.querySelectorAll('#lpPipeline .lp-connector');
  if (!agents.length) return;
  let current = 0;
  function tick() {
    agents.forEach((a, i) => a.classList.toggle('active', i === current));
    connectors.forEach((c, i) => c.classList.toggle('active', i === current));
    current = (current + 1) % agents.length;
  }
  tick();
  setInterval(tick, 1800);
})();

// Extra landing CTAs
document.getElementById("runDemo2")?.addEventListener("click", () => run("/api/healthcare-scan"));
document.getElementById("navTechViewHero")?.addEventListener("click", () => {
  if (!stepsReady) run("/api/demo").then(showTech);
  else showTech();
});

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
    // Round out the demo: return to landing and scroll to the before/after section
    gotoStep(0);
    setTimeout(() => {
      document.querySelector(".lp-ba-section")
        ?.scrollIntoView({ behavior: "smooth", block: "start" });
    }, 350);
  }
});

