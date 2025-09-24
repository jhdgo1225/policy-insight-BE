from celery import Celery
from dotenv import load_dotenv
import os

load_dotenv()

app = Celery(
    'worker',
    broker=os.getenv('REDIS_URL'),
    include=['tasks.data_collection', 'tasks.analysis']
)