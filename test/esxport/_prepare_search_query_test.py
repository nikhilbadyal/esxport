"""Export testing."""
from __future__ import annotations

import string
from random import choice, randint
from typing import TYPE_CHECKING, Any
from unittest.mock import patch

import pytest

from esxport.exceptions import IndexNotFoundError
from esxport.strings import index_not_found, output_fields, sorting_by, using_indexes

if TYPE_CHECKING:
    from typing_extensions import Self

    from esxport.esxport import EsXport


@patch("esxport.esxport.EsXport._validate_fields")
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

    def test_index(self: Self, _: Any, esxport_obj: EsXport) -> None:
        """Arr, matey!.

        Let's test if our search query be successful, with valid input parameters!.
        """
        random_strings = [self.random_string(10) for _ in range(5)]
        esxport_obj.opts.index_prefixes = random_strings
        indexes = ",".join(random_strings)

        esxport_obj._prepare_search_query()
        assert esxport_obj.search_args["index"] == indexes

    def test_all_index(self: Self, _: Any, esxport_obj: EsXport) -> None:
        """Arr, matey!.

        Let's test if our search query be successful, with valid input parameters!.
        """
        esxport_obj.opts.index_prefixes = ["_all", "invalid_index"]
        esxport_obj._check_indexes()
        assert esxport_obj.opts.index_prefixes == ["_all"]

    def test_invalid_index(
        self: Self,
        _: Any,
        esxport_obj: EsXport,
    ) -> None:
        """Arr, matey!.

        Let's test if our search query be successful, with valid input parameters!.
        """
        esxport_obj.opts.index_prefixes = ["invalid_index"]

        with patch.object(esxport_obj.es_client, "indices_exists", return_value=False):
            with pytest.raises(IndexNotFoundError) as exc_info:
                esxport_obj._check_indexes()

            msg = index_not_found.format("invalid_index", esxport_obj.opts.url)
            assert str(exc_info.value) == msg

    def test_size(
        self: Self,
        _: Any,
        esxport_obj: EsXport,
    ) -> None:
        """Arr, matey!.

        Let's test if our search query be successful, with valid input parameters!.
        """
        page_size = randint(100, 9999)
        esxport_obj.opts.scroll_size = page_size

        esxport_obj._prepare_search_query()
        assert esxport_obj.search_args["size"] == page_size

    def test_query(self: Self, _: Any, esxport_obj: EsXport) -> None:
        """Arr, matey!.

        Let's test if our search query be successful, with valid input parameters!.
        """
        expected_query: dict[str, Any] = {"query": {"match_all": {}}}
        esxport_obj.opts.query = expected_query
        actual_query = expected_query["query"]

        esxport_obj._prepare_search_query()
        assert esxport_obj.search_args["query"] == actual_query

    def test_terminate_after(self: Self, _: Any, esxport_obj: EsXport) -> None:
        """Arr, matey!.

        Let's test if our search query be successful, with valid input parameters!.
        """
        random_max = self.random_number()
        esxport_obj.opts.max_results = random_max
        esxport_obj._prepare_search_query()
        assert esxport_obj.search_args["terminate_after"] == random_max

    def test_sort(
        self: Self,
        _: Any,
        esxport_obj: EsXport,
    ) -> None:
        """Arr, matey!.

        Let's test if our search query be successful, with valid input parameters!.
        """
        random_sort = [{self.random_string(): "asc"}, {self.random_string(): "desc"}]
        esxport_obj.opts.sort = random_sort

        esxport_obj._prepare_search_query()
        assert esxport_obj.search_args["sort"] == random_sort

    def test_debug_option(
        self: Self,
        _: Any,
        esxport_obj: EsXport,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Arr, matey!.

        Let's test if our search query be successful, with valid input parameters!.
        """
        esxport_obj.opts.debug = True

        esxport_obj._prepare_search_query()
        assert caplog.records[0].msg == using_indexes.format(indexes={", ".join(esxport_obj.opts.index_prefixes)})
        assert caplog.records[1].msg.startswith("Using query")
        assert caplog.records[2].msg == output_fields.format(fields={", ".join(esxport_obj.opts.fields)})
        assert caplog.records[3].msg == sorting_by.format(sort=esxport_obj.opts.sort)

    def test_custom_output_fields(self: Self, _: Any, esxport_obj: EsXport) -> None:
        """Test if selection only some fields for the output works."""
        random_strings = [self.random_string(10) for _ in range(5)]
        esxport_obj.opts.fields = random_strings
        esxport_obj._prepare_search_query()
        assert esxport_obj.search_args["_source_includes"] == ",".join(random_strings)
