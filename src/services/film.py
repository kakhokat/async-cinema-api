from functools import lru_cache
from typing import Any, Dict, List, Optional, Tuple

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film, FilmDetail, FilmListItem

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут
INDEX = "movies"


def _cache_key(prefix: str, params: Dict[str, Any]) -> str:
    # стабильный ключ кеша по набору параметров
    items = sorted((k, str(v)) for k, v in params.items() if v is not None)
    return prefix + ":" + "|".join(f"{k}={v}" for k, v in items)


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    # ---------- public ----------
    async def get_by_id(self, film_id: str) -> Optional[Film]:
        film = await self._film_from_cache(film_id)
        if film:
            return film
        film = await self._get_film_from_elastic(film_id)
        if film:
            await self._put_film_to_cache(film)
        return film

    async def list_films(
        self,
        sort: Optional[str],
        page_number: int,
        page_size: int,
        genre: Optional[str] = None,
    ) -> List[FilmListItem]:
        params = {
            "sort": sort,
            "page_number": page_number,
            "page_size": page_size,
            "genre": genre,
        }
        key = _cache_key("films:list", params)
        cached = await self.redis.get(key)
        if cached:
            return [
                FilmListItem.parse_raw(row) for row in eval(cached.decode("utf-8"))
            ]  # simple cached rows

        query, es_sort = self._build_list_query(sort=sort, genre=genre)
        from_ = (page_number - 1) * page_size
        resp = await self.elastic.search(
            index=INDEX,
            query=query,
            sort=es_sort,
            from_=from_,
            size=page_size,
            _source=["id", "title", "imdb_rating"],
        )
        rows: List[FilmListItem] = []
        for hit in resp["hits"]["hits"]:
            src = hit["_source"]
            rows.append(
                FilmListItem(
                    uuid=src.get("id") or hit["_id"],
                    title=src.get("title", ""),
                    imdb_rating=src.get("imdb_rating"),
                )
            )
        # cache as list of json strings
        await self.redis.set(
            key,
            str([r.json() for r in rows]).encode("utf-8"),
            FILM_CACHE_EXPIRE_IN_SECONDS,
        )
        return rows

    async def search_films(
        self,
        query_str: str,
        page_number: int,
        page_size: int,
    ) -> List[FilmListItem]:
        params = {"q": query_str, "page_number": page_number, "page_size": page_size}
        key = _cache_key("films:search", params)
        cached = await self.redis.get(key)
        if cached:
            return [FilmListItem.parse_raw(row) for row in eval(cached.decode("utf-8"))]

        from_ = (page_number - 1) * page_size
        query = {
            "multi_match": {
                "query": query_str,
                "fields": ["title^3", "description"],
                "fuzziness": "AUTO",
            }
        }
        resp = await self.elastic.search(
            index=INDEX,
            query=query,
            sort=[{"imdb_rating": {"order": "desc", "missing": "_last"}}],
            from_=from_,
            size=page_size,
            _source=["id", "title", "imdb_rating"],
        )
        rows: List[FilmListItem] = []
        for hit in resp["hits"]["hits"]:
            src = hit["_source"]
            rows.append(
                FilmListItem(
                    uuid=src.get("id") or hit["_id"],
                    title=src.get("title", ""),
                    imdb_rating=src.get("imdb_rating"),
                )
            )
        await self.redis.set(
            key,
            str([r.json() for r in rows]).encode("utf-8"),
            FILM_CACHE_EXPIRE_IN_SECONDS,
        )
        return rows

    # ---------- internals ----------
    async def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
        try:
            doc = await self.elastic.get(index=INDEX, id=film_id)
        except NotFoundError:
            return None
        src = doc["_source"]
        # если в _source нет id — используем _id
        src.setdefault("id", doc["_id"])
        return Film(**src)

    async def _film_from_cache(self, film_id: str) -> Optional[Film]:
        data = await self.redis.get(film_id)
        if not data:
            return None
        return Film.parse_raw(data)

    async def _put_film_to_cache(self, film: Film):
        await self.redis.set(film.id, film.json(), FILM_CACHE_EXPIRE_IN_SECONDS)

    def _build_list_query(
        self, sort: Optional[str], genre: Optional[str]
    ) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        es_sort: List[Dict[str, Any]] = []
        if sort:
            order = "desc" if sort.startswith("-") else "asc"
            field = sort.lstrip("+-")
            # соответствие ТЗ: sort=-imdb_rating
            es_sort.append({field: {"order": order, "missing": "_last"}})

        must: List[Dict[str, Any]] = []
        if genre:
            # ожидаем, что в документе фильма есть поле "genre" — список uuid жанров
            must.append({"terms": {"genre": [genre]}})

        query: Dict[str, Any] = {"bool": {"must": must}} if must else {"match_all": {}}
        return query, es_sort or [
            {"imdb_rating": {"order": "desc", "missing": "_last"}}
        ]


@lru_cache()
def get_film_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
