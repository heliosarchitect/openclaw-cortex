#!/bin/bash
# discord-post.sh — Post to LBF Operations Discord channels
# Usage: discord-post.sh <channel-name> <message>
# Channels: general, trading-alerts, pattern-discovery, daily-report,
#           sub-agent-reports, system-health, memory-log, daily-summary, email-alerts

set -euo pipefail

source ~/.secrets/discord.env

declare -A CHANNELS=(
  [general]="1470466123777703978"
  [trading-alerts]="1470472344236462172"
  [pattern-discovery]="1470472345192759379"
  [daily-report]="1470472346233081933"
  [sub-agent-reports]="1470472347436847124"
  [system-health]="1470472348573372500"
  [memory-log]="1470472349299249245"
  [daily-summary]="1470472350502883582"
  [email-alerts]="1470472351975211030"
)

CHANNEL_NAME="${1:-}"
MESSAGE="${2:-}"

if [[ -z "$CHANNEL_NAME" || -z "$MESSAGE" ]]; then
  echo "Usage: discord-post.sh <channel-name> <message>"
  echo "Channels: ${!CHANNELS[*]}"
  exit 1
fi

CHANNEL_ID="${CHANNELS[$CHANNEL_NAME]:-}"
if [[ -z "$CHANNEL_ID" ]]; then
  echo "Unknown channel: $CHANNEL_NAME"
  echo "Available: ${!CHANNELS[*]}"
  exit 1
fi

# Discord message limit is 2000 chars — chunk if needed
if [[ ${#MESSAGE} -le 2000 ]]; then
  curl -s -X POST "https://discord.com/api/v10/channels/${CHANNEL_ID}/messages" \
    -H "Authorization: Bot ${DISCORD_BOT_TOKEN}" \
    -H "Content-Type: application/json" \
    -d "$(python3 -c "import json; print(json.dumps({'content': '''${MESSAGE}'''[:2000]}))")" \
    > /dev/null 2>&1
  echo "✅ Posted to #${CHANNEL_NAME}"
else
  # Chunk by 2000 chars on line boundaries
  echo "$MESSAGE" | fold -s -w 1990 | while IFS= read -r chunk; do
    curl -s -X POST "https://discord.com/api/v10/channels/${CHANNEL_ID}/messages" \
      -H "Authorization: Bot ${DISCORD_BOT_TOKEN}" \
      -H "Content-Type: application/json" \
      -d "$(python3 -c "import json,sys; print(json.dumps({'content': sys.stdin.read()}))" <<< "$chunk")" \
      > /dev/null 2>&1
    sleep 0.5
  done
  echo "✅ Posted to #${CHANNEL_NAME} (chunked)"
fi
