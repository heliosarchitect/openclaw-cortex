#!/bin/bash
# wazuh-alerts-cron.sh — Cron wrapper for Wazuh-to-Discord alerting
# Suggested crontab entry (every 6 hours):
#   0 */6 * * * /home/bonsaihorn/.openclaw/workspace/scripts/wazuh-alerts-cron.sh >> /tmp/wazuh-alerts.log 2>&1
#
# Or daily at 8am:
#   0 8 * * * /home/bonsaihorn/.openclaw/workspace/scripts/wazuh-alerts-cron.sh >> /tmp/wazuh-alerts.log 2>&1

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="/tmp"

echo "=== Wazuh Alert Check: $(date -Iseconds) ==="

python3 "${SCRIPT_DIR}/wazuh-alerts.py"
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo "WARNING: Script exited with code $EXIT_CODE"
fi

echo "=== Done ==="
