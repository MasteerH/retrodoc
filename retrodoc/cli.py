import argparse
import json
from dataclasses import asdict
from pathlib import Path

from retrodoc.docgen import generer_documentation
from retrodoc.llm import OllamaClient
from retrodoc.models import ClassInfo
from retrodoc.parser import parser_fichier


def trouver_fichiers_java(dossier: str) -> list[str]:
    fichiers = Path(dossier).rglob("*.java")
    liste = []
    for fichier in fichiers:
        if fichier.is_file():
            liste.append(str(fichier))
    return liste



def analyser_dossier(dossier: str) -> list[ClassInfo]:
    classes_dossier = []

    for fichier in trouver_fichiers_java(dossier = dossier):
        classes_fichier = parser_fichier(fichier)
        classes_dossier.extend(classes_fichier)

    return classes_dossier

def ecrire_json(classes: list[ClassInfo], chemin_sortie: str) -> None:
    donnees = []
    for classe in classes:
        donnees.append(asdict(classe))
    with open(chemin_sortie, "w", encoding="utf-8") as f:
        json.dump(donnees, f, indent=2, ensure_ascii=False)

def main():
    lecteur = argparse.ArgumentParser()
    lecteur.add_argument("commande", choices=["analyze", "doc"])
    lecteur.add_argument("dossier")
    lecteur.add_argument("--sortie")
    lecteur.add_argument("--modele", default="qwen2.5-coder:7b")
    args = lecteur.parse_args()

    classes = analyser_dossier(args.dossier)
    print(len(classes), "classes trouvées")

    if args.commande == "analyze":
        sortie = args.sortie or "analyse.json"
        ecrire_json(classes, sortie)
    else:
        sortie = args.sortie or "DOCUMENTATION.md"
        client = OllamaClient(modele=args.modele)
        documentation = generer_documentation(classes, client)
        with open(sortie, "w", encoding="utf-8") as f:
            f.write(documentation)

    print("→", sortie)










if __name__ == "__main__":
    main()