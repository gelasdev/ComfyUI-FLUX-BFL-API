#!/usr/bin/env bash
# PostToolUse(Edit|Write) hook — auto-ruff after Python edits.
#
# Runs `ruff format` + `ruff check --fix` on the edited file using the
# project's pyproject.toml configuration. Skips __pycache__ and .venv.
# Advisory: ruff diagnostics surface back via stderr, but we exit 0
# either way (post-edit lint feedback should not re-block a successful
# write). If ruff is not installed, exit 0 with a one-line notice.

set -euo pipefail

input=$(cat)

file_path=$(printf '%s' "$input" | python3 -c '
import json, sys
try:
    data = json.loads(sys.stdin.read())
    ti = data.get("tool_input", {}) or {}
    print(ti.get("file_path") or ti.get("path") or "")
except Exception:
    print("")
' 2>/dev/null || echo "")

if [ -z "$file_path" ]; then
  exit 0
fi

case "$file_path" in
  *.py) ;;
  *)    exit 0 ;;
esac

case "$file_path" in
  *__pycache__*|*/.venv/*|*/venv/*) exit 0 ;;
esac

project_dir="${CLAUDE_PROJECT_DIR:-$(pwd)}"
cd "$project_dir" || exit 0

if ! command -v ruff >/dev/null 2>&1; then
  printf '[post-edit-ruff] ruff not on PATH — skipping format/check on %s\n' "$file_path" >&2
  exit 0
fi

rel="${file_path#${project_dir}/}"

ruff format "$rel" >&2 || true
ruff check --fix "$rel" >&2 || true
exit 0
