# Options


| Short Form |   Longer Form    | Description                                           | Required |        Default         |
|:-----------|:----------------:|-------------------------------------------------------|:---------|:----------------------:|
| -q         |     --query      | Query string in Query DSL syntax                      | ✅        |           -            |
| -o         |  --output-file   | CSV file location                                     | ✅        |           -            |
| -i         | --index-prefixes | Index name/prefix(es)                                 | ✅        |           -            |
| -u         |      --url       | Elasticsearch host URL.                               | ❎        | https://localhost:9200 |
| -U         |      --user      | Elasticsearch basic_auth authentication user.         | ❎        |        elastic         |
| -p         |    --password    | Elasticsearch basic_auth authentication password.     | ✅        |           -            |
| -f         |     --fields     | List of _source fields to present be in output.       | ❎        |          _all          |
| -S         |      --sort      | List of fields to sort on in form <field>:<direction> | ❎        |           []           |
| -d         |   --delimiter    | Delimiter to use in CSV file.                         | ❎        |           ,            |
| -m         |  --max-results   | Maximum number of results to return.                  | ❎        |           10           |
| -s         |  --scroll-size   | Scroll size for each batch of results.                | ❎        |          100           |
| -e         |  --meta-fields   | Meta-fields to add in output file                     | ❎        |           -            |
|            |  --verify-certs  | Verify SSL certificates.                              | ❎        |           -            |
|            |    --ca-certs    | Location of CA bundle.                                | ❎        |           -            |
|            |  --client-cert   | Location of Client Auth cert.                         | ❎        |           -            |
|            |   --client-key   | Location of Client Cert Key                           | ❎        |           -            |
| -v         |    --version     | Show version and exit.                                | ❎        |           -            |
|            |     --debug      | Debug mode on.                                        | ❎        |         False          |
| --help     |      --help      | Show this message and exit.                           | ❎        |           -            |

[1]: https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl.html
[2]: https://www.elastic.co/guide/en/elasticsearch/client/python-api/current/connecting.html#_verifying_https_with_ca_certificates
[3]: https://www.elastic.co/guide/en/elasticsearch/reference/8.9/search-search.html#search-search-api-path-params
[4]: https://www.elastic.co/guide/en/elasticsearch/reference/8.9/search-search.html#search-search-api-query-params



# Examples

query
-----
Searching on **http://localhost:9200**, by default

```bash
esxport -q '{"query": {"match_all": {}}}' -i index_name -o index_name.csv
```

output-file
-----------
Save to **database.csv** file

```bash
esxport -q '{"query": {"match_all": {}}}' -i index_name -o database.csv
```

index-prefixes
-----------
Search in **top-secrets** index

```bash
esxport -q '{"query": {"match_all": {}}}' -i top-secrets -o database.csv
```

url
---
On custom Elasticsearch host, **my.es.com**

```bash
esxport -q '{"query": {"match_all": {}}}' -i index_name -o database.csv -u https://my.es.com
```

user
----
Authorization with custom, **crawler** user

```bash
esxport -q '{"query": {"match_all": {}}}' -i index_name -o database.csv -U crawler
```

password
----
Authorization with explicit password, **mountains**

```bash
esxport -q '{"query": {"match_all": {}}}' -i index_name -o database.csv -p mountains
```

fields
------
Selecting some fields, what you are interesting in, if you don't need all of them (query run faster)

```bash
esxport -q '{"query": {"match_all": {}}}' -i index_name -o database.csv -f coolField
```

Selecting all fields, (default behaviour)

```bash
esxport -q '{"query": {"match_all": {}}}' -i index_name -o database.csv -f _all
```

sort
----
Sorting by fields, in order what you are interesting in.

```bash
esxport -q '{"query": {"match_all": {}}}' -i index_name -o database.csv -S coolField:desc
```

delimiter
---------
Changing column delimiter in CSV file, by default ','

```bash
esxport -q '{"query": {"match_all": {}}}' -i index_name -o database.csv -d ';'
```

max
---
Max results count

```bash
esxport -q '{"query": {"match_all": {}}}' -i index_name -o database.csv -m 1000
```

scroll-size
---
Retrieve 2000 results in just 2 requests (two scrolls 1000 each):

```bash
esxport -q '{"query": {"match_all": {}}}' -i index_name -o database.csv -m 2000 -S 1000
```

meta-fields
-----------
Selecting meta-fields: _id, _index, _score, _type

```bash
esxport -q '{"query": {"match_all": {}}}' -i index_name -o database.csv -e _id
```

verify-certs
------------
With enabled SSL certificate verification (off by default)

```bash
esxport -q '{"query": {"match_all": {}}}' -i index_name -o database.csv --verify-certs
```

ca-certs
--------
With your own certificate authority bundle, client cert and cert key

```bash
esxport -q '{"query": {"match_all": {}}}' -i index_name -o database.csv --ca-certs ca.crt --client-cert client.
cert --client-key cert.key
```

version
--------
Show the version and exit

```bash
esxport -v
```

debug
--------
Run the tool in debug mode

```bash
esxport -q '{"query": {"match_all": {}}}' -i index_name -o database.csv --debug
```

debug
--------
Show help message

```bash
esxport --help
```
