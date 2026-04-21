import requests
from core.config import OLLAMA_BASE_URL, OLLAMA_MODEL

def ollama_generate(prompt: str) -> str:
    r = requests.post(
        f"{OLLAMA_BASE_URL}/api/generate",
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.1}
        },
        timeout=120
    )
    r.raise_for_status()
    return r.json().get("response", "").strip()
