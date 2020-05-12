#!/bin/bash

set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

echo "[*] Building backend base"
docker build -t pomomondreganto/forcad_base:latest -f docker_config/base_images/backend.Dockerfile "${DIR}"

echo "[*] Pushing backend base"
docker push pomomondreganto/forcad_base:latest

echo "[+] Done!"
