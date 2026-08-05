"""Tests for api/routes/health.py"""

from unittest.mock import AsyncMock, patch

import pytest

from api.routes.health import health_check


@pytest.mark.unit
class TestHealthCheck:
    """Test suite for the health check endpoint."""

    @pytest.mark.asyncio
    async def test_health_check_postgres_healthy(self):
        """Test health check reports postgres healthy when SELECT 1 succeeds."""
        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=None)

        with patch("redis.Redis") as mock_redis_cls, \
             patch("core.config.settings") as mock_settings:
            mock_redis_cls.return_value.ping.return_value = True
            mock_settings.vector_db_url = "http://fake-vector-db"
            mock_settings.redis_host = "localhost"
            mock_settings.redis_port = 6379

            result = await health_check(db=mock_db)

        assert result["dependencies"]["postgres"] == "healthy"

    @pytest.mark.asyncio
    async def test_health_check_postgres_query_uses_text_wrapper(self):
        """Regression test for #154: raw SQL must be wrapped via text()."""
        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=None)

        with patch("redis.Redis") as mock_redis_cls, \
             patch("core.config.settings") as mock_settings:
            mock_redis_cls.return_value.ping.return_value = True
            mock_settings.vector_db_url = "http://fake-vector-db"
            mock_settings.redis_host = "localhost"
            mock_settings.redis_port = 6379

            await health_check(db=mock_db)

        called_arg = mock_db.execute.call_args[0][0]
        assert not isinstance(called_arg, str)

    @pytest.mark.asyncio
    async def test_health_check_postgres_unhealthy_on_db_error(self):
        """Test health check reports postgres unhealthy when the query fails."""
        from fastapi import HTTPException

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(side_effect=ConnectionError("connection refused"))

        with patch("redis.Redis") as mock_redis_cls, \
             patch("core.config.settings") as mock_settings:
            mock_redis_cls.return_value.ping.return_value = True
            mock_settings.vector_db_url = "http://fake-vector-db"
            mock_settings.redis_host = "localhost"
            mock_settings.redis_port = 6379

            with pytest.raises(HTTPException) as exc_info:
                await health_check(db=mock_db)

            assert exc_info.value.status_code == 503
            assert exc_info.value.detail["dependencies"]["postgres"] == "unhealthy"
