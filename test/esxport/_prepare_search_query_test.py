"""Export testing."""
from __future__ import annotations

import string
from random import choice, randint
from typing import TYPE_CHECKING, Any
from unittest.mock import patch

import pytest

from src.esxport import EsXport
from src.exceptions import IndexNotFoundError
from src.strings import index_not_found

if TYPE_CHECKING:
    from typing_extensions import Self

    from src.click_opt.cli_options import CliOptions
    from src.elastic import ElasticsearchClient


@patch("src.esxport.EsXport._validate_fields")
class TestSearchQuery:
    """Tests that a search query with valid input parameters is successful."""

    @staticmethod
    def random_string(str_len: int = 20) -> str:
        """Generates a random string."""
        characters = string.ascii_letters + string.digits
        return "".join(choice(characters) for _ in range(str_len))

    @staticmethod
    def random_number(upper: int = 100, lower: int = 10000) -> int:
        """Generates a random number."""
        return randint(upper, lower)

    def test_index(
        self: Self,
        _: Any,
        mock_es_client: ElasticsearchClient,
        cli_options: CliOptions,
    ) -> None:
        """Arr, matey!.

        Let's test if our search query be successful, with valid input parameters!.
        """
        random_strings = [self.random_string(10) for _ in range(5)]
        cli_options.index_prefixes = random_strings
        indexes = ",".join(random_strings)

        es_export = EsXport(cli_options, mock_es_client)
        es_export._prepare_search_query()
        assert es_export.search_args["index"] == indexes

    def test_all_index(
        self: Self,
        _: Any,
        mock_es_client: ElasticsearchClient,
        cli_options: CliOptions,
    ) -> None:
        """Arr, matey!.

        Let's test if our search query be successful, with valid input parameters!.
        """
        cli_options.index_prefixes = ["_all", "invalid_index"]

        es_export = EsXport(cli_options, mock_es_client)
        es_export._check_indexes()
        assert es_export.opts.index_prefixes == ["_all"]

    def test_invalid_index(
        self: Self,
        _: Any,
        mock_es_client: ElasticsearchClient,
        cli_options: CliOptions,
    ) -> None:
        """Arr, matey!.

        Let's test if our search query be successful, with valid input parameters!.
        """
        cli_options.index_prefixes = ["invalid_index"]
        es_export = EsXport(cli_options, mock_es_client)

        with patch.object(es_export.es_client, "indices_exists", return_value=False):
            with pytest.raises(IndexNotFoundError) as exc_info:
                es_export._check_indexes()

            msg = index_not_found.format("invalid_index", cli_options.url)
            assert str(exc_info.value) == msg

    def test_size(
        self: Self,
        _: Any,
        mock_es_client: ElasticsearchClient,
        cli_options: CliOptions,
    ) -> None:
        """Arr, matey!.

        Let's test if our search query be successful, with valid input parameters!.
        """
        page_size = randint(100, 9999)
        cli_options.scroll_size = page_size

        es_export = EsXport(cli_options, mock_es_client)
        es_export._prepare_search_query()
        assert es_export.search_args["size"] == page_size

    def test_query(
        self: Self,
        _: Any,
        mock_es_client: ElasticsearchClient,
        cli_options: CliOptions,
    ) -> None:
        """Arr, matey!.

        Let's test if our search query be successful, with valid input parameters!.
        """
        expected_query: dict[str, Any] = {"query": {"match_all": {}}}
        cli_options.query = expected_query

        es_export = EsXport(cli_options, mock_es_client)
        es_export._prepare_search_query()
        assert es_export.search_args["body"] == expected_query

    def test_terminate_after(
        self: Self,
        _: Any,
        mock_es_client: ElasticsearchClient,
        cli_options: CliOptions,
    ) -> None:
        """Arr, matey!.

        Let's test if our search query be successful, with valid input parameters!.
        """
        random_max = self.random_number()
        cli_options.max_results = random_max

        es_export = EsXport(cli_options, mock_es_client)
        es_export._prepare_search_query()
        assert es_export.search_args["terminate_after"] == random_max

    def test_sort(
        self: Self,
        _: Any,
        mock_es_client: ElasticsearchClient,
        cli_options: CliOptions,
    ) -> None:
        """Arr, matey!.

        Let's test if our search query be successful, with valid input parameters!.
        """
        random_sort = [{self.random_string(): "asc"}, {self.random_string(): "desc"}]
        cli_options.sort = random_sort

        es_export = EsXport(cli_options, mock_es_client)
        es_export._prepare_search_query()
        assert es_export.search_args["sort"] == random_sort
