#!/usr/bin/env bash
# PreToolUse(Edit|Write) hook — block writing a real X_KEY to config.ini.
#
# config.ini is committed with the placeholder value `your-key`. Users edit
# it locally after clone. If an Edit/Write would set X_KEY to anything other
# than `your-key` (or empty), refuse — the user almost certainly did not mean
# to commit their real BFL API key to the public repo.
#
# Exit 2 = block (PreToolUse honors exit 2 as a hard deny).
# Exit 0 = allow.

set -euo pipefail

input=$(cat)

read -r file_path payload <<<"$(printf '%s' "$input" | python3 -c '
import json, sys
try:
    data = json.loads(sys.stdin.read())
    ti = data.get("tool_input", {}) or {}
    fp = ti.get("file_path") or ti.get("path") or ""
    # Edit uses new_string; Write uses content. Read whichever is set.
    payload = ti.get("new_string") or ti.get("content") or ""
    # Single-line, space-separated: file_path then base64-encoded payload to
    # survive shell escaping. We base64 on the python side and decode below.
    import base64
    b = base64.b64encode(payload.encode("utf-8")).decode("ascii")
    print(fp, b)
except Exception:
    print("", "")
' 2>/dev/null)"

if [ -z "$file_path" ]; then
  exit 0
fi

# Only inspect config.ini (any depth).
case "$file_path" in
  *config.ini|*/config.ini)
    ;;
  *)
    exit 0
    ;;
esac

# Decode the payload and grep for X_KEY = <value>.
content=$(printf '%s' "$payload" | python3 -c 'import sys,base64; sys.stdout.write(base64.b64decode(sys.stdin.read()).decode("utf-8","replace"))' 2>/dev/null || echo "")

if [ -z "$content" ]; then
  # Nothing to inspect (e.g. Edit with empty new_string) — allow.
  exit 0
fi

# Match `X_KEY = <value>` (case-insensitive key, optional spaces).
value=$(printf '%s' "$content" | grep -iE '^[[:space:]]*X_KEY[[:space:]]*=' | head -1 | sed -E 's/^[[:space:]]*[Xx]_[Kk][Ee][Yy][[:space:]]*=[[:space:]]*//' | sed -E 's/[[:space:]]+$//')

if [ -z "$value" ] || [ "$value" = "your-key" ]; then
  exit 0
fi

cat >&2 <<EOF
Refusing to write a real X_KEY value to config.ini.

Tracked value must stay the placeholder \`your-key\`. Real BFL API keys are
user-local — set them after clone, never commit them.

Detected value (truncated): ${value:0:6}...

To override locally (NOT committed), edit config.ini after the file is
written and keep that change off git. To bypass this hook for a legitimate
non-key edit, write the file with X_KEY = your-key in the new content.

See CLAUDE.md "Never commit a real X_KEY in config.ini".
EOF
exit 2
