#!/bin/bash -e

SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
source "${SCRIPTS_DIR}/vars.sh"

RELEASE_DIR="ForcAD_${VERSION}"

pushd "${BASE_DIR}" >/dev/null

rm -rf "${RELEASE_DIR}" "${RELEASE_DIR}.zip"

# to create clean releases locally
find . -name "__pycache__" -prune -exec rm -rf {} \;

while read -r file; do
  echo "$file"
  mkdir -p "${RELEASE_DIR}/$(dirname "${file}")"
  cp -r "${file}" "${RELEASE_DIR}/${file}"
done <"${SCRIPTS_DIR}/BOM.txt"

zip -r "${RELEASE_DIR}.zip" "${RELEASE_DIR}"

popd >/dev/null
