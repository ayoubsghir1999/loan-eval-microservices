# Utilisation d'une image Python légère
FROM python:3.10-slim

# Définition du répertoire de travail
WORKDIR /app

# Copier tous les fichiers du dossier `credit-check` dans `/app`
COPY . .

ENV PYTHONPATH=/app

# Installation des dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port utilisé par FastAPI
EXPOSE 8002

# Commande pour démarrer Celery et FastAPI
CMD ["sh", "-c", "celery -A celery_app worker --loglevel=info & uvicorn service_credit_check:app --host 0.0.0.0 --port 8002"]
