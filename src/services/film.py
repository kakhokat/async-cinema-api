# src/services/film.py
import json
from functools import lru_cache
from typing import Any, Dict, List, Optional, Tuple

import redis.exceptions as redis_exc
from elasticsearch import AsyncElasticsearch, NotFoundError, TransportError
from fastapi import Depends, HTTPException
from redis.asyncio import Redis

from core.settings import settings
from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film, FilmListItem

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут
INDEX = settings.ES_INDEX


def _cache_key(prefix: str, params: Dict[str, Any]) -> str:
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

        # Если документ не найден в ES — возвращаем None (роутер отдаст 404).
        try:
            film = await self._get_film_from_elastic(film_id)
        except TransportError as exc:
            # отдадим 503 — обработчик в main.py тоже перехватит,
            # но здесь можно явно маппить на HTTPException
            raise HTTPException(
                status_code=503, detail="Elasticsearch is unavailable"
            ) from exc

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

        # читаем кеш безопасно
        rows = await self._read_list_from_cache(key)
        if rows is not None:
            return rows

        query, es_sort = self._build_list_query(sort=sort, genre=genre)
        from_ = (page_number - 1) * page_size

        try:
            resp = await self.elastic.search(
                index=INDEX,
                query=query,
                sort=es_sort,
                from_=from_,
                size=page_size,
                _source=["id", "title", "imdb_rating"],
            )
        except NotFoundError:
            # индекса нет — трактуем как "ничего не найдено"
            return []
        except TransportError as exc:
            # ES недоступен — 503
            raise HTTPException(
                status_code=503, detail="Elasticsearch is unavailable"
            ) from exc

        rows: List[FilmListItem] = []
        for hit in resp.get("hits", {}).get("hits", []):
            src = hit.get("_source", {})
            rows.append(
                FilmListItem(
                    uuid=src.get("id") or hit.get("_id", ""),
                    title=src.get("title", ""),
                    imdb_rating=src.get("imdb_rating"),
                )
            )

        await self._write_list_to_cache(key, rows)
        return rows

    async def search_films(
        self,
        query_str: str,
        page_number: int,
        page_size: int,
    ) -> List[FilmListItem]:
        params = {"q": query_str, "page_number": page_number, "page_size": page_size}
        key = _cache_key("films:search", params)

        rows = await self._read_list_from_cache(key)
        if rows is not None:
            return rows

        from_ = (page_number - 1) * page_size
        query = {
            "multi_match": {
                "query": query_str,
                "fields": ["title^3", "description"],
                "fuzziness": "AUTO",
            }
        }

        try:
            resp = await self.elastic.search(
                index=INDEX,
                query=query,
                sort=[{"imdb_rating": {"order": "desc", "missing": "_last"}}],
                from_=from_,
                size=page_size,
                _source=["id", "title", "imdb_rating"],
            )
        except NotFoundError:
            # индекса нет — пустой результат
            return []
        except TransportError as exc:
            raise HTTPException(
                status_code=503, detail="Elasticsearch is unavailable"
            ) from exc

        rows: List[FilmListItem] = []
        for hit in resp.get("hits", {}).get("hits", []):
            src = hit.get("_source", {})
            rows.append(
                FilmListItem(
                    uuid=src.get("id") or hit.get("_id", ""),
                    title=src.get("title", ""),
                    imdb_rating=src.get("imdb_rating"),
                )
            )

        await self._write_list_to_cache(key, rows)
        return rows

    # ---------- internals ----------
    async def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
        try:
            doc = await self.elastic.get(index=INDEX, id=film_id)
        except NotFoundError:
            return None
        src = doc.get("_source", {})
        src.setdefault("id", doc.get("_id"))
        return Film(**src)

    async def _film_from_cache(self, film_id: str) -> Optional[Film]:
        if not self.redis:
            return None
        try:
            data = await self.redis.get(film_id)
        except redis_exc.RedisError:
            return None
        if not data:
            return None
        try:
            return Film.parse_raw(data)
        except Exception:
            return None

    async def _put_film_to_cache(self, film: Film):
        if not self.redis:
            return
        try:
            await self.redis.set(film.id, film.json(), FILM_CACHE_EXPIRE_IN_SECONDS)
        except redis_exc.RedisError:
            pass

    def _build_list_query(
        self, sort: Optional[str], genre: Optional[str]
    ) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        es_sort: List[Dict[str, Any]] = []
        if sort:
            order = "desc" if sort.startswith("-") else "asc"
            field = sort.lstrip("+-")
            es_sort.append({field: {"order": order, "missing": "_last"}})

        must: List[Dict[str, Any]] = []
        if genre:
            must.append({"terms": {"genre": [genre]}})

        query: Dict[str, Any] = {"bool": {"must": must}} if must else {"match_all": {}}
        return query, es_sort or [
            {"imdb_rating": {"order": "desc", "missing": "_last"}}
        ]

    # -------- cache helpers for lists --------
    async def _read_list_from_cache(self, key: str) -> Optional[List[FilmListItem]]:
        if not self.redis:
            return None
        try:
            cached = await self.redis.get(key)
        except redis_exc.RedisError:
            return None
        if not cached:
            return None
        try:
            raw = json.loads(cached.decode("utf-8"))
            return [FilmListItem(**item) for item in raw]
        except Exception:
            return None

    async def _write_list_to_cache(self, key: str, rows: List[FilmListItem]) -> None:
        if not self.redis:
            return
        try:
            payload = json.dumps([r.dict() for r in rows]).encode("utf-8")
            await self.redis.set(key, payload, FILM_CACHE_EXPIRE_IN_SECONDS)
        except redis_exc.RedisError:
            pass


@lru_cache()
def get_film_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
