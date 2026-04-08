import json
from app.queue.config import get_connection
from app.core.chatbot import chatbot
from app.store.result_store import save_result

def callback(ch, method, properties, body):

    payload = json.loads(body)
    task_id = payload.get("task_id")

    result = chatbot(payload)

    save_result(task_id, result)
    print("Saving result:", task_id, result)
    print(f"Processed task {task_id}")

def start_worker():

    connection = get_connection()
    channel = connection.channel()

    channel.queue_declare(queue='chat_queue')

    channel.basic_consume(
        queue='chat_queue',
        on_message_callback=callback,
        auto_ack=True
    )

    print("Worker started...")
    channel.start_consuming()


if __name__ == "__main__":
    start_worker()