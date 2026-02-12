#!/usr/bin/env python3
"""
AUGUR Short-Hold Signal Discovery — Final Version
Focused on highest-volatility products, full data, efficient queries.
"""

import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime
import warnings, time
warnings.filterwarnings('ignore')

DB_PATH = '/home/bonsaihorn/Projects/augur-collector/enhanced_data.db'
BAR_SIZE = 5
RT_FEE = 0.0020  # 0.20% round trip
RT_FEE_MAKER = 0.0010  # 0.10% round trip with limit orders
HOLD_PERIODS = [3, 6, 12]  # 15s, 30s, 60s
HOLD_LABELS = {3: '15s', 6: '30s', 12: '60s'}

# Focus on products we know have volatility from earlier analysis
# NKN: 0.834%, ZKP: 0.665%, BNKR: 0.428%, FIGHT: 0.242%, ELSA: 0.265%
# Also add a few more to check
PRODUCTS = ['NKN-USD', 'ZKP-USD', 'BNKR-USD', 'FIGHT-USD', 'ELSA-USD',
            'MAMO-USD', 'BIRB-USD', 'TRIA-USD', 'KITE-USD', 'SKY-USD']

MIN_OCCURRENCES = 30
MIN_WR = 0.53
PERCENTILE_THRESHOLDS = [1, 2, 3, 5, 10, 15, 20, 80, 85, 90, 95, 97, 98, 99]


def load_product_data(conn, product):
    """Load product data efficiently using PK index."""
    t0 = time.time()
    
    ob = pd.read_sql_query(
        "SELECT timestamp, best_bid, best_ask, bid_size, ask_size, mid_price "
        "FROM orderbook_snapshots WHERE product = ? ORDER BY timestamp",
        conn, params=(product,)
    )
    
    tf = pd.read_sql_query(
        "SELECT timestamp, buy_volume, sell_volume, buy_count, sell_count, vwap "
        "FROM trade_flow WHERE product = ? ORDER BY timestamp",
        conn, params=(product,)
    )
    
    t1 = time.time()
    
    if len(ob) < 500:
        return None, t1-t0
    
    # Aggregate into 5s bars
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
        df = ob_agg.copy()
        for c in ['buy_volume', 'sell_volume', 'buy_count', 'sell_count']:
            df[c] = 0.0
        df['vwap'] = df['mid_price']
    
    df = df.sort_values('bar').reset_index(drop=True)
    for c in ['buy_volume', 'sell_volume', 'buy_count', 'sell_count']:
        df[c] = df[c].fillna(0)
    df['vwap'] = df['vwap'].fillna(df['mid_price'])
    
    df['total_volume'] = df['buy_volume'] + df['sell_volume']
    df['price'] = df['mid_price']
    df['bar_diff'] = df['bar'].diff()
    df['is_continuous'] = df['bar_diff'] == BAR_SIZE
    df.iloc[0, df.columns.get_loc('is_continuous')] = True
    
    t2 = time.time()
    return df, t2-t0


def compute_all(df):
    """All indicators + forward returns."""
    
    p = df['price']
    
    # Book indicators
    denom = df['bid_size'] + df['ask_size']
    df['book_imbalance'] = np.where(denom > 0, (df['bid_size'] - df['ask_size']) / denom, 0)
    df['ba_ratio'] = np.where((df['bid_size'] > 0) & (df['ask_size'] > 0), 
                               np.log(df['bid_size'] / df['ask_size']), np.nan)
    df['book_imb_ma6'] = df['book_imbalance'].rolling(6, min_periods=3).mean()
    df['book_imb_change'] = df['book_imbalance'] - df['book_imbalance'].shift(1)
    
    # Spread indicators
    df['spread'] = (df['best_ask'] - df['best_bid']) / p
    df['spread_change'] = df['spread'] - df['spread'].shift(1)
    spread_ma = df['spread'].rolling(24, min_periods=6).mean().shift(1)
    spread_std = df['spread'].rolling(24, min_periods=6).std().shift(1)
    df['spread_zscore'] = np.where(spread_std > 0, (df['spread'] - spread_ma) / spread_std, np.nan)
    
    # Trade indicators
    total_trades = df['buy_count'] + df['sell_count']
    df['trade_imbalance'] = np.where(total_trades > 0, 
                                      (df['buy_count'] - df['sell_count']) / total_trades, np.nan)
    
    # Volume
    rolling_vol = df['total_volume'].rolling(12, min_periods=3).mean().shift(1)
    df['volume_surge'] = np.where(rolling_vol > 0, df['total_volume'] / rolling_vol, np.nan)
    
    # Flow
    df['flow_ratio'] = np.where(df['total_volume'] > 50, df['buy_volume'] / df['total_volume'], np.nan)
    
    # Price indicators
    df['price_velocity'] = (p - p.shift(3)) / p.shift(3)
    df['price_accel'] = df['price_velocity'] - df['price_velocity'].shift(1)
    df['price_mom_6'] = (p - p.shift(6)) / p.shift(6)
    
    # VWAP
    df['vwap_dev'] = (p - df['vwap']) / p
    
    # Size changes
    df['bid_size_pctchg'] = df['bid_size'].pct_change()
    df['ask_size_pctchg'] = df['ask_size'].pct_change()
    
    # Forward returns (gap-aware)
    for hold in HOLD_PERIODS:
        df[f'future_price_{hold}'] = p.shift(-hold)
        for offset in range(1, hold + 1):
            gap = df['is_continuous'].shift(-offset) == False
            df.loc[gap, f'future_price_{hold}'] = np.nan
        df[f'return_{hold}'] = (df[f'future_price_{hold}'] - p) / p
    
    return df


