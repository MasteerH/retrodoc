FROM python:3.12-slim

WORKDIR /app

# Les dépendances d'abord : cette couche reste en cache tant que pyproject.toml ne change pas.
COPY pyproject.toml ./
COPY retrodoc ./retrodoc
RUN pip install --no-cache-dir .

# L'API ne tourne pas en root.
RUN useradd --create-home retrodoc
USER retrodoc

# Ollama tourne sur la machine hôte, pas dans le conteneur.
ENV OLLAMA_URL=http://host.docker.internal:11434

EXPOSE 8000
CMD ["uvicorn", "retrodoc.api:app", "--host", "0.0.0.0", "--port", "8000"]
