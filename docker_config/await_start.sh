#!/bin/bash

set +e

echo "[*] Checking is postgres container started"
python3 /db_check.py
while [[ $? != 0 ]]; do
  sleep 5
  echo "[*] Waiting for postgres container..."
  python3 /db_check.py
done

echo "[*] Checking whether the initializer is done"
python3 /check_initialized.py
while [[ $? != 0 ]]; do
  sleep 5
  echo "[*] Waiting for initializer..."
  python3 /check_initialized.py
done
