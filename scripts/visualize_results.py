#!/usr/bin/env python3
"""
ASCII visualization of backtest results
"""
import csv
import os

def load_results(csv_path):
    """Load CSV results"""
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        return list(reader)

def ascii_chart(data, key, label, width=60):
    """Generate ASCII bar chart"""
    values = [float(row[key]) for row in data]
    labels = [f"{float(row['threshold_pct']):.2f}%" for row in data]
    
    max_val = max(values)
    
    print(f"\n{label}")
    print("=" * (width + 20))
    
    for i, (val, lbl) in enumerate(zip(values, labels)):
        bar_len = int((val / max_val) * width) if max_val > 0 else 0
        bar = "█" * bar_len
        
        if key == 'total_profit':
            val_str = f"${val:,.0f}"
        elif key == 'opportunities':
            val_str = f"{val:,.0f}"
        elif key == 'fills_per_sec':
            val_str = f"{val:.4f}"
        else:
            val_str = f"{val:.2f}"
        
        print(f"{lbl:>6} │{bar:<{width}} {val_str}")
    
    print()

def main():
    csv_path = os.path.expanduser("~/.openclaw/workspace/scripts/backtest_results.csv")
    
    if not os.path.exists(csv_path):
        print("Run backtest_hfv.py first to generate results!")
        return
    
    results = load_results(csv_path)
    
    print("\n" + "="*80)
    print("BACKTEST RESULTS VISUALIZATION")
    print("="*80)
    
    ascii_chart(results, 'total_profit', 'Total Profit by Threshold')
    ascii_chart(results, 'opportunities', 'Trading Opportunities by Threshold')
    ascii_chart(results, 'fills_per_sec', 'Maximum Fills/Second by Threshold')
    
    print("="*80)
    print("\nKey Takeaway:")
    print("  • Profit maximized at lower thresholds (more opportunities)")
    print("  • Volume throughput also highest at lower thresholds")
    print("  • Strategy works best with aggressive spread capture (0.05-0.10%)")
    print("="*80)

if __name__ == "__main__":
    main()
