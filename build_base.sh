#!/bin/bash

set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

echo "[*] Building backend base"
docker build -t pomomondreganto/forcad_base:latest -f docker_config/base_images/backend.Dockerfile "${DIR}"

echo "[*] Building postgres base"
docker build -t pomomondreganto/forcad_postgres:latest -f docker_config/base_images/postgres.Dockerfile "${DIR}"

echo "[*] Pushing backend base"
docker push pomomondreganto/forcad_base:latest

echo "[*] Pushing postgres base"
docker push pomomondreganto/forcad_postgres:latest

echo "[+] Done!"
