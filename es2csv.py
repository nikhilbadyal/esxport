#!/usr/bin/python
"""Main export module."""
import contextlib
import csv
import json
import sys
import time
from collections.abc import Callable
from functools import wraps
from pathlib import Path
from typing import Any, Self, TypeVar

import elasticsearch
from loguru import logger
from tqdm import tqdm

import cli_options

FLUSH_BUFFER = 1000  # Chunk of docs to flush in temp file
CONNECTION_TIMEOUT = 120
TIMES_TO_TRY = 3
RETRY_DELAY = 60
META_FIELDS = ["_id", "_index", "_score"]

F = TypeVar("F", bound=Callable[..., Any])


# Retry decorator for functions with exceptions
def retry(
    exception_to_check: type[BaseException],
    tries: int = TIMES_TO_TRY,
    delay: int = RETRY_DELAY,
) -> Callable[[F], F]:
    """Retryn connection."""

    def deco_retry(f: Any) -> Any:
        @wraps(f)
        def f_retry(*args: Any, **kwargs: dict[Any, Any]) -> Any:
            mtries = tries
            while mtries > 0:
                try:
                    return f(*args, **kwargs)
                except exception_to_check as e:
                    logger.error(e)
                    logger.info(f"Retrying in {delay} seconds ...")
                    time.sleep(delay)
                    mtries -= 1
            try:
                return f(*args, **kwargs)
            except exception_to_check as e:
                logger.exception(f"Fatal Error: {e}")
                sys.exit(1)

        return f_retry

    return deco_retry


