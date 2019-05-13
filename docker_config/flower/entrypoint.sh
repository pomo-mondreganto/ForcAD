#!/bin/sh

/await_start.sh

cd /app
echo "[*] Starting flower"
celery flower -A celery_tasks \
    --basic_auth="$FLOWER_BASIC_AUTH" \
    --url-prefix=flower \
    --host=0.0.0.0 \
    --port=5555