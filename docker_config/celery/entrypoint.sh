#!/bin/bash

/await_start.sh

set -e

cd /app/services

case ${SERVICE} in
"worker")
  echo "[*] Starting celery worker"
  celery -A tasks.app \
    worker \
    -E -l info
  ;;
"flower")
  set +e
  echo "[*] Checking if celery is available"
  celery -A tasks.app inspect registered
  # shellcheck disable=SC2181
  while [[ $? != 0 ]]; do
    echo "[*] Waiting for celery..."
    sleep 5
    celery -A tasks.app inspect registered
  done
  set -e

  echo "[*] Starting celery flower"
  FLOWER_PORT=${PORT:-5000} \
    celery -A tasks.app \
    flower \
    --basic_auth="${ADMIN_USERNAME}:${ADMIN_PASSWORD}" \
    --url_prefix=flower \
    --address=0.0.0.0 \
    --broker_api="${BROKER_API_URL}"
  ;;
esac
