#!/usr/bin/env python3
"""Monitor CPU temperature and alert if too hot."""
import subprocess
import re

def get_cpu_temp():
    """Get AMD CPU temperature from sensors."""
    try:
        result = subprocess.run(['sensors'], capture_output=True, text=True, timeout=5)
        output = result.stdout
        
        # Look for k10temp Tctl (main CPU die temp)
        for line in output.split('\n'):
            if 'Tctl:' in line:
                # Extract temperature value
                match = re.search(r'\+(\d+\.\d+)°C', line)
                if match:
                    return float(match.group(1))
        
        return None
    except Exception as e:
        print(f"Error reading temperature: {e}")
        return None

def main():
    temp = get_cpu_temp()
    
    if temp is None:
        print("⚠️ Could not read CPU temperature")
        return
    
    print(f"🌡️ CPU: {temp:.1f}°C", end="")
    
    # Alert thresholds
    if temp >= 95:
        print(f" 🔥 CRITICAL - THROTTLING RISK!")
    elif temp >= 90:
        print(f" ⚠️ HOT - Close to throttle threshold")
    elif temp >= 85:
        print(f" 🔶 Warm - Monitor closely")
    elif temp >= 75:
        print(f" ✅ Normal under load")
    else:
        print(f" ✅ Cool")

if __name__ == '__main__':
    main()
