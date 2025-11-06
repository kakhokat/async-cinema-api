from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.db.elastic import elastic_manager
from app.db.redis import redis_manager
from app.main import app


@pytest.fixture(autouse=True)
async def mock_database_connections():
    """Мокаем подключения к базам данных для всех тестов"""
    # Мокаем Elasticsearch
    mock_elastic = AsyncMock()
    mock_elastic.ping.return_value = True
    elastic_manager.client = mock_elastic

    # Мокаем Redis
    mock_redis = AsyncMock()
    mock_redis.ping.return_value = True
    redis_manager.client = mock_redis

    yield

    # Очищаем моки после тестов
    elastic_manager.client = None
    redis_manager.client = None


@pytest.fixture
def client():
    """Фикстура для тестового клиента FastAPI"""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_film_data():
    """Пример данных фильма для тестов"""
    return {
        "uuid": "123e4567-e89b-12d3-a456-426614174000",
        "title": "Test Film",
        "imdb_rating": 8.5,
        "description": "Test description",
    }


@pytest.fixture
def sample_genre_data():
    """Пример данных жанра для тестов"""
    return {"uuid": "123e4567-e89b-12d3-a456-426614174001", "name": "Action"}


@pytest.fixture
def sample_person_data():
    """Пример данных персоны для тестов"""
    return {"uuid": "123e4567-e89b-12d3-a456-426614174002", "full_name": "John Doe"}
