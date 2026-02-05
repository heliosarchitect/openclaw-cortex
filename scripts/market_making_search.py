#!/usr/bin/env python3
"""
Market Making Parameter Search

Tests combinations of:
- Max hold time (30s, 60s, 90s, 120s)
- Spread threshold (only trade when tight enough)
- Exit urgency (force exit if limit doesn't fill)
- Inventory limits

Based on insight: Golden hour = 30-second holds, Bad hours = 48-minute holds
"""
import sqlite3
import sys
from datetime import datetime, timedelta
from itertools import product
import json

DB_PATH = '/home/bonsaihorn/Projects/Chad_Volume_tracker/trading_data.db'

# Parameter space to search
PARAM_SPACE = {
    'max_hold_seconds': [30, 60, 90, 120, 180],
    'spread_threshold_pct': [0.05, 0.10, 0.15, 0.20, 0.30],
    'force_exit_after_seconds': [20, 30, 45, 60],
    'max_positions': [2, 4, 6, 8]
}

def load_historical_candles():
    """Load minute candles from Aug-Nov 2025"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get schema first
    cursor.execute("PRAGMA table_info(candles)")
    columns = [col[1] for col in cursor.fetchall()]
    
    # Adjust query based on actual columns
    if 'timestamp' in columns:
        time_col = 'timestamp'
    elif 'time' in columns:
        time_col = 'time'
    else:
        print(f'Available columns: {columns}')
        return []
    
    cursor.execute(f'''
        SELECT {time_col}, open, high, low, close, volume
        FROM candles
        ORDER BY {time_col} ASC
    ''')
    
    candles = cursor.fetchall()
    conn.close()
    
    return [
        {
            'time': c[0],
            'open': c[1],
            'high': c[2],
            'low': c[3],
            'close': c[4],
            'volume': c[5]
        }
        for c in candles
    ]

def calculate_spread(candle):
    """Estimate bid-ask spread from candle range"""
    range_dollars = candle['high'] - candle['low']
    mid_price = (candle['high'] + candle['low']) / 2
    spread_pct = (range_dollars / mid_price) * 100 if mid_price > 0 else 999
    return spread_pct

def simulate_market_making(candles, params):
    """
    Simulate market-making with given parameters
    
    Strategy:
    1. Enter when spread < threshold
    2. Place limit sell at mid + half spread
    3. Exit after max_hold_seconds if not filled
    4. Enforce position limits
    """
    max_hold = params['max_hold_seconds']
    spread_threshold = params['spread_threshold_pct']
    force_exit = params['force_exit_after_seconds']
    max_positions = params['max_positions']
    
    positions = []
    trades = []
    capital = 2500.0
    
    for i, candle in enumerate(candles):
        current_time = candle['time']
        price = candle['close']
        spread_pct = calculate_spread(candle)
        
        # Exit positions that hit max hold time
        for pos in positions[:]:
            # Handle Unix timestamps
            entry_ts = pos['entry_time']
            current_ts = current_time
            
            # Convert to seconds if needed
            if isinstance(entry_ts, (int, float)):
                entry_seconds = entry_ts
            else:
                entry_seconds = float(entry_ts)
                
            if isinstance(current_ts, (int, float)):
                current_seconds = current_ts
            else:
                current_seconds = float(current_ts)
            
            hold_seconds = current_seconds - entry_seconds
            
            # Force exit if held too long
            if hold_seconds >= max_hold:
                exit_price = price
                pnl = (exit_price - pos['entry_price']) * pos['size'] - 0.02  # fees
                
                capital += pos['entry_price'] * pos['size']  # Return capital
                capital += pnl  # Add profit/loss
                
                trades.append({
                    'entry_time': pos['entry_time'],
                    'exit_time': current_time,
                    'hold_seconds': hold_seconds,
                    'entry_price': pos['entry_price'],
                    'exit_price': exit_price,
                    'pnl': pnl,
                    'reason': 'max_hold'
                })
                
                positions.remove(pos)
                continue
            
            # Check if limit sell would have filled
            if price >= pos['target_price'] and hold_seconds >= 10:  # Min 10 sec hold
                exit_price = pos['target_price']
                pnl = (exit_price - pos['entry_price']) * pos['size'] - 0.02
                
                capital += pos['entry_price'] * pos['size']
                capital += pnl
                
                trades.append({
                    'entry_time': pos['entry_time'],
                    'exit_time': current_time,
                    'hold_seconds': hold_seconds,
                    'entry_price': pos['entry_price'],
                    'exit_price': exit_price,
                    'pnl': pnl,
                    'reason': 'target_hit'
                })
                
                positions.remove(pos)
        
        # Enter new position if conditions met
        if (len(positions) < max_positions and 
            spread_pct < spread_threshold and
            capital > 50):
            
            entry_price = price
            size = min(50 / entry_price, (capital * 0.2) / entry_price)  # 20% of capital per trade
            
            if size * entry_price < capital:
                # Calculate target (capture half the spread)
                target_price = entry_price * (1 + (spread_pct / 200))  # Half spread
                
                positions.append({
                    'entry_time': current_time,
                    'entry_price': entry_price,
                    'target_price': target_price,
                    'size': size
                })
                
                capital -= entry_price * size
    
    # Close remaining positions at final price
    if candles:
        final_price = candles[-1]['close']
        for pos in positions:
            pnl = (final_price - pos['entry_price']) * pos['size'] - 0.02
            capital += pos['entry_price'] * pos['size'] + pnl
    
    # Calculate metrics
    total_pnl = capital - 2500.0
    wins = sum(1 for t in trades if t['pnl'] > 0)
    losses = sum(1 for t in trades if t['pnl'] < 0)
    win_rate = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0
    
    avg_hold = sum(t['hold_seconds'] for t in trades) / len(trades) if trades else 0
    
    return {
        'params': params,
        'total_pnl': total_pnl,
        'total_trades': len(trades),
        'win_rate': win_rate,
        'wins': wins,
        'losses': losses,
        'avg_hold_seconds': avg_hold,
        'final_capital': capital
    }

def main():
    print('🔍 Market Making Parameter Search')
    print('=' * 80)
    
    # Load historical data
    print('📊 Loading historical candles...')
    candles = load_historical_candles()
    
    if not candles:
        print('❌ No candles loaded - check database')
        return
    
    print(f'✅ Loaded {len(candles)} candles')
    print(f'   Range: {candles[0]["time"]} to {candles[-1]["time"]}')
    
    # Generate parameter combinations
    param_combinations = [
        {
            'max_hold_seconds': mh,
            'spread_threshold_pct': st,
            'force_exit_after_seconds': fe,
            'max_positions': mp
        }
        for mh, st, fe, mp in product(
            PARAM_SPACE['max_hold_seconds'],
            PARAM_SPACE['spread_threshold_pct'],
            PARAM_SPACE['force_exit_after_seconds'],
            PARAM_SPACE['max_positions']
        )
    ]
    
    print(f'\n🔬 Testing {len(param_combinations)} parameter combinations...')
    
    results = []
    for i, params in enumerate(param_combinations):
        if i % 20 == 0:
            print(f'   Progress: {i}/{len(param_combinations)} ({i/len(param_combinations)*100:.1f}%)')
        
        result = simulate_market_making(candles, params)
        results.append(result)
    
    # Sort by profitability
    results.sort(key=lambda r: r['total_pnl'], reverse=True)
    
    # Show top 10
    print('\n🏆 Top 10 Parameter Sets:')
    print('=' * 80)
    print(f'{"Rank":<6} {"P/L":<10} {"Trades":<8} {"WR":<8} {"Hold":<10} {"Parameters"}')
    print('-' * 80)
    
    for i, r in enumerate(results[:10], 1):
        p = r['params']
        param_str = f"hold={p['max_hold_seconds']}s spread<{p['spread_threshold_pct']}% max_pos={p['max_positions']}"
        
        print(f'{i:<6} ${r["total_pnl"]:>7.2f}  {r["total_trades"]:<8} {r["win_rate"]:>5.1f}%   '
              f'{r["avg_hold_seconds"]/60:>5.1f}min   {param_str}')
    
    # Save results
    output_file = '/home/bonsaihorn/.openclaw/workspace/market_making_results.json'
    with open(output_file, 'w') as f:
        json.dump(results[:50], f, indent=2)
    
    print(f'\n✅ Full results saved to: {output_file}')
    
    # Show best strategy
    best = results[0]
    print(f'\n🌟 Best Strategy:')
    print(f'   Max hold: {best["params"]["max_hold_seconds"]} seconds')
    print(f'   Spread threshold: {best["params"]["spread_threshold_pct"]}%')
    print(f'   Max positions: {best["params"]["max_positions"]}')
    print(f'   → Profit: ${best["total_pnl"]:.2f}')
    print(f'   → Win rate: {best["win_rate"]:.1f}%')
    print(f'   → Avg hold: {best["avg_hold_seconds"]/60:.1f} minutes')

if __name__ == '__main__':
    main()
