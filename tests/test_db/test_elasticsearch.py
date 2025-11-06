import asyncio

import aiohttp
from elasticsearch import AsyncElasticsearch


async def test_elasticsearch_connection():
    """Тестирует подключение к Elasticsearch"""
    print("🧪 Testing Elasticsearch connection...")

    try:
        # Тестируем прямое HTTP подключение
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:9200/") as response:
                print(f"📡 HTTP Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Elasticsearch info: {data}")
                else:
                    print(f"❌ HTTP Error: {response.status}")

    except Exception as e:
        print(f"❌ HTTP Connection failed: {e}")

    try:
        # Тестируем через клиент Elasticsearch
        client = AsyncElasticsearch(
            hosts=["http://localhost:9200"], verify_certs=False, request_timeout=10
        )

        print("🔄 Testing with Elasticsearch client...")
        is_connected = await client.ping()
        print(f"✅ Elasticsearch client ping: {is_connected}")

        if is_connected:
            info = await client.info()
            print(
                f"📊 Cluster info: {
                    info['cluster_name']
                    } (version: {
                        info['version']['number']
                        })"
            )

        await client.close()

    except Exception as e:
        print(f"❌ Elasticsearch client failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_elasticsearch_connection())
