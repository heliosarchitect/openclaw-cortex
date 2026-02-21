# Quickstart (5 minutes)

This quickstart is written for someone who just cloned the repo and wants to understand what it is *without* reading the whole codebase.

## 1) What this repo is

This is a working repo that includes both **operational code** (things you actually run) and **workspace artifacts** (notes, analysis, experiments).

If you only want to contribute docs or small utilities, you can do that without understanding every subfolder.

## 2) Basic orientation

- Start here: `docs/REPO_MAP.md`
- Then skim: `AGENTS.md`, `BEST_PRACTICES.md`

## 3) Run something safe (no credentials)

Pick a read-only script first:

```bash
python3 -c "print('hello from openclaw-cortex')"
```

(We intentionally keep the quickstart low-risk; many scripts in this repo are operational.)

## 4) When you *do* need credentials

Some automation will require API keys / OAuth / local secrets.

Rule: **do not commit secrets**. Put them in your environment or in your local secrets manager.

## 5) What to do next

- Want to contribute structure/docs? Open a PR improving `docs/REPO_MAP.md`.
- Want to contribute code? Pick one issue and ship a minimal vertical slice.
