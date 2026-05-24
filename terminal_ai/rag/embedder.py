import requests
from typing import List

OLLAMA_EMBED_URL = "http://localhost:11434/api/embeddings"
EMBED_MODEL = "nomic-embed-text"


def embed(text: str) -> List[float]:
    """
    Embeds a single string using Ollama's nomic-embed-text model.
    Returns a list of floats (the embedding vector).
    """
    try:
        response = requests.post(
            OLLAMA_EMBED_URL,
            json={"model": EMBED_MODEL, "prompt": text},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()["embedding"]

    except requests.exceptions.ConnectionError:
        raise RuntimeError(
            "Could not connect to Ollama. Is it running? Try: ollama serve"
        )
    except requests.exceptions.HTTPError as e:
        if "model not found" in str(e).lower() or response.status_code == 404:
            raise RuntimeError(
                f"Embedding model '{EMBED_MODEL}' not found. "
                f"Pull it with: ollama pull {EMBED_MODEL}"
            )
        raise


def embed_chunks(chunks: List[dict], show_progress: bool = True) -> List[dict]:
    """
    Embeds each chunk's text and adds an 'embedding' key.
    Returns the same list with embeddings attached.
    """
    total = len(chunks)

    for i, chunk in enumerate(chunks):
        if show_progress and i % 20 == 0:
            print(f"  Embedding chunk {i + 1}/{total}...", end="\r")

        chunk["embedding"] = embed(chunk["text"])

    if show_progress:
        print(f"  Embedded {total} chunks.              ")

    return chunks