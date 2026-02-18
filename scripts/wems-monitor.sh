#!/bin/bash
# WEMS Monitor — lightweight earthquake region watch
# Runs via cron, costs zero tokens. Only wakes Helios when threshold triggers.
#
# Usage: wems-monitor.sh [--region NAME] [--min-mag N] [--hours N]
# Default: Iran/Pakistan region, 4.5+ magnitude, last 1 hour

REGION="${1:-iran-pakistan}"
MIN_MAG="${2:-4.5}"
HOURS="${3:-1}"

# Region bounding boxes (minlat,maxlat,minlon,maxlon)
case "$REGION" in
  iran-pakistan)  BBOX="24,40,44,70" ;;
  pacific-ring)  BBOX="-60,60,100,180" ;;
  caribbean)     BBOX="10,25,-90,-58" ;;
  virginia)      BBOX="36,40,-84,-75" ;;
  *)             echo "Unknown region: $REGION"; exit 1 ;;
esac

IFS=',' read -r MINLAT MAXLAT MINLON MAXLON <<< "$BBOX"

STATE_FILE="/tmp/wems-last-seen-${REGION}.txt"
touch "$STATE_FILE" 2>/dev/null

# Query USGS
FEED=$(curl -sf "https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&minmagnitude=${MIN_MAG}&minlatitude=${MINLAT}&maxlatitude=${MAXLAT}&minlongitude=${MINLON}&maxlongitude=${MAXLON}&orderby=time&limit=5&starttime=$(date -u -d "${HOURS} hours ago" +%Y-%m-%dT%H:%M:%S)")

if [ -z "$FEED" ]; then
  exit 0  # Silent fail — no tokens wasted
fi

COUNT=$(echo "$FEED" | jq '.metadata.count // 0')

if [ "$COUNT" -eq 0 ]; then
  exit 0  # Nothing to report
fi

# Check for new events we haven't seen
NEW_EVENTS=""
while IFS= read -r line; do
  ID=$(echo "$line" | jq -r '.id')
  MAG=$(echo "$line" | jq -r '.properties.mag')
  PLACE=$(echo "$line" | jq -r '.properties.place')
  TIME=$(echo "$line" | jq -r '.properties.time / 1000 | strftime("%H:%M UTC")')
  TSUNAMI=$(echo "$line" | jq -r '.properties.tsunami')
  
  # Skip if already seen
  if grep -qF "$ID" "$STATE_FILE" 2>/dev/null; then
    continue
  fi
  
  # Record as seen
  echo "$ID" >> "$STATE_FILE"
  
  # Build alert
  ALERT="🌍 M${MAG} — ${PLACE} (${TIME})"
  if [ "$TSUNAMI" = "1" ]; then
    ALERT="${ALERT} ⚠️ TSUNAMI POTENTIAL"
  fi
  NEW_EVENTS="${NEW_EVENTS}${ALERT}\n"
done < <(echo "$FEED" | jq -c '.features[]')

# Only notify if there are NEW events
if [ -n "$NEW_EVENTS" ]; then
  MSG="🔔 WEMS Alert [${REGION}]:\n${NEW_EVENTS}"
  
  # Wake Helios via cron wake event
  # This injects a system message into the session — no polling needed
  echo -e "$MSG"
  
  # Also log it
  echo "$(date -Iseconds) | ${MSG}" >> /tmp/wems-alerts.log
fi

# Prune state file (keep last 50 IDs)
tail -50 "$STATE_FILE" > "${STATE_FILE}.tmp" && mv "${STATE_FILE}.tmp" "$STATE_FILE"
