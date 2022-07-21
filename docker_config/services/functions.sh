#!/bin/bash -e

start_web() {
  echo "[*] Starting web service $1"
  cd "services/$1"
  gunicorn "app:app" \
    --bind "0.0.0.0:${PORT:-5000}" \
    --log-level "${LOG_LEVEL:-INFO}" \
    --worker-class eventlet \
    --worker-connections 1024
}

start_api() {
  start_web api
}

start_admin() {
  start_web admin
}

start_events() {
  start_web events
}

start_http_receiver() {
  start_web http_receiver
}

start_ticker() {
  echo "[*] Starting ticker"
  cd services
  python3 -m ticker
}
