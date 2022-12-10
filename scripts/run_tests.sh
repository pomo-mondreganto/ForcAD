#!/bin/bash -e

export TEST=1

python tests/setup_forcad.py
./control.py setup
# shellcheck disable=SC2038,SC2046
export $(find ./docker_config -name "*.env" -exec egrep -v '^#' {} \; | xargs)
./control.py reset
./control.py build
./control.py start
docker ps
docker compose ps
docker compose logs -f initializer
python tests/wait_for_start.py
./control.py rd ps
env | sort
python -m unittest discover -v -s tests
