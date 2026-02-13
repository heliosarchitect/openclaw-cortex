#!/bin/bash
# WEMS Cron Wrapper — runs monitor, only wakes Helios on new events
# Install: crontab -e → */15 * * * * ~/.openclaw/workspace/scripts/wems-cron-wrapper.sh

SCRIPT="$HOME/.openclaw/workspace/scripts/wems-monitor.sh"
OUTPUT=$("$SCRIPT" iran-pakistan 4.5 1 2>/dev/null)

if [ -n "$OUTPUT" ]; then
  # New earthquake activity detected — wake Helios
  openclaw cron wake --text "🌍 WEMS ALERT (Iran/Pakistan):\n${OUTPUT}\n\nAlert Matthew if 5.5+ or tsunami potential." --mode now 2>/dev/null || true
fi
