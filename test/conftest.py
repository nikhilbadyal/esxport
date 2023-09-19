"""Conftest for Pytest."""
from __future__ import annotations

from typing import Any
from unittest.mock import Mock

import pytest

from src.click_opt.cli_options import CliOptions
from src.esxport import EsXport


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
def es_client_without_data() -> Mock:
    """Mock ElasticSearch Client."""
    mock_client = Mock()
    mock_client.search.return_value = {
        "_scroll_id": "abc",
        "hits": {
            "total": {
                "value": 0,
            },
            "hits": None,
        },
    }
    return mock_client


@pytest.fixture()
def es_client_with_data() -> Mock:
    """Mock ElasticSearch Client."""
    mock_client = Mock()
    mock_client.search.return_value = {
        "_scroll_id": "abc",
        "hits": {
            "total": {
                "value": 2,
            },
            "hits": [
                {
                    "_index": "index1",
                    "_id": "ABC",
                    "_score": 2,
                    "_source": {
                        "test_id": "ABC",
                    },
                },
                {
                    "_index": "index1",
                    "_id": "DEF",
                    "_score": 1,
                    "_source": {
                        "test_id": "DEF",
                    },
                },
            ],
        },
    }
    return mock_client


@pytest.fixture()
def esxport_obj(cli_options: CliOptions, es_client_without_data: Mock) -> EsXport:
    """Mocked EsXport class."""
    return EsXport(cli_options, es_client_without_data)


@pytest.fixture()
def esxport_obj_with_data(cli_options: CliOptions, es_client_with_data: Mock) -> EsXport:
    """Mocked EsXport class."""
    return EsXport(cli_options, es_client_with_data)
