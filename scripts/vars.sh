#!/bin/bash -e

SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
BASE_DIR="$(dirname "${SCRIPTS_DIR}")"

pushd "${BASE_DIR}" >/dev/null

VERSION="${FORCAD_VERSION}"

if [[ -z "${VERSION}" ]]; then
  echo "[*] Trying to use version from .version"
  VERSION=$(tr -d '\n' <.version)
fi

if [[ -z "${VERSION}" ]]; then
  echo "[*] Could not find specific version, using latest"
  VERSION=latest
fi

popd >/dev/null
