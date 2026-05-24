from terminal_ai.llm.ollama_provider import OllamaProvider

def main():

    provider = OllamaProvider()

    print("\nTerminal AI Agent")
    print("Type 'exit' to quit")
    print("Type 'clear' to reset context\n")

    messages = [
        {
            "role": "system",
            "content": "You are a helpful coding assistant inside a terminal."
        }
    ]

    while True:

        user_input = input("You: ")

        # exit command
        if user_input.lower() == "exit":
            break

        # reset memory
        if user_input.lower() == "clear":
            messages = messages[:1]
            print("Context cleared.\n")
            continue

        messages.append({
            "role": "user",
            "content": user_input
        })

        # send FULL conversation history (important upgrade)
        response = provider.chat(messages)

        print("\nAI:", response, "\n")

        messages.append({
            "role": "assistant",
            "content": response
        })


if __name__ == "__main__":
    main()