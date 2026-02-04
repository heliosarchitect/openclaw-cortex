#!/usr/bin/env python3
"""
Trade Analysis Tool - Learn from your trading session
Analyzes logs to identify patterns, strengths, weaknesses
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import List, Dict
import pytz

EST = pytz.timezone('America/New_York')


class TradeAnalyzer:
    """Analyze trading performance"""
    
    def __init__(self, log_file: str):
        self.log_file = Path(log_file)
        self.trades = []
        self.asset_stats = defaultdict(lambda: {
            'total_profit': 0.0,
            'total_trades': 0,
            'wins': 0,
            'losses': 0,
            'biggest_win': 0.0,
            'biggest_loss': 0.0,
            'profits': [],
            'hourly': defaultdict(lambda: {'profit': 0.0, 'trades': 0})
        })
        
    def load_trades(self):
        """Load trades from JSONL file"""
        if not self.log_file.exists():
            print(f"❌ Log file not found: {self.log_file}")
            return False
        
        with open(self.log_file, 'r') as f:
            for line in f:
                try:
                    trade = json.loads(line.strip())
                    self.trades.append(trade)
                    
                    # Update asset stats
                    asset = trade['asset']
                    profit = trade['profit']
                    
                    stats = self.asset_stats[asset]
                    stats['total_profit'] += profit
                    stats['total_trades'] += 1
                    stats['profits'].append(profit)
                    
                    if profit > 0:
                        stats['wins'] += 1
                        stats['biggest_win'] = max(stats['biggest_win'], profit)
                    else:
                        stats['losses'] += 1
                        stats['biggest_loss'] = min(stats['biggest_loss'], profit)
                    
                    # Hourly breakdown
                    try:
                        timestamp = datetime.fromisoformat(trade['timestamp'].replace('Z', '+00:00'))
                        hour = timestamp.hour
                        stats['hourly'][hour]['profit'] += profit
                        stats['hourly'][hour]['trades'] += 1
                    except:
                        pass
                        
                except Exception as e:
                    continue
        
        print(f"✅ Loaded {len(self.trades)} trades from {len(self.asset_stats)} assets")
        return True
    
    def print_summary(self):
        """Print overall summary"""
        if not self.trades:
            print("No trades to analyze")
            return
        
        total_profit = sum(t['profit'] for t in self.trades)
        starting_capital = self.trades[0].get('total_capital', 2495.58) - self.trades[0]['profit']
        final_capital = self.trades[-1].get('total_capital', starting_capital + total_profit)
        return_pct = (total_profit / starting_capital) * 100 if starting_capital > 0 else 0
        
        wins = sum(1 for t in self.trades if t['profit'] > 0)
        losses = sum(1 for t in self.trades if t['profit'] < 0)
        win_rate = (wins / len(self.trades)) * 100 if self.trades else 0
        
        print("=" * 80)
        print("📊 SESSION SUMMARY")
        print("=" * 80)
        print(f"Starting Capital:  ${starting_capital:,.2f}")
        print(f"Final Capital:     ${final_capital:,.2f}")
        print(f"Net P&L:           ${total_profit:,.2f}  ({return_pct:+.2f}%)")
        print(f"Total Trades:      {len(self.trades)}")
        print(f"Win Rate:          {win_rate:.1f}% ({wins}W / {losses}L)")
        print()
        
        if total_profit > 0:
            print(f"💰 Average profit per trade: ${total_profit / len(self.trades):.2f}")
        else:
            print(f"📉 Average loss per trade: ${total_profit / len(self.trades):.2f}")
        
        print("=" * 80)
        print()
    
    def print_asset_breakdown(self):
        """Print per-asset analysis"""
        print("=" * 80)
        print("🎯 ASSET BREAKDOWN")
        print("=" * 80)
        
        # Sort by profit
        sorted_assets = sorted(
            self.asset_stats.items(),
            key=lambda x: x[1]['total_profit'],
            reverse=True
        )
        
        print(f"{'ASSET':12} | {'PROFIT':>12} | {'TRADES':>7} | {'WIN%':>6} | {'AVG':>10} | {'BEST':>10} | {'WORST':>10}")
        print("-" * 80)
        
        for asset, stats in sorted_assets:
            symbol = asset.split('-')[0]
            profit = stats['total_profit']
            trades = stats['total_trades']
            win_rate = (stats['wins'] / trades * 100) if trades > 0 else 0
            avg_profit = profit / trades if trades > 0 else 0
            best = stats['biggest_win']
            worst = stats['biggest_loss']
            
            print(f"{symbol:12} | ${profit:>11.2f} | {trades:>7} | {win_rate:>5.1f}% | "
                  f"${avg_profit:>9.2f} | ${best:>9.2f} | ${worst:>9.2f}")
        
        print("=" * 80)
        print()
    
    def print_hourly_analysis(self):
        """Print hourly P&L breakdown"""
        print("=" * 80)
        print("⏰ HOURLY ANALYSIS")
        print("=" * 80)
        
        # Aggregate across all assets
        hourly_total = defaultdict(lambda: {'profit': 0.0, 'trades': 0})
        
        for asset, stats in self.asset_stats.items():
            for hour, data in stats['hourly'].items():
                hourly_total[hour]['profit'] += data['profit']
                hourly_total[hour]['trades'] += data['trades']
        
        # Sort by hour
        sorted_hours = sorted(hourly_total.items())
        
        print(f"{'HOUR':6} | {'PROFIT':>12} | {'TRADES':>7} | {'AVG/TRADE':>12}")
        print("-" * 80)
        
        for hour, data in sorted_hours:
            profit = data['profit']
            trades = data['trades']
            avg = profit / trades if trades > 0 else 0
            
            hour_str = f"{hour:02d}:00"
            emoji = "💰" if profit > 0 else "📉" if profit < 0 else "➡️"
            
            print(f"{hour_str:6} | {emoji} ${profit:>9.2f} | {trades:>7} | ${avg:>11.2f}")
        
        print("=" * 80)
        print()
        
        # Find best/worst hours
        if hourly_total:
            best_hour = max(hourly_total.items(), key=lambda x: x[1]['profit'])
            worst_hour = min(hourly_total.items(), key=lambda x: x[1]['profit'])
            
            print(f"🏆 Best Hour:  {best_hour[0]:02d}:00 (${best_hour[1]['profit']:.2f})")
            print(f"💀 Worst Hour: {worst_hour[0]:02d}:00 (${worst_hour[1]['profit']:.2f})")
            print()
    
    def print_recommendations(self):
        """Print actionable recommendations"""
        print("=" * 80)
        print("💡 RECOMMENDATIONS")
        print("=" * 80)
        
        # Asset recommendations
        sorted_assets = sorted(
            self.asset_stats.items(),
            key=lambda x: x[1]['total_profit'],
            reverse=True
        )
        
        # Best performers
        if len(sorted_assets) >= 2:
            top_2 = sorted_assets[:2]
            print("✅ FOCUS ON WINNERS:")
            for asset, stats in top_2:
                symbol = asset.split('-')[0]
                profit = stats['total_profit']
                win_rate = (stats['wins'] / stats['total_trades'] * 100) if stats['total_trades'] > 0 else 0
                print(f"   • {symbol}: ${profit:.2f} profit, {win_rate:.1f}% win rate")
                print(f"     → Consider increasing allocation")
            print()
        
        # Worst performers
        if len(sorted_assets) >= 2:
            bottom_2 = sorted_assets[-2:]
            losers = [(a, s) for a, s in bottom_2 if s['total_profit'] < 0]
            
            if losers:
                print("⚠️  UNDERPERFORMERS:")
                for asset, stats in reversed(losers):
                    symbol = asset.split('-')[0]
                    profit = stats['total_profit']
                    win_rate = (stats['wins'] / stats['total_trades'] * 100) if stats['total_trades'] > 0 else 0
                    print(f"   • {symbol}: ${profit:.2f} loss, {win_rate:.1f}% win rate")
                    if win_rate < 40:
                        print(f"     → Consider REMOVING from rotation")
                    else:
                        print(f"     → Review config, may need wider profit targets")
                print()
        
        # Timing recommendations
        hourly_total = defaultdict(lambda: {'profit': 0.0, 'trades': 0})
        for asset, stats in self.asset_stats.items():
            for hour, data in stats['hourly'].items():
                hourly_total[hour]['profit'] += data['profit']
                hourly_total[hour]['trades'] += data['trades']
        
        if hourly_total:
            profitable_hours = [h for h, d in hourly_total.items() if d['profit'] > 0]
            unprofitable_hours = [h for h, d in hourly_total.items() if d['profit'] < 0]
            
            if profitable_hours and unprofitable_hours:
                print("⏰ TIMING INSIGHTS:")
                print(f"   • Profitable hours: {', '.join([f'{h:02d}:00' for h in sorted(profitable_hours)])}")
                print(f"   • Unprofitable hours: {', '.join([f'{h:02d}:00' for h in sorted(unprofitable_hours)])}")
                print(f"     → Consider reducing position sizes during unprofitable hours")
                print()
        
        # Overall strategy
        total_profit = sum(t['profit'] for t in self.trades)
        win_rate = (sum(1 for t in self.trades if t['profit'] > 0) / len(self.trades) * 100) if self.trades else 0
        
        print("🎯 STRATEGY TUNING:")
        if win_rate > 60:
            print(f"   • Win rate is good ({win_rate:.1f}%)")
            if total_profit > 0:
                print(f"   • Keep current strategy, maybe INCREASE position sizes")
            else:
                print(f"   • Win rate good but unprofitable → profit targets too tight")
                print(f"     → INCREASE base_profit_target_bps in configs")
        elif win_rate < 45:
            print(f"   • Win rate is low ({win_rate:.1f}%)")
            print(f"   • Profit targets may be too wide, missing fills")
            print(f"     → DECREASE base_profit_target_bps")
            print(f"     → Consider tighter spreads")
        else:
            print(f"   • Win rate is moderate ({win_rate:.1f}%)")
            print(f"   • Strategy is balanced, fine-tune based on asset performance")
        
        print("=" * 80)
        print()
    
    def run_analysis(self):
        """Run complete analysis"""
        if not self.load_trades():
            return
        
        self.print_summary()
        self.print_asset_breakdown()
        self.print_hourly_analysis()
        self.print_recommendations()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze trading session')
    parser.add_argument('log_file', nargs='?', help='Path to trades JSONL file')
    parser.add_argument('--today', action='store_true', help='Analyze today\'s trades')
    parser.add_argument('--date', type=str, help='Analyze specific date (YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    # Determine log file
    if args.today or not args.log_file:
        today = datetime.now(EST).strftime('%Y-%m-%d')
        log_file = f"logs/trades/trades_{today}.jsonl"
    elif args.date:
        log_file = f"logs/trades/trades_{args.date}.jsonl"
    else:
        log_file = args.log_file
    
    print(f"Analyzing: {log_file}")
    print()
    
    analyzer = TradeAnalyzer(log_file)
    analyzer.run_analysis()


if __name__ == "__main__":
    main()
