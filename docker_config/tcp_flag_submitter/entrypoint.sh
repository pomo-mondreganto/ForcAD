#!/bin/sh

/await_start.sh

cd /app/flag_submitter/stdin_default
echo "[*] Starting stdin (socat) flag submitter"
socat TCP4-LISTEN:31337,reuseaddr,fork EXEC:"python3 __init__.py"
