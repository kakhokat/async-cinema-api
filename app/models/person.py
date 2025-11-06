from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel


class FilmRole(BaseModel):
    uuid: UUID
    roles: List[str]


class PersonBase(BaseModel):
    uuid: UUID
    full_name: str


class Person(PersonBase):
    films: Optional[List[FilmRole]] = None


class PersonDetailed(PersonBase):
    films: Optional[List[FilmRole]] = None
