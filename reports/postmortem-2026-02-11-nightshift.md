# Incident Post-Mortem — NIGHT-001

**Date:** 2026-02-11
**Severity:** P2
**Service:** Helios Night Shift (heartbeat loop + cron automation)
**Duration:** 2026-02-11 04:00 EST → 2026-02-11 06:45 EST (2h 45m)

## Summary
Helios spent 2.5 hours cycling HEARTBEAT_OKs and performing redundant low-value checks (earthquake monitoring, email re-reads, ClawHub browsing) while cron-spawned sessions silently failed or completed in milliseconds. No productive work was accomplished between 04:00–06:45 EST.

## Timeline
| Time (EST) | Event |
|------------|-------|
| 22:00 Feb 10 | LLM Fleet Dev cron fires (52075e39), spawns sub-agent |
| 22:00 Feb 10 | Main session sees 24s runtime, assumes failure — does not investigate |
| 22:06 Feb 10 | Sub-agent actually completes successfully (6m31s, builds 3 models, fixes 3) |
| 23:00 Feb 10 | Reflection cron fires (6aa4edc5) — runs <10ms, no output |
| 00:00 Feb 11 | Reflection cron fires (fe799b39) — runs <10ms, no output |
| 04:00 Feb 11 | Self-improvement cron fires (f683a04b) — runs 112s, unclear output |
| 04:00–06:45 | Heartbeat loop: earthquake check → email check → earthquake check → email check → Moltbook → ClawHub → repeat |
| 06:45 | Matthew wakes, identifies the pattern |
| 07:35 | Helios finally builds something (LLM fleet smoke test) |

## Impact
- **Data lost:** None
- **Money lost:** ~$2-4 in API costs (Opus tokens on empty heartbeat cycles)
- **Downtime:** 2h 45m of zero productive output
- **Cascading failures:** Tasks that could have been completed overnight now compete with daytime work

## Root Cause
Two independent failures compounding:

1. **No cron output validation.** Sessions fire-and-forget. The 10PM session appeared to fail (24s in main session view) but the sub-agent actually completed successfully. The 11PM and midnight sessions ran for milliseconds with no output — nobody checked.

2. **No idle-state mandate.** HEARTBEAT.md allowed unlimited consecutive HEARTBEAT_OKs. When nothing was broken, the system defaulted to trivial monitoring checks (same earthquakes, same emails) instead of productive work. There was no task queue to pull from.

The pattern: *checking the same thing repeatedly with no change, while real work sits undone.*

## Fix Applied

### Fix 1: Anti-idle heartbeat mandate
HEARTBEAT.md rewritten with build-by-default mode, max 2 consecutive HEARTBEAT_OKs.
```
# Added to HEARTBEAT.md:
## 🔨 Default Mode: BUILD
When all systems green, pull from `memory/task-queue.md` and execute.
**Never cycle more than 2 consecutive HEARTBEAT_OKs.** On the 3rd, pick a task.
```
Commit: `136be5f` — fix: anti-idle heartbeat system - task queue, cron audit, build mandate

### Fix 2: Persistent task queue
Created `memory/task-queue.md` — prioritized list of build tasks that heartbeats pull from when idle.
Commit: `136be5f`

### Fix 3: Cron output validation
Created `scripts/cron-audit.sh` — executable script that checks recent cron runs for:
- Sessions under expected minimum runtime
- Sessions with error status
- Sessions that produced no artifacts
Integrated into heartbeat loop.
Commit: `{pending}`

## Prevention
- [x] Constraint added: **NO more than 2 consecutive HEARTBEAT_OKs** — must build on 3rd
- [x] Task queue created: persistent build list at `memory/task-queue.md`
- [x] Cron audit script: `scripts/cron-audit.sh` checks session outputs every heartbeat
- [x] Documentation updated: HEARTBEAT.md, cron-audit.md
- [ ] Expected runtime metadata added to cron job descriptions

## Lessons Learned
1. **Fire-and-forget is silent failure.** Any automated system needs output validation. "Did it run?" is not the same as "did it produce results?"
2. **Idle loops are expensive.** Each HEARTBEAT_OK costs tokens and time. If the system is healthy, the correct action is to build, not to confirm health again.
3. **Redundant checks are a smell.** Checking the same 5 emails 4 times in 3 hours is a signal that the heartbeat logic needs a task to do instead.
4. **Appearances deceive.** The 10PM session looked like a 24s failure from the main session's perspective. The sub-agent actually completed successfully with significant output. Always check the sub-agent's own transcript.

---
*Template: lbf-templates/reports/postmortem.md*
