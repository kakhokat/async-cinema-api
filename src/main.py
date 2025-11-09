# src/main.py
from contextlib import asynccontextmanager
from logging.config import dictConfig

import redis.exceptions as redis_exc
from elasticsearch import AsyncElasticsearch, TransportError
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, ORJSONResponse
from redis.asyncio import Redis
from starlette.middleware.cors import CORSMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from api.v1 import films
from core.logger import LOGGING
from core.settings import settings
from db import elastic, redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    redis.redis = Redis.from_url(
        settings.REDIS_URL, encoding="utf-8", decode_responses=False
    )
    elastic.es = AsyncElasticsearch(hosts=[settings.ELASTIC_URL])
    try:
        yield
    finally:
        # shutdown
        if redis.redis:
            await redis.redis.aclose()
        if elastic.es:
            await elastic.es.close()


# logging config
dictConfig(LOGGING)

app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url=settings.DOCS_URL,
    openapi_url=settings.OPENAPI_URL,
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

# доверяем X-Forwarded-* от nginx
trusted = (
    ["*"]
    if settings.PROXY_TRUSTED_HOSTS.strip() == "*"
    else [h.strip() for h in settings.PROXY_TRUSTED_HOSTS.split(",") if h.strip()]
)
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts=trusted)

# CORS (управляется через env CORS_ALLOW_ORIGINS)
origins = (
    ["*"]
    if settings.CORS_ALLOW_ORIGINS.strip() == "*"
    else [o.strip() for o in settings.CORS_ALLOW_ORIGINS.split(",") if o.strip()]
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(TransportError)
async def es_transport_error_handler(_: Request, exc: TransportError):
    return JSONResponse(
        status_code=503,
        content={"detail": "Elasticsearch is unavailable", "reason": str(exc)},
    )


@app.exception_handler(redis_exc.RedisError)
async def redis_error_handler(_: Request, exc: redis_exc.RedisError):
    return JSONResponse(
        status_code=503,
        content={"detail": "Redis is unavailable", "reason": str(exc)},
    )


# routers
app.include_router(films.router, prefix="/api/v1/films", tags=["films"])
