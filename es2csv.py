"""Main export module."""
import codecs
import contextlib
import csv
import json
import sys
import time
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Self, TypeVar

import elasticsearch
import progressbar

FLUSH_BUFFER = 1000  # Chunk of docs to flush in temp file
CONNECTION_TIMEOUT = 120
TIMES_TO_TRY = 3
RETRY_DELAY = 60
META_FIELDS = ["_id", "_index", "_score", "_type"]

F = TypeVar("F", bound=Callable[..., Any])


# Retry decorator for functions with exceptions
def retry(ExceptionToCheck: Any, tries: int = TIMES_TO_TRY, delay: int = RETRY_DELAY) -> Callable[[F], F]:
    """Retryn connection."""

    def deco_retry(f: Any) -> Any:
        @wraps(f)
        def f_retry(*args: Any, **kwargs: Dict[Any, Any]) -> Any:
            mtries = tries
            while mtries > 0:
                try:
                    return f(*args, **kwargs)
                except ExceptionToCheck as e:
                    print(e)
                    print(f"Retrying in {delay} seconds ...")
                    time.sleep(delay)
                    mtries -= 1
            try:
                return f(*args, **kwargs)
            except ExceptionToCheck as e:
                print(f"Fatal Error: {e}")
                sys.exit(1)

        return f_retry

    return deco_retry


