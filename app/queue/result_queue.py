import json
from typing import Any, Dict
import pika

from app.queue.config import get_connection

RESULT_QUEUE = "result_queue"


def send_result(job_id: str, result: Dict[str, Any]) -> None:
    """Publish a processed chatbot result to RabbitMQ."""
    connection = get_connection()
    try:
        channel = connection.channel()
        channel.confirm_delivery()
        channel.queue_declare(queue=RESULT_QUEUE)

        payload = {
            "job_id": job_id,
            "result": result,
        }

        channel.basic_publish(
            exchange="",
            routing_key=RESULT_QUEUE,
            body=json.dumps(payload),
            properties=pika.BasicProperties(
                delivery_mode=2,
                content_type="application/json",
            ),
            mandatory=True,
        )
    finally:
        connection.close()


def drain_results(max_messages: int = 100) -> Dict[str, Dict[str, Any]]:
    """Drain available result messages from RabbitMQ into a job_id-keyed dict."""
    collected: Dict[str, Dict[str, Any]] = {}

    connection = get_connection()
    try:
        channel = connection.channel()
        channel.queue_declare(queue=RESULT_QUEUE)

        for _ in range(max_messages):
            method_frame, _, body = channel.basic_get(queue=RESULT_QUEUE, auto_ack=False)
            if method_frame is None:
                break

            try:
                payload = json.loads(body)
                job_id = payload.get("job_id")
                result = payload.get("result")
                if job_id is not None and result is not None:
                    collected[job_id] = result
                channel.basic_ack(delivery_tag=method_frame.delivery_tag)
            except Exception:
                # Corrupt payloads are dropped so they do not block the queue forever.
                channel.basic_ack(delivery_tag=method_frame.delivery_tag)

        return collected
    finally:
        connection.close()
