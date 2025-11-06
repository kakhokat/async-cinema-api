from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query

from app.models.film import FilmShort
from app.models.person import Person, PersonDetailed
from app.services.person import PersonService, get_person_service

router = APIRouter()


@router.get("/search/", response_model=List[Person])
async def persons_search(
    query: str = Query(..., min_length=1),
    page_number: int = Query(1, ge=1, alias="page_number"),
    page_size: int = Query(50, ge=1, le=100, alias="page_size"),
    person_service: PersonService = Depends(get_person_service),
) -> List[Person]:
    persons = await person_service.search(query, page_number, page_size)
    return persons


@router.get("/{person_id}", response_model=PersonDetailed)
async def person_details(
    person_id: str,
    person_service: PersonService = Depends(get_person_service),
) -> PersonDetailed:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return person


@router.get("/{person_id}/film", response_model=List[FilmShort])
async def person_films(
    person_id: str,
    page_number: int = Query(1, ge=1, alias="page_number"),
    page_size: int = Query(50, ge=1, le=100, alias="page_size"),
    person_service: PersonService = Depends(get_person_service),
) -> List[FilmShort]:
    films = await person_service.get_person_films(person_id, page_number, page_size)
    return films
