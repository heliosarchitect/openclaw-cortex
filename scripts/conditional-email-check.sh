#!/bin/bash
# Conditional email check - only wakes Helios if action needed
# Replaces wasteful every-30min polling

LOGFILE="/tmp/email-check-$(date +%Y-%m-%d).log"
echo "$(date): Starting conditional email check" >> "$LOGFILE"

# Check for unread emails
unread_output=$(gog gmail search 'is:unread' --account heliosarchitectlbf@gmail.com --max 5 2>/dev/null)
unread_count=$(echo "$unread_output" | grep -c "^[0-9a-f]")

# Check for high-priority keywords
priority_keywords="stripe|payment|customer|urgent|action required|security|error|down"
has_priority=$(echo "$unread_output" | grep -iE "$priority_keywords" | wc -l)

echo "$(date): Found $unread_count unread emails, $has_priority priority" >> "$LOGFILE"

# Only wake if there are priority emails or 5+ unread (possible backlog)
if [ "$has_priority" -gt 0 ] || [ "$unread_count" -ge 5 ]; then
    echo "$(date): WAKE TRIGGERED - Priority: $has_priority, Count: $unread_count" >> "$LOGFILE"
    
    # Write alert flag for consolidator
    mkdir -p /tmp/helios-alerts
    echo "EMAIL: $unread_count unread emails, $has_priority priority items requiring attention" > /tmp/helios-alerts/email-alert
    echo "$(date): Alert flag written" >> "$LOGFILE"
else
    echo "$(date): No action needed - routine emails only" >> "$LOGFILE"
fi