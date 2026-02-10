#!/usr/bin/env python3
"""
AUGUR Short-Hold Signal Discovery V2
Relaxed filters, more products, smarter approach.
"""

import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

DB_PATH = '/home/bonsaihorn/Projects/augur-collector/enhanced_data.db'
BAR_SIZE = 5
MON_START = int(datetime(2026, 2, 9, 14, 0, 0).timestamp())
MON_END = int(datetime(2026, 2, 9, 23, 0, 0).timestamp())
RT_FEE = 0.0020
HOLD_PERIODS = [3, 6, 12]  # 15s, 30s, 60s
HOLD_LABELS = {3: '15s', 6: '30s', 12: '60s'}

# Broader product set — all mid-caps with decent bar counts AND volatility
PRODUCTS = ['NKN-USD', 'ZRO-USD', 'BNKR-USD', 'BIRB-USD', 'DOGE-USD',
            'SKY-USD', 'MAMO-USD', 'PENGU-USD', 'MON-USD', 'HBAR-USD',
            'XLM-USD', 'SUI-USD', 'ADA-USD', 'PUMP-USD', 'ONDO-USD',
            'FIGHT-USD', 'WLFI-USD', 'ELSA-USD', 'ZKP-USD', 'INX-USD',
            'TRIA-USD', 'ZORA-USD', 'SKR-USD', 'FLR-USD', 'KITE-USD',
            'AERO-USD', 'BERA-USD']

MIN_VOLUME_BAR = 1  # $1 min volume (relaxed - vol filter was too harsh)
MIN_OCCURRENCES = 50
MIN_WR = 0.53

PERCENTILE_THRESHOLDS = [5, 10, 15, 20, 80, 85, 90, 95]


