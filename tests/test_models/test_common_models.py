from uuid import UUID

import pytest

from app.models.genre import Genre
from app.models.person import FilmRole, Person, PersonDetailed


class TestCommonModels:
    def test_genre_model(self):
        """Тест модели жанра"""
        genre_data = {"uuid": "123e4567-e89b-12d3-a456-426614174001", "name": "Action"}
        genre = Genre(**genre_data)

        assert genre.uuid == UUID(genre_data["uuid"])
        assert genre.name == genre_data["name"]

    def test_person_model(self):
        """Тест модели персоны"""
        person_data = {
            "uuid": "123e4567-e89b-12d3-a456-426614174002",
            "full_name": "John Doe",
        }
        person = Person(**person_data)

        assert person.uuid == UUID(person_data["uuid"])
        assert person.full_name == person_data["full_name"]
        assert person.films is None

    def test_person_detailed_model(self):
        """Тест детальной модели персоны"""
        person_data = {
            "uuid": "123e4567-e89b-12d3-a456-426614174002",
            "full_name": "John Doe",
            "films": [
                {
                    "uuid": "123e4567-e89b-12d3-a456-426614174005",
                    "roles": ["actor", "director"],
                }
            ],
        }
        person = PersonDetailed(**person_data)

        assert person.uuid == UUID(person_data["uuid"])
        assert person.full_name == person_data["full_name"]
        assert len(person.films) == 1
        assert person.films[0].uuid == UUID("123e4567-e89b-12d3-a456-426614174005")
        assert person.films[0].roles == ["actor", "director"]

    def test_film_role_model(self):
        """Тест модели роли в фильме"""
        role_data = {"uuid": "123e4567-e89b-12d3-a456-426614174005", "roles": ["actor"]}
        film_role = FilmRole(**role_data)

        assert film_role.uuid == UUID(role_data["uuid"])
        assert film_role.roles == ["actor"]
