from fastapi import FastAPI
from pydantic import BaseModel
import pika
import json
import uvicorn

app = FastAPI()

# Définition du modèle Pydantic pour recevoir les données de la requête POST
class InsuranceRequest(BaseModel):
    cin: str
    interested: bool

# Fonction pour envoyer un message à RabbitMQ
def send_to_queue(queue_name, message):
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)
    channel.basic_publish(exchange='', routing_key=queue_name, body=json.dumps(message))
    connection.close()

@app.post("/offer-insurance/")
def offer_insurance(request: InsuranceRequest):
    if request.interested:
        message = "Envoyer un devis d'assurance habitation"
    else:
        message = "Client non intéressé par l'assurance"

    send_to_queue("insurance_offers", {"cin": request.cin, "message": message})
    
    return {"cin": request.cin, "status": message}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8006)
