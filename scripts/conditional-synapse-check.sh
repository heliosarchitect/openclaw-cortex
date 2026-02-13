#!/bin/bash
# Conditional synapse check - only wakes Helios for action/urgent messages
# Filters out "info" priority messages (Nova chatter)

LOGFILE="/tmp/synapse-check-$(date +%Y-%m-%d).log"
echo "$(date): Starting conditional synapse check" >> "$LOGFILE"

# Check synapse inbox via brain CLI
inbox_output=$(~/bin/brain inbox --agent helios 2>/dev/null)
message_count=$(echo "$inbox_output" | jq -r '.count // 0' 2>/dev/null)

if [ "$message_count" = "null" ] || [ -z "$message_count" ]; then
    message_count=0
fi

echo "$(date): Found $message_count messages in synapse inbox" >> "$LOGFILE"

# Filter for action/urgent priority only
if [ "$message_count" -gt 0 ]; then
    action_messages=$(echo "$inbox_output" | jq -r '.messages[] | select(.priority == "action" or .priority == "urgent") | .id' 2>/dev/null | wc -l)
    
    if [ "$action_messages" -gt 0 ]; then
        # Get the subjects of action items
        subjects=$(echo "$inbox_output" | jq -r '.messages[] | select(.priority == "action" or .priority == "urgent") | .subject' 2>/dev/null | head -3 | tr '\n' '; ')
        
        echo "$(date): WAKE TRIGGERED - $action_messages action items: $subjects" >> "$LOGFILE"
        
        # Write alert flag for consolidator
        mkdir -p /tmp/helios-alerts
        echo "SYNAPSE: $action_messages action items requiring attention: $subjects" > /tmp/helios-alerts/synapse-alert
        echo "$(date): Alert flag written" >> "$LOGFILE"
    else
        echo "$(date): Only info messages found - no wake needed" >> "$LOGFILE"
    fi
else
    echo "$(date): No synapse messages" >> "$LOGFILE"
fi