from unittest.mock import AsyncMock

import pytest

from app.services.genre import GenreService
from app.services.person import PersonService


class TestCommonServices:
    @pytest.mark.asyncio
    async def test_genre_service_methods(self):
        """Тест методов сервиса жанров"""
        mock_elastic = AsyncMock()
        service = GenreService(mock_elastic)

        # Тест get_by_id
        result = await service.get_by_id("nonexistent-id")
        assert result is None

        # Тест get_all
        result = await service.get_all()
        assert result == []

    @pytest.mark.asyncio
    async def test_person_service_methods(self):
        """Тест методов сервиса персон"""
        mock_elastic = AsyncMock()
        service = PersonService(mock_elastic)

        # Тест get_by_id
        result = await service.get_by_id("nonexistent-id")
        assert result is None

        # Тест search
        result = await service.search("test query")
        assert result == []
