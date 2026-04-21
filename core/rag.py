from core.embeddings import embed_query
from core.vector_store import query_topk
from core.guard import Evidence, hallucination_guard
from core.llm_ollama import ollama_generate

def build_prompt(question, evidence):
    ctx = []
    for i, e in enumerate(evidence, start=1):
        snippet = e.text[:400] + ("..." if len(e.text) > 400 else "")
        ctx.append(f"[{i}] Page {e.page}: {snippet}")

    context = "\n\n".join(ctx)

    return f"""
You are CiteCheck AI.

RULES:
- Answer ONLY using the evidence below.
- If the answer is not clearly supported, say:
  "Insufficient evidence in the provided document."
- Do NOT use outside knowledge.
- Cite claims using [#].

QUESTION:
{question}

EVIDENCE:
{context}

Answer:
"""

def answer_question(question, k=5):
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
        return "Insufficient evidence in the provided document.", evidence, guard.reason

    prompt = build_prompt(question, evidence)
    answer = ollama_generate(prompt)
    return answer, evidence, "OK"
