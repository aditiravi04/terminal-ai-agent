from typing import List
from terminal_ai.llm.ollama_provider import OllamaProvider
from terminal_ai.rag.embedder import embed
from terminal_ai.memory.store import save_memory

SUMMARY_MODEL = "qwen2.5:3b"  # fast model is fine for summarization

provider = OllamaProvider()


def summarize_and_save(chat_history: List[dict]):
    """
    Takes the full chat history from a session, asks the LLM to extract
    key facts and decisions, then embeds and stores the summary.

    chat_history format: [{"role": "user"|"assistant", "content": str}, ...]
    """
    if not chat_history:
        return

    # Format history as readable text
    transcript = "\n".join(
        f"{msg['role'].upper()}: {msg['content']}"
        for msg in chat_history
    )

    summary_prompt = f"""
You are a memory extraction system.

Read this conversation and extract a concise list of key facts, decisions, and context that would be useful to remember in future sessions.

Focus on:
- Facts about the user or their project
- Technical decisions made
- Problems that were solved and how
- Important context about what was built

Output ONLY a short paragraph summary (3-5 sentences). No bullet points, no preamble.

Conversation:
{transcript}
"""

    summary = provider.chat(
        [{"role": "user", "content": summary_prompt}],
        model=SUMMARY_MODEL
    )

    if not summary.strip():
        return

    # Embed and store
    embedding = embed(summary)
    save_memory(summary, embedding)