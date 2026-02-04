#!/usr/bin/env python3
"""
Analyze historical trading data to find optimal time windows for the strategy.
Not "when did Matthew make money" but "when does momentum scalping work best".
"""
import sqlite3
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# Load historical data
hist_db = Path.home() / 'Projects' / 'Chad_Volume_tracker' / 'trading_data.db'
conn = sqlite3.connect(hist_db)
cursor = conn.cursor()

# Get all 1-minute candles
cursor.execute("""
    SELECT timestamp, open, high, low, close, volume
    FROM candles
    WHERE product = 'ETH-USD' AND granularity = 1
    ORDER BY timestamp
""")

# Analyze by hour
hourly_stats = defaultdict(lambda: {
    'candles': 0,
    'opportunities': 0,
    'total_volatility': 0,
    'total_volume': 0
})

dow_stats = defaultdict(lambda: {
    'candles': 0,
    'opportunities': 0,
    'total_volatility': 0
})

total_candles = 0
total_opportunities = 0

for row in cursor.fetchall():
    timestamp, open_price, high, low, close, volume = row
    
    # Parse timestamp (UNIX timestamp in seconds)
    dt = datetime.fromtimestamp(timestamp)
    hour = dt.hour
    dow = dt.weekday()  # 0=Monday
    
    # Calculate indicators
    price_change_pct = abs((close - open_price) / open_price * 100)
    range_pct = (high - low) / open_price * 100
    
    # Is this a scalping opportunity? (>0.3% range + clear direction)
    is_opportunity = (range_pct > 0.3 and price_change_pct > 0.15)
    
    # Update hourly stats
    hourly_stats[hour]['candles'] += 1
    hourly_stats[hour]['opportunities'] += 1 if is_opportunity else 0
    hourly_stats[hour]['total_volatility'] += range_pct
    hourly_stats[hour]['total_volume'] += volume
    
    # Update DOW stats
    dow_stats[dow]['candles'] += 1
    dow_stats[dow]['opportunities'] += 1 if is_opportunity else 0
    dow_stats[dow]['total_volatility'] += range_pct
    
    total_candles += 1
    total_opportunities += 1 if is_opportunity else 0

conn.close()

# Calculate averages and sort
hourly_results = []
for hour in range(24):
    stats = hourly_stats[hour]
    if stats['candles'] > 0:
        opp_rate = (stats['opportunities'] / stats['candles']) * 100
        avg_vol = stats['total_volatility'] / stats['candles']
        avg_volume = stats['total_volume'] / stats['candles']
        
        hourly_results.append({
            'hour': hour,
            'candles': stats['candles'],
            'opportunities': stats['opportunities'],
            'opp_rate': opp_rate,
            'avg_volatility': avg_vol,
            'avg_volume': avg_volume
        })

# Sort by opportunity rate
hourly_results.sort(key=lambda x: x['opp_rate'], reverse=True)

# Print results
print("=" * 80)
print("ETH-USD OPTIMAL TRADING WINDOWS (based on momentum opportunities)")
print("=" * 80)
print(f"Data: {total_candles:,} 1-minute candles")
print(f"Total opportunities: {total_opportunities:,} ({(total_opportunities/total_candles)*100:.1f}%)")
print()
print("Ranked by opportunity rate (>0.3% range + clear direction):")
print()
print(f"{'Hour':>6} {'Candles':>8} {'Opps':>8} {'Rate%':>8} {'AvgVol%':>10}")
print("-" * 50)
for result in hourly_results:
    print(f"{result['hour']:02d}:00  {result['candles']:>8,} {result['opportunities']:>8,} {result['opp_rate']:>7.1f}% {result['avg_volatility']:>9.2f}%")

print()
print("=" * 80)
print("BEST CONSECUTIVE 3-HOUR WINDOWS:")
print("=" * 80)

# Find best 3-hour windows
windows = []
for start_hour in range(22):  # 0-21
    window_candles = []
    window_opps = []
    
    for hour in range(start_hour, start_hour + 3):
        stats = hourly_stats[hour]
        if stats['candles'] > 0:
            window_candles.append(stats['candles'])
            window_opps.append(stats['opportunities'])
    
    if window_candles:
        total_candles_window = sum(window_candles)
        total_opps_window = sum(window_opps)
        opp_rate = (total_opps_window / total_candles_window) * 100
        
        windows.append({
            'window': f"{start_hour:02d}:00-{(start_hour+3):02d}:00",
            'opp_rate': opp_rate,
            'opportunities': total_opps_window,
            'candles': total_candles_window
        })

windows.sort(key=lambda x: x['opp_rate'], reverse=True)

print(f"{'Window':>14} {'Opps':>8} {'Candles':>10} {'Rate%':>8}")
print("-" * 50)
for w in windows[:10]:
    print(f"{w['window']:>14} {w['opportunities']:>8,} {w['candles']:>10,} {w['opp_rate']:>7.1f}%")

print()
print("=" * 80)
print("BY DAY OF WEEK:")
print("=" * 80)
dow_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
print(f"{'Day':>12} {'Candles':>10} {'Opps':>8} {'Rate%':>8}")
print("-" * 50)
for dow in range(7):
    stats = dow_stats[dow]
    if stats['candles'] > 0:
        opp_rate = (stats['opportunities'] / stats['candles']) * 100
        print(f"{dow_names[dow]:>12} {stats['candles']:>10,} {stats['opportunities']:>8,} {opp_rate:>7.1f}%")

print()
print("=" * 80)
print("RECOMMENDATIONS:")
print("=" * 80)
top_5_hours = [h['hour'] for h in hourly_results[:5]]
print(f"Top 5 hours: {', '.join([f'{h:02d}:00' for h in top_5_hours])}")
print(f"Best 3-hour window: {windows[0]['window']} ({windows[0]['opp_rate']:.1f}% opp rate)")
print()

# Check Asia/Europe
asia_hours = [18, 19, 20]  # 6pm-9pm EST
europe_hours = [3, 4, 5]  # 3am-6am EST

asia_in_top = any(h in top_5_hours for h in asia_hours)
europe_in_top = any(h in top_5_hours for h in europe_hours)

print(f"Asia hours (18:00-21:00): {'✅ IN TOP 5' if asia_in_top else '❌ Not in top 5'}")
print(f"Europe hours (03:00-06:00): {'✅ IN TOP 5' if europe_in_top else '❌ Not in top 5'}")
