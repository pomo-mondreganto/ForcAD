#!/bin/bash

/await_start.sh

set -e

cd /app/flag_submitter/stdin_default
echo "[*] Starting stdin (socat) flag submitter"
socat TCP4-LISTEN:31338,reuseaddr,fork EXEC:"python3 server.py"
