#!/usr/bin/env python3
"""
Market Making Parameter Search - FIXED VERSION

Proper capital tracking, fees, and sanity checks.
"""
import sqlite3
import sys
from datetime import datetime
from itertools import product
import json

DB_PATH = '/home/bonsaihorn/Projects/Chad_Volume_tracker/trading_data.db'

# Smaller parameter space for faster testing
PARAM_SPACE = {
    'max_hold_seconds': [30, 60, 120],
    'spread_threshold_pct': [0.10, 0.20, 0.30],
    'max_positions': [2, 4, 6]
}

FEE_RATE = 0.001  # 0.1% per trade (0.2% round trip)

def load_sample_candles(limit=10000):
    """Load a sample of candles for faster testing"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(candles)")
    columns = [col[1] for col in cursor.fetchall()]
    
    time_col = 'timestamp' if 'timestamp' in columns else 'time'
    
    # Get ETH-USD candles only
    cursor.execute(f'''
        SELECT {time_col}, open, high, low, close, volume
        FROM candles
        WHERE product = 'ETH-USD'
        ORDER BY {time_col} ASC
        LIMIT {limit} OFFSET 10000
    ''')
    
    candles = cursor.fetchall()
    conn.close()
    
    return [
        {
            'time': c[0],
            'open': float(c[1]),
            'high': float(c[2]),
            'low': float(c[3]),
            'close': float(c[4]),
            'volume': float(c[5])
        }
        for c in candles
    ]

def calculate_spread_pct(candle):
    """Estimate bid-ask spread from candle range"""
    range_dollars = candle['high'] - candle['low']
    mid_price = (candle['high'] + candle['low']) / 2
    return (range_dollars / mid_price * 100) if mid_price > 0 else 999

def simulate_market_making(candles, params):
    """
    Simulate market-making with proper capital tracking
    """
    max_hold = params['max_hold_seconds']
    spread_threshold = params['spread_threshold_pct']
    max_positions = params['max_positions']
    
    positions = []
    trades = []
    capital = 2500.0
    starting_capital = 2500.0
    
    POSITION_SIZE_USD = 50.0  # Fixed $50 per position
    
    for i, candle in enumerate(candles):
        current_time = candle['time']
        price = candle['close']
        spread_pct = calculate_spread_pct(candle)
        
        # Exit positions that hit max hold time
        for pos in positions[:]:
            entry_ts = float(pos['entry_time'])
            current_ts = float(current_time)
            hold_seconds = current_ts - entry_ts
            
            # Force exit if held too long
            if hold_seconds >= max_hold:
                exit_price = price
                cost_basis = pos['entry_price'] * pos['size']
                proceeds = exit_price * pos['size']
                
                # Calculate P&L with fees
                entry_fee = cost_basis * FEE_RATE
                exit_fee = proceeds * FEE_RATE
                pnl = proceeds - cost_basis - entry_fee - exit_fee
                
                capital += proceeds - exit_fee
                
                trades.append({
                    'hold_seconds': hold_seconds,
                    'entry_price': pos['entry_price'],
                    'exit_price': exit_price,
                    'pnl': pnl,
                    'reason': 'max_hold'
                })
                
                positions.remove(pos)
                continue
            
            # Check if limit sell would have filled
            if price >= pos['target_price'] and hold_seconds >= 10:
                exit_price = pos['target_price']
                cost_basis = pos['entry_price'] * pos['size']
                proceeds = exit_price * pos['size']
                
                entry_fee = cost_basis * FEE_RATE
                exit_fee = proceeds * FEE_RATE
                pnl = proceeds - cost_basis - entry_fee - exit_fee
                
                capital += proceeds - exit_fee
                
                trades.append({
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
            capital > POSITION_SIZE_USD * 2):  # Need 2x position size as buffer
            
            entry_price = price
            size = POSITION_SIZE_USD / entry_price
            cost = entry_price * size
            entry_fee = cost * FEE_RATE
            total_cost = cost + entry_fee
            
            if total_cost < capital:
                # Calculate target (capture half the spread)
                target_price = entry_price * (1 + (spread_pct / 200))
                
                positions.append({
                    'entry_time': current_time,
                    'entry_price': entry_price,
                    'target_price': target_price,
                    'size': size
                })
                
                capital -= total_cost
    
    # Close remaining positions at final price
    if candles:
        final_price = candles[-1]['close']
        for pos in positions:
            cost_basis = pos['entry_price'] * pos['size']
            proceeds = final_price * pos['size']
            
            entry_fee = cost_basis * FEE_RATE
            exit_fee = proceeds * FEE_RATE
            pnl = proceeds - cost_basis - entry_fee - exit_fee
            
            capital += proceeds - exit_fee
    
    # Calculate metrics
    total_pnl = capital - starting_capital
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
    print('🔍 Market Making Parameter Search (FIXED)')
    print('=' * 80)
    
    # Load sample data
    print('📊 Loading sample candles...')
    candles = load_sample_candles(limit=10000)
    
    if not candles:
        print('❌ No candles loaded')
        return
    
    print(f'✅ Loaded {len(candles)} candles')
    print(f'   Starting capital: $2,500')
    print(f'   Fee rate: {FEE_RATE*100:.1f}% per side')
    
    # Generate parameter combinations
    param_combinations = [
        {
            'max_hold_seconds': mh,
            'spread_threshold_pct': st,
            'max_positions': mp
        }
        for mh, st, mp in product(
            PARAM_SPACE['max_hold_seconds'],
            PARAM_SPACE['spread_threshold_pct'],
            PARAM_SPACE['max_positions']
        )
    ]
    
    print(f'\n🔬 Testing {len(param_combinations)} parameter combinations...')
    
    results = []
    for i, params in enumerate(param_combinations):
        result = simulate_market_making(candles, params)
        results.append(result)
        
        # Sanity check
        if abs(result['total_pnl']) > 50000:
            print(f'\n⚠️  SANITY CHECK FAILED: P/L = ${result["total_pnl"]:.2f}')
            print(f'   Params: {params}')
            print(f'   Something is still broken!')
            return
    
    # Sort by profitability
    results.sort(key=lambda r: r['total_pnl'], reverse=True)
    
    # Show top 10
    print('\n🏆 Top 10 Parameter Sets:')
    print('=' * 80)
    print(f'{"Rank":<6} {"P/L":<10} {"Trades":<8} {"WR":<8} {"Hold":<10} {"Parameters"}')
    print('-' * 80)
    
    for i, r in enumerate(results[:10], 1):
        p = r['params']
        param_str = f"hold={p['max_hold_seconds']}s spread<{p['spread_threshold_pct']}% pos={p['max_positions']}"
        
        print(f'{i:<6} ${r["total_pnl"]:>7.2f}  {r["total_trades"]:<8} {r["win_rate"]:>5.1f}%   '
              f'{r["avg_hold_seconds"]/60:>5.1f}min   {param_str}')
    
    # Show worst for comparison
    print('\n❌ Worst 3 Parameter Sets:')
    print('-' * 80)
    for i, r in enumerate(results[-3:], 1):
        p = r['params']
        param_str = f"hold={p['max_hold_seconds']}s spread<{p['spread_threshold_pct']}% pos={p['max_positions']}"
        
        print(f'   ${r["total_pnl"]:>7.2f}  {r["total_trades"]:<8} {r["win_rate"]:>5.1f}%   '
              f'{r["avg_hold_seconds"]/60:>5.1f}min   {param_str}')
    
    # Save results
    output_file = '/home/bonsaihorn/.openclaw/workspace/market_making_results_fixed.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f'\n✅ Full results saved to: {output_file}')
    
    # Show best strategy details
    best = results[0]
    print(f'\n🌟 Best Strategy:')
    print(f'   Max hold: {best["params"]["max_hold_seconds"]} seconds')
    print(f'   Spread threshold: {best["params"]["spread_threshold_pct"]}%')
    print(f'   Max positions: {best["params"]["max_positions"]}')
    print(f'   → Profit: ${best["total_pnl"]:.2f} ({best["total_pnl"]/2500*100:+.1f}%)')
    print(f'   → Win rate: {best["win_rate"]:.1f}%')
    print(f'   → Trades: {best["total_trades"]}')
    print(f'   → Avg hold: {best["avg_hold_seconds"]/60:.1f} minutes')

if __name__ == '__main__':
    main()
