from core.embeddings import embed_query
from core.vector_store import query_topk
from core.guard import Evidence, hallucination_guard
from core.llm_ollama import ollama_generate


def build_prompt(question, evidence):
    ctx = []
    for i, e in enumerate(evidence, start=1):
        snippet = e.text[:1500] + ("..." if len(e.text) > 1500 else "")
        ctx.append(f"[{i}] Page {e.page}:\n{snippet}")
    context = "\n\n".join(ctx)

    return f"""QUESTION:
{question}

EVIDENCE:
{context}

Answer the question using only the evidence above. Cite using [N]."""


def _format_evidence_for_validator(evidence):
    return "\n\n".join(
        f"[{i}] Page {e.page}: {e.text}"
        for i, e in enumerate(evidence, start=1)
    )


def answer_question(question, k=5):
    """
    Returns: (answer, evidence, status, reason)
      status is one of:
        "answered"          - LLM gave a real answer
        "guard_refused"     - retrieval too weak, never called LLM
        "llm_refused"       - LLM had evidence but said insufficient
        "validator_rejected"- LLM answered but validator caught it
      reason is a short human-readable string
    """
    q_emb = embed_query(question)
    res = query_topk(q_emb, k=k)
    evidence = [
        Evidence(
            chunk_id=res["ids"][0][i],
            page=res["metadatas"][0][i]["page"],
            text=res["documents"][0][i],
            distance=res["distances"][0][i],
        )
        for i in range(len(res["ids"][0]))
    ]

    guard = hallucination_guard(evidence)
    if not guard.ok:
        return (
            "Insufficient evidence in the provided document.",
            evidence,
            "guard_refused",
            guard.reason,
        )

    prompt = build_prompt(question, evidence)
    evidence_text = _format_evidence_for_validator(evidence)
    answer, source = ollama_generate(
        prompt, question=question, evidence_text=evidence_text
    )

    if source == "llm_refused":
        return answer, evidence, "llm_refused", "LLM could not extract an answer from the evidence."
    if source == "validator_rejected":
        return answer, evidence, "validator_rejected", "Answer failed type-check validation."
    return answer, evidence, "answered", guard.reason
