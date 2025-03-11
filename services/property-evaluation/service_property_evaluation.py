# service_property_evaluation.py
from fastapi import FastAPI, HTTPException
import sqlite3
import pika
import json
import uvicorn
import logging
from pydantic import BaseModel
import sys
sys.path.append("/app")  # Ajoute le dossier au chemin d'import
from celery_app import celery

app = FastAPI()

# Connexion à la base de données SQLite
def get_db_connection():
    conn = sqlite3.connect("/app/db/loan_requests.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# Base de données externe : prix du m² par ville
price_per_sqm = {
    "Paris": 10500,
    "Lyon": 5000,
    "Marseille": 4000,
    "Toulouse": 3500,
    "Bordeaux": 4500,
    "Nice": 6000
}

# Fonction pour envoyer un message à RabbitMQ
def send_to_queue(queue_name, message):
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    if not connection:
        print("❌ Impossible d'envoyer le message, RabbitMQ non accessible.")
        return
    try:
        channel = connection.channel()
        channel.queue_declare(queue=queue_name)
        channel.basic_publish(exchange='', routing_key=queue_name, body=json.dumps(message))
        print(f"✅ Message envoyé à {queue_name} : {message}")
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi du message à RabbitMQ : {e}")
    finally:
        connection.close()

# Modèle de requête pour FastAPI
class PropertyEvaluationRequest(BaseModel):
    cin: str
    city: str
    sqm: float

# Tâche asynchrone Celery pour l'évaluation du bien
@celery.task(name="app.evaluate_property_task", queue="property_evaluation_queue")
def evaluate_property_task(cin: str, city: str, sqm: float):
    print(f"🟢 Évaluation du bien pour {cin} dans {city} ({sqm}m²)...")

    if city not in price_per_sqm:
        return {"cin": cin, "decision": "Non valide - Ville inconnue"}

    estimated_value = price_per_sqm[city] * sqm
    decision = "Valide" if estimated_value >= 50000 else "Non valide"

    # Envoyer le résultat à RabbitMQ
    send_to_queue("property_evaluation_results", {"cin": cin, "decision": decision})
    
    print(f"✅ Résultat évaluation pour {cin}: {decision} ({estimated_value}€)")
    return {"cin": cin, "decision": decision, "estimated_value": estimated_value}

@app.post("/evaluate-property/")
def evaluate_property(request: PropertyEvaluationRequest):
    task = evaluate_property_task.apply_async(args=[request.cin, request.city, request.sqm])
    return {"task_id": task.id, "message": "Évaluation en cours"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)
