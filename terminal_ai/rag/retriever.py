from typing import List
from .embedder import embed
from .store import get_collection, DEFAULT_PERSIST_DIR


def retrieve(
    query: str,
    top_k: int = 5,
    persist_dir: str = DEFAULT_PERSIST_DIR,
) -> List[dict]:
    """
    Embeds the query and returns the top_k most relevant chunks.

    Each result:
      {
        "text": str,
        "path": str,
        "language": str,
        "chunk_index": int,
        "score": float,   # cosine distance (lower = more similar)
      }
    """
    query_embedding = embed(query)
    collection = get_collection(persist_dir)

    if collection.count() == 0:
        return []

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    for i in range(len(results["ids"][0])):
        chunks.append({
            "text": results["documents"][0][i],
            "path": results["metadatas"][0][i]["path"],
            "language": results["metadatas"][0][i]["language"],
            "chunk_index": results["metadatas"][0][i]["chunk_index"],
            "score": results["distances"][0][i],
        })

    return chunks


def format_context(chunks: List[dict]) -> str:
    """
    Formats retrieved chunks into a clean context block for the LLM prompt.
    """
    if not chunks:
        return "No relevant code found."

    parts = []
    for chunk in chunks:
        parts.append(
            f"### {chunk['path']} (chunk {chunk['chunk_index']})\n"
            f"```{chunk['language']}\n"
            f"{chunk['text']}\n"
            f"```"
        )

    return "\n\n".join(parts)