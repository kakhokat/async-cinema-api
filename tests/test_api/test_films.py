from unittest.mock import AsyncMock, patch

import pytest


class TestFilmsAPI:
    def test_films_list_endpoint(self, client):
        """Тест эндпоинта списка фильмов"""
        response = client.get("/api/v1/films/")

        assert response.status_code == 200
        assert response.json() == []

    def test_films_list_with_query_params(self, client):
        """Тест списка фильмов с параметрами запроса"""
        response = client.get(
            "/api/v1/films/?sort=-imdb_rating&page_number=1&page_size=10"
        )

        assert response.status_code == 200
        assert response.json() == []

    def test_films_search_endpoint(self, client):
        """Тест эндпоинта поиска фильмов"""
        response = client.get("/api/v1/films/search/?query=star")

        assert response.status_code == 200
        assert response.json() == []

    def test_film_details_not_found(self, client):
        """Тест получения несуществующего фильма"""
        response = client.get("/api/v1/films/nonexistent-id")

        assert response.status_code == 404
        assert response.json()["detail"] == "Film not found"
