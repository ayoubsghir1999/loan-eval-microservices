import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Déclarer une queue pour voir si elle apparaît dans RabbitMQ
channel.queue_declare(queue="test_queue")

print("✅ Queue 'test_queue' créée avec succès !")
connection.close()
