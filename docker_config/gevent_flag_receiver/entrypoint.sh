#!/bin/bash

/await_start.sh

set -e

cd /app/flag_receiver/gevent_tcp
echo "[*] Starting gevent flag receiver"
python3 server.py
