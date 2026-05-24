import typer
from terminal_ai.agent.orchestrator import run_chat

app = typer.Typer()


@app.command()
def chat():
    run_chat()


def main():
    app()


if __name__ == "__main__":
    main()