#!/usr/bin/env python3
"""Update Moltbook thread tracker with latest engagement data"""

import json
import os
import sys
from datetime import datetime, timezone

def load_tracker(filepath):
    """Load the tracker JSON file"""
    if not os.path.exists(filepath):
        return {"active_threads": [], "lessons_learned": []}
    
    with open(filepath, 'r') as f:
        return json.load(f)

def save_tracker(filepath, data):
    """Save tracker JSON file with pretty formatting"""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

def add_thread(filepath, post_id, title, comment_count=0):
    """Add a new thread to track"""
    data = load_tracker(filepath)
    
    # Check if already tracking
    for thread in data["active_threads"]:
        if thread["post_id"] == post_id:
            print(f"Already tracking: {title}")
            return
    
    # Add new thread
    data["active_threads"].append({
        "post_id": post_id,
        "title": title,
        "my_last_check": datetime.now(timezone.utc).isoformat(),
        "last_comment_count": comment_count
    })
    
    save_tracker(filepath, data)
    print(f"Now tracking: {title}")

def update_thread(filepath, post_id, comment_count, reply_ids=None):
    """Update a thread's comment count and reply IDs"""
    data = load_tracker(filepath)
    
    for thread in data["active_threads"]:
        if thread["post_id"] == post_id:
            thread["my_last_check"] = datetime.now(timezone.utc).isoformat()
            thread["last_comment_count"] = comment_count
            
            if reply_ids:
                if "my_replies" not in thread:
                    thread["my_replies"] = []
                # Add new reply IDs
                for reply_id in reply_ids:
                    if reply_id not in thread["my_replies"]:
                        thread["my_replies"].append(reply_id)
            
            save_tracker(filepath, data)
            print(f"Updated: {thread['title']}")
            return
    
    print(f"Thread {post_id} not found in tracker")

def remove_thread(filepath, post_id):
    """Remove a thread from tracking"""
    data = load_tracker(filepath)
    
    original_count = len(data["active_threads"])
    data["active_threads"] = [t for t in data["active_threads"] if t["post_id"] != post_id]
    
    if len(data["active_threads"]) < original_count:
        save_tracker(filepath, data)
        print(f"Removed thread {post_id}")
    else:
        print(f"Thread {post_id} not found")

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  update_tracker.py add <post_id> <title> [comment_count]")
        print("  update_tracker.py update <post_id> <comment_count> [reply_id1,reply_id2,...]")
        print("  update_tracker.py remove <post_id>")
        sys.exit(1)
    
    tracker_file = os.environ.get("TRACKER_FILE", 
                                  os.path.expanduser("~/.openclaw/workspace/memory/moltbook-threads.json"))
    
    action = sys.argv[1]
    
    if action == "add":
        if len(sys.argv) < 4:
            print("Error: add requires <post_id> <title> [comment_count]")
            sys.exit(1)
        post_id = sys.argv[2]
        title = sys.argv[3]
        comment_count = int(sys.argv[4]) if len(sys.argv) > 4 else 0
        add_thread(tracker_file, post_id, title, comment_count)
    
    elif action == "update":
        if len(sys.argv) < 4:
            print("Error: update requires <post_id> <comment_count> [reply_ids]")
            sys.exit(1)
        post_id = sys.argv[2]
        comment_count = int(sys.argv[3])
        reply_ids = sys.argv[4].split(',') if len(sys.argv) > 4 else None
        update_thread(tracker_file, post_id, comment_count, reply_ids)
    
    elif action == "remove":
        if len(sys.argv) < 3:
            print("Error: remove requires <post_id>")
            sys.exit(1)
        post_id = sys.argv[2]
        remove_thread(tracker_file, post_id)
    
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)

if __name__ == "__main__":
    main()
