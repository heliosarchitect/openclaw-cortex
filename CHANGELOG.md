# Helios Workspace Changelog

## ⛔ CONSTRAINTS — What NOT To Do

*Every constraint has a scar behind it. Remove only when the underlying system changes make them obsolete.*

### Heartbeat Constraints
- **NO more than 2 consecutive HEARTBEAT_OKs** — Must pull from task queue on 3rd cycle. Wasted 2.5 hours cycling idle checks (NIGHT-001, 2026-02-11).
- **NO redundant monitoring checks** — If the same check returns the same result twice, stop checking and BUILD instead. Checked same 5 emails 4 times in one shift.
- **NO fire-and-forget cron** — Every cron session must be audited for output. "Did it run?" ≠ "Did it produce results?" (NIGHT-001).

### Safety Constraints
- **NO deleting files without archiving** — Use `trash` or `mv` to archive, never `rm` on user data.
- **NO public actions without confirmation** — Tweets, emails to external humans, public posts require Matthew's go-ahead unless pre-authorized.

---

## v0.2.0 - "Night Watch" (2026-02-11)

### ⛔ New Constraints
- **NO more than 2 consecutive HEARTBEAT_OKs** — build on 3rd cycle
- **NO redundant monitoring checks** — stop and build if unchanged
- **NO fire-and-forget cron** — audit every session output

### New Features
- **NEW**: Task queue system — `memory/task-queue.md` with prioritized build tasks
- **NEW**: Cron audit procedure — `scripts/cron-audit.md` with expected runtimes and escalation tiers
- **NEW**: Night shift runbook — `runbooks/nightshift.md` with decision tree, troubleshooting, and monitoring
- **NEW**: LLM Fleet API smoke test — `~/Projects/llm-fleet/scripts/smoke-test-api.sh` (16/16 pass)
- **NEW**: AUGUR V4.1 "Speed" — taker-only execution, 0.5s poll (was 10s), sub-1s market response

### Bug Fixes
- **FIX**: HEARTBEAT.md rewritten — was purely event-driven with no idle-state mandate → now build-by-default with max 2 consecutive OKs
- **FIX**: Cron output validation — sessions were fire-and-forget → now audited every heartbeat with expected runtime thresholds

### Cron Cleanup
- **DISABLED**: Trading Manager (old Chad system, firing every 5min for nothing)
- **DISABLED**: Fine-tune dataset builder (same old system)
- **DISABLED**: Weekly pair updater (referenced `Chad_Volume_tracker`)
- **UPDATED**: Trading Day Start/End → AUGUR V4 with mid-cap focus, LONG only
- **FIXED**: Night shift cron restricted to 23:00-07:00 (was 24/7)

### Key Commits
- `136be5f` — fix: anti-idle heartbeat system - task queue, cron audit, build mandate
- `325f2ba` — docs: NIGHT-001 postmortem, night shift runbook, changelog, cron audit
- `329e2c3` — docs: log cron audit and remediation work
- `3d4f3d5` — feat: add API-based smoke test, first full quality run (16/16 pass)
- `bf5a1a9` — perf: taker-only execution, 0.5s poll interval (augur-trading)

### Lessons Learned
See `reports/postmortem-2026-02-11-nightshift.md` for full incident analysis.
Core lesson: automation without validation is just the illusion of productivity.

---

## v0.1.0 - "Bootstrap" (2026-02-09)

### New Features
- Initial workspace setup
- SOUL.md, IDENTITY.md, USER.md, MEMORY.md
- Cortex memory system (STM + embeddings + atoms)
- H0 Phase 0: file trimming (~5,200 tokens/turn saved)
- Ansible fleet management
- AUGUR signal mining infrastructure

---
*Template: lbf-templates/project/CHANGELOG.md*
