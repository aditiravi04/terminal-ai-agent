import typer
from terminal_ai.agent.orchestrator import run_chat
from terminal_ai.rag import index, index_exists

app = typer.Typer()


@app.command()
def chat(
    reindex: bool = typer.Option(False, "--index", help="Re-index the codebase before starting"),
):
    if reindex:
        print("🔄 Re-indexing codebase...\n")
        index(root=".", force=True)

    elif not index_exists():
        print("📚 No index found. Indexing repo for the first time...\n")
        index(root=".", force=False)

    run_chat()


def main():
    app()


if __name__ == "__main__":
    main()