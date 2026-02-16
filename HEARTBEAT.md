# HEARTBEAT.md

**Default: HEARTBEAT_OK.** Only act if something needs attention.

## Do NOT poll on every heartbeat
System health, CI, synapse, sessions — these are checked by external scripts.
Only investigate if a script ALERTS you (via cron systemEvent or n8n webhook).

## When to act (not routine — only if triggered)
1. Matthew messages → respond immediately
2. System alert injected → investigate and fix
3. Context > 75% → message Matthew: "⚠️ Context at X% — /new soon"
4. **Broken service requiring human action** → escalate to Matthew IMMEDIATELY (don't sit on it)
   - Examples: expired OAuth tokens, failed backups, broken integrations needing credentials
   - If I can't fix it myself and it's blocking functionality, TELL MATTHEW NOW
   - **Detection should happen via n8n/cron scripts, NOT heartbeat polling** — only act when alerted

## When NOT to act
- Don't run system-health-check.sh (cron handles this)
- Don't check sessions_list (only if alerted)
- Don't check synapse inbox (only if alerted)
- Don't check GitHub CI (only if alerted)
- Don't poll the same thing twice

## BUILD mode
If idle for >2 consecutive heartbeats AND no alerts, pull from `memory/task-queue.md`.
