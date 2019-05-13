#!/bin/sh

rm -rf docker_volumes/postgres/data
rm -f docker_volumes/shared/initialized
rm -f docker_volumes/celery/celery*
rm -f docker_volumes/shared/game_running
rm -f docker_volumes/shared/round