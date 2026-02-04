#!/usr/bin/env python3
"""
High-Frequency Market Making Backtest Engine
Simulates market making strategy on ETH-USD using historical 1s candles
No external dependencies - pure Python stdlib
"""

import sqlite3
import csv
from datetime import datetime
from typing import Dict, List, Tuple
import os
import statistics

class HFBacktester:
    def __init__(self, db_path: str):
        self.db_path = os.path.expanduser(db_path)
        self.data = []
        
    def load_data(self) -> List[Dict]:
        """Load 1s ETH-USD candles from database"""
        print(f"Loading data from {self.db_path}...")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT timestamp, open, high, low, close, volume
            FROM candles
            WHERE product='ETH-USD' AND granularity=1
            ORDER BY timestamp ASC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        # Process data and estimate bid/ask spreads
        for row in rows:
            timestamp, open_p, high, low, close, volume = row
            
            # Estimate bid/ask from high/low
            mid = (high + low) / 2
            spread_est = (high - low) / 2
            bid = mid - spread_est
            ask = mid + spread_est
            spread_pct = ((ask - bid) / mid * 100) if mid > 0 else 0
            
            self.data.append({
                'timestamp': timestamp,
                'datetime': datetime.fromtimestamp(timestamp),
                'open': open_p,
                'high': high,
                'low': low,
                'close': close,
                'volume': volume,
                'mid': mid,
                'bid': bid,
                'ask': ask,
                'spread_pct': spread_pct
            })
        
        spreads = [d['spread_pct'] for d in self.data]
        
        print(f"Loaded {len(self.data):,} candles")
        print(f"Date range: {self.data[0]['datetime']} to {self.data[-1]['datetime']}")
        print(f"Avg spread: {statistics.mean(spreads):.3f}%")
        print(f"Median spread: {statistics.median(spreads):.3f}%")
        
        return self.data
    
    def backtest_strategy(self, threshold_pct: float) -> Dict:
        """
        Test market making strategy:
        - Place buy at bid, sell at ask when spread > threshold
        - Track profitability and volume
        """
        if not self.data:
            raise ValueError("Must load data first")
        
        # Filter candles where spread exceeds threshold
        tradeable = [d for d in self.data if d['spread_pct'] >= threshold_pct]
        
        if len(tradeable) == 0:
            return {
                'threshold_pct': threshold_pct,
                'opportunities': 0,
                'total_profit': 0,
                'avg_profit_per_trade': 0,
                'fills_per_sec': 0,
                'total_volume': 0,
                'win_rate': 0,
                'avg_spread_pct': 0,
                'median_spread_pct': 0
            }
        
        # Calculate metrics
        trade_size = 1.0  # 1 ETH per trade
        total_opportunities = len(tradeable)
        
        profits = []
        volumes = []
        spreads = []
        
        for candle in tradeable:
            profit_per_trade = candle['ask'] - candle['bid']
            profits.append(profit_per_trade * trade_size)
            volumes.append(trade_size * candle['mid'])
            spreads.append(candle['spread_pct'])
        
        total_profit = sum(profits)
        avg_profit_per_trade = statistics.mean(profits)
        total_volume = sum(volumes)
        
        # Calculate time span and fills/sec
        time_span_sec = tradeable[-1]['timestamp'] - tradeable[0]['timestamp']
        fills_per_sec = total_opportunities / time_span_sec if time_span_sec > 0 else 0
        
        return {
            'threshold_pct': threshold_pct,
            'opportunities': total_opportunities,
            'total_profit': total_profit,
            'avg_profit_per_trade': avg_profit_per_trade,
            'fills_per_sec': fills_per_sec,
            'total_volume': total_volume,
            'win_rate': 100.0,  # All trades are winners in pure MM
            'avg_spread_pct': statistics.mean(spreads),
            'median_spread_pct': statistics.median(spreads)
        }
    
    def run_threshold_sweep(self, thresholds: List[float]) -> List[Dict]:
        """Test multiple spread thresholds"""
        results = []
        
        print("\nRunning threshold sweep...")
        for threshold in thresholds:
            result = self.backtest_strategy(threshold)
            results.append(result)
            print(f"Threshold {threshold:>5.2f}%: {result['opportunities']:>8,} opportunities, "
                  f"${result['total_profit']:>10,.2f} profit, "
                  f"{result['fills_per_sec']:>7.4f} fills/sec")
        
        return results
    
    def generate_report(self, results: List[Dict]):
        """Generate profitability vs volume analysis"""
        print("\n" + "="*90)
        print("HIGH-FREQUENCY MARKET MAKING BACKTEST RESULTS")
        print("="*90)
        
        print(f"\nData Summary:")
        print(f"  Total candles: {len(self.data):,}")
        print(f"  Date range: {self.data[0]['datetime']} to {self.data[-1]['datetime']}")
        duration_hours = (self.data[-1]['timestamp'] - self.data[0]['timestamp']) / 3600
        print(f"  Duration: {duration_hours:.1f} hours ({duration_hours/24:.1f} days)")
        
        print(f"\n{'Threshold':<12} {'Opportunities':<15} {'Profit ($)':<15} {'Fills/Sec':<12} {'Volume ($)':<15}")
        print("-" * 90)
        
        for row in results:
            print(f"{row['threshold_pct']:<11.2f}% {row['opportunities']:<15,} "
                  f"${row['total_profit']:<14,.2f} {row['fills_per_sec']:<12.4f} "
                  f"${row['total_volume']:<14,.0f}")
        
        # Find optimal threshold (max profit)
        best = max(results, key=lambda x: x['total_profit'])
        
        print("\n" + "="*90)
        print(f"OPTIMAL CONFIGURATION: {best['threshold_pct']:.2f}% threshold")
        print(f"  Total Profit: ${best['total_profit']:,.2f}")
        print(f"  Opportunities: {best['opportunities']:,}")
        print(f"  Average profit per trade: ${best['avg_profit_per_trade']:.4f}")
        print(f"  Maximum sustainable fills/sec: {best['fills_per_sec']:.4f}")
        print(f"  Total volume: ${best['total_volume']:,.0f}")
        print(f"  Average spread at this threshold: {best['avg_spread_pct']:.3f}%")
        print("="*90)
        
        # Save results to CSV
        output_path = os.path.expanduser("~/.openclaw/workspace/scripts/backtest_results.csv")
        with open(output_path, 'w', newline='') as f:
            if results:
                writer = csv.DictWriter(f, fieldnames=results[0].keys())
                writer.writeheader()
                writer.writerows(results)
        
        print(f"\nResults saved to: {output_path}")
        
        # Profitability vs Volume curve insight
        print("\n" + "="*90)
        print("PROFITABILITY vs VOLUME ANALYSIS:")
        print("="*90)
        print("\nKey Insights:")
        print(f"  • Lower thresholds = More volume but lower profit per trade")
        print(f"  • Higher thresholds = Less volume but higher profit per trade")
        print(f"  • Optimal balance at {best['threshold_pct']:.2f}% threshold")
        print(f"  • Maximum observed spread: {max(d['spread_pct'] for d in self.data):.3f}%")
        print(f"  • Minimum observed spread: {min(d['spread_pct'] for d in self.data):.3f}%")


def main():
    db_path = "~/Projects/Chad_Volume_tracker/trading_data.db"
    
    # Initialize backtester
    bt = HFBacktester(db_path)
    bt.load_data()
    
    # Test different spread thresholds
    thresholds = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.50, 0.75, 1.0]
    
    # Run backtest
    results = bt.run_threshold_sweep(thresholds)
    
    # Generate report
    bt.generate_report(results)
    
    return results


if __name__ == "__main__":
    main()
