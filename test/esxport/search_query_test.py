"""Search API Test cases."""
import inspect
from pathlib import Path
from test.esxport._export_test import TestExport
from unittest.mock import Mock, patch

from typing_extensions import Self

from src.esxport import EsXport


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
        self.out_file = esxport_obj_with_data.opts.output_file
        mocker.patch.object(
            esxport_obj_with_data,
            "_validate_fields",
            return_value=None,
        )
        esxport_obj_with_data.search_query()
        assert Path(f"{esxport_obj_with_data.opts.output_file}.tmp").exists() is True
        TestExport.rm_export_file(f"{inspect.stack()[0].function}.csv")