def load_data(conn, product):
    """Load and merge into 5s bars. Use outer join with OB to keep OB-only bars."""
    
    tf = pd.read_sql_query("""
        SELECT timestamp, buy_volume, sell_volume, buy_count, sell_count, vwap
        FROM trade_flow WHERE product = ? AND timestamp >= ? AND timestamp < ?
        ORDER BY timestamp
    """, conn, params=(product, MON_START, MON_END))
    
    ob = pd.read_sql_query("""
        SELECT timestamp, best_bid, best_ask, bid_size, ask_size, mid_price
        FROM orderbook_snapshots WHERE product = ? AND timestamp >= ? AND timestamp < ?
        ORDER BY timestamp
    """, conn, params=(product, MON_START, MON_END))
    
    if len(ob) < 200:
        return None
    
    tf['bar'] = (tf['timestamp'] // BAR_SIZE) * BAR_SIZE
    ob['bar'] = (ob['timestamp'] // BAR_SIZE) * BAR_SIZE
    
    # Aggregate
    if len(tf) > 0:
        tf_agg = tf.groupby('bar').agg({
            'buy_volume': 'sum', 'sell_volume': 'sum',
            'buy_count': 'sum', 'sell_count': 'sum', 'vwap': 'last'
        }).reset_index()
    else:
        tf_agg = pd.DataFrame(columns=['bar', 'buy_volume', 'sell_volume', 'buy_count', 'sell_count', 'vwap'])
    
    ob_agg = ob.groupby('bar').agg({
        'best_bid': 'last', 'best_ask': 'last',
        'bid_size': 'last', 'ask_size': 'last', 'mid_price': 'last'
    }).reset_index()
    
    # LEFT join from OB (we always have price from OB)
    merged = pd.merge(ob_agg, tf_agg, on='bar', how='left')
    merged = merged.sort_values('bar').reset_index(drop=True)
    
    # Fill missing trade_flow with 0
    for col in ['buy_volume', 'sell_volume', 'buy_count', 'sell_count']:
        merged[col] = merged[col].fillna(0)
    merged['vwap'] = merged['vwap'].fillna(merged['mid_price'])
    
    merged['total_volume'] = merged['buy_volume'] + merged['sell_volume']
    merged['price'] = merged['mid_price']
    
    # Check gaps — if bars aren't continuous, forward returns are wrong
    # Only keep runs of consecutive 5s bars
    merged['bar_diff'] = merged['bar'].diff()
    merged['is_continuous'] = merged['bar_diff'] == BAR_SIZE
    merged.loc[0, 'is_continuous'] = True
    
    return merged


def compute_indicators(df):
    """Compute all microstructure indicators."""
    
    # 1. Spread
    df['spread'] = (df['best_ask'] - df['best_bid']) / df['price']
    
    # 2. Spread change
    df['spread_change'] = df['spread'] - df['spread'].shift(1)
    
    # 3. Book imbalance
    denom = df['bid_size'] + df['ask_size']
    df['book_imbalance'] = np.where(denom > 0, (df['bid_size'] - df['ask_size']) / denom, 0)
    
    # 4. Trade imbalance (only where trades exist)
    total_trades = df['buy_count'] + df['sell_count']
    df['trade_imbalance'] = np.where(
        total_trades > 0,
        (df['buy_count'] - df['sell_count']) / total_trades,
        np.nan
    )
    
    # 5. Volume surge
    rolling_vol = df['total_volume'].rolling(12, min_periods=3).mean().shift(1)
    df['volume_surge'] = np.where(rolling_vol > 0, df['total_volume'] / rolling_vol, np.nan)
    
    # 6. Price velocity (3-bar)
    df['price_velocity'] = (df['price'] - df['price'].shift(3)) / df['price'].shift(3)
    
    # 7. Flow ratio (when vol > $50)
    df['flow_ratio'] = np.where(
        df['total_volume'] > 50,
        df['buy_volume'] / df['total_volume'],
        np.nan
    )
    
    # 8. VWAP deviation
    df['vwap_dev'] = (df['price'] - df['vwap']) / df['price']
    
    # 9. Book imbalance change (momentum of book)
    df['book_imb_change'] = df['book_imbalance'] - df['book_imbalance'].shift(1)
    
    # 10. Bid size change ratio
    df['bid_size_change'] = df['bid_size'].pct_change()
    
    # 11. Ask size change ratio  
    df['ask_size_change'] = df['ask_size'].pct_change()
    
    # 12. Spread z-score (spread relative to recent mean)
    spread_ma = df['spread'].rolling(24, min_periods=6).mean().shift(1)
    spread_std = df['spread'].rolling(24, min_periods=6).std().shift(1)
    df['spread_zscore'] = np.where(spread_std > 0, (df['spread'] - spread_ma) / spread_std, np.nan)
    
    # 13. Price acceleration (velocity change)
    df['price_accel'] = df['price_velocity'] - df['price_velocity'].shift(1)
    
    # Future prices — but ONLY for continuous bars
    for hold in HOLD_PERIODS:
        df[f'future_price_{hold}'] = df['price'].shift(-hold)
        # Nullify if any gap in the next N bars
        for offset in range(1, hold + 1):
            gap_mask = df['is_continuous'].shift(-offset) == False
            df.loc[gap_mask, f'future_price_{hold}'] = np.nan
        df[f'return_{hold}'] = (df[f'future_price_{hold}'] - df['price']) / df['price']
    
    return df


def test_signals(df, product):
    """Test all combinations."""
    
    indicators = [
        'spread', 'spread_change', 'book_imbalance', 'trade_imbalance',
        'volume_surge', 'price_velocity', 'flow_ratio', 'vwap_dev',
        'book_imb_change', 'bid_size_change', 'ask_size_change',
        'spread_zscore', 'price_accel'
    ]
    
    results = []
    
    n = len(df)
    half = n // 2
    train = df.iloc[:half].copy()
    test = df.iloc[half:].copy()
    
    for indicator in indicators:
        valid_train = train[indicator].dropna()
        valid_test = test[indicator].dropna()
        if len(valid_train) < 100 or len(valid_test) < 100:
            continue
        
        # Compute percentiles from TRAIN only
        train_vals = train[indicator].dropna().values
        percentiles = {p: np.percentile(train_vals, p) for p in PERCENTILE_THRESHOLDS}
        
        for pct in PERCENTILE_THRESHOLDS:
            threshold = percentiles[pct]
            
            for direction in ['long', 'short']:
                for hold in HOLD_PERIODS:
                    ret_col = f'return_{hold}'
                    
                    if pct <= 50:
                        train_mask = (train[indicator] <= threshold) & train[ret_col].notna()
                        test_mask = (test[indicator] <= threshold) & test[ret_col].notna()
                    else:
                        train_mask = (train[indicator] >= threshold) & train[ret_col].notna()
                        test_mask = (test[indicator] >= threshold) & test[ret_col].notna()
                    
                    train_signals = train[train_mask]
                    test_signals = test[test_mask]
                    
                    if len(train_signals) < MIN_OCCURRENCES or len(test_signals) < MIN_OCCURRENCES:
                        continue
                    
                    if direction == 'long':
                        train_returns = train_signals[ret_col].values - RT_FEE
                        test_returns = test_signals[ret_col].values - RT_FEE
                    else:
                        train_returns = -train_signals[ret_col].values - RT_FEE
                        test_returns = -test_signals[ret_col].values - RT_FEE
                    
                    train_wr = np.mean(train_returns > 0)
                    test_wr = np.mean(test_returns > 0)
                    train_avg = np.mean(train_returns) * 100
                    test_avg = np.mean(test_returns) * 100
                    train_med = np.median(train_returns) * 100
                    test_med = np.median(test_returns) * 100
                    
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
                            'train_med_ret': train_med,
                            'test_med_ret': test_med,
                        })
    
    return results


