#!/usr/bin/env python3
"""
Check for recent earthquakes
- 4.5+ in last hour (general awareness)
- 6.0+ in last 24 hours (ALERT Matthew)
- 8.0+ any time (IMMEDIATE alert)
"""
import urllib.request
import json
from datetime import datetime, timedelta

def check_earthquakes():
    # Check for major quakes first (6.0+)
    day_url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
    hour_url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_hour.geojson"
    
    try:
        # Get all quakes in last 24 hours
        with urllib.request.urlopen(day_url, timeout=10) as response:
            day_data = json.loads(response.read().decode())
        
        # Filter for 6.0+
        now = datetime.utcnow()
        major_quakes = []
        
        for feature in day_data.get('features', []):
            props = feature.get('properties', {})
            mag = props.get('mag', 0)
            
            if mag >= 6.0:
                time_ms = props.get('time', 0)
                quake_time = datetime.utcfromtimestamp(time_ms / 1000)
                hours_ago = (now - quake_time).total_seconds() / 3600
                place = props.get('place', 'Unknown location')
                major_quakes.append((mag, place, hours_ago))
        
        # Alert on major quakes
        if major_quakes:
            print(f"🚨 {len(major_quakes)} MAJOR earthquake(s) 6.0+ in last 24 hours:")
            for mag, place, hours_ago in sorted(major_quakes, key=lambda x: x[0], reverse=True):
                print(f"  🔴 M{mag:.1f} - {place} ({hours_ago:.1f}h ago)")
        
        # Check recent 4.5+ quakes
        with urllib.request.urlopen(hour_url, timeout=10) as response:
            hour_data = json.loads(response.read().decode())
        
        quakes = hour_data.get('features', [])
        
        if not quakes and not major_quakes:
            print("✅ No 4.5+ earthquakes in past hour")
        elif quakes:
            print(f"🌍 {len(quakes)} earthquake(s) detected:")
            for feature in quakes:
                props = feature.get('properties', {})
                mag = props.get('mag', 0)
                place = props.get('place', 'Unknown location')
                time_ms = props.get('time', 0)
                quake_time = datetime.utcfromtimestamp(time_ms / 1000)
                
                emoji = "🔴" if mag >= 6.0 else "🟡" if mag >= 5.0 else "🟢"
                print(f"  {emoji} M{mag:.1f} - {place} ({quake_time.strftime('%H:%M UTC')})")
    
    except Exception as e:
        print(f"❌ Error checking earthquakes: {e}")

if __name__ == "__main__":
    check_earthquakes()
