"""Click CLI test cases."""
import inspect
import json
from pathlib import Path
from test.esxport._export_test import TestExport
from test.esxport._prepare_search_query_test import TestSearchQuery
from unittest.mock import patch

from click.testing import CliRunner
from typing_extensions import Self

from esxport.__init__ import __version__
from esxport.esxport import EsXport
from esxport.esxport_cli import cli
from esxport.strings import cli_version, invalid_query_format, invalid_sort_format

args = {
    "q": '{"query":{"match_all":{}}}',
    "o": "output.csv",
    "i": "index1",
}
usage_error_code = 2
random_pass = "password\n"  # noqa: S105
export_module = "esxport.esxport.EsXport"


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
        with patch(export_module, return_value=esxport_obj_with_data):
            result = cli_runner.invoke(
                cli,
                ["-q", args["q"], "-o", args["o"], "-i", args["i"]],
                input=random_pass,
                catch_exceptions=False,
            )
            assert result.exit_code == 0
        with Path(esxport_obj_with_data.opts.output_file).open("r") as fp:
            lines = len(fp.readlines())
            assert lines == esxport_obj_with_data.es_client.search()["hits"]["total"]["value"] + 1  # 1 for header
        TestExport.rm_csv_export_file(esxport_obj_with_data.opts.output_file)

    def test_sort_type(self: Self, cli_runner: CliRunner, esxport_obj_with_data: EsXport) -> None:
        """Test sort type is asc or desc."""
        esxport_obj_with_data.opts.output_file = f"{inspect.stack()[0].function}.csv"
        random_string = TestSearchQuery.random_string(10)
        with patch(export_module, return_value=esxport_obj_with_data):
            result = cli_runner.invoke(
                cli,
                ["-q", args["q"], "-o", args["o"], "-i", args["i"], "-S", f"field:{random_string}"],
                input=random_pass,
                catch_exceptions=False,
            )
            error_msg = f"Error: Invalid value for '-S' / '--sort': Invalid sort type {random_string}."
            assert error_msg in result.output
            assert result.exit_code == usage_error_code

            result = cli_runner.invoke(
                cli,
                ["-q", args["q"], "-o", args["o"], "-i", args["i"], "-S", "field:desc"],
                input=random_pass,
                catch_exceptions=False,
            )
            error_msg = f"Error: Invalid value for '-S' / '--sort': Invalid sort type {random_string}."
            assert error_msg not in result.output
            assert result.exit_code == 0
            TestExport.rm_csv_export_file(esxport_obj_with_data.opts.output_file)

    def test_sort_format(self: Self, cli_runner: CliRunner, esxport_obj_with_data: EsXport) -> None:
        """Test sort input is in the form field:sort_order."""
        esxport_obj_with_data.opts.output_file = f"{inspect.stack()[0].function}.csv"
        random_string = TestSearchQuery.random_string(10)
        with patch(export_module, return_value=esxport_obj_with_data):
            result = cli_runner.invoke(
                cli,
                ["-q", args["q"], "-o", args["o"], "-i", args["i"], "-S", f"field@{random_string}"],
                input=random_pass,
                catch_exceptions=False,
            )
            error_msg = invalid_sort_format.format(value=f"field@{random_string}")
            assert error_msg in result.output
            assert result.exit_code == usage_error_code

    def test_query_accepts_dict(self: Self, cli_runner: CliRunner, esxport_obj_with_data: EsXport) -> None:
        """Test sort input is in the form field:sort_order."""
        esxport_obj_with_data.opts.output_file = f"{inspect.stack()[0].function}.csv"
        with patch(export_module, return_value=esxport_obj_with_data):
            result = cli_runner.invoke(
                cli,
                ["-q", json.dumps(args["q"]), "-o", args["o"], "-i", args["i"]],
                input=random_pass,
                catch_exceptions=False,
            )
            assert result.exit_code == 0
            TestExport.rm_csv_export_file(esxport_obj_with_data.opts.output_file)

    def test_error_is_rasied_on_invalid_json(self: Self, cli_runner: CliRunner) -> None:
        """Test sort input is in the form field:sort_order."""
        result = cli_runner.invoke(
            cli,
            ["-q", "@", "-o", args["o"], "-i", args["i"]],
            input=random_pass,
            catch_exceptions=False,
        )
        json_error_message = invalid_query_format.format(value="@", exc="")
        assert json_error_message in result.output
        assert result.exit_code == usage_error_code

    def test_cli_version_check(self: Self, cli_runner: CliRunner) -> None:
        """Test version is printed correctly."""
        result = cli_runner.invoke(
            cli,
            ["-v"],
            catch_exceptions=False,
        )
        version_message = cli_version.format(__version__=__version__)
        assert version_message == result.output.strip()
        assert result.exit_code == 0
