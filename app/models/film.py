from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

# Импортируем модели из других файлов вместо дублирования
from app.models.genre import Genre
from app.models.person import Person


class FilmBase(BaseModel):
    uuid: UUID
    title: str


class FilmShort(FilmBase):
    imdb_rating: Optional[float] = None


class FilmDetailed(FilmShort):
    description: Optional[str] = None
    genres: Optional[List[Genre]] = None
    actors: Optional[List[Person]] = None
    writers: Optional[List[Person]] = None
    directors: Optional[List[Person]] = None
