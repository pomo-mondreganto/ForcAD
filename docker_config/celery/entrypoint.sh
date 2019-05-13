#!/bin/sh

/await_start.sh

cd /app
echo "[*] Starting celery"
celery worker -A celery_tasks \
    -E -l info \
#    --statedb=/volumes/celery/%n%I.state \
    --pool=gevent \
    --concurrency=500
