"""Search API Test cases."""
import inspect
import json
from pathlib import Path
from test.esxport._export_test import TestExport
from test.esxport._prepare_search_query_test import TestSearchQuery
from unittest.mock import Mock, patch

import pytest
from typing_extensions import Self

from src.esxport import EsXport
from src.exceptions import MetaFieldNotFoundError, ScrollExpiredError


class TestVSearchQuery:
    """Search API Test cases."""

    def test_data_not_flused_when_results_are_zero(self: Self, mocker: Mock, esxport_obj: EsXport) -> None:
        """Test that export is not called if no of records are zero."""
        esxport_obj.opts.output_file = f"{inspect.stack()[0].function}.csv"
        mocker.patch.object(
            esxport_obj,
            "_validate_fields",
            return_value=None,
        )
        with patch.object(esxport_obj, "_write_to_temp_file") as mock_write_to_temp_file:
            esxport_obj.search_query()
            mock_write_to_temp_file.assert_not_called()
            assert Path(f"{esxport_obj.opts.output_file}.tmp").exists() is False

    def test_data_flused_when_results_are_non_zero(self: Self, mocker: Mock, esxport_obj_with_data: EsXport) -> None:
        """Test that export is not called if no of records are zero."""
        esxport_obj_with_data.opts.output_file = f"{inspect.stack()[0].function}.csv"
        mocker.patch.object(
            esxport_obj_with_data,
            "_validate_fields",
            return_value=None,
        )
        with patch.object(esxport_obj_with_data, "_write_to_temp_file") as mock_write_to_temp_file:
            esxport_obj_with_data.search_query()
            mock_write_to_temp_file.assert_called_once_with(esxport_obj_with_data.es_client.search())
        TestExport.rm_export_file(f"{inspect.stack()[0].function}.csv")

    def test_data_flused_when_results_are_non_zero1(self: Self, mocker: Mock, esxport_obj_with_data: EsXport) -> None:
        """Test that export is not called if no of records are zero."""
        esxport_obj_with_data.opts.output_file = f"{inspect.stack()[0].function}.csv"
        mocker.patch.object(
            esxport_obj_with_data,
            "_validate_fields",
            return_value=None,
        )
        esxport_obj_with_data.search_query()
        assert Path(f"{esxport_obj_with_data.opts.output_file}.tmp").exists() is True
        TestExport.rm_export_file(f"{inspect.stack()[0].function}.csv")

    def test_meta_fields_are_flushed(self: Self, mocker: Mock, esxport_obj_with_data: EsXport) -> None:
        """Test that meta fields are dumped."""
        esxport_obj_with_data.opts.output_file = f"{inspect.stack()[0].function}.csv"
        esxport_obj_with_data.opts.meta_fields = ["_score", "_id"]
        mocker.patch.object(
            esxport_obj_with_data,
            "_validate_fields",
            return_value=None,
        )
        esxport_obj_with_data.search_query()
        with Path(f"{inspect.stack()[0].function}.csv.tmp").open() as f:
            first_line = json.loads(f.readline().strip("\n"))
            assert first_line.keys() == esxport_obj_with_data.es_client.search()["hits"]["hits"][0]["_source"].keys()
            TestExport.rm_export_file(f"{inspect.stack()[0].function}.csv")

    def test_invalid_meta_fields_raises_exception(
        self: Self,
        mocker: Mock,
        esxport_obj_with_data: EsXport,
    ) -> None:
        """Test that invalid meta fields raised exception."""
        esxport_obj_with_data.opts.output_file = f"{inspect.stack()[0].function}.csv"
        random_strings = [TestSearchQuery.random_string(10) for _ in range(5)]
        esxport_obj_with_data.opts.meta_fields = random_strings
        mocker.patch.object(
            esxport_obj_with_data,
            "_validate_fields",
            return_value=None,
        )
        with pytest.raises(MetaFieldNotFoundError):
            esxport_obj_with_data.search_query()
        TestExport.rm_export_file(f"{inspect.stack()[0].function}.csv")

    def test_data_is_flused_on_buffer_hit(
        self: Self,
        esxport_obj_with_data: EsXport,
    ) -> None:
        """Test that invalid meta fields raised exception."""
        data = esxport_obj_with_data.es_client.search()
        no_of_records = data["hits"]["total"]["value"]
        flush_size = 1
        with patch.object(esxport_obj_with_data, "_flush_to_file") as mock_flush_to_file, patch(
            "src.esxport.FLUSH_BUFFER",
            flush_size,
        ):
            esxport_obj_with_data.search_query()
            assert mock_flush_to_file.call_count == no_of_records / flush_size + 1

    def test_function_exits_when_scroll_expire(self: Self, mocker: Mock, esxport_obj_with_data: EsXport) -> None:
        """Test function exist when scroll expires."""
        esxport_obj_with_data.opts.output_file = f"{inspect.stack()[0].function}.csv"
        flush_size = 1
        mocker.patch.object(
            esxport_obj_with_data.es_client,
            "scroll",
            side_effect=ScrollExpiredError("abc"),
        )
        with patch("src.esxport.FLUSH_BUFFER", flush_size), patch.object(esxport_obj_with_data, "num_results", 4):
            esxport_obj_with_data.search_query()
            assert Path(f"{esxport_obj_with_data.opts.output_file}.tmp").exists() is True
            assert Path(esxport_obj_with_data.opts.output_file).exists() is False
            TestExport.rm_export_file(f"{inspect.stack()[0].function}.csv")
