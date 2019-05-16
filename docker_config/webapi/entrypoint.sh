#!/bin/sh

/await_start.sh

cd /app/webapi
echo "[*] Starting web api"
gunicorn app:app --bind 0.0.0.0:5000 --worker-class sanic.worker.GunicornWorker