def scan_single(df):
    """Scan all single-indicator signals."""
    indicators = [
        'book_imbalance', 'ba_ratio', 'book_imb_ma6', 'book_imb_change',
        'spread', 'spread_change', 'spread_zscore',
        'trade_imbalance', 'volume_surge', 'flow_ratio',
        'price_velocity', 'price_accel', 'price_mom_6', 'vwap_dev',
        'bid_size_pctchg', 'ask_size_pctchg'
    ]
    
    n = len(df)
    half = n // 2
    train = df.iloc[:half]
    test = df.iloc[half:]
    results = []
    
    for ind in indicators:
        vals = train[ind].dropna().values
        if len(vals) < 100:
            continue
        
        thresholds = {p: np.percentile(vals, p) for p in PERCENTILE_THRESHOLDS}
        
        for pct in PERCENTILE_THRESHOLDS:
            t = thresholds[pct]
            
            if pct <= 50:
                tr_cond = train[ind] <= t
                te_cond = test[ind] <= t
            else:
                tr_cond = train[ind] >= t
                te_cond = test[ind] >= t
            
            for direction in ['long', 'short']:
                for hold in HOLD_PERIODS:
                    rc = f'return_{hold}'
                    
                    tr_m = tr_cond & train[rc].notna()
                    te_m = te_cond & test[rc].notna()
                    
                    tr_n = tr_m.sum()
                    te_n = te_m.sum()
                    if tr_n < MIN_OCCURRENCES or te_n < MIN_OCCURRENCES:
                        continue
                    
                    tr_vals = train.loc[tr_m, rc].values
                    te_vals = test.loc[te_m, rc].values
                    
                    if direction == 'short':
                        tr_vals = -tr_vals
                        te_vals = -te_vals
                    
                    # Test at BOTH fee levels
                    for fee, fee_label in [(RT_FEE, 'taker'), (RT_FEE_MAKER, 'maker')]:
                        tr_ret = tr_vals - fee
                        te_ret = te_vals - fee
                        
                        tr_wr = (tr_ret > 0).mean()
                        te_wr = (te_ret > 0).mean()
                        tr_avg = tr_ret.mean() * 100
                        te_avg = te_ret.mean() * 100
                        
                        if tr_wr >= MIN_WR and te_wr >= MIN_WR and tr_avg > 0 and te_avg > 0:
                            results.append({
                                'indicator': ind,
                                'type': 'single',
                                'percentile': f'p{pct}',
                                'threshold': t,
                                'direction': direction,
                                'hold': HOLD_LABELS[hold],
                                'fee_type': fee_label,
                                'fee': fee * 100,
                                'train_n': int(tr_n),
                                'test_n': int(te_n),
                                'train_wr': tr_wr,
                                'test_wr': te_wr,
                                'train_avg': tr_avg,
                                'test_avg': te_avg,
                            })
    
    return results


