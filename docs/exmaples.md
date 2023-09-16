# Options


| Short Form |   Longer Form    | Description                                           | Required |        Default         |
|:-----------|:----------------:|-------------------------------------------------------|:---------|:----------------------:|
| -q         |     --query      | Query string in Query DSL syntax                      | ✅        |           -            |
| -o         |  --output-file   | CSV file location                                     | ✅        |           -            |
| -u         |      --url       | Elasticsearch host URL.                               | ❎        | https://localhost:9200 |
| -U         |      --user      | Elasticsearch basic_auth authentication user.         | ❎        |        elastic         |
| -p         |    --password    | Elasticsearch basic_auth authentication password.     | ✅        |           -            |
| -i         | --index-prefixes | Index name/prefix(es)                                 | ✅        |           -            |
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
