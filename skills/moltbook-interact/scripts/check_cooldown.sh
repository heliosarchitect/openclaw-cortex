#!/usr/bin/env bash
# Check Moltbook comment cooldown status

COOLDOWN_FILE="${HOME}/.cache/moltbook_last_comment"
COOLDOWN_SECONDS=900  # 15 minutes

# Create cache dir if needed
mkdir -p "$(dirname "$COOLDOWN_FILE")"

# Get last comment time
if [[ -f "$COOLDOWN_FILE" ]]; then
    LAST_COMMENT=$(cat "$COOLDOWN_FILE")
else
    LAST_COMMENT=0
fi

NOW=$(date +%s)
ELAPSED=$((NOW - LAST_COMMENT))
REMAINING=$((COOLDOWN_SECONDS - ELAPSED))

if [[ $REMAINING -le 0 ]]; then
    echo "✅ Ready to comment"
    exit 0
else
    MINUTES=$((REMAINING / 60))
    SECONDS=$((REMAINING % 60))
    echo "⏰ Rate limit: Wait ${MINUTES}m ${SECONDS}s"
    exit 1
fi
