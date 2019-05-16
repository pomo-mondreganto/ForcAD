#!/bin/sh

/await_start.sh

cd /app/flag_submitter/http_server

echo "[*] Starting http flag submitter"
gunicorn --worker-class gevent --worker-connections 1024 --bind 0.0.0.0:5000 app:app