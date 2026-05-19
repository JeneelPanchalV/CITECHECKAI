import os
import chromadb
from chromadb.config import Settings
from core.config import CHROMA_DIR

_client = None

def _get_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(
            path=CHROMA_DIR,
            settings=Settings(anonymized_telemetry=False)
        )
    return _client

def get_collection():
    os.makedirs(CHROMA_DIR, exist_ok=True)
    client = _get_client()
    return client.get_or_create_collection(name="citecheck")

def upsert_chunks(chunks, embeddings, doc_name: str):
    col = get_collection()
    col.upsert(
        ids=[c.chunk_id for c in chunks],
        documents=[c.text for c in chunks],
        metadatas=[{"page": c.page, "doc": doc_name} for c in chunks],
        embeddings=embeddings
    )

def query_topk(query_embedding, k=5):
    col = get_collection()
    collection_size = col.count()
    safe_k = max(1, min(k, collection_size))
    return col.query(
        query_embeddings=[query_embedding],
        n_results=safe_k,
        include=["documents", "metadatas", "distances"]
    )
