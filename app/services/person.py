from typing import List, Optional

from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from app.db.elastic import get_elastic
from app.models.film import FilmShort
from app.models.person import Person, PersonDetailed


class PersonService:
    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    async def get_by_id(self, person_id: str) -> Optional[PersonDetailed]:
        return None

    async def search(
        self, query: str, page_number: int = 1, page_size: int = 50
    ) -> List[Person]:
        return []

    async def get_person_films(
        self, person_id: str, page_number: int = 1, page_size: int = 50
    ) -> List[FilmShort]:
        return []


async def get_person_service(
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(elastic)
