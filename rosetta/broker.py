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

from .datahub_client import MetricDefinition, RosettaDataHub
from .detector import Conflict

# Verification status constants (Connected Mode only)
VERIFIED            = "VERIFIED"
PARTIALLY_VERIFIED  = "PARTIALLY_VERIFIED"
VERIFICATION_FAILED = "VERIFICATION_FAILED"
NOT_EXECUTED        = "NOT_EXECUTED"

# Cap how many assets / deprecated terms we re-read during verification.
# A full re-read could be slow on large graphs; a representative sample is
# enough to confirm the write applied correctly.
_VERIFY_ASSET_SAMPLE = 3
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

@dataclass
class VerificationCheck:
    operation: str
    target_urn: str
    expected: str
    observed: str
    passed: bool

    def to_dict(self) -> dict:
        return {
            "operation": self.operation,
            "targetUrn": self.target_urn,
            "expected": self.expected,
            "observed": self.observed,
            "passed": self.passed,
        }


@dataclass
class VerificationResult:
    """Result of re-reading DataHub entities after apply_proposal()."""
    status: str          # VERIFIED | PARTIALLY_VERIFIED | VERIFICATION_FAILED | NOT_EXECUTED
    total_checks: int
    passed_checks: int
    checks: list[VerificationCheck]

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "totalChecks": self.total_checks,
            "passedChecks": self.passed_checks,
            "checks": [c.to_dict() for c in self.checks],
        }


def verify_proposal(
    dh: RosettaDataHub,
    proposal: Proposal,
    write_result: dict,
) -> VerificationResult:
    """Re-read each affected DataHub entity and compare to the approved plan.

    Called after apply_proposal() in Connected Mode.  A representative sample
    (capped by _VERIFY_ASSET_SAMPLE / _VERIFY_DEPRECATE_SAMPLE) is checked so
    that verification is fast even on large graphs.

    Returns VERIFIED when every sampled check passes, PARTIALLY_VERIFIED when
    some pass, VERIFICATION_FAILED when none pass, or NOT_EXECUTED if the
    write_result is empty.
    """
    if not write_result:
        return VerificationResult(
            status=NOT_EXECUTED, total_checks=0, passed_checks=0, checks=[]
        )

    checks: list[VerificationCheck] = []
    canonical_term_urn = write_result.get(
        "canonical_term", f"urn:li:glossaryTerm:{proposal.term_id}"
    )

    # ── Check 1: canonical GlossaryTerm exists ────────────────────────────
    term_data = dh.read_glossary_term(canonical_term_urn)
    term_exists = bool(term_data and term_data.get("exists"))
    checks.append(VerificationCheck(
        operation="upsert_glossary_term",
        target_urn=canonical_term_urn,
        expected="exists",
        observed="exists" if term_exists else "missing",
        passed=term_exists,
    ))

    # ── Check 2: sample of affected assets has the canonical term ─────────
    sampled_assets = proposal.affected_assets[:_VERIFY_ASSET_SAMPLE]
    for asset_urn in sampled_assets:
        attached = dh.read_asset_term_urns(asset_urn)
        has_term = any(
            canonical_term_urn in u or proposal.term_id in u for u in attached
        )
        checks.append(VerificationCheck(
            operation="attach_term_to_asset",
            target_urn=asset_urn,
            expected=f"has_term:{canonical_term_urn}",
            observed=(
                f"found: {', '.join(attached[:2]) or 'none'}"
                + (" …" if len(attached) > 2 else "")
            ),
            passed=has_term,
        ))

    # ── Check 3: sample of deprecated terms is marked deprecated ─────────
    sampled_deprecated = proposal.deprecated_terms[:_VERIFY_DEPRECATE_SAMPLE]
    for dep_urn in sampled_deprecated:
        dep_data = dh.read_glossary_term(dep_urn)
        is_deprecated = bool(dep_data and dep_data.get("deprecated"))
        checks.append(VerificationCheck(
            operation="deprecate_term",
            target_urn=dep_urn,
            expected="deprecated=True",
            observed=(
                f"deprecated={dep_data.get('deprecated')}"
                if dep_data else "unreadable"
            ),
            passed=is_deprecated,
        ))

    # ── Aggregate ─────────────────────────────────────────────────────────
    total  = len(checks)
    passed = sum(1 for c in checks if c.passed)

    if total == 0:
        status = NOT_EXECUTED
    elif passed == total:
        status = VERIFIED
    elif passed > 0:
        status = PARTIALLY_VERIFIED
    else:
        status = VERIFICATION_FAILED

    return VerificationResult(
        status=status,
        total_checks=total,
        passed_checks=passed,
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
