#!/usr/bin/env bash
# auto-format.sh — PostToolUse hook for Edit/Write
# Auto-formats files after Claude edits them.
# Routes by file extension: ruff for Python, biome for TypeScript/JS.

set -euo pipefail

FILE_PATH=$(jq -r '.tool_input.file_path // empty' < /dev/stdin)

# Exit silently if no file path
[[ -z "$FILE_PATH" ]] && exit 0

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"

case "$FILE_PATH" in
  */apps/api/*.py)
    cd "$PROJECT_DIR/apps/api" && uv run ruff format "$FILE_PATH" 2>/dev/null || true
    ;;
  */apps/web/*.ts | */apps/web/*.tsx | */apps/web/*.js | */apps/web/*.jsx)
    cd "$PROJECT_DIR/apps/web" && npx @biomejs/biome format --write "$FILE_PATH" 2>/dev/null || true
    ;;
esac

exit 0
