from pathlib import Path


def search_code(keyword):
    results = []

    for file in Path(".").rglob("*.py"):
        try:
            text = file.read_text(encoding="utf-8")
            if keyword.lower() in text.lower():
                results.append(str(file))
        except:
            pass

    return results