#!/bin/bash
# Alert watcher — runs from system crontab every 5 minutes
# Only wakes OpenClaw when there are actual alerts (no-op otherwise)

RESULT=$(/home/bonsaihorn/.openclaw/workspace/scripts/alert-consolidator.sh 2>/dev/null)

if [ "$RESULT" = "HEARTBEAT_OK" ]; then
    exit 0  # Nothing to report, don't wake OpenClaw
fi

# There are alerts — wake OpenClaw via the cron wake API
curl -sf -X POST http://127.0.0.1:18789/api/cron/wake \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"$RESULT\", \"mode\": \"now\"}" \
  >/dev/null 2>&1
