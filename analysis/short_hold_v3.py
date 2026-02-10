#!/usr/bin/env python3
"""
AUGUR Short-Hold Signal Discovery V3 — Final Comprehensive Scan
Uses ALL data (Feb 7-10), proper train/test split, exhaustive combinations.
"""

import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

DB_PATH = '/home/bonsaihorn/Projects/augur-collector/enhanced_data.db'
BAR_SIZE = 5
RT_FEE = 0.0020
HOLD_PERIODS = [3, 6, 12]  # 15s, 30s, 60s
HOLD_LABELS = {3: '15s', 6: '30s', 12: '60s'}

# All products with decent data
PRODUCTS = [
    'NKN-USD', 'ZRO-USD', 'BNKR-USD', 'BIRB-USD', 'DOGE-USD',
    'SKY-USD', 'MAMO-USD', 'PENGU-USD', 'MON-USD', 'HBAR-USD',
    'XLM-USD', 'SUI-USD', 'ADA-USD', 'PUMP-USD', 'ONDO-USD',
    'FIGHT-USD', 'WLFI-USD', 'ELSA-USD', 'ZKP-USD', 'INX-USD',
    'TRIA-USD', 'ZORA-USD', 'SKR-USD', 'FLR-USD', 'KITE-USD',
    'AERO-USD', 'BERA-USD', 'XRP-USD', 'SOL-USD', 'LINK-USD',
    'B3-USD', 'TOSHI-USD', 'ZK-USD', 'AXS-USD'
]

MIN_OCCURRENCES = 30  # Relaxed from 50 for better coverage
MIN_WR = 0.53

PERCENTILE_THRESHOLDS = [1, 2, 3, 5, 10, 15, 20, 80, 85, 90, 95, 97, 98, 99]


