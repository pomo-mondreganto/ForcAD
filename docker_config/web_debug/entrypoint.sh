#!/bin/sh

/await_start.sh

cd /app/interface/debug
echo "[*] Starting debug web app"
python3 __init__.py