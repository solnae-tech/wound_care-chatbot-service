import json
import uuid
from app.queue.config import get_connection

def send_task(payload):

    connection = get_connection()
    channel = connection.channel()

    channel.queue_declare(queue='chat_queue')

    task_id = str(uuid.uuid4())
    payload["task_id"] = task_id

    channel.basic_publish(
        exchange='',
        routing_key='chat_queue',
        body=json.dumps(payload)
    )

    connection.close()

    return task_id