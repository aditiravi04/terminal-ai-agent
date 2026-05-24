import chromadb
import os
from typing import List

# Where ChromaDB stores its data on disk
DEFAULT_PERSIST_DIR = os.path.expanduser("~/.terminal_ai/chroma")
COLLECTION_NAME = "codebase"


def _get_client(persist_dir: str = DEFAULT_PERSIST_DIR) -> chromadb.ClientAPI:
    os.makedirs(persist_dir, exist_ok=True)
    return chromadb.PersistentClient(path=persist_dir)


def get_collection(persist_dir: str = DEFAULT_PERSIST_DIR):
    client = _get_client(persist_dir)
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},  # cosine similarity for code/text
    )


def clear_collection(persist_dir: str = DEFAULT_PERSIST_DIR):
    """Wipe the existing index so we can re-index from scratch."""
    client = _get_client(persist_dir)
    try:
        client.delete_collection(COLLECTION_NAME)
        print("🗑️  Cleared existing index.")
    except Exception:
        pass  # collection didn't exist yet, that's fine


def store_chunks(chunks: List[dict], persist_dir: str = DEFAULT_PERSIST_DIR):
    """
    Stores embedded chunks into ChromaDB.
    Each chunk must have: text, path, language, chunk_index, embedding
    """
    collection = get_collection(persist_dir)

    ids = []
    embeddings = []
    documents = []
    metadatas = []

    for chunk in chunks:
        chunk_id = f"{chunk['path']}::{chunk['chunk_index']}"
        ids.append(chunk_id)
        embeddings.append(chunk["embedding"])
        documents.append(chunk["text"])
        metadatas.append({
            "path": chunk["path"],
            "language": chunk["language"],
            "chunk_index": chunk["chunk_index"],
        })

    # Upsert in batches of 100 to avoid memory spikes
    batch_size = 100
    for i in range(0, len(ids), batch_size):
        collection.upsert(
            ids=ids[i:i + batch_size],
            embeddings=embeddings[i:i + batch_size],
            documents=documents[i:i + batch_size],
            metadatas=metadatas[i:i + batch_size],
        )

    print(f"✅ Stored {len(chunks)} chunks in vector store.")


def index_exists(persist_dir: str = DEFAULT_PERSIST_DIR) -> bool:
    """Returns True if there's already an index with at least one chunk."""
    try:
        collection = get_collection(persist_dir)
        return collection.count() > 0
    except Exception:
        return False