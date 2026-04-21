import os
import chromadb
from chromadb.config import Settings
from core.config import CHROMA_DIR

def get_collection():
    os.makedirs(CHROMA_DIR, exist_ok=True)
    client = chromadb.PersistentClient(
        path=CHROMA_DIR,
        settings=Settings(anonymized_telemetry=False)
    )
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
    return col.query(
        query_embeddings=[query_embedding],
        n_results=k,
        include=["documents", "metadatas", "distances"]
    )