def scan_combined(df):
    """Scan paired indicator signals."""
    n = len(df)
    half = n // 2
    train = df.iloc[:half]
    test = df.iloc[half:]
    results = []
    
    combos = [
        ('book_imbalance', [5, 10, 90, 95], 'volume_surge', [70, 80, 90]),
        ('book_imbalance', [5, 10, 90, 95], 'spread_change', [5, 10, 90, 95]),
        ('book_imbalance', [5, 10, 90, 95], 'price_velocity', [5, 10, 90, 95]),
        ('book_imb_ma6', [5, 10, 90, 95], 'volume_surge', [70, 80, 90]),
        ('ba_ratio', [5, 10, 90, 95], 'volume_surge', [70, 80, 90]),
        ('trade_imbalance', [5, 10, 90, 95], 'book_imbalance', [10, 90]),
        ('flow_ratio', [10, 20, 80, 90], 'book_imbalance', [10, 90]),
        ('spread_zscore', [5, 10, 90, 95], 'book_imbalance', [10, 90]),
        ('book_imbalance', [5, 10, 90, 95], 'book_imb_change', [10, 90]),
    ]
    
    for ind1, pcts1, ind2, pcts2 in combos:
        v1 = train[ind1].dropna().values
        v2 = train[ind2].dropna().values
        if len(v1) < 100 or len(v2) < 100:
            continue
        
        t1map = {p: np.percentile(v1, p) for p in pcts1}
        t2map = {p: np.percentile(v2, p) for p in pcts2}
        
        for p1 in pcts1:
            for p2 in pcts2:
                c1_tr = (train[ind1] <= t1map[p1]) if p1 <= 50 else (train[ind1] >= t1map[p1])
                c1_te = (test[ind1] <= t1map[p1]) if p1 <= 50 else (test[ind1] >= t1map[p1])
                c2_tr = (train[ind2] <= t2map[p2]) if p2 <= 50 else (train[ind2] >= t2map[p2])
                c2_te = (test[ind2] <= t2map[p2]) if p2 <= 50 else (test[ind2] >= t2map[p2])
                
                for direction in ['long', 'short']:
                    for hold in HOLD_PERIODS:
                        rc = f'return_{hold}'
                        
                        tr_m = c1_tr & c2_tr & train[rc].notna()
                        te_m = c1_te & c2_te & test[rc].notna()
                        
                        tr_n = tr_m.sum()
                        te_n = te_m.sum()
                        if tr_n < MIN_OCCURRENCES or te_n < MIN_OCCURRENCES:
                            continue
                        
                        tr_vals = train.loc[tr_m, rc].values
                        te_vals = test.loc[te_m, rc].values
                        
                        if direction == 'short':
                            tr_vals = -tr_vals
                            te_vals = -te_vals
                        
                        for fee, fee_label in [(RT_FEE, 'taker'), (RT_FEE_MAKER, 'maker')]:
                            tr_ret = tr_vals - fee
                            te_ret = te_vals - fee
                            
                            tr_wr = (tr_ret > 0).mean()
                            te_wr = (te_ret > 0).mean()
                            tr_avg = tr_ret.mean() * 100
                            te_avg = te_ret.mean() * 100
                            
                            if tr_wr >= MIN_WR and te_wr >= MIN_WR and tr_avg > 0 and te_avg > 0:
                                results.append({
                                    'indicator': f'{ind1}+{ind2}',
                                    'type': 'combined',
                                    'percentile': f'p{p1}+p{p2}',
                                    'threshold': f'{t1map[p1]:.6f}+{t2map[p2]:.6f}',
                                    'direction': direction,
                                    'hold': HOLD_LABELS[hold],
                                    'fee_type': fee_label,
                                    'fee': fee * 100,
                                    'train_n': int(tr_n),
                                    'test_n': int(te_n),
                                    'train_wr': tr_wr,
                                    'test_wr': te_wr,
                                    'train_avg': tr_avg,
                                    'test_avg': te_avg,
                                })
    
    return results


