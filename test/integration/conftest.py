"""Configuration for integration tests."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture()
def temp_output_file(tmp_path: Path) -> Path:
    """Provide a temporary output file path."""
    return tmp_path / "test_output.csv"


@pytest.fixture()
def minimal_query() -> dict[str, dict[str, dict[Any, Any]] | int]:
    """Provide a minimal test query."""
    return {"query": {"match_all": {}}, "size": 1}
