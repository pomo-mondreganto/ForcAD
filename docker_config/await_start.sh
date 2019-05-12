#!/bin/sh

while [[ ! -f /volumes/shared/initialized ]]
do
    echo "[*] Waiting for initializer..."
    sleep 3
done

set +e
echo "[*] Checking is postgres container started"
python3 /db_check.py
while [[ $? != 0 ]] ; do
    sleep 3; echo "[*] Waiting for postgres container..."
    python3 /db_check.py
done
