import requests

from terminal_ai.llm.provider import LLMProvider


class OllamaProvider(LLMProvider):

    def generate(self, prompt):

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2",
                "prompt": prompt,
                "stream": False
            }
        )

        return response.json()["response"]
    

# talks to ollama