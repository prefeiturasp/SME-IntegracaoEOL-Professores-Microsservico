#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

docker compose -f ../docker-compose-dev.yml build professores

docker compose -f ../docker-compose-dev.yml run --rm professores \
  python -m coverage run -m pytest

docker compose -f ../docker-compose-dev.yml run --rm professores \
  python -m coverage report --show-missing --fail-under=90
