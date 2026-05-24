from terminal_ai.llm.ollama_provider import OllamaProvider
from terminal_ai.tools.filesystem import read_file, list_directory
from terminal_ai.tools.search import search_code


provider = OllamaProvider()


def run_chat():
    """
    Basic interactive chat loop with simple tool support.
    """

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful terminal AI assistant. "
                "You help the user with coding, explaining files, and answering questions."
            )
        }
    ]

    print("\nTerminal AI Agent (Phase 10)")
    print("Commands:")
    print("  exit  -> quit")
    print("  clear -> reset conversation")
    print("  ls    -> list files")
    print("  cat <file> -> read file\n")

    while True:

        user_input = input("You: ").strip()

        # -----------------------
        # EXIT
        # -----------------------
        if user_input.lower() == "exit":
            break

        # -----------------------
        # CLEAR MEMORY
        # -----------------------
        if user_input.lower() == "clear":
            messages = messages[:1]
            print("Context cleared.\n")
            continue

        # -----------------------
        # LIST FILES TOOL
        # -----------------------
        if user_input.lower() == "ls":
            files = list_directory(".")
            print("\nFiles in directory:")
            for f in files:
                print("-", f)
            print()
            continue

        # -----------------------
        # READ FILE TOOL
        # -----------------------
        if user_input.startswith("cat "):
            file_path = user_input.replace("cat ", "").strip()

            try:
                content = read_file(file_path)
                print(f"\n--- {file_path} ---\n")
                print(content[:2000])  # prevent flooding terminal
                print("\n-------------------\n")

            except Exception as e:
                print(f"Error reading file: {e}\n")

            continue
        
        # SEARCH
        if user_input.startswith("search "):
            keyword = user_input.replace("search ", "")
            results = search_code(keyword)

            print("\nFound in:")
            for r in results:
                print("-", r)

            continue
            
        # ASK
        if user_input.startswith("ask "):

            question = user_input.replace("ask ", "")

            matches = search_code(question.split()[0])

            context = ""

            for file in matches[:3]:
                context += read_file(file) + "\n\n"

            prompt = f"""
            Answer this question using the codebase:

            QUESTION:
            {question}

            CODE CONTEXT:
            {context}
            """

            response = provider.chat([
                {"role": "user", "content": prompt}
            ])

            print("\nAI:", response)
            continue

        # -----------------------
        # NORMAL CHAT (LLM)
        # -----------------------
        messages.append({
            "role": "user",
            "content": user_input
        })

        response = provider.chat(messages)

        print("\nAI:", response, "\n")

        messages.append({
            "role": "assistant",
            "content": response
        })