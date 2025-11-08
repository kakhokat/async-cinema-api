FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app/src

WORKDIR /app

# system deps for building wheels (orjson, elastic)
RUN apt-get update && apt-get install -y \
    build-essential curl && \
    rm -rf /var/lib/apt/lists/*

# copy and install
COPY requirements.txt ./requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# copy source
COPY src ./src
COPY .env.example ./.env.example

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "src"]
