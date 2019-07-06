#!/bin/sh

/await_start.sh

cd /app/flag_submitter/tcp_server
echo "[*] Starting tcp flag submitter"
python3 server.py
