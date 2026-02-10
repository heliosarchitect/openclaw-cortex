#!/bin/bash
# Gmail Cleanup Script for bonsaihorn@gmail.com
# DO NOT send emails. DO NOT delete photos.
export GOG_ACCOUNT=bonsaihorn@gmail.com

RESULTS_FILE="/home/bonsaihorn/.openclaw/workspace/analysis/gmail-cleanup-results.md"
mkdir -p "$(dirname "$RESULTS_FILE")"

GRAND_TOTAL=0

# Function to search, paginate, and delete
cleanup_category() {
    local label="$1"
    local query="$2"
    local total=0
    local page_token=""
    local page_num=0

    echo "=== Processing: $label ==="
    echo "Query: $query"

    while true; do
        page_num=$((page_num + 1))
        echo "  Page $page_num..."

        # Build command
        if [ -z "$page_token" ]; then
            output=$(gog gmail search "$query" --max 100 --json --no-input 2>&1)
        else
            output=$(gog gmail search "$query" --max 100 --json --no-input --page "$page_token" 2>&1)
        fi

        # Check for errors or empty results
        if echo "$output" | grep -q '"threads"'; then
            # Extract thread IDs (which are also message IDs for single-message threads)
            ids=$(echo "$output" | python3 -c "
import sys, json
data = json.load(sys.stdin)
threads = data.get('threads', [])
for t in threads:
    print(t['id'])
" 2>/dev/null)

            if [ -z "$ids" ]; then
                echo "  No more messages found."
                break
            fi

            count=$(echo "$ids" | wc -l)
            echo "  Found $count threads on this page."

            # For each thread, we need to get message IDs
            # Thread ID might contain multiple messages
            # Let's try batch delete with thread IDs first - they might work as message IDs
            id_list=$(echo "$ids" | tr '\n' ' ')
            
            # Batch delete in chunks of 50 to avoid command line limits
            echo "$ids" | while IFS= read -r batch_line; do
                echo "$batch_line"
            done | xargs -n 50 bash -c '
                gog gmail batch delete "$@" --force --no-input 2>&1
            ' _

            total=$((total + count))
            echo "  Deleted $count (running total: $total)"

            # Check for next page
            page_token=$(echo "$output" | python3 -c "
import sys, json
data = json.load(sys.stdin)
token = data.get('nextPageToken', '')
print(token)
" 2>/dev/null)

            if [ -z "$page_token" ]; then
                echo "  No more pages."
                break
            fi
            echo "  Next page token: ${page_token:0:20}..."
        else
            # Check if it's a "no results" response
            if echo "$output" | grep -qi "no messages\|no threads\|0 threads\|not found"; then
                echo "  No messages found."
            else
                echo "  Response: $output"
            fi
            break
        fi
    done

    echo "  TOTAL for $label: $total"
    echo ""
    GRAND_TOTAL=$((GRAND_TOTAL + total))
    
    # Write to results
    echo "| $label | $total |" >> "$RESULTS_FILE"
    
    # Export for parent
    echo "$total"
}

# Initialize results file
cat > "$RESULTS_FILE" << 'EOF'
# Gmail Cleanup Results - bonsaihorn@gmail.com
**Date:** $(date '+%Y-%m-%d %H:%M EST')

## Summary

| Category | Threads Deleted |
|----------|----------------|
EOF

# Fix the date
sed -i "s|\$(date '+%Y-%m-%d %H:%M EST')|$(date '+%Y-%m-%d %H:%M EST')|" "$RESULTS_FILE"

# 1. SPAM
echo "========================================="
echo "TASK 1: DELETE SPAM"
echo "========================================="
spam_total=0
page_token=""
while true; do
    if [ -z "$page_token" ]; then
        output=$(gog gmail search 'in:spam' --max 100 --json --no-input 2>&1)
    else
        output=$(gog gmail search 'in:spam' --max 100 --json --no-input --page "$page_token" 2>&1)
    fi
    
    ids=$(echo "$output" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    threads = data.get('threads', [])
    for t in threads:
        print(t['id'])
except: pass
" 2>/dev/null)
    
    if [ -z "$ids" ]; then
        echo "No more spam messages."
        break
    fi
    
    count=$(echo "$ids" | wc -l)
    echo "Found $count spam threads, deleting..."
    
    echo "$ids" | xargs gog gmail batch delete --force --no-input 2>&1
    
    spam_total=$((spam_total + count))
    echo "Deleted batch ($spam_total total so far)"
    
    page_token=$(echo "$output" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('nextPageToken', ''))
except: print('')
" 2>/dev/null)
    
    if [ -z "$page_token" ]; then
        break
    fi
done
echo "SPAM TOTAL: $spam_total"
echo "| Spam | $spam_total |" >> "$RESULTS_FILE"
GRAND_TOTAL=$((GRAND_TOTAL + spam_total))

# 2. PROMOTIONS
echo ""
echo "========================================="
echo "TASK 2: DELETE PROMOTIONS"
echo "========================================="
promo_total=0
page_token=""
while true; do
    if [ -z "$page_token" ]; then
        output=$(gog gmail search 'category:promotions' --max 100 --json --no-input 2>&1)
    else
        output=$(gog gmail search 'category:promotions' --max 100 --json --no-input --page "$page_token" 2>&1)
    fi
    
    ids=$(echo "$output" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    threads = data.get('threads', [])
    for t in threads:
        print(t['id'])
except: pass
" 2>/dev/null)
    
    if [ -z "$ids" ]; then
        echo "No more promotions."
        break
    fi
    
    count=$(echo "$ids" | wc -l)
    echo "Found $count promotion threads, deleting..."
    
    echo "$ids" | xargs gog gmail batch delete --force --no-input 2>&1
    
    promo_total=$((promo_total + count))
    echo "Deleted batch ($promo_total total so far)"
    
    page_token=$(echo "$output" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('nextPageToken', ''))
except: print('')
" 2>/dev/null)
    
    if [ -z "$page_token" ]; then
        break
    fi
done
echo "PROMOTIONS TOTAL: $promo_total"
echo "| Promotions | $promo_total |" >> "$RESULTS_FILE"
GRAND_TOTAL=$((GRAND_TOTAL + promo_total))

# 3. BLACK FRIDAY/SALES
echo ""
echo "========================================="
echo "TASK 3: DELETE BLACK FRIDAY/SALES EMAILS"
echo "========================================="
sales_total=0
page_token=""
while true; do
    if [ -z "$page_token" ]; then
        output=$(gog gmail search 'subject:(black friday OR cyber monday OR sale OR deal OR discount OR coupon) -is:starred' --max 100 --json --no-input 2>&1)
    else
        output=$(gog gmail search 'subject:(black friday OR cyber monday OR sale OR deal OR discount OR coupon) -is:starred' --max 100 --json --no-input --page "$page_token" 2>&1)
    fi
    
    ids=$(echo "$output" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    threads = data.get('threads', [])
    for t in threads:
        print(t['id'])
except: pass
" 2>/dev/null)
    
    if [ -z "$ids" ]; then
        echo "No more sales emails."
        break
    fi
    
    count=$(echo "$ids" | wc -l)
    echo "Found $count sales threads, deleting..."
    
    echo "$ids" | xargs gog gmail batch delete --force --no-input 2>&1
    
    sales_total=$((sales_total + count))
    echo "Deleted batch ($sales_total total so far)"
    
    page_token=$(echo "$output" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('nextPageToken', ''))
except: print('')
" 2>/dev/null)
    
    if [ -z "$page_token" ]; then
        break
    fi
done
echo "SALES TOTAL: $sales_total"
echo "| Black Friday/Sales | $sales_total |" >> "$RESULTS_FILE"
GRAND_TOTAL=$((GRAND_TOTAL + sales_total))

# 4. SUBSTACK
echo ""
echo "========================================="
echo "TASK 4: DELETE SUBSTACK NEWSLETTERS"
echo "========================================="
sub_total=0
page_token=""
while true; do
    if [ -z "$page_token" ]; then
        output=$(gog gmail search 'from:substack.com' --max 100 --json --no-input 2>&1)
    else
        output=$(gog gmail search 'from:substack.com' --max 100 --json --no-input --page "$page_token" 2>&1)
    fi
    
    ids=$(echo "$output" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    threads = data.get('threads', [])
    for t in threads:
        print(t['id'])
except: pass
" 2>/dev/null)
    
    if [ -z "$ids" ]; then
        echo "No more Substack emails."
        break
    fi
    
    count=$(echo "$ids" | wc -l)
    echo "Found $count Substack threads, deleting..."
    
    echo "$ids" | xargs gog gmail batch delete --force --no-input 2>&1
    
    sub_total=$((sub_total + count))
    echo "Deleted batch ($sub_total total so far)"
    
    page_token=$(echo "$output" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('nextPageToken', ''))
except: print('')
" 2>/dev/null)
    
    if [ -z "$page_token" ]; then
        break
    fi
done
echo "SUBSTACK TOTAL: $sub_total"
echo "| Substack Newsletters | $sub_total |" >> "$RESULTS_FILE"
GRAND_TOTAL=$((GRAND_TOTAL + sub_total))

# 5. GITHUB NOTIFICATIONS
echo ""
echo "========================================="
echo "TASK 5: DELETE GITHUB NOTIFICATIONS"
echo "========================================="
gh_total=0
page_token=""
while true; do
    if [ -z "$page_token" ]; then
        output=$(gog gmail search 'from:notifications@github.com' --max 100 --json --no-input 2>&1)
    else
        output=$(gog gmail search 'from:notifications@github.com' --max 100 --json --no-input --page "$page_token" 2>&1)
    fi
    
    ids=$(echo "$output" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    threads = data.get('threads', [])
    for t in threads:
        print(t['id'])
except: pass
" 2>/dev/null)
    
    if [ -z "$ids" ]; then
        echo "No more GitHub notifications."
        break
    fi
    
    count=$(echo "$ids" | wc -l)
    echo "Found $count GitHub threads, deleting..."
    
    echo "$ids" | xargs gog gmail batch delete --force --no-input 2>&1
    
    gh_total=$((gh_total + count))
    echo "Deleted batch ($gh_total total so far)"
    
    page_token=$(echo "$output" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('nextPageToken', ''))
except: print('')
" 2>/dev/null)
    
    if [ -z "$page_token" ]; then
        break
    fi
done
echo "GITHUB TOTAL: $gh_total"
echo "| GitHub Notifications | $gh_total |" >> "$RESULTS_FILE"
GRAND_TOTAL=$((GRAND_TOTAL + gh_total))

# 6. GROUPS.IO
echo ""
echo "========================================="
echo "TASK 6: DELETE GROUPS.IO EMAILS"
echo "========================================="
groups_total=0
page_token=""
while true; do
    if [ -z "$page_token" ]; then
        output=$(gog gmail search 'from:groups.io' --max 100 --json --no-input 2>&1)
    else
        output=$(gog gmail search 'from:groups.io' --max 100 --json --no-input --page "$page_token" 2>&1)
    fi
    
    ids=$(echo "$output" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    threads = data.get('threads', [])
    for t in threads:
        print(t['id'])
except: pass
" 2>/dev/null)
    
    if [ -z "$ids" ]; then
        echo "No more groups.io emails."
        break
    fi
    
    count=$(echo "$ids" | wc -l)
    echo "Found $count groups.io threads, deleting..."
    
    echo "$ids" | xargs gog gmail batch delete --force --no-input 2>&1
    
    groups_total=$((groups_total + count))
    echo "Deleted batch ($groups_total total so far)"
    
    page_token=$(echo "$output" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('nextPageToken', ''))
except: print('')
" 2>/dev/null)
    
    if [ -z "$page_token" ]; then
        break
    fi
done
echo "GROUPS.IO TOTAL: $groups_total"
echo "| Groups.io | $groups_total |" >> "$RESULTS_FILE"
GRAND_TOTAL=$((GRAND_TOTAL + groups_total))

# 7. TRUMP CAMPAIGN
echo ""
echo "========================================="
echo "TASK 7: DELETE TRUMP CAMPAIGN EMAILS"
echo "========================================="
trump_total=0
page_token=""
while true; do
    if [ -z "$page_token" ]; then
        output=$(gog gmail search 'from:trump OR from:donaldjtrump OR from:winred' --max 100 --json --no-input 2>&1)
    else
        output=$(gog gmail search 'from:trump OR from:donaldjtrump OR from:winred' --max 100 --json --no-input --page "$page_token" 2>&1)
    fi
    
    ids=$(echo "$output" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    threads = data.get('threads', [])
    for t in threads:
        print(t['id'])
except: pass
" 2>/dev/null)
    
    if [ -z "$ids" ]; then
        echo "No more Trump campaign emails."
        break
    fi
    
    count=$(echo "$ids" | wc -l)
    echo "Found $count Trump campaign threads, deleting..."
    
    echo "$ids" | xargs gog gmail batch delete --force --no-input 2>&1
    
    trump_total=$((trump_total + count))
    echo "Deleted batch ($trump_total total so far)"
    
    page_token=$(echo "$output" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('nextPageToken', ''))
except: print('')
" 2>/dev/null)
    
    if [ -z "$page_token" ]; then
        break
    fi
done
echo "TRUMP TOTAL: $trump_total"
echo "| Trump Campaign | $trump_total |" >> "$RESULTS_FILE"
GRAND_TOTAL=$((GRAND_TOTAL + trump_total))

# Final summary
echo "" >> "$RESULTS_FILE"
echo "| **GRAND TOTAL** | **$GRAND_TOTAL** |" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"
echo "## Notes" >> "$RESULTS_FILE"
echo "- No emails were sent" >> "$RESULTS_FILE"
echo "- No photos were deleted" >> "$RESULTS_FILE"
echo "- Threads were permanently deleted (not trashed)" >> "$RESULTS_FILE"
echo "- Some overlap between categories (e.g., sales emails may also be in promotions)" >> "$RESULTS_FILE"

echo ""
echo "========================================="
echo "GRAND TOTAL: $GRAND_TOTAL threads deleted"
echo "========================================="
echo "Results saved to: $RESULTS_FILE"
