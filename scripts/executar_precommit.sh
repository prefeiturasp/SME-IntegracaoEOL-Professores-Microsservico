#!/usr/bin/env bash

docker compose -f docker-compose-dev.yml run --rm professores pre-commit run --all-files