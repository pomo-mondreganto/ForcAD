#!/bin/sh

cd -P -- "$(dirname -- "$0")" && pwd -P

rm -rf docker_volumes/postgres/data
rm -f docker_volumes/shared/initialized
rm -f docker_volumes/celery/celery*
rm -f docker_volumes/shared/game_running
rm -f docker_volumes/shared/round
docker-compose down -v --remove-orphans
