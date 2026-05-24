from terminal_ai.llm.ollama_provider import OllamaProvider
from terminal_ai.tools.registry import TOOLS
from terminal_ai.memory import retrieve_memories, format_memories, summarize_and_save
import json
import re

DECISION_MODEL = "qwen2.5:3b"  # fast, just picks a tool
ANSWER_MODEL = "qwen2.5:3b"      # fast

# ANSWER_MODEL = "llama3.2"      # full quality for final answer

provider = OllamaProvider()


def extract_json(text: str) -> str:
    text = text.strip()
    text = re.sub(r"```[a-zA-Z]*\n?", "", text)
    text = text.replace("```", "").strip()

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        raw = match.group(0)
        raw = re.sub(r"(?<![\"\\])~", "", raw)
        return raw

    return text


def is_likely_file(path: str) -> bool:
    return "." in path and path != "."


def run_chat():

    print("\nAI Agent (Tool Mode)\nType 'exit' to quit\n")

    # Track full conversation history for memory summarization at end
    chat_history = []

    while True:

        user_input = input("You: ").strip()

        if user_input.lower() == "exit":
            # Summarize and save this session to memory before quitting
            summarize_and_save(chat_history)
            print("👋 Goodbye!\n")
            break

        # -------------------------
        # STEP 1: RETRIEVE MEMORIES
        # -------------------------
        memories = retrieve_memories(user_input)
        memory_context = format_memories(memories)

        # -------------------------
        # STEP 2: TOOL DECISION (fast model)
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
            model=DECISION_MODEL
        )

        print("\nDEBUG RAW MODEL OUTPUT:\n", decision, "\n")

        # -------------------------
        # STEP 3: PARSE JSON SAFELY
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
        # STEP 4: VALIDATE TOOL NAME
        # -------------------------
        if tool not in TOOLS and tool != "none":
            print(f"❌ Invalid tool: '{tool}' — valid options: {list(TOOLS.keys())}\n")
            continue

        # -------------------------
        # STEP 5: AUTO-CORRECT TOOL MISMATCH
        # -------------------------
        if tool == "list_dir" and is_likely_file(tool_input):
            print("⚠️  AI tried to list a file as directory. Switching to read_file.")
            tool = "read_file"

        if tool == "read_file" and not is_likely_file(tool_input):
            print("⚠️  AI tried to read a directory as file. Switching to list_dir.")
            tool = "list_dir"

        # -------------------------
        # STEP 6: EXECUTE TOOL
        # -------------------------
        if tool != "none":

            try:
                result = TOOLS[tool].run(tool_input)
            except Exception as e:
                print(f"❌ Tool execution failed: {e}\n")
                continue

            # -------------------------
            # STEP 7: FINAL RESPONSE (full model + memory context)
            # -------------------------
            final_prompt = f"""
You have the following memory from past conversations with this user:
{memory_context}

User request: {user_input}

Tool used: {tool}
Tool input: {tool_input}

Tool result:
{result}

Use the memory above to personalize your response. Now explain this clearly and helpfully.
""".strip()

            response = provider.chat(
                [{"role": "user", "content": final_prompt}],
                model=ANSWER_MODEL
            )

            print("\nAI:", response, "\n")

        else:

            # -------------------------
            # STEP 7: DIRECT RESPONSE (full model + memory context)
            # -------------------------
            direct_prompt = f"""
You have the following memory from past conversations with this user:
{memory_context}

Answer the user's message using the memory above when relevant.

User: {user_input}
""".strip()

            response = provider.chat(
                [{"role": "user", "content": direct_prompt}],
                model=ANSWER_MODEL
            )

            print("\nAI:", response, "\n")

        # Track history for end-of-session summarization
        chat_history.append({"role": "user", "content": user_input})
        chat_history.append({"role": "assistant", "content": response})