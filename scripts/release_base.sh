#!/bin/bash -e

SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
source "${SCRIPTS_DIR}/vars.env"

pushd "${BASE_DIR}" >/dev/null

IMAGE="ghcr.io/pomo-mondreganto/forcad_base:${VERSION}"

echo "[*] Building ${IMAGE}"
docker build -t "${IMAGE}" -f docker_config/base_images/backend.Dockerfile "${BASE_DIR}"

popd >/dev/null

if [[ $* == *"--push"* ]]; then
  echo "[*] Pushing ${IMAGE}"
  docker push "${IMAGE}"
fi

echo "[+] Done!"
