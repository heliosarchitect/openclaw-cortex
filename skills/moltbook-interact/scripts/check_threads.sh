#!/bin/bash
# Check active Moltbook threads for new engagement

TRACKER_FILE="${TRACKER_FILE:-$HOME/.openclaw/workspace/memory/moltbook-threads.json}"
API_KEY="${MOLTBOOK_API_KEY}"

if [[ -z "$API_KEY" ]]; then
    echo "Error: MOLTBOOK_API_KEY not set"
    exit 1
fi

if [[ ! -f "$TRACKER_FILE" ]]; then
    echo "Error: Tracker file not found at $TRACKER_FILE"
    exit 1
fi

# Read active threads
threads=$(cat "$TRACKER_FILE" | grep -o '"post_id": *"[^"]*"' | cut -d'"' -f4)

if [[ -z "$threads" ]]; then
    echo "No active threads to check"
    exit 0
fi

echo "Checking $(echo "$threads" | wc -l) active threads..."
echo ""

new_activity=0

for post_id in $threads; do
    # Fetch current comment count
    response=$(curl -s -H "Authorization: Bearer ${API_KEY}" \
        "https://www.moltbook.com/api/v1/posts/${post_id}")
    
    if echo "$response" | grep -q '"success":true'; then
        current_count=$(echo "$response" | grep -o '"comment_count":[0-9]*' | grep -o '[0-9]*')
        title=$(echo "$response" | grep -o '"title":"[^"]*"' | cut -d'"' -f4 | head -1)
        
        # Get last known count from tracker
        last_count=$(grep -A 3 "\"post_id\": \"$post_id\"" "$TRACKER_FILE" | \
                    grep "last_comment_count" | grep -o '[0-9]*')
        
        if [[ -n "$current_count" && -n "$last_count" ]]; then
            if [[ $current_count -gt $last_count ]]; then
                new_comments=$((current_count - last_count))
                echo "✨ $title"
                echo "   Post ID: $post_id"
                echo "   New comments: $new_comments ($last_count → $current_count)"
                echo "   URL: https://www.moltbook.com/post/$post_id"
                echo ""
                new_activity=1
            fi
        fi
    fi
done

if [[ $new_activity -eq 0 ]]; then
    echo "No new activity on tracked threads"
fi

exit 0
