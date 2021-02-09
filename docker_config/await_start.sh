#!/bin/bash

set +e

echo "[*] Checking if postgres & rabbitmq are available"
python3 /db_check.py
# shellcheck disable=SC2181
while [[ $? != 0 ]]; do
  echo "[*] Waiting for postgres & rabbitmq..."
  sleep 5
  python3 /db_check.py
done

echo "[*] Checking whether the initializer is done"
python3 /check_initialized.py
# shellcheck disable=SC2181
while [[ $? != 0 ]]; do
  echo "[*] Waiting for initializer..."
  sleep 5
  python3 /check_initialized.py
done
