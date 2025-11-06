def test_root_endpoint(client):
    """Тест корневого эндпоинта"""
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Async Cinema API!"}


def test_health_check(client):
    """Тест health check эндпоинта"""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_openapi_docs_available(client):
    """Тест доступности документации OpenAPI"""
    response = client.get("/api/openapi")

    assert response.status_code == 200
    assert "swagger" in response.text.lower() or "openapi" in response.text.lower()
