from abc import ABC, abstractmethod

import requests


class LLMClient(ABC):

    @abstractmethod
    def generate(self, prompt) -> str:
        pass


class OllamaClient(LLMClient):
    def __init__(self, url = "http://localhost:11434", modele = "qwen2.5-coder:7b"):
        self.url = url
        self.modele = modele

    def generate(self, prompt: str) -> str:
        reponse = requests.post(self.url + "/api/generate", json = {"model" : self.modele, "prompt" : prompt, "stream" : False}, timeout = 120)
        reponse.raise_for_status()
        return reponse.json()["response"]


if __name__ == "__main__":
    client = OllamaClient()
    print(client.generate("Dis bonjour en une phrase."))