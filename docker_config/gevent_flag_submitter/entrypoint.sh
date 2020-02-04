#!/bin/bash

/await_start.sh

set -e

cd /app/flag_submitter/gevent_tcp
echo "[*] Starting gevent flag submitter"
python3 server.py