def main():
    conn = sqlite3.connect(DB_PATH)
    
    all_results = []
    product_stats = []
    
    print("=== AUGUR Short-Hold Signal Discovery — Final ===")
    print(f"Products: {PRODUCTS}")
    print(f"Testing at BOTH taker (0.20% RT) and maker (0.10% RT) fee levels")
    print()
    
    for product in PRODUCTS:
        df, load_time = load_product_data(conn, product)
        if df is None:
            print(f"  {product}: SKIP (insufficient data, loaded in {load_time:.1f}s)")
            continue
        
        df = compute_all(df)
        
        ret_30 = df['return_6'].dropna()
        vol_30 = ret_30.std() * 100 if len(ret_30) > 10 else 0
        product_stats.append({'product': product, 'bars': len(df), 'vol_30s': vol_30, 'load_time': load_time})
        
        if vol_30 < 0.03:
            print(f"  {product}: SKIP (vol={vol_30:.4f}%, loaded in {load_time:.1f}s)")
            continue
        
        single = scan_single(df)
        combined = scan_combined(df)
        
        product_results = single + combined
        for r in product_results:
            r['product'] = product
        all_results.extend(product_results)
        
        taker_results = [r for r in product_results if r['fee_type'] == 'taker']
        maker_results = [r for r in product_results if r['fee_type'] == 'maker']
        
        if product_results:
            best = max(product_results, key=lambda x: x['test_avg'])
            print(f"  {product}: {len(df):,} bars, vol={vol_30:.3f}%, loaded in {load_time:.1f}s")
            print(f"    → {len(taker_results)} taker signals, {len(maker_results)} maker signals")
            print(f"    → best: {best['indicator']} {best['percentile']} {best['direction']} {best['hold']} ({best['fee_type']}): {best['test_avg']:+.4f}%")
        else:
            print(f"  {product}: {len(df):,} bars, vol={vol_30:.3f}%, loaded in {load_time:.1f}s, NO signals")
    
    conn.close()
    
    all_results.sort(key=lambda x: x['test_avg'], reverse=True)
    
    # Generate report
    report = generate_full_report(all_results, product_stats)
    output_path = '/home/bonsaihorn/.openclaw/workspace/analysis/augur-short-hold-discovery.md'
    with open(output_path, 'w') as f:
        f.write(report)
    
    print(f"\nReport: {output_path}")
    print(f"Total: {len(all_results)} signals ({len([r for r in all_results if r['fee_type']=='taker'])} taker, {len([r for r in all_results if r['fee_type']=='maker'])} maker)")
    
    if all_results:
        print(f"\n=== TOP 15 ===")
        for i, r in enumerate(all_results[:15]):
            print(f"{i+1}. {r['product']} [{r['fee_type']}] {r['indicator']} {r['percentile']} {r['direction']} {r['hold']}: "
                  f"Train {r['train_n']}t {r['train_wr']:.1%} {r['train_avg']:+.4f}% | "
                  f"Test {r['test_n']}t {r['test_wr']:.1%} {r['test_avg']:+.4f}%")


