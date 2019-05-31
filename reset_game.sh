#!/bin/sh

cd -P -- "$(dirname -- "$0")" && pwd -P

rm -rf docker_volumes/postgres/data
docker-compose down -v --remove-orphans
