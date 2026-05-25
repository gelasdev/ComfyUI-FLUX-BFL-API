---
description: Draft and create a Conventional Commits 1.0.0 git commit from the current diff. No Jira prefix, no AI attribution. BFL scope inferred from changed paths. Never auto-stages with -A; refuses on detected API keys.
disable-model-invocation: true
allowed-tools: Read, Bash(git status:*), Bash(git diff:*), Bash(git log -1:*), Bash(git add:*), Bash(git commit:*), Bash(git branch:*)
argument-hint: [type] [scope:name] [hint phrase]
---

# `/commit` — Conventional Commits 1.0.0 for ComfyUI-FLUX-BFL-API

Drafts and creates a single Conventional Commits–compliant commit from the current diff. **Never auto-commits without showing the proposed message and the file list first.**

## Convention authority

- [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/).
- Lowercase, imperative ("add", "fix", "rename", not "added"/"adds"), no period at end of subject, ≤ 72 chars.
- Do **NOT** inspect existing `git log` to derive style — historical commits used non-standard types like `update:`. The new standard starts now.
- Do **NOT** include any ticket/Jira prefix.
- **No AI attribution lines.** No `Co-Authored-By: Claude`, no "Generated with…" footer. Never.

## Workflow

1. Run `git status -s` and `git diff` (staged + unstaged) in parallel.
2. Read the diff. Classify the dominant change to pick `type`:
   `feat | fix | refactor | chore | docs | style | perf | test | build | ci`
   (use `$ARGUMENTS` if the user passed a hint).
3. Infer an optional `scope` from changed paths using the BFL module map:
   - `nodes/api_node.py` → `api`
   - `nodes/finetune.py` → `finetune`
   - `nodes/config.py`, `nodes/config_node.py` → `config`
   - `nodes/utils.py`, `nodes/base.py`, `nodes/status.py` → `utils`
   - `web/js/*` → `web`
   - `README.md`, `workflows/*` → `docs`
   - `pyproject.toml` `version` bump only → `release`
   - `.claude/*`, `CLAUDE.md` → `tooling`
   If the change spans multiple modules with no dominant scope, omit scope entirely.
4. Write a one-line description: lowercase, imperative, no period, ≤ 72 chars.
5. If the change is non-trivial (>50 LOC or crosses modules), add a body explaining *why* (not *what*). Single blank line after the subject; wrap body at 72 chars.
6. If the change is breaking (renames a node registry key, changes RETURN_TYPES, changes config schema), append `!` to type/scope and add a `BREAKING CHANGE:` footer.
7. Stage explicitly selected files (NEVER `git add -A`, NEVER `git add .`). Default to only the files that match the inferred classification — show the user the proposed file list and ask "Confirm? (y/n)" before staging.
8. Loud warning if `git branch --show-current` returns `master` — `master`-direct commits are the current norm, but the warning makes the choice explicit.
9. Commit with a heredoc to preserve newlines:

   ```bash
   git commit -m "$(cat <<'EOF'
   <type>[scope][!]: <subject>

   <optional body explaining why>

   <optional BREAKING CHANGE: footer>
   EOF
   )"
   ```

## Safety rails

- **Refuse** if any staged file matches `.env`, `.env.*` (except `.env.example`), `*.key`, `*.pem`, `secrets/`.
- **Refuse** if any staged change to `config.ini` sets `X_KEY` to anything other than `your-key`. (The PreToolUse hook already blocks the write, but check here too — older state on the filesystem could slip through.)
- **Refuse** if `git diff --cached` contains a value that looks like a real BFL API key — long alphanumeric/dash string assigned to `X_KEY` or to `x-key` header.
- **Refuse** `git commit --amend` unless the user explicitly types "amend" in this command's arguments.
- **Never** use `--no-verify`. If a pre-commit hook fails, fix the underlying issue.
- **Never** push. Pushing is a separate, explicit user action.

## Example flow

```
User: /commit feat scope:api
You:  Diff: nodes/api_node.py (+45 -2), README.md (+2 -0)
      Proposed:

          feat(api): add Flux 3 generation node

          adds the Flux 3 model class with aspect_ratio support and the
          standard config-override path; registers as Flux3_BFL and
          updates the README node table.

      Staging: nodes/api_node.py, README.md
      Confirm? (y/n)
```

Wait for `y` before staging + committing. On `n`, ask what to change and re-draft.
