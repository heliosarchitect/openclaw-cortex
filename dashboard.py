#!/usr/bin/env python3
"""
Trading Dashboard - Simple terminal UI to monitor active_trader.py
Real-time view of positions, P&L, and bot status
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import pytz

EST = pytz.timezone('America/New_York')


class TradingDashboard:
    """Real-time trading dashboard"""
    
    def __init__(self, trade_log_dir='logs/trades'):
        self.trade_log_dir = Path(trade_log_dir)
        self.last_check = 0
        self.assets = {}
        self.total_pnl = 0.0
        self.starting_capital = 2495.58  # Will be updated from first log entry
        
    def clear_screen(self):
        """Clear terminal"""
        print("\033[2J\033[H", end='')
    
    def load_latest_trades(self):
        """Load trades from today's log file"""
        today = datetime.now(EST).strftime('%Y-%m-%d')
        log_file = self.trade_log_dir / f"trades_{today}.jsonl"
        
        if not log_file.exists():
            return
        
        # Reset stats
        self.assets = defaultdict(lambda: {'profit': 0.0, 'trades': 0, 'last_trade': None})
        
        # Read all trades
        with open(log_file, 'r') as f:
            for line in f:
                try:
                    trade = json.loads(line.strip())
                    asset = trade['asset']
                    
                    self.assets[asset]['profit'] += trade['profit']
                    self.assets[asset]['trades'] += 1
                    self.assets[asset]['last_trade'] = trade['timestamp']
                    self.assets[asset]['total_capital'] = trade.get('total_capital', 0)
                    
                    # Update starting capital from first entry
                    if len(self.assets) == 1 and self.assets[asset]['trades'] == 1:
                        self.starting_capital = trade.get('total_capital', 2495.58) - trade['profit']
                    
                except Exception as e:
                    continue
        
        # Calculate total P&L
        self.total_pnl = sum(a['profit'] for a in self.assets.values())
    
    def render(self):
        """Render dashboard"""
        self.clear_screen()
        
        # Header
        now = datetime.now(EST)
        print("=" * 80)
        print(f"{'🎯 ACTIVE TRADING MONITOR':^80}")
        print("=" * 80)
        print(f"Time: {now.strftime('%Y-%m-%d %H:%M:%S EST'):^80}")
        print("=" * 80)
        
        # Portfolio summary
        current_capital = self.starting_capital + self.total_pnl
        return_pct = (self.total_pnl / self.starting_capital) * 100 if self.starting_capital > 0 else 0
        
        pnl_emoji = "📈" if self.total_pnl > 0 else "📉" if self.total_pnl < 0 else "➡️"
        
        print()
        print(f"  Starting Capital:  ${self.starting_capital:>10,.2f}")
        print(f"  Current Capital:   ${current_capital:>10,.2f}")
        print(f"  Session P&L:       {pnl_emoji} ${self.total_pnl:>9,.2f}  ({return_pct:+.2f}%)")
        print()
        print("=" * 80)
        
        # Asset breakdown
        print(f"{'ASSET':^12} | {'PROFIT':^12} | {'TRADES':^8} | {'LAST TRADE':^20}")
        print("-" * 80)
        
        if not self.assets:
            print(f"{'No trades yet...':^80}")
        else:
            # Sort by profit (descending)
            sorted_assets = sorted(
                self.assets.items(),
                key=lambda x: x[1]['profit'],
                reverse=True
            )
            
            for asset, stats in sorted_assets:
                symbol = asset.split('-')[0]
                profit = stats['profit']
                trades = stats['trades']
                last_trade = stats['last_trade']
                
                # Color code profit
                if profit > 0:
                    profit_str = f"\033[92m${profit:>9.2f}\033[0m"  # Green
                elif profit < 0:
                    profit_str = f"\033[91m${profit:>9.2f}\033[0m"  # Red
                else:
                    profit_str = f"${profit:>9.2f}"
                
                # Format last trade time
                if last_trade:
                    try:
                        trade_dt = datetime.fromisoformat(last_trade.replace('Z', '+00:00'))
                        last_trade_str = trade_dt.strftime('%H:%M:%S')
                    except:
                        last_trade_str = "N/A"
                else:
                    last_trade_str = "N/A"
                
                print(f"{symbol:^12} | {profit_str} | {trades:^8} | {last_trade_str:^20}")
        
        print("=" * 80)
        
        # Footer
        print()
        print(f"  Auto-refresh: 5s  |  Press Ctrl+C to exit")
        print()
    
    def run(self):
        """Run dashboard loop"""
        print("Starting trading dashboard...")
        
        try:
            while True:
                self.load_latest_trades()
                self.render()
                time.sleep(5)  # Refresh every 5 seconds
                
        except KeyboardInterrupt:
            print("\n\nDashboard stopped.")
            sys.exit(0)


def main():
    dashboard = TradingDashboard()
    dashboard.run()


if __name__ == "__main__":
    main()
