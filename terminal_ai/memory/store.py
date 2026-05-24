import chromadb
import os
import uuid
from datetime import datetime
from typing import List

DEFAULT_PERSIST_DIR = os.path.expanduser("~/.terminal_ai/chroma")
MEMORY_COLLECTION = "memories"


def _get_collection(persist_dir: str = DEFAULT_PERSIST_DIR):
    os.makedirs(persist_dir, exist_ok=True)
    client = chromadb.PersistentClient(path=persist_dir)
    return client.get_or_create_collection(
        name=MEMORY_COLLECTION,
        metadata={"hnsw:space": "cosine"},
    )


def save_memory(text: str, embedding: List[float], persist_dir: str = DEFAULT_PERSIST_DIR):
    """
    Saves a memory summary with its embedding and a timestamp.
    """
    collection = _get_collection(persist_dir)

    memory_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()

    collection.upsert(
        ids=[memory_id],
        embeddings=[embedding],
        documents=[text],
        metadatas=[{"timestamp": timestamp}],
    )


def memory_count(persist_dir: str = DEFAULT_PERSIST_DIR) -> int:
    try:
        return _get_collection(persist_dir).count()
    except Exception:
        return 0