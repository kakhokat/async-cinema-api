from http import HTTPStatus
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from models.film import FilmDetail, FilmListItem
from services.film import FilmService, get_film_service

router = APIRouter()


@router.get("/", response_model=List[FilmListItem])
async def films_list(
    sort: Optional[str] = Query(
        default="-imdb_rating", description="Example: -imdb_rating"
    ),
    page_size: int = Query(default=50, ge=1, le=1000),
    page_number: int = Query(default=1, ge=1),
    genre: Optional[str] = Query(default=None, description="Genre UUID"),
    film_service: FilmService = Depends(get_film_service),
) -> List[FilmListItem]:
    return await film_service.list_films(
        sort=sort, page_number=page_number, page_size=page_size, genre=genre
    )


# Поиск — поддержим оба пути
@router.get("/search", response_model=List[FilmListItem])
@router.get("/search/", response_model=List[FilmListItem])
async def films_search(
    query: str = Query(min_length=1),
    page_size: int = Query(default=50, ge=1, le=1000),
    page_number: int = Query(default=1, ge=1),
    film_service: FilmService = Depends(get_film_service),
) -> List[FilmListItem]:
    return await film_service.search_films(
        query_str=query, page_number=page_number, page_size=page_size
    )


# Детальная — СТРОГО после search, и film_id типизируем как UUID
@router.get("/{film_id}", response_model=FilmDetail)
async def film_details(
    film_id: UUID, film_service: FilmService = Depends(get_film_service)
) -> FilmDetail:
    film = await film_service.get_by_id(str(film_id))
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="film not found")
    return FilmDetail(
        uuid=film.id,
        title=film.title,
        imdb_rating=film.imdb_rating,
        description=film.description,
        genre=film.genre,
    )
