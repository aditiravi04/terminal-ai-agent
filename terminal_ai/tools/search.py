from pathlib import Path
from terminal_ai.tools.base import Tool


class SearchTool(Tool):

    def run(self, input_text: str):

        results = []

        for file in Path(".").rglob("*.py"):
            try:
                text = file.read_text()
                if input_text.lower() in text.lower():
                    results.append(str(file))
            except:
                pass

        return results