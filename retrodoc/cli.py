from pathlib import Path
from retrodoc.parser import parser_fichier
from retrodoc.models import ClassInfo
from dataclasses import asdict
import json
import argparse

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
    lecteur.add_argument("commande", choices=["analyze"])
    lecteur.add_argument("dossier")
    args = lecteur.parse_args()

    classes = analyser_dossier(args.dossier)
    ecrire_json(classes, "analyse.json")
    print(len(classes), "classes trouvées")










if __name__ == "__main__":
    main()