"""Main export module."""
from __future__ import annotations

import contextlib
import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

from elasticsearch.exceptions import ConnectionError
from loguru import logger
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential
from tqdm import tqdm
from typing_extensions import Self

from .click_opt.click_custom import Json
from .constant import FLUSH_BUFFER, TIMES_TO_TRY
from .elastic import ElasticsearchClient
from .exceptions import (
    FieldNotFoundError,
    HealthCheckError,
    IndexNotFoundError,
    InvalidEsQueryError,
    MetaFieldNotFoundError,
    NoDataFoundError,
    ScrollExpiredError,
)
from .strings import (
    index_not_found,
    meta_field_not_found,
    output_fields,
    query_key_missing,
    sorting_by,
    using_indexes,
    using_query,
)
from .writer import Writer

if TYPE_CHECKING:
    from .click_opt.cli_options import CliOptions


class EsXport(object):
    """Main class."""

    def __init__(self: Self, opts: CliOptions, es_client: ElasticsearchClient | None = None) -> None:
        self.search_args: dict[str, Any] = {}
        self.opts = opts
        self.num_results = 0
        self.scroll_ids: list[str] = []
        self.scroll_time = "30m"
        self.rows_written = 0

        self.es_client = es_client or self._create_default_client(opts)

    def _create_default_client(self: Self, opts: CliOptions) -> ElasticsearchClient:
        return ElasticsearchClient(opts)

    @retry(
        wait=wait_exponential(2),
        stop=stop_after_attempt(TIMES_TO_TRY),
        reraise=True,
        retry=retry_if_exception_type(ConnectionError),
    )
    def _check_indexes(self: Self) -> None:
        """Check if input indexes exist."""
        indexes = self.opts.index_prefixes
        if "_all" in indexes:
            indexes = ["_all"]
        else:
            indexes_status = self.es_client.indices_exists(index=indexes)
            if not indexes_status:
                msg = index_not_found.format(", ".join(self.opts.index_prefixes), self.opts.url)
                raise IndexNotFoundError(
                    msg,
                )
        self.opts.index_prefixes = indexes

    def _ping_cluster(self: Self) -> None:
        """Check if cluster is live."""
        try:
            _ = self.es_client.ping()
        except Exception as e:  # noqa: BLE001
            msg = f"Unable to connect with cluster {e}."
            raise HealthCheckError(msg) from e

    def _validate_fields(self: Self) -> None:
        all_fields_dict: dict[str, list[str]] = {}
        indices_names = list(self.opts.index_prefixes)
        all_expected_fields = self.opts.fields.copy()
        for sort_query in self.opts.sort:
            sort_key = next(iter(sort_query.keys()))
            parts = sort_key.split(".")
            sort_param = parts[0] if len(parts) > 0 else sort_key
            all_expected_fields.append(sort_param)
        if "_all" in all_expected_fields:
            all_expected_fields.remove("_all")

        for index in indices_names:
            response: dict[str, Any] = self.es_client.get_mapping(index=index)
            all_fields_dict[index] = []
            for field in response[index]["mappings"]["properties"]:
                all_fields_dict[index].append(field)
        all_es_fields = {value for values_list in all_fields_dict.values() for value in values_list}

        for element in all_expected_fields:
            if element not in all_es_fields:
                msg = f"Fields {element} doesn't exist in any index."
                raise FieldNotFoundError(msg)

    def _prepare_search_query(self: Self) -> None:
        """Prepares search query from input."""
        try:
            self.search_args = {
                "index": ",".join(self.opts.index_prefixes),
                "scroll": self.scroll_time,
                "size": self.opts.scroll_size,
                "terminate_after": self.opts.max_results,
                "query": Json().convert(self.opts.query, None, None)["query"],
            }
            if self.opts.sort:
                self.search_args["sort"] = self.opts.sort

            if "_all" not in self.opts.fields:
                self.search_args["_source_includes"] = ",".join(self.opts.fields)

            if self.opts.debug:
                logger.debug(using_indexes.format(indexes={", ".join(self.opts.index_prefixes)}))
                query = json.dumps(self.opts.query, default=str)
                logger.debug(using_query.format(query={query}))
                logger.debug(output_fields.format(fields={", ".join(self.opts.fields)}))
                logger.debug(sorting_by.format(sort=self.opts.sort))
        except KeyError as e:
            raise InvalidEsQueryError(query_key_missing) from e

    @retry(
        wait=wait_exponential(2),
        stop=stop_after_attempt(TIMES_TO_TRY),
        reraise=True,
        retry=retry_if_exception_type(ConnectionError),
    )
    def next_scroll(self: Self, scroll_id: str) -> Any:
        """Paginate to the next page."""
        return self.es_client.scroll(scroll=self.scroll_time, scroll_id=scroll_id)

    def _write_to_temp_file(self: Self, res: Any) -> None:
        """Write to temp file."""
        hit_list: list[dict[str, Any]] = []
        total_size = int(min(self.opts.max_results, self.num_results))
        bar = tqdm(
            desc=f"{self.opts.output_file}.tmp",
            total=total_size,
            unit="docs",
            colour="green",
        )
        try:
            while self.rows_written != total_size:
                if res["_scroll_id"] not in self.scroll_ids:
                    self.scroll_ids.append(res["_scroll_id"])

                for hit in res["hits"]["hits"]:
                    self.rows_written += 1
                    bar.update(1)
                    hit_list.append(hit)
                    if len(hit_list) == FLUSH_BUFFER:
                        self._flush_to_file(hit_list)
                        hit_list = []
                res = self.next_scroll(res["_scroll_id"])
        except ScrollExpiredError:
            logger.error("Scroll expired(multiple reads?). Saving loaded data.")
        finally:
            bar.close()
            self._flush_to_file(hit_list)

    @retry(
        wait=wait_exponential(2),
        stop=stop_after_attempt(TIMES_TO_TRY),
        reraise=True,
        retry=retry_if_exception_type(ConnectionError),
    )
    def search_query(self: Self) -> Any:
        """Search the index."""
        self._validate_fields()
        self._prepare_search_query()
        res = self.es_client.search(**self.search_args)
        self.num_results = res["hits"]["total"]["value"]

        logger.info(f"Found {self.num_results} results.")

        if self.num_results == 0:
            msg = "No Data found in index."
            raise NoDataFoundError(msg)
        self._write_to_temp_file(res)

    def _flush_to_file(self: Self, hit_list: list[dict[str, Any]]) -> None:
        """Flush the search results to a temporary file."""

        def add_meta_fields() -> None:
            if self.opts.meta_fields:
                for field in self.opts.meta_fields:
                    try:
                        data[field] = hit[field]
                    except KeyError as e:  # noqa: PERF203
                        raise MetaFieldNotFoundError(meta_field_not_found.format(field=field)) from e

        with Path(f"{self.opts.output_file}.tmp").open(mode="a", encoding="utf-8") as tmp_file:
            for hit in hit_list:
                data = hit["_source"]
                data.pop("_meta", None)
                add_meta_fields()
                tmp_file.write(json.dumps(data))
                tmp_file.write("\n")

    def _clean_scroll_ids(self: Self) -> None:
        """Clear all scroll ids."""
        with contextlib.suppress(Exception):
            self.es_client.clear_scroll(scroll_id="_all")

    def _extract_headers(self: Self) -> list[str]:
        """Extract CSV headers from the first line of the file."""
        file_name = f"{self.opts.output_file}.tmp"
        with Path(file_name).open() as f:
            first_line = json.loads(f.readline())
            return list(first_line.keys())

    def _export(self: Self) -> None:
        """Export the data."""
        headers = self._extract_headers()
        kwargs = {
            "delimiter": self.opts.delimiter,
            "output_format": self.opts.export_format,
        }
        Writer.write(
            headers=headers,
            total_records=self.rows_written,
            out_file=self.opts.output_file,
            **kwargs,
        )

    def export(self: Self) -> None:
        """Export the data."""
        self._ping_cluster()
        self._check_indexes()
        self.search_query()
        self._clean_scroll_ids()
        self._export()


#
