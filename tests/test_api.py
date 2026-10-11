import io
import zipfile

import pytest
from fastapi.testclient import TestClient

from retrodoc import api
from tests.conftest import FIXTURES, RESUME_FIXE


@pytest.fixture
def http(monkeypatch, faux_client):
    """Client HTTP de test : le vrai LLM est remplacé par le faux client."""
    monkeypatch.setattr(api, "client", faux_client)
    monkeypatch.setattr(api, "ANALYSES", {})
    return TestClient(api.app)


@pytest.fixture
def zip_fixtures():
    tampon = io.BytesIO()
    with zipfile.ZipFile(tampon, "w") as archive:
        for fichier in sorted(FIXTURES.glob("*.java")):
            archive.write(fichier, "src/" + fichier.name)
    tampon.seek(0)
    return tampon


def envoyer(http, zip_fixtures):
    reponse = http.post(
        "/analyses", files={"fichier": ("projet.zip", zip_fixtures, "application/zip")}
    )
    assert reponse.status_code == 200
    return reponse.json()["id"]


def test_post_renvoie_un_identifiant(http, zip_fixtures):
    analyse_id = envoyer(http, zip_fixtures)
    assert isinstance(analyse_id, str)
    assert analyse_id in api.ANALYSES


def test_deux_envois_donnent_deux_identifiants(http, zip_fixtures):
    premier = envoyer(http, zip_fixtures)
    zip_fixtures.seek(0)
    second = envoyer(http, zip_fixtures)
    assert premier != second


def test_get_renvoie_la_structure(http, zip_fixtures):
    analyse_id = envoyer(http, zip_fixtures)

    reponse = http.get("/analyses/" + analyse_id)

    assert reponse.status_code == 200
    classes = {c["nom"]: c for c in reponse.json()}
    assert len(classes) == 7
    assert classes["Chien"]["parent"] == "Animal"
    assert classes["Nageur"]["genre"] == "interface"
    assert classes["Couleur"]["genre"] == "enum"


def test_get_doc_renvoie_le_markdown(http, zip_fixtures, faux_client):
    analyse_id = envoyer(http, zip_fixtures)

    reponse = http.get("/analyses/" + analyse_id + "/doc")

    assert reponse.status_code == 200
    assert reponse.headers["content-type"].startswith("text/plain")
    assert reponse.text.startswith("# Documentation du projet")
    assert "classDiagram" in reponse.text
    assert reponse.text.count(RESUME_FIXE) == 7
    assert len(faux_client.prompts) == 7


def test_analyse_inconnue_renvoie_404(http):
    for route in ("/analyses/inconnu", "/analyses/inconnu/doc"):
        reponse = http.get(route)
        assert reponse.status_code == 404
        assert reponse.json() == {"detail": "Analyse introuvable"}


def test_post_avec_un_faux_zip_renvoie_400(http):
    reponse = http.post(
        "/analyses", files={"fichier": ("projet.zip", io.BytesIO(b"pas un zip"), "application/zip")}
    )
    assert reponse.status_code == 400
    assert api.ANALYSES == {}


def test_post_sans_fichier_renvoie_422(http):
    assert http.post("/analyses").status_code == 422
