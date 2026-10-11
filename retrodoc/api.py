import os
import tempfile
import uuid
import zipfile
from dataclasses import asdict

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.responses import PlainTextResponse

from retrodoc.cli import analyser_dossier
from retrodoc.docgen import generer_documentation
from retrodoc.llm import LLMClient, OllamaClient

app = FastAPI(title="RetroDoc")
ANALYSES = {}
# Dans Docker, Ollama n'est pas sur "localhost" : l'adresse se règle avec OLLAMA_URL.
client: LLMClient = OllamaClient(url=os.environ.get("OLLAMA_URL", "http://localhost:11434"))


@app.post("/analyses")
def creer_analyse(fichier: UploadFile):
    dossier = tempfile.mkdtemp()
    try:
        zipfile.ZipFile(fichier.file).extractall(dossier)
    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Le fichier envoyé n'est pas un zip valide")

    classes = analyser_dossier(dossier)

    analyse_id = str(uuid.uuid4())
    ANALYSES[analyse_id] = classes
    return {"id": analyse_id}



@app.get("/analyses/{analyse_id}")
def lire_analyse(analyse_id: str):
    if analyse_id not in ANALYSES:
        raise HTTPException(status_code=404, detail="Analyse introuvable")
    return [asdict(c) for c in ANALYSES[analyse_id]]

@app.get("/analyses/{analyse_id}/doc", response_class=PlainTextResponse)
def lire_doc(analyse_id: str):
    if analyse_id not in ANALYSES:
        raise HTTPException(status_code=404, detail="Analyse introuvable")
    return generer_documentation(ANALYSES[analyse_id], client)
