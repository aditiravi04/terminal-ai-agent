import os
from terminal_ai.tools.base import Tool


class ReadFileTool(Tool):

    def run(self, input_text: str):
        with open(input_text, "r", encoding="utf-8") as f:
            return f.read()


class ListDirTool(Tool):

    def run(self, input_text: str = "."):
        return os.listdir(input_text)