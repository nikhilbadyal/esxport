"""Conftest for Pytest."""
from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from test.esxport._prepare_search_query_test import TestSearchQuery
from typing import TYPE_CHECKING, Any, Iterator
from unittest.mock import Mock, patch

import pytest
from dotenv import load_dotenv
from elasticsearch.helpers import bulk
from faker import Faker
from filelock import FileLock
from pytest_elasticsearch import factories

from esxport.click_opt.cli_options import CliOptions
from esxport.elastic import ElasticsearchClient
from esxport.esxport import EsXport

if TYPE_CHECKING:
    from _pytest.tmpdir import TempPathFactory
    from elasticsearch import Elasticsearch

load_dotenv(Path(Path(__file__).resolve().parent, ".env"))

elasticsearch_nooproc = factories.elasticsearch_noproc(
    port=9200,
    scheme="https",
    host="localhost",
    user="elastic",
    password=os.getenv("ELASTICSEARCH_PASSWORD"),
)
elasticsearch_proc = factories.elasticsearch("elasticsearch_nooproc")


@pytest.fixture()
def cli_options() -> CliOptions:
    """Mock Click CLI options."""
    query: dict[str, Any] = {"query": {"match_all": {}}}
    return CliOptions(
        {
            "query": query,
            "output_file": "output.csv",
            "url": "https://localhost:9200",
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
    mock_client.get_mapping.return_value = {
        "index1": {
            "mappings": {
                "properties": ["test_id"],
            },
        },
        "index2": {
            "mappings": {
                "properties": ["field1", "field2", "field3"],
            },
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


@pytest.fixture(autouse=True)
def _capture_wrap() -> None:
    """Avoid https://github.com/pytest-dev/pytest/issues/5502."""
    sys.stderr.close = lambda *args: None  # type: ignore[method-assign] #noqa: ARG005
    sys.stdout.close = lambda *args: None  # type: ignore[method-assign] #noqa: ARG005


@pytest.fixture(scope="session")
def index_name() -> str:
    """Index name."""
    return TestSearchQuery.random_string(10).lower()


@pytest.fixture()
def es_index(index_name: str, elasticsearch_proc: Elasticsearch) -> Any:
    """Create index."""
    elasticsearch_proc.indices.create(index=index_name)
    return index_name


# noinspection PyTypeChecker
def generate_actions(dataset_path: str) -> Iterator[dict[str, Any]]:
    """Reads the file through csv.DictReader() and for each row yields a single document.

    This function is passed into the bulk() helper to create many documents in sequence.
    """
    with Path(dataset_path).open() as f:
        reader = csv.DictReader(f)

        for row in reader:
            doc = {
                "id": row["id"],
                "name": row["name"],
                "email": row["email"],
                "phone": row["phone"],
                "address": row["address"] or None,
            }
            yield doc


@pytest.fixture()
def populate_data(es_index: str, elasticsearch_proc: Elasticsearch) -> Elasticsearch:
    """Populates the data in elastic instances."""
    bulk(client=elasticsearch_proc, index=es_index, actions=generate_actions(es_index + ".csv"))
    return elasticsearch_proc


@pytest.fixture()
def elastic_client(
    cli_options: CliOptions,
    populate_data: Elasticsearch,
    generate_test_csv: str,  # noqa: ARG001
) -> Iterator[ElasticsearchClient]:
    """Patches Elasticsearch client."""
    es_client = ElasticsearchClient(cli_options)
    with patch.object(es_client, "client", populate_data):
        yield es_client


def _create_csv(csv_file_name: str) -> None:
    # Create a Faker instance
    fake = Faker()

    # Define the number of rows you want in your CSV
    num_rows = TestSearchQuery.random_number(10, 20)

    # Define the CSV header
    csv_header = ["id", "name", "email", "phone", "address"]

    # Generate random data and write it to the CSV file
    with Path(csv_file_name).open("w", newline="") as csvfile:
        writer = csv.writer(csvfile)

        # Write the header row
        writer.writerow(csv_header)

        # Generate and write random data rows
        for i in range(1, num_rows + 1):
            name = fake.name()
            email = fake.email()
            phone = fake.phone_number()
            address = fake.address()

            # Write the data to the CSV file
            writer.writerow([i, name, email, phone, address])


# https://github.com/pytest-dev/pytest-xdist/issues/271
@pytest.fixture(scope="session")
def generate_test_csv(index_name: str, tmp_path_factory: TempPathFactory, worker_id: str) -> Iterator[str]:
    """Generate random csv for testing."""
    csv_file_name = f"{index_name}.csv"

    if worker_id == "master":
        yield csv_file_name

    # get the temp directory shared by all workers
    root_tmp_dir = tmp_path_factory.getbasetemp().parent

    fn = root_tmp_dir / "data.json"
    with FileLock(str(fn) + ".lock"):
        if fn.is_file():
            data = json.loads(fn.read_text())
        else:
            _create_csv(csv_file_name)
            data = csv_file_name
            fn.write_text(json.dumps(data))

    yield data
    Path(csv_file_name).unlink(missing_ok=True)
