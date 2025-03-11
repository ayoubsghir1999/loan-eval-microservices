# service_loan_requests.py
from fastapi import FastAPI, HTTPException
import sqlite3
import uvicorn
import pika
import json
from pydantic import BaseModel
import uuid
import datetime
import os

app = FastAPI()

# Définition du modèle de données attendu pour une demande de prêt
class LoanRequest(BaseModel):
    cin: str
    ville: str
    montant: float
    duree: int

# Connexion à la base de données SQLite
def get_db_connection():
    conn = sqlite3.connect("/app/db/loan_requests.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")  # Permet plusieurs accès simultanés
    return conn


# Détecter l’hôte RabbitMQ (pour s'adapter à Docker et au mode local)
def get_rabbitmq_host():
    return os.getenv("RABBITMQ_HOST", "localhost")  # Par défaut, localhost

# Fonction pour envoyer un message à RabbitMQ
def send_to_queue(queue_name, message):
    try:
        rabbitmq_host = get_rabbitmq_host()  # Utiliser la config dynamique
        print(f"rabbitmq host name :", rabbitmq_host)
        connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitmq_host))
        channel = connection.channel()
        print("✅ Connexion à RabbitMQ réussie !")
        channel.queue_declare(queue=queue_name)
        channel.basic_publish(exchange='', routing_key=queue_name, body=json.dumps(message))
        connection.close()
    except Exception as e:
        print("❌ Erreur de connexion à RabbitMQ :", e)


# Endpoint pour créer une demande de prêt
@app.post("/loan-request/")
def create_loan_request(request: LoanRequest):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Vérifier si le client existe
    cursor.execute("SELECT * FROM clients_credit WHERE cin = ?", (request.cin,))
    client = cursor.fetchone()
    if not client:
        raise HTTPException(status_code=404, detail="Client non trouvé")

    # Vérifier si une demande en attente existe déjà
    cursor.execute("SELECT * FROM loan_requests WHERE cin = ? AND etat = 'en attente'", (request.cin,))
    existing_request = cursor.fetchone()
    if existing_request:
        raise HTTPException(status_code=409, detail="Une demande de prêt est déjà en attente.")
    
    print(f"isinstance(request.montant, (int, float))", isinstance(request.montant, (int, float)))
    print(f"isinstance(request.duree, int)", isinstance(request.duree, int))

    # Vérifier si le montant et la durée sont valides
    if not isinstance(request.montant, (int, float)) or not isinstance(request.duree, int):
        raise HTTPException(status_code=400, detail=f"Type invalide : montant={type(request.montant)}, duree={type(request.duree)}")


    # 📌 Forcer le casting et valider les valeurs
    try:
        montant = float(request.montant)
        duree = int(request.duree)
    except ValueError:
        raise HTTPException(status_code=400, detail="Montant doit être un nombre décimal et durée un entier.")

    if montant <= 0 or duree <= 0:
        raise HTTPException(status_code=400, detail="Montant et durée doivent être positifs")


   # Générer  la date de soumission
    date_soumission = datetime.datetime.now().isoformat()
    print(date_soumission)
    # 📌 Ajout d'un log pour voir les données avant insertion
    print(f"🔍 Données insérées :  cin={request.cin}, montant={request.montant}, duree={request.duree}, etat='en attente', date_soumission={date_soumission}")

    # Ajouter la demande de prêt avec l’état "en attente"
    cursor.execute(
        "INSERT INTO loan_requests (cin, montant, duree, etat, date_soumission) VALUES (?, ?, ?, ?, ?)",
        (request.cin, float(request.montant), int(request.duree), "en attente", date_soumission),
    )
    conn.commit()

    # Récupérer l'ID auto-généré
    loan_id = cursor.lastrowid

    # Envoyer la demande pour validation
    send_to_queue("loan_requests", {
        "id": loan_id,
        "cin": request.cin,
        "montant": request.montant,
        "duree": request.duree,
        "date_soumission": date_soumission
    })

    conn.close()
    return {
        "message": "Demande de prêt créée et en attente d'évaluation",
        "id": loan_id,
        "cin": request.cin,
        "montant": request.montant,
        "duree": request.duree,
        "ville": request.ville,
        "date_soumission": date_soumission
    }

# Endpoint pour lister toutes les demandes de prêt
@app.get("/loan-requests/")
def list_loan_requests():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM loan_requests")
    loans = cursor.fetchall()
    conn.close()
    
    return [dict(loan) for loan in loans]

@app.get("/clients-credits/")
def list_loan_requests():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients_credit")
    credits = cursor.fetchall()
    conn.close()
    
    return [dict(credit) for credit in credits]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)

