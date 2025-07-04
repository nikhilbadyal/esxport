"""Test module API functionality of installed package."""

import tempfile
from pathlib import Path

import esxport
from esxport import CliOptions, EsXport, __version__
from esxport.click_opt.click_custom import JSON, sort
from esxport.constant import META_FIELDS, default_config_fields
from esxport.strings import cli_version


def test_cli_options_class() -> None:
    """Test CliOptions class functionality."""
    kwargs = {
        "query": {"query": {"match_all": {}}},
        "output_file": "test.csv",
        "index_prefixes": ["test-index"],
        "url": "https://localhost:9200",
        "user": "elastic",
        "password": "password",
        "debug": True,
    }

    options = CliOptions(kwargs)

    # Test that options are set correctly
    assert options.query == kwargs["query"]
    assert options.output_file == kwargs["output_file"]
    assert options.index_prefixes == kwargs["index_prefixes"]
    assert options.url == kwargs["url"]
    assert options.user == kwargs["user"]
    assert options.password == kwargs["password"]
    assert options.debug == kwargs["debug"]


def test_esxport_class_instantiation() -> None:
    """Test EsXport class can be instantiated."""
    kwargs = {
        "query": {"query": {"match_all": {}}},
        "output_file": "test.csv",
        "index_prefixes": ["test-index"],
        "password": "password",
        "verify_certs": False,  # Avoid SSL certificate issues in integration tests
    }

    options = CliOptions(kwargs)
    esxport = EsXport(options)

    # Verify object is created
    assert esxport is not None
    assert hasattr(esxport, "export")
    assert callable(esxport.export)


def test_cli_options_defaults() -> None:
    """Test that CliOptions applies defaults correctly."""
    minimal_kwargs = {
        "query": {"query": {"match_all": {}}},
        "output_file": "test.csv",
        "index_prefixes": ["test-index"],
        "password": "password",
    }

    options = CliOptions(minimal_kwargs)

    # Test that defaults are applied
    assert options.url == "https://localhost:9200"  # Default URL
    assert options.user == "elastic"  # Default user
    assert options.delimiter == ","  # Default delimiter
    assert options.max_results == 10  # Default max results
    assert options.debug is False  # Default debug


def test_module_constants_available() -> None:
    """Test that module constants are available."""
    # Test META_FIELDS is available and populated
    assert META_FIELDS is not None
    assert isinstance(META_FIELDS, (list, tuple))
    assert len(META_FIELDS) > 0

    # Test default_config_fields is available
    assert default_config_fields is not None
    assert isinstance(default_config_fields, dict)
    assert "url" in default_config_fields
    assert "user" in default_config_fields


def test_cli_custom_imports() -> None:
    """Test that custom CLI components can be imported."""
    # Test that custom click types are available
    assert JSON is not None
    assert sort is not None


def test_module_with_file_operations() -> None:
    """Test module API with actual file operations."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        output_file = f.name

    try:
        kwargs = {
            "query": {"query": {"match_all": {}}, "size": 1},
            "output_file": output_file,
            "index_prefixes": ["test-index"],
            "url": "https://nonexistent:9200",  # Will fail to connect
            "password": "password",
            "max_results": 1,
            "debug": True,
            "verify_certs": False,  # Avoid SSL certificate issues in integration tests
        }

        options = CliOptions(kwargs)
        esxport = EsXport(options)

        # This will fail due to no ES connection, but should not fail due to API issues
        try:
            esxport.export()
        except Exception as e:
            # Should be connection-related error, not API error
            error_msg = str(e).lower()
            api_errors = ["attribute", "import", "module", "not found"]
            assert not any(api_error in error_msg for api_error in api_errors)

    finally:
        Path(output_file).unlink(missing_ok=True)


def test_version_consistency() -> None:
    """Test that version is consistent across imports."""
    # Version should be consistent
    assert __version__ == esxport.__version__

    # Version should be a valid string
    assert isinstance(__version__, str)
    assert "." in __version__  # Should have at least one dot

    # Should be able to split into parts
    version_parts = __version__.split(".")
    assert len(version_parts) >= 2  # At least major.minor
    assert all(
        part.isdigit() or part.replace("rc", "").replace("a", "").replace("b", "").isdigit() for part in version_parts
    )  # Should be numeric or pre-release


def test_strings_module() -> None:
    """Test that strings module is available and functional."""
    # Test that cli_version template is available
    assert cli_version is not None
    assert isinstance(cli_version, str)
    assert "{__version__}" in cli_version

    # Test that it can be formatted
    formatted = cli_version.format(__version__=__version__)
    assert __version__ in formatted
    assert "EsXport" in formatted or "esxport" in formatted
