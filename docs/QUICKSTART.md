# openclaw-cortex Quickstart (5 minutes)

This guide is for external contributors who need a reliable first run path.

## 1) Clone and inspect

```bash
git clone https://github.com/heliosarchitect/openclaw-cortex.git
cd openclaw-cortex
```

## 2) Identify product core vs workspace artifacts

Use the repo map first:

- [`docs/REPO_MAP.md`](./REPO_MAP.md)

Product runtime focus (start here):

- `memory/` (Cortex memory + tools)
- `scripts/` (operational automation)
- `docs/` (protocols/runbooks)

Workspace artifacts (do not treat as runtime dependencies) include historical analysis outputs, logs, and ad hoc research files at repo root.

## 3) Run a safe verification path

```bash
# memory health snapshot
python memory/cortex_cli.py stats

# optional maintenance dry-run style checks
./scripts/system-health-check.sh
```

If a command is missing dependencies, install only what that command requests instead of broad environment changes.

## 4) First docs to read

- [`README.md`](../README.md)
- [`docs/REPO_MAP.md`](./REPO_MAP.md)
- [`docs/SYNAPSE_V2.md`](./SYNAPSE_V2.md)
- [`docs/BC_DR.md`](./BC_DR.md)

## Troubleshooting (common)

- **`python: can't open file memory/cortex_cli.py`**
  - Confirm you are in repo root: `pwd` should end with `openclaw-cortex`.
- **Permission denied on scripts**
  - Run with bash: `bash ./scripts/system-health-check.sh`.
- **Missing local env/tooling**
  - Start with read-only/status commands first; avoid changing runtime config unless required by your task.

---

Semver/doc intent: additive documentation only (no runtime behavior changes).
