import multiprocessing
import os

bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"

# управляем через ENV, с безопасными дефолтами для контейнера
workers = int(os.getenv("GUNICORN_WORKERS", "2"))
threads = int(os.getenv("GUNICORN_THREADS", "1"))

worker_class = "uvicorn.workers.UvicornWorker"
accesslog = "-"
errorlog = "-"
graceful_timeout = 30
timeout = 120
keepalive = 5

# немного гигиены на долгоживущих процессах
max_requests = int(os.getenv("GUNICORN_MAX_REQUESTS", "1000"))
max_requests_jitter = int(os.getenv("GUNICORN_MAX_REQUESTS_JITTER", "100"))
