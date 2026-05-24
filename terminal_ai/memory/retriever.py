from typing import List
from terminal_ai.rag.embedder import embed
from terminal_ai.memory.store import _get_collection, DEFAULT_PERSIST_DIR


def retrieve_memories(
    query: str,
    top_k: int = 3,
    persist_dir: str = DEFAULT_PERSIST_DIR,
) -> List[str]:
    """
    Embeds the query and returns the top_k most relevant past memories as strings.
    Returns empty list if no memories exist yet.
    """
    collection = _get_collection(persist_dir)

    if collection.count() == 0:
        return []

    query_embedding = embed(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, collection.count()),
        include=["documents"],
    )

    return results["documents"][0] if results["documents"] else []


def format_memories(memories: List[str]) -> str:
    """
    Formats memory strings into a clean block for injection into the prompt.
    """
    if not memories:
        return ""

    lines = "\n".join(f"- {m}" for m in memories)
    return f"Relevant context from past sessions:\n{lines}"