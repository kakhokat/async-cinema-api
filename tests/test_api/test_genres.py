import pytest


class TestGenresAPI:
    def test_genres_list_endpoint(self, client):
        """Тест эндпоинта списка жанров"""
        response = client.get("/api/v1/genres/")

        assert response.status_code == 200
        assert response.json() == []

    def test_genre_details_not_found(self, client):
        """Тест получения несуществующего жанра"""
        response = client.get("/api/v1/genres/nonexistent-id")

        assert response.status_code == 404
        assert response.json()["detail"] == "Genre not found"
