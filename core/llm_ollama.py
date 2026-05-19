import re
import requests
from core.config import OLLAMA_BASE_URL, OLLAMA_MODEL

SYSTEM_PROMPT = """You are DocGuard AI, a careful document question-answering assistant.

You answer questions strictly from provided evidence excerpts. Follow these rules exactly:

1. Use ONLY information from the evidence below. Never use outside knowledge.

2. Many documents contain tables that get extracted as space-separated text. For example, a receipt table might appear as:
   "Ticket Defendant Offense Penalty Service Fee Payment 0906 P48 264877 332-31 $50.00 $1.50 $51.50"
   In this format, values appear in the SAME ORDER as their column headers. Match values to headers positionally: Penalty=$50.00, Service Fee=$1.50, Payment=$51.50. Apply this same column-matching logic to any table-like text.

3. BLANK CELLS MATTER. When flat text from a table is extracted, empty cells disappear. If you are asked about a field (e.g., "defendant name", "customer name", "recipient") and the value in that position does NOT resemble what the field should contain — for example, if "defendant" maps to a short alphanumeric code like "P48" instead of a human name — treat the field as MISSING and refuse. Do not force a positional match when the candidate value is implausible for the field type.

4. Type expectations for common fields:
   - Names of people: multiple words, capitalized, no digits
   - Dates: contain digits and a recognizable date format
   - Money: contain currency symbols or decimal amounts
   - IDs / confirmation numbers: digits, typically 6+ characters
   - Addresses: contain street names, cities, or postal codes
   If a candidate value violates the type expectation for the asked field, refuse.

5. Be confident when the evidence clearly supports an answer. Refuse only when the information is genuinely missing or when the candidate value fails a type check.

6. Cite every factual claim using [N] where N is the evidence number (e.g., [1], not [#1]).

7. Keep answers concise and direct. Do not restate the question. Do not add disclaimers.

8. When refusing, respond with EXACTLY this phrase and nothing else:
   Insufficient evidence in the provided document."""


VALIDATOR_PROMPT_TEMPLATE = """You are reviewing an answer for type-correctness.

QUESTION ASKED: {question}

ANSWER GIVEN: {answer}

EVIDENCE THE ANSWER CAME FROM:
{evidence}

Your job: decide whether the ANSWER is plausibly correct for the QUESTION, given the EVIDENCE.

Check specifically:
- Does the answer's TYPE match what the question asked for? (e.g., a question asking for a person's name should be answered with a name — multiple words, capitalized, no digits — not a short code like "P48" or "A1B".)
- Does the evidence actually contain this answer, or was it inferred from a positional guess on a table with blank cells?

Respond with exactly one of:
VALID - if the answer is plausibly correct
INVALID - if the answer fails a type check or appears to be a positional misinterpretation

Respond with only one word: VALID or INVALID."""


# Heuristic: does this answer look suspicious enough to warrant validation?
# We validate when an identity/name question gets a short code-like answer.
NAME_QUESTION_KEYWORDS = [
    "name", "who", "defendant", "plaintiff", "recipient",
    "sender", "author", "customer", "client", "patient",
]


def _looks_like_code(text: str) -> bool:
    """Returns True if text looks like a short alphanumeric code rather than a name."""
    # Strip citation markers and whitespace
    cleaned = re.sub(r"\[\d+\]", "", text).strip()
    if not cleaned:
        return False
    # If it's short and contains digits, it's probably a code
    if len(cleaned) <= 10 and any(c.isdigit() for c in cleaned):
        return True
    # If it's short and all uppercase letters/digits (looks like an ID)
    if len(cleaned) <= 6 and cleaned.replace(" ", "").isalnum():
        return True
    return False


def _needs_validation(question: str, answer: str) -> bool:
    """Decide whether to run the validator second-pass."""
    q_lower = question.lower()
    # Only validate when asking about a name/identity AND the answer looks like a code
    asks_about_identity = any(kw in q_lower for kw in NAME_QUESTION_KEYWORDS)
    if not asks_about_identity:
        return False
    if "insufficient evidence" in answer.lower():
        return False  # already refused
    return _looks_like_code(answer)


def _call_ollama(prompt: str, system: str = None) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1}
    }
    if system:
        payload["system"] = system
    r = requests.post(
        f"{OLLAMA_BASE_URL}/api/generate",
        json=payload,
        timeout=120
    )
    r.raise_for_status()
    return r.json().get("response", "").strip()


def ollama_generate(prompt: str, question: str = None, evidence_text: str = None):
    """
    Generate an answer with optional second-pass validation.

    Returns: (answer_text, source)
      source is one of: "llm", "llm_refused", "validator_rejected"
    """
    answer = _call_ollama(prompt, system=SYSTEM_PROMPT)

    # Detect direct LLM refusal
    if "insufficient evidence" in answer.lower():
        return answer, "llm_refused"

    # Run validation if caller provided context for it
    if question is not None and evidence_text is not None:
        if _needs_validation(question, answer):
            validator_prompt = VALIDATOR_PROMPT_TEMPLATE.format(
                question=question,
                answer=answer,
                evidence=evidence_text,
            )
            verdict = _call_ollama(validator_prompt).upper()
            if "INVALID" in verdict:
                return "Insufficient evidence in the provided document.", "validator_rejected"

    return answer, "llm"
