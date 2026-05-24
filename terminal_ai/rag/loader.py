import os
import pathlib
from typing import Iterator

# File types to index
ALLOWED_EXTENSIONS = {".py", ".md", ".txt"}

# Folders to always skip
SKIP_DIRS = {
    ".git", "__pycache__", ".venv", "venv", "env",
    "node_modules", ".mypy_cache", ".pytest_cache",
    "dist", "build", ".eggs", "*.egg-info"
}


def _is_ignored_by_gitignore(path: str, root: str) -> bool:
    """
    Checks .gitignore patterns at the repo root.
    Simple line-by-line match — not a full gitignore parser.
    """
    gitignore_path = os.path.join(root, ".gitignore")
    if not os.path.exists(gitignore_path):
        return False

    rel_path = os.path.relpath(path, root)

    with open(gitignore_path, "r", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # Simple pattern: if the path contains the pattern, skip it
            pattern = line.rstrip("/")
            if pattern in rel_path or rel_path.startswith(pattern):
                return True

    return False


def load_repo(root: str) -> Iterator[dict]:
    """
    Walks the repo from `root`, yields dicts:
      { "path": str, "content": str, "language": str }

    Skips binary files, ignored dirs, and non-allowed extensions.
    """
    root = os.path.abspath(root)

    for dirpath, dirnames, filenames in os.walk(root):
        # Prune skip dirs in-place so os.walk doesn't descend into them
        dirnames[:] = [
            d for d in dirnames
            if d not in SKIP_DIRS and not d.endswith(".egg-info")
        ]

        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            ext = pathlib.Path(filename).suffix.lower()

            if ext not in ALLOWED_EXTENSIONS:
                continue

            if _is_ignored_by_gitignore(filepath, root):
                continue

            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                if not content.strip():
                    continue

                yield {
                    "path": os.path.relpath(filepath, root),
                    "content": content,
                    "language": _ext_to_language(ext),
                }

            except Exception as e:
                print(f"⚠️  Could not read {filepath}: {e}")
                continue


def _ext_to_language(ext: str) -> str:
    return {
        ".py": "python",
        ".md": "markdown",
        ".txt": "text",
    }.get(ext, "unknown")