#!/bin/bash -e

source /functions.sh
/await_start.sh

cd /app

"start_${SERVICE}"
