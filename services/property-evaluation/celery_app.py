from celery import Celery
import os

# Détection de RabbitMQ dans Docker
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")

celery = Celery(
    "property_evaluation",
    broker=f"pyamqp://guest@{RABBITMQ_HOST}//",  # Utilise RabbitMQ
    backend="rpc://"  # Stocke les résultats sans Redis
)

# Indiquer le module qui contient les tâches
celery.autodiscover_tasks(['service_property_evaluation'])

celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    task_routes={
        "app.evaluate_property_task": {"queue": "property_evaluation_queue"}
    },
)
