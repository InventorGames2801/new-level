@echo off
docker compose -f sqlite-compose.yml down -v %*