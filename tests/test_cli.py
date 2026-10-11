import json
import sys

import pytest

from retrodoc import cli
from tests.conftest import FIXTURES, RESUME_FIXE, FauxClient


def test_trouver_fichiers_java():
    fichiers = cli.trouver_fichiers_java(str(FIXTURES))
    assert len(fichiers) == 7
    assert all(f.endswith(".java") for f in fichiers)


def test_trouver_fichiers_java_dans_les_sous_dossiers(tmp_path):
    (tmp_path / "a" / "b").mkdir(parents=True)
    (tmp_path / "a" / "b" / "X.java").write_text("class X {}", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("pas du java", encoding="utf-8")
    fichiers = cli.trouver_fichiers_java(str(tmp_path))
    assert [f.replace("\\", "/").split("/")[-1] for f in fichiers] == ["X.java"]


def test_analyser_dossier(classes):
    assert {c.nom for c in classes} == {
        "Animal", "Chien", "Compteur", "Couleur", "Mobile", "Nageur", "Vivant",
    }


def test_ecrire_json(classes, tmp_path):
    sortie = tmp_path / "analyse.json"
    cli.ecrire_json(classes, str(sortie))

    donnees = json.loads(sortie.read_text(encoding="utf-8"))
    chien = next(c for c in donnees if c["nom"] == "Chien")
    assert chien["parent"] == "Animal"
    assert chien["interfaces"] == ["Comparable", "Cloneable"]


def test_commande_analyze(monkeypatch, tmp_path, capsys):
    sortie = tmp_path / "resultat.json"
    monkeypatch.setattr(sys, "argv", ["retrodoc", "analyze", str(FIXTURES), "--sortie", str(sortie)])

    cli.main()

    assert len(json.loads(sortie.read_text(encoding="utf-8"))) == 7
    assert "7 classes trouvées" in capsys.readouterr().out


def test_commande_doc_sans_vrai_llm(monkeypatch, tmp_path):
    sortie = tmp_path / "DOC.md"
    monkeypatch.setattr(cli, "OllamaClient", lambda modele: FauxClient())
    monkeypatch.setattr(sys, "argv", ["retrodoc", "doc", str(FIXTURES), "--sortie", str(sortie)])

    cli.main()

    doc = sortie.read_text(encoding="utf-8")
    assert doc.startswith("# Documentation du projet")
    assert doc.count(RESUME_FIXE) == 7


def test_commande_inconnue(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["retrodoc", "banane", str(FIXTURES)])
    with pytest.raises(SystemExit):
        cli.main()
