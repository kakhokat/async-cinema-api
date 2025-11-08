import typing as t
import copy
import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.models.film import Film, FilmListItem
from src.services.film import get_film_service as get_film_service_src
from services.film import get_film_service as get_film_service_pkg


@pytest.fixture(scope="session")
def sample_movies() -> t.List[dict]:
    return [
        {
            "id": "b31592e5-673d-46dc-a561-9446438aea0f",
            "title": "Lunar: The Silver Star",
            "description": "From the village of Burg...",
            "imdb_rating": 9.2,
            "genre": ["6f822a92-7b51-4753-8d00-ecfedf98a937", "00f74939-18b1-42e4-b541-b52f667d50d9"],
        },
        {
            "id": "27fc3dc6-2656-43cb-8e56-d0dfb75ea0b2",
            "title": "Wishes on a Falling Star",
            "description": "Romance with a cosmic twist.",
            "imdb_rating": 8.5,
            "genre": ["7ac3cb3b-972d-4004-9e42-ff147ede7463"],
        },
        {
            "id": "00000000-0000-0000-0000-000000000001",
            "title": "Silent Moon",
            "description": "Moonlight horror",
            "imdb_rating": 7.0,
            "genre": ["6f822a92-7b51-4753-8d00-ecfedf98a937"],
        },
        {
            "id": "223e4317-e89b-22d3-f3b6-426614174000",
            "title": "Billion Star Hotel",
            "description": "Some description",
            "imdb_rating": 6.1,
            "genre": ["00f74939-18b1-42e4-b541-b52f667d50d9"],
        },
        {
            "id": "00000000-0000-0000-0000-000000000002",
            "title": "Zero Rating Mystery",
            "description": "Something strange",
            "imdb_rating": None,
            "genre": ["00f74939-18b1-42e4-b541-b52f667d50d9"],
        },
    ]


# ---------- IN-MEMORY СЕРВИС ----------
class InMemoryFilmService:
    """Полная замена FilmService для юнит-тестов: без Redis/ES."""

    def __init__(self, films: t.List[dict]):
        self._films: t.List[Film] = [Film(**copy.deepcopy(x)) for x in films]

    async def get_by_id(self, film_id: str) -> t.Optional[Film]:
        for f in self._films:
            if f.id == film_id:
                return f
        return None

    async def list_films(
        self,
        sort: t.Optional[str],
        page_number: int,
        page_size: int,
        genre: t.Optional[str] = None,
    ) -> t.List[FilmListItem]:
        items = self._films

        # фильтр по жанру
        if genre:
            items = [f for f in items if f.genre and genre in f.genre]

        # сортировка (по умолчанию -imdb_rating)
        sort = sort or "-imdb_rating"
        order = "desc" if sort.startswith("-") else "asc"
        field = sort.lstrip("+-") or "imdb_rating"

        def key_fn_desc(f: Film):
            val = getattr(f, field, None)
            # None в конец + по убыванию значения
            return (val is None, -(val) if isinstance(val, (int, float)) else 0)

        def key_fn_asc(f: Film):
            val = getattr(f, field, None)
            # None в конец + по возрастанию значения
            return (val is None, val if val is not None else 0)

        key_fn = key_fn_desc if order == "desc" else key_fn_asc
        items = sorted(items, key=key_fn)

        # пагинация
        start = (page_number - 1) * page_size
        end = start + page_size
        items = items[start:end]

        # возвращаем то, что ожидает API: FilmListItem
        return [FilmListItem(uuid=f.id, title=f.title, imdb_rating=f.imdb_rating) for f in items]

    async def search_films(
        self,
        query_str: str,
        page_number: int,
        page_size: int,
    ) -> t.List[FilmListItem]:
        q = (query_str or "").lower()

        def match(f: Film):
            return q in (f.title or "").lower() or q in (f.description or "").lower()

        items = [f for f in self._films if match(f)]

        # приближённая релевантность: по рейтингу по убыванию, None — в конец
        items = sorted(items, key=lambda f: (f.imdb_rating is None, -(f.imdb_rating or 0)))

        start = (page_number - 1) * page_size
        end = start + page_size
        items = items[start:end]

        return [FilmListItem(uuid=f.id, title=f.title, imdb_rating=f.imdb_rating) for f in items]


# ---------- ПОДМЕНА ЗАВИСИМОСТЕЙ ----------
@pytest.fixture(autouse=True)
def override_service(sample_movies):
    def factory():
        return InMemoryFilmService(sample_movies)

    # подменяем обе ссылки на зависимость (и с префиксом src, и без него)
    app.dependency_overrides[get_film_service_src] = factory
    app.dependency_overrides[get_film_service_pkg] = factory
    yield
    app.dependency_overrides.clear()


# ---------- КЛИЕНТ ----------
@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c
