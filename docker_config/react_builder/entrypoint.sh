#!/bin/sh

cd /app

echo "[*] Running npm run build"
npm run build

echo "[*] Cleaning /react_build"
rm -rf /react_build/*

echo "[*] Copying build/* files to /react_build"
cp -r  build/* /react_build

echo "[+] Done, exiting"
