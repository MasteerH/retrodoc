from retrodoc.models import ClassInfo

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




if __name__ == "__main__":
    from retrodoc.cli import analyser_dossier
    classes = analyser_dossier(r"C:\Users\MasteerH Desktop\Desktop\3A\hackaton java POO\2024-2025-poo-java-g17-main")
    print(lire_code(classes[0]))
    print(signature(classes[0]))
