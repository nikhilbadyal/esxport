"""Client Test cases."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import Mock, patch

import pytest
from elastic_transport import ObjectApiResponse

from esxport.click_opt.cli_options import CliOptions
from esxport.elastic import ElasticsearchClient
from esxport.exceptions import ScrollExpiredError

if TYPE_CHECKING:
    from typing_extensions import Self


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

    @pytest.mark.xdist_group(name="elastic")
    def test_scroll_success(self: Self, generate_test_csv: str, elastic_client: ElasticsearchClient) -> None:
        """Test client return true when index exists."""
        path = Path(generate_test_csv)
        index_name = path.stem
        size = 2
        body = {"query": {"match_all": {}}, "index": index_name, "scroll": "5m", "size": size}
        search_results = elastic_client.search(**body)
        assert size == len(search_results["hits"]["hits"])
        scroll_id = search_results["_scroll_id"]
        search_results = elastic_client.scroll(scroll="5m", scroll_id=scroll_id)
        assert size == len(search_results["hits"]["hits"])
        clear_result = elastic_client.clear_scroll(scroll_id="_all")
        assert clear_result["num_freed"] == 1

    @pytest.mark.xdist_group(name="elastic")
    def test_scroll_expired(self: Self, elastic_client: ElasticsearchClient) -> None:
        """Test client return true when index exists."""
        with pytest.raises(ScrollExpiredError):
            elastic_client.scroll(scroll="5m", scroll_id="brqwdwefwef")

    @pytest.mark.xdist_group(name="elastic")
    def test_ping(self: Self, elastic_client: ElasticsearchClient) -> None:
        """Test that ping returns valid cluster information."""
        response = elastic_client.ping()

        # Assert that the response is an instance of ObjectApiResponse
        assert isinstance(response, ObjectApiResponse), "Ping response should be an ObjectApiResponse."

        # Convert to dictionary and check for cluster information
        response_dict = response.raw
        assert isinstance(response_dict, dict), "Ping response should be convertible to a dictionary."
        assert "cluster_name" in response_dict, "Cluster name should be present in the ping response."
        assert "version" in response_dict, "Elasticsearch version should be present in the ping response."
        assert "tagline" in response_dict, "Tagline should be present in the ping response."

    @patch("esxport.elastic.elasticsearch.Elasticsearch")
    @pytest.mark.parametrize(
        ("url", "tls_expected"),
        [
            ("https://example.com:9200", True),
            ("http://example.com:9200", False),
            ("HTTPS://example.com:9200", True),  # Test uppercase scheme
            ("HTTP://example.com:9200", False),  # Test uppercase scheme
        ],
    )
    def test_url_scheme_handles_tls_options(
        self: Self,
        mock_elasticsearch: Mock,
        url: str,
        tls_expected: bool,  # noqa: FBT001
    ) -> None:
        """Test that TLS options are passed only for HTTPS URLs."""
        cli_options = CliOptions(
            {
                "query": {"query": {"match_all": {}}},
                "output_file": "test.csv",
                "url": url,
                "user": "test_user",
                "password": "test_password",
                "index_prefixes": ["test_index"],
                "verify_certs": True,
                "ca_certs": "/path/to/ca.crt",
                "client_cert": "/path/to/client.crt",
                "client_key": "/path/to/client.key",
            },
        )

        ElasticsearchClient(cli_options)

        mock_elasticsearch.assert_called_once()
        call_kwargs = mock_elasticsearch.call_args.kwargs

        assert call_kwargs["hosts"] == [url]
        assert call_kwargs["basic_auth"] == ("test_user", "test_password")

        if tls_expected:
            assert call_kwargs["verify_certs"] is True
            assert call_kwargs["ca_certs"] == "/path/to/ca.crt"
            assert call_kwargs["client_cert"] == "/path/to/client.crt"
            assert call_kwargs["client_key"] == "/path/to/client.key"
        else:
            assert "verify_certs" not in call_kwargs
            assert "ca_certs" not in call_kwargs
            assert "client_cert" not in call_kwargs
            assert "client_key" not in call_kwargs
