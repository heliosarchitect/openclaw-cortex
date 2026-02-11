# Cron Audit Procedure — Operational Runbook

## When to Run
Every heartbeat, as specified in HEARTBEAT.md § Cron Audit.

## Steps

### 1. List recent cron runs
```
cron list → get all active job IDs
For each job: cron runs jobId=<id> → check lastRun
```

### 2. Check for failures
Flag any job where:
- `lastStatus` = "error" or "timeout"
- Runtime < expected minimum (see table below)
- Session produced no tool calls or artifacts

### 3. Expected Runtimes
| Job ID | Cron | Expected Min | Purpose |
|--------|------|-------------|---------|
| 52075e39 | 10 PM ET | 300s | LLM Fleet Dev (DISABLED) |
| 6aa4edc5 | 11 PM ET | 120s | Reflection (DISABLED) |
| fe799b39 | midnight ET | 120s | Reflection (DISABLED) |
| f683a04b | 4 AM ET | 300s | Self-improvement |

### 4. If failure detected
1. Pull session history: `sessions_history sessionKey=<key>`
2. Determine root cause:
   - Did the session start? (check for any tool calls)
   - Did it crash? (check error messages)
   - Did it produce output? (check for file writes, commits)
3. Log finding in `memory/YYYY-MM-DD.md`
4. Fix if possible (restart, adjust config)
5. Alert Matthew if: data loss, repeated failures, or unfixable

### 5. Success criteria
A cron run is "successful" if ALL of:
- Runtime >= expected minimum
- At least 1 tool call executed
- No error status
- Produced at least 1 artifact (file change, commit, memory entry, or meaningful log)

## Escalation

| Tier | Condition | Action |
|------|-----------|--------|
| 0 | Single run < expected time | Log, investigate next heartbeat |
| 1 | 2+ consecutive failures | Investigate immediately, check config |
| 2 | Same job fails 3+ times | Disable job, log postmortem, alert Matthew |

---
*Template: lbf-templates/project/RUNBOOK.md (adapted)*
