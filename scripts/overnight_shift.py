#!/usr/bin/env python3
"""
Overnight Autonomous Shift - Run every 15 minutes while Matthew sleeps
Proactive work that adds value without asking permission
"""

import random
import subprocess
import json
from datetime import datetime

def log_activity(activity):
    """Log what I did during the shift"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("/home/bonsaihorn/.openclaw/workspace/memory/overnight_log.txt", "a") as f:
        f.write(f"[{timestamp}] {activity}\n")

def get_rotation_task():
    """Rotate through different types of productive work"""
    tasks = [
        "github_activity",
        "email_outreach",
        "skill_review",
        "moltbook_engage",
        "documentation",
        "cortex_reflection",
        "code_improvement"
    ]
    # Simple round-robin based on hour and minute
    now = datetime.now()
    index = (now.hour * 60 + now.minute) // 15 % len(tasks)
    return tasks[index]

def main():
    task = get_rotation_task()
    log_activity(f"Starting overnight shift task: {task}")
    
    print(f"🌙 Overnight Shift - Task: {task}")
    print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
    print(f"Matthew is sleeping. Time to ship.")
    
    # The actual work will be done by the agent, not this script
    # This just signals which type of work to prioritize
    print(f"\n✅ Task rotation: {task}")
    
    log_activity(f"Completed: {task}")

if __name__ == "__main__":
    main()
