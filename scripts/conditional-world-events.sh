#!/bin/bash
# Conditional world events check - only wakes Helios if significant events
# Replaces wasteful every-30min polling

LOGFILE="/tmp/world-events-$(date +%Y-%m-%d).log"
echo "$(date): Starting conditional world events check" >> "$LOGFILE"

wake_needed=false
alert_text=""

# Check earthquakes 4.5+ in last hour
eq_data=$(curl -s "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_hour.geojson" 2>/dev/null)
eq_count=$(echo "$eq_data" | jq -r '.metadata.count // 0' 2>/dev/null)

if [ "$eq_count" = "null" ] || [ -z "$eq_count" ]; then
    eq_count=0
fi

echo "$(date): Found $eq_count earthquakes 4.5+" >> "$LOGFILE"

# Check for 6.0+ earthquakes (immediate alert threshold)  
if [ "$eq_count" -gt 0 ]; then
    significant_eq=$(echo "$eq_data" | jq -r '.features[] | select(.properties.mag >= 6.0) | .properties.mag' 2>/dev/null | wc -l)
    
    if [ "$significant_eq" -gt 0 ]; then
        wake_needed=true
        max_mag=$(echo "$eq_data" | jq -r '.features[] | .properties.mag' 2>/dev/null | sort -nr | head -1)
        location=$(echo "$eq_data" | jq -r '.features[0].properties.place' 2>/dev/null)
        alert_text="🚨 EARTHQUAKE ALERT: ${max_mag} magnitude quake in ${location}"
        echo "$(date): SIGNIFICANT EARTHQUAKE: $max_mag" >> "$LOGFILE"
    fi
fi

# TODO: Add crypto price movement check (>5% moves)
# TODO: Add severe weather warnings for Virginia

# Fire wake event if needed
if [ "$wake_needed" = true ]; then
    echo "$(date): WAKE TRIGGERED - $alert_text" >> "$LOGFILE"
    
    export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    # Write alert flag for consolidator
    mkdir -p /tmp/helios-alerts
    echo "$alert_text" > /tmp/helios-alerts/world-events-alert
    echo "$(date): Alert flag written" >> "$LOGFILE"
else
    echo "$(date): No significant events detected" >> "$LOGFILE"
fi