"""Testes para Celery tasks."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.mark.asyncio
async def test_sync_all_tenants_dispatches():
    """sync_all_tenants deve despachar sync_tenant para cada tenant ativo."""
    with patch("app.workers.tasks.sync_tenant") as mock_sync_tenant:
        mock_sync_tenant.delay = MagicMock()

        # Mock do banco retornando tenant_ids
        with patch("app.workers.tasks.AsyncSessionLocal") as mock_session_cls:
            mock_session = AsyncMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=False)

            mock_result = MagicMock()
            mock_result.all.return_value = ["tenant-1", "tenant-2"]
            mock_session.scalars = AsyncMock(return_value=mock_result)

            mock_session_cls.return_value = mock_session

            from app.workers.tasks import _sync_all_tenants_async
            await _sync_all_tenants_async()

        assert mock_sync_tenant.delay.call_count == 2
