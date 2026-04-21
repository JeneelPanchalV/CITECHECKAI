import sys
sys.path.insert(0, '.')

from core.config import OLLAMA_MODEL, OLLAMA_BASE_URL
from langchain_ollama import ChatOllama, OllamaEmbeddings
from ragas.llms       import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper

def get_ragas_llm():
    llm = ChatOllama(
        model       = OLLAMA_MODEL,
        base_url    = OLLAMA_BASE_URL,
        temperature = 0,
        timeout     = 600,
    )
    return LangchainLLMWrapper(llm)

def get_ragas_embeddings():
    emb = OllamaEmbeddings(
        model    = OLLAMA_MODEL,
        base_url = OLLAMA_BASE_URL,
    )
    return LangchainEmbeddingsWrapper(emb)
