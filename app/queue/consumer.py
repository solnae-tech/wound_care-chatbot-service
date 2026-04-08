import json
import pika
from app.queue.config import get_connection
from app.core.chatbot import chatbot
from app.queue.result_queue import send_result

CHAT_QUEUE = "chat_queue"
CHAT_DLQ = "chat_queue_dlq"
MAX_RETRIES = 3


def _normalize_result(payload, raw_result):
    if isinstance(raw_result, dict):
        answer = raw_result.get("answer", "")
        medical_attention_needed = raw_result.get("medical_attention_needed", "no")
        severity = raw_result.get("severity", "low")
    else:
        answer = str(raw_result)
        medical_attention_needed = "no"
        severity = "low"

    return {
        "user_id": payload.get("user_id"),
        "job_id": payload.get("job_id"),
        "answer": answer,
        "medical_attention_needed": medical_attention_needed,
        "severity": severity,
    }

def callback(ch, method, properties, body):
    try:
        payload = json.loads(body)
        job_id = payload.get("job_id")

        if not job_id:
            raise ValueError("job_id missing in chat queue payload")

        raw_result = chatbot(payload)
        result = _normalize_result(payload, raw_result)

        send_result(job_id, result)
        print("Published result for job:", job_id, result)
        print(f"Processed job {job_id}")
        
        # Acknowledge only after successful processing
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"Error processing task: {e}")
        import traceback
        traceback.print_exc()  # Print full stack trace for debugging

        headers = dict(properties.headers or {}) if properties else {}
        current_retry = int(headers.get("x-retry-count", 0))

        if current_retry < MAX_RETRIES:
            headers["x-retry-count"] = current_retry + 1
            ch.basic_publish(
                exchange="",
                routing_key=CHAT_QUEUE,
                body=body,
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type="application/json",
                    headers=headers,
                ),
                mandatory=True,
            )
            ch.basic_ack(delivery_tag=method.delivery_tag)
            print(f"Requeued job with retry {current_retry + 1}/{MAX_RETRIES}")
            return

        headers["x-final-error"] = str(e)
        ch.basic_publish(
            exchange="",
            routing_key=CHAT_DLQ,
            body=body,
            properties=pika.BasicProperties(
                delivery_mode=2,
                content_type="application/json",
                headers=headers,
            ),
            mandatory=True,
        )
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print("Moved job to DLQ after max retries")

def start_worker():

    connection = get_connection()
    channel = connection.channel()

    channel.queue_declare(queue=CHAT_DLQ, durable=True)
    channel.queue_declare(queue=CHAT_QUEUE)
    channel.basic_qos(prefetch_count=1)

    channel.basic_consume(
        queue=CHAT_QUEUE,
        on_message_callback=callback,
        auto_ack=False  # Manual acknowledgment for reliability
    )

    print("Worker started...")
    channel.start_consuming()


if __name__ == "__main__":
    start_worker()