#!/usr/bin/env python3
"""
Analyze historical fill data to reverse-engineer market microstructure.
"""

import sqlite3
import json
from datetime import datetime
from collections import defaultdict
import statistics

DB_PATH = "/home/bonsaihorn/Projects/Chad_Volume_tracker/trading_data.db"

def connect_db():
    return sqlite3.connect(DB_PATH)

def analyze_fill_density():
    """Find periods with highest fill density (>5 fills/sec)"""
    conn = connect_db()
    cursor = conn.cursor()
    
    # Get all fills ordered by trade_time, filter out zero-price fills
    cursor.execute("""
        SELECT trade_time, product, side, price, size 
        FROM fills 
        WHERE price > 0 AND size > 0
        ORDER BY trade_time
    """)
    
    fills = cursor.fetchall()
    conn.close()
    
    print(f"Total fills: {len(fills)}")
    
    # Group fills by second
    fills_by_second = defaultdict(list)
    for fill in fills:
        timestamp_str = fill[0]
        # Parse timestamp and truncate to second
        try:
            dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            second_key = dt.strftime('%Y-%m-%d %H:%M:%S')
            fills_by_second[second_key].append(fill)
        except Exception as e:
            print(f"Error parsing timestamp {timestamp_str}: {e}")
            continue
    
    # Find high-density periods (>5 fills/sec)
    high_density_periods = []
    for second, fills_in_second in fills_by_second.items():
        fill_count = len(fills_in_second)
        if fill_count > 5:
            high_density_periods.append({
                'timestamp': second,
                'fill_count': fill_count,
                'fills': fills_in_second
            })
    
    # Sort by fill count
    high_density_periods.sort(key=lambda x: x['fill_count'], reverse=True)
    
    print(f"\nHigh-density periods (>5 fills/sec): {len(high_density_periods)}")
    if high_density_periods:
        print(f"Highest: {high_density_periods[0]['fill_count']} fills/sec at {high_density_periods[0]['timestamp']}")
    
    return fills, fills_by_second, high_density_periods

def calculate_spreads(fills):
    """Calculate typical spread from consecutive buy/sell prices"""
    # Group by symbol
    by_symbol = defaultdict(list)
    for fill in fills:
        timestamp, symbol, side, price, size = fill
        by_symbol[symbol].append({
            'timestamp': timestamp,
            'side': side,
            'price': float(price),
            'size': float(size)
        })
    
    spread_data = {}
    for symbol, symbol_fills in by_symbol.items():
        # Sort by timestamp
        symbol_fills.sort(key=lambda x: x['timestamp'])
        
        # Find consecutive buy/sell pairs
        spreads = []
        for i in range(len(symbol_fills) - 1):
            current = symbol_fills[i]
            next_fill = symbol_fills[i + 1]
            
            # If buy followed by sell (or vice versa), calculate spread
            if current['side'] != next_fill['side']:
                if current['side'] == 'buy':
                    # Spread = sell price - buy price
                    spread_pct = ((next_fill['price'] - current['price']) / current['price']) * 100
                else:
                    # Spread = buy price - sell price (for sell first, then buy)
                    spread_pct = ((current['price'] - next_fill['price']) / next_fill['price']) * 100
                
                spreads.append(spread_pct)
        
        if spreads:
            spread_data[symbol] = {
                'avg_spread_pct': statistics.mean(spreads),
                'median_spread_pct': statistics.median(spreads),
                'min_spread_pct': min(spreads),
                'max_spread_pct': max(spreads),
                'sample_size': len(spreads)
            }
    
    return spread_data

def analyze_high_volume_profits(high_density_periods):
    """Measure average profit per fill during high-volume periods"""
    profits = []
    
    for period in high_density_periods:
        fills_in_period = period['fills']
        
        # Group by symbol
        by_symbol = defaultdict(list)
        for fill in fills_in_period:
            timestamp, symbol, side, price, size = fill
            by_symbol[symbol].append({
                'side': side,
                'price': float(price),
                'size': float(size)
            })
        
        # Calculate profit for each symbol in this period
        for symbol, symbol_fills in by_symbol.items():
            buys = [f for f in symbol_fills if f['side'] == 'buy']
            sells = [f for f in symbol_fills if f['side'] == 'sell']
            
            if buys and sells:
                avg_buy_price = statistics.mean([f['price'] for f in buys])
                avg_sell_price = statistics.mean([f['price'] for f in sells])
                profit_pct = ((avg_sell_price - avg_buy_price) / avg_buy_price) * 100
                profits.append(profit_pct)
    
    if profits:
        return {
            'avg_profit_pct': statistics.mean(profits),
            'median_profit_pct': statistics.median(profits),
            'total_periods_analyzed': len(high_density_periods)
        }
    return None

