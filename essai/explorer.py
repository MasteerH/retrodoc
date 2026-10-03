import tree_sitter_java
from tree_sitter import Language, Parser

JAVA = Language(tree_sitter_java.language())
parser = Parser(JAVA)

code = open("essai/Chien.java", "rb").read()
tree = parser.parse(code)
racine = tree.root_node


def afficher(noeud, niveau):
    if not noeud.is_named:
        return

    indentation = "  " * niveau

    if len(noeud.children) == 0:
        print(indentation + noeud.type + " : " + noeud.text.decode())
    else:
        print(indentation + noeud.type)

    for enfant in noeud.children:
        afficher(enfant, niveau + 1)


afficher(racine, 0)
for enfant in racine.children:
    if enfant.type == "class_declaration":
        print("Classe : " + enfant.child_by_field_name("name").text.decode())
        print("Parent : " + enfant.child_by_field_name("superclass").named_children[0].text.decode())