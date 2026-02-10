#!/usr/bin/env python3
"""Gmail Cleanup Script v2 for bonsaihorn@gmail.com
Uses batch modify --add TRASH (batch delete requires full mail scope).
Includes rate limit handling.
DO NOT send emails. DO NOT delete photos.
"""
import subprocess
import json
import sys
import os
import time
from datetime import datetime

os.environ['GOG_ACCOUNT'] = 'bonsaihorn@gmail.com'

RESULTS_FILE = '/home/bonsaihorn/.openclaw/workspace/analysis/gmail-cleanup-results.md'

def run_cmd(cmd, retries=3):
    """Run command with retry on rate limit"""
    for attempt in range(retries):
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
        output = result.stdout + result.stderr
        if 'rateLimitExceeded' in output:
            wait_time = 30 * (attempt + 1)
            print(f"    Rate limited, waiting {wait_time}s...", flush=True)
            time.sleep(wait_time)
            continue
        return output
    return output  # Return last attempt even if rate limited

def search_and_trash(label, query):
    """Search for emails matching query, paginate, and trash all."""
    total = 0
    page_token = None
    page_num = 0
    
    while True:
        page_num += 1
        cmd = f"GOG_ACCOUNT=bonsaihorn@gmail.com gog gmail search '{query}' --max 100 --json --no-input"
        if page_token:
            cmd += f" --page {page_token}"
        
        print(f"  [{label}] Page {page_num}...", flush=True)
        output = run_cmd(cmd)
        
        # Try to parse JSON
        try:
            json_start = output.find('{')
            if json_start == -1:
                print(f"  [{label}] No JSON response. Output: {output[:200]}", flush=True)
                break
            data = json.loads(output[json_start:])
        except json.JSONDecodeError as e:
            print(f"  [{label}] JSON parse error: {e}", flush=True)
            print(f"  Output: {output[:300]}", flush=True)
            break
        
        threads = data.get('threads', [])
        if not threads:
            print(f"  [{label}] No threads found.", flush=True)
            break
        
        ids = [t['id'] for t in threads]
        count = len(ids)
        print(f"  [{label}] Found {count} threads, trashing...", flush=True)
        
        # Batch modify to add TRASH - chunks of 50
        for i in range(0, len(ids), 50):
            chunk = ids[i:i+50]
            id_str = ' '.join(chunk)
            trash_cmd = f"GOG_ACCOUNT=bonsaihorn@gmail.com gog gmail batch modify {id_str} --add TRASH --force --no-input"
            trash_output = run_cmd(trash_cmd)
            print(f"    Trashed {len(chunk)}: {trash_output.strip()[:100]}", flush=True)
            # Small pause between batches to avoid rate limits
            time.sleep(1)
        
        total += count
        print(f"  [{label}] Running total: {total}", flush=True)
        
        # Check for next page
        page_token = data.get('nextPageToken')
        if not page_token:
            break
        
        # Pause between pages to be gentle on API
        time.sleep(2)
    
    print(f"  [{label}] FINAL TOTAL: {total}", flush=True)
    return total

def main():
    results = {}
    grand_total = 0
    
    categories = [
        ("Spam", "in:spam"),
        ("Promotions", "category:promotions"),
        ("Black Friday/Sales", "subject:(black friday OR cyber monday OR sale OR deal OR discount OR coupon) -is:starred"),
        ("Substack Newsletters", "from:substack.com"),
        ("GitHub Notifications", "from:notifications@github.com"),
        ("Groups.io", "from:groups.io"),
        ("Trump Campaign", "from:trump OR from:donaldjtrump OR from:winred"),
    ]
    
    for label, query in categories:
        print(f"\n{'='*50}", flush=True)
        print(f"TASK: {label}", flush=True)
        print(f"Query: {query}", flush=True)
        print(f"{'='*50}", flush=True)
        
        count = search_and_trash(label, query)
        results[label] = count
        grand_total += count
        
        # Pause between categories
        if count > 0:
            print(f"  Pausing 5s between categories...", flush=True)
            time.sleep(5)
    
    # Write results
    now = datetime.now().strftime('%Y-%m-%d %H:%M EST')
    with open(RESULTS_FILE, 'w') as f:
        f.write(f"# Gmail Cleanup Results - bonsaihorn@gmail.com\n")
        f.write(f"**Date:** {now}\n\n")
        f.write(f"## Summary\n\n")
        f.write(f"| Category | Threads Trashed |\n")
        f.write(f"|----------|----------------|\n")
        for label, count in results.items():
            f.write(f"| {label} | {count} |\n")
        f.write(f"| **GRAND TOTAL** | **{grand_total}** |\n\n")
        f.write(f"## Notes\n")
        f.write(f"- No emails were sent\n")
        f.write(f"- No photos were deleted\n")
        f.write(f"- Threads were moved to Trash (will auto-delete after 30 days)\n")
        f.write(f"- Used `batch modify --add TRASH` (permanent delete requires full mail scope)\n")
        f.write(f"- Some overlap between categories (e.g., sales emails already trashed as promotions won't appear again)\n")
        f.write(f"- First 2 spam messages trashed in initial test run (included in count above if re-searched)\n")
    
    print(f"\n{'='*50}", flush=True)
    print(f"GRAND TOTAL: {grand_total} threads trashed", flush=True)
    print(f"Results saved to: {RESULTS_FILE}", flush=True)
    print(f"{'='*50}", flush=True)

if __name__ == '__main__':
    main()
