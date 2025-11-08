# src/main.py
import redis.exceptions as redis_exc
from elasticsearch import TransportError  # базовый для сетевых/HTTP ошибок клиента ES
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, ORJSONResponse
from redis.asyncio import Redis

from api.v1 import films
from core import config
from db import elastic, redis

app = FastAPI(
    title=config.PROJECT_NAME,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)


@app.exception_handler(TransportError)
async def es_transport_error_handler(_: Request, exc: TransportError):
    # Любая сетевая/HTTP ошибка Elaticsearch клиента -> 503
    return JSONResponse(
        status_code=503,
        content={"detail": "Elasticsearch is unavailable", "reason": str(exc)},
    )


@app.exception_handler(redis_exc.RedisError)
async def redis_error_handler(_: Request, exc: redis_exc.RedisError):
    # Любая ошибка Redis -> 503
    return JSONResponse(
        status_code=503,
        content={"detail": "Redis is unavailable", "reason": str(exc)},
    )


@app.on_event("startup")
async def startup():
    # use URLs from env
    redis.redis = Redis.from_url(
        config.REDIS_URL, encoding="utf-8", decode_responses=False
    )
    elastic.es = AsyncElasticsearch(hosts=[config.ELASTIC_URL])


@app.on_event("shutdown")
async def shutdown():
    if redis.redis:
        await redis.redis.aclose()
    if elastic.es:
        await elastic.es.close()


# routers
app.include_router(films.router, prefix="/api/v1/films", tags=["films"])
