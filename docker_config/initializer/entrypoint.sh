#!/bin/bash -e

cd /app

set +e

echo "[*] Checking if postgres & rabbitmq are available"
python3 /db_check.py
# shellcheck disable=SC2181
while [[ $? != 0 ]]; do
  echo "[*] Waiting for postgres & rabbitmq..."
  sleep 5
  python3 /db_check.py
done

python3 /check_initialized.py
# shellcheck disable=SC2181
if [[ $? == 0 ]]; then
  echo "[+] Already initialized"
else
  echo "[*] Initializing game"
  set -e

  echo "[*] Resetting & initializing database"
  python3 ./scripts/full_reset.py

  echo "[+] Successfully initialized"
fi
