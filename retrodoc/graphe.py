from retrodoc.models import ClassInfo


def construire_liens(classes: list[ClassInfo]) -> list[tuple[str, str, str]]:
    noms_connus = {c.nom for c in classes}
    liens = []
    for classe in classes:
        if classe.parent in noms_connus:
            liens.append((classe.nom,classe.parent,"herite"))
        for interface in classe.interfaces:
            if interface in noms_connus:
                liens.append((classe.nom, interface, "implemente"))
        for dep in classe.dependances:
            if (dep in noms_connus) and (dep != classe.parent) and (dep not in classe.interfaces):
                liens.append((classe.nom, dep, "utilise"))
    return liens

def exporter_mermaid(classes: list[ClassInfo]) -> str:
    lignes = ["classDiagram"]
    for triplet in construire_liens(classes = classes):
        if triplet[2] == "herite":
            lignes.append("    " + triplet[1] + " <|-- " + triplet[0])
        elif triplet[2] == "implemente":
            lignes.append("    " + triplet[1] + " <|.. " + triplet[0])
        elif triplet[2] == "utilise":
            lignes.append("    " + triplet[0] + " --> " + triplet[1])
    return "\n".join(lignes)


if __name__ == "__main__":
    from retrodoc.cli import analyser_dossier
    classes = analyser_dossier(r"C:\Users\MasteerH Desktop\Desktop\3A\hackaton java POO\2024-2025-poo-java-g17-main")
    print(exporter_mermaid(classes))