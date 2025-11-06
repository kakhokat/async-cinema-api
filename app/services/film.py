from typing import List, Optional

from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from app.db.elastic import get_elastic
from app.models.film import FilmDetailed, FilmShort


class FilmService:
    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    async def get_by_id(self, film_id: str) -> Optional[FilmDetailed]:
        # Заглушка - позже заменим на реальную логику
        return None

    async def get_all(
        self,
        sort: str,
        genre: Optional[str] = None,
        page_number: int = 1,
        page_size: int = 50,
    ) -> List[FilmShort]:
        # Заглушка
        return []

    async def search(
        self, query: str, page_number: int = 1, page_size: int = 50
    ) -> List[FilmShort]:
        # Заглушка
        return []


# Factory функция для создания сервиса
async def get_film_service(
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(elastic)
