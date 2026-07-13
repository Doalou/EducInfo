#!/bin/sh
set -eu

python -m flask --app run:app db upgrade
educinfo admin ensure
exec "$@"
