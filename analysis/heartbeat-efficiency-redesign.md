# Heartbeat Efficiency Redesign — H0-7

## Problem Statement

OpenClaw heartbeats fire every 30 minutes regardless of whether anything needs attention. Each heartbeat loads the full system prompt, workspace files, memory context (~2,200 tokens from Cortex), and conversation history. Most end in `HEARTBEAT_OK` — pure waste.

## Current State (Baseline)

- **Frequency**: Every 30 minutes (config: `agents.defaults.heartbeat.every: "30m"`)
- **Model**: `claude-sonnet-4-20250514` (Sonnet — cheaper than main Opus session)
- **Per-heartbeat cost estimate**:
  - System prompt + workspace files: ~4,000 tokens
  - Memory injection (Cortex): ~2,200 tokens (H0-5 measured)
  - Conversation history/summary: ~2,000-5,000 tokens
  - HEARTBEAT.md instructions: ~300 tokens
  - Output (HEARTBEAT_OK or work): ~50-2,000 tokens
  - **Total input per heartbeat: ~8,500-11,500 tokens**
  - At Sonnet pricing ($3/M input, $15/M output): ~$0.03-0.04 per heartbeat
- **Daily cost**: 48 heartbeats × ~$0.035 = **~$1.68/day** on heartbeats alone
- **Waste rate**: Estimate 60-70% of heartbeats are HEARTBEAT_OK (no action taken)
- **Wasted daily**: ~$1.00-1.18/day

## Proposed Architecture: Event-Driven + Scheduled

### Tier 1: Eliminate idle heartbeats (saves 30-50%)
Replace fixed-interval heartbeats with:
1. **Cron jobs for scheduled work** — Email checks, AUGUR EOD, world events get their own cron schedules. These fire only when needed and carry minimal context.
2. **Disable heartbeat entirely** when no active tasks are queued. Re-enable when work is dispatched.

### Tier 2: Reduce per-heartbeat cost (saves 10-20%)
3. **H0-5 token budget reduction** — Cut memory injection from 2,200 to 800 tokens (already designed).
4. **Lightweight triage model** — Route heartbeats to a cheaper/local model for the "anything happening?" check. Only escalate to Sonnet when there's actual work.

### Tier 3: Smart scheduling (saves 5-15%)
5. **Adaptive frequency** — When active tasks exist, heartbeat at 15min. When idle, 2hr or off.
6. **Sub-agent completion events** — Instead of polling for Nova results, sub-agents write to synapse/file. Next natural wake (user message or cron) picks it up.

## Implementation Plan

### Phase A: Measure (Nova task)
- Instrument heartbeat outcomes: count HEARTBEAT_OK vs productive heartbeats
- Parse recent session history to establish actual waste rate
- Calculate precise per-heartbeat token usage from session logs
- Produce baseline report with exact $/day numbers

### Phase B: Cron Migration (Nova task)
- Audit HEARTBEAT.md for all scheduled activities
- Create individual cron jobs for each:
  - Email check: every 30min → `cron` job with `systemEvent`
  - World events: every 30min → `cron` job
  - AUGUR EOD: daily 23:00 → `cron` job
  - Sub-agent check: event-driven (synapse), not polled
- Each cron job carries ONLY the context needed for that specific task

### Phase C: Config Change
- Increase heartbeat interval to 2hr (or disable)
- Apply H0-5 memory budget reduction (800 tokens)
- Test for 24hrs, measure savings

## Expected Savings

| Change | Savings | Confidence |
|--------|---------|------------|
| Eliminate idle heartbeats via cron migration | 30-50% | High |
| H0-5 memory budget (2200→800 tokens) | 10-15% | Very High |
| Adaptive frequency (active vs idle) | 5-10% | Medium |
| **Combined** | **45-65%** | Medium-High |

Conservative estimate: **$0.75-1.10/day saved** from heartbeat optimization alone.
Percentage of total heartbeat spend: **45-65%** (exceeds the 5-50% target).

## Deliverables
1. `analysis/heartbeat-baseline-report.md` — measured current waste
2. `analysis/heartbeat-cron-migration.md` — cron job specs for each scheduled task
3. Recommended config changes with before/after projections
4. Implementation script or ready-to-apply config patch
