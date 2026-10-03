from retrodoc.models import ClassInfo
import tree_sitter_java
from tree_sitter import Language, Parser

JAVA = Language(tree_sitter_java.language())
parser = Parser(JAVA)


def parser_fichier(chemin: str) -> list[ClassInfo]:
    
    code = open(chemin, "rb").read()
    tree = parser.parse(code)
    racine = tree.root_node
    liste = []

    for enfant in racine.children:
        if enfant.type == "class_declaration":
            noeud_parent = enfant.child_by_field_name("superclass")
            if noeud_parent is None:
                parent = None
            else:
                parent = enfant.child_by_field_name("superclass").named_children[0].text.decode()
            classe = ClassInfo(
                nom = enfant.child_by_field_name("name").text.decode(),
                parent = parent,
                genre = "class",
                fichier = chemin,
                ligne_debut = enfant.start_point[0] + 1,
                ligne_fin = enfant.end_point[0]+1,
            )    
            liste.append(classe)
    return liste

print(parser_fichier("essai/Chien.java"))
print(parser_fichier("essai/Animal.java"))
