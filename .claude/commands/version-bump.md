---
description: Bump the package version in pyproject.toml (patch | minor | major), date its CHANGELOG section, and suggest the release commit message and tag.
allowed-tools: Read, Edit, Bash(git diff:*)
argument-hint: patch | minor | major
---

# `/version-bump` — bump pyproject.toml version

Edits `[project] version` in `pyproject.toml` using semver, and dates the matching `CHANGELOG.md` section (the publish workflow sends that section to the registry as the version's changelog).

## Workflow

1. Read current `version` from `pyproject.toml` (e.g. `1.0.13`).
2. Parse `$ARGUMENTS`:
   - `patch` → bump the third number (`1.0.13` → `1.0.14`).
   - `minor` → bump the second, reset patch (`1.0.13` → `1.1.0`).
   - `major` → bump the first, reset minor + patch (`1.0.13` → `2.0.0`).
   - If missing or invalid: ask once.
3. Edit `pyproject.toml`:
   - `version = "<old>"` → `version = "<new>"`.
4. Edit `CHANGELOG.md`:
   - `## [Unreleased]` → `## [<new>] — <today, YYYY-MM-DD>`.
   - If there is no `## [Unreleased]` section, warn the user: the registry will show no changelog for `<new>`.
5. `git diff pyproject.toml CHANGELOG.md` — confirm exactly one line changed in each.
6. Propose the commit message and the tag (do not run `git commit` or `git tag`):

   ```
   chore(release): bump version to <new>
   ```

   Suggest the user run `/commit` (or `git commit -m '...' pyproject.toml CHANGELOG.md`), then tag that commit with `git tag -a v<new> -m "v<new>"` and push both with `git push --follow-tags`.

## Safety rails

- **Only** modify the `version` field and the CHANGELOG heading. No description / license / dependency changes.
- Do not touch any other file (no git tag, no push).
- Do not commit.
- If `version` is missing or unparseable, stop and ask the user.
