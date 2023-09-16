# es2csv

An adept Python CLI utility designed for querying Elasticsearch and exporting result as a CSV file.


Requirements
------------
1. This tool should be used with Elasticsearch 8.x version.
2. You also need `Python 3.11.x`.

Installation
------------

From source:

```bash
pip install git+https://github.com/nikhilbadyal/es2csv.git
```
Usage
-----

```bash
es2csv --help
```

Arguments
---------
```text
Options:
  -q, --query JSON                Query string in Query DSL syntax.
                                  [required]
  -o, --output-file PATH          CSV file location.  [required]
  -i, --index-prefixes TEXT       Index name prefix(es).  [required]
  -u, --url URL                   Elasticsearch host URL.  [default:
                                  https://localhost:9200]
  -U, --user TEXT                 Elasticsearch basic authentication user.
                                  [default: elastic]
  -p, --password TEXT             Elasticsearch basic authentication password.
                                  [required]
  -f, --fields TEXT               List of _source fields to present be in
                                  output.  [default: _all]
  -S, --sort ELASTIC SORT         List of fields to sort on in form
                                  <field>:<direction>
  -d, --delimiter TEXT            Delimiter to use in CSV file.  [default: ,]
  -m, --max-results INTEGER       Maximum number of results to return.
                                  [default: 10]
  -s, --scroll-size INTEGER       Scroll size for each batch of results.
                                  [default: 100]
  -e, --meta-fields [_id|_index|_score]
                                  Add meta-fields in output.
  --verify-certs                  Verify SSL certificates.
  --ca-certs PATH                 Location of CA bundle.
  --client-cert PATH              Location of Client Auth cert.
  --client-key PATH               Location of Client Cert Key.
  -v, --version                   Show version and exit.
  --debug                         Debug mode on.
  --help                          Show this message and exit.
```
