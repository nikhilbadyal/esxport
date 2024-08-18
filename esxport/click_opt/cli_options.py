"""CLII options."""
from __future__ import annotations

import json
from typing import Any

# noinspection PyPackageRequirements
import urllib3
from elastic_transport import SecurityWarning
from typing_extensions import Self

from esxport.constant import default_config_fields

urllib3.disable_warnings()
urllib3.disable_warnings(SecurityWarning)


class CliOptions(object):
    """CLI options."""

    # Explicitly declare all attributes with their types
    query: dict[str, Any]
    output_file: str
    url: str
    user: str
    password: str
    index_prefixes: list[str]
    fields: list[str]
    sort: list[dict[str, str]]
    delimiter: str
    max_results: int
    scroll_size: int
    meta_fields: list[str]
    verify_certs: bool
    ca_certs: str
    client_cert: str
    client_key: str
    debug: bool
    export_format: str

    def __init__(self: Self, myclass_kwargs: dict[str, Any]) -> None:
        # All keys that you want to set as attributes
        attrs_to_set = {
            "query",
            "output_file",
            "url",
            "user",
            "password",
            "index_prefixes",
            "fields",
            "sort",
            "delimiter",
            "max_results",
            "scroll_size",
            "meta_fields",
            "verify_certs",
            "ca_certs",
            "client_cert",
            "client_key",
            "debug",
        }

        for attr in attrs_to_set:
            setattr(self, attr, myclass_kwargs.get(attr, default_config_fields.get(attr)))

        # Additional processing for certain attributes
        self.fields: list[str] = list(self.fields)
        self.index_prefixes: list[str] = list(self.index_prefixes)
        self.meta_fields: list[str] = list(self.meta_fields)
        self.sort: list[dict[str, str]] = self.sort
        self.max_results = int(self.max_results)
        self.scroll_size = int(self.scroll_size)
        self.export_format: str = "csv"

    def __str__(self: Self) -> str:
        """Print the class."""
        return json.dumps(self.__dict__, indent=4, default=str)
