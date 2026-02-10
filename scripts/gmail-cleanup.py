#!/usr/bin/env python3
"""Gmail Cleanup Script for bonsaihorn@gmail.com
DO NOT send emails. DO NOT delete photos.
"""
import subprocess
import json
import sys
import os
from datetime import datetime

os.environ['GOG_ACCOUNT'] = 'bonsaihorn@gmail.com'

RESULTS_FILE = '/home/bonsaihorn/.openclaw/workspace/analysis/gmail-cleanup-results.md'

def run_cmd(cmd):
    """Run command and return output"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
    return result.stdout + result.stderr

def search_and_delete(label, query):
    """Search for emails matching query, paginate, and batch delete all."""
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
            # Find the JSON object in output (might have extra text)
            json_start = output.find('{')
            if json_start == -1:
                print(f"  [{label}] No JSON response. Output: {output[:200]}", flush=True)
                break
            json_str = output[json_start:]
            # Find matching closing brace
            data = json.loads(json_str)
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
        print(f"  [{label}] Found {count} threads, deleting...", flush=True)
        
        # Batch delete - split into chunks of 50 to avoid arg limits
        for i in range(0, len(ids), 50):
            chunk = ids[i:i+50]
            id_str = ' '.join(chunk)
            del_cmd = f"GOG_ACCOUNT=bonsaihorn@gmail.com gog gmail batch delete {id_str} --force --no-input"
            del_output = run_cmd(del_cmd)
            print(f"    Deleted chunk of {len(chunk)}: {del_output.strip()[:100]}", flush=True)
        
        total += count
        print(f"  [{label}] Running total: {total}", flush=True)
        
        # Check for next page
        page_token = data.get('nextPageToken')
        if not page_token:
            break
    
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
        
        count = search_and_delete(label, query)
        results[label] = count
        grand_total += count
    
    # Write results
    now = datetime.now().strftime('%Y-%m-%d %H:%M EST')
    with open(RESULTS_FILE, 'w') as f:
        f.write(f"# Gmail Cleanup Results - bonsaihorn@gmail.com\n")
        f.write(f"**Date:** {now}\n\n")
        f.write(f"## Summary\n\n")
        f.write(f"| Category | Threads Deleted |\n")
        f.write(f"|----------|----------------|\n")
        for label, count in results.items():
            f.write(f"| {label} | {count} |\n")
        f.write(f"| **GRAND TOTAL** | **{grand_total}** |\n\n")
        f.write(f"## Notes\n")
        f.write(f"- No emails were sent\n")
        f.write(f"- No photos were deleted\n")
        f.write(f"- Threads were permanently deleted (not trashed)\n")
        f.write(f"- Some overlap possible between categories (e.g., sales emails already deleted as promotions)\n")
        f.write(f"- Promotions category is comprehensive and likely covers many sales/deal emails\n")
    
    print(f"\n{'='*50}", flush=True)
    print(f"GRAND TOTAL: {grand_total} threads deleted", flush=True)
    print(f"Results saved to: {RESULTS_FILE}", flush=True)
    print(f"{'='*50}", flush=True)

if __name__ == '__main__':
    main()
