"""CLII options."""
from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

# noinspection PyPackageRequirements
import urllib3
from elastic_transport import SecurityWarning

from esxport.constant import default_config_fields

if TYPE_CHECKING:
    from typing_extensions import Self

urllib3.disable_warnings()
urllib3.disable_warnings(SecurityWarning)


class CliOptions(object):
    """CLI options."""

    def __init__(
        self: Self,
        myclass_kwargs: dict[str, Any],
    ) -> None:
        self.query: dict[str, Any] = myclass_kwargs["query"]
        self.output_file = myclass_kwargs["output_file"]
        self.url = myclass_kwargs.get("url", default_config_fields["url"])
        self.user = myclass_kwargs.get("user", default_config_fields["user"])
        self.password = myclass_kwargs["password"]
        self.index_prefixes = myclass_kwargs.get("index_prefixes", default_config_fields["index_prefixes"])
        self.fields: list[str] = list(myclass_kwargs.get("fields", default_config_fields["fields"]))
        self.sort: list[dict[str, str]] = myclass_kwargs.get("sort", default_config_fields["sort"])
        self.delimiter = myclass_kwargs.get("delimiter", default_config_fields["delimiter"])
        self.max_results = int(myclass_kwargs.get("max_results", default_config_fields["max_results"]))
        self.scroll_size = int(myclass_kwargs.get("scroll_size", default_config_fields["scroll_size"]))
        self.meta_fields: list[str] = list(myclass_kwargs.get("meta_fields", default_config_fields["meta_fields"]))
        self.verify_certs: bool = myclass_kwargs.get("verify_certs", default_config_fields["verify_certs"])
        self.ca_certs = myclass_kwargs.get("ca_certs", default_config_fields["ca_certs"])
        self.client_cert = myclass_kwargs.get("ca_certs", default_config_fields["client_cert"])
        self.client_key = myclass_kwargs.get("ca_certs", default_config_fields["client_key"])
        self.debug: bool = myclass_kwargs.get("debug", default_config_fields["debug"])
        self.format: str = "csv"

    def __str__(self: Self) -> str:
        """Print the class."""
        return json.dumps(self.__dict__, indent=4, default=str)
