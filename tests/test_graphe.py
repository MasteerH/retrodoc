from retrodoc.graphe import construire_liens, exporter_mermaid


def test_lien_heritage(classes):
    assert ("Chien", "Animal", "herite") in construire_liens(classes)


def test_lien_implemente_seulement_si_interface_connue(classes):
    liens = construire_liens(classes)
    assert ("Nageur", "Vivant", "implemente") in liens
    assert ("Nageur", "Mobile", "implemente") in liens
    # Comparable et Cloneable ne sont pas des classes du projet
    assert all(cible not in ("Comparable", "Cloneable") for _, cible, _ in liens)


def test_lien_utilise(classes):
    liens = construire_liens(classes)
    assert ("Compteur", "Chien", "utilise") in liens
    assert ("Compteur", "Animal", "utilise") in liens


def test_aucun_lien_vers_une_classe_externe(classes):
    noms = {c.nom for c in classes}
    for source, cible, _ in construire_liens(classes):
        assert source in noms
        assert cible in noms


def test_pas_de_utilise_en_double_de_herite(classes):
    liens = construire_liens(classes)
    assert ("Chien", "Animal", "utilise") not in liens


def test_export_mermaid(classes):
    mermaid = exporter_mermaid(classes)
    lignes = [ligne.replace(" ", "") for ligne in mermaid.splitlines()]
    assert lignes[0] == "classDiagram"
    assert "Animal<|--Chien" in lignes
    assert "Vivant<|..Nageur" in lignes
    assert "Compteur-->Chien" in lignes
