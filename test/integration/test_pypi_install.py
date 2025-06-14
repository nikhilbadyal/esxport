"""Test PyPI installation functionality."""
import subprocess
import sys


def test_pypi_package_import() -> None:
    """Test that PyPI installed package can be imported."""
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            'import esxport; print(f"Version: {esxport.__version__}")',
        ],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )

    assert result.returncode == 0
    assert "Version:" in result.stdout
    assert len(result.stdout.strip()) > 8  # Should have actual version


def test_pypi_cli_functionality() -> None:
    """Test that PyPI installed CLI works."""
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "esxport",
            "--version",
        ],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )

    assert result.returncode == 0
    assert any(char.isdigit() for char in result.stdout)


def test_pypi_package_completeness() -> None:
    """Test that all expected modules are available in PyPI package."""
    modules_to_test = [
        "esxport",
        "esxport.cli",
        "esxport.esxport",
        "esxport.constant",
        "esxport.strings",
        "esxport.click_opt.click_custom",
    ]

    for module in modules_to_test:
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                f'import {module}; print("OK")',
            ],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )

        assert result.returncode == 0, f"Failed to import {module}: {result.stderr}"
        assert "OK" in result.stdout
