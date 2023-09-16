"""Custom CLick types."""
from typing import Any, Self

from click import Context, Parameter, ParamType


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
            self.fail(f'Invalid input format: "{value}". Use the format "field:sort_order".', param, ctx)
        else:
            return {field: sort_order}

    def __repr__(self: Self) -> str:
        """Return a string representation."""
        return str(self.name)


sort = Sort()
