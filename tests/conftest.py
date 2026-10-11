from pathlib import Path

import pytest

from retrodoc.cli import analyser_dossier
from retrodoc.llm import LLMClient

FIXTURES = Path(__file__).parent / "fixtures"
RESUME_FIXE = "Résumé de test."


class FauxClient(LLMClient):
    """Remplace le vrai LLM : renvoie un texte fixe et garde les prompts reçus."""

    def __init__(self):
        self.prompts = []

    def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return RESUME_FIXE


@pytest.fixture
def faux_client():
    return FauxClient()


@pytest.fixture
def classes():
    return analyser_dossier(str(FIXTURES))


@pytest.fixture
def par_nom(classes):
    return {c.nom: c for c in classes}