def analyze_nov_15_event(fills_by_second):
    """Identify what conditions enabled 13.4 fills/sec sustained (Nov 15)"""
    # Find Nov 15 data (check both 2024 and 2025)
    nov_15_periods = []
    for second, fills_in_second in fills_by_second.items():
        if '-11-15' in second:  # Match any year
            nov_15_periods.append({
                'timestamp': second,
                'fill_count': len(fills_in_second),
                'fills': fills_in_second
            })
    
    nov_15_periods.sort(key=lambda x: x['fill_count'], reverse=True)
    
    print(f"\nNov 15 analysis:")
    print(f"Total seconds with fills: {len(nov_15_periods)}")
    if nov_15_periods:
        print(f"Peak: {nov_15_periods[0]['fill_count']} fills/sec at {nov_15_periods[0]['timestamp']}")
        
        # Analyze top periods
        top_periods = nov_15_periods[:10]
        symbols_in_top = defaultdict(int)
        for period in top_periods:
            for fill in period['fills']:
                symbol = fill[1]
                symbols_in_top[symbol] += 1
        
        print(f"Symbols in top 10 periods: {dict(symbols_in_top)}")
    
    return nov_15_periods

def extract_patterns(high_density_periods):
    """Extract pattern: what market state allows high-frequency execution?"""
    
    patterns = {
        'symbols_in_high_density': defaultdict(int),
        'avg_fills_per_symbol': {},
        'time_distribution': defaultdict(int),
        'side_balance': defaultdict(int)
    }
    
    for period in high_density_periods:
        # Extract hour for time distribution
        hour = period['timestamp'].split()[1].split(':')[0]
        patterns['time_distribution'][hour] += 1
        
        # Count symbols
        for fill in period['fills']:
            symbol = fill[1]
            side = fill[2]
            patterns['symbols_in_high_density'][symbol] += 1
            patterns['side_balance'][side] += 1
    
    return patterns

def main():
    print("Starting microstructure analysis...")
    print("=" * 60)
    
    # 1. Analyze fill density
    fills, fills_by_second, high_density_periods = analyze_fill_density()
    
    # 2. Calculate spreads
    print("\n" + "=" * 60)
    print("Calculating spreads...")
    spread_data = calculate_spreads(fills)
    print(f"Spread analysis for {len(spread_data)} symbols")
    
    # 3. Analyze profits in high-volume periods
    print("\n" + "=" * 60)
    print("Analyzing high-volume period profits...")
    profit_data = analyze_high_volume_profits(high_density_periods)
    if profit_data:
        print(f"Average profit: {profit_data['avg_profit_pct']:.4f}%")
    
    # 4. Analyze Nov 15 event
    print("\n" + "=" * 60)
    nov_15_data = analyze_nov_15_event(fills_by_second)
    
    # 5. Extract patterns
    print("\n" + "=" * 60)
    print("Extracting patterns...")
    patterns = extract_patterns(high_density_periods)
    
    # Compile results
    results = {
        'summary': {
            'total_fills': len(fills),
            'total_seconds_analyzed': len(fills_by_second),
            'high_density_periods_count': len(high_density_periods),
            'highest_density': high_density_periods[0] if high_density_periods else None
        },
        'high_density_periods': [
            {
                'timestamp': p['timestamp'],
                'fill_count': p['fill_count'],
                'fills_detail': [
                    {'symbol': f[1], 'side': f[2], 'price': float(f[3]), 'size': float(f[4])}
                    for f in p['fills']
                ]
            }
            for p in high_density_periods[:20]  # Top 20
        ],
        'spread_analysis': spread_data,
        'high_volume_profit_analysis': profit_data,
        'nov_15_analysis': {
            'total_periods': len(nov_15_data),
            'peak_period': nov_15_data[0] if nov_15_data else None,
            'top_10_periods': [
                {'timestamp': p['timestamp'], 'fill_count': p['fill_count']}
                for p in nov_15_data[:10]
            ]
        },
        'patterns': {
            'symbols_in_high_density': dict(patterns['symbols_in_high_density']),
            'time_distribution': dict(patterns['time_distribution']),
            'side_balance': patterns['side_balance']
        }
    }
    
    # Write to JSON
    output_path = "/home/bonsaihorn/.openclaw/workspace/microstructure_analysis.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n✓ Analysis complete! Results saved to {output_path}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total fills analyzed: {len(fills)}")
    print(f"High-density periods (>5 fills/sec): {len(high_density_periods)}")
    if high_density_periods:
        top = high_density_periods[0]
        print(f"\nPeak execution rate: {top['fill_count']} fills/sec")
        print(f"Occurred at: {top['timestamp']}")
        
        # Show symbols in peak period
        symbols = defaultdict(int)
        for fill in top['fills']:
            symbols[fill[1]] += 1
        print(f"Symbols involved: {dict(symbols)}")
    
    if spread_data:
        print(f"\nSpread analysis:")
        for symbol, data in list(spread_data.items())[:5]:
            print(f"  {symbol}: avg={data['avg_spread_pct']:.4f}%, median={data['median_spread_pct']:.4f}%")
    
    if profit_data:
        print(f"\nHigh-volume period profitability:")
        print(f"  Average profit: {profit_data['avg_profit_pct']:.4f}%")
        print(f"  Median profit: {profit_data['median_profit_pct']:.4f}%")
    
    print(f"\nMost active hours: {sorted(patterns['time_distribution'].items(), key=lambda x: x[1], reverse=True)[:5]}")
    print(f"Most active symbols: {sorted(patterns['symbols_in_high_density'].items(), key=lambda x: x[1], reverse=True)[:5]}")

if __name__ == '__main__':
    main()
