import json
from app.queue.config import get_connection
from app.core.chatbot import chatbot
from app.store.result_store import save_result

def callback(ch, method, properties, body):
    try:
        payload = json.loads(body)
        task_id = payload.get("task_id")

        result = chatbot(payload)

        save_result(task_id, result)
        print("Saving result:", task_id, result)
        print(f"Processed task {task_id}")
        
        # Acknowledge only after successful processing
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"Error processing task: {e}")
        import traceback
        traceback.print_exc()  # Print full stack trace for debugging
        # Reject and requeue on failure
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

def start_worker():

    connection = get_connection()
    channel = connection.channel()

    channel.queue_declare(queue='chat_queue')

    channel.basic_consume(
        queue='chat_queue',
        on_message_callback=callback,
        auto_ack=False  # Manual acknowledgment for reliability
    )

    print("Worker started...")
    channel.start_consuming()


if __name__ == "__main__":
    start_worker()