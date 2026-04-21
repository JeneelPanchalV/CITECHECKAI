import json, os, sys
sys.path.insert(0, '.')

from core.pdf_loader   import load_pdf_pages
from core.chunking     import chunk_pages
from core.embeddings   import embed_texts, embed_query
from core.vector_store import upsert_chunks, query_topk

DATASET_PATH = 'dataset/qa_pairs.json'
PDF_DIR      = 'dataset/pdfs'
PREVIEW_N    = 10

with open(DATASET_PATH) as f:
    pairs = json.load(f)[:PREVIEW_N]

indexed = set()
for p in pairs:
    pdf_path = os.path.join(PDF_DIR, p['pdf'])
    if pdf_path in indexed:
        continue
    print(f'Indexing {p["pdf"]}...')
    pages  = load_pdf_pages(pdf_path)
    chunks = chunk_pages(pages)
    embs   = embed_texts([c.text for c in chunks])
    upsert_chunks(chunks, embs, doc_name=p['pdf'])
    indexed.add(pdf_path)

print('\n' + '='*65)
ok_count   = 0
warn_count = 0

for p in pairs:
    q_emb     = embed_query(p['question'])
    res       = query_topk(q_emb, k=3)
    best_dist = res['distances'][0][0]
    best_text = res['documents'][0][0][:100]

    status = 'OK  ' if best_dist < 1.4 else ('WARN' if best_dist < 1.8 else 'FAIL')
    if status == 'OK  ':
        ok_count += 1
    else:
        warn_count += 1

    print(f'[{status}] dist={best_dist:.3f}  Q: {p["question"][:55]}...')
    if status != 'OK  ':
        print(f'         snippet: {best_text}...')

print('='*65)
print(f'OK: {ok_count}  |  Needs review: {warn_count}  |  Total: {len(pairs)}')
