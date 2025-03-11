from celery import Celery
import os

# Détection de RabbitMQ dans Docker
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")

celery = Celery(
    "credit_check",
    broker=f"pyamqp://guest@{RABBITMQ_HOST}//",  # Utilise RabbitMQ
    backend="rpc://"  # Stocke les résultats sans Redis
)

# Indiquer le module qui contient les tâches
celery.autodiscover_tasks(['service_credit_check'])

celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    task_routes={
        "app.check_credit_task": {"queue": "credit_check_queue"}
    },
)

