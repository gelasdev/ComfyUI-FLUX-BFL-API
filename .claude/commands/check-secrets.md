---
description: Scan the working tree and recent git history for accidentally-committed BFL API keys, webhook secrets, or other credentials.
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Bash(rg:*), Bash(grep:*), Bash(git log:*), Bash(git show:*)
---

# `/check-secrets` — scan for committed credentials

Catches the most common leakage paths for this project.

## Workflow

1. **Working tree scan**:
   - `config.ini` — confirm `X_KEY = your-key` (the placeholder). Anything else is a finding.
   - `rg -n 'X_KEY[[:space:]]*=[[:space:]]*[^[:space:]]+' .` (excluding `your-key`).
   - `rg -n 'x-key[[:space:]]*:[[:space:]]*[A-Za-z0-9-_]{20,}' .` — header strings with embedded keys.
   - `rg -n 'webhook_secret[[:space:]]*=[[:space:]]*[A-Za-z0-9-_]{16,}' .` — webhook secrets in code.
   - `rg -n 'api\.bfl\.ai/v1/.*\?.*key=' .` — URL-embedded keys (rare but worth checking).
2. **Recent history scan** (last 20 commits):
   - `git log --oneline -20 --all`
   - For each commit: `git show --no-color <sha> -- config.ini` — verify `X_KEY` stayed `your-key`.
3. **Report**:
   - List every finding as `file:line:context`.
   - Distinguish working-tree findings (fixable now) from committed history findings (require `git filter-repo` or rewriting history — flag as urgent).
4. **Do not** print the full secret value. Truncate to first 6 chars + `...`.

## Safety rails

- Read-only. No edits, no rewrites, no `git filter-repo`.
- If a secret is found in committed history, **tell the user explicitly** that rotating the key is the first action — repo rewrites can come after.
- Do not push, do not commit.
