from terminal_ai.llm.ollama_provider import OllamaProvider


def main():

    provider = OllamaProvider()

    prompt = input("You: ")

    answer = provider.generate(prompt)

    print("\nAI:")
    print(answer)


if __name__ == "__main__":
    main()