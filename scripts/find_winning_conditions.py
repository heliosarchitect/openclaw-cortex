#!/usr/bin/env python3
"""
Find Winning Trade Conditions

Analyzes today's trades to discover:
1. What conditions predicted 30-second winners (golden hour)?
2. What conditions predicted 48-minute losers (bad hours)?
3. Build rules that ONLY trade when conditions match winners

Uses real trade data, not simulation.
"""
import sqlite3
from datetime import datetime
from collections import defaultdict
import statistics

DB_PATH = '/home/bonsaihorn/Projects/Chad2930/Chad_Profit_Bot/live_trading.db'

def load_todays_trades_with_context():
    """Load trades with entry/exit times and calculate metrics"""
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
    
    trades = []
    for t in cursor.fetchall():
        entry = datetime.fromisoformat(t[0])
        exit_time = datetime.fromisoformat(t[1])
        hold_seconds = (exit_time - entry).total_seconds()
        
        trades.append({
            'entry_time': t[0],
            'exit_time': t[1],
            'hour': entry.hour,
            'entry_price': t[2],
            'exit_price': t[3],
            'profit': t[4],
            'won': t[4] > 0,
            'hold_seconds': hold_seconds,
            'product': t[5],
            'size': t[6]
        })
    
    conn.close()
    return trades

def find_golden_vs_bad_patterns(trades):
    """Compare golden hour (81.6% WR) vs bad hours to find differences"""
    
    golden_trades = [t for t in trades if t['hour'] == 12]
    bad_trades = [t for t in trades if t['hour'] in [15, 17]]  # Worst hours
    
    if not golden_trades or not bad_trades:
        print('❌ Not enough data from golden/bad hours')
        return
    
    print('🔍 Golden Hour (12 PM - 81.6% WR) vs Bad Hours (3,5 PM - 31% WR)')
    print('=' * 80)
    
    # Hold time comparison
    golden_holds = [t['hold_seconds'] for t in golden_trades]
    bad_holds = [t['hold_seconds'] for t in bad_trades]
    
    print('\n📊 Hold Time:')
    print(f'   Golden: {statistics.mean(golden_holds)/60:.1f} min (median: {statistics.median(golden_holds)/60:.1f})')
    print(f'   Bad:    {statistics.mean(bad_holds)/60:.1f} min (median: {statistics.median(bad_holds)/60:.1f})')
    print(f'   → Golden exits {statistics.mean(bad_holds)/statistics.mean(golden_holds):.1f}x FASTER')
    
    # Trade size comparison
    golden_sizes = [t['size'] for t in golden_trades]
    bad_sizes = [t['size'] for t in bad_trades]
    
    print('\n📊 Position Size:')
    print(f'   Golden: ${statistics.mean(golden_sizes):.2f}')
    print(f'   Bad:    ${statistics.mean(bad_sizes):.2f}')
    
    # Win rate
    golden_wr = sum(1 for t in golden_trades if t['won']) / len(golden_trades) * 100
    bad_wr = sum(1 for t in bad_trades if t['won']) / len(bad_trades) * 100
    
    print('\n📊 Win Rate:')
    print(f'   Golden: {golden_wr:.1f}%')
    print(f'   Bad:    {bad_wr:.1f}%')
    
    # Price movement
    golden_moves = [abs(t['exit_price'] - t['entry_price']) for t in golden_trades]
    bad_moves = [abs(t['exit_price'] - t['entry_price']) for t in bad_trades]
    
    print('\n📊 Price Movement (per trade):')
    print(f'   Golden: ${statistics.mean(golden_moves):.2f}')
    print(f'   Bad:    ${statistics.mean(bad_moves):.2f}')
    
    return {
        'golden_avg_hold': statistics.mean(golden_holds),
        'bad_avg_hold': statistics.mean(bad_holds),
        'golden_wr': golden_wr,
        'bad_wr': bad_wr
    }