class Es2csv:
    """Main class."""

    def __init__(self: Self, opts: Any) -> None:
        self.opts = opts

        self.num_results = 0
        self.scroll_ids: List[str] = []
        self.scroll_time = "30m"

        self.csv_headers = list(META_FIELDS) if self.opts.meta_fields else []
        self.tmp_file = f"{opts.output_file}.tmp"

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
                print(
                    f'Any of index(es) {", ".join(self.opts.index_prefixes)} does not exist in {self.opts.url}.'
                )
                sys.exit(1)
        self.opts.index_prefixes = indexes

    @retry(elasticsearch.exceptions.ConnectionError, tries=TIMES_TO_TRY)
    def search_query(self: Self) -> Any:
        """"Prepare search query string."""

        @retry(elasticsearch.exceptions.ConnectionError, tries=TIMES_TO_TRY)
        def next_scroll(scroll_id: Any) -> Any:
            return self.es_conn.scroll(scroll=self.scroll_time, scroll_id=scroll_id)

        search_args = {
            "index": ",".join(self.opts.index_prefixes),
            "scroll": self.scroll_time,
            "size": self.opts.scroll_size,
            "terminate_after": self.opts.max_results,
        }
        if self.opts.sort:
            search_args["sort"] = ",".join(self.opts.sort)

        if self.opts.doc_types:
            search_args["doc_type"] = self.opts.doc_types

        if self.opts.query.startswith("@"):
            query_file = self.opts.query[1:]
            if Path(query_file).exists():
                with codecs.open(query_file, mode="r", encoding="utf-8") as f:
                    self.opts.query = f.read()
            else:
                print(f"No such file: {query_file}.")
                sys.exit(1)
        if self.opts.raw_query:
            try:
                query = json.loads(self.opts.query)
            except ValueError as e:
                print(f"Invalid JSON syntax in query. {e}")
                sys.exit(1)
            search_args["body"] = query
        else:
            query = (
                self.opts.query
                if not self.opts.tags
                else "{} AND tags: ({})".format(self.opts.query, " AND ".join(self.opts.tags))
            )
            search_args["q"] = query

        if "_all" not in self.opts.fields:
            search_args["_source_include"] = ",".join(self.opts.fields)
            self.csv_headers.extend([str(field, "utf-8") for field in self.opts.fields if "*" not in field])

        if self.opts.debug_mode:
            print("Using these indices: {}.".format(", ".join(self.opts.index_prefixes)))
            print(
                "Query[{0[0]}]: {0[1]}.".format(
                    ("Query DSL", json.dumps(query, ensure_ascii=False).encode("utf8"))
                    if self.opts.raw_query
                    else ("Lucene", query)
                )
            )
            print("Output field(s): {}.".format(", ".join(self.opts.fields)))
            print("Sorting by: {}.".format(", ".join(self.opts.sort)))

        res = self.es_conn.search(**search_args)
        self.num_results = res["hits"]["total"]["value"]

        print(f"Found {self.num_results} results.")
        if self.opts.debug_mode:
            print(json.dumps(res.raw, ensure_ascii=False).encode("utf8"))

        if self.num_results > 0:
            codecs.open(self.opts.output_file, mode="w", encoding="utf-8").close()
            codecs.open(self.tmp_file, mode="w", encoding="utf-8").close()

            hit_list = []
            total_lines = 0

            widgets = [
                "Run query ",
                progressbar.Bar(left="[", marker="#", right="]"),
                progressbar.FormatLabel(" [%(value)i/%(max)i] ["),
                progressbar.Percentage(),
                progressbar.FormatLabel("] [%(elapsed)s] ["),
                progressbar.ETA(),
                "] [",
                progressbar.FileTransferSpeed(unit="docs"),
                "]",
            ]
            bar = progressbar.ProgressBar(widgets=widgets, maxval=self.num_results).start()

            while total_lines != self.num_results:
                if res["_scroll_id"] not in self.scroll_ids:
                    self.scroll_ids.append(res["_scroll_id"])

                if not res["hits"]["hits"]:
                    print("Scroll[{}] expired(multiple reads?). Saving loaded data.".format(res["_scroll_id"]))
                    break
                for hit in res["hits"]["hits"]:
                    total_lines += 1
                    bar.update(total_lines)
                    hit_list.append(hit)
                    if len(hit_list) == FLUSH_BUFFER:
                        self.flush_to_file(hit_list)
                        hit_list = []
                    if self.opts.max_results and total_lines == self.opts.max_results:
                        self.flush_to_file(hit_list)
                        print(f"Hit max result limit: {self.opts.max_results} records")
                        return
                res = next_scroll(res["_scroll_id"])
            self.flush_to_file(hit_list)
            bar.finish()

    def flush_to_file(self: Self, hit_list: Any) -> None:
        """Write data to file."""

        def to_keyvalue_pairs(source: Any, ancestors: Any = None, header_delimeter: str = ".") -> Any:
            if ancestors is None:
                ancestors = []

            def is_list(arg: Any) -> bool:
                return isinstance(arg, list)

            def is_dict(arg: Any) -> bool:
                return isinstance(arg, dict)

            if is_dict(source):
                for key in source:
                    to_keyvalue_pairs(source[key], [*ancestors, key])

            elif is_list(source):
                if self.opts.kibana_nested:
                    [to_keyvalue_pairs(item, ancestors) for item in source]
                else:
                    [to_keyvalue_pairs(item, [*ancestors, str(index)]) for index, item in enumerate(source)]
            else:
                header = header_delimeter.join(ancestors)
                if header not in self.csv_headers:
                    self.csv_headers.append(header)
                try:
                    out[header] = f"{out[header]}{self.opts.delimiter}{source}"
                except Exception:
                    out[header] = source

        with codecs.open(self.tmp_file, mode="a", encoding="utf-8") as tmp_file:
            for hit in hit_list:
                out = {field: hit[field] for field in META_FIELDS} if self.opts.meta_fields else {}
                if "_source" in hit and len(hit["_source"]) > 0:
                    to_keyvalue_pairs(hit["_source"])
                    tmp_file.write(f"{json.dumps(out)}\n")
        tmp_file.close()

    def write_to_csv(self: Self) -> None:
        """"Write to csv file."""
        if self.num_results <= 0:
            return
        self.num_results = sum(
            1 for _ in codecs.open(self.tmp_file, mode="r", encoding="utf-8")
        )
        if self.num_results > 0:
            output_file = codecs.open(self.opts.output_file, mode="a", encoding="utf-8")
            csv_writer = csv.DictWriter(output_file, fieldnames=self.csv_headers)
            csv_writer.writeheader()
            widgets = [
                "Write to csv ",
                progressbar.Bar(left="[", marker="#", right="]"),
                progressbar.FormatLabel(" [%(value)i/%(max)i] ["),
                progressbar.Percentage(),
                progressbar.FormatLabel("] [%(elapsed)s] ["),
                progressbar.ETA(),
                "] [",
                progressbar.FileTransferSpeed(unit="lines"),
                "]",
            ]
            bar = progressbar.ProgressBar(widgets=widgets, maxval=self.num_results).start()

            for timer, line in enumerate(codecs.open(self.tmp_file, mode="r", encoding="utf-8"), start=1):
                bar.update(timer)
                csv_writer.writerow(json.loads(line))
            output_file.close()
            bar.finish()
        else:
            print(
                f'There is no docs with selected field(s): {",".join(self.opts.fields)}.'
            )
        Path(self.tmp_file).unlink()

    def clean_scroll_ids(self: Self) -> None:
        """Clean up scroll."""
        with contextlib.suppress(Exception):
            self.es_conn.clear_scroll(body=",".join(self.scroll_ids))
