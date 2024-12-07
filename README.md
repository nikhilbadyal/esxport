# EsXport
[![codecov](https://codecov.io/gh/nikhilbadyal/esxport/graph/badge.svg?token=zaoNlW2YXq)](https://codecov.io/gh/nikhilbadyal/esxport)
[![PyPI Downloads](https://static.pepy.tech/badge/esxport)](https://pypi.org/project/esxport/)
[![PyPI Version](https://img.shields.io/pypi/v/esxport.svg?style=flat)](https://pypi.org/project/esxport/)

A Python-based CLI utility and module designed for querying Elasticsearch and exporting results as a CSV file.

Requirements
------------
1. This tool should be used with Elasticsearch 8.x version.
2. You also need >= `Python 3.8.x`.

Installation
------------

From source:

```bash
pip install esxport
```
For development purpose
```bash
pip install "esxport[dev]"
```
Usage
-----

### CLI Usage

Run `esxport --help` for detailed information on available options:


OPTIONS
---------
```text
Usage: esxport [OPTIONS]

Options:
  -q, --query JSON           Query string in Query DSL syntax. [required]
  -o, --output-file PATH     CSV file location. [required]
  -i, --index-prefixes TEXT  Index name prefix(es). [required]
  -u, --url URL              Elasticsearch host URL. [default: https://localhost:9200]
  -U, --user TEXT            Elasticsearch basic authentication user. [default: elastic]
  -p, --password TEXT        Elasticsearch basic authentication password. [required]
  -f, --fields TEXT          List of _source fields to present in the output. [default: _all]
  -S, --sort ELASTIC SORT    List of fields to sort in the format `<field>:<direction>`.
  -d, --delimiter TEXT       Delimiter to use in the CSV file. [default: ,]
  -m, --max-results INTEGER  Maximum number of results to return. [default: 10]
  -s, --scroll-size INTEGER  Scroll size for each batch of results. [default: 100]
  -e, --meta-fields [_id|_index|_score]
                             Add meta-fields to the output.
  --verify-certs             Verify SSL certificates.
  --ca-certs PATH            Location of CA bundle.
  --client-cert PATH         Location of Client Auth cert.
  --client-key PATH          Location of Client Cert Key.
  -v, --version              Show version and exit.
  --debug                    Enable debug mode.
  --help                     Show this message and exit.
```


Module Usage
---------
In addition to the CLI, EsXport can now be used as a Python module. Below is an example of how to integrate it into
your Python application:

```python
from esxport import CliOptions, EsXport

kwargs = {
    "query": {
        "query": {"match_all": {}},
        "size": 1000
    },
    "output_file": "output.csv",
    "index_prefixes": ["my-index-prefix"],
    "url": "https://localhost:9200",
    "user": "elastic",
    "password": "password",
    "verify_certs": False,
    "debug": True,
    "max_results": 1000,
    "scroll_size": 100,
    "sort": ["field_name:asc"],
    "ca_certs": "path/to/ca.crt"
}

# Create CLI options and initialize EsXport
cli_options = CliOptions(kwargs)
es = EsXport(cli_options)

# Export data
es.export()
```

Class Descriptions
------------------

### `CliOptions`

A configuration class to manage CLI arguments programmatically when using the module.

#### Attributes

| **Attribute**    | **Type**    | **Description**                                         | **Default**                   |
|------------------|-------------|---------------------------------------------------------|-------------------------------|
| `query`          | `dict`      | Elasticsearch Query DSL syntax for filtering data.      | N/A                           |
| `output_file`    | `str`       | Path to save the exported CSV file.                     | N/A                           |
| `url`            | `str`       | Elasticsearch host URL.                                 | `"https://localhost:9200"`    |
| `user`           | `str`       | Basic authentication username for Elasticsearch.        | `"elastic"`                   |
| `password`       | `str`       | Basic authentication password for Elasticsearch.        | N/A                           |
| `index_prefixes` | `list[str]` | List of index prefixes to query.                        | N/A                           |
| `fields`         | `list[str]` | List of `_source` fields to include in the output.      | `["_all"]`                    |
| `sort`           | `list[str]` | Fields to sort the output in the format `field_name:asc | desc`.                        | N/A               |
| `delimiter`      | `str`       | Delimiter for the CSV output.                           | `","`                         |
| `max_results`    | `int`       | Maximum number of results to fetch.                     | `10`                          |
| `scroll_size`    | `int`       | Batch size for scroll queries.                          | `100`                         |
| `meta_fields`    | `list[str]` | Metadata fields to include in the output.               | `["_id", "_index", "_score"]` |
| `verify_certs`   | `bool`      | Whether to verify SSL certificates.                     | `False`                       |
| `ca_certs`       | `str`       | Path to the CA certificate bundle.                      | N/A                           |
| `client_cert`    | `str`       | Path to the client certificate for authentication.      | N/A                           |
| `client_key`     | `str`       | Path to the client key for authentication.              | N/A                           |
| `debug`          | `bool`      | Enable debugging.                                       | `False`                       |

---

#### Example Initialization

```python
from esxport import CliOptions

cli_options = CliOptions({
    "query": {"query": {"match_all": {}}},
    "output_file": "data.csv",
    "url": "https://localhost:9200",
    "user": "elastic",
    "password": "password",
    "index_prefixes": ["my-index-prefix"],
    "fields": ["field1", "field2"],
    "sort": ["field1:asc"],
    "max_results": 1000,
    "scroll_size": 100
})
```


### `EsXport`

The main class for executing the export operation.

#### Methods

| **Method**                                                                  | **Description**                                                                                    |
|-----------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------|
| `__init__(opts: CliOptions, es_client: ElasticsearchClient \| None = None)` | Initializes the `EsXport` object with options (`CliOptions`) and an optional Elasticsearch client. |
| `export()`                                                                  | Executes the query and exports the results to the specified CSV file.                              |

---

#### Example Initialization and Usage

```python
from esxport import CliOptions, EsXport

# Define CLI options
cli_options = CliOptions({
    "query": {"query": {"match_all": {}}},
    "output_file": "output.csv",
    "url": "https://localhost:9200",
    "user": "elastic",
    "password": "password",
    "index_prefixes": ["my-index-prefix"]
})

# Initialize EsXport
esxport = EsXport(cli_options)

# Export data
esxport.export()
```
