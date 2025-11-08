import os
from logging import config as logging_config
from urllib.parse import urlparse

from core.logger import LOGGING

# apply logging config
logging_config.dictConfig(LOGGING)

PROJECT_NAME = os.getenv("PROJECT_NAME", "movies")

# Redis: prefer REDIS_URL, fallback to host/port
REDIS_URL = os.getenv("REDIS_URL")
if not REDIS_URL:
    redis_host = os.getenv("REDIS_HOST", "127.0.0.1")
    redis_port = int(os.getenv("REDIS_PORT", 6379))
    REDIS_URL = f"redis://{redis_host}:{redis_port}/0"

# Elasticsearch: prefer ELASTIC_URL, fallback to host/port (ensure scheme)
ELASTIC_URL = os.getenv("ELASTIC_URL")
if not ELASTIC_URL:
    elastic_host = os.getenv("ELASTIC_HOST", "127.0.0.1")
    elastic_port = int(os.getenv("ELASTIC_PORT", 9200))
    ELASTIC_URL = f"http://{elastic_host}:{elastic_port}"

# Project base dir
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
