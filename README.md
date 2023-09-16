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
```bash
 Arguments:
  -q, --query QUERY                        Query string in Query DSL syntax.               [required]
  -o, --output-file FILE                   CSV file location.                           [required]
  -u, --url URL                            Elasticsearch host URL. Default is http://localhost:9200.
  -U, --user USER                          Elasticsearch basic authentication user.
  -p, --password password                  Elasticsearch basic authentication password. [required]
  -i, --index-prefixes INDEX [INDEX ...]   Index name prefix(es). Default is ['logstash-*'].
  -t, --tags TAGS [TAGS ...]               Query tags.
  -f, --fields FIELDS [FIELDS ...]         List of selected fields in output. Default is ['_all'].
  -S, --sort FIELDS [FIELDS ...]           List of <field>:<direction> pairs to sort on. Default is [].
  -d, --delimiter DELIMITER                Delimiter to use in CSV file. Default is ",".
  -m, --max INTEGER                        Maximum number of results to return. Default is 0.
  -s, --scroll-size INTEGER                Scroll size for each batch of results. Default is 100.
  -e, --meta-fields                        Add meta-fields in output.
  --verify-certs                           Verify SSL certificates. Default is False.
  --ca-certs CA_CERTS                      Location of CA bundle.
  --client-cert CLIENT_CERT                Location of Client Auth cert.
  --client-key CLIENT_KEY                  Location of Client Cert Key.
  -v, --version                            Show version and exit.
  --debug                                  Debug mode on.
  -h, --help                               show this help message and exit
```
