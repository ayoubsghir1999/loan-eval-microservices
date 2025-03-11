# service_notification.py
from fastapi import FastAPI, HTTPException
import pika
import json
import uvicorn
import threading

app = FastAPI()

# Base en mémoire pour stocker les notifications
notifications_db = {}

def get_rabbitmq_connection():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        return connection
    except Exception as e:
        print(f"❌ Erreur de connexion à RabbitMQ : {e}")
        return None

def send_to_queue(queue_name, message):
    connection = get_rabbitmq_connection()
    if not connection:
        return
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)
    channel.basic_publish(exchange='', routing_key=queue_name, body=json.dumps(message))
    connection.close()
    print(f"📩 Message envoyé à {queue_name}: {message}")

def callback(ch, method, properties, body):
    data = json.loads(body)
    cin = data["cin"]
    decision = data["decision"]

    print(f"📩 Notification reçue pour {cin}, décision: {decision}")

    # Stocker la notification en mémoire
    if cin not in notifications_db:
        notifications_db[cin] = []
    notifications_db[cin].append({"decision": decision})

    # Si le prêt est approuvé, proposer une assurance habitation
    if decision == "Approuvé":
        print(f"📢 Proposition d'assurance envoyée à {cin}")
        send_to_queue("insurance_offers", {"cin": cin, "proposition": "Voulez-vous une assurance habitation?"})

def listen_to_rabbitmq():
    connection = get_rabbitmq_connection()
    if not connection:
        print("❌ Impossible de se connecter à RabbitMQ.")
        return

    channel = connection.channel()
    channel.queue_declare(queue="loan_decision_results")
    channel.basic_consume(queue="loan_decision_results", on_message_callback=callback, auto_ack=True)

    print("📢 Service Notification en attente des décisions de prêt...")
    channel.start_consuming()

@app.get("/start-notification-listener/")
def start_listener():
    threading.Thread(target=listen_to_rabbitmq, daemon=True).start()
    return {"status": "Notification listener started"}

@app.get("/notifications/{cin}")
def get_notifications(cin: str):
    if cin not in notifications_db:
        raise HTTPException(status_code=404, detail="Aucune notification trouvée pour ce client.")
    return {"cin": cin, "notifications": notifications_db[cin]}

# Lancer l'écoute dès que le service démarre
threading.Thread(target=listen_to_rabbitmq, daemon=True).start()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8005)
