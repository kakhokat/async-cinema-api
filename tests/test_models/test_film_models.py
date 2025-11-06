from uuid import UUID

import pytest

from app.models.film import FilmBase, FilmDetailed, FilmShort


class TestFilmModels:
    def test_film_base(self):
        """Тест базовой модели фильма"""
        film_data = {
            "uuid": "123e4567-e89b-12d3-a456-426614174000",
            "title": "Test Film",
        }
        film = FilmBase(**film_data)

        assert film.uuid == UUID(film_data["uuid"])
        assert film.title == film_data["title"]

    def test_film_short(self):
        """Тест краткой модели фильма"""
        film_data = {
            "uuid": "123e4567-e89b-12d3-a456-426614174000",
            "title": "Test Film",
            "imdb_rating": 8.5,
        }
        film = FilmShort(**film_data)

        assert film.uuid == UUID(film_data["uuid"])
        assert film.title == film_data["title"]
        assert film.imdb_rating == film_data["imdb_rating"]

    def test_film_detailed(self):
        """Тест детальной модели фильма"""
        film_data = {
            "uuid": "123e4567-e89b-12d3-a456-426614174000",
            "title": "Test Film",
            "imdb_rating": 8.5,
            "description": "Test description",
            "genres": [
                {"uuid": "123e4567-e89b-12d3-a456-426614174001", "name": "Action"}
            ],
            "actors": [
                {
                    "uuid": "123e4567-e89b-12d3-a456-426614174002",
                    "full_name": "Actor One",
                }
            ],
            "writers": [
                {
                    "uuid": "123e4567-e89b-12d3-a456-426614174003",
                    "full_name": "Writer One",
                }
            ],
            "directors": [
                {
                    "uuid": "123e4567-e89b-12d3-a456-426614174004",
                    "full_name": "Director One",
                }
            ],
        }
        film = FilmDetailed(**film_data)

        assert film.uuid == UUID(film_data["uuid"])
        assert film.title == film_data["title"]
        assert film.imdb_rating == film_data["imdb_rating"]
        assert film.description == film_data["description"]
        assert len(film.genres) == 1
        assert film.genres[0].name == "Action"
        assert len(film.actors) == 1
        assert film.actors[0].full_name == "Actor One"

    def test_film_optional_fields(self):
        """Тест опциональных полей в моделях"""
        film_data = {
            "uuid": "123e4567-e89b-12d3-a456-426614174000",
            "title": "Test Film",
        }
        film_short = FilmShort(**film_data)

        assert film_short.imdb_rating is None

        film_detailed = FilmDetailed(**film_data)
        assert film_detailed.imdb_rating is None
        assert film_detailed.description is None
        assert film_detailed.genres is None
        assert film_detailed.actors is None
        assert film_detailed.writers is None
        assert film_detailed.directors is None
