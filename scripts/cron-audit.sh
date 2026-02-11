#!/bin/bash
# Cron Audit Script — checks recent cron runs for failures
# Called during heartbeats to validate automation output
#
# Usage: bash scripts/cron-audit.sh [hours_back]
# Returns: 0 if all OK, 1 if issues found
# Output: JSON-ish summary suitable for LLM consumption

HOURS_BACK=${1:-6}
ISSUES=0
AUDIT_LOG="/tmp/cron-audit-$(date +%Y%m%d).log"

echo "=== Cron Audit $(date -Iseconds) ===" >> "$AUDIT_LOG"

# Expected minimum runtimes (seconds) for known cron jobs
# Format: JOB_ID:MIN_SECONDS:DESCRIPTION
declare -A EXPECTED_RUNTIMES=(
    ["52075e39"]="300:LLM Fleet Dev (10PM)"
    ["6aa4edc5"]="120:Reflection (11PM)"
    ["fe799b39"]="120:Reflection (midnight)"
    ["f683a04b"]="300:Self-improvement (4AM)"
)

echo "Cron Audit — checking last ${HOURS_BACK}h"
echo "---"

# Get cron job list and recent runs via OpenClaw API
# This script is meant to be called from within an agent session
# where cron tools are available. For standalone use, it outputs
# the checks that should be performed.

echo "CHECKS_NEEDED:"
echo "1. List all cron jobs: cron list"
echo "2. For each job, get last run: cron runs jobId=<id>"
echo "3. Flag if:"
echo "   - lastStatus = error or timeout"
echo "   - Runtime < expected minimum"
echo "   - No artifacts produced"
echo ""
echo "EXPECTED_RUNTIMES:"
for job_id in "${!EXPECTED_RUNTIMES[@]}"; do
    IFS=':' read -r min_sec desc <<< "${EXPECTED_RUNTIMES[$job_id]}"
    echo "  $job_id: min ${min_sec}s ($desc)"
done

echo "" >> "$AUDIT_LOG"
echo "Completed audit check" >> "$AUDIT_LOG"
