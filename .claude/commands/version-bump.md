---
description: Bump the package version in pyproject.toml (patch | minor | major) and suggest the matching Conventional Commits release commit message.
allowed-tools: Read, Edit, Bash(git diff:*)
argument-hint: patch | minor | major
---

# `/version-bump` — bump pyproject.toml version

Edits a single field — `[project] version` in `pyproject.toml` — using semver.

## Workflow

1. Read current `version` from `pyproject.toml` (e.g. `1.0.13`).
2. Parse `$ARGUMENTS`:
   - `patch` → bump the third number (`1.0.13` → `1.0.14`).
   - `minor` → bump the second, reset patch (`1.0.13` → `1.1.0`).
   - `major` → bump the first, reset minor + patch (`1.0.13` → `2.0.0`).
   - If missing or invalid: ask once.
3. Edit `pyproject.toml`:
   - `version = "<old>"` → `version = "<new>"`.
4. `git diff pyproject.toml` — confirm exactly one line changed.
5. Propose a commit message (do not run `git commit`):

   ```
   chore(release): bump version to <new>
   ```

   Suggest the user run `/commit` (or `git commit -m '...' pyproject.toml`) when they're ready.

## Safety rails

- **Only** modify the `version` field. No description / license / dependency changes.
- Do not touch any other file (no CHANGELOG, no git tag, no push).
- Do not commit.
- If `version` is missing or unparseable, stop and ask the user.
