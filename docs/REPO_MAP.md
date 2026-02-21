# openclaw-cortex Repo Map (skeleton)

Purpose: make ownership boundaries obvious in under 2 minutes.

## Product Core (runtime-relevant)

| Path | Role | Notes |
|---|---|---|
| `memory/` | Cortex memory system, persistence, tooling | Primary system of record for agent memory operations |
| `scripts/` | Operational automation and checks | Health, hygiene, reporting, maintenance |
| `docs/` | Protocols and runbooks | SYNAPSE, recovery docs, contributor paths |
| `cortex/` | Supporting Cortex module/assets | Treat as core dependency surface |
| `config/` | Runtime configuration | Environment-specific details |

## Workspace Artifacts (non-core / historical / generated)

| Path/Pattern | Type | Guidance |
|---|---|---|
| `analysis/`, `reports/`, `archive/` | Research outputs + historical data | Useful reference; not required for core runtime bring-up |
| `*.log`, generated benchmark files | Generated outputs | Regenerate as needed; avoid coupling features to these |
| Ad hoc root files | Session artifacts | Prefer moving durable docs into `docs/` |

## Ownership Domains

- **Core Runtime:** `memory/`, `scripts/`, `config/`, `cortex/`
- **Operational Docs:** `docs/`
- **Historical/Exploratory:** `analysis/`, `reports/`, `archive/`, generated logs

## Contributor Routing

- Need to run/verify behavior? Start in **Product Core**.
- Need protocol/context? Start in **docs/**.
- Need prior experiments/evidence? Check **Workspace Artifacts**.

## Planned follow-ups (issue #13 alignment)

- Define stricter move/retention rules for root-level ad hoc files.
- Add `.gitignore` hardening pass for high-churn generated outputs.
- Introduce architecture map with explicit data flow links.

---

Status: incremental skeleton for issue #13/#14. Safe to extend.
