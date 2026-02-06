#!/usr/bin/env python3
"""
Order Book Collector Health Monitor
Checks if orderbook_ws_collector.py is running, restarts if crashed
"""
import subprocess
import os
from datetime import datetime

def is_collector_running():
    """Check if order book collector process is running"""
    try:
        result = subprocess.run(
            ['ps', 'aux'],
            capture_output=True,
            text=True
        )
        return 'orderbook_ws_collector.py' in result.stdout
    except Exception as e:
        print(f"Error checking process: {e}")
        return False

def get_last_snapshot_time():
    """Get timestamp of last snapshot from log"""
    log_path = os.path.expanduser("~/Projects/Chad_Volume_tracker/orderbook_ws.log")
    try:
        with open(log_path, 'r') as f:
            lines = f.readlines()
            if lines:
                last_line = lines[-1]
                # Extract timestamp from log line format: "💾 N snapshots | HH:MM:SS | ..."
                if '|' in last_line:
                    parts = last_line.split('|')
                    if len(parts) >= 2:
                        return parts[1].strip()
        return None
    except Exception as e:
        print(f"Error reading log: {e}")
        return None

def restart_collector():
    """Restart the order book collector"""
    try:
        # Change to project directory and start collector
        os.chdir(os.path.expanduser("~/Projects/Chad_Volume_tracker"))
        subprocess.Popen(
            ['nohup', 'python3', '-u', 'orderbook_ws_collector.py'],
            stdout=open('orderbook_ws.log', 'a'),
            stderr=subprocess.STDOUT,
            start_new_session=True
        )
        print("✅ Order book collector restarted")
        return True
    except Exception as e:
        print(f"❌ Failed to restart collector: {e}")
        return False

def main():
    running = is_collector_running()
    last_time = get_last_snapshot_time()
    
    if running:
        print(f"✅ Collector running (last snapshot: {last_time})")
    else:
        print(f"🚨 Collector STOPPED (last snapshot: {last_time})")
        print("Restarting collector...")
        if restart_collector():
            import time
            time.sleep(2)
            if is_collector_running():
                print("✅ Restart successful")
            else:
                print("❌ Restart failed - process not running")

if __name__ == "__main__":
    main()
