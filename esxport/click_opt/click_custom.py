"""Custom CLick types."""
from __future__ import annotations

import json
from typing import Any

from click import Context, Parameter, ParamType
from typing_extensions import Self

from esxport.strings import invalid_query_format, invalid_sort_format


class FormatError(ValueError):
    """Invalid input format."""


class Sort(ParamType):
    """Sort type ES."""

    name = "Elastic Sort"
    _possible_sorts = ["asc", "desc"]

    def _check_sort_type(self: Self, sort_order: str) -> None:
        """Check if sort type is correct."""
        if sort_order not in self._possible_sorts:
            msg = f"Invalid sort type {sort_order}."
            raise FormatError(msg)

    def convert(self: Self, value: Any, param: Parameter | None, ctx: Context | None) -> Any:
        """Convert str to dict."""
        try:
            field, sort_order = value.split(":")
            self._check_sort_type(sort_order)
        except FormatError as e:
            self.fail(str(e), param, ctx)
        except ValueError:
            self.fail(invalid_sort_format.format(value=value), param, ctx)
        else:
            return {field: sort_order}


sort = Sort()


class Json(ParamType):
    """Json Validator."""

    name = "json"

    def convert(self: Self, value: Any, param: Parameter | None, ctx: Context | None) -> dict[str, Any]:
        """Convert input to json."""
        try:
            return value if isinstance(value, dict) else json.loads(value)  # type: ignore[no-any-return]
        except json.JSONDecodeError as exc:
            self.fail(invalid_query_format.format(value=value, exc=exc), param, ctx)


JSON = Json()
