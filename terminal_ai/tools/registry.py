from terminal_ai.tools.filesystem import ReadFileTool, ListDirTool
from terminal_ai.tools.search import SearchTool
from terminal_ai.tools.ask_codebase import AskCodebaseTool

TOOLS = {
    "read_file": ReadFileTool(),
    "list_dir": ListDirTool(),
    "search": SearchTool(),
    "ask_codebase": AskCodebaseTool()
}