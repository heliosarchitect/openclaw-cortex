#!/usr/bin/env python3
"""
Bot Guardian - Monitor and auto-restart trading bot if it dies
Tracks crash patterns and alerts on repeated failures
"""

import subprocess
import time
import json
from pathlib import Path
from datetime import datetime

BOT_DIR = Path.home() / "Projects/Chad2930/Chad_Profit_Bot"
BOT_SCRIPT = "live_trader_final.py"
LOG_FILE = BOT_DIR / "trader.log"
STATE_FILE = Path.home() / ".openclaw/workspace/memory/bot_guardian_state.json"

def is_bot_running():
    """Check if trading bot process is active"""
    result = subprocess.run(
        ["pgrep", "-f", BOT_SCRIPT],
        capture_output=True,
        text=True
    )
    return bool(result.stdout.strip())

def start_bot():
    """Start the trading bot"""
    cmd = f"cd {BOT_DIR} && nohup python3 {BOT_SCRIPT} > trader.log 2>&1 &"
    subprocess.run(cmd, shell=True)
    time.sleep(3)  # Give it time to start
    return is_bot_running()

def load_state():
    """Load guardian state"""
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {
        "crashes": [],
        "restarts": 0,
        "last_check": None
    }

def save_state(state):
    """Save guardian state"""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))

def main():
    state = load_state()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if not is_bot_running():
        print(f"🚨 Bot died at {now}")
        
        # Log the crash
        state["crashes"].append(now)
        
        # Restart
        if start_bot():
            state["restarts"] += 1
            print(f"✅ Bot restarted (restart #{state['restarts']})")
            
            # Alert if too many crashes
            recent_crashes = [c for c in state["crashes"] if c >= datetime.now().strftime("%Y-%m-%d")]
            if len(recent_crashes) >= 3:
                print(f"⚠️  WARNING: {len(recent_crashes)} crashes today - investigate cause!")
        else:
            print("❌ Failed to restart bot")
    else:
        print(f"✅ Bot running at {now}")
    
    state["last_check"] = now
    save_state(state)

if __name__ == "__main__":
    main()
