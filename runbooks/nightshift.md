# Helios Night Shift — Operational Runbook

## Services

### Heartbeat Loop
- **Check:** Active session in `sessions_list`
- **Active hours:** 23:00–08:00 EST (while Matthew sleeps)
- **Cycle:** 15-45 min depending on cron config
- **Kill switch:** Matthew sends "stop" or gateway restart

### Cron Jobs
- **Check:** `cron list`
- **Logs:** `cron runs jobId=<id>`
- **Start/Stop:** `cron update jobId=<id> patch={"enabled": true/false}`

| Job ID | Schedule | Purpose | Status |
|--------|----------|---------|--------|
| 52075e39 | 10 PM ET | LLM Fleet Dev | DISABLED |
| 6aa4edc5 | 11 PM ET | Reflection | DISABLED |
| fe799b39 | Midnight ET | Reflection | DISABLED |
| f683a04b | 4 AM ET | Self-improvement | ACTIVE |

## Common Procedures

### Start of Night Shift
1. Read HEARTBEAT.md
2. Check `memory/task-queue.md` for pending tasks
3. Run cron audit on any recent runs (see `scripts/cron-audit.md`)
4. Pick first task if nothing needs fixing

### Heartbeat Decision Tree
```
Matthew message? → Respond immediately
Something broken? → Fix it
Cron ran recently? → Audit output (scripts/cron-audit.md)
< 2 consecutive OKs? → HEARTBEAT_OK
≥ 2 consecutive OKs? → Pull task from memory/task-queue.md
```

### Emergency Stop
```bash
# Stop all cron jobs
# Via tool: cron update jobId=<id> patch={"enabled": false}

# Stop heartbeat
# Send HEARTBEAT_OK and don't schedule next (gateway handles)
```

### Check Health
```bash
# Services
systemctl --user status paper-augur enhanced-collector openclaw-gateway

# Databases
sqlite3 ~/Projects/augur-collector/enhanced_data.db "SELECT COUNT(*) FROM trade_flow"
sqlite3 ~/Projects/augur-trading/augur_signals.db "SELECT COUNT(*) FROM signals"

# GPU
nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total --format=csv,noheader

# Ollama
curl -s http://localhost:11434/api/ps | python3 -m json.tool
```

## Troubleshooting

### Heartbeat cycling with no productive output
- **Symptom:** 3+ consecutive HEARTBEAT_OKs, no file changes or commits
- **Cause:** No task queue, or all tasks blocked
- **Fix:** Pull from `memory/task-queue.md`. If all blocked, add new tasks or explore.

### Cron session runs for < 10 seconds
- **Symptom:** Session completes almost instantly, no artifacts
- **Cause:** Empty/bad prompt, session timeout too short, or model error
- **Fix:** Check `sessions_history` for the session. Verify prompt text in cron config. Check model availability.

### Sub-agent appears to fail but actually succeeded
- **Symptom:** Main session sees short runtime, but sub-agent ran longer
- **Cause:** `sessions_spawn` returns quickly; sub-agent runs asynchronously
- **Fix:** Always check sub-agent session directly via `sessions_history`, not just the spawn call duration.

### Same check repeated with no change
- **Symptom:** Checking same emails/earthquakes/status 3+ times
- **Cause:** No state tracking between heartbeats
- **Fix:** If result unchanged after 2 checks, STOP and BUILD. Track last-checked timestamps.

## Escalation

| Tier | Action | Who |
|------|--------|-----|
| 0 | Self-fix (restart service, re-run task) | Helios |
| 1 | Log to daily notes, continue working | Helios |
| 2 | Alert via Signal if data/money at risk | Matthew |
| 3 | Stop all automated actions, wait for direction | Matthew |

### What triggers each tier
- **Tier 0:** Service restart, transient error, single cron failure
- **Tier 1:** Repeated minor issues, performance degradation
- **Tier 2:** Data loss risk, money at risk, security event, 3+ cascade failures
- **Tier 3:** Unclear situation with potential for harm

## Monitoring

| Metric | Source | Alert Threshold |
|--------|--------|-----------------|
| Consecutive HEARTBEAT_OKs | Heartbeat loop | > 2 (must build) |
| Cron session runtime | `cron runs` | < expected minimum |
| Task queue depth | `memory/task-queue.md` | 0 tasks available |
| GPU memory | nvidia-smi | > 30GB (model stuck) |
| Collector status | systemd | inactive during 8:30-18:30 ET |

---
*Template: lbf-templates/project/RUNBOOK.md*
*Created: 2026-02-11 — post NIGHT-001 incident*
