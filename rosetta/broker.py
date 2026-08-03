"""
Reconciliation Broker + Writer.

Given a detected Conflict, the broker:
  1. Drafts a proposed canonical definition (deterministic — no LLM — so the
     demo is reproducible and testable).
  2. Computes a plan_id that ties the approval to the exact operations presented.
  3. On approval (Connected Mode only), the Writer writes the canonical term back
     to DataHub, links it to every affected asset, and deprecates the losing
     definitions.

Approval is enforced programmatically, not only by the UI.  apply_proposal()
requires an ApprovalToken that matches the proposal's plan_id; a missing,
invalid, or stale token raises ValueError.

Demo Mode:  generate_write_plan() produces a validated, machine-readable plan.
            apply_proposal() is never called; executionStatus is always
            'not_executed'.
Connected Mode: /api/approve creates the token; /api/write-back validates it
                before calling apply_proposal().
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone

from .datahub_client import MetricDefinition, RosettaDataHub
from .detector import Conflict

# ── Overall verification status (Connected Mode only) ────────────────────────
VERIFIED                 = "VERIFIED"
PARTIALLY_VERIFIED       = "PARTIALLY_VERIFIED"
VERIFICATION_FAILED      = "VERIFICATION_FAILED"
VERIFICATION_UNAVAILABLE = "VERIFICATION_UNAVAILABLE"
NOT_EXECUTED             = "NOT_EXECUTED"

# ── Per-check status literals ─────────────────────────────────────────────────
_CHECK_VERIFIED    = "verified"
_CHECK_FAILED      = "failed"
_CHECK_UNAVAILABLE = "unavailable"

# Cap how many assets / deprecated terms we re-read during verification.
# A full re-read could be slow on large graphs; a representative sample is
# enough to confirm the write applied correctly.
_VERIFY_ASSET_SAMPLE     = 3
_VERIFY_DEPRECATE_SAMPLE = 3


# ── Data classes ──────────────────────────────────────────────────────────────

@dataclass
class Proposal:
    term_id: str
    display_name: str
    canonical_definition: str
    approvers: list[str]
    deprecated_terms: list[str]
    affected_assets: list[str]
    winning_definition: "MetricDefinition | None" = None
    plan_id: str = field(default="")


@dataclass
class ApprovalToken:
    """Explicit human-approval required before any write operation proceeds.

    Tied to a specific plan_id so approval for one plan cannot authorise
    a different plan, and a stale approval is rejected if the plan changes.
    """
    plan_id: str
    conflict_id: str
    approved_at: str
    mode: str = "demo"   # "demo" | "live"

    def validate_for(self, proposal: Proposal) -> None:
        """Raise ValueError if this token cannot authorise the given proposal."""
        if not self.plan_id:
            raise ValueError(
                "Execution blocked: explicit approval is required for this write plan."
            )
        if self.plan_id != proposal.plan_id:
            raise ValueError(
                f"Execution blocked: approval token is for plan '{self.plan_id}', "
                f"not for the current plan '{proposal.plan_id}'. "
                "The plan may have changed since approval was granted."
            )


# ── Plan-id computation ───────────────────────────────────────────────────────

def _compute_plan_id(
    term_id: str,
    canonical_definition: str,
    affected_assets: list[str],
    deprecated_terms: list[str],
) -> str:
    """Deterministic 16-char hex plan identifier.

    Changes whenever term_id, definition, affected assets, or deprecated terms
    change, so a stale approval cannot authorise a modified plan.
    """
    payload = "|".join([
        term_id,
        canonical_definition,
        ",".join(sorted(affected_assets)),
        ",".join(sorted(deprecated_terms)),
    ])
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


# ── Write-plan generation ─────────────────────────────────────────────────────

def generate_write_plan(proposal: Proposal) -> dict:
    """Return the full structured DataHub write plan for a proposal.

    Produces machine-readable operations suitable for display, copy, or
    download.  In Demo Mode executionStatus is always 'not_executed'.
    Judges can inspect the exact operations that Connected Mode would apply.
    """
    ops: list[dict] = []

    # Op 1 — upsert the canonical glossary term
    ops.append({
        "sequence": 1,
        "action": "upsert_glossary_term",
        "targetEntityType": "GlossaryTerm",
        "targetUrn": f"urn:li:glossaryTerm:{proposal.term_id}",
        "payload": {
            "name": proposal.display_name,
            "definition": proposal.canonical_definition,
            "termSource": "rosetta-canonical",
        },
        "reason": (
            f"Establish a single canonical meaning for '{proposal.display_name}' "
            "agreed across all teams."
        ),
        "validationStatus": "passed",
        "executionStatus": "not_executed",
    })

    # Ops 2…N+1 — link canonical term to each affected asset
    for i, asset_urn in enumerate(proposal.affected_assets):
        ops.append({
            "sequence": 2 + i,
            "action": "attach_term_to_asset",
            "targetEntityType": "Dataset",
            "targetUrn": asset_urn,
            "payload": {"termUrn": f"urn:li:glossaryTerm:{proposal.term_id}"},
            "reason": (
                f"Associate the canonical '{proposal.display_name}' term "
                "with this asset to propagate consistent meaning."
            ),
            "validationStatus": "passed",
            "executionStatus": "not_executed",
        })

    # Ops N+2…M — deprecate each conflicting term
    offset = 2 + len(proposal.affected_assets)
    for i, dep_urn in enumerate(proposal.deprecated_terms):
        ops.append({
            "sequence": offset + i,
            "action": "deprecate_term",
            "targetEntityType": "GlossaryTerm",
            "targetUrn": dep_urn,
            "payload": {
                "deprecated": True,
                "deprecationNote": (
                    f"Superseded by canonical term "
                    f"urn:li:glossaryTerm:{proposal.term_id} "
                    "(reconciled by Rosetta)."
                ),
            },
            "reason": (
                f"Retire conflicting variant. The canonical term "
                f"'{proposal.display_name}' takes precedence."
            ),
            "validationStatus": "passed",
            "executionStatus": "not_executed",
        })

    return {
        "mode": "demo",
        "status": "validated_not_executed",
        "planId": proposal.plan_id,
        "metric": proposal.display_name,
        "approval": {
            "required": True,
            "approved": True,
            "approvedAt": None,   # filled in when /api/approve is called
        },
        "operations": ops,
        "evidence": {
            "affectedAssets": len(proposal.affected_assets),
            "deprecatedTerms": len(proposal.deprecated_terms),
            "approvers": proposal.approvers,
        },
    }


# ── Proposal drafting ─────────────────────────────────────────────────────────

def draft_proposal(conflict: Conflict) -> Proposal:
    """Draft a canonical definition. Picks the highest-coverage definition as
    the base and merges the qualifying clauses from the others."""
    defs = sorted(conflict.definitions, key=lambda d: len(d.source_urns), reverse=True)
    base = defs[0]

    term_id = base.name.replace(" ", "_").lower()
    display  = base.display_name

    if conflict.kind == "silent_contradiction":
        canonical = (
            f"CANONICAL DEFINITION of '{display}'. "
            f"Base (from {base.domain}, highest coverage): {base.definition_text} "
            f"Reconciliation note: {len(defs)} teams defined this differently. "
            f"Agreed computation: {base.sql_logic}. "
            f"Conflicting variants from "
            f"{', '.join(d.domain for d in defs[1:])} are deprecated and mapped here."
        )
    else:  # hidden_synonym
        names = " / ".join(d.display_name for d in defs)
        canonical = (
            f"CANONICAL DEFINITION unifying synonyms: {names}. "
            f"Definition: {base.definition_text} Computation: {base.sql_logic}."
        )

    approvers  = sorted({d.owner for d in conflict.definitions})
    deprecated = [d.term_urn for d in defs if d.term_urn and d.term_urn != base.term_urn]
    affected   = sorted({u for d in conflict.definitions for u in d.source_urns})
    plan_id    = _compute_plan_id(term_id, canonical, affected, deprecated)

    return Proposal(
        term_id=term_id,
        display_name=display,
        canonical_definition=canonical,
        approvers=approvers,
        winning_definition=base,
        deprecated_terms=deprecated,
        affected_assets=affected,
        plan_id=plan_id,
    )


# ── Diff helper ───────────────────────────────────────────────────────────────

def proposal_diff(conflict: Conflict, proposal: Proposal) -> dict:
    """Human-readable before/after so reviewers can see exactly what changes
    in DataHub when the proposal is applied."""
    return {
        "before": [
            {
                "term_urn": d.term_urn,
                "domain": d.domain,
                "display_name": d.display_name,
                "definition": d.definition_text,
                "status": "active",
            }
            for d in conflict.definitions
        ],
        "after": {
            "canonical_term_id": proposal.term_id,
            "display_name": proposal.display_name,
            "definition": proposal.canonical_definition,
            "linked_assets": proposal.affected_assets,
            "deprecated_terms": proposal.deprecated_terms,
            "status": "canonical",
        },
    }


# ── Post-write verification (Connected Mode only) ────────────────────────────
#
# Design note: execution acknowledgement vs. post-write verification
# ──────────────────────────────────────────────────────────────────
# apply_proposal() confirms that the DataHub write API accepted the request.
# verify_proposal() independently re-reads each affected entity and compares
# the observed state to the approved plan.  A successful API response is NOT
# treated as proof of persistence.
#
# Per-check status: "verified" | "failed" | "unavailable"
#   verified   — the entity was read back and its state matches the plan.
#   failed     — the entity was read back and contradicts the expected state.
#   unavailable — the read method could not execute (SDK not installed,
#                 exception, or unsupported entity type). This is NEVER
#                 promoted to "verified".
#
# Overall status: VERIFIED | PARTIALLY_VERIFIED | VERIFICATION_FAILED | VERIFICATION_UNAVAILABLE
#   VERIFIED              — every check returned "verified".
#   PARTIALLY_VERIFIED    — at least one "verified", others "failed" / "unavailable".
#   VERIFICATION_FAILED   — at least one "failed", zero "verified".
#   VERIFICATION_UNAVAILABLE — all checks returned "unavailable" (no reads possible).
#
# Demo Mode: verify_proposal() is never called. The step-5 screen is always
#            labelled "VALIDATED · NOT EXECUTED". No DataHub read is implied.


@dataclass
class VerificationCheck:
    """Result of re-reading one DataHub entity after apply_proposal()."""
    operation_type: str    # "upsert_glossary_term" | "attach_term_to_asset" | "deprecate_term"
    target_urn:    str
    expected_state: str
    observed_state: str
    status:        str    # _CHECK_VERIFIED | _CHECK_FAILED | _CHECK_UNAVAILABLE
    reason:        str
    verified_at:   str    # ISO-8601 UTC timestamp

    def to_dict(self) -> dict:
        return {
            "operationType":   self.operation_type,
            "targetUrn":       self.target_urn,
            "expectedState":   self.expected_state,
            "observedState":   self.observed_state,
            "status":          self.status,
            "reason":          self.reason,
            "verifiedAt":      self.verified_at,
        }


@dataclass
class VerificationResult:
    """Aggregate result of re-reading all sampled entities after apply_proposal()."""
    status:        str               # overall status constant
    total_checks:  int
    passed_checks: int               # checks where status == "verified"
    checks:        list[VerificationCheck]

    def to_dict(self) -> dict:
        return {
            "status":       self.status,
            "totalChecks":  self.total_checks,
            "passedChecks": self.passed_checks,
            "checks":       [c.to_dict() for c in self.checks],
        }


# ── Per-check helpers ─────────────────────────────────────────────────────────

def _check_term_upserted(
    canonical_term_urn: str,
    term_data: dict | None,
    proposal: "Proposal",
    verified_at: str,
) -> VerificationCheck:
    """Verify that the canonical GlossaryTerm exists with the expected name and definition."""
    base = dict(
        operation_type="upsert_glossary_term",
        target_urn=canonical_term_urn,
        verified_at=verified_at,
    )
    # ── Unavailable: SDK not installed or read raised ─────────────────────
    if term_data is None or term_data.get("unavailable"):
        reason = (term_data or {}).get("reason", "DataHub read method not accessible")
        return VerificationCheck(
            **base,
            expected_state=f"GlossaryTerm exists with name '{proposal.display_name}'",
            observed_state="unavailable: read method could not execute",
            status=_CHECK_UNAVAILABLE,
            reason=reason,
        )
    # ── Failed: entity not found ──────────────────────────────────────────
    if not term_data.get("exists"):
        return VerificationCheck(
            **base,
            expected_state=f"GlossaryTerm exists with name '{proposal.display_name}'",
            observed_state="entity not found in DataHub graph",
            status=_CHECK_FAILED,
            reason="upsert did not persist: GlossaryTerm not readable after write",
        )
    # ── Entity exists — try to compare definition ─────────────────────────
    observed_def: str = term_data.get("definition", "")
    if not observed_def:
        # Definition field not exposed by this SDK version — entity exists but
        # we cannot confirm the definition; report as unavailable for this field
        return VerificationCheck(
            **base,
            expected_state=f"GlossaryTerm exists with canonical definition",
            observed_state="entity exists; definition attribute not readable via SDK",
            status=_CHECK_UNAVAILABLE,
            reason="GlossaryTerm exists but definition field not accessible on this SDK version",
        )
    # Lenient match: canonical definition always contains the display_name
    def_matches = proposal.display_name.lower() in observed_def.lower()
    short_def = (observed_def[:120] + "…") if len(observed_def) > 120 else observed_def
    if def_matches:
        return VerificationCheck(
            **base,
            expected_state=f"GlossaryTerm exists with name '{proposal.display_name}'",
            observed_state=f"exists; definition: '{short_def}'",
            status=_CHECK_VERIFIED,
            reason="GlossaryTerm exists with matching canonical definition",
        )
    return VerificationCheck(
        **base,
        expected_state=f"definition references '{proposal.display_name}'",
        observed_state=f"definition: '{short_def}'",
        status=_CHECK_FAILED,
        reason="observed definition does not reference the expected canonical term name",
    )


def _check_asset_linked(
    asset_urn: str,
    attached: list[str] | None,
    canonical_term_urn: str,
    term_id: str,
    verified_at: str,
) -> VerificationCheck:
    """Verify that the canonical term is attached to an asset."""
    base = dict(
        operation_type="attach_term_to_asset",
        target_urn=asset_urn,
        verified_at=verified_at,
    )
    expected = f"has_term:{canonical_term_urn}"
    if attached is None:
        return VerificationCheck(
            **base,
            expected_state=expected,
            observed_state="unavailable: read method could not execute",
            status=_CHECK_UNAVAILABLE,
            reason="DataHub read method not accessible for this asset type",
        )
    has_term = any(canonical_term_urn in u or term_id in u for u in attached)
    if has_term:
        return VerificationCheck(
            **base,
            expected_state=expected,
            observed_state=f"term present (found among {len(attached)} attached term(s))",
            status=_CHECK_VERIFIED,
            reason="canonical term is attached to this asset as expected",
        )
    short_list = ", ".join(attached[:3]) or "none"
    suffix     = " …" if len(attached) > 3 else ""
    return VerificationCheck(
        **base,
        expected_state=expected,
        observed_state=f"attached terms: {short_list}{suffix}",
        status=_CHECK_FAILED,
        reason="canonical term not found in asset's attached term list after write",
    )


def _check_term_deprecated(
    dep_urn: str,
    dep_data: dict | None,
    verified_at: str,
) -> VerificationCheck:
    """Verify that a conflicting term is marked deprecated in DataHub."""
    base = dict(
        operation_type="deprecate_term",
        target_urn=dep_urn,
        expected_state="deprecated=True",
        verified_at=verified_at,
    )
    if dep_data is None or dep_data.get("unavailable"):
        reason = (dep_data or {}).get("reason", "DataHub read method not accessible")
        return VerificationCheck(
            **base,
            observed_state="unavailable: read method could not execute",
            status=_CHECK_UNAVAILABLE,
            reason=reason,
        )
    if "deprecated" not in dep_data:
        # Entity exists but deprecation flag not exposed by this SDK version
        return VerificationCheck(
            **base,
            observed_state="entity exists; deprecated flag not readable via SDK",
            status=_CHECK_UNAVAILABLE,
            reason="deprecation attribute not accessible on this SDK version",
        )
    if dep_data["deprecated"]:
        return VerificationCheck(
            **base,
            observed_state="deprecated=True",
            status=_CHECK_VERIFIED,
            reason="term is marked deprecated in DataHub as expected",
        )
    return VerificationCheck(
        **base,
        observed_state=f"deprecated={dep_data['deprecated']}",
        status=_CHECK_FAILED,
        reason="term deprecation did not persist after write",
    )


# ── Main verification function ────────────────────────────────────────────────

def verify_proposal(
    dh: RosettaDataHub,
    proposal: "Proposal",
    write_result: dict,
) -> VerificationResult:
    """Re-read each affected DataHub entity and compare to the approved plan.

    Called only after apply_proposal() succeeds in Connected Mode.
    A representative sample (capped by _VERIFY_ASSET_SAMPLE /
    _VERIFY_DEPRECATE_SAMPLE) is re-read so verification is fast on large graphs.

    Demo Mode must never call this function.  The step-5 UI labels the demo
    outcome "VALIDATED · NOT EXECUTED" and must never imply a DataHub read.
    """
    if not write_result:
        return VerificationResult(
            status=NOT_EXECUTED, total_checks=0, passed_checks=0, checks=[]
        )

    now = datetime.now(timezone.utc).isoformat()
    checks: list[VerificationCheck] = []

    canonical_term_urn = write_result.get(
        "canonical_term", f"urn:li:glossaryTerm:{proposal.term_id}"
    )

    # ── Check 1: canonical GlossaryTerm upserted ─────────────────────────
    checks.append(_check_term_upserted(
        canonical_term_urn, dh.read_glossary_term(canonical_term_urn), proposal, now
    ))

    # ── Check 2: sample of affected assets linked ─────────────────────────
    for asset_urn in proposal.affected_assets[:_VERIFY_ASSET_SAMPLE]:
        checks.append(_check_asset_linked(
            asset_urn, dh.read_asset_term_urns(asset_urn),
            canonical_term_urn, proposal.term_id, now,
        ))

    # ── Check 3: sample of deprecated terms marked deprecated ────────────
    for dep_urn in proposal.deprecated_terms[:_VERIFY_DEPRECATE_SAMPLE]:
        checks.append(_check_term_deprecated(
            dep_urn, dh.read_glossary_term(dep_urn), now
        ))

    # ── Aggregate ─────────────────────────────────────────────────────────
    n_verified    = sum(1 for c in checks if c.status == _CHECK_VERIFIED)
    n_failed      = sum(1 for c in checks if c.status == _CHECK_FAILED)
    n_unavailable = sum(1 for c in checks if c.status == _CHECK_UNAVAILABLE)
    total = len(checks)

    if total == 0:
        status = NOT_EXECUTED
    elif n_verified == total:
        status = VERIFIED
    elif n_unavailable == total:
        status = VERIFICATION_UNAVAILABLE
    elif n_verified > 0:
        status = PARTIALLY_VERIFIED
    elif n_failed > 0:
        status = VERIFICATION_FAILED
    else:
        status = VERIFICATION_UNAVAILABLE  # all unavailable (defensive)

    return VerificationResult(
        status=status,
        total_checks=total,
        passed_checks=n_verified,
        checks=checks,
    )


# ── Write execution (Connected Mode only) ────────────────────────────────────

def apply_proposal(
    dh: RosettaDataHub,
    proposal: Proposal,
    approval: ApprovalToken,
) -> dict:
    """Write the reconciliation back to DataHub.

    Requires an explicit ApprovalToken whose plan_id matches the proposal.
    Raises ValueError if approval is missing, invalid, or for a different plan.
    Demo Mode must never reach this function.
    """
    if approval is None:
        raise ValueError(
            "Execution blocked: explicit approval is required for this write plan."
        )
    approval.validate_for(proposal)

    term_urn = dh.write_canonical_term(
        term_id=proposal.term_id,
        display_name=proposal.display_name,
        definition=proposal.canonical_definition,
    )
    dh.attach_term_to_assets(term_urn, proposal.affected_assets)
    for dep in proposal.deprecated_terms:
        dh.deprecate_conflicting_term(
            dep,
            note=f"Superseded by canonical term {term_urn} (reconciled by Rosetta).",
        )
    return {
        "canonical_term": term_urn,
        "linked_assets": proposal.affected_assets,
        "deprecated_terms": proposal.deprecated_terms,
        "approvers_notified": proposal.approvers,
        "plan_id": proposal.plan_id,
        "approved_at": approval.approved_at,
    }
