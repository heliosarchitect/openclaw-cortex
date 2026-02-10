#!/usr/bin/env python3
"""
AUGUR Short-Hold Signal Discovery
Finds profitable microstructure signals at 15s, 30s, 60s hold periods.
"""

import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

DB_PATH = '/home/bonsaihorn/Projects/augur-collector/enhanced_data.db'
BAR_SIZE = 5  # 5-second bars
MON_START = int(datetime(2026, 2, 9, 14, 0, 0).timestamp())
MON_END = int(datetime(2026, 2, 9, 23, 0, 0).timestamp())
RT_FEE = 0.0020  # 0.20% round trip
HOLD_PERIODS = [3, 6, 12]  # in bars (15s, 30s, 60s)
HOLD_LABELS = {3: '15s', 6: '30s', 12: '60s'}

# Products to test — the 5 specified mid-caps (swap BLZ for DOGE due to data)
PRODUCTS = ['NKN-USD', 'ZRO-USD', 'BNKR-USD', 'BIRB-USD', 'DOGE-USD']

MIN_VOLUME = 10  # $10 minimum bar volume
MIN_OCCURRENCES = 50  # per half
MIN_WR = 0.53

PERCENTILE_THRESHOLDS = [10, 20, 80, 90]

def load_and_merge(conn, product):
    """Load trade_flow and orderbook data, merge into 5s bars."""
    
    # Load trade_flow
    tf = pd.read_sql_query("""
        SELECT timestamp, buy_volume, sell_volume, buy_count, sell_count, vwap
        FROM trade_flow 
        WHERE product = ? AND timestamp >= ? AND timestamp < ?
        ORDER BY timestamp
    """, conn, params=(product, MON_START, MON_END))
    
    # Load orderbook snapshots
    ob = pd.read_sql_query("""
        SELECT timestamp, best_bid, best_ask, bid_size, ask_size, mid_price
        FROM orderbook_snapshots
        WHERE product = ? AND timestamp >= ? AND timestamp < ?
        ORDER BY timestamp
    """, conn, params=(product, MON_START, MON_END))
    
    if len(tf) < 100 or len(ob) < 100:
        print(f"  {product}: insufficient data (tf={len(tf)}, ob={len(ob)})")
        return None
    
    # Create 5-second bins
    tf['bar'] = (tf['timestamp'] // BAR_SIZE) * BAR_SIZE
    ob['bar'] = (ob['timestamp'] // BAR_SIZE) * BAR_SIZE
    
    # Aggregate trade_flow per bar
    tf_agg = tf.groupby('bar').agg({
        'buy_volume': 'sum',
        'sell_volume': 'sum',
        'buy_count': 'sum',
        'sell_count': 'sum',
        'vwap': 'last'  # last VWAP in the bar
    }).reset_index()
    
    # Aggregate orderbook per bar (last snapshot)
    ob_agg = ob.groupby('bar').agg({
        'best_bid': 'last',
        'best_ask': 'last',
        'bid_size': 'last',
        'ask_size': 'last',
        'mid_price': 'last'
    }).reset_index()
    
    # Merge on bar
    merged = pd.merge(tf_agg, ob_agg, on='bar', how='inner')
    merged = merged.sort_values('bar').reset_index(drop=True)
    
    # Calculate total volume
    merged['total_volume'] = merged['buy_volume'] + merged['sell_volume']
    
    # Filter: volume > $10 AND both sides have volume
    merged = merged[
        (merged['total_volume'] >= MIN_VOLUME) & 
        (merged['buy_volume'] > 0) & 
        (merged['sell_volume'] > 0)
    ].reset_index(drop=True)
    
    print(f"  {product}: {len(merged)} valid bars after filtering")
    return merged


def compute_indicators(df):
    """Compute all microstructure indicators."""
    
    # Price from mid_price
    df['price'] = df['mid_price']
    
    # 1. Spread
    df['spread'] = (df['best_ask'] - df['best_bid']) / df['price']
    
    # 2. Spread change
    df['spread_change'] = df['spread'] - df['spread'].shift(1)
    
    # 3. Book imbalance
    df['book_imbalance'] = (df['bid_size'] - df['ask_size']) / (df['bid_size'] + df['ask_size'])
    
    # 4. Trade imbalance
    total_trades = df['buy_count'] + df['sell_count']
    df['trade_imbalance'] = np.where(
        total_trades > 0,
        (df['buy_count'] - df['sell_count']) / total_trades,
        0
    )
    
    # 5. Volume surge (current / rolling 12-bar mean)
    rolling_vol = df['total_volume'].rolling(12, min_periods=1).mean().shift(1)
    df['volume_surge'] = df['total_volume'] / rolling_vol
    
    # 6. Price velocity (change over last 3 bars)
    df['price_velocity'] = (df['price'] - df['price'].shift(3)) / df['price'].shift(3)
    
    # 7. Flow ratio (buy_vol / total_vol) - only when volume > $50
    df['flow_ratio'] = np.where(
        df['total_volume'] > 50,
        df['buy_volume'] / df['total_volume'],
        np.nan
    )
    
    # 8. VWAP deviation
    df['vwap_dev'] = (df['price'] - df['vwap']) / df['price']
    
    # Future prices for outcome measurement
    for hold in HOLD_PERIODS:
        df[f'future_price_{hold}'] = df['price'].shift(-hold)
        df[f'return_{hold}'] = (df[f'future_price_{hold}'] - df['price']) / df['price']
    
    return df


def test_signals(df, product):
    """Test all indicator/threshold/direction combinations."""
    
    indicators = ['spread', 'spread_change', 'book_imbalance', 'trade_imbalance',
                  'volume_surge', 'price_velocity', 'flow_ratio', 'vwap_dev']
    
    results = []
    
    # Train/test split: first half / second half
    n = len(df)
    half = n // 2
    train = df.iloc[:half].copy()
    test = df.iloc[half:].copy()
    
    for indicator in indicators:
        # Skip if too many NaN
        valid_train = train[indicator].dropna()
        valid_test = test[indicator].dropna()
        if len(valid_train) < 100 or len(valid_test) < 100:
            continue
        
        # Compute percentiles from TRAIN data only (no lookahead)
        percentiles = {}
        for p in PERCENTILE_THRESHOLDS:
            percentiles[p] = np.nanpercentile(train[indicator].values, p)
        
        for pct in PERCENTILE_THRESHOLDS:
            threshold = percentiles[pct]
            
            for direction in ['long', 'short']:
                for hold in HOLD_PERIODS:
                    ret_col = f'return_{hold}'
                    
                    # Determine signal condition
                    if pct <= 50:
                        # Low percentile: indicator <= threshold
                        train_mask = (train[indicator] <= threshold) & train[ret_col].notna()
                        test_mask = (test[indicator] <= threshold) & test[ret_col].notna()
                    else:
                        # High percentile: indicator >= threshold
                        train_mask = (train[indicator] >= threshold) & train[ret_col].notna()
                        test_mask = (test[indicator] >= threshold) & test[ret_col].notna()
                    
                    train_signals = train[train_mask]
                    test_signals = test[test_mask]
                    
                    if len(train_signals) < MIN_OCCURRENCES or len(test_signals) < MIN_OCCURRENCES:
                        continue
                    
                    # Calculate returns
                    if direction == 'long':
                        train_returns = train_signals[ret_col].values - RT_FEE
                        test_returns = test_signals[ret_col].values - RT_FEE
                    else:
                        train_returns = -train_signals[ret_col].values - RT_FEE
                        test_returns = -test_signals[ret_col].values - RT_FEE
                    
                    train_wr = np.mean(train_returns > 0)
                    test_wr = np.mean(test_returns > 0)
                    train_avg = np.mean(train_returns) * 100  # as %
                    test_avg = np.mean(test_returns) * 100
                    
                    # Check if passes all filters
                    if (train_wr >= MIN_WR and test_wr >= MIN_WR and
                        train_avg > 0 and test_avg > 0):
                        
                        results.append({
                            'product': product,
                            'indicator': indicator,
                            'percentile': f'p{pct}',
                            'threshold': threshold,
                            'direction': direction,
                            'hold': HOLD_LABELS[hold],
                            'hold_bars': hold,
                            'train_n': len(train_signals),
                            'test_n': len(test_signals),
                            'train_wr': train_wr,
                            'test_wr': test_wr,
                            'train_avg_ret': train_avg,
                            'test_avg_ret': test_avg,
                            'train_total_ret': train_avg * len(train_signals),
                            'test_total_ret': test_avg * len(test_signals),
                        })
    
    return results


def main():
    conn = sqlite3.connect(DB_PATH)
    
    all_results = []
    
    print("=== AUGUR Short-Hold Signal Discovery ===")
    print(f"Monday Feb 9, 14:00-23:00 UTC")
    print(f"Bar size: {BAR_SIZE}s, RT fees: {RT_FEE*100:.2f}%")
    print(f"Hold periods: {[HOLD_LABELS[h] for h in HOLD_PERIODS]}")
    print(f"Products: {PRODUCTS}")
    print()
    
    for product in PRODUCTS:
        print(f"Processing {product}...")
        df = load_and_merge(conn, product)
        if df is None:
            continue
        
        df = compute_indicators(df)
        results = test_signals(df, product)
        all_results.extend(results)
        
        if results:
            print(f"  → {len(results)} passing signals found")
        else:
            print(f"  → No passing signals")
    
    conn.close()
    
    # Sort by test avg return
    all_results.sort(key=lambda x: x['test_avg_ret'], reverse=True)
    
    # Generate report
    report = generate_report(all_results)
    
    output_path = '/home/bonsaihorn/.openclaw/workspace/analysis/augur-short-hold-discovery.md'
    with open(output_path, 'w') as f:
        f.write(report)
    
    print(f"\nReport written to {output_path}")
    print(f"Total passing signals: {len(all_results)}")
    
    # Also print top 20
    if all_results:
        print(f"\n=== TOP 20 SIGNALS (by test avg return) ===")
        for i, r in enumerate(all_results[:20]):
            print(f"{i+1}. {r['product']} {r['indicator']} {r['percentile']} {r['direction']} {r['hold']}: "
                  f"Train {r['train_n']}t {r['train_wr']:.1%}WR {r['train_avg_ret']:+.3f}% | "
                  f"Test {r['test_n']}t {r['test_wr']:.1%}WR {r['test_avg_ret']:+.3f}%")


def generate_report(results):
    lines = []
    lines.append("# AUGUR Short-Hold Signal Discovery")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"**Data:** Monday Feb 9 2026, 14:00-23:00 UTC")
    lines.append(f"**Bar size:** 5 seconds")
    lines.append(f"**Round-trip fees:** 0.20% (VIP 2 taker)")
    lines.append(f"**Hold periods:** 15s, 30s, 60s")
    lines.append(f"**Products:** {', '.join(PRODUCTS)}")
    lines.append(f"**Train/Test:** First half / Second half of Monday data")
    lines.append("")
    lines.append("## Validation Criteria")
    lines.append("- Both train AND test profitable after 0.20% RT fees")
    lines.append("- Minimum 50 occurrences in each half")
    lines.append("- Win rate > 53% in both halves")
    lines.append("- No lookahead bias")
    lines.append("")
    
    if not results:
        lines.append("## ❌ NO PASSING SIGNALS FOUND")
        lines.append("")
        lines.append("No indicator/threshold combinations passed all validation criteria.")
        lines.append("This suggests that at 5s bar resolution with 0.20% RT fees,")
        lines.append("these microstructure indicators don't generate enough edge")
        lines.append("at 15s-60s hold periods for these products.")
        return '\n'.join(lines)
    
    lines.append(f"## ✅ {len(results)} PASSING SIGNALS FOUND")
    lines.append("")
    
    # Group by product
    by_product = {}
    for r in results:
        by_product.setdefault(r['product'], []).append(r)
    
    for product in PRODUCTS:
        if product not in by_product:
            lines.append(f"### {product}: No passing signals")
            lines.append("")
            continue
        
        prod_results = by_product[product]
        lines.append(f"### {product}: {len(prod_results)} signals")
        lines.append("")
        lines.append("| Indicator | Pctl | Dir | Hold | Train N | Train WR | Train Ret | Test N | Test WR | Test Ret |")
        lines.append("|-----------|------|-----|------|---------|----------|-----------|--------|---------|----------|")
        
        for r in sorted(prod_results, key=lambda x: x['test_avg_ret'], reverse=True):
            lines.append(
                f"| {r['indicator']} | {r['percentile']} | {r['direction']} | {r['hold']} | "
                f"{r['train_n']} | {r['train_wr']:.1%} | {r['train_avg_ret']:+.3f}% | "
                f"{r['test_n']} | {r['test_wr']:.1%} | {r['test_avg_ret']:+.3f}% |"
            )
        lines.append("")
    
    # Summary by hold period
    lines.append("## Summary by Hold Period")
    lines.append("")
    for hold_label in ['15s', '30s', '60s']:
        hold_results = [r for r in results if r['hold'] == hold_label]
        if hold_results:
            avg_ret = np.mean([r['test_avg_ret'] for r in hold_results])
            avg_wr = np.mean([r['test_wr'] for r in hold_results])
            lines.append(f"- **{hold_label}:** {len(hold_results)} signals, avg test return {avg_ret:+.3f}%, avg test WR {avg_wr:.1%}")
        else:
            lines.append(f"- **{hold_label}:** No passing signals")
    lines.append("")
    
    # Summary by indicator
    lines.append("## Summary by Indicator")
    lines.append("")
    by_ind = {}
    for r in results:
        by_ind.setdefault(r['indicator'], []).append(r)
    for ind, ind_results in sorted(by_ind.items(), key=lambda x: -len(x[1])):
        avg_ret = np.mean([r['test_avg_ret'] for r in ind_results])
        lines.append(f"- **{ind}:** {len(ind_results)} signals, avg test return {avg_ret:+.3f}%")
    lines.append("")
    
    # Top 10 actionable signals
    lines.append("## Top 10 Actionable Signals")
    lines.append("")
    for i, r in enumerate(results[:10]):
        lines.append(f"**{i+1}. {r['product']} — {r['indicator']} {r['percentile']} → {r['direction'].upper()} {r['hold']}**")
        lines.append(f"   - Threshold: {r['threshold']:.6f}")
        lines.append(f"   - Train: {r['train_n']} trades, {r['train_wr']:.1%} WR, {r['train_avg_ret']:+.3f}% avg")
        lines.append(f"   - Test:  {r['test_n']} trades, {r['test_wr']:.1%} WR, {r['test_avg_ret']:+.3f}% avg")
        lines.append(f"   - Est. daily edge: {r['test_avg_ret'] * r['test_n'] / 1:.1f}% cumulative")
        lines.append("")
    
    return '\n'.join(lines)


if __name__ == '__main__':
    main()
