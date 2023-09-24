"""Client Test cases."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import Self

    from esxport.elastic import ElasticsearchClient


class TestElasticsearchClient:
    """Elastic Client Test cases."""

    def test_index_exists(self: Self, es_index: str, elastic_client: ElasticsearchClient) -> None:
        """Test client return true when index exists."""
        assert elastic_client.indices_exists(index=es_index) is True
