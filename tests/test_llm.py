import pytest
import requests

from retrodoc.llm import LLMClient, OllamaClient


class FausseReponse:
    def __init__(self, donnees, erreur=None):
        self.donnees = donnees
        self.erreur = erreur

    def raise_for_status(self):
        if self.erreur:
            raise self.erreur

    def json(self):
        return self.donnees


def test_llmclient_est_abstraite():
    with pytest.raises(TypeError):
        LLMClient()


def test_ollama_envoie_la_bonne_requete(monkeypatch):
    appels = []

    def faux_post(url, json, timeout):
        appels.append((url, json, timeout))
        return FausseReponse({"response": "Bonjour !"})

    monkeypatch.setattr(requests, "post", faux_post)

    client = OllamaClient(url="http://ollama:1234", modele="mon-modele")
    assert client.generate("Dis bonjour") == "Bonjour !"

    url, corps, timeout = appels[0]
    assert url == "http://ollama:1234/api/generate"
    assert corps == {"model": "mon-modele", "prompt": "Dis bonjour", "stream": False}
    assert timeout > 0


def test_ollama_valeurs_par_defaut():
    client = OllamaClient()
    assert client.url == "http://localhost:11434"
    assert client.modele == "qwen2.5-coder:7b"


def test_ollama_remonte_les_erreurs_http(monkeypatch):
    def faux_post(url, json, timeout):
        return FausseReponse({}, erreur=requests.HTTPError("404 modèle introuvable"))

    monkeypatch.setattr(requests, "post", faux_post)

    with pytest.raises(requests.HTTPError):
        OllamaClient().generate("Dis bonjour")
