from dotenv import load_dotenv
import os
import pika

load_dotenv()

def get_connection():
    url = os.getenv("CLOUDAMQP_URL")
    params = pika.URLParameters(url)
    params.ssl_options = pika.SSLOptions()
    return pika.BlockingConnection(params)