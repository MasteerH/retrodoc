from dataclasses import dataclass, field


@dataclass
class ParametreInfo:
    nom: str
    type: str

@dataclass
class FieldInfo:
    nom: str
    type: str
    visibilite: str

@dataclass
class MethodInfo:
    est_constructeur: bool
    nom: str
    visibilite: str
    type_sortie: str | None = None
    parametres: list[ParametreInfo] = field(default_factory=list)

@dataclass
class ClassInfo:
    fichier: str
    ligne_debut: int
    ligne_fin: int
    nom: str
    genre: str
    parent: str | None = None
    interfaces: list[str] = field(default_factory=list)
    attributs: list[FieldInfo] = field(default_factory=list)
    methodes: list[MethodInfo] = field(default_factory=list)
    