"""Click CLI test cases."""
import inspect
from pathlib import Path
from test.esxport._export_test import TestExport
from unittest.mock import patch

from click.testing import CliRunner
from typing_extensions import Self

from src.esxport import EsXport
from src.esxport_cli import cli

args = {
    "q": '{"query":{"match_all":{}}}',
    "o": "output.csv",
    "i": "index1",
}
usage_error_code = 2


# noinspection PyTypeChecker
class TestCli:
    """Cli Test cases."""

    def test_query_is_mandatory(self: Self, cli_runner: CliRunner) -> None:
        """Test Query param is mandatory."""
        query_missing = "Error: Missing option '-q' / '--query'."
        result = cli_runner.invoke(cli, [], catch_exceptions=False)
        assert query_missing in result.output
        assert result.exit_code == usage_error_code

    def test_output_file_is_mandatory(self: Self, cli_runner: CliRunner) -> None:
        """Test Query param is mandatory."""
        query_missing = "Error: Missing option '-o' / '--output-file'."
        result = cli_runner.invoke(cli, ["-q", args["q"]], catch_exceptions=False)
        assert query_missing in result.output
        assert result.exit_code == usage_error_code

    def test_index_is_mandatory(self: Self, cli_runner: CliRunner) -> None:
        """Test Index param is mandatory."""
        query_missing = "Error: Missing option '-i' / '--index-prefixes'."
        result = cli_runner.invoke(cli, ["-q", args["q"], "-o", args["o"]], input="secret\n", catch_exceptions=False)
        assert query_missing in result.output
        assert result.exit_code == usage_error_code

    def test_mandatory(self: Self, cli_runner: CliRunner, esxport_obj_with_data: EsXport) -> None:
        """Test Index param is mandatory."""
        esxport_obj_with_data.opts.output_file = f"{inspect.stack()[0].function}.csv"
        with patch("src.esxport.EsXport", return_value=esxport_obj_with_data):
            result = cli_runner.invoke(
                cli,
                ["-q", args["q"], "-o", args["o"], "-i", args["i"]],
                input="password\n",
                catch_exceptions=False,
            )
            assert result.exit_code == 0
        with Path(esxport_obj_with_data.opts.output_file).open("r") as fp:
            lines = len(fp.readlines())
            assert lines == esxport_obj_with_data.es_client.search()["hits"]["total"]["value"] + 1  # 1 for header
        TestExport.rm_csv_export_file(esxport_obj_with_data.opts.output_file)
