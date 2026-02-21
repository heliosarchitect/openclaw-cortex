# Repo map

This repo is a *workspace-style* repository. It contains both operational code and working artifacts.

## Top-level directories (high level)

- `cortex/` — Cortex-related code/config (memory, automation, glue).
- `scripts/` — runnable scripts and helpers.
- `runbooks/` — human runbooks / operational procedures.
- `docs/` — contributor-facing documentation.
- `analysis/` — investigations, results, and one-off research.
- `archive/` — historical snapshots and older artifacts.
- `skills/` — OpenClaw skills bundled in-tree.
- `templates/` — templates for consistent docs/scripts.
- `data/` — local datasets and generated outputs (not all are meant to be committed forever).

## Key files

- `README.md` — the entry point
- `AGENTS.md` — agent operating rules and conventions
- `BEST_PRACTICES.md` — conventions and guardrails
- `BOOTSTRAP.md` — initial setup notes

## Contribution guideline

If you’re adding something new and aren’t sure where it goes:

1. Put it in `docs/` (if it’s explanation) or `scripts/` (if it’s executable).
2. Add one sentence to this file so the next person can find it.
