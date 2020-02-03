#!/bin/sh

set -e

cd /app

echo "[*] Running yarn build"
yarn build

echo "[*] Cleaning /front_build"
rm -rf /front_build/*

echo "[*] Copying dist/* files to /react_build"
cp -r dist/* /front_build

echo "[+] Done, exiting"
