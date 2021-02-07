#!/bin/bash

/await_start.sh

set -e

cd /app/services/tasks

case ${SERVICE} in
"worker")
  echo "[*] Starting celery worker"
  celery -A app \
    worker \
    -E -l info \
    --pool=gevent \
    --concurrency=20
  ;;
"beat")
  echo "[*] Starting celery beat"
  celery -A app \
    beat \
    -l info \
    --pidfile=/tmp/celerybeat.pid \
    --schedule=/tmp/celerybeat-schedule
  ;;
"flower")
  echo "[*] Starting celery flower"
  FLOWER_PORT=${PORT:-5555} \
    celery -A app \
    flower \
    --basic_auth="${ADMIN_USERNAME}:${ADMIN_PASSWORD}" \
    --url_prefix=flower \
    --address=0.0.0.0
  ;;
esac