def generate_full_report(results, product_stats):
    lines = []
    lines.append("# AUGUR Short-Hold Signal Discovery")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"**Data:** Feb 7-10 2026 (all available data)")
    lines.append(f"**Bar size:** 5 seconds")
    lines.append(f"**Fee scenarios:** Taker 0.20% RT | Maker 0.10% RT")
    lines.append(f"**Hold periods:** 15s, 30s, 60s")
    lines.append(f"**Products tested:** {len(product_stats)}")
    lines.append(f"**Train/Test:** First half / Second half chronological")
    lines.append("")
    lines.append("## Validation Criteria")
    lines.append(f"- Both train AND test profitable after fees")
    lines.append(f"- Minimum {MIN_OCCURRENCES} occurrences in each half")
    lines.append(f"- Win rate > {MIN_WR:.0%} in both halves")
    lines.append("- No lookahead bias")
    lines.append("- Gap-aware future returns")
    lines.append("")
    
    # Product table
    lines.append("## Product Data Summary")
    lines.append("| Product | Bars | 30s Vol | Fee Ratio (taker) | Fee Ratio (maker) |")
    lines.append("|---------|------|---------|-------------------|-------------------|")
    for ps in sorted(product_stats, key=lambda x: -x['vol_30s']):
        rt = ps['vol_30s'] / (RT_FEE * 100) if ps['vol_30s'] > 0 else 0
        rm = ps['vol_30s'] / (RT_FEE_MAKER * 100) if ps['vol_30s'] > 0 else 0
        lines.append(f"| {ps['product']} | {ps['bars']:,} | {ps['vol_30s']:.4f}% | {rt:.1f}x | {rm:.1f}x |")
    lines.append("")
    lines.append("*Fee Ratio = 30s volatility / round-trip fee. Higher = more room for edge.*")
    lines.append("")
    
    taker_results = [r for r in results if r['fee_type'] == 'taker']
    maker_results = [r for r in results if r['fee_type'] == 'maker']
    
    # === TAKER SECTION ===
    lines.append("---")
    lines.append(f"## Taker Fee Results (0.20% RT)")
    lines.append("")
    
    if not taker_results:
        lines.append("### ❌ NO SIGNALS pass at taker fees")
        lines.append("")
        lines.append("The 0.20% round-trip taker fee exceeds the available alpha at 15-60s holds.")
        lines.append("Book imbalance shows ~0.10-0.15% predictive edge at extreme tails — not enough.")
        lines.append("")
    else:
        lines.append(f"### ✅ {len(taker_results)} signals at taker fees")
        lines.append("")
        _emit_results_table(lines, taker_results)
    
    # === MAKER SECTION ===
    lines.append("---")
    lines.append(f"## Maker Fee Results (0.10% RT)")
    lines.append("")
    
    if not maker_results:
        lines.append("### ❌ NO SIGNALS pass even at maker fees")
        lines.append("")
    else:
        lines.append(f"### ✅ {len(maker_results)} signals at maker fees")
        lines.append("")
        _emit_results_table(lines, maker_results)
    
    # === CONCLUSIONS ===
    lines.append("---")
    lines.append("## Conclusions & Recommendations")
    lines.append("")
    
    if not results:
        lines.append("### The Fundamental Challenge")
        lines.append("At 5-second bar resolution with even maker fees (0.10% RT),")
        lines.append("microstructure indicators don't generate sufficient edge at 15-60s holds")
        lines.append("across the tested products. The predictive signal exists (book imbalance")
        lines.append("is monotonically correlated with future returns) but it's smaller than fees.")
        lines.append("")
        lines.append("### What IS Predictive")
        lines.append("- **Book imbalance** is the strongest single predictor of short-term price direction")
        lines.append("- The effect is ~0.07-0.15% in the top/bottom quintiles (vs 0.10-0.20% fees)")
        lines.append("- Extreme tails (p1-p3, p97-p99) show the biggest effects")
        lines.append("- NKN-USD shows the strongest edge (highest volatility/fee ratio)")
        lines.append("")
        lines.append("### Actionable Next Steps")
        lines.append("1. **Stick with 300s holds** — already validated, fees are a smaller % of returns")
        lines.append("2. **Use book imbalance as ENTRY TIMING** for longer-hold signals")
        lines.append("3. **Consider limit order strategies** — capturing the spread adds ~0.05-0.10%")
        lines.append("4. **If fees drop further** (higher volume tiers), revisit short-hold signals")
        lines.append("5. **Test NKN-USD at 2-3 minute holds** — sweet spot between edge and fee impact")
    else:
        lines.append("### Key Findings")
        # Group by fee type
        for ft in ['taker', 'maker']:
            fr = [r for r in results if r['fee_type'] == ft]
            if fr:
                best = max(fr, key=lambda x: x['test_avg'])
                lines.append(f"- **{ft.title()} ({len(fr)} signals):** Best edge {best['test_avg']:+.4f}% on {best['product']}")
        
        # Best product
        by_prod = {}
        for r in results:
            by_prod.setdefault(r['product'], []).append(r)
        for prod, pr in sorted(by_prod.items(), key=lambda x: -len(x[1])):
            lines.append(f"- **{prod}:** {len(pr)} signals")
    
    return '\n'.join(lines)


def _emit_results_table(lines, results):
    by_product = {}
    for r in results:
        by_product.setdefault(r['product'], []).append(r)
    
    for product in sorted(by_product.keys(), key=lambda p: -max(r['test_avg'] for r in by_product[p])):
        prod_results = by_product[product]
        lines.append(f"#### {product}: {len(prod_results)} signals")
        lines.append("")
        lines.append("| Type | Indicator | Pctl | Dir | Hold | Tr N | Tr WR | Tr Ret | Te N | Te WR | Te Ret |")
        lines.append("|------|-----------|------|-----|------|------|-------|--------|------|-------|--------|")
        for r in sorted(prod_results, key=lambda x: x['test_avg'], reverse=True)[:25]:
            lines.append(
                f"| {r['type']} | {r['indicator']} | {r['percentile']} | {r['direction']} | {r['hold']} | "
                f"{r['train_n']} | {r['train_wr']:.1%} | {r['train_avg']:+.4f}% | "
                f"{r['test_n']} | {r['test_wr']:.1%} | {r['test_avg']:+.4f}% |"
            )
        lines.append("")
    
    # Top 10 overall
    lines.append("#### Top 10 Overall")
    lines.append("")
    for i, r in enumerate(sorted(results, key=lambda x: x['test_avg'], reverse=True)[:10]):
        lines.append(f"**{i+1}. {r['product']} — {r['type']} {r['indicator']} {r['percentile']} → {r['direction'].upper()} {r['hold']}**")
        lines.append(f"   Train: {r['train_n']}t, {r['train_wr']:.1%} WR, {r['train_avg']:+.4f}%")
        lines.append(f"   Test:  {r['test_n']}t, {r['test_wr']:.1%} WR, {r['test_avg']:+.4f}%")
        lines.append("")


if __name__ == '__main__':
    main()
