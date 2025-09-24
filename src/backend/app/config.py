import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL")
    REDIS_URL = os.getenv("REDIS_URL")
    ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL")
    KIBANA_URL = os.getenv("KIBANA_URL")

settings = Settings()