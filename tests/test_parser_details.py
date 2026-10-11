from retrodoc.parser import extraire_types, parser, parser_fichier
from tests.conftest import FIXTURES


def test_visibilite_sans_static_ni_final():
    compteur = parser_fichier(str(FIXTURES / "Compteur.java"))[0]
    visibilites = {a.nom: a.visibilite for a in compteur.attributs}
    assert visibilites == {"total": "private", "NOM": "public", "chiens": "package"}


def test_visibilite_des_methodes():
    compteur = parser_fichier(str(FIXTURES / "Compteur.java"))[0]
    visibilites = {m.nom: m.visibilite for m in compteur.methodes}
    assert visibilites == {"ajouter": "package", "premier": "public"}


def test_methode_avec_parametres_et_type_de_sortie():
    chien = parser_fichier(str(FIXTURES / "Chien.java"))[0]
    aboyer = next(m for m in chien.methodes if m.nom == "aboyer")
    assert aboyer.type_sortie == "String"
    assert aboyer.est_constructeur is False
    assert [(p.type, p.nom) for p in aboyer.parametres] == [("int", "fois")]


def test_constructeur_sans_type_de_sortie():
    chien = parser_fichier(str(FIXTURES / "Chien.java"))[0]
    constructeur = next(m for m in chien.methodes if m.est_constructeur)
    assert constructeur.nom == "Chien"
    assert constructeur.type_sortie is None


def test_enum():
    couleur = parser_fichier(str(FIXTURES / "Couleur.java"))[0]
    assert couleur.nom == "Couleur"
    assert couleur.genre == "enum"
    assert couleur.parent is None


def test_interface_attributs_et_methodes():
    nageur = parser_fichier(str(FIXTURES / "Nageur.java"))[0]
    assert [a.nom for a in nageur.attributs] == ["VITESSE"]
    assert [m.nom for m in nageur.methodes] == ["nager"]


def test_lignes_de_la_classe():
    animal = parser_fichier(str(FIXTURES / "Animal.java"))[0]
    assert animal.ligne_debut < animal.ligne_fin
    assert animal.fichier.endswith("Animal.java")


def test_extraire_types_generiques_et_tableaux():
    arbre = parser.parse(b"class A { Map<Integer, Salle> x; String[] y; List<List<Oeuvre>> z; }")
    assert extraire_types(arbre.root_node) == [
        "Map", "Integer", "Salle", "String", "List", "List", "Oeuvre",
    ]


def test_dependances_sans_doublon_ni_soi_meme():
    compteur = parser_fichier(str(FIXTURES / "Compteur.java"))[0]
    assert compteur.dependances == sorted(set(compteur.dependances))
    assert "Compteur" not in compteur.dependances
    assert {"Chien", "Animal", "List", "ArrayList"} <= set(compteur.dependances)
