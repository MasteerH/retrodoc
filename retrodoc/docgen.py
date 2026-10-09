from pathlib import Path

from retrodoc.graphe import construire_liens, exporter_mermaid
from retrodoc.llm import LLMClient
from retrodoc.models import ClassInfo

CONSIGNE = """Tu es un développeur Java qui rédige la documentation technique d'un projet.

Règles strictes :
- Décris uniquement ce qui est écrit dans le code fourni.
- N'invente aucune méthode, aucun attribut, aucun comportement.
- Si une information n'est pas dans le code, ne la suppose pas.
- Les classes voisines servent seulement à comprendre le contexte : ne les décris pas.
- Réponds en français, en 3 à 5 phrases, sans titre, sans liste, sans bloc de code."""

def lire_code(classe: ClassInfo) -> str:
    with open(classe.fichier,  "r", encoding="utf-8") as f:
        lignes = f.readlines()
    morceau = lignes[classe.ligne_debut - 1 : classe.ligne_fin]
    return "".join(morceau)


def signature(classe: ClassInfo) -> str:
    lignes = []
    if classe.parent:
        lignes.append(classe.genre + " " + classe.nom + " extends " + classe.parent)
    else:
        lignes.append(classe.genre + " " + classe.nom)

    for method in classe.methodes:
        ligne_methode = "  + " + method.nom + "("
        ligne_parametre = []
        for parametre in method.parametres:
            ligne_parametre.append(parametre.type + " " + parametre.nom)
        ligne_methode += ", ".join(ligne_parametre) + ")"
        if not method.est_constructeur:
            ligne_methode += " : " + method.type_sortie
        lignes.append(ligne_methode)
    return "\n".join(lignes)


def voisins(classe: ClassInfo, classes: list[ClassInfo]) -> list[ClassInfo]:
    noms_voisins = set()
    for source, cible, _ in construire_liens(classes):
        if source == classe.nom:
            noms_voisins.add(cible)
        if cible == classe.nom:
            noms_voisins.add(source)
    return [c for c in classes if c.nom in noms_voisins]


def construire_prompt(classe: ClassInfo, classes: list[ClassInfo]) -> str:
    blocs = [CONSIGNE]

    blocs.append("### Code de la classe " + classe.nom + "\n```java\n" + lire_code(classe).rstrip() + "\n```")

    signatures_voisines = [signature(v) for v in voisins(classe, classes)]
    if signatures_voisines:
        texte_voisines = "\n\n".join(signatures_voisines)
    else:
        texte_voisines = "Aucune"
    blocs.append("### Classes voisines (signatures seulement)\n" + texte_voisines)

    blocs.append("### Ta réponse\nRésume le rôle de la classe " + classe.nom + " :")
    return "\n\n".join(blocs)


def section_classe(classe: ClassInfo, resume: str) -> str:
    lignes = ["### " + classe.nom, ""]

    infos = "*" + classe.genre + "* · `" + Path(classe.fichier).name + "`"
    infos += " (lignes " + str(classe.ligne_debut) + "-" + str(classe.ligne_fin) + ")"
    if classe.parent:
        infos += " · hérite de **" + classe.parent + "**"
    if classe.interfaces:
        infos += " · implémente " + ", ".join("**" + i + "**" for i in classe.interfaces)
    lignes.append(infos)
    lignes.append("")

    lignes.append(resume.strip())
    lignes.append("")

    if classe.attributs:
        lignes.append("**Attributs**")
        lignes.append("")
        for attribut in classe.attributs:
            lignes.append("- `" + attribut.visibilite + " " + attribut.type + " " + attribut.nom + "`")
        lignes.append("")

    if classe.methodes:
        lignes.append("**Méthodes**")
        lignes.append("")
        for ligne_methode in signature(classe).splitlines()[1:]:
            lignes.append("- `" + ligne_methode.strip().removeprefix("+ ") + "`")
        lignes.append("")

    return "\n".join(lignes)


def generer_documentation(classes: list[ClassInfo], client: LLMClient) -> str:
    classes = sorted(classes, key=lambda c: c.nom)
    genres = [c.genre for c in classes]

    lignes = ["# Documentation du projet", ""]

    lignes.append("## Vue d'ensemble")
    lignes.append("")
    lignes.append(
        str(len(classes)) + " types : "
        + str(genres.count("class")) + " classes, "
        + str(genres.count("interface")) + " interfaces, "
        + str(genres.count("enum")) + " enums, "
        + str(sum(len(c.methodes) for c in classes)) + " méthodes."
    )
    lignes.append("")
    lignes.append("| Type | Genre | Hérite de | Fichier |")
    lignes.append("|---|---|---|---|")
    for c in classes:
        lien = "[" + c.nom + "](#" + c.nom.lower() + ")"
        lignes.append(
            "| " + lien + " | " + c.genre + " | " + (c.parent or "") + " | "
            + Path(c.fichier).name + " |"
        )
    lignes.append("")

    lignes.append("## Diagramme de classes")
    lignes.append("")
    lignes.append("```mermaid")
    lignes.append(exporter_mermaid(classes))
    lignes.append("```")
    lignes.append("")

    lignes.append("## Détail des classes")
    lignes.append("")
    for numero, classe in enumerate(classes, start=1):
        print("[" + str(numero) + "/" + str(len(classes)) + "] " + classe.nom)
        resume = client.generate(construire_prompt(classe, classes))
        lignes.append(section_classe(classe, resume))

    return "\n".join(lignes)


if __name__ == "__main__":
    from retrodoc.cli import analyser_dossier
    classes = analyser_dossier(r"C:\Users\MasteerH Desktop\Desktop\3A\hackaton java POO\2024-2025-poo-java-g17-main")
    c = {x.nom: x for x in classes}
    print(construire_prompt(c["MuseeSciences"], classes))