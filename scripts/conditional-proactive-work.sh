#!/bin/bash
# Conditional proactive work - only during productive hours and when tasks available
# Replaces wasteful 24/7 every-15min polling

LOGFILE="/tmp/proactive-work-$(date +%Y-%m-%d).log"
echo "$(date): Starting conditional proactive work check" >> "$LOGFILE"

# Only run during productive hours (9 AM - 11 PM EST)
current_hour=$(date +%H)
if [ "$current_hour" -lt 9 ] || [ "$current_hour" -ge 23 ]; then
    echo "$(date): Outside productive hours ($current_hour) - skipping" >> "$LOGFILE"
    exit 0
fi

# Check if Matthew is actively chatting (activity in last 30 min)
last_activity=$(stat -c %Y ~/.openclaw/workspace/memory/task-queue.md 2>/dev/null || echo 0)
current_time=$(date +%s)
minutes_since=$(( (current_time - last_activity) / 60 ))

if [ "$minutes_since" -lt 30 ]; then
    echo "$(date): Recent activity detected ($minutes_since min ago) - skipping to avoid interruption" >> "$LOGFILE"
    exit 0
fi

# Check if there are actual tasks in the queue
available_tasks=$(grep -c "^- \[ \]" ~/.openclaw/workspace/memory/task-queue.md 2>/dev/null || echo 0)
priority_tasks=$(grep -c "## Priority" ~/.openclaw/workspace/memory/task-queue.md 2>/dev/null || echo 0)

echo "$(date): Found $available_tasks available tasks, $priority_tasks priority items" >> "$LOGFILE"

# Only wake if there are tasks to work on
if [ "$available_tasks" -gt 0 ] || [ "$priority_tasks" -gt 0 ]; then
    echo "$(date): WAKE TRIGGERED - Tasks available for proactive work" >> "$LOGFILE"
    
    # Write alert flag for consolidator
    mkdir -p /tmp/helios-alerts
    echo "PROACTIVE WORK: $available_tasks tasks available, $priority_tasks priority items - productive work session" > /tmp/helios-alerts/proactive-work-alert
    echo "$(date): Alert flag written" >> "$LOGFILE"
else
    echo "$(date): No tasks available for proactive work" >> "$LOGFILE"
fi