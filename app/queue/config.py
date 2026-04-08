from dotenv import load_dotenv
import os
import pika
import ssl

load_dotenv()

def get_connection():
    url = os.getenv("CLOUDAMQP_URL")

    if url:
        params = pika.URLParameters(url)
        params.heartbeat = int(os.getenv("RABBITMQ_HEARTBEAT", "60"))
        params.blocked_connection_timeout = int(os.getenv("RABBITMQ_BLOCKED_TIMEOUT", "30"))

        # Ensure TLS is enabled for amqps URLs.
        if url.startswith("amqps://") and params.ssl_options is None:
            context = ssl.create_default_context()
            params.ssl_options = pika.SSLOptions(context)

        return pika.BlockingConnection(params)

    host = os.getenv("RABBITMQ_HOST", "localhost")
    params = pika.ConnectionParameters(
        host=host,
        heartbeat=int(os.getenv("RABBITMQ_HEARTBEAT", "60")),
        blocked_connection_timeout=int(os.getenv("RABBITMQ_BLOCKED_TIMEOUT", "30")),
    )
    return pika.BlockingConnection(params)