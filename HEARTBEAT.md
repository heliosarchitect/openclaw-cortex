# HEARTBEAT.md - Living Checklist

**Philosophy:** Event-driven, not polling. When nothing's broken, BUILD.

## 🔥 Priority: Respond & Fix
- Matthew messages → respond immediately
- Something breaks → fix it
- Interesting discovery → share it

## 🔨 Default Mode: BUILD
When all systems green, pull from `memory/task-queue.md` and execute.
**Never cycle more than 2 consecutive HEARTBEAT_OKs.** On the 3rd, pick a task.

## 🔍 Cron Audit (every heartbeat)
Check recent cron/sub-agent sessions for failures:
```
sessions_list with activeMinutes filter, check for:
- Sessions that ran < 60 seconds (likely crashed)
- Sessions with no tool calls (empty runs)
- Sessions that didn't produce artifacts
```
If found: investigate and log, don't silently pass.

## ⚡ What I Don't Poll
- ~~CPU temp~~ (only at 100% load)
- ~~Same emails repeatedly~~ (check once per 30min max, stop if unchanged)
- ~~Earthquake feed~~ (only when world events cron fires)
- ~~Moltbook karma~~
- ~~AUGUR health~~ (self-monitoring built in)

**Rule:** If checking the same thing repeatedly with no change, STOP and BUILD instead.

---
*Last evolved: 2026-02-11 08:17 - Added task queue, cron audit, anti-idle mandate*
