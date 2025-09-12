"""Client to interact with Elasticsearch."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from urllib.parse import urlparse

import elasticsearch
from elasticsearch import Elasticsearch
from typing_extensions import Self

from .constant import CONNECTION_TIMEOUT
from .exceptions import ScrollExpiredError

if TYPE_CHECKING:
    from .click_opt.cli_options import CliOptions


class ElasticsearchClient:
    """Elasticsearch client."""

    def __init__(
        self: Self,
        cli_options: CliOptions,
    ) -> None:
        # Parse URL to determine scheme (more robust than string checking)
        parsed_url = urlparse(cli_options.url)
        is_https = parsed_url.scheme.lower() == "https"

        # Common connection parameters
        hosts = [cli_options.url]  # Wrap in list for Elasticsearch client consistency
        timeout = CONNECTION_TIMEOUT
        auth = (cli_options.user, cli_options.password)

        # Conditionally pass TLS options for HTTPS connections only
        if is_https:
            client = elasticsearch.Elasticsearch(
                hosts=hosts,
                request_timeout=timeout,
                basic_auth=auth,
                verify_certs=cli_options.verify_certs,
                ca_certs=cli_options.ca_certs,
                client_cert=cli_options.client_cert,
                client_key=cli_options.client_key,
            )
        else:
            client = elasticsearch.Elasticsearch(
                hosts=hosts,
                request_timeout=timeout,
                basic_auth=auth,
            )

        self.client: Elasticsearch = client

    def indices_exists(self: Self, index: str | list[str] | tuple[str, ...]) -> bool:
        """Check if a given index exists."""
        return bool(self.client.indices.exists(index=index))

    def get_mapping(self: Self, index: str) -> dict[str, Any]:
        """Get the mapping for a given index."""
        return self.client.indices.get_mapping(index=index).raw

    def search(self: Self, **kwargs: Any) -> Any:
        """Search in the index."""
        return self.client.search(**kwargs)

    def scroll(self: Self, scroll: str, scroll_id: str) -> Any:
        """Paginated the search results."""
        try:
            return self.client.scroll(scroll=scroll, scroll_id=scroll_id)
        except (elasticsearch.NotFoundError, elasticsearch.AuthorizationException) as e:
            msg = f"Scroll {scroll_id} expired or {e}."
            raise ScrollExpiredError(msg) from e

    def clear_scroll(self: Self, scroll_id: str) -> Any:
        """Remove all scrolls."""
        return self.client.clear_scroll(scroll_id=scroll_id)

    def ping(self: Self) -> Any:
        """Ping the Elasticsearch cluster and retrieve detailed information.

        Returns
        -------
            dict: Cluster information if reachable, otherwise an error message.
        """
        return self.client.info()