def generate_report(results, product_stats):
    lines = []
    lines.append("# AUGUR Short-Hold Signal Discovery")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"**Data:** Monday Feb 9 2026, 14:00-23:00 UTC")
    lines.append(f"**Bar size:** 5 seconds")
    lines.append(f"**Round-trip fees:** 0.20% (VIP 2 taker)")
    lines.append(f"**Hold periods:** 15s, 30s, 60s")
    lines.append(f"**Train/Test:** First half / Second half of Monday data")
    lines.append("")
    lines.append("## Validation Criteria")
    lines.append("- Both train AND test profitable after 0.20% RT fees")
    lines.append("- Minimum 50 occurrences in each half")
    lines.append("- Win rate > 53% in both halves")
    lines.append("- No lookahead bias (percentiles computed on train only)")
    lines.append("- Gap-aware: future returns nullified across non-continuous bars")
    lines.append("")
    
    lines.append("## Data Summary")
    lines.append("")
    lines.append("| Product | OB Bars | Valid Returns (30s) | 30s Volatility |")
    lines.append("|---------|---------|--------------------|-----------------| ")
    for ps in sorted(product_stats, key=lambda x: -x['vol_30s']):
        lines.append(f"| {ps['product']} | {ps['bars']:,} | {ps['valid_returns']} | {ps['vol_30s']:.4f}% |")
    lines.append("")
    
    if not results:
        lines.append("## ❌ NO PASSING SIGNALS FOUND")
        lines.append("")
        lines.append("No indicator/threshold combinations passed all validation criteria.")
        lines.append("")
        lines.append("### Analysis")
        lines.append("At 5s bar resolution with 0.20% round-trip fees, the fee burden relative")
        lines.append("to achievable alpha at 15-60s hold periods appears too high for single-indicator signals.")
        lines.append("Potential next steps:")
        lines.append("- Test stacked signals (multiple conditions)")
        lines.append("- Test wider hold periods (2-5 min)")
        lines.append("- Test with maker fees (0.05% each way = 0.10% RT)")
        lines.append("- Focus on highest-volatility products only")
        return '\n'.join(lines)
    
    lines.append(f"## ✅ {len(results)} PASSING SIGNALS FOUND")
    lines.append("")
    
    # Group by product
    by_product = {}
    for r in results:
        by_product.setdefault(r['product'], []).append(r)
    
    for product, prod_results in sorted(by_product.items(), key=lambda x: -max(r['test_avg_ret'] for r in x[1])):
        lines.append(f"### {product}: {len(prod_results)} signals")
        lines.append("")
        lines.append("| Indicator | Pctl | Dir | Hold | Train N | Train WR | Train Ret | Test N | Test WR | Test Ret |")
        lines.append("|-----------|------|-----|------|---------|----------|-----------|--------|---------|----------|")
        
        for r in sorted(prod_results, key=lambda x: x['test_avg_ret'], reverse=True):
            lines.append(
                f"| {r['indicator']} | {r['percentile']} | {r['direction']} | {r['hold']} | "
                f"{r['train_n']} | {r['train_wr']:.1%} | {r['train_avg_ret']:+.4f}% | "
                f"{r['test_n']} | {r['test_wr']:.1%} | {r['test_avg_ret']:+.4f}% |"
            )
        lines.append("")
    
    # Top 10
    lines.append("## Top 10 Actionable Signals")
    lines.append("")
    for i, r in enumerate(results[:10]):
        lines.append(f"**{i+1}. {r['product']} — {r['indicator']} {r['percentile']} → {r['direction'].upper()} {r['hold']}**")
        lines.append(f"   - Threshold: {r['threshold']:.8f}")
        lines.append(f"   - Train: {r['train_n']} trades, {r['train_wr']:.1%} WR, {r['train_avg_ret']:+.4f}% avg")
        lines.append(f"   - Test:  {r['test_n']} trades, {r['test_wr']:.1%} WR, {r['test_avg_ret']:+.4f}% avg")
        lines.append("")
    
    # Summary tables
    lines.append("## Summary by Hold Period")
    for hl in ['15s', '30s', '60s']:
        hr = [r for r in results if r['hold'] == hl]
        if hr:
            lines.append(f"- **{hl}:** {len(hr)} signals, best test return {max(r['test_avg_ret'] for r in hr):+.4f}%")
        else:
            lines.append(f"- **{hl}:** None")
    lines.append("")
    
    lines.append("## Summary by Indicator")
    by_ind = {}
    for r in results:
        by_ind.setdefault(r['indicator'], []).append(r)
    for ind, ir in sorted(by_ind.items(), key=lambda x: -len(x[1])):
        lines.append(f"- **{ind}:** {len(ir)} signals, best {max(r['test_avg_ret'] for r in ir):+.4f}%")
    lines.append("")
    
    return '\n'.join(lines)


