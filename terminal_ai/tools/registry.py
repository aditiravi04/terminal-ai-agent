from terminal_ai.tools.filesystem import ReadFileTool, ListDirTool
from terminal_ai.tools.search import SearchTool

TOOLS = {
    "read_file": ReadFileTool(),
    "list_dir": ListDirTool(),
    "search": SearchTool()
}