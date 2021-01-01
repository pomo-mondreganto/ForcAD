#!/bin/bash -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
IMAGE=ghcr.io/pomo-mondreganto/forcad_base:latest

pushd "${DIR}"

echo "[*] Building backend base"
docker build -t "${IMAGE}" -f docker_config/base_images/backend.Dockerfile "${DIR}"

popd

if [[ $* == *"--push"* ]]; then
  echo "[*] Pushing backend base"
  docker push "${IMAGE}"
fi

echo "[+] Done!"
