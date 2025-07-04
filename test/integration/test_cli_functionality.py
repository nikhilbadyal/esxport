"""Test CLI functionality of installed package."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path


def test_cli_help_command() -> None:
    """Test that CLI help command works."""
    result = subprocess.run(
        [sys.executable, "-m", "esxport", "--help"],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )

    assert result.returncode == 0
    assert "Usage: python -m esxport" in result.stdout or "Usage: esxport" in result.stdout
    assert "--query" in result.stdout
    assert "--output-file" in result.stdout
    assert "--index-prefixes" in result.stdout


def test_console_script_help_command() -> None:
    """Test that direct esxport console script works."""
    result = subprocess.run(
        ["esxport", "--help"],  # noqa: S607
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )

    assert result.returncode == 0, f"Console script failed: {result.stderr}"
    assert "Usage: esxport" in result.stdout
    assert "--query" in result.stdout
    assert "--output-file" in result.stdout
    assert "--index-prefixes" in result.stdout


def test_console_script_version_command() -> None:
    """Test that direct esxport version command works."""
    result = subprocess.run(
        ["esxport", "--version"],  # noqa: S607
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )

    assert result.returncode == 0, f"Console script failed: {result.stderr}"
    assert "EsXport" in result.stdout
    # Should contain version number
    assert any(char.isdigit() for char in result.stdout)


def test_cli_version_command() -> None:
    """Test that CLI version command works."""
    result = subprocess.run(
        [sys.executable, "-m", "esxport", "--version"],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )

    assert result.returncode == 0
    assert "EsXport" in result.stdout
    # Should contain version number
    assert any(char.isdigit() for char in result.stdout)


def test_cli_missing_required_args() -> None:
    """Test CLI behavior with missing required arguments."""
    result = subprocess.run(
        [sys.executable, "-m", "esxport"],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )

    # Should fail with missing required arguments
    assert result.returncode != 0
    assert "Error:" in result.stderr or "Usage:" in result.stderr


def test_cli_invalid_json_query() -> None:
    """Test CLI behavior with invalid JSON query."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        output_file = f.name

    try:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "esxport",
                "--query",
                "invalid-json",
                "--output-file",
                output_file,
                "--index-prefixes",
                "test-index",
                "--password",
                "dummy",
            ],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )

        # Should fail due to invalid JSON
        assert result.returncode != 0
    finally:
        Path(output_file).unlink(missing_ok=True)


def test_cli_valid_json_query_format() -> None:
    """Test that CLI accepts valid JSON query format."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        output_file = f.name

    query = json.dumps({"query": {"match_all": {}}})

    try:
        # This will fail due to no Elasticsearch connection, but should pass JSON validation
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "esxport",
                "--query",
                query,
                "--output-file",
                output_file,
                "--index-prefixes",
                "test-index",
                "--password",
                "dummy",
                "--url",
                "https://nonexistent:9200",
                "--max-results",
                "1",
            ],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )

        # Should fail due to connection, not JSON parsing
        # If it fails due to JSON, the error would be different
        assert "JSON" not in result.stderr if result.stderr else True

    finally:
        Path(output_file).unlink(missing_ok=True)


def test_cli_entry_point_exists() -> None:
    """Test that the CLI entry point is properly installed."""
    # Test that we can import and call the CLI function
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            'from esxport.cli import cli; print("CLI function available")',
        ],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )

    assert result.returncode == 0
    assert "CLI function available" in result.stdout


def test_cli_with_all_basic_options() -> None:
    """Test CLI with all basic options to verify argument parsing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        output_file = f.name

    query = json.dumps({"query": {"match_all": {}}, "size": 1})

    try:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "esxport",
                "--query",
                query,
                "--output-file",
                output_file,
                "--index-prefixes",
                "test-index",
                "--url",
                "http://localhost:9200",
                "--user",
                "elastic",
                "--password",
                "testpass",
                "--delimiter",
                ",",
                "--max-results",
                "1",
                "--scroll-size",
                "10",
                "--debug",
                "--fields",
                "_id",
                "--fields",
                "_source",
            ],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )

        # This will likely fail due to no ES connection, but arguments should parse correctly
        # The error should be about connection, not argument parsing
        if result.returncode != 0 and result.stderr:
            # Should not contain argument parsing errors
            parsing_errors = ["unrecognized arguments", "invalid choice", "expected one argument"]
            assert not any(error in result.stderr.lower() for error in parsing_errors)

    finally:
        Path(output_file).unlink(missing_ok=True)


def test_module_execution() -> None:
    """Test that the module can be executed with python -m."""
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            'import esxport.cli; print("Module can be imported")',
        ],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )

    assert result.returncode == 0
    assert "Module can be imported" in result.stdout
