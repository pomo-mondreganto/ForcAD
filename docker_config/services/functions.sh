#!/bin/bash -e

start_worker() {
  echo "[*] Starting celery worker"
  cd services/tasks
  celery -A services.tasks \
    -E -l info \
    --pool=gevent \
    --concurrency=20 \
    worker
}

start_beat() {
  echo "[*] Starting celery beat"
  cd services/tasks
  celery -A tasks \
    -l info \
    --pidfile=/tmp/celerybeat.pid \
    --schedule=/tmp/celerybeat-schedule \
    beat
}

start_flower() {
  echo "[*] Starting celery flower"
  cd services/tasks
  celery -A tasks \
    --basic_auth="$FLOWER_BASIC_AUTH" \
    --url-prefix=flower \
    --host=0.0.0.0 \
    --port=5555 \
    flower
}

start_tcp_receiver() {
  echo "[*] Starting gevent flag receiver"
  cd services/tcp_receiver
  python3 server.py
}

start_web() {
  echo "[*] Starting web service $1"
  cd "services/$1"
  gunicorn "app:app" --bind 0.0.0.0:5000 --worker-class eventlet
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

start_monitoring() {
  start_web monitoring
}
