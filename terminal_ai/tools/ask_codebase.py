from terminal_ai.rag import retrieve, format_context, index_exists


class AskCodebaseTool:
    name = "ask_codebase"
    description = "Ask a question about the codebase. Use this for questions about how code works, where something is defined, or what a module does."

    def run(self, query: str) -> str:
        """
        Retrieves relevant code chunks for `query` and returns
        a formatted context block for the LLM to reason over.
        """
        if not index_exists():
            return (
                "❌ No codebase index found. "
                "Run with --index flag first: python -m terminal_ai.cli --index"
            )

        chunks = retrieve(query, top_k=5)

        if not chunks:
            return "No relevant code found for that query."

        return format_context(chunks)