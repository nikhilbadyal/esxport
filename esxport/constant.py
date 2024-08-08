"""Useful constants."""
FLUSH_BUFFER = 1000  # Chunk of docs to flush in temp file
CONNECTION_TIMEOUT = 120
TIMES_TO_TRY = 3
RETRY_DELAY = 60
META_FIELDS = ["_id", "_index", "_score"]
default_config_fields = {
    "url": "https://localhost:9200",
    "user": "elastic",
    "index_prefixes": "",
    "fields": ["_all"],
    "sort": [],
    "delimiter": ",",
    "max_results": 10,
    "scroll_size": 100,
    "meta_fields": [],
    "verify_certs": True,
    "ca_certs": "",
    "client_cert": "",
    "client_key": "",
    "debug": False,
}
