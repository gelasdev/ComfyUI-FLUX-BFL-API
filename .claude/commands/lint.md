---
description: Run ruff format + ruff check --fix across the project using the pyproject.toml configuration. Reports what changed.
disable-model-invocation: true
allowed-tools: Bash(ruff:*), Bash(git diff:*), Bash(git status:*)
---

# `/lint` — ruff format + check across the project

Runs the project's ruff configuration (`pyproject.toml` `[tool.ruff]`) once, fixes what it can, surfaces what it can't.

## Workflow

1. `command -v ruff >/dev/null` — if ruff is not on PATH, tell the user to `pip install -e .[dev]` (or `pip install ruff`) and stop.
2. `ruff format .` — auto-format.
3. `ruff check --fix .` — auto-fix lint rules in the selected set (E, F, I, W, UP, B).
4. `git status -s` — show files ruff changed.
5. If ruff reported diagnostics it could **not** fix, list them. The user decides whether to address now or skip.

## Safety rails

- Do not commit. The user runs `/commit` if they want to keep the formatting changes.
- Do not add or remove rules from `pyproject.toml` `[tool.ruff.lint]` `select` — that's a separate, explicit decision.
- Do not run with `--no-cache` or other non-default flags unless the user asks.
