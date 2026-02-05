#!/usr/bin/env python3
"""
Learn from Today's Trading - Build Better Strategy

Analyzes today's actual trading performance and generates a new strategy
that would have performed better by:
1. Trading only during good conditions
2. Stopping when volatility drops
3. Fewer, higher-quality trades

Uses chronological data (no lookahead bias).
"""
import sqlite3
import sys
from datetime import datetime, timedelta
from collections import defaultdict

DB_PATH = '/home/bonsaihorn/Projects/Chad2930/Chad_Profit_Bot/live_trading.db'

def load_todays_trades():
    """Load all trades from today"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    cursor.execute('''
        SELECT 
            timestamp,
            exit_timestamp,
            price,
            exit_price,
            profit_loss,
            product,
            size
        FROM trades
        WHERE date(timestamp) = ?
        AND profit_loss IS NOT NULL
        ORDER BY timestamp ASC
    ''', (today,))
    
    trades = cursor.fetchall()
    conn.close()
    
    return [
        {
            'entry_time': t[0],
            'exit_time': t[1],
            'entry_price': t[2],
            'exit_price': t[3],
            'profit': t[4],
            'product': t[5],
            'size': t[6]
        }
        for t in trades
    ]

def analyze_hourly_performance(trades):
    """Break down performance by hour to find when strategy failed"""
    hourly_stats = defaultdict(lambda: {'trades': 0, 'wins': 0, 'losses': 0, 'profit': 0.0})
    
    for trade in trades:
        # Parse hour from timestamp
        hour = int(trade['entry_time'][11:13])
        
        hourly_stats[hour]['trades'] += 1
        if trade['profit'] > 0:
            hourly_stats[hour]['wins'] += 1
        else:
            hourly_stats[hour]['losses'] += 1
        hourly_stats[hour]['profit'] += trade['profit']
    
    # Calculate win rates
    for hour, stats in hourly_stats.items():
        total = stats['wins'] + stats['losses']
        stats['win_rate'] = (stats['wins'] / total * 100) if total > 0 else 0
    
    return hourly_stats

def find_stop_trading_signals(hourly_stats):
    """Identify when we should have stopped trading"""
    print('\n📊 Hourly Performance Analysis')
    print('=' * 70)
    print(f'{"Hour":<6} {"Trades":<8} {"WR":<8} {"Profit":<10} {"Decision"}')
    print('-' * 70)
    
    best_hours = []
    bad_hours = []
    
    for hour in sorted(hourly_stats.keys()):
        stats = hourly_stats[hour]
        wr = stats['win_rate']
        profit = stats['profit']
        
        decision = '✅ GOOD'
        if wr < 55:
            decision = '⚠️  WEAK'
            bad_hours.append(hour)
        elif wr > 65:
            best_hours.append(hour)
        
        if wr < 50:
            decision = '❌ STOP'
            
        print(f'{hour:02d}:00  {stats["trades"]:<8} {wr:>5.1f}%   ${profit:>7.2f}   {decision}')
    
    print('=' * 70)
    
    return best_hours, bad_hours

def calculate_what_should_have_done(trades, bad_hours):
    """Calculate P/L if we had stopped trading during bad hours"""
    filtered_trades = [
        t for t in trades 
        if int(t['entry_time'][11:13]) not in bad_hours
    ]
    
    total_profit = sum(t['profit'] for t in filtered_trades)
    wins = sum(1 for t in filtered_trades if t['profit'] > 0)
    losses = sum(1 for t in filtered_trades if t['profit'] < 0)
    win_rate = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0
    
    return {
        'trades': len(filtered_trades),
        'profit': total_profit,
        'win_rate': win_rate,
        'wins': wins,
        'losses': losses
    }

def main():
    print('🧠 Learning from Today\'s Trading Performance')
    print('=' * 70)
    
    # Load today's trades
    trades = load_todays_trades()
    
    if not trades:
        print('❌ No trades found for today')
        return
    
    print(f'📈 Loaded {len(trades)} trades from today')
    
    # Actual performance
    actual_profit = sum(t['profit'] for t in trades)
    actual_wins = sum(1 for t in trades if t['profit'] > 0)
    actual_losses = sum(1 for t in trades if t['profit'] < 0)
    actual_wr = (actual_wins / (actual_wins + actual_losses) * 100)
    
    print(f'\n💰 Actual Performance:')
    print(f'   Trades: {len(trades)}')
    print(f'   Win Rate: {actual_wr:.1f}%')
    print(f'   Profit: ${actual_profit:.2f}')
    
    # Analyze by hour
    hourly_stats = analyze_hourly_performance(trades)
    best_hours, bad_hours = find_stop_trading_signals(hourly_stats)
    
    # Calculate what we should have done
    should_have = calculate_what_should_have_done(trades, bad_hours)
    
    print(f'\n✨ Optimal Strategy (skip bad hours):')
    print(f'   Trades: {should_have["trades"]} (vs {len(trades)})')
    print(f'   Win Rate: {should_have["win_rate"]:.1f}% (vs {actual_wr:.1f}%)')
    print(f'   Profit: ${should_have["profit"]:.2f} (vs ${actual_profit:.2f})')
    print(f'   Improvement: ${should_have["profit"] - actual_profit:+.2f}')
    
    print(f'\n📝 Key Lessons:')
    print(f'   ✅ Good hours: {", ".join([f"{h:02d}:00" for h in best_hours])}')
    print(f'   ❌ Bad hours: {", ".join([f"{h:02d}:00" for h in bad_hours])}')
    print(f'   📊 Trading {len(trades) - should_have["trades"]} fewer trades = ${should_have["profit"] - actual_profit:+.2f}')
    
    print(f'\n💡 Strategy Rules to Add:')
    print(f'   1. Monitor rolling 1-hour win rate')
    print(f'   2. Stop trading if WR drops below 55%')
    print(f'   3. Resume only if 3 consecutive good signals')
    print(f'   4. Max trades per hour: {max(hourly_stats[h]["trades"] for h in best_hours)}')
    
    # Save analysis
    with open('/home/bonsaihorn/.openclaw/workspace/todays_lessons.txt', 'w') as f:
        f.write(f'Analysis of {datetime.now().strftime("%Y-%m-%d")}\n')
        f.write('=' * 70 + '\n\n')
        f.write(f'Actual: {len(trades)} trades, {actual_wr:.1f}% WR, ${actual_profit:.2f}\n')
        f.write(f'Optimal: {should_have["trades"]} trades, {should_have["win_rate"]:.1f}% WR, ${should_have["profit"]:.2f}\n')
        f.write(f'\nBad hours to avoid: {bad_hours}\n')
        f.write(f'Good hours: {best_hours}\n')
    
    print(f'\n✅ Analysis saved to: todays_lessons.txt')

if __name__ == '__main__':
    main()
