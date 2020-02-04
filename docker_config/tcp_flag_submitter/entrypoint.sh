#!/bin/bash

/await_start.sh

set -e

cd /app/flag_submitter/tcp_server
echo "[*] Starting tcp flag submitter"
python3 server.py
