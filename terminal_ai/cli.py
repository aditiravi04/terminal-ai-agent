import typer
from terminal_ai.agent.orchestrator import run_chat
from terminal_ai.tools.filesystem import read_file, list_directory

app = typer.Typer()


@app.command()
def chat():
    run_chat()


@app.command()
def ls(path: str = "."):
    print(list_directory(path))


@app.command()
def cat(file_path: str):
    print(read_file(file_path))


if __name__ == "__main__":
    app()