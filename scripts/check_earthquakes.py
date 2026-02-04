#!/usr/bin/env python3
"""Check for recent significant earthquakes using USGS API."""

import json
import urllib.request
import urllib.error
from datetime import datetime

def check_earthquakes():
    """Check USGS for recent 4.5+ earthquakes."""
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_hour.geojson"
    
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
        
        features = data.get('features', [])
        
        if not features:
            print("✅ No 4.5+ earthquakes in past hour")
            return
        
        print(f"🌍 {len(features)} earthquake(s) detected:")
        
        for quake in features[:5]:  # Show top 5
            props = quake['properties']
            mag = props['mag']
            place = props['place']
            time_ms = props['time']
            
            # Convert timestamp to readable format
            dt = datetime.fromtimestamp(time_ms / 1000)
            time_str = dt.strftime('%H:%M UTC')
            
            # Alert level
            if mag >= 8.0:
                alert = "🔴 MAJOR"
            elif mag >= 6.0:
                alert = "🟠 SIGNIFICANT"
            elif mag >= 5.5:
                alert = "🟡 MODERATE"
            else:
                alert = "🟢"
            
            print(f"  {alert} M{mag:.1f} - {place} ({time_str})")
    
    except urllib.error.URLError as e:
        print(f"⚠️ USGS API unavailable: {e.reason}")
    except json.JSONDecodeError as e:
        print(f"⚠️ Invalid response from USGS API")
    except Exception as e:
        print(f"⚠️ Error checking earthquakes: {type(e).__name__}")

if __name__ == "__main__":
    check_earthquakes()
