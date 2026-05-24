from terminal_ai.llm.ollama_provider import OllamaProvider
from terminal_ai.tools.registry import TOOLS
import json

provider = OllamaProvider()


def run_chat():

    print("\nAI Agent (Tool Mode)\n")

    while True:

        user_input = input("You: ")

        if user_input == "exit":
            break

        # STEP 1: ask AI what to do
        tool_prompt = f"""
You are an AI agent.

You have tools:
- read_file(filename)
- list_dir(path)
- search(query)

Return ONLY JSON like:
{{
  "tool": "...",
  "input": "..."
}}

If no tool is needed:
{{
  "tool": "none",
  "input": ""
}}

User request:
{user_input}
"""

        decision = provider.chat([
            {"role": "user", "content": tool_prompt}
        ])

        try:
            action = json.loads(decision)
        except:
            print("AI failed to return valid JSON")
            continue

        tool = action["tool"]
        tool_input = action["input"]

        # STEP 2: execute tool if needed
        if tool != "none":
            result = TOOLS[tool].run(tool_input)

            final_prompt = f"""
User asked: {user_input}

Tool used: {tool}
Tool result: {result}

Now give a final helpful answer.
"""

            response = provider.chat([
                {"role": "user", "content": final_prompt}
            ])

            print("\nAI:", response, "\n")

        else:
            response = provider.chat([
                {"role": "user", "content": user_input}
            ])

            print("\nAI:", response, "\n")