"""Test that all imports work correctly in the installed package."""
import importlib
import sys
from pathlib import Path

import pytest


def test_main_package_import() -> None:
    """Test that main package can be imported."""
    import esxport

    assert hasattr(esxport, "__version__")
    assert esxport.__version__ is not None


def test_version_import() -> None:
    """Test version import from package."""
    from esxport import __version__

    assert __version__ is not None
    assert isinstance(__version__, str)
    assert len(__version__.split(".")) >= 2  # At least major.minor


def test_core_classes_import() -> None:
    """Test that core classes can be imported."""
    from esxport import CliOptions, EsXport

    # Verify classes exist and are callable
    assert callable(EsXport)
    assert callable(CliOptions)


def test_cli_module_import() -> None:
    """Test CLI module imports."""
    from esxport import cli

    assert hasattr(cli, "cli")
    assert callable(cli.cli)


def test_all_submodules_importable() -> None:
    """Test that all expected submodules can be imported."""
    expected_modules = [
        "esxport.cli",
        "esxport.esxport",
        "esxport.constant",
        "esxport.strings",
        "esxport.click_opt",
        "esxport.click_opt.click_custom",
    ]

    failed_imports = []

    for module_name in expected_modules:
        try:
            importlib.import_module(module_name)
        except ImportError as e:
            failed_imports.append((module_name, str(e)))

    if failed_imports:
        error_msg = "Failed to import modules:\n"
        for module, error in failed_imports:
            error_msg += f"  - {module}: {error}\n"
        pytest.fail(error_msg)


def test_no_dev_dependencies_imported() -> None:
    """Ensure no development dependencies are accidentally imported."""
    dev_modules = ["black", "mypy", "ruff", "coverage"]  # pytest is expected in test environment

    # Get all currently imported modules
    imported_modules = set(sys.modules.keys())

    # Check for dev dependencies that shouldn't be imported
    accidentally_imported = []
    for dev_mod in dev_modules:
        if dev_mod in imported_modules:
            accidentally_imported.append(dev_mod)

    if accidentally_imported:
        pytest.fail(f"Development dependencies accidentally imported: {accidentally_imported}")


def test_package_installation_location() -> None:
    """Verify package is installed in expected location."""
    import esxport

    package_path = Path(esxport.__file__).parent

    # Should be in site-packages when testing installed package
    assert "site-packages" in str(package_path)  # Should be in site-packages

    # Verify required files exist
    required_files = ["__init__.py", "cli.py", "esxport.py"]
    for file_name in required_files:
        file_path = package_path / file_name
        assert file_path.exists(), f"Required file {file_name} not found in package"


def test_entry_points_available() -> None:
    """Test that CLI entry points are available."""
    import esxport.cli

    # The CLI function should be available
    assert hasattr(esxport.cli, "cli")

    # Test that the CLI function has expected attributes
    cli_func = esxport.cli.cli
    assert hasattr(cli_func, "params")  # Click command parameters
    assert hasattr(cli_func, "callback")  # Click command callback
