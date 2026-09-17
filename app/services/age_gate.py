"""18+ hard gate for every ingest.

Rejects items when age_proof is missing, empty, or clearly unclear.
Country-agnostic: requires affirmative adult attestation / proof marker.
"""

from __future__ import annotations

from typing import Optional

# Tokens that indicate unclear / missing / underage — hard reject
_UNCLEAR_MARKERS = {
    "unknown",
    "unclear",
    "n/a",
    "na",
    "none",
    "missing",
    "?",
    "tba",
    "tbd",
    "unverified",
    "no",
    "false",
    "0",
    "underage",
    "minor",
    "child",
    "teen",  # ambiguous without adult context — treat as unclear for hard gate
}

# Affirmative markers that pass the gate (examples; connectors may supply richer strings)
_AFFIRMATIVE_HINTS = (
    "18+",
    "21+",
    "adult",
    "verified",
    "age_verified",
    "age-verified",
    "consenting adult",
    "all characters 18+",
    "18 plus",
    "over 18",
    "of age",
    "attested",
)


class AgeGateError(ValueError):
    """Raised when age_proof fails the 18+ hard gate."""

    def __init__(self, message: str = "age_proof missing or unclear; 18+ required"):
        super().__init__(message)
        self.message = message


def normalize_age_proof(raw: Optional[str]) -> str:
    if raw is None:
        return ""
    return str(raw).strip()


def check_age_proof(age_proof: Optional[str]) -> str:
    """Validate age_proof. Returns normalized string or raises AgeGateError."""
    proof = normalize_age_proof(age_proof)
    if not proof:
        raise AgeGateError("age_proof missing or empty; 18+ required")

    lowered = proof.lower().strip()
    if lowered in _UNCLEAR_MARKERS:
        raise AgeGateError(f"age_proof unclear or invalid: {proof!r}")

    # If it looks like a bare negative / refusal
    if lowered.startswith("no ") or lowered in {"not verified", "not 18", "under 18"}:
        raise AgeGateError(f"age_proof does not affirm 18+: {proof!r}")

    # Prefer affirmative language; also allow structured attestations
    has_hint = any(h in lowered for h in _AFFIRMATIVE_HINTS)
    # Structured / opaque proofs (hashes, UUIDs, long attestations) allowed if not unclear
    looks_structured = len(proof) >= 8 and lowered not in _UNCLEAR_MARKERS

    if not has_hint and not looks_structured:
        # Short vague strings fail
        raise AgeGateError(f"age_proof unclear; must affirm 18+: {proof!r}")

    return proof


def require_adult(age_proof: Optional[str]) -> str:
    """Public alias used by ingest path."""
    return check_age_proof(age_proof)
