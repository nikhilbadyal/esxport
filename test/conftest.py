"""Conftest for Pytest."""
from typing import Any
from unittest.mock import Mock

import pytest

from src.click_opt.cli_options import CliOptions


@pytest.fixture()
def cli_options() -> CliOptions:
    """Mock Click CLI options."""
    query: dict[str, Any] = {"query": {"match_all": {}}}
    return CliOptions(
        {
            "query": query,
            "output_file": "output.csv",
            "url": "http://localhost:9200",
            "user": "admin",
            "password": "password",
            "index_prefixes": ["index1", "index2"],
            "fields": ["field1", "field2"],
            "sort": [],
            "delimiter": ",",
            "max_results": 100,
            "scroll_size": 100,
            "meta_fields": [],
            "verify_certs": True,
            "ca_certs": None,
            "client_cert": None,
            "client_key": None,
            "debug": False,
        },
    )


@pytest.fixture()
def mock_es_client() -> Mock:
    """Mock ElasticSearch Client."""
    mock_client = Mock()
    mock_client.search.return_value = {
        "hits": {
            "total": {
                "value": 0,
            },
        },
    }
    return mock_client
