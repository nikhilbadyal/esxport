#!/bin/bash

set -o allexport
source test/.env
set +o allexport
set -euxo pipefail

# Check if SKIP_ES_SETUP is set to 1 (skip if set to 1)
if [ "${SKIP_ES_SETUP:-0}" = "1" ]; then
  echo "Skipping Elasticsearch setup as SKIP_ES_SETUP is set to 1."
  exit 0
fi

if [[ -z $STACK_VERSION ]]; then
  echo -e "\033[31;1mERROR:\033[0m Required environment variable [STACK_VERSION] not set\033[0m"
  exit 1
fi

MAJOR_VERSION="$(echo "${STACK_VERSION}" | cut -c 1)"
network_name=elastic
stop_and_remove_containers() {
  existing_containers=$(docker ps -a --filter "network=$network_name" --filter "name=es*" -q)

  if [ -n "$existing_containers" ]; then
    echo "Stopping and removing existing Elasticsearch containers in network $network_name:"
    docker kill "$existing_containers"
    docker rm --force "$existing_containers"
  fi
}

stop_and_remove_containers
if ! docker network inspect "$network_name" &>/dev/null; then
  docker network create "$network_name"
  echo "Created network: $network_name"
else
  echo "Network $network_name already exists."
fi

mkdir -p "$(pwd)"/es/plugins

if [[ ! -z $PLUGINS ]]; then
  docker run --rm \
    --network=elastic \
    -v "$(pwd)"/es/plugins/:/usr/share/elasticsearch/plugins/ \
    --entrypoint=/usr/share/elasticsearch/bin/elasticsearch-plugin \
    docker.elastic.co/elasticsearch/elasticsearch:"${STACK_VERSION}" \
    install "${PLUGINS/\\n/ }" --batch
fi

for (( node=1; node<=${NODES-1}; node++ ))
do
  port_com=$((9300 + node - 1))
  UNICAST_HOSTS+="es$node:${port_com},"
done

for (( node=1; node<=${NODES-1}; node++ ))
do
  port=$((${PORT:-9200} + node - 1))
  port_com=$((9300 + node - 1))
  if [ "x${MAJOR_VERSION}" == 'x6' ]; then
    docker run \
      --rm \
      --env "node.name=es${node}" \
      --env "cluster.name=docker-elasticsearch" \
      --env "cluster.routing.allocation.disk.threshold_enabled=false" \
      --env "bootstrap.memory_lock=true" \
      --env "ES_JAVA_OPTS=-Xms1g -Xmx1g" \
      --env "xpack.security.enabled=false" \
      --env "xpack.license.self_generated.type=basic" \
      --env "discovery.zen.ping.unicast.hosts=${UNICAST_HOSTS}" \
      --env "discovery.zen.minimum_master_nodes=${NODES}" \
      --env "http.port=${port}" \
      --ulimit nofile=65536:65536 \
      --ulimit memlock=-1:-1 \
      --publish "${port}:${port}" \
      --publish "${port_com}:${port_com}" \
      --detach \
      --network=elastic \
      --name="es${node}" \
      -v "$(pwd)"/es/plugins/:/usr/share/elasticsearch/plugins/ \
      docker.elastic.co/elasticsearch/elasticsearch:"${STACK_VERSION}"
  elif [ "x${MAJOR_VERSION}" == 'x7' ]; then
    docker run \
      --rm \
      --env "node.name=es${node}" \
      --env "cluster.name=docker-elasticsearch" \
      --env "cluster.initial_master_nodes=es1" \
      --env "discovery.seed_hosts=es1" \
      --env "cluster.routing.allocation.disk.threshold_enabled=false" \
      --env "bootstrap.memory_lock=true" \
      --env "ES_JAVA_OPTS=-Xms1g -Xmx1g" \
      --env "xpack.security.enabled=false" \
      --env "xpack.license.self_generated.type=basic" \
      --env "http.port=${port}" \
      --env "action.destructive_requires_name=false" \
      --ulimit nofile=65536:65536 \
      --ulimit memlock=-1:-1 \
      --publish "${port}:${port}" \
      --detach \
      --network=elastic \
      --name="es${node}" \
      -v "$(pwd)"/es/plugins/:/usr/share/elasticsearch/plugins/ \
      docker.elastic.co/elasticsearch/elasticsearch:"${STACK_VERSION}"
  elif [ "x${MAJOR_VERSION}" == 'x8' ]; then
    if [ "${SECURITY_ENABLED}" == 'true' ]; then
      elasticsearch_password=${ELASTICSEARCH_PASSWORD-'changeme'}
      docker run \
        --rm \
        --env "ELASTIC_PASSWORD=${elasticsearch_password}" \
        --env "xpack.license.self_generated.type=basic" \
        --env "node.name=es${node}" \
        --env "cluster.name=docker-elasticsearch" \
        --env "cluster.initial_master_nodes=es1" \
        --env "discovery.seed_hosts=es1" \
        --env "cluster.routing.allocation.disk.threshold_enabled=false" \
        --env "bootstrap.memory_lock=true" \
        --env "ES_JAVA_OPTS=-Xms1g -Xmx1g" \
        --env "http.port=${port}" \
        --env "action.destructive_requires_name=false" \
        --ulimit nofile=65536:65536 \
        --ulimit memlock=-1:-1 \
        --publish "${port}:${port}" \
        --network=elastic \
        --name="es${node}" \
        --detach \
        -v "$(pwd)"/es/plugins/:/usr/share/elasticsearch/plugins/ \
        docker.elastic.co/elasticsearch/elasticsearch:"${STACK_VERSION}"
    else
      docker run \
        --rm \
        --env "xpack.security.enabled=false" \
        --env "node.name=es${node}" \
        --env "cluster.name=docker-elasticsearch" \
        --env "cluster.initial_master_nodes=es1" \
        --env "discovery.seed_hosts=es1" \
        --env "cluster.routing.allocation.disk.threshold_enabled=false" \
        --env "bootstrap.memory_lock=true" \
        --env "ES_JAVA_OPTS=-Xms1g -Xmx1g" \
        --env "xpack.license.self_generated.type=basic" \
        --env "http.port=${port}" \
        --env "action.destructive_requires_name=false" \
        --ulimit nofile=65536:65536 \
        --ulimit memlock=-1:-1 \
        --publish "${port}:${port}" \
        --network=elastic \
        --name="es${node}" \
        --detach \
        -v "$(pwd)"/es/plugins/:/usr/share/elasticsearch/plugins/ \
        docker.elastic.co/elasticsearch/elasticsearch:"${STACK_VERSION}"
    fi
  fi
done
sleep 10
if [ "x${MAJOR_VERSION}" == 'x8' ] && [ "${SECURITY_ENABLED}" == 'true' ]; then
  docker run \
    --network elastic \
    --rm \
    alpine/curl \
    --max-time 10 \
    --retry 60 \
    --retry-delay 1 \
    --retry-connrefused \
    --show-error \
    --silent \
    -k \
    -u elastic:"${ELASTICSEARCH_PASSWORD-'changeme'}" \
    https://es1:"$PORT"
else
  docker run \
    --network elastic \
    --rm \
    alpine/curl \
    --max-time 10 \
    --retry 60 \
    --retry-delay 1 \
    --retry-connrefused \
    --show-error \
    --silent \
    http://es1:"$PORT"
fi


echo "Elasticsearch up and running"
