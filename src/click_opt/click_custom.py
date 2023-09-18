"""Custom CLick types."""
import json
from typing import Any

from click import Context, Parameter, ParamType
from click_params.miscellaneous import JsonParamType


class FormatError(ValueError):
    """Invalid input format."""


class Sort(ParamType):
    """Sort type ES."""

    name = "Elastic Sort"
    _possible_sorts = ["asc", "desc"]

    def _check_sort_type(self: "Sort", sort_order: str) -> None:
        """Check if sort type is correct."""
        if sort_order not in self._possible_sorts:
            msg = f"Invalid sort type {sort_order}."
            raise FormatError(msg)

    def convert(self: "Sort", value: Any, param: Parameter | None, ctx: Context | None) -> Any:
        """Convert str to dict."""
        try:
            field, sort_order = value.split(":")
            self._check_sort_type(sort_order)
        except FormatError as e:
            self.fail(str(e), param, ctx)
        except ValueError:
            self.fail(f'Invalid input format: "{value}". Use the format "field:sort_order".', param, ctx)
        else:
            return {field: sort_order}

    def __repr__(self: "Sort") -> str:
        """Return a string representation."""
        return str(self.name)


sort = Sort()


class Json(JsonParamType):  # type: ignore[misc]
    """Json Validator."""

    name = "json"

    def convert(self: "Json", value: Any, param: Parameter, ctx: Context) -> dict[str, Any]:  # type: ignore[return]
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
            self.fail(f"{value} is not a valid json string, caused {exc}", param, ctx)

    def __repr__(self: "Json") -> str:
        """String representation of the object."""
        return self.name.upper()


JSON = Json()
