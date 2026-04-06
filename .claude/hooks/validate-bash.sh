#!/usr/bin/env bash
# validate-bash.sh — Pre-hook for Bash tool calls
# Runs before any Bash command executed by Claude Code.
# Exit 0 to allow, exit non-zero to block.

set -euo pipefail

COMMAND="${CLAUDE_BASH_COMMAND:-}"

# Block dangerous patterns
if echo "$COMMAND" | grep -qE '(rm\s+-rf\s+/|mkfs\.|dd\s+if=|>\s*/dev/sd)'; then
  echo "BLOCKED: Dangerous command pattern detected: $COMMAND" >&2
  exit 1
fi

# Log all commands for audit
echo "[validate-bash] $(date -u +%Y-%m-%dT%H:%M:%SZ) — $COMMAND" >> /tmp/echo-claude-bash-audit.log

exit 0
