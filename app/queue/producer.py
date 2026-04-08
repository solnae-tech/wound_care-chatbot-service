import json
import pika
from app.queue.config import get_connection


CHAT_QUEUE = "chat_queue"
CHAT_DLQ = "chat_queue_dlq"

def send_task(payload):

    connection = get_connection()
    try:
        channel = connection.channel()
        channel.confirm_delivery()

        channel.queue_declare(queue=CHAT_DLQ, durable=True)
        channel.queue_declare(queue=CHAT_QUEUE)

        job_id = payload.get("job_id")
        if not job_id:
            raise ValueError("job_id is required in payload")

        channel.basic_publish(
            exchange="",
            routing_key=CHAT_QUEUE,
            body=json.dumps(payload),
            properties=pika.BasicProperties(
                delivery_mode=2,
                content_type="application/json",
            ),
            mandatory=True,
        )

        return job_id
    finally:
        connection.close()