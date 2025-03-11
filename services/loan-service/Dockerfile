# Utilisation d'une image Python légère
FROM python:3.10-slim

# Définition du répertoire de travail
WORKDIR /app

# Copier tous les fichiers nécessaires dans le conteneur
COPY . .

# Installation des dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port utilisé par FastAPI
EXPOSE 8001

# Commande pour exécuter `db_setup.py` avant de lancer l'API
CMD ["sh", "-c", "python db/db_setup.py && uvicorn service_loan_requests:app --host 0.0.0.0 --port 8001"]