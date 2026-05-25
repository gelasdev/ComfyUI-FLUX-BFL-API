#!/usr/bin/env bash
# SessionStart hook.
#
# Emits current git branch, last 5 commits, and short status as
# hookSpecificOutput.additionalContext so the new session knows
# exactly where it's resuming.
#
# Read-only. Exits 0 always — SessionStart cannot block on exit 2.

set -euo pipefail

cd "${CLAUDE_PROJECT_DIR:-$(pwd)}"

if ! command -v git >/dev/null 2>&1 || ! git rev-parse --git-dir >/dev/null 2>&1; then
  exit 0
fi

branch=$(git branch --show-current 2>/dev/null || echo "(detached)")
log=$(git log --oneline -5 2>/dev/null || echo "(no commits)")
status=$(git status --short 2>/dev/null | head -10 || echo "")
status_count=$(printf '%s\n' "$status" | sed '/^$/d' | wc -l | tr -d ' ')

context=$(printf 'BFL git context (auto-injected at session start):\n\nBranch: %s\n\nRecent commits:\n%s\n\nWorking tree (%s files changed):\n%s\n' \
  "$branch" "$log" "$status_count" "${status:-(clean)}")

if command -v jq >/dev/null 2>&1; then
  jq -n --arg ctx "$context" '{
    hookSpecificOutput: {
      hookEventName: "SessionStart",
      additionalContext: $ctx
    }
  }'
else
  escaped=$(printf '%s' "$context" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()), end="")' 2>/dev/null || printf '"%s"' "$(printf '%s' "$context" | sed 's/\\/\\\\/g; s/"/\\"/g; s/$/\\n/' | tr -d '\n')")
  printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":%s}}\n' "$escaped"
fi

exit 0
