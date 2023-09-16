#!/usr/bin/env bats

DOCS_COUNT=$(cat /data/tests/es_data/docs.ndjson | wc -l)
OUT_FILE=/data/out.csv

@test "prints usage instructions" {
  run esxport -h
  [ "$status" -eq 0 ]
  [ $(expr "${lines[0]}" : "usage: esxport.*") -ne 0 ]
}
@test "query result count" {
  run esxport -q '*' -o $OUT_FILE --debug
  echo ${output}
  [ "$status" -eq 0 ]
  [ "${lines[3]//[^0-9]/}" -eq "$DOCS_COUNT" ]
  [ $(expr $(cat out.csv | wc -l) - 1) -eq "$DOCS_COUNT" ]
}
