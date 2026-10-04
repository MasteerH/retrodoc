from retrodoc.parser import parser_fichier


def test_parser_fichier():
    classes = parser_fichier("tests/fixtures/Animal.java")
    assert len(classes) == 1
    assert classes[0].nom == "Animal"
    assert classes[0].parent is None


def test_classe_qui_herite():
    classes = parser_fichier("tests/fixtures/Chien.java")
    constructeur = False
    for i in classes[0].methodes:
        if i.est_constructeur:
            constructeur = True

    assert len(classes) == 1
    assert classes[0].interfaces == ["Comparable", "Cloneable"]
    assert classes[0].parent == "Animal"
    assert len(classes[0].attributs) == 2
    assert constructeur


def test_interface():
    classes = parser_fichier("tests/fixtures/Nageur.java")
    assert classes[0].genre == "interface"
    assert classes[0].interfaces == ["Vivant", "Mobile"]