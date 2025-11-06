import asyncio

from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from app.core.config import settings


class ElasticsearchManager:
    def __init__(self):
        self.client: AsyncElasticsearch | None = None
        self.is_connected = False

    async def connect(self):
        """Подключается к Elasticsearch."""
        try:
            print("Connecting to Elasticsearch at", end="")
            print(f"{settings.ELASTIC_HOST}:{settings.ELASTIC_PORT}")

            # Упрощенное подключение для версии 8.x
            self.client = AsyncElasticsearch(
                hosts=[f"http://{settings.ELASTIC_HOST}:{settings.ELASTIC_PORT}"],
                verify_certs=False,
                ssl_show_warn=False,
                request_timeout=60,
                retry_on_timeout=True,
                max_retries=5,
            )

            # Проверяем подключение с повторными попытками
            print("🔄 Testing Elasticsearch connection...")
            max_attempts = 10
            for attempt in range(max_attempts):
                try:
                    success = await self.client.ping()
                    if success:
                        print("✅ Successfully connected to Elasticsearch")
                        self.is_connected = True

                        # Проверим информацию о кластере
                        info = await self.client.info()
                        print("📊 Elasticsearch cluster: ", end="")
                        print("{info['cluster_name']},", end="")
                        print(f"version: {info['version']['number']}")

                        return
                    else:
                        print("⚠️  Elasticsearch ping returned False,", end="")
                        print(f"attempt {attempt + 1}/{max_attempts}")

                except Exception as e:
                    print(f"⚠️  Connection attempt {attempt + 1}", end="")
                    print(f"/{max_attempts} failed: {str(e)}")

                if attempt < max_attempts - 1:
                    wait_time = 2 * (attempt + 1)  # Увеличиваем время ожидания
                    print(f"⏳ Waiting {wait_time} seconds before next attempt...")
                    await asyncio.sleep(wait_time)

            print("❌ Failed to connect to Elasticsearch after all attempts")
            self.client = None
            self.is_connected = False

        except Exception as e:
            print(f"❌ Elasticsearch connection error: {str(e)}")
            self.client = None
            self.is_connected = False

    async def close(self):
        """Закрывает подключение к Elasticsearch."""
        if self.client:
            await self.client.close()
            self.client = None
            self.is_connected = False

    async def get_client(self) -> AsyncElasticsearch:
        """Возвращает клиент Elasticsearch."""
        if self.client is None or not self.is_connected:
            # Попробуем переподключиться
            await self.connect()
            if self.client is None:
                raise Exception(
                    "Elasticsearch is not connected. Check the connection logs."
                )
        return self.client


# Создаем экземпляр менеджера
elastic_manager = ElasticsearchManager()


# Dependency для FastAPI
async def get_elastic() -> AsyncElasticsearch:
    return await elastic_manager.get_client()
