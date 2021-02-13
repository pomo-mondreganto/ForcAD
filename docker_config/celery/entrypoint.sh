#!/bin/bash

/await_start.sh

set -e

cd /app/services

case ${SERVICE} in
"worker")
  echo "[*] Starting celery worker"
  celery -A tasks.app \
    worker \
    -E -l info \
    --pool=gevent \
    --concurrency=20
  ;;
"flower")
  echo "[*] Starting celery flower"
  FLOWER_PORT=${PORT:-5555} \
    celery -A tasks.app \
    flower \
    --basic_auth="${ADMIN_USERNAME}:${ADMIN_PASSWORD}" \
    --url_prefix=flower \
    --address=0.0.0.0
  ;;
esac
