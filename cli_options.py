"""CLII options."""
import json
from pathlib import Path
from typing import Any, Self

# noinspection PyPackageRequirements
import urllib3
from elastic_transport import SecurityWarning

urllib3.disable_warnings()
urllib3.disable_warnings(SecurityWarning)


class CliOptions(object):
    """CLI options."""

    def __init__(
        self: Self,
        myclass_kwargs: dict[str, Any],
    ) -> None:
        self.query: dict[str, Any] = myclass_kwargs["query"]
        self.output_file: Path = Path(myclass_kwargs["output_file"])
        self.url = myclass_kwargs["url"]
        self.user = myclass_kwargs["user"]
        self.password = myclass_kwargs["password"]
        self.index_prefixes = myclass_kwargs["index_prefixes"]
        self.fields = myclass_kwargs["fields"]
        self.sort = myclass_kwargs["sort"]
        self.delimiter = myclass_kwargs["delimiter"]
        self.max_results = int(myclass_kwargs["max_results"])
        self.scroll_size = int(myclass_kwargs["scroll_size"])
        self.meta_fields: list[str] = list(myclass_kwargs["meta_fields"])
        self.verify_certs: bool = myclass_kwargs["verify_certs"]
        self.ca_certs = myclass_kwargs["ca_certs"]
        self.client_cert = myclass_kwargs["ca_certs"]
        self.client_key = myclass_kwargs["ca_certs"]
        self.debug: bool = myclass_kwargs["debug"]

    def __str__(self: Self) -> str:
        """Print the class."""
        return json.dumps(self.__dict__, indent=4, default=str)
