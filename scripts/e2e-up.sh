#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

docker compose up -d db
echo "waiting for postgres..."
for i in {1..30}; do
  if docker compose exec -T db pg_isready -U postgres >/dev/null 2>&1; then break; fi
  sleep 1
done

(cd apps/api && uv run alembic upgrade head)
(cd apps/api && uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 >/tmp/echo-api.log 2>&1 &)
echo $! > /tmp/echo-api.pid

echo "waiting for api..."
for i in {1..30}; do
  if curl -sf http://localhost:8000/health >/dev/null; then break; fi
  sleep 1
done

(cd apps/web && bun run build && bun run start >/tmp/echo-web.log 2>&1 &)
echo $! > /tmp/echo-web.pid

echo "waiting for web..."
for i in {1..60}; do
  if curl -sf http://localhost:3000 >/dev/null; then break; fi
  sleep 1
done
echo "stack up"
