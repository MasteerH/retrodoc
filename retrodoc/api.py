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
client: LLMClient = OllamaClient()


@app.post("/analyses")
def creer_analyse(fichier: UploadFile):
    dossier = tempfile.mkdtemp()
    zipfile.ZipFile(fichier.file).extractall(dossier)

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
