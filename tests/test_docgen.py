from retrodoc.docgen import (
    construire_prompt,
    generer_documentation,
    lire_code,
    section_classe,
    signature,
    voisins,
)
from tests.conftest import RESUME_FIXE


def test_lire_code_commence_et_finit_sur_la_classe(par_nom):
    code = lire_code(par_nom["Chien"]).strip().splitlines()
    assert code[0].startswith("public class Chien")
    assert code[-1] == "}"


def test_signature_classe_avec_parent(par_nom):
    lignes = signature(par_nom["Chien"]).splitlines()
    assert lignes[0] == "class Chien extends Animal"
    assert "  + Chien(String nom)" in lignes
    assert "  + aboyer(int fois) : String" in lignes


def test_signature_sans_parent_ni_methode(par_nom):
    assert signature(par_nom["Couleur"]) == "enum Couleur"


def test_voisins_dans_les_deux_sens(par_nom, classes):
    assert {v.nom for v in voisins(par_nom["Animal"], classes)} == {"Chien", "Compteur"}
    assert {v.nom for v in voisins(par_nom["Chien"], classes)} == {"Animal", "Compteur"}


def test_prompt_contient_consigne_code_et_voisines(par_nom, classes):
    prompt = construire_prompt(par_nom["Chien"], classes)
    assert "N'invente aucune méthode" in prompt
    assert "public class Chien extends Animal" in prompt
    assert "class Animal" in prompt
    assert "class Compteur" in prompt


def test_prompt_sans_voisine(par_nom, classes):
    assert "Aucune" in construire_prompt(par_nom["Couleur"], classes)


def test_section_classe(par_nom):
    section = section_classe(par_nom["Chien"], "  Un chien.  ")
    assert section.startswith("### Chien")
    assert "hérite de **Animal**" in section
    assert "implémente **Comparable**, **Cloneable**" in section
    assert "Un chien." in section
    assert "- `private String nom`" in section
    assert "- `aboyer(int fois) : String`" in section


def test_documentation_complete(classes, faux_client):
    doc = generer_documentation(classes, faux_client)

    assert doc.startswith("# Documentation du projet")
    assert "7 types : 3 classes, 3 interfaces, 1 enums" in doc
    assert "```mermaid\nclassDiagram" in doc
    for classe in classes:
        assert "### " + classe.nom in doc
    assert doc.count(RESUME_FIXE) == len(classes)


def test_un_appel_au_llm_par_classe(classes, faux_client):
    generer_documentation(classes, faux_client)
    assert len(faux_client.prompts) == len(classes)
