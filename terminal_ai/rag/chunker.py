from typing import List


def chunk_text(
    text: str,
    path: str,
    language: str,
    chunk_size: int = 500,
    overlap: int = 100,
) -> List[dict]:
    """
    Splits `text` into overlapping word-based chunks.

    Returns list of dicts:
      {
        "text": str,          # the chunk content
        "path": str,          # source file path
        "language": str,      # python / markdown / text
        "chunk_index": int,   # position within the file
      }
    """
    words = text.split()

    if not words:
        return []

    chunks = []
    start = 0
    index = 0

    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunk_text = " ".join(chunk_words)

        chunks.append({
            "text": chunk_text,
            "path": path,
            "language": language,
            "chunk_index": index,
        })

        # Move forward by (chunk_size - overlap) so chunks overlap
        start += chunk_size - overlap
        index += 1

    return chunks


def chunk_files(files: List[dict], chunk_size: int = 500, overlap: int = 100) -> List[dict]:
    """
    Convenience wrapper: takes the output of loader.load_repo()
    and returns all chunks across all files.
    """
    all_chunks = []

    for file in files:
        chunks = chunk_text(
            text=file["content"],
            path=file["path"],
            language=file["language"],
            chunk_size=chunk_size,
            overlap=overlap,
        )
        all_chunks.extend(chunks)

    return all_chunks