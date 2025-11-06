from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.models.film import FilmDetailed, FilmShort
from app.services.film import FilmService, get_film_service

router = APIRouter()


@router.get("/", response_model=List[FilmShort])
async def films_list(
    sort: str = Query(default="-imdb_rating"),
    genre: Optional[str] = Query(default=None),
    page_number: int = Query(1, ge=1, alias="page_number"),
    page_size: int = Query(50, ge=1, le=100, alias="page_size"),
    film_service: FilmService = Depends(get_film_service),  # Dependency injection
) -> List[FilmShort]:
    films = await film_service.get_all(sort, genre, page_number, page_size)
    return films


@router.get("/search/", response_model=List[FilmShort])
async def films_search(
    query: str = Query(..., min_length=1),
    page_number: int = Query(1, ge=1, alias="page_number"),
    page_size: int = Query(50, ge=1, le=100, alias="page_size"),
    film_service: FilmService = Depends(get_film_service),  # Dependency injection
) -> List[FilmShort]:
    films = await film_service.search(query, page_number, page_size)
    return films


@router.get("/{film_id}", response_model=FilmDetailed)
async def film_details(
    film_id: str,
    film_service: FilmService = Depends(get_film_service),  # Dependency injection
) -> FilmDetailed:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=404, detail="Film not found")
    return film
