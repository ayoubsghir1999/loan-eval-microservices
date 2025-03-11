# service_credit_check.py
from fastapi import FastAPI, HTTPException
import sqlite3
import pika
import json
from pydantic import BaseModel
import uvicorn
import os
import sys
sys.path.append("/app")  # Ajoute `/app` dans le PATH pour que Python trouve `celery_app`
from celery_app import celery
import threading

app = FastAPI()

class CreditCheckRequest(BaseModel):
    cin: str
# Connexion à la base de données SQLite (éviter "database is locked")
def get_db_connection():
    conn = sqlite3.connect("/app/db/loan_requests.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# Détecter l’hôte RabbitMQ (support Docker et local)
def get_rabbitmq_host():
    return os.getenv("RABBITMQ_HOST", "rabbitmq")

# Connexion RabbitMQ persistante (éviter reconnections multiples)
def get_rabbitmq_connection():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(get_rabbitmq_host()))
        return connection
    except Exception as e:
        print(f"❌ Erreur de connexion à RabbitMQ : {e}")
        return None

# Fonction pour envoyer un message à RabbitMQ
# def send_to_queue(queue_name, message):
#     connection = get_rabbitmq_connection()
#     if not connection:
#         print("❌ Impossible d'envoyer le message, RabbitMQ non accessible.")
#         return
    
#     try:
#         channel = connection.channel()
#         channel.queue_declare(queue=queue_name)
#         channel.basic_publish(exchange='', routing_key=queue_name, body=json.dumps(message))
#         print(f"✅ Message envoyé à {queue_name} : {message}")
#     except Exception as e:
#         print(f"❌ Erreur lors de l'envoi du message à RabbitMQ : {e}")
#     finally:
#         connection.close()

def send_to_queue(queue_name, message):
    try:
        rabbitmq_host = get_rabbitmq_host()  # Utiliser la config dynamique
        print(f"rabbitmq host name :", rabbitmq_host)
        connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitmq_host))
        channel = connection.channel()
        print("✅ Connexion à RabbitMQ réussie !")
        channel.queue_declare(queue=queue_name)
        print(f"📩 Envoi du message à la queue '{queue_name}': {message}")
        channel.basic_publish(exchange='', routing_key=queue_name, body=json.dumps(message))
        print(f"✅ Message envoyé avec succès.")
        connection.close()
    except Exception as e:
        print("❌ Erreur de connexion à RabbitMQ :", e)

# Tâche Celery pour vérifier le crédit

@celery.task(name="app.check_credit_task", queue="credit_check_queue")
def check_credit_task(cin: str):
    print(f"🟢 Traitement de la vérification du crédit pour {cin}...")

    # Connexion à la base de données SQLite
    conn = sqlite3.connect("/app/db/loan_requests.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients_credit WHERE cin = ?", (cin,))
    client = cursor.fetchone()
    
    if not client:
        return {"cin": cin, "decision": "Rejeté - Client introuvable"}
    
        # ✅ Convertir correctement en dictionnaire
    columns = [column[0] for column in cursor.description]  # Récupère les noms des colonnes
    client = dict(zip(columns, client))  # Associe chaque colonne à sa valeur

    print(f" client is :", client)
    
    # Évaluation du crédit
    score = client["score_credit"]
    incidents = client["incidents_paiement"]
    revenus_stables = client["revenus_stables"]
    
    decision = "Approuvé" if score >= 700 and incidents == 0 and revenus_stables == "Oui" else "Rejeté"

    print(f"📩 Envoi du résultat au queue 'credit_check_results' : {decision}")

    # ✅ Ajout d'un try/except pour voir si l'envoi fonctionne
    try:
        send_to_queue("credit_check_results", {"cin": cin, "decision": decision})
        print(f"✅ Message bien envoyé à RabbitMQ: {cin} - {decision}")
    except Exception as e:
        print(f"❌ ERREUR lors de l'envoi à RabbitMQ: {e}")

    return {"cin": cin, "decision": decision}
    

# Callback pour écouter RabbitMQ
def callback(ch, method, properties, body):
    data = json.loads(body)
    cin = data.get("cin")
    print(f"📩 Message reçu de RabbitMQ : {data}")
    check_credit_task.apply_async(args=[cin])  # Exécuter la tâche Celery

# Fonction pour écouter la file RabbitMQ
def listen_to_rabbitmq():
    connection = get_rabbitmq_connection()
    if not connection:
        print("❌ RabbitMQ non disponible. Réessai...")
        return
    
    channel = connection.channel()
    channel.queue_declare(queue="loan_requests")
    channel.basic_consume(queue="loan_requests", on_message_callback=callback, auto_ack=True)

    print("✅ Service Credit Check en attente de messages sur loan_requests...")
    try:
        channel.start_consuming()
    except Exception as e:
        print(f"❌ Erreur RabbitMQ : {e}")
    finally:
        connection.close()

@app.post("/check-credit/")
def check_credit(request: CreditCheckRequest):
    task = check_credit_task.apply_async(args=[request.cin])
    return {"task_id": task.id, "message": "Vérification en cours"}

if __name__ == "__main__":
    threading.Thread(target=listen_to_rabbitmq, daemon=True).start()
    uvicorn.run(app, host="0.0.0.0", port=8002)

