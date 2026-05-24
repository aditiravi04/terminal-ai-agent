import requests

class OllamaProvider:

    def __init__(self, model="llama3.2"):
        self.model = model
        self.url = "http://localhost:11434/api/chat"

    def chat(self, messages, model=None):
        response = requests.post(
            self.url,
            json={
                "model": model or self.model,
                "messages": messages,
                "stream": False
            }
        )

        data = response.json()

        if "message" not in data:
            raise RuntimeError(
                f"Ollama error: {data.get('error', 'unknown error')}\n"
                f"Model requested: {model or self.model}\n"
                f"Is the model pulled? Run: ollama pull {model or self.model}"
            )

        return data["message"]["content"]