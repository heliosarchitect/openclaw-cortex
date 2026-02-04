#!/usr/bin/env python3
"""
Live Pattern Tester - Test winning patterns on new data
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime

class PatternTester:
    def __init__(self, db_path):
        self.db_path = db_path
        self.df = None
        
    def load_data(self, limit=None):
        """Load candle data"""
        conn = sqlite3.connect(self.db_path)
        query = "SELECT timestamp, open, high, low, close, volume FROM candles ORDER BY timestamp"
        if limit:
            query += f" LIMIT {limit}"
        
        self.df = pd.read_sql_query(query, conn)
        conn.close()
        
        # Calculate derived features
        self.df['body'] = abs(self.df['close'] - self.df['open'])
        self.df['upper_wick'] = self.df['high'] - self.df[['open', 'close']].max(axis=1)
        self.df['lower_wick'] = self.df[['open', 'close']].min(axis=1) - self.df['low']
        self.df['range'] = self.df['high'] - self.df['low']
        self.df['wick_ratio'] = (self.df['upper_wick'] + self.df['lower_wick']) / (self.df['body'] + 1e-9)
        self.df['body_pct'] = self.df['body'] / (self.df['range'] + 1e-9)
        
        print(f"✓ Loaded {len(self.df):,} candles")
    
    def champion_pattern(self):
        """(volume × upper_wick) threshold 1.0"""
        signals = []
        window = 5
        
        for i in range(window, len(self.df)):
            v = self.df['volume'].iloc[i]
            uw = self.df['upper_wick'].iloc[i]
            v_avg = self.df['volume'].iloc[i-window:i].mean()
            uw_avg = self.df['upper_wick'].iloc[i-window:i].mean()
            
            if (v * uw) > (v_avg * uw_avg * 1.0):
                signals.append(i)
        
        return signals
    
    def runner_up_pattern(self):
        """(body / wick_ratio) threshold 1.0"""
        signals = []
        window = 5
        
        for i in range(window, len(self.df)):
            body = self.df['body'].iloc[i]
            wr = self.df['wick_ratio'].iloc[i]
            body_avg = self.df['body'].iloc[i-window:i].mean()
            wr_avg = self.df['wick_ratio'].iloc[i-window:i].mean()
            
            if (body / (wr + 1e-9)) > (body_avg / (wr_avg + 1e-9) * 1.0):
                signals.append(i)
        
        return signals
    
    def high_winrate_pattern(self):
        """(wick_ratio / upper_wick) threshold 3.0"""
        signals = []
        window = 5
        
        for i in range(window, len(self.df)):
            wr = self.df['wick_ratio'].iloc[i]
            uw = self.df['upper_wick'].iloc[i]
            wr_avg = self.df['wick_ratio'].iloc[i-window:i].mean()
            uw_avg = self.df['upper_wick'].iloc[i-window:i].mean()
            
            if (wr / (uw + 1e-9)) > (wr_avg / (uw_avg + 1e-9) * 3.0):
                signals.append(i)
        
        return signals
    
    def volume_increasing_pattern(self):
        """Simple volume momentum"""
        signals = []
        window = 5
        
        for i in range(window, len(self.df)):
            volumes = self.df['volume'].iloc[i-window:i].values
            if np.all(np.diff(volumes) > 0):
                signals.append(i)
        
        return signals
    
    def time_decay_pattern(self):
        """Wick ratio time decay 0.5"""
        signals = []
        window = 15
        decay = 0.5
        
        for i in range(window, len(self.df)):
            wr = self.df['wick_ratio'].iloc[i-window:i].values
            weights = np.array([decay ** (window - j - 1) for j in range(window)])
            weighted_avg = np.average(wr, weights=weights)
            
            if self.df['wick_ratio'].iloc[i] > weighted_avg * 1.5:
                signals.append(i)
        
        return signals
    
    def backtest(self, signals, name="Pattern"):
        """Backtest a pattern"""
        if len(signals) == 0:
            print(f"{name}: No signals generated")
            return None
        
        balance = 10000
        position = None
        trades = []
        equity = [balance]
        
        for idx in signals:
            if idx >= len(self.df):
                continue
            
            if position is None:
                entry_price = self.df['close'].iloc[idx]
                position = {'entry': entry_price, 'shares': balance / entry_price, 'entry_idx': idx}
            else:
                exit_price = self.df['close'].iloc[idx]
                profit = (exit_price - position['entry']) * position['shares']
                balance += profit
                
                trades.append({
                    'entry': position['entry'],
                    'exit': exit_price,
                    'profit': profit,
                    'return': (exit_price / position['entry'] - 1) * 100,
                    'bars': idx - position['entry_idx']
                })
                
                equity.append(balance)
                position = None
        
        # Close final position
        if position:
            exit_price = self.df['close'].iloc[-1]
            profit = (exit_price - position['entry']) * position['shares']
            balance += profit
            trades.append({'profit': profit, 'return': (exit_price / position['entry'] - 1) * 100})
            equity.append(balance)
        
        if len(trades) == 0:
            print(f"{name}: No completed trades")
            return None
        
        # Calculate metrics
        total_profit = balance - 10000
        num_trades = len(trades)
        wins = sum(1 for t in trades if t['profit'] > 0)
        win_rate = wins / num_trades
        avg_profit = total_profit / num_trades
        
        # Max drawdown
        peak = equity[0]
        max_dd = 0
        for e in equity:
            if e > peak:
                peak = e
            dd = (peak - e) / peak
            if dd > max_dd:
                max_dd = dd
        
        # Avg bars per trade
        avg_bars = np.mean([t['bars'] for t in trades if 'bars' in t])
        
        results = {
            'name': name,
            'profit': total_profit,
            'num_trades': num_trades,
            'win_rate': win_rate,
            'avg_profit': avg_profit,
            'max_dd': max_dd,
            'avg_bars': avg_bars
        }
        
        return results
    
    def test_all_patterns(self):
        """Test all winning patterns"""
        patterns = [
            ('Champion: Volume × Upper Wick', self.champion_pattern),
            ('Runner-Up: Body / Wick Ratio', self.runner_up_pattern),
            ('High WR: WR / Upper Wick', self.high_winrate_pattern),
            ('Simple: Volume Increasing', self.volume_increasing_pattern),
            ('Time Decay: Wick Ratio', self.time_decay_pattern),
        ]
        
        results = []
        
        print("="*80)
        print("TESTING ALL PATTERNS")
        print("="*80)
        print()
        
        for name, pattern_func in patterns:
            print(f"Testing {name}...")
            signals = pattern_func()
            result = self.backtest(signals, name)
            if result:
                results.append(result)
                print(f"  ✓ Profit: ${result['profit']:,.2f}")
                print(f"  ✓ Trades: {result['num_trades']:,} @ {result['win_rate']*100:.1f}% win rate")
                print(f"  ✓ Avg: ${result['avg_profit']:.2f}/trade")
                print(f"  ✓ Max DD: {result['max_dd']*100:.1f}%")
                print(f"  ✓ Avg Hold: {result['avg_bars']:.1f} bars")
                print()
        
        if results:
            print("="*80)
            print("RANKING")
            print("="*80)
            results.sort(key=lambda x: x['profit'], reverse=True)
            for i, r in enumerate(results, 1):
                print(f"{i}. {r['name']:40s} ${r['profit']:8,.2f}")
            print()
            
            print("="*80)
            print("BEST BY METRIC")
            print("="*80)
            best_profit = max(results, key=lambda x: x['profit'])
            best_wr = max(results, key=lambda x: x['win_rate'])
            best_avg = max(results, key=lambda x: x['avg_profit'])
            
            print(f"Highest Profit:    {best_profit['name']:40s} ${best_profit['profit']:,.2f}")
            print(f"Highest Win Rate:  {best_wr['name']:40s} {best_wr['win_rate']*100:.1f}%")
            print(f"Best Avg/Trade:    {best_avg['name']:40s} ${best_avg['avg_profit']:.2f}")
            print()

def main():
    print("="*80)
    print("LIVE PATTERN TESTER")
    print("="*80)
    print()
    
    db_path = '/home/bonsaihorn/Projects/Chad_Volume_tracker/trading_data.db'
    
    tester = PatternTester(db_path)
    tester.load_data()
    tester.test_all_patterns()
    
    print("="*80)
    print("✓ Testing complete!")
    print("="*80)

if __name__ == '__main__':
    main()