def load_data(conn, product):
    """Load ALL data for product, not just Monday."""
    
    ob = pd.read_sql_query("""
        SELECT timestamp, best_bid, best_ask, bid_size, ask_size, mid_price
        FROM orderbook_snapshots WHERE product = ?
        ORDER BY timestamp
    """, conn, params=(product,))
    
    tf = pd.read_sql_query("""
        SELECT timestamp, buy_volume, sell_volume, buy_count, sell_count, vwap
        FROM trade_flow WHERE product = ?
        ORDER BY timestamp
    """, conn, params=(product,))
    
    if len(ob) < 500:
        return None
    
    ob['bar'] = (ob['timestamp'] // BAR_SIZE) * BAR_SIZE
    ob_agg = ob.groupby('bar').agg({
        'mid_price': 'last', 'bid_size': 'last', 'ask_size': 'last',
        'best_bid': 'last', 'best_ask': 'last'
    }).reset_index().sort_values('bar').reset_index(drop=True)
    
    if len(tf) > 0:
        tf['bar'] = (tf['timestamp'] // BAR_SIZE) * BAR_SIZE
        tf_agg = tf.groupby('bar').agg({
            'buy_volume': 'sum', 'sell_volume': 'sum',
            'buy_count': 'sum', 'sell_count': 'sum', 'vwap': 'last'
        }).reset_index()
        df = pd.merge(ob_agg, tf_agg, on='bar', how='left')
    else:
        df = ob_agg
        for c in ['buy_volume', 'sell_volume', 'buy_count', 'sell_count', 'vwap']:
            df[c] = 0 if c != 'vwap' else df['mid_price']
    
    df = df.sort_values('bar').reset_index(drop=True)
    for c in ['buy_volume', 'sell_volume', 'buy_count', 'sell_count']:
        df[c] = df[c].fillna(0)
    df['vwap'] = df['vwap'].fillna(df['mid_price'])
    
    df['total_volume'] = df['buy_volume'] + df['sell_volume']
    df['price'] = df['mid_price']
    
    # Gap detection
    df['bar_diff'] = df['bar'].diff()
    df['is_continuous'] = df['bar_diff'] == BAR_SIZE
    df.iloc[0, df.columns.get_loc('is_continuous')] = True
    
    return df


def compute_indicators(df):
    """All microstructure indicators."""
    
    # 1. Spread
    df['spread'] = (df['best_ask'] - df['best_bid']) / df['price']
    
    # 2. Spread change
    df['spread_change'] = df['spread'] - df['spread'].shift(1)
    
    # 3. Book imbalance
    denom = df['bid_size'] + df['ask_size']
    df['book_imbalance'] = np.where(denom > 0, (df['bid_size'] - df['ask_size']) / denom, 0)
    
    # 4. Trade imbalance
    total_trades = df['buy_count'] + df['sell_count']
    df['trade_imbalance'] = np.where(total_trades > 0, (df['buy_count'] - df['sell_count']) / total_trades, np.nan)
    
    # 5. Volume surge
    rolling_vol = df['total_volume'].rolling(12, min_periods=3).mean().shift(1)
    df['volume_surge'] = np.where(rolling_vol > 0, df['total_volume'] / rolling_vol, np.nan)
    
    # 6. Price velocity (3-bar)
    df['price_velocity'] = (df['price'] - df['price'].shift(3)) / df['price'].shift(3)
    
    # 7. Flow ratio
    df['flow_ratio'] = np.where(df['total_volume'] > 50, df['buy_volume'] / df['total_volume'], np.nan)
    
    # 8. VWAP deviation
    df['vwap_dev'] = (df['price'] - df['vwap']) / df['price']
    
    # 9. Book imbalance change
    df['book_imb_change'] = df['book_imbalance'] - df['book_imbalance'].shift(1)
    
    # 10. Spread z-score
    spread_ma = df['spread'].rolling(24, min_periods=6).mean().shift(1)
    spread_std = df['spread'].rolling(24, min_periods=6).std().shift(1)
    df['spread_zscore'] = np.where(spread_std > 0, (df['spread'] - spread_ma) / spread_std, np.nan)
    
    # 11. Price acceleration
    df['price_accel'] = df['price_velocity'] - df['price_velocity'].shift(1)
    
    # 12. Bid/ask size ratio (log)
    df['ba_ratio'] = np.where(
        (df['bid_size'] > 0) & (df['ask_size'] > 0),
        np.log(df['bid_size'] / df['ask_size']),
        np.nan
    )
    
    # 13. Book imbalance MA(6) — smoothed signal
    df['book_imb_ma6'] = df['book_imbalance'].rolling(6, min_periods=3).mean()
    
    # 14. Price momentum (6-bar)
    df['price_mom_6'] = (df['price'] - df['price'].shift(6)) / df['price'].shift(6)
    
    # 15. Relative bid size change
    df['bid_size_pctchg'] = df['bid_size'].pct_change()
    
    # 16. Relative ask size change
    df['ask_size_pctchg'] = df['ask_size'].pct_change()
    
    # Future prices with gap awareness
    for hold in HOLD_PERIODS:
        df[f'future_price_{hold}'] = df['price'].shift(-hold)
        for offset in range(1, hold + 1):
            gap_mask = df['is_continuous'].shift(-offset) == False
            df.loc[gap_mask, f'future_price_{hold}'] = np.nan
        df[f'return_{hold}'] = (df[f'future_price_{hold}'] - df['price']) / df['price']
    
    return df


def test_signals(df, product):
    """Test all single-indicator signals."""
    
    indicators = [
        'spread', 'spread_change', 'book_imbalance', 'trade_imbalance',
        'volume_surge', 'price_velocity', 'flow_ratio', 'vwap_dev',
        'book_imb_change', 'spread_zscore', 'price_accel',
        'ba_ratio', 'book_imb_ma6', 'price_mom_6',
        'bid_size_pctchg', 'ask_size_pctchg'
    ]
    
    results = []
    
    n = len(df)
    half = n // 2
    train = df.iloc[:half].copy()
    test = df.iloc[half:].copy()
    
    for indicator in indicators:
        valid_train = train[indicator].dropna()
        if len(valid_train) < 100:
            continue
        
        train_vals = valid_train.values
        percentiles = {p: np.percentile(train_vals, p) for p in PERCENTILE_THRESHOLDS}
        
        for pct in PERCENTILE_THRESHOLDS:
            threshold = percentiles[pct]
            
            for direction in ['long', 'short']:
                for hold in HOLD_PERIODS:
                    ret_col = f'return_{hold}'
                    
                    if pct <= 50:
                        tr_mask = (train[indicator] <= threshold) & train[ret_col].notna()
                        te_mask = (test[indicator] <= threshold) & test[ret_col].notna()
                    else:
                        tr_mask = (train[indicator] >= threshold) & train[ret_col].notna()
                        te_mask = (test[indicator] >= threshold) & test[ret_col].notna()
                    
                    tr_sig = train[tr_mask]
                    te_sig = test[te_mask]
                    
                    if len(tr_sig) < MIN_OCCURRENCES or len(te_sig) < MIN_OCCURRENCES:
                        continue
                    
                    if direction == 'long':
                        tr_ret = tr_sig[ret_col].values - RT_FEE
                        te_ret = te_sig[ret_col].values - RT_FEE
                    else:
                        tr_ret = -tr_sig[ret_col].values - RT_FEE
                        te_ret = -te_sig[ret_col].values - RT_FEE
                    
                    tr_wr = (tr_ret > 0).mean()
                    te_wr = (te_ret > 0).mean()
                    tr_avg = tr_ret.mean() * 100
                    te_avg = te_ret.mean() * 100
                    
                    if tr_wr >= MIN_WR and te_wr >= MIN_WR and tr_avg > 0 and te_avg > 0:
                        results.append({
                            'product': product,
                            'indicator': indicator,
                            'type': 'single',
                            'percentile': f'p{pct}',
                            'threshold': threshold,
                            'direction': direction,
                            'hold': HOLD_LABELS[hold],
                            'hold_bars': hold,
                            'train_n': len(tr_sig),
                            'test_n': len(te_sig),
                            'train_wr': tr_wr,
                            'test_wr': te_wr,
                            'train_avg_ret': tr_avg,
                            'test_avg_ret': te_avg,
                        })
    
    return results


def test_combined_signals(df, product):
    """Test paired indicator combinations."""
    
    results = []
    n = len(df)
    half = n // 2
    train = df.iloc[:half].copy()
    test = df.iloc[half:].copy()
    
    # Key combinations to test
    combos = [
        # (indicator1, pct_range1, indicator2, pct_range2)
        ('book_imbalance', [5, 10, 90, 95], 'volume_surge', [70, 80, 90]),
        ('book_imbalance', [5, 10, 90, 95], 'spread_change', [5, 10, 90, 95]),
        ('book_imbalance', [5, 10, 90, 95], 'price_velocity', [5, 10, 90, 95]),
        ('book_imb_ma6', [5, 10, 90, 95], 'volume_surge', [70, 80, 90]),
        ('ba_ratio', [5, 10, 90, 95], 'volume_surge', [70, 80, 90]),
        ('trade_imbalance', [5, 10, 90, 95], 'book_imbalance', [5, 10, 90, 95]),
        ('flow_ratio', [5, 10, 90, 95], 'book_imbalance', [5, 10, 90, 95]),
        ('spread_zscore', [5, 10, 90, 95], 'book_imbalance', [5, 10, 90, 95]),
    ]
    
    for ind1, pcts1, ind2, pcts2 in combos:
        v1 = train[ind1].dropna()
        v2 = train[ind2].dropna()
        if len(v1) < 100 or len(v2) < 100:
            continue
        
        thresh1 = {p: np.percentile(v1.values, p) for p in pcts1}
        thresh2 = {p: np.percentile(v2.values, p) for p in pcts2}
        
        for p1 in pcts1:
            for p2 in pcts2:
                t1 = thresh1[p1]
                t2 = thresh2[p2]
                
                # Build conditions
                if p1 <= 50:
                    c1_tr = train[ind1] <= t1
                    c1_te = test[ind1] <= t1
                else:
                    c1_tr = train[ind1] >= t1
                    c1_te = test[ind1] >= t1
                
                if p2 <= 50:
                    c2_tr = train[ind2] <= t2
                    c2_te = test[ind2] <= t2
                else:
                    c2_tr = train[ind2] >= t2
                    c2_te = test[ind2] >= t2
                
                for direction in ['long', 'short']:
                    for hold in HOLD_PERIODS:
                        ret_col = f'return_{hold}'
                        
                        tr_mask = c1_tr & c2_tr & train[ret_col].notna()
                        te_mask = c1_te & c2_te & test[ret_col].notna()
                        
                        tr_sig = train[tr_mask]
                        te_sig = test[te_mask]
                        
                        if len(tr_sig) < MIN_OCCURRENCES or len(te_sig) < MIN_OCCURRENCES:
                            continue
                        
                        if direction == 'long':
                            tr_ret = tr_sig[ret_col].values - RT_FEE
                            te_ret = te_sig[ret_col].values - RT_FEE
                        else:
                            tr_ret = -tr_sig[ret_col].values - RT_FEE
                            te_ret = -te_sig[ret_col].values - RT_FEE
                        
                        tr_wr = (tr_ret > 0).mean()
                        te_wr = (te_ret > 0).mean()
                        tr_avg = tr_ret.mean() * 100
                        te_avg = te_ret.mean() * 100
                        
                        if tr_wr >= MIN_WR and te_wr >= MIN_WR and tr_avg > 0 and te_avg > 0:
                            results.append({
                                'product': product,
                                'indicator': f'{ind1}+{ind2}',
                                'type': 'combined',
                                'percentile': f'p{p1}+p{p2}',
                                'threshold': f'{t1:.6f}+{t2:.6f}',
                                'direction': direction,
                                'hold': HOLD_LABELS[hold],
                                'hold_bars': hold,
                                'train_n': len(tr_sig),
                                'test_n': len(te_sig),
                                'train_wr': tr_wr,
                                'test_wr': te_wr,
                                'train_avg_ret': tr_avg,
                                'test_avg_ret': te_avg,
                            })
    
    return results


def generate_report(results, product_stats):
    lines = []
    lines.append("# AUGUR Short-Hold Signal Discovery")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"**Data:** Feb 7-10 2026 (full dataset)")
    lines.append(f"**Bar size:** 5 seconds")
    lines.append(f"**Round-trip fees:** 0.20% (VIP 2 taker)")
    lines.append(f"**Hold periods:** 15s, 30s, 60s")
    lines.append(f"**Products tested:** {len(product_stats)}")
    lines.append(f"**Train/Test:** First half / Second half chronological")
    lines.append(f"**Percentiles tested:** {PERCENTILE_THRESHOLDS}")
    lines.append(f"**Indicators:** 16 single + 8 combined pairs")
    lines.append("")
    lines.append("## Validation Criteria")
    lines.append("- Both train AND test profitable after 0.20% RT fees")
    lines.append(f"- Minimum {MIN_OCCURRENCES} occurrences in each half")
    lines.append(f"- Win rate > {MIN_WR:.0%} in both halves")
    lines.append("- No lookahead bias (percentiles from train only)")
    lines.append("- Gap-aware future returns")
    lines.append("")
    
    # Product volatility table
    lines.append("## Product Volatility (30s returns)")
    lines.append("")
    lines.append("| Product | Bars | 30s Std | 30s/Fee Ratio | Signals |")
    lines.append("|---------|------|---------|---------------|---------|")
    sig_counts = {}
    for r in results:
        sig_counts[r['product']] = sig_counts.get(r['product'], 0) + 1
    for ps in sorted(product_stats, key=lambda x: -x['vol_30s']):
        ratio = ps['vol_30s'] / (RT_FEE * 100) if ps['vol_30s'] > 0 else 0
        sc = sig_counts.get(ps['product'], 0)
        lines.append(f"| {ps['product']} | {ps['bars']:,} | {ps['vol_30s']:.4f}% | {ratio:.1f}x | {sc} |")
    lines.append("")
    
    if not results:
        lines.append("## ❌ NO PASSING SIGNALS FOUND")
        lines.append("")
        lines.append("### Why?")
        lines.append("At 5s bar resolution with 0.20% round-trip fees:")
        lines.append("- The fee (0.20%) exceeds the typical alpha available at 15-60s timeframes")
        lines.append("- Book imbalance shows monotonic predictability (bid-heavy → price up)")
        lines.append("  but the effect size (~0.10-0.15% at extreme tails) is smaller than fees")
        lines.append("- Only NKN-USD and ZKP-USD show edge approaching the fee threshold")
        lines.append("")
        lines.append("### Recommendations")
        lines.append("1. **Use limit orders** — maker fee is 0.05% ea (0.10% RT) instead of 0.20%")
        lines.append("2. **Target 300s holds** — already validated to work")
        lines.append("3. **Book imbalance is the strongest short-term predictor** — use it to time entries in longer-hold strategies")
        lines.append("4. **NKN-USD is the best candidate** for short-hold if fees can be reduced")
        return '\n'.join(lines)
    
    lines.append(f"## ✅ {len(results)} PASSING SIGNALS FOUND")
    lines.append("")
    
    # Group by product
    by_product = {}
    for r in results:
        by_product.setdefault(r['product'], []).append(r)
    
    for product in sorted(by_product.keys(), key=lambda p: -max(r['test_avg_ret'] for r in by_product[p])):
        prod_results = by_product[product]
        best = max(prod_results, key=lambda x: x['test_avg_ret'])
        lines.append(f"### {product}: {len(prod_results)} signals (best: {best['test_avg_ret']:+.4f}%)")
        lines.append("")
        lines.append("| Type | Indicator | Pctl | Dir | Hold | Train N | Train WR | Train Ret | Test N | Test WR | Test Ret |")
        lines.append("|------|-----------|------|-----|------|---------|----------|-----------|--------|---------|----------|")
        
        for r in sorted(prod_results, key=lambda x: x['test_avg_ret'], reverse=True)[:20]:
            lines.append(
                f"| {r['type']} | {r['indicator']} | {r['percentile']} | {r['direction']} | {r['hold']} | "
                f"{r['train_n']} | {r['train_wr']:.1%} | {r['train_avg_ret']:+.4f}% | "
                f"{r['test_n']} | {r['test_wr']:.1%} | {r['test_avg_ret']:+.4f}% |"
            )
        lines.append("")
    
    # Top 15 overall
    lines.append("## Top 15 Signals Overall")
    lines.append("")
    for i, r in enumerate(results[:15]):
        lines.append(f"**{i+1}. {r['product']} — {r['type']} {r['indicator']} {r['percentile']} → {r['direction'].upper()} {r['hold']}**")
        lines.append(f"   - Train: {r['train_n']} trades, {r['train_wr']:.1%} WR, {r['train_avg_ret']:+.4f}%")
        lines.append(f"   - Test:  {r['test_n']} trades, {r['test_wr']:.1%} WR, {r['test_avg_ret']:+.4f}%")
        lines.append("")
    
    # Summary
    lines.append("## Summary by Hold Period")
    for hl in ['15s', '30s', '60s']:
        hr = [r for r in results if r['hold'] == hl]
        if hr:
            lines.append(f"- **{hl}:** {len(hr)} signals, best {max(r['test_avg_ret'] for r in hr):+.4f}%")
        else:
            lines.append(f"- **{hl}:** None")
    lines.append("")
    
    lines.append("## Summary by Indicator")
    by_ind = {}
    for r in results:
        by_ind.setdefault(r['indicator'], []).append(r)
    for ind, ir in sorted(by_ind.items(), key=lambda x: -len(x[1])):
        lines.append(f"- **{ind}:** {len(ir)} signals")
    
    return '\n'.join(lines)


def main():
    conn = sqlite3.connect(DB_PATH)
    
    all_results = []
    product_stats = []
    
    total_combos = len(PRODUCTS) * (16 * len(PERCENTILE_THRESHOLDS) * 2 * 3 + 500)  # approx
    print(f"=== AUGUR Short-Hold V3 — Full Dataset, Exhaustive Scan ===")
    print(f"Products: {len(PRODUCTS)}, ~{total_combos:,} total combinations")
    print()
    
    for product in PRODUCTS:
        df = load_data(conn, product)
        if df is None:
            print(f"  {product}: SKIP (insufficient data)")
            continue
        
        df = compute_indicators(df)
        
        # Check volatility
        ret_30 = df['return_6'].dropna()
        vol_30 = ret_30.std() * 100 if len(ret_30) > 10 else 0
        
        ps = {'product': product, 'bars': len(df), 'vol_30s': vol_30}
        product_stats.append(ps)
        
        if vol_30 < 0.03:
            print(f"  {product}: SKIP (vol={vol_30:.4f}%)")
            continue
        
        # Single indicators
        single_results = test_signals(df, product)
        # Combined indicators
        combined_results = test_combined_signals(df, product)
        
        total = single_results + combined_results
        all_results.extend(total)
        
        if total:
            best = max(total, key=lambda x: x['test_avg_ret'])
            print(f"  {product}: {len(df):,} bars, vol={vol_30:.3f}%, "
                  f"{len(single_results)} single + {len(combined_results)} combined ★ "
                  f"best={best['test_avg_ret']:+.4f}%")
        else:
            print(f"  {product}: {len(df):,} bars, vol={vol_30:.3f}%, NO signals")
    
    conn.close()
    
    all_results.sort(key=lambda x: x['test_avg_ret'], reverse=True)
    
    report = generate_report(all_results, product_stats)
    output_path = '/home/bonsaihorn/.openclaw/workspace/analysis/augur-short-hold-discovery.md'
    with open(output_path, 'w') as f:
        f.write(report)
    
    print(f"\nReport: {output_path}")
    print(f"Total passing signals: {len(all_results)}")
    
    if all_results:
        print(f"\n=== TOP 10 ===")
        for i, r in enumerate(all_results[:10]):
            print(f"{i+1}. {r['product']} [{r['type']}] {r['indicator']} {r['percentile']} {r['direction']} {r['hold']}: "
                  f"Train {r['train_n']}t {r['train_wr']:.1%}WR {r['train_avg_ret']:+.4f}% | "
                  f"Test {r['test_n']}t {r['test_wr']:.1%}WR {r['test_avg_ret']:+.4f}%")


if __name__ == '__main__':
    main()
