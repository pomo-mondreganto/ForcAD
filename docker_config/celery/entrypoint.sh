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
  celery -A app \
    flower \
    --basic_auth="$FLOWER_BASIC_AUTH" \
    --url-prefix=flower \
    --host=0.0.0.0 \
    --port=5555
  ;;
esac
