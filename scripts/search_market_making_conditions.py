#!/usr/bin/env python3
"""
Market Making Condition Search - Find WHEN to trade, not WHAT indicators to use

Based on golden hour discovery:
- Noon: 81.6% WR with 30s holds = proper market making
- Other hours: 48% WR with 48min holds = directional gambling

Search for conditions that enable successful market making:
1. Spread thresholds (bid/ask spread %)
2. Volume levels (higher volume = tighter spreads)
3. Time-of-day patterns
4. Volatility windows
5. Quick exit timing (30-60s max)
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path.home() / "Projects/Chad2930/Chad_Profit_Bot/live_trading.db"
MARKET_DB = Path.home() / "Projects/Chad2930/Chad_Profit_Bot/market_data.db"

def load_market_candles(hours=72):
    """Load Level2 market data with bid/ask/spread info"""
    conn = sqlite3.connect(MARKET_DB)
    
    cutoff = datetime.now() - timedelta(hours=hours)
    cutoff_ts = int(cutoff.timestamp())
    
    query = """
        SELECT 
            timestamp,
            open, high, low, close, volume,
            best_bid, best_ask, avg_spread_pct,
            bid_size, ask_size
        FROM market_candles
        WHERE timestamp > ?
        ORDER BY timestamp ASC
    """
    
    df = pd.read_sql_query(query, conn, params=(cutoff_ts,))
    conn.close()
    
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
    df['hour'] = df['datetime'].dt.hour
    df['minute'] = df['datetime'].dt.minute
    
    return df

def calculate_conditions(df):
    """Calculate market-making condition indicators"""
    
    # Spread metrics
    df['spread_tight'] = df['avg_spread_pct'] < 0.3
    df['spread_loose'] = df['avg_spread_pct'] > 0.5
    
    # Volume metrics (rolling average)
    df['volume_5m'] = df['volume'].rolling(5).mean()
    df['volume_15m'] = df['volume'].rolling(15).mean()
    df['volume_high'] = df['volume'] > df['volume_15m']
    
    # Volatility metrics
    df['price_range'] = df['high'] - df['low']
    df['volatility_5m'] = df['price_range'].rolling(5).std()
    df['volatility_low'] = df['volatility_5m'] < df['volatility_5m'].quantile(0.33)
    
    # Order book depth (bid/ask sizes)
    df['book_balanced'] = (df['bid_size'] / (df['bid_size'] + df['ask_size'])).between(0.4, 0.6)
    
    # Time patterns (detect golden hour characteristics)
    df['is_morning'] = df['hour'].between(9, 11)
    df['is_noon'] = df['hour'] == 12
    df['is_afternoon'] = df['hour'].between(13, 17)
    
    return df

def test_condition_combination(df, conditions):
    """Test a specific combination of market-making conditions"""
    
    mask = pd.Series([True] * len(df), index=df.index)
    
    for cond_name, cond_value in conditions.items():
        if cond_value and cond_name in df.columns:
            mask &= df[cond_name]
    
    matching_candles = df[mask]
    
    if len(matching_candles) < 10:
        return None  # Not enough data
    
    # Simulate market-making performance
    # Assume: Buy at bid, sell at ask after 30-60 seconds
    avg_spread = matching_candles['avg_spread_pct'].mean()
    spread_volatility = matching_candles['avg_spread_pct'].std()
    
    # Estimate win rate based on spread stability
    # Tighter, more stable spreads = higher success rate
    estimated_wr = min(95, 50 + (0.5 / max(avg_spread, 0.01)) * 10 - spread_volatility * 20)
    
    # Estimate profit per trade (spread capture minus fees)
    fee_pct = 0.6  # Coinbase Advanced Trade maker fee
    net_spread = avg_spread - fee_pct
    
    trades_per_day = len(matching_candles) / (len(df) / 1440)  # candles per day
    
    result = {
        'conditions': conditions,
        'candles_matched': len(matching_candles),
        'avg_spread_pct': avg_spread,
        'spread_volatility': spread_volatility,
        'estimated_wr': estimated_wr,
        'net_spread_pct': net_spread,
        'trades_per_day': trades_per_day,
        'viable': net_spread > 0 and estimated_wr > 70
    }
    
    return result

def search_combinations(df):
    """Search through combinations of conditions"""
    
    print("🔍 Searching for market-making conditions...")
    print(f"📊 Analyzing {len(df)} 1-minute candles")
    print()
    
    # Condition categories to test
    spread_conditions = [
        {'spread_tight': True},
        {'spread_tight': True, 'spread_loose': False},
    ]
    
    volume_conditions = [
        {},
        {'volume_high': True},
    ]
    
    time_conditions = [
        {},
        {'is_noon': True},
        {'is_morning': True},
        {'is_afternoon': True},
    ]
    
    volatility_conditions = [
        {},
        {'volatility_low': True},
    ]
    
    book_conditions = [
        {},
        {'book_balanced': True},
    ]
    
    results = []
    
    total_combinations = (len(spread_conditions) * len(volume_conditions) * 
                         len(time_conditions) * len(volatility_conditions) * 
                         len(book_conditions))
    
    tested = 0
    
    for spread_cond in spread_conditions:
        for volume_cond in volume_conditions:
            for time_cond in time_conditions:
                for volatility_cond in volatility_conditions:
                    for book_cond in book_conditions:
                        conditions = {}
                        conditions.update(spread_cond)
                        conditions.update(volume_cond)
                        conditions.update(time_cond)
                        conditions.update(volatility_cond)
                        conditions.update(book_cond)
                        
                        result = test_condition_combination(df, conditions)
                        if result:
                            results.append(result)
                        
                        tested += 1
                        if tested % 10 == 0:
                            print(f"Progress: {tested}/{total_combinations} combinations tested...")
    
    return results

def main():
    print("=" * 60)
    print("Market Making Condition Search")
    print("Goal: Find WHEN to trade (conditions), not WHAT to trade (indicators)")
    print("=" * 60)
    print()
    
    # Load market data
    print("📥 Loading Level2 market data...")
    df = load_market_candles(hours=72)
    
    if len(df) == 0:
        print("❌ No market data found. Is the Level2 WebSocket running?")
        return
    
    print(f"✅ Loaded {len(df)} candles")
    print(f"   Time range: {df['datetime'].min()} to {df['datetime'].max()}")
    print()
    
    # Calculate condition indicators
    print("🔧 Calculating market conditions...")
    df = calculate_conditions(df)
    print("✅ Conditions calculated")
    print()
    
    # Search for viable combinations
    results = search_combinations(df)
    
    # Filter and sort results
    viable_results = [r for r in results if r['viable']]
    viable_results.sort(key=lambda x: x['estimated_wr'], reverse=True)
    
    print()
    print("=" * 60)
    print(f"📊 Found {len(viable_results)} viable market-making conditions")
    print("=" * 60)
    print()
    
    for i, result in enumerate(viable_results[:10], 1):
        print(f"\n{i}. Estimated WR: {result['estimated_wr']:.1f}%")
        print(f"   Avg Spread: {result['avg_spread_pct']:.3f}%")
        print(f"   Net Spread: {result['net_spread_pct']:.3f}%")
        print(f"   Trades/Day: {result['trades_per_day']:.0f}")
        print(f"   Matched: {result['candles_matched']} candles")
        
        active_conditions = [k for k, v in result['conditions'].items() if v]
        if active_conditions:
            print(f"   Conditions: {', '.join(active_conditions)}")
        else:
            print(f"   Conditions: (none - always trade)")
    
    # Save top results
    output_file = Path.home() / ".openclaw/workspace/market_making_conditions.txt"
    with open(output_file, 'w') as f:
        f.write("Market Making Condition Search Results\n")
        f.write(f"Generated: {datetime.now()}\n")
        f.write("=" * 60 + "\n\n")
        
        for i, result in enumerate(viable_results[:20], 1):
            f.write(f"{i}. Estimated WR: {result['estimated_wr']:.1f}%\n")
            f.write(f"   Avg Spread: {result['avg_spread_pct']:.3f}%\n")
            f.write(f"   Net Spread: {result['net_spread_pct']:.3f}%\n")
            f.write(f"   Trades/Day: {result['trades_per_day']:.0f}\n")
            f.write(f"   Matched: {result['candles_matched']} candles\n")
            
            active_conditions = [k for k, v in result['conditions'].items() if v]
            if active_conditions:
                f.write(f"   Conditions: {', '.join(active_conditions)}\n")
            else:
                f.write(f"   Conditions: (none - always trade)\n")
            f.write("\n")
    
    print(f"\n💾 Results saved to: {output_file}")

if __name__ == "__main__":
    main()
