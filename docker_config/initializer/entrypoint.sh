#!/bin/bash

set +e
echo "[*] Checking is postgres container started"
python3 /db_check.py
while [[ $? != 0 ]]; do
  sleep 3
  echo "[*] Waiting for postgres container..."
  python3 /db_check.py
done

python3 /check_initialized.py
if [[ $? == 0 ]]; then
  echo "[+] Already initialized, starting"
else
  echo "[*] Initializing game"
  set -e

  echo "[*] Resetting & initializing database"
  python3 /app/scripts/full_reset.py

  echo "[+] Successfully initialized"
fi
