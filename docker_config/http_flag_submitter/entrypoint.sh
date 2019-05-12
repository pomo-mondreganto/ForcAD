#!/bin/sh

/await_start.sh

cd /app/flag_submitter/http_server
echo "[*] Starting http flag submitter"
python3 __init__.py
