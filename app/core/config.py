import os
from typing import Optional

from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()


class Settings:
    # Project
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Async Cinema API")
    VERSION: str = os.getenv("VERSION", "1.0.0")
    API_V1_STR: str = os.getenv("API_V1_STR", "/api/v1")

    # Elasticsearch
    ELASTIC_HOST: str = os.getenv("ELASTIC_HOST", "localhost")
    ELASTIC_PORT: int = int(os.getenv("ELASTIC_PORT", "9200"))

    # Redis
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))


settings = Settings()
