from terminal_ai.llm.ollama_provider import OllamaProvider
from terminal_ai.tools.registry import TOOLS
import json
import re

DECISION_MODEL = "qwen2.5:3b"  # fast, just picks a tool
ANSWER_MODEL = "qwen2.5:3b"
# ANSWER_MODEL = "llama3.2"      # full quality for final answer

provider = OllamaProvider()


def extract_json(text: str) -> str:
    text = text.strip()
    text = re.sub(r"```[a-zA-Z]*\n?", "", text)
    text = text.replace("```", "").strip()

    # Greedy match handles multiline JSON
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        raw = match.group(0)
        # Strip characters that are never valid in JSON
        raw = re.sub(r"(?<![\"\\])~", "", raw)
        return raw

    return text


def is_likely_file(path: str) -> bool:
    return "." in path and path != "."


def run_chat():

    print("\nAI Agent (Tool Mode)\nType 'exit' to quit\n")

    while True:

        user_input = input("You: ").strip()

        if user_input.lower() == "exit":
            break

        # -------------------------
        # STEP 1: TOOL DECISION (fast model)
        # -------------------------
        tool_prompt = f"""
You are a strict AI agent.

You MUST output ONLY valid JSON — no explanation, no markdown, no extra text.

TOOLS:
- list_dir(path)       → list contents of a directory
- read_file(path)      → read a specific file by path
- search(query)        → search the web for external knowledge
- ask_codebase(query)  → answer questions about THIS project's code and structure
- none                 → no tool needed, answer directly

RULES:
- Use ask_codebase for ANY question about how the code works, where something is defined, or what a module does
- Use read_file only when the user gives a specific file path
- Use list_dir only for exploring directory structure
- Use search for external/web knowledge
- Use none for greetings, math, or general knowledge questions

Respond with ONLY this JSON and nothing else:
{{
  "tool": "list_dir | read_file | search | ask_codebase | none",
  "input": "string"
}}

User request: {user_input}
"""

        decision = provider.chat(
            [{"role": "user", "content": tool_prompt}],
            model=DECISION_MODEL  # fast model for tool picking
        )

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
            # STEP 6: FINAL RESPONSE (full model)
            # -------------------------
            final_prompt = f"""
User request: {user_input}

Tool used: {tool}
Tool input: {tool_input}

Tool result:
{result}

Now explain this clearly and helpfully.
"""

            response = provider.chat(
                [{"role": "user", "content": final_prompt}],
                model=ANSWER_MODEL  # full model for quality answers
            )

            print("\nAI:", response, "\n")

        else:

            response = provider.chat(
                [{"role": "user", "content": user_input}],
                model=ANSWER_MODEL  # full model for quality answers
            )

            print("\nAI:", response, "\n")