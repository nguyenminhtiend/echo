#!/usr/bin/env bash
set -euo pipefail
[ -f /tmp/echo-web.pid ] && kill "$(cat /tmp/echo-web.pid)" 2>/dev/null || true
[ -f /tmp/echo-api.pid ] && kill "$(cat /tmp/echo-api.pid)" 2>/dev/null || true
rm -f /tmp/echo-web.pid /tmp/echo-api.pid
docker compose down
