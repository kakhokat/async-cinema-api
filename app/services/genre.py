from typing import List, Optional

from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from app.db.elastic import get_elastic
from app.models.genre import Genre


class GenreService:
    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    async def get_by_id(self, genre_id: str) -> Optional[Genre]:
        return None

    async def get_all(self) -> List[Genre]:
        return []


async def get_genre_service(
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(elastic)
