#!/bin/bash
docker compose -f sqlite-compose.yml down -v "$@"