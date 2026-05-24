# terminal-ai-agent

A fully local AI agent that runs in your terminal. It can answer questions, read your files, search the web, understand your codebase, and remember things across sessions, all without sending your data anywhere.

Built with Python, Ollama, and ChromaDB.

---

## Features

- **Tool-calling** — the agent decides which tool to use based on your request, executes it, and explains the result
- **Codebase awareness** — index your repo and ask questions about your own code
- **Persistent memory** — remembers context from past sessions using semantic search
- **Fully local** — everything runs on your machine, no API keys required
- **Installable CLI** — run it from anywhere with `ai-agent`

---

## Tools

| Tool | What it does |
|---|---|
| `read_file` | Reads a specific file by path |
| `list_dir` | Lists the contents of a directory |
| `search` | Searches the web for external knowledge |
| `ask_codebase` | Answers questions about your project's code and structure |

---

## How it works

```
Your message
    ↓
Tool decision (fast 3B model)
    ↓
Tool execution (file, search, or RAG)
    ↓
Final answer (full 8B model + memory context)
    ↓
Memory saved at end of session
```

On startup, the agent indexes your codebase once. At the end of every session, it summarizes the conversation and stores it in a local vector database. Next time you start it, relevant memories are silently injected into the context.

---

## Requirements

- Python 3.9+
- [Ollama](https://ollama.com) running locally

Pull the required models:
```bash
ollama pull llama3.2
ollama pull qwen2.5:3b
ollama pull nomic-embed-text
```

---

## Installation

```bash
git clone https://github.com/yourusername/terminal-ai-agent
cd terminal-ai-agent
pip install -e .
```

---

## Usage

```bash
# Start the agent (auto-indexes on first run)
ai-agent

# Force re-index after making code changes
ai-agent --index
```

Example session:
```
You: how does the tool router work?
You: read the file terminal_ai/cli.py
You: list the terminal_ai directory
You: what is the capital of France?
You: exit
```

---

## Project structure

```
terminal_ai/
├── agent/
│   └── orchestrator.py    # tool routing, JSON parsing, response loop
├── llm/
│   └── ollama_provider.py # Ollama API wrapper
├── memory/
│   ├── retriever.py       # fetches relevant memories per turn
│   ├── store.py           # saves memories to ChromaDB
│   └── summarizer.py      # summarizes session on exit
├── rag/
│   ├── loader.py          # walks repo and reads files
│   ├── chunker.py         # splits files into overlapping chunks
│   ├── embedder.py        # embeds chunks via nomic-embed-text
│   ├── store.py           # stores embeddings in ChromaDB
│   └── retriever.py       # semantic search over codebase
├── tools/
│   ├── ask_codebase.py    # RAG tool
│   ├── filesystem.py      # read_file and list_dir tools
│   ├── search.py          # web search tool
│   └── registry.py        # tool registry
└── cli.py                 # entry point (typer)
```

---

## Tech stack

- **[Ollama](https://ollama.com)** — local LLM inference
- **[ChromaDB](https://www.trychroma.com)** — local vector database for RAG and memory
- **[Typer](https://typer.tiangolo.com)** — CLI framework
- **nomic-embed-text** — embedding model for semantic search
