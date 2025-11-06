from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1 import films, genres, persons
from app.core.config import settings
from app.db.elastic import elastic_manager
from app.db.redis import redis_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting application...")

    # Подключаемся к базам данных
    await elastic_manager.connect()
    await redis_manager.connect()

    yield

    # Shutdown
    print("🛑 Shutting down...")
    await elastic_manager.close()
    await redis_manager.close()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# Подключаем роутеры
app.include_router(films.router, prefix="/api/v1/films", tags=["films"])
app.include_router(genres.router, prefix="/api/v1/genres", tags=["genres"])
app.include_router(persons.router, prefix="/api/v1/persons", tags=["persons"])


@app.get("/")
async def root():
    return {"message": "Welcome to Async Cinema API!"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
