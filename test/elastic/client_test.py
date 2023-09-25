"""Client Test cases."""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from typing_extensions import Self

    from esxport.elastic import ElasticsearchClient


class TestElasticsearchClient:
    """Elastic Client Test cases."""

    # https://github.com/pytest-dev/pytest-xdist/issues/385#issuecomment-1304877301
    @pytest.mark.xdist_group(name="elastic")
    def test_index_exists(self: Self, generate_test_csv: str, elastic_client: ElasticsearchClient) -> None:
        """Test client return true when index exists."""
        path = Path(generate_test_csv)
        index_name = path.stem
        assert elastic_client.indices_exists(index=index_name) is True

    @pytest.mark.xdist_group(name="elastic")
    def test_get_mapping(self: Self, generate_test_csv: str, elastic_client: ElasticsearchClient) -> None:
        """Test client return true when index exists."""
        path = Path(generate_test_csv)
        index_name = path.stem
        assert elastic_client.get_mapping(index=index_name) is not None

    @pytest.mark.xdist_group(name="elastic")
    def test_search(self: Self, generate_test_csv: str, elastic_client: ElasticsearchClient) -> None:
        """Test client return true when index exists."""
        path = Path(generate_test_csv)
        index_name = path.stem
        with Path(path).open("r") as fp:
            lines = len(fp.readlines())
        elastic_client.client.indices.refresh(index=index_name)
        body = {"query": {"match_all": {}}, "index": index_name}
        response = elastic_client.search(**body)
        assert response["hits"]["total"]["value"] == (lines - 1) / 2
