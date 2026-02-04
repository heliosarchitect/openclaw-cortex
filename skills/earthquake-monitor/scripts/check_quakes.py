#!/usr/bin/env python3
"""
Earthquake monitor using USGS GeoJSON feeds.
"""
import json
import urllib.request
import sys
from datetime import datetime
from argparse import ArgumentParser

FEEDS = {
    'hour': 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson',
    'day': 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson',
    'significant_hour': 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_hour.geojson',
    'significant_day': 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_day.geojson',
}

def fetch_quakes(feed='day'):
    """Fetch earthquake data from USGS."""
    url = FEEDS.get(feed, FEEDS['day'])
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
            return data.get('features', [])
    except Exception as e:
        print(f"Error fetching earthquake data: {e}", file=sys.stderr)
        return []

def format_time(timestamp_ms):
    """Convert Unix timestamp (ms) to readable format."""
    dt = datetime.fromtimestamp(timestamp_ms / 1000)
    return dt.strftime('%Y-%m-%d %H:%M UTC')

def alert_level(magnitude):
    """Determine alert level based on magnitude."""
    if magnitude >= 8.0:
        return 'catastrophic', '🚨'
    elif magnitude >= 7.0:
        return 'major', '⚠️'
    elif magnitude >= 6.0:
        return 'notable', '📍'
    elif magnitude >= 5.0:
        return 'moderate', '•'
    else:
        return 'minor', '·'

def check_earthquakes(feed='day', min_magnitude=0.0, format='text'):
    """
    Check for earthquakes above minimum magnitude.
    
    Returns:
        dict with 'quakes' list and 'alert_level' (catastrophic/major/notable/none)
    """
    quakes = fetch_quakes(feed)
    
    # Filter by magnitude
    filtered = [
        q for q in quakes 
        if q['properties']['mag'] >= min_magnitude
    ]
    
    # Sort by magnitude (descending)
    filtered.sort(key=lambda q: q['properties']['mag'], reverse=True)
    
    # Determine max alert level
    max_alert = 'none'
    if filtered:
        max_mag = filtered[0]['properties']['mag']
        max_alert, _ = alert_level(max_mag)
    
    return {
        'quakes': filtered,
        'alert_level': max_alert,
        'count': len(filtered)
    }

def main():
    parser = ArgumentParser(description='Check USGS earthquake data')
    parser.add_argument('--feed', choices=FEEDS.keys(), default='day',
                        help='Which feed to check (default: day)')
    parser.add_argument('--min', type=float, default=4.5,
                        help='Minimum magnitude (default: 4.5)')
    parser.add_argument('--format', choices=['text', 'json'], default='text',
                        help='Output format')
    parser.add_argument('--limit', type=int, default=10,
                        help='Max quakes to show')
    
    args = parser.parse_args()
    
    result = check_earthquakes(args.feed, args.min, args.format)
    
    if args.format == 'json':
        print(json.dumps(result, indent=2))
        return
    
    # Text output
    print(f"🌍 Earthquakes {args.min}+ magnitude ({args.feed}):")
    print(f"Found: {result['count']}")
    
    if result['alert_level'] in ['catastrophic', 'major']:
        print(f"⚠️  ALERT LEVEL: {result['alert_level'].upper()}")
    
    print()
    
    if not result['quakes']:
        print("No significant quakes.")
        return
    
    for quake in result['quakes'][:args.limit]:
        props = quake['properties']
        mag = props['mag']
        place = props['place']
        time = format_time(props['time'])
        depth = quake['geometry']['coordinates'][2]
        
        level, icon = alert_level(mag)
        
        print(f"{icon} {mag:.1f} - {place}")
        print(f"   {time} | Depth: {depth:.1f} km")
        print()

if __name__ == '__main__':
    main()
