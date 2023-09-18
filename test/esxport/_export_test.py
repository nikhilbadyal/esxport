# Generated by CodiumAI
import json
from pathlib import Path
from typing import Any
from unittest.mock import create_autospec, patch

import pytest
from typing_extensions import Self

from src.click_opt.cli_options import CliOptions
from src.elastic import ElasticsearchClient
from src.esxport import EsXport


@patch("src.esxport.EsXport._validate_fields")
class TestExport:
    """Tests that the method exports the data with valid arguments."""

    out_file = "_export.csv"

    csv_header = ["age", "name"]

    def teardown_method(self: Self) -> None:
        """Cleaer up resources."""
        Path(f"{self.out_file}.tmp").unlink(missing_ok=True)

    def test_export_with_valid_arguments(
        self: Self,
        _: Any,
        mock_es_client: ElasticsearchClient,
        cli_options: CliOptions,
    ) -> None:
        """Checks if the method exports the data properly when given valid arguments."""
        export = create_autospec(EsXport(cli_options, mock_es_client).export)

        export()

        export.assert_called_once_with()

    def test_export_invalid_format(
        self: Self,
        _: Any,
        mock_es_client: ElasticsearchClient,
        cli_options: CliOptions,
    ) -> None:
        """Check if exception is raised when formatting is invalid."""
        cli_options.format = "invalid_format"
        with patch.object(EsXport, "_extract_headers", return_value=[]), pytest.raises(NotImplementedError):
            EsXport(cli_options, mock_es_client).export()

    def test_headers_extraction(
        self: Self,
        _: Any,
        mock_es_client: ElasticsearchClient,
        cli_options: CliOptions,
    ) -> None:
        """Check if exception is raised when formatting is invalid."""
        test_json = {"age": 2, "bar": "foo", "hello": "world"}
        with Path(f"{self.out_file}.tmp").open(mode="w", encoding="utf-8") as tmp_file:
            tmp_file.write(json.dumps(test_json))
            tmp_file.write("\n")
        keys = list(test_json.keys())
        cli_options.output_file = self.out_file
        assert EsXport(cli_options, mock_es_client)._extract_headers() == keys
