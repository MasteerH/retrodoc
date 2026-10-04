from retrodoc.models import ClassInfo
from retrodoc.models import FieldInfo
from retrodoc.models import MethodInfo
from retrodoc.models import ParametreInfo
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

        interfaces = []
        attributes = []
        methodes = []

        if enfant.type in ("class_declaration", "interface_declaration"):
            noeud_parent = enfant.child_by_field_name("superclass")
            noeud_interface = enfant.child_by_field_name("interfaces")
            noeud_corps = enfant.child_by_field_name("body")

            for kid in noeud_corps.named_children:
                if kid.type in ("constant_declaration", "field_declaration"):
                    declarateur = kid.child_by_field_name("declarator")

                    type_att = kid.child_by_field_name("type").text.decode()

                    nom_att = declarateur.child_by_field_name("name").text.decode()
                    
                    visibility = "package"
                    for i in kid.named_children:
                        if i.type == "modifiers":
                            visibility = i.text.decode()

                    field  = FieldInfo(nom= nom_att, type = type_att, visibilite = visibility)
                    attributes.append(field)

                elif kid.type in ("method_declaration", "constructor_declaration"):
                    
                    type_sortie = None
                    if kid.type == "method_declaration":
                        type_sortie = kid.child_by_field_name("type").text.decode()

                    est_constructeur = False
                    if kid.type == "constructor_declaration":
                        est_constructeur = True

                    nom_methode = kid.child_by_field_name("name").text.decode()

                    visibility = "package"
                    for i in kid.named_children:
                        if i.type == "modifiers":
                            visibility = i.text.decode()
                    parametres = []
                    param = kid.child_by_field_name("parameters")
                    for parametre in param.named_children:
                        nom_param = parametre.child_by_field_name("name").text.decode()
                        type_param = parametre.child_by_field_name("type").text.decode()
                        para = ParametreInfo(nom = nom_param, type = type_param)
                        parametres.append(para)
                    
                        

                    method = MethodInfo(est_constructeur = est_constructeur, nom = nom_methode, visibilite = visibility, type_sortie = type_sortie, parametres = parametres)
                    methodes.append(method)


            if enfant.type == "class_declaration":
                if noeud_interface is not None:
                    type_list = noeud_interface.named_children[0]

                    for interface in type_list.named_children:
                        interfaces.append(interface.text.decode())
            else:
                for kid in enfant.named_children:
                    if kid.type == "extends_interfaces":
                        type_list = kid.named_children[0]
                        for interface in type_list.named_children:
                            interfaces.append(interface.text.decode())

            if noeud_parent is None:
                parent = None

            else:
                parent = enfant.child_by_field_name("superclass").named_children[0].text.decode()

            
            genre = "interface"
            if enfant.type == "class_declaration":
                genre = "class"

            classe = ClassInfo(
                nom = enfant.child_by_field_name("name").text.decode(),
                parent = parent,
                genre = genre,
                fichier = chemin,
                ligne_debut = enfant.start_point[0] + 1,
                ligne_fin = enfant.end_point[0]+1,
                interfaces = interfaces,
                attributs = attributes,
                methodes = methodes
            )
            liste.append(classe)
    return liste
if __name__ == "__main__":
    print(parser_fichier("essai/Chien.java"))
    print(parser_fichier("essai/Animal.java"))
    print(parser_fichier("essai/Nageur.java"))