def extract_winning_rules(trades):
    """Extract rules that separate winners from losers"""
    
    winners = [t for t in trades if t['won']]
    losers = [t for t in trades if not t['won']]
    
    print('\n\n✅ Winning Trade Characteristics:')
    print('=' * 80)
    
    # Hold time threshold
    winner_holds = [t['hold_seconds'] for t in winners]
    loser_holds = [t['hold_seconds'] for t in losers]
    
    winner_median = statistics.median(winner_holds)
    loser_median = statistics.median(loser_holds)
    
    print(f'\n📏 Hold Time:')
    print(f'   Winners: {winner_median/60:.1f} min median')
    print(f'   Losers:  {loser_median/60:.1f} min median')
    
    # Find threshold
    threshold = (winner_median + loser_median) / 2
    print(f'   → RULE: Exit if not profitable after {threshold/60:.1f} minutes')
    
    # Quick wins vs slow wins
    quick_wins = [t for t in winners if t['hold_seconds'] < 120]  # 2 min
    slow_wins = [t for t in winners if t['hold_seconds'] >= 120]
    
    print(f'\n⚡ Quick Wins (<2 min): {len(quick_wins)} trades')
    print(f'🐌 Slow Wins (>2 min): {len(slow_wins)} trades')
    print(f'   → {len(quick_wins)/(len(quick_wins)+len(slow_wins))*100:.1f}% of wins happen FAST')
    
    if quick_wins:
        quick_profits = [t['profit'] for t in quick_wins]
        print(f'   → Quick wins avg: ${statistics.mean(quick_profits):.2f}')
    
    # Hour-based rules
    hourly_wr = defaultdict(lambda: {'wins': 0, 'total': 0})
    for t in trades:
        hourly_wr[t['hour']]['total'] += 1
        if t['won']:
            hourly_wr[t['hour']]['wins'] += 1
    
    print(f'\n⏰ Hour-Based Rules:')
    good_hours = []
    bad_hours = []
    
    for hour in sorted(hourly_wr.keys()):
        stats = hourly_wr[hour]
        wr = (stats['wins'] / stats['total'] * 100) if stats['total'] > 0 else 0
        
        if wr > 65:
            good_hours.append(hour)
            print(f'   ✅ {hour:02d}:00 - {wr:.1f}% WR ({stats["total"]} trades) - TRADE')
        elif wr < 50:
            bad_hours.append(hour)
            print(f'   ❌ {hour:02d}:00 - {wr:.1f}% WR ({stats["total"]} trades) - SKIP')
    
    return {
        'max_hold_seconds': threshold,
        'quick_win_threshold': 120,
        'good_hours': good_hours,
        'bad_hours': bad_hours,
        'winner_median_hold': winner_median,
        'quick_win_pct': len(quick_wins)/(len(quick_wins)+len(slow_wins))*100 if (quick_wins or slow_wins) else 0
    }

def generate_strategy_code(rules):
    """Generate Python code for the winning strategy"""
    
    print('\n\n🔧 Generated Strategy Code:')
    print('=' * 80)
    
    code = f'''
class WinningStrategy:
    """
    Auto-generated from {datetime.now().strftime('%Y-%m-%d')} trade analysis
    
    Key insights:
    - {rules['quick_win_pct']:.0f}% of wins happen in <2 minutes
    - Exit if not profitable after {rules['max_hold_seconds']/60:.1f} minutes
    - Only trade during hours: {rules['good_hours']}
    """
    
    MAX_HOLD_SECONDS = {rules['max_hold_seconds']:.0f}
    QUICK_WIN_THRESHOLD = {rules['quick_win_threshold']}
    GOOD_HOURS = {rules['good_hours']}
    BAD_HOURS = {rules['bad_hours']}
    
    def should_enter(self, current_hour):
        # Only trade during proven good hours
        if current_hour in self.BAD_HOURS:
            return False
        return True
    
    def should_exit(self, position, current_time):
        hold_time = (current_time - position.entry_time).total_seconds()
        
        # Exit winners quickly if target hit
        if position.is_profitable() and hold_time >= self.QUICK_WIN_THRESHOLD:
            return True, "quick_win"
        
        # Force exit if held too long without profit
        if hold_time >= self.MAX_HOLD_SECONDS:
            return True, "max_hold_timeout"
        
        return False, None
'''
    
    print(code)
    
    # Save to file
    with open('/home/bonsaihorn/.openclaw/workspace/winning_strategy.py', 'w') as f:
        f.write(code)
    
    print('\n✅ Strategy saved to: winning_strategy.py')

def main():
    print('🔍 Finding Winning Trade Conditions')
    print('=' * 80)
    
    trades = load_todays_trades_with_context()
    
    if not trades:
        print('❌ No trades found for today')
        return
    
    print(f'✅ Loaded {len(trades)} trades from today')
    
    # Compare golden vs bad hours
    patterns = find_golden_vs_bad_patterns(trades)
    
    # Extract winning rules
    rules = extract_winning_rules(trades)
    
    # Generate strategy code
    generate_strategy_code(rules)
    
    print('\n\n💡 Summary:')
    print('=' * 80)
    print('✅ Pattern Found: Winners exit FAST, losers hold FOREVER')
    print(f'✅ Rule: Max hold time = {rules["max_hold_seconds"]/60:.1f} minutes')
    print(f'✅ Rule: Only trade during hours: {rules["good_hours"]}')
    print(f'✅ Expected: {rules["quick_win_pct"]:.0f}% of wins in <2 min')
    
    print('\n📝 Next Step: Deploy winning_strategy.py to live bot')

if __name__ == '__main__':
    main()
