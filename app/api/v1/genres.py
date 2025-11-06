from typing import List

from fastapi import APIRouter, Depends, HTTPException

from app.models.genre import Genre
from app.services.genre import GenreService, get_genre_service

router = APIRouter()


@router.get("/", response_model=List[Genre])
async def genres_list(
    genre_service: GenreService = Depends(get_genre_service),
) -> List[Genre]:
    genres = await genre_service.get_all()
    return genres


@router.get("/{genre_id}", response_model=Genre)
async def genre_details(
    genre_id: str,
    genre_service: GenreService = Depends(get_genre_service),
) -> Genre:
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=404, detail="Genre not found")
    return genre
