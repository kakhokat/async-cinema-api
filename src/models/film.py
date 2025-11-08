from typing import List, Optional

from pydantic import BaseModel, Field


# модель бизнес-логики (как хранится в ES)
class Film(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    imdb_rating: Optional[float] = Field(default=None)
    genre: Optional[List[str]] = None


# модели для API-ответов
class FilmListItem(BaseModel):
    uuid: str
    title: str
    imdb_rating: Optional[float] = None


class FilmDetail(BaseModel):
    uuid: str
    title: str
    imdb_rating: Optional[float] = None
    description: Optional[str] = None
    genre: Optional[list] = None
