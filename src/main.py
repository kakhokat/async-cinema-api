from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

from api.v1 import films
from core import config
from db import elastic, redis

app = FastAPI(
    title=config.PROJECT_NAME,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)

@app.on_event('startup')
async def startup():
    # use URLs from env
    redis.redis = Redis.from_url(config.REDIS_URL, encoding="utf-8", decode_responses=False)
    elastic.es = AsyncElasticsearch(hosts=[config.ELASTIC_URL])

@app.on_event('shutdown')
async def shutdown():
    if redis.redis:
        await redis.redis.aclose()
    if elastic.es:
        await elastic.es.close()

# routers
app.include_router(films.router, prefix='/api/v1/films', tags=['films'])
