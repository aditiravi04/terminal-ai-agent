import requests

class OllamaProvider:

    def __init__(self, model="llama3.2"):
        self.model = model
        self.url = "http://localhost:11434/api/chat"

    def chat(self, messages):

        response = requests.post(
            self.url,
            json={
                "model": self.model,
                "messages": messages,
                "stream": False
            }
        )

        return response.json()["message"]["content"]
    
# system supports multi-turn memory i.e. remembers conversation history
# chat format
