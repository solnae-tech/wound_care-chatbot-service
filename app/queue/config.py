from dotenv import load_dotenv
import os
import pika
import ssl

load_dotenv()

def get_connection():
    url = os.getenv("CLOUDAMQP_URL")
    
    # If using local RabbitMQ (no SSL)
    if url and "localhost" in url:
        params = pika.URLParameters(url)
        return pika.BlockingConnection(params)
    
    # If using CloudAMQP (with SSL)
    if url and "cloudamqp.com" in url:
        params = pika.URLParameters(url)
        context = ssl.create_default_context()
        params.ssl_options = pika.SSLOptions(context)
        return pika.BlockingConnection(params)
    
    # Fallback to local RabbitMQ without authentication
    return pika.BlockingConnection(
        pika.ConnectionParameters('localhost')
    )