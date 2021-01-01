#!/bin/bash -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

pushd "${DIR}"

echo "[*] Building backend base"
docker build -t pomomondreganto/forcad_base:latest -f docker_config/base_images/backend.Dockerfile "${DIR}"

popd

if [[ $* == *"--push"* ]]; then
  echo "[*] Pushing backend base"
  docker push pomomondreganto/forcad_base:latest
fi

echo "[+] Done!"
