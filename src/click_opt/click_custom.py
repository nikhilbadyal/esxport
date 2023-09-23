"""Custom CLick types."""
from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from click import Context, Parameter, ParamType
from click_params.miscellaneous import JsonParamType

from src.strings import invalid_query_format, invalid_sort_format

if TYPE_CHECKING:
    from typing_extensions import Self


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


class Json(JsonParamType):  # type: ignore[misc]
    """Json Validator."""

    name = "json"

    def convert(self: Self, value: Any, param: Parameter, ctx: Context) -> dict[str, Any]:  # type: ignore[return]
        """Convert input to json."""
        try:
            return json.loads(  # type: ignore[no-any-return]
                value,
                cls=self._cls,
                object_hook=self._object_hook,
                parse_float=self._parse_float,
                parse_int=self._parse_int,
                parse_constant=self._parse_constant,
                object_pairs_hook=self._object_pairs_hook,
                **self._kwargs,
            )
        except json.JSONDecodeError as exc:
            self.fail(invalid_query_format.format(value=value, exc=exc), param, ctx)


JSON = Json()
