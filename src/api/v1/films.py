# src/api/v1/films.py

from http import HTTPStatus
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from core.pagination import PaginationParams
from models.film import FilmDetail, FilmListItem
from services.film import FilmService, get_film_service

router = APIRouter()


# ================================
# 📋 Список фильмов
# ================================
@router.get(
    "/",
    response_model=List[FilmListItem],
    summary="List films",
    description=(
        "Список фильмов с сортировкой, пагинацией и фильтром по жанру.\n\n"
        "- Сортировка: передайте поле с префиксом `-` (например, `-imdb_rating`).\n"
        "- Пагинация: `page_number` и `page_size`.\n"
        "- Фильтр по жанру: `genre` — UUID жанра."
    ),
)
async def films_list(
    sort: Optional[str] = Query(default="-imdb_rating", description="..."),
    genre: Optional[str] = Query(
        default=None, description="UUID жанра для фильтрации."
    ),
    pagination: PaginationParams = Depends(),
    film_service: FilmService = Depends(get_film_service),
) -> List[FilmListItem]:
    return await film_service.list_films(
        sort=sort,
        page_number=pagination.page_number,
        page_size=pagination.page_size,
        genre=genre,
    )


# ================================
# 🔍 Поиск фильмов
# ================================
@router.get(
    "/search",
    response_model=List[FilmListItem],
    summary="Search films",
    description=(
        "Полнотекстовый поиск по названию и описанию фильмов.\n\n"
        "- Поле запроса: `query` (минимум 1 символ).\n"
        "- Сортировка результата по рейтингу `imdb_rating` по убыванию; "
        "значения `None` — в конце.\n"
        "- Пагинация: `page_number` и `page_size`."
    ),
)
async def films_search(
    query: str = Query(min_length=1, description="Строка поиска (минимум 1 символ)."),
    pagination: PaginationParams = Depends(),
    film_service: FilmService = Depends(get_film_service),
) -> List[FilmListItem]:
    return await film_service.search_films(
        query_str=query,
        page_number=pagination.page_number,
        page_size=pagination.page_size,
    )


# ================================
# 🎬 Детальная информация о фильме
# ================================
@router.get(
    "/{film_id}",
    response_model=FilmDetail,
    summary="Film details",
    description="Детальная информация о фильме по его UUID.",
    responses={
        404: {
            "description": "Film not found",
            "content": {"application/json": {"example": {"detail": "film not found"}}},
        }
    },
)
async def film_details(
    film_id: UUID, film_service: FilmService = Depends(get_film_service)
) -> FilmDetail:
    """
    Возвращает полную информацию о фильме по его UUID.
    Если фильм не найден — 404.
    """
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
