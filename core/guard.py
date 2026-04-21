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

def hallucination_guard(evidence: List[Evidence]) -> GuardResult:
    if not evidence:
        return GuardResult(False, "No evidence retrieved.")

    best = min(e.distance for e in evidence)
    avg = sum(e.distance for e in evidence) / len(evidence)
    total_chars = sum(len(e.text) for e in evidence)

    if best > 1.4:
        return GuardResult(False, "Top evidence match is too weak.")
    
    if avg > 1.8:
        return GuardResult(False, "Overall evidence relevance is low.")

    if total_chars < 600:
        return GuardResult(False, "Not enough evidence to answer reliably.")

    return GuardResult(True, "OK")
