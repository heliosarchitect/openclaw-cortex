#!/usr/bin/env python3
"""Check Fear & Greed Index for crypto market sentiment."""

import json
import urllib.request
import urllib.error

def check_fear_greed():
    """Get current Fear & Greed Index."""
    url = "https://api.alternative.me/fng/"
    
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
        
        if 'data' not in data or not data['data']:
            print("⚠️ No data returned from Fear & Greed API")
            return
        
        current = data['data'][0]
        value = int(current['value'])
        classification = current['value_classification']
        
        # Emoji based on value
        if value <= 20:
            emoji = "🔴"  # Extreme Fear
        elif value <= 40:
            emoji = "🟠"  # Fear
        elif value <= 60:
            emoji = "🟡"  # Neutral
        elif value <= 80:
            emoji = "🟢"  # Greed
        else:
            emoji = "🔵"  # Extreme Greed
        
        print(f"{emoji} Fear & Greed: {value} ({classification})")
        
    except urllib.error.URLError as e:
        print(f"⚠️ Fear & Greed API unavailable: {e.reason}")
    except json.JSONDecodeError:
        print(f"⚠️ Invalid response from Fear & Greed API")
    except Exception as e:
        print(f"⚠️ Error checking Fear & Greed: {type(e).__name__}")

if __name__ == "__main__":
    check_fear_greed()
