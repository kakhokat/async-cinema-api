import pytest


class TestPersonsAPI:
    def test_persons_search_endpoint(self, client):
        """Тест эндпоинта поиска персон"""
        response = client.get("/api/v1/persons/search/?query=john")

        assert response.status_code == 200
        assert response.json() == []

    def test_person_details_not_found(self, client):
        """Тест получения несуществующей персоны"""
        response = client.get("/api/v1/persons/nonexistent-id")

        assert response.status_code == 404
        assert response.json()["detail"] == "Person not found"
