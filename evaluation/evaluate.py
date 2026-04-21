import sys, json, os
import pandas as pd
import requests
sys.path.insert(0, ".")

from core.pdf_loader   import load_pdf_pages
from core.chunking     import chunk_pages
from core.embeddings   import embed_texts
from core.vector_store import upsert_chunks
from core.rag          import answer_question
from core.config       import OLLAMA_BASE_URL, OLLAMA_MODEL

DATASET_PATH = "dataset/qa_pairs.json"
PDF_DIR      = "dataset/pdfs"
OUT_CSV      = "results/ragas_scores.csv"

os.makedirs("results", exist_ok=True)

def ollama(prompt):
    """Direct Ollama call — same as your existing llm_ollama.py."""
    r = requests.post(
        f"{OLLAMA_BASE_URL}/api/generate",
        json={"model": OLLAMA_MODEL, "prompt": prompt,
              "stream": False, "options": {"temperature": 0}},
        timeout=120
    )
    r.raise_for_status()
    return r.json().get("response", "").strip()

def score_faithfulness(answer, contexts):
    """Ask LLM: is every claim in the answer supported by the context?"""
    ctx = "\n".join(contexts[:3])
    prompt = f"""You are an evaluator. Given the context and an answer, 
score how faithful the answer is to the context on a scale of 0.0 to 1.0.
1.0 = every claim is supported. 0.0 = answer contradicts or ignores context.
Reply with ONLY a number between 0.0 and 1.0, nothing else.

CONTEXT:
{ctx[:1500]}

ANSWER:
{answer[:500]}

SCORE:"""
    try:
        result = ollama(prompt)
        return float(result.strip().split()[0])
    except:
        return None

def score_answer_relevancy(question, answer):
    """Ask LLM: does the answer actually address the question?"""
    prompt = f"""You are an evaluator. Score how relevant this answer is 
to the question on a scale of 0.0 to 1.0.
1.0 = directly answers the question. 0.0 = completely off-topic.
Reply with ONLY a number between 0.0 and 1.0, nothing else.

QUESTION:
{question}

ANSWER:
{answer[:500]}

SCORE:"""
    try:
        result = ollama(prompt)
        return float(result.strip().split()[0])
    except:
        return None

def score_context_precision(question, contexts):
    """Ask LLM: are the retrieved contexts relevant to the question?"""
    ctx = "\n".join(contexts[:3])
    prompt = f"""You are an evaluator. Score how relevant the retrieved 
context is to the question on a scale of 0.0 to 1.0.
1.0 = context is highly relevant. 0.0 = context is irrelevant.
Reply with ONLY a number between 0.0 and 1.0, nothing else.

QUESTION:
{question}

CONTEXT:
{ctx[:1500]}

SCORE:"""
    try:
        result = ollama(prompt)
        return float(result.strip().split()[0])
    except:
        return None

# Load dataset
with open(DATASET_PATH) as f:
    pairs = json.load(f)
print(f"Loaded {len(pairs)} Q&A pairs.")

# Index PDFs
indexed = set()
for p in pairs:
    pdf_path = os.path.join(PDF_DIR, p["pdf"])
    if pdf_path in indexed:
        continue
    print(f"Indexing: {p['pdf']}...")
    pages  = load_pdf_pages(pdf_path)
    chunks = chunk_pages(pages)
    embs   = embed_texts([c.text for c in chunks])
    upsert_chunks(chunks, embs, doc_name=p["pdf"])
    indexed.add(pdf_path)
    print(f"  Done — {len(chunks)} chunks from {len(pages)} pages.")

# Run each question and score
records = []
for i, p in enumerate(pairs):
    print(f"[{i+1:>3}/{len(pairs)}] {p['question'][:65]}...")
    try:
        answer, evidence, guard = answer_question(p["question"])
        contexts = [e.text for e in evidence]
    except Exception as ex:
        print(f"        ERROR: {ex}")
        answer, contexts, guard = "", [], f"ERROR: {ex}"

    print(f"         Scoring faithfulness...")
    faith = score_faithfulness(answer, contexts)
    print(f"         Scoring answer relevancy...")
    relevancy = score_answer_relevancy(p["question"], answer)
    print(f"         Scoring context precision...")
    precision = score_context_precision(p["question"], contexts)
    print(f"         faith={faith}  relevancy={relevancy}  precision={precision}")

    records.append({
        "id":                p["id"],
        "pdf":               p["pdf"],
        "question":          p["question"],
        "answer":            answer,
        "ground_truth":      p["ideal_answer"],
        "guard_status":      guard,
        "source_page":       p["source_page"],
        "faithfulness":      faith,
        "answer_relevancy":  relevancy,
        "context_precision": precision,
    })

df = pd.DataFrame(records)
df.to_csv(OUT_CSV, index=False)
print(f"\nSaved {len(df)} rows to {OUT_CSV}")

print("\n=== SCORES (mean) ===")
for col in ["faithfulness", "answer_relevancy", "context_precision"]:
    vals = df[col].dropna()
    mean = vals.mean() if len(vals) else float("nan")
    print(f"{col:<25}  {mean:.3f}  ({len(vals)}/{len(df)} scored)")
refused = (df["guard_status"] != "OK").sum()
print(f"Guard refusals          {refused}/{len(df)} ({100*refused/len(df):.1f}%)")
