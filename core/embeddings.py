from sentence_transformers import SentenceTransformer
from core.config import EMBED_MODEL

_model = None

def get_embedder():
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBED_MODEL)
    return _model

def embed_texts(texts):
    model = get_embedder()
    vectors = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=False
    )
    return [v.tolist() for v in vectors]

def embed_query(query):
    model = get_embedder()
    v = model.encode(
        [query],
        normalize_embeddings=True,
        show_progress_bar=False
    )[0]
    return v.tolist()
