"""Retry requests."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any
from unittest import mock

import pytest
from elasticsearch.exceptions import ConnectionError
from typing_extensions import Self

from esxport.constant import TIMES_TO_TRY

if TYPE_CHECKING:
    from unittest.mock import Mock

    from esxport.esxport import EsXport


class TestRetry:
    """Test that retry happens on connection errors."""

    def test_retry_happens_on_connection_error(self: Self, mocker: Mock, esxport_obj: EsXport) -> None:
        """Test that retry happens on connect errors."""
        esxport_obj._check_indexes.retry.sleep = mock.Mock()  # type: ignore[attr-defined]
        mocker.patch.object(
            esxport_obj.es_client,
            "indices_exists",
            side_effect=ConnectionError("mocked error"),
        )
        with pytest.raises(ConnectionError):
            esxport_obj._check_indexes()

        stats: dict[str, Any] = esxport_obj._check_indexes.statistics  # type: ignore[attr-defined]
        assert "attempt_number" in stats
        assert stats["attempt_number"] == TIMES_TO_TRY
