from dataclasses import dataclass
from typing import List

@dataclass
class Evidence:
    chunk_id: str
    page: int
    text: str
    distance: float  # lower = better

@dataclass
class GuardResult:
    ok: bool
    reason: str

# Tuned for sentence-transformers/all-MiniLM-L6-v2 which typically
# produces distances in the 1.0-1.8 range for semantic matches.
BEST_DISTANCE_MAX = 1.8
AVG_DISTANCE_MAX = 1.9
MIN_TOTAL_CHARS = 300


def hallucination_guard(evidence: List[Evidence]) -> GuardResult:
    if not evidence:
        return GuardResult(False, "No evidence retrieved.")

    best = min(e.distance for e in evidence)
    avg = sum(e.distance for e in evidence) / len(evidence)
    total_chars = sum(len(e.text) for e in evidence)

    if best > BEST_DISTANCE_MAX:
        return GuardResult(
            False,
            f"Top evidence match is too weak (distance {best:.2f} > {BEST_DISTANCE_MAX})."
        )

    if avg > AVG_DISTANCE_MAX:
        return GuardResult(
            False,
            f"Overall evidence relevance is low (avg distance {avg:.2f} > {AVG_DISTANCE_MAX})."
        )

    if total_chars < MIN_TOTAL_CHARS:
        return GuardResult(
            False,
            f"Not enough evidence to answer reliably ({total_chars} chars < {MIN_TOTAL_CHARS})."
        )

    return GuardResult(True, f"OK (best={best:.2f}, avg={avg:.2f}, chars={total_chars})")
