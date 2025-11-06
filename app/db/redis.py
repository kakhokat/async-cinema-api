import redis.asyncio as redis
from fastapi import Depends

from app.core.config import settings


class RedisManager:
    def __init__(self):
        self.client: redis.Redis | None = None

    async def connect(self):
        """Подключается к Redis."""
        try:
            self.client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                decode_responses=True,
            )
            await self.client.ping()
            print("✅ Connected to Redis")
        except Exception as e:
            print(f"❌ Could not connect to Redis: {e}")
            self.client = None

    async def close(self):
        """Закрывает подключение к Redis."""
        if self.client:
            await self.client.close()
            self.client = None

    async def get_client(self) -> redis.Redis:
        """Возвращает клиент Redis."""
        if self.client is None:
            raise Exception("Redis not connected")
        return self.client


# Создаем экземпляр менеджера
redis_manager = RedisManager()


# Dependency для FastAPI
async def get_redis() -> redis.Redis:
    return await redis_manager.get_client()