class Es2csv:
    """Main class."""

    def __init__(self: Self, opts: cli_options.CliOptions) -> None:
        self.opts = opts

        self.num_results = 0
        self.scroll_ids: list[str] = []
        self.scroll_time = "30m"

        self.csv_headers = list(META_FIELDS) if self.opts.meta_fields else []
        self.tmp_file = f"{opts.output_file}.tmp"
        self.rows_written = 0

    @retry(elasticsearch.exceptions.ConnectionError, tries=TIMES_TO_TRY)
    def create_connection(self: Self) -> None:
        """Create a connection to Elasticsearch."""
        es = elasticsearch.Elasticsearch(
            self.opts.url,
            timeout=CONNECTION_TIMEOUT,
            basic_auth=(self.opts.user, self.opts.password),
            verify_certs=self.opts.verify_certs,
            ca_certs=self.opts.ca_certs,
            client_cert=self.opts.client_cert,
            client_key=self.opts.client_key,
        )
        es.cluster.health()
        # noinspection PyAttributeOutsideInit
        self.es_conn = es

    @retry(elasticsearch.exceptions.ConnectionError, tries=TIMES_TO_TRY)
    def check_indexes(self: Self) -> None:
        """Check if indexes are valid."""
        indexes = self.opts.index_prefixes
        if "_all" in indexes:
            indexes = ["_all"]
        else:
            indexes_status = self.es_conn.indices.exists(index=indexes)
            if not indexes_status:
                logger.error(
                    f'Any of index(es) {", ".join(self.opts.index_prefixes)} does not exist in {self.opts.url}.',
                )
                sys.exit(1)
        self.opts.index_prefixes = indexes

    def _validate_fields(self: Self) -> None:
        """Validate fields."""
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
            response: dict[str, Any] = self.es_conn.indices.get_mapping(index=index)
            all_fields_dict[index] = []
            for field in response[index]["mappings"]["properties"]:
                all_fields_dict[index].append(field)
        all_es_fields = {value for values_list in all_fields_dict.values() for value in values_list}

        for element in all_expected_fields:
            if element not in all_es_fields:
                logger.error(f"Fields {element} doesn't exist in any index.")
                sys.exit(1)

    def prepare_search_query(self: Self) -> dict[str, Any]:
        """Prepare search query."""
        search_args = {
            "index": ",".join(self.opts.index_prefixes),
            "scroll": self.scroll_time,
            "size": self.opts.scroll_size,
            "terminate_after": self.opts.max_results,
            "body": self.opts.query,
        }
        if self.opts.sort:
            search_args["sort"] = self.opts.sort

        if "_all" not in self.opts.fields:
            search_args["_source_includes"] = ",".join(self.opts.fields)
            self.csv_headers.extend([field for field in self.opts.fields if "*" not in field])

        if self.opts.debug:
            logger.debug("Using these indices: {}.".format(", ".join(self.opts.index_prefixes)))
            logger.debug(f"Query {self.opts.query}")
            logger.debug("Output field(s): {}.".format(", ".join(self.opts.fields)))
            logger.debug(f"Sorting by: {self.opts.sort}.")
        return search_args

    @retry(elasticsearch.exceptions.ConnectionError, tries=TIMES_TO_TRY)
    def next_scroll(self: Self, scroll_id: str) -> Any:
        """Scroll to the next page."""
        return self.es_conn.scroll(scroll=self.scroll_time, scroll_id=scroll_id)

    def write_to_temp_file(self: Self, res: Any) -> None:
        """Write data to temp file."""
        hit_list = []
        total_size = int(min(self.opts.max_results, self.num_results))
        bar = tqdm(
            desc=self.tmp_file,
            total=total_size,
            unit="docs",
            colour="green",
        )

        while self.rows_written != total_size:
            if res["_scroll_id"] not in self.scroll_ids:
                self.scroll_ids.append(res["_scroll_id"])

            if not res["hits"]["hits"]:
                logger.info("Scroll[{}] expired(multiple reads?). Saving loaded data.".format(res["_scroll_id"]))
                break
            for hit in res["hits"]["hits"]:
                self.rows_written += 1
                bar.update(1)
                hit_list.append(hit)
                if len(hit_list) == FLUSH_BUFFER:
                    self.flush_to_file(hit_list)
                    hit_list = []
            res = self.next_scroll(res["_scroll_id"])
        bar.close()
        self.flush_to_file(hit_list)

    @retry(elasticsearch.exceptions.ConnectionError, tries=TIMES_TO_TRY)
    def search_query(self: Self) -> Any:
        """Prepare search query string."""
        self._validate_fields()
        search_args = self.prepare_search_query()
        res = self.es_conn.search(**search_args)
        self.num_results = res["hits"]["total"]["value"]

        logger.info(f"Found {self.num_results} results.")

        if self.num_results > 0:
            self.write_to_temp_file(res)

    def flush_to_file(self: Self, hit_list: list[dict[str, Any]]) -> None:
        """Write data to file."""

        def add_meta_fields() -> None:
            if self.opts.meta_fields:
                for fields in self.opts.meta_fields:
                    data[fields] = hit.get(fields, None)

        with Path(self.tmp_file).open(mode="a", encoding="utf-8") as tmp_file:
            for hit in hit_list:
                data = hit["_source"]
                data.pop("_meta", None)
                add_meta_fields()
                tmp_file.write(json.dumps(data))
                tmp_file.write("\n")

    def write_to_csv(self: Self) -> None:
        """Write to csv file."""
        if self.rows_written > 0:
            with Path(self.tmp_file).open() as f:
                first_line = json.loads(f.readline().strip("\n"))
                self.csv_headers = first_line.keys()
            with Path(self.opts.output_file).open(mode="a", encoding="utf-8") as output_file:
                csv_writer = csv.DictWriter(output_file, fieldnames=self.csv_headers, delimiter=self.opts.delimiter)
                csv_writer.writeheader()
                bar = tqdm(
                    desc=self.opts.output_file,
                    total=self.rows_written,
                    unit="docs",
                    colour="green",
                )
                with Path(self.tmp_file).open(encoding="utf-8") as file:
                    for _timer, line in enumerate(file, start=1):
                        bar.update(1)
                        csv_writer.writerow(json.loads(line))

                bar.close()
        else:
            logger.info(
                f'There is no docs with selected field(s): {",".join(self.opts.fields)}.',
            )
        Path(self.tmp_file).unlink()

    def clean_scroll_ids(self: Self) -> None:
        """Clean up scroll."""
        with contextlib.suppress(Exception):
            self.es_conn.clear_scroll(body=",".join(self.scroll_ids))
