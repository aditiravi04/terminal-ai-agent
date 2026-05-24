from abc import ABC, abstractmethod

class Tool(ABC):

    @abstractmethod
    def run(self, input_text: str):
        pass