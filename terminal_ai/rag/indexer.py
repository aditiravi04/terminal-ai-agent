import os
from .loader import load_repo
from .chunker import chunk_files
from .embedder import embed_chunks
from .store import store_chunks, clear_collection, index_exists, DEFAULT_PERSIST_DIR


def index(
    root: str = ".",
    force: bool = False,
    persist_dir: str = DEFAULT_PERSIST_DIR,
):
    """
    Full indexing pipeline: load → chunk → embed → store.

    Args:
        root:        Root directory of the repo to index (default: cwd)
        force:       If True, re-index even if an index already exists
        persist_dir: Where to store ChromaDB data
    """
    root = os.path.abspath(root)

    if index_exists(persist_dir) and not force:
        print("📚 Index already exists. Use --index to force a re-index.")
        return

    print(f"🔍 Indexing repo at: {root}\n")

    # Step 1: Load files
    print("📂 Loading files...")
    files = list(load_repo(root))
    print(f"   Found {len(files)} files.\n")

    if not files:
        print("⚠️  No files found to index. Check your root path.")
        return

    # Step 2: Chunk
    print("✂️  Chunking files...")
    chunks = chunk_files(files)
    print(f"   Created {len(chunks)} chunks.\n")

    # Step 3: Embed
    print("🧠 Embedding chunks (this may take a minute)...")
    if index_exists(persist_dir):
        clear_collection(persist_dir)

    embedded = embed_chunks(chunks, show_progress=True)
    print()

    # Step 4: Store
    print("💾 Storing in vector database...")
    store_chunks(embedded, persist_dir=persist_dir)

    print(f"\n✅ Indexing complete! {len(chunks)} chunks ready to query.\n")