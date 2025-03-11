# service_decision.py
from fastapi import FastAPI
import pika
import json
import threading
import uvicorn
import time

app = FastAPI()

# Variables pour stocker les décisions temporaires
credit_results = {}
property_results = {}

# Endpoint racine pour vérifier que le service fonctionne
@app.get("/")
def read_root():
    return {"message": "Service Decision est en cours d'exécution."}

# Fonction pour envoyer un message à RabbitMQ
def send_to_queue(queue_name, message):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        channel = connection.channel()
        channel.queue_declare(queue=queue_name)
        channel.basic_publish(exchange='', routing_key=queue_name, body=json.dumps(message))
        connection.close()
        print(f"✅ Message envoyé à {queue_name}: {message}")
    except Exception as e:
        print(f"❌ Erreur d'envoi à RabbitMQ: {e}")

# Vérifier si les deux résultats sont reçus et prendre une décision
def check_final_decision(cin):
    if cin in credit_results and cin in property_results:
        if credit_results[cin] == "Approuvé" and property_results[cin] == "Valide":
            decision = "Approuvé"
        else:
            decision = "Rejeté"
        
        # Envoyer la décision finale à RabbitMQ
        send_to_queue("loan_decision_results", {"cin": cin, "decision": decision})
        print(f"📢 Décision finale pour {cin}: {decision}")

        # Nettoyer les résultats après la prise de décision
        del credit_results[cin]
        del property_results[cin]

# Callback pour les résultats de vérification de crédit
def credit_callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        print(f"📩 Message reçu de credit_check_results: {data}")  
        cin = data.get("cin")
        decision = data.get("decision")

        if not cin or not decision:
            print("❌ Erreur: Message de crédit invalide:", data)
            return

        credit_results[cin] = decision
        check_final_decision(cin)
    except Exception as e:
        print(f"❌ Erreur dans credit_callback: {e}")

# Callback pour les résultats d'évaluation immobilière
def property_callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        print(f"📩 Message reçu de property_evaluation_results: {data}")
        cin = data.get("cin")
        decision = data.get("decision")

        if not cin or not decision:
            print("❌ Erreur: Message d'évaluation immobilière invalide:", data)
            return

        property_results[cin] = decision
        check_final_decision(cin)
    except Exception as e:
        print(f"❌ Erreur dans property_callback: {e}")

# Écouter RabbitMQ en arrière-plan avec gestion des erreurs
def start_listening():
    while True:  # Boucle infinie pour gérer les erreurs de connexion
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
            channel = connection.channel()

            # Déclarer les queues
            channel.queue_declare(queue="credit_check_results")
            channel.queue_declare(queue="property_evaluation_results")

            # Associer les callbacks
            channel.basic_consume(queue="credit_check_results", on_message_callback=credit_callback, auto_ack=False)
            channel.basic_consume(queue="property_evaluation_results", on_message_callback=property_callback, auto_ack=False)

            print("🔄 En attente des résultats de crédit et d'évaluation immobilière...")
            channel.start_consuming()
        except Exception as e:
            print(f"❌ Erreur dans start_listening: {e}. Réessai dans 5 secondes...")
            time.sleep(5)  # Attendre avant de réessayer

# Lancer l'écoute de RabbitMQ en arrière-plan au démarrage de l'application
@app.on_event("startup")
def startup_event():
    thread = threading.Thread(target=start_listening, daemon=True)
    thread.start()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8004)