def main():
    conn = sqlite3.connect(DB_PATH)
    
    all_results = []
    product_stats = []
    
    print("=== AUGUR Short-Hold Signal Discovery V2 ===")
    print(f"Testing {len(PRODUCTS)} products × 13 indicators × {len(PERCENTILE_THRESHOLDS)} thresholds × 2 dirs × 3 holds")
    print(f"= {len(PRODUCTS) * 13 * len(PERCENTILE_THRESHOLDS) * 2 * 3:,} combinations")
    print()
    
    for product in PRODUCTS:
        df = load_data(conn, product)
        if df is None:
            print(f"  {product}: SKIP (insufficient OB data)")
            continue
        
        df = compute_indicators(df)
        
        # Stats
        ret_30 = df['return_6'].dropna()
        vol_30 = ret_30.std() * 100 if len(ret_30) > 10 else 0
        
        ps = {'product': product, 'bars': len(df), 'valid_returns': len(ret_30), 'vol_30s': vol_30}
        product_stats.append(ps)
        
        # Skip low-volatility products where fees > 1 std
        if vol_30 < 0.05:
            print(f"  {product}: SKIP (30s vol {vol_30:.4f}% < 0.05% — fees dominate)")
            continue
        
        results = test_signals(df, product)
        all_results.extend(results)
        
        if results:
            best = max(results, key=lambda x: x['test_avg_ret'])
            print(f"  {product}: {len(df)} bars, vol={vol_30:.3f}%, {len(results)} signals ★ best={best['indicator']} {best['percentile']} {best['direction']} {best['hold']} → {best['test_avg_ret']:+.4f}%")
        else:
            print(f"  {product}: {len(df)} bars, vol={vol_30:.3f}%, NO signals")
    
    conn.close()
    
    all_results.sort(key=lambda x: x['test_avg_ret'], reverse=True)
    
    report = generate_report(all_results, product_stats)
    output_path = '/home/bonsaihorn/.openclaw/workspace/analysis/augur-short-hold-discovery.md'
    with open(output_path, 'w') as f:
        f.write(report)
    
    print(f"\nReport: {output_path}")
    print(f"Total passing signals: {len(all_results)}")
    
    if all_results:
        print(f"\n=== TOP 20 ===")
        for i, r in enumerate(all_results[:20]):
            print(f"{i+1}. {r['product']} {r['indicator']} {r['percentile']} {r['direction']} {r['hold']}: "
                  f"Train {r['train_n']}t {r['train_wr']:.1%}WR {r['train_avg_ret']:+.4f}% | "
                  f"Test {r['test_n']}t {r['test_wr']:.1%}WR {r['test_avg_ret']:+.4f}%")
    else:
        # Deep diagnostic
        print("\n=== DIAGNOSTIC: Why no signals? ===")
        # Reload best product and check near-misses
        best_product = max(product_stats, key=lambda x: x['vol_30s'])
        print(f"Highest vol product: {best_product['product']} ({best_product['vol_30s']:.3f}%)")
        
        df = load_data(sqlite3.connect(DB_PATH), best_product['product'])
        df = compute_indicators(df)
        
        n = len(df)
        half = n // 2
        train = df.iloc[:half]
        test = df.iloc[half:]
        
        print("\nNear-misses (relaxed to WR>50%, avg>-0.05%):")
        for indicator in ['book_imbalance', 'trade_imbalance', 'spread', 'price_velocity', 'flow_ratio', 'spread_zscore']:
            valid = train[indicator].dropna()
            if len(valid) < 100:
                continue
            for pct in [10, 90]:
                thresh = np.percentile(valid.values, pct)
                for direction in ['long', 'short']:
                    for hold in HOLD_PERIODS:
                        ret_col = f'return_{hold}'
                        if pct <= 50:
                            mask_tr = (train[indicator] <= thresh) & train[ret_col].notna()
                            mask_te = (test[indicator] <= thresh) & test[ret_col].notna()
                        else:
                            mask_tr = (train[indicator] >= thresh) & train[ret_col].notna()
                            mask_te = (test[indicator] >= thresh) & test[ret_col].notna()
                        
                        ts = train[mask_tr]
                        te = test[mask_te]
                        if len(ts) < 30 or len(te) < 30:
                            continue
                        
                        if direction == 'long':
                            tr_ret = ts[ret_col].values - RT_FEE
                            te_ret = te[ret_col].values - RT_FEE
                        else:
                            tr_ret = -ts[ret_col].values - RT_FEE
                            te_ret = -te[ret_col].values - RT_FEE
                        
                        tr_wr = np.mean(tr_ret > 0)
                        te_wr = np.mean(te_ret > 0)
                        tr_avg = np.mean(tr_ret) * 100
                        te_avg = np.mean(te_ret) * 100
                        
                        if tr_wr > 0.50 and te_wr > 0.50 and tr_avg > -0.05 and te_avg > -0.05:
                            status = "✓" if (tr_wr >= 0.53 and te_wr >= 0.53 and tr_avg > 0 and te_avg > 0) else "~"
                            print(f"  {status} {indicator} p{pct} {direction} {HOLD_LABELS[hold]}: "
                                  f"Train {len(ts)}t {tr_wr:.1%} {tr_avg:+.4f}% | "
                                  f"Test {len(te)}t {te_wr:.1%} {te_avg:+.4f}%")


if __name__ == '__main__':
    main()
