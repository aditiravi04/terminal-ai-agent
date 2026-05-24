from terminal_ai.llm.ollama_provider import OllamaProvider
from terminal_ai.tools.registry import TOOLS
import json
import os
import re

provider = OllamaProvider()


def extract_json(text: str) -> str:
    """
    Strips markdown fences and extracts the first {...} JSON object found.
    Much more robust than just removing backticks.
    """
    text = text.strip()

    # Remove ```json ... ``` or ``` ... ``` fences
    text = re.sub(r"```[a-zA-Z]*\n?", "", text)
    text = text.replace("```", "").strip()

    # Extract the first {...} block (handles extra prose before/after JSON)
    match = re.search(r"\{.*?\}", text, re.DOTALL)
    if match:
        return match.group(0)

    return text  # fall through and let json.loads raise the error


def is_likely_file(path: str) -> bool:
    """
    Heuristic: treat as file if it has an extension (but not just a lone dot).
    """
    return "." in path and path != "."


def run_chat():

    print("\nAI Agent (Tool Mode)\nType 'exit' to quit\n")

    while True:

        user_input = input("You: ").strip()

        if user_input.lower() == "exit":
            break

        # -------------------------
        # STEP 1: TOOL DECISION
        # -------------------------
        tool_prompt = f"""
You are a strict AI agent.

You MUST output ONLY valid JSON — no explanation, no markdown, no extra text.

TOOLS:
- list_dir(path) → use ONLY for folders/directories
- read_file(path) → use ONLY for files (.py, .txt, .md, etc.)
- search(query)   → use for web/knowledge queries
- none            → use when no tool is needed

CRITICAL RULES:
- If the path has a file extension (.py, .txt, .md, etc.), ALWAYS use read_file
- If the path is a directory, use list_dir
- NEVER use list_dir on a file path
- If no tool is needed, use "none"

Respond with ONLY this JSON and nothing else:
{{
  "tool": "list_dir | read_file | search | none",
  "input": "string"
}}

User request: {user_input}
"""

        decision = provider.chat([
            {"role": "user", "content": tool_prompt}
        ])

        print("\nDEBUG RAW MODEL OUTPUT:\n", decision, "\n")

        # -------------------------
        # STEP 2: PARSE JSON SAFELY
        # -------------------------
        try:
            cleaned = extract_json(decision)
            action = json.loads(cleaned)

            tool = action.get("tool", "none").strip()
            tool_input = action.get("input", "").strip()

        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse model output: {e}")
            print(f"   Raw output was: {repr(decision)}\n")
            continue
        except Exception as e:
            print(f"❌ Unexpected error during parsing: {e}\n")
            continue

        # -------------------------
        # STEP 3: VALIDATE TOOL NAME
        # -------------------------
        if tool not in TOOLS and tool != "none":
            print(f"❌ Invalid tool: '{tool}' — valid options: {list(TOOLS.keys())}\n")
            continue

        # -------------------------
        # STEP 4: AUTO-CORRECT TOOL MISMATCH
        # -------------------------
        if tool == "list_dir" and is_likely_file(tool_input):
            print("⚠️  AI tried to list a file as directory. Switching to read_file.")
            tool = "read_file"

        if tool == "read_file" and not is_likely_file(tool_input):
            print("⚠️  AI tried to read a directory as file. Switching to list_dir.")
            tool = "list_dir"

        # -------------------------
        # STEP 5: EXECUTE TOOL
        # -------------------------
        if tool != "none":

            try:
                result = TOOLS[tool].run(tool_input)
            except Exception as e:
                print(f"❌ Tool execution failed: {e}\n")
                continue

            # -------------------------
            # STEP 6: FINAL RESPONSE
            # -------------------------
            final_prompt = f"""
User request: {user_input}

Tool used: {tool}
Tool input: {tool_input}

Tool result:
{result}

Now explain this clearly and helpfully.
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