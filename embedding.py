# embedding.py

import requests
from config import OLLAMA_EMBEDDING_URL, OLLAMA_MODEL

def get_embedding(text: str) -> list[float]:
    response = requests.post(
        OLLAMA_EMBEDDING_URL,
        json={"model": OLLAMA_MODEL, "prompt": text}
    )
    response.raise_for_status()
    return response.json()["embedding"]
