#!/bin/sh

/await_start.sh

cd /app
echo "[*] Starting celerybeat"
celery beat -A celery_tasks \
    --schedule=/volumes/celery/celerybeat-schedule \
    --pidfile=/tmp/celerybeat.pid