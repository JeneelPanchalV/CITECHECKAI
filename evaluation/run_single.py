import sys
sys.path.insert(0, '.')

from core.pdf_loader   import load_pdf_pages
from core.chunking     import chunk_pages
from core.embeddings   import embed_texts
from core.vector_store import upsert_chunks
from core.rag          import answer_question

PDF_PATH = 'dataset/pdfs/3597503.3639187.pdf'
QUESTION = 'What is GILT?'

print(f'Indexing {PDF_PATH}...')
pages  = load_pdf_pages(PDF_PATH)
chunks = chunk_pages(pages)
embs   = embed_texts([c.text for c in chunks])
upsert_chunks(chunks, embs, doc_name=PDF_PATH.split("/")[-1])
print(f'Indexed {len(chunks)} chunks from {len(pages)} pages.')

print(f'\nQuestion: {QUESTION}')
answer, evidence, guard = answer_question(QUESTION)

print(f'\nGuard status : {guard}')
print(f'Answer       : {answer[:300]}')
print(f'\nTop evidence:')
for i, e in enumerate(evidence[:3], 1):
    print(f'  [{i}] Page {e.page}  dist={e.distance:.3f}  {e.text[:80]}...')
