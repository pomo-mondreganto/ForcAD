#!/bin/sh

cd -P -- "$(dirname -- "$0")" && pwd -P

rm -rf docker_volumes/postgres/data
rm -f docker_volumes/celery/celery*
docker-compose down -v --remove-orphans
