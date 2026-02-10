#!/usr/bin/env python3
"""
AUGUR Signal Discovery - Exhaustive Search
Builds 5-second candles from 1s trade_flow data, computes indicators from PRIOR bars only,
and tests forward returns at multiple horizons.
"""

import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime, timezone
import time
import sys
import warnings
warnings.filterwarnings('ignore')

DB_PATH = '/home/bonsaihorn/Projects/augur-collector/enhanced_data.db'
OUTPUT_PATH = '/home/bonsaihorn/.openclaw/workspace/analysis/augur-signal-discovery.md'
RT_FEE = 0.0020  # 0.20% round-trip (VIP2 taker 0.10% each way)

# Products with enough data for meaningful analysis
MIN_ROWS = 5000  # Minimum 1s rows to include a product

def get_products(conn):
    """Get products with sufficient data."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT product, COUNT(*) as cnt 
        FROM trade_flow 
        GROUP BY product 
        HAVING cnt >= ? 
        ORDER BY cnt DESC
    """, (MIN_ROWS,))
    return [(r[0], r[1]) for r in cursor.fetchall()]

def load_trade_flow(conn, product):
    """Load trade_flow data for a product."""
    df = pd.read_sql_query(
        "SELECT timestamp, buy_volume, sell_volume, buy_count, sell_count, vwap "
        "FROM trade_flow WHERE product=? ORDER BY timestamp",
        conn, params=(product,)
    )
    return df

def load_orderbook(conn, product):
    """Load orderbook snapshot data for a product."""
    df = pd.read_sql_query(
        "SELECT timestamp, best_bid, best_ask, bid_size, ask_size, spread_pct, mid_price "
        "FROM orderbook_snapshots WHERE product=? ORDER BY timestamp",
        conn, params=(product,)
    )
    return df

def build_5s_candles(tf_df, ob_df=None):
    """Build 5-second candles from 1s trade_flow data, join with orderbook."""
    if len(tf_df) == 0:
        return pd.DataFrame()
    
    # Create 5-second time buckets
    tf_df = tf_df.copy()
    tf_df['bucket'] = (tf_df['timestamp'] // 5) * 5
    
    # Aggregate into 5s candles
    candles = tf_df.groupby('bucket').agg(
        open_vwap=('vwap', 'first'),
        close_vwap=('vwap', 'last'),
        high_vwap=('vwap', 'max'),
        low_vwap=('vwap', 'min'),
        buy_volume=('buy_volume', 'sum'),
        sell_volume=('sell_volume', 'sum'),
        buy_count=('buy_count', 'sum'),
        sell_count=('sell_count', 'sum'),
        tick_count=('timestamp', 'count'),
    ).reset_index()
    
    candles.rename(columns={'bucket': 'timestamp'}, inplace=True)
    
    # Filter out candles with zero VWAP (no real data)
    candles = candles[candles['close_vwap'] > 0].copy()
    
    # Add orderbook data if available
    if ob_df is not None and len(ob_df) > 0:
        ob = ob_df.copy()
        ob['bucket'] = (ob['timestamp'] // 5) * 5
        ob_agg = ob.groupby('bucket').agg(
            avg_bid_size=('bid_size', 'mean'),
            avg_ask_size=('ask_size', 'mean'),
            avg_spread_pct=('spread_pct', 'mean'),
            avg_mid_price=('mid_price', 'mean'),
        ).reset_index()
        ob_agg.rename(columns={'bucket': 'timestamp'}, inplace=True)
        candles = candles.merge(ob_agg, on='timestamp', how='left')
    
    return candles

def compute_indicators(candles):
    """Compute all candidate indicators using only PRIOR bars."""
    c = candles.copy()
    
    # Basic derived columns
    c['total_volume'] = c['buy_volume'] + c['sell_volume']
    c['total_count'] = c['buy_count'] + c['sell_count']
    c['net_volume'] = c['buy_volume'] - c['sell_volume']
    c['bar_return'] = c['close_vwap'].pct_change()
    
    # === ORDER FLOW INDICATORS (from prior bars) ===
    
    # Buy/sell volume ratio (use prior bar)
    c['flow_ratio'] = (c['buy_volume'] / (c['sell_volume'] + 1e-10)).shift(1)
    
    # Buy/sell count ratio
    c['count_ratio'] = (c['buy_count'] / (c['sell_count'] + 1e-10)).shift(1)
    
    # Net flow normalized
    c['net_flow_norm'] = (c['net_volume'] / (c['total_volume'] + 1e-10)).shift(1)
    
    # Flow ratio rolling averages
    for n in [3, 6, 12]:
        c[f'flow_ratio_{n}'] = c['flow_ratio'].rolling(n).mean()
        c[f'net_flow_norm_{n}'] = c['net_flow_norm'].rolling(n).mean()
    
    # Flow acceleration (change in flow ratio)
    c['flow_accel'] = c['flow_ratio'].diff().shift(1)
    
    # Buy volume acceleration
    c['buy_vol_accel'] = c['buy_volume'].diff().shift(1)
    
    # === VOLUME INDICATORS ===
    
    # Volume surge relative to recent average
    for n in [6, 12, 24, 60]:
        avg = c['total_volume'].shift(1).rolling(n).mean()
        c[f'vol_surge_{n}'] = (c['total_volume'].shift(1)) / (avg + 1e-10)
    
    # Volume dry-up (inverse of surge)
    c['vol_dryup'] = c['total_volume'].shift(1).rolling(6).mean() / (c['total_volume'].shift(1).rolling(24).mean() + 1e-10)
    
    # Buy volume as % of total
    c['buy_pct'] = (c['buy_volume'] / (c['total_volume'] + 1e-10)).shift(1)
    c['buy_pct_6'] = c['buy_pct'].rolling(6).mean()
    c['buy_pct_12'] = c['buy_pct'].rolling(12).mean()
    
    # === PRICE ACTION INDICATORS ===
    
    # Momentum (N-bar return) using prior bars only
    for n in [3, 6, 12, 24, 60]:
        c[f'momentum_{n}'] = (c['close_vwap'].shift(1) / c['close_vwap'].shift(n+1) - 1)
    
    # Consecutive green/red bars
    green = (c['bar_return'] > 0).shift(1)
    c['consec_green'] = green.groupby((green != green.shift()).cumsum()).cumcount()
    red = (c['bar_return'] < 0).shift(1)
    c['consec_red'] = red.groupby((red != red.shift()).cumsum()).cumcount()
    
    # Volatility (rolling std of returns)
    for n in [6, 12, 24]:
        c[f'volatility_{n}'] = c['bar_return'].shift(1).rolling(n).std()
    
    # Volatility expansion ratio
    c['vol_expand'] = c['volatility_6'] / (c['volatility_24'] + 1e-10)
    
    # VWAP deviation from rolling mean
    for n in [12, 24, 60]:
        mean_price = c['close_vwap'].shift(1).rolling(n).mean()
        std_price = c['close_vwap'].shift(1).rolling(n).std()
        c[f'vwap_zscore_{n}'] = (c['close_vwap'].shift(1) - mean_price) / (std_price + 1e-10)
    
    # === ORDERBOOK INDICATORS ===
    if 'avg_bid_size' in c.columns:
        # Bid/ask size imbalance
        c['ob_imbalance'] = ((c['avg_bid_size'] - c['avg_ask_size']) / 
                             (c['avg_bid_size'] + c['avg_ask_size'] + 1e-10)).shift(1)
        c['ob_imbalance_6'] = c['ob_imbalance'].rolling(6).mean()
        c['ob_imbalance_12'] = c['ob_imbalance'].rolling(12).mean()
        
        # Spread change
        c['spread_change'] = c['avg_spread_pct'].diff().shift(1)
        c['spread_ma6'] = c['avg_spread_pct'].shift(1).rolling(6).mean()
        
        # OB pressure change
        c['ob_pressure_change'] = c['ob_imbalance'].diff()
    
    # === CROSS-TIMEFRAME ===
    # 5s trend (already have)
    # 30s trend (6-bar)
    c['trend_30s'] = np.sign(c['momentum_6'])
    # 60s trend (12-bar) 
    c['trend_60s'] = np.sign(c['momentum_12'])
    # 300s trend (60-bar)
    c['trend_300s'] = np.sign(c['momentum_60'])
    
    # Trend alignment (all same direction)
    c['trend_align'] = (c['trend_30s'] + c['trend_60s'] + c['trend_300s']) / 3
    
    # === MEAN REVERSION ===
    # Oversold bounce: big drop + volume spike
    c['oversold_signal'] = (c['momentum_6'] < c['momentum_6'].rolling(60).quantile(0.1).shift(1)) & \
                           (c[f'vol_surge_12'] > 1.5)
    c['overbought_signal'] = (c['momentum_6'] > c['momentum_6'].rolling(60).quantile(0.9).shift(1)) & \
                              (c[f'vol_surge_12'] > 1.5)
    
    # RSI-like (6 bar)
    gains = c['bar_return'].shift(1).clip(lower=0).rolling(6).mean()
    losses = (-c['bar_return'].shift(1).clip(upper=0)).rolling(6).mean()
    c['rsi_6'] = 100 - (100 / (1 + gains / (losses + 1e-10)))
    
    gains12 = c['bar_return'].shift(1).clip(lower=0).rolling(12).mean()
    losses12 = (-c['bar_return'].shift(1).clip(upper=0)).rolling(12).mean()
    c['rsi_12'] = 100 - (100 / (1 + gains12 / (losses12 + 1e-10)))
    
    return c

def compute_forward_returns(candles, horizons=[3, 6, 12, 24, 60]):
    """Compute forward returns at each horizon (in bars = 5s each).
    Horizons: 3=15s, 6=30s, 12=60s, 24=120s, 60=300s"""
    c = candles.copy()
    for h in horizons:
        c[f'fwd_{h}'] = c['close_vwap'].shift(-h) / c['close_vwap'] - 1
    return c

def analyze_indicator(df, indicator_col, horizons=[3, 6, 12, 24, 60], n_buckets=5, product='ALL'):
    """Analyze a single indicator by bucketing and computing forward returns."""
    results = []
    
    valid = df[[indicator_col] + [f'fwd_{h}' for h in horizons]].dropna()
    if len(valid) < 100:
        return results
    
    # Handle boolean columns
    if valid[indicator_col].dtype == bool:
        for val in [True, False]:
            mask = valid[indicator_col] == val
            if mask.sum() < 20:
                continue
            for h in horizons:
                fwd = valid.loc[mask, f'fwd_{h}'].dropna()
                if len(fwd) < 20:
                    continue
                hold_sec = h * 5
                wr = (fwd > 0).mean()
                avg_ret = fwd.mean()
                net_ret = avg_ret - RT_FEE
                # Also track SHORT win rate (for fade signals)
                wr_short = (fwd < 0).mean()
                avg_ret_short = -fwd.mean()
                
                results.append({
                    'indicator': indicator_col,
                    'bucket': f'{val}',
                    'direction': 'LONG' if avg_ret > 0 else 'SHORT',
                    'hold_bars': h,
                    'hold_sec': hold_sec,
                    'wr_long': wr,
                    'wr_short': wr_short,
                    'avg_gross_ret': avg_ret,
                    'avg_net_ret': net_ret,
                    'best_dir_net': max(avg_ret - RT_FEE, -avg_ret - RT_FEE),
                    'best_dir': 'LONG' if avg_ret > 0 else 'SHORT',
                    'sample_count': len(fwd),
                    'product': product,
                })
        return results
    
    # Numeric: use quintile buckets
    try:
        buckets = pd.qcut(valid[indicator_col], n_buckets, labels=False, duplicates='drop')
    except:
        return results
    
    bucket_edges = {}
    for b in sorted(buckets.dropna().unique()):
        vals = valid.loc[buckets == b, indicator_col]
        bucket_edges[b] = (vals.min(), vals.max())
    
    for b in sorted(buckets.dropna().unique()):
        mask = buckets == b
        if mask.sum() < 20:
            continue
        
        for h in horizons:
            fwd = valid.loc[mask, f'fwd_{h}'].dropna()
            if len(fwd) < 20:
                continue
            
            hold_sec = h * 5
            wr = (fwd > 0).mean()
            avg_ret = fwd.mean()
            net_ret = avg_ret - RT_FEE
            wr_short = (fwd < 0).mean()
            
            lo, hi = bucket_edges[b]
            
            results.append({
                'indicator': indicator_col,
                'bucket': f'Q{b}[{lo:.4g},{hi:.4g}]',
                'direction': 'LONG' if avg_ret > 0 else 'SHORT',
                'hold_bars': h,
                'hold_sec': hold_sec,
                'wr_long': wr,
                'wr_short': wr_short,
                'avg_gross_ret': avg_ret,
                'avg_net_ret': net_ret,
                'best_dir_net': max(avg_ret - RT_FEE, -avg_ret - RT_FEE),
                'best_dir': 'LONG' if avg_ret > 0 else 'SHORT',
                'sample_count': len(fwd),
                'product': product,
            })
    
    return results


def compute_base_rates(all_candles_dict, horizons=[3, 6, 12, 24, 60]):
    """Compute base rates for all products combined and individually."""
    base_rates = {}
    
    # Combined
    all_fwd = {h: [] for h in horizons}
    for product, candles in all_candles_dict.items():
        for h in horizons:
            col = f'fwd_{h}'
            if col in candles.columns:
                vals = candles[col].dropna().values
                all_fwd[h].extend(vals)
    
    for h in horizons:
        arr = np.array(all_fwd[h])
        if len(arr) > 0:
            hold_sec = h * 5
            base_rates[f'ALL_{hold_sec}s'] = {
                'wr_long': (arr > 0).mean(),
                'wr_short': (arr < 0).mean(),
                'avg_ret': arr.mean(),
                'std_ret': arr.std(),
                'sample': len(arr),
            }
    
    # Per-product
    for product, candles in all_candles_dict.items():
        for h in horizons:
            col = f'fwd_{h}'
            if col in candles.columns:
                arr = candles[col].dropna().values
                if len(arr) > 100:
                    hold_sec = h * 5
                    base_rates[f'{product}_{hold_sec}s'] = {
                        'wr_long': (arr > 0).mean(),
                        'wr_short': (arr < 0).mean(),
                        'avg_ret': arr.mean(),
                        'std_ret': arr.std(),
                        'sample': len(arr),
                    }
    
    return base_rates


def main():
    print("=" * 60)
    print("AUGUR SIGNAL DISCOVERY - EXHAUSTIVE SEARCH")
    print("=" * 60)
    
    conn = sqlite3.connect(DB_PATH)
    
    # Step 1: Get products with enough data
    products = get_products(conn)
    print(f"\nProducts with >= {MIN_ROWS} rows: {len(products)}")
    for p, cnt in products[:15]:
        print(f"  {p:15s} {cnt:>8,} rows")
    
    # Focus on top products for initial sweep
    # Include top 30 products by data volume
    top_products = [p for p, _ in products[:30]]
    
    # Step 2: Build 5s candles for each product
    print("\n--- Building 5-second candles ---")
    all_candles = {}
    
    for product in top_products:
        t0 = time.time()
        tf_df = load_trade_flow(conn, product)
        ob_df = load_orderbook(conn, product)
        candles = build_5s_candles(tf_df, ob_df)
        
        if len(candles) < 200:
            print(f"  {product}: only {len(candles)} candles, skipping")
            continue
        
        candles = compute_indicators(candles)
        candles = compute_forward_returns(candles)
        all_candles[product] = candles
        dt = time.time() - t0
        print(f"  {product}: {len(candles):,} candles ({dt:.1f}s)")
    
    # Step 3: Compute base rates
    print("\n--- Computing base rates ---")
    base_rates = compute_base_rates(all_candles)
    for key in sorted(base_rates.keys()):
        if key.startswith('ALL_'):
            br = base_rates[key]
            print(f"  {key}: WR_long={br['wr_long']:.3f} WR_short={br['wr_short']:.3f} "
                  f"avg_ret={br['avg_ret']*100:.4f}% std={br['std_ret']*100:.4f}% n={br['sample']:,}")
    
    # Step 4: Test all indicators
    print("\n--- Testing all indicators ---")
    
    # Define indicators to test
    indicators = [
        # Order flow
        'flow_ratio', 'count_ratio', 'net_flow_norm',
        'flow_ratio_3', 'flow_ratio_6', 'flow_ratio_12',
        'net_flow_norm_3', 'net_flow_norm_6', 'net_flow_norm_12',
        'flow_accel', 'buy_vol_accel',
        # Volume
        'vol_surge_6', 'vol_surge_12', 'vol_surge_24', 'vol_surge_60',
        'vol_dryup',
        'buy_pct', 'buy_pct_6', 'buy_pct_12',
        # Price action
        'momentum_3', 'momentum_6', 'momentum_12', 'momentum_24', 'momentum_60',
        'consec_green', 'consec_red',
        'volatility_6', 'volatility_12', 'volatility_24',
        'vol_expand',
        'vwap_zscore_12', 'vwap_zscore_24', 'vwap_zscore_60',
        # Orderbook
        'ob_imbalance', 'ob_imbalance_6', 'ob_imbalance_12',
        'spread_change', 'spread_ma6',
        'ob_pressure_change',
        # Cross-timeframe
        'trend_align',
        # Mean reversion
        'oversold_signal', 'overbought_signal',
        'rsi_6', 'rsi_12',
    ]
    
    all_results = []
    
    for product, candles in all_candles.items():
        sys.stdout.write(f"\r  Testing {product}...          ")
        sys.stdout.flush()
        
        for ind in indicators:
            if ind not in candles.columns:
                continue
            results = analyze_indicator(candles, ind, product=product)
            all_results.extend(results)
    
    print(f"\n  Total signal tests: {len(all_results):,}")
    
    # Step 5: Find the best signals
    print("\n--- Ranking signals ---")
    
    if not all_results:
        print("NO RESULTS! Something went wrong.")
        conn.close()
        return
    
    results_df = pd.DataFrame(all_results)
    
    # Best signals by net return (considering best direction)
    # For LONG: net_ret = avg_gross_ret - 0.002
    # For SHORT: net_ret = -avg_gross_ret - 0.002
    # Already computed as best_dir_net
    
    # Filter for minimum sample size
    results_df = results_df[results_df['sample_count'] >= 50]
    
    # Sort by best_dir_net
    top_signals = results_df.nlargest(100, 'best_dir_net')
    
    print(f"\nTop 20 single signals:")
    for i, row in top_signals.head(20).iterrows():
        wr = row['wr_long'] if row['best_dir'] == 'LONG' else row['wr_short']
        print(f"  {row['indicator']:25s} {row['bucket']:25s} {row['best_dir']:5s} "
              f"{row['hold_sec']:3.0f}s WR={wr:.1%} net={row['best_dir_net']*100:.3f}% "
              f"n={row['sample_count']:,} [{row['product']}]")
    
    # Step 6: Try combinations on the best indicators
    print("\n--- Testing combinations ---")
    
    # Get top indicator/bucket combos per product
    combo_results = []
    
    # For each product, find its best indicators and combine them
    for product, candles in all_candles.items():
        # Get top 5 signals for this product
        prod_signals = results_df[results_df['product'] == product].nlargest(10, 'best_dir_net')
        if len(prod_signals) < 2:
            continue
        
        # Try pairwise combinations of top indicators
        top_inds = prod_signals[['indicator', 'bucket', 'best_dir', 'hold_bars']].values
        
        for i in range(min(5, len(top_inds))):
            for j in range(i+1, min(5, len(top_inds))):
                ind1, buck1, dir1, h1 = top_inds[i]
                ind2, buck2, dir2, h2 = top_inds[j]
                
                if ind1 not in candles.columns or ind2 not in candles.columns:
                    continue
                if ind1 == ind2:
                    continue
                
                # Use same hold period
                h = int(h1)
                fwd_col = f'fwd_{h}'
                if fwd_col not in candles.columns:
                    continue
                
                # Create combined mask
                valid = candles[[ind1, ind2, fwd_col]].dropna()
                if len(valid) < 100:
                    continue
                
                # Parse bucket ranges for each indicator
                # For boolean: just check True/False
                # For numeric: use quintile matching
                try:
                    if buck1 in ('True', 'False'):
                        q1_mask = valid[ind1] == (buck1 == 'True')
                    else:
                        # Parse Q{n}[lo,hi]
                        parts = buck1.split('[')
                        lo, hi = parts[1].rstrip(']').split(',')
                        q1_mask = (valid[ind1] >= float(lo)) & (valid[ind1] <= float(hi))
                    
                    if buck2 in ('True', 'False'):
                        q2_mask = valid[ind2] == (buck2 == 'True')
                    else:
                        parts = buck2.split('[')
                        lo, hi = parts[1].rstrip(']').split(',')
                        q2_mask = (valid[ind2] >= float(lo)) & (valid[ind2] <= float(hi))
                    
                    combined_mask = q1_mask & q2_mask
                    n_combined = combined_mask.sum()
                    
                    if n_combined < 30:
                        continue
                    
                    fwd = valid.loc[combined_mask, fwd_col]
                    avg_ret = fwd.mean()
                    wr_long = (fwd > 0).mean()
                    wr_short = (fwd < 0).mean()
                    best_net = max(avg_ret - RT_FEE, -avg_ret - RT_FEE)
                    best_dir = 'LONG' if avg_ret > 0 else 'SHORT'
                    
                    combo_results.append({
                        'combo': f'{ind1}={buck1} + {ind2}={buck2}',
                        'direction': best_dir,
                        'hold_sec': h * 5,
                        'wr': wr_long if best_dir == 'LONG' else wr_short,
                        'avg_gross_ret': avg_ret if best_dir == 'LONG' else -avg_ret,
                        'avg_net_ret': best_net,
                        'sample_count': n_combined,
                        'product': product,
                    })
                except Exception as e:
                    continue
    
    if combo_results:
        combo_df = pd.DataFrame(combo_results)
        combo_df = combo_df[combo_df['sample_count'] >= 30]
        top_combos = combo_df.nlargest(30, 'avg_net_ret')
        
        print(f"\nTop 10 combo signals:")
        for i, row in top_combos.head(10).iterrows():
            print(f"  {row['combo'][:60]:60s} {row['direction']:5s} "
                  f"{row['hold_sec']:3.0f}s WR={row['wr']:.1%} net={row['avg_net_ret']*100:.3f}% "
                  f"n={row['sample_count']:,} [{row['product']}]")
    
    # Step 7: Write report
    print("\n--- Writing report ---")
    write_report(base_rates, results_df, top_signals, 
                 combo_df if combo_results else pd.DataFrame(), 
                 all_candles)
    
    conn.close()
    print(f"\nDone! Report at {OUTPUT_PATH}")


def write_report(base_rates, results_df, top_signals, combo_df, all_candles):
    """Write the final report."""
    
    lines = []
    lines.append("# AUGUR Signal Discovery - Exhaustive Search Results")
    lines.append(f"\nGenerated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append(f"\nDatabase: enhanced_data.db")
    lines.append(f"Round-trip fee: 0.20% (VIP2 taker 0.10% each way)")
    lines.append(f"Win = gross return > 0.20% at exit")
    lines.append(f"All indicators computed from PRIOR bars only (no lookahead)")
    
    # Base rates
    lines.append("\n## 1. Base Rates (Random Entry)")
    lines.append("\n### Combined (All Products)")
    lines.append("| Hold Time | WR Long | WR Short | Avg Return | Std Dev | Samples |")
    lines.append("|-----------|---------|----------|------------|---------|---------|")
    for key in sorted(base_rates.keys()):
        if key.startswith('ALL_'):
            br = base_rates[key]
            hold = key.replace('ALL_', '')
            lines.append(f"| {hold} | {br['wr_long']:.3f} | {br['wr_short']:.3f} | "
                        f"{br['avg_ret']*100:.4f}% | {br['std_ret']*100:.4f}% | {br['sample']:,} |")
    
    # Per-product base rates for top products
    lines.append("\n### Per-Product Base Rates (60s hold)")
    lines.append("| Product | WR Long | Avg Return | Samples |")
    lines.append("|---------|---------|------------|---------|")
    for key in sorted(base_rates.keys()):
        if key.endswith('_60s') and not key.startswith('ALL_'):
            br = base_rates[key]
            prod = key.replace('_60s', '')
            lines.append(f"| {prod} | {br['wr_long']:.3f} | {br['avg_ret']*100:.4f}% | {br['sample']:,} |")
    
    # Top 20 single indicators
    lines.append("\n## 2. Top 20 Single-Indicator Signals")
    lines.append("\nRanked by net return after 0.20% RT fees.")
    lines.append("\n| Rank | Product | Indicator | Bucket | Dir | Hold | WR | Gross Ret | Net Ret | Samples |")
    lines.append("|------|---------|-----------|--------|-----|------|----|-----------|---------|---------|")
    
    for rank, (i, row) in enumerate(top_signals.head(20).iterrows(), 1):
        wr = row['wr_long'] if row['best_dir'] == 'LONG' else row['wr_short']
        gross = row['avg_gross_ret'] if row['best_dir'] == 'LONG' else -row['avg_gross_ret']
        lines.append(f"| {rank} | {row['product']} | {row['indicator']} | {row['bucket']} | "
                     f"{row['best_dir']} | {row['hold_sec']:.0f}s | {wr:.1%} | "
                     f"{gross*100:.3f}% | {row['best_dir_net']*100:.3f}% | {row['sample_count']:,} |")
    
    # Top signals grouped by indicator type
    lines.append("\n## 3. Best Signal Per Indicator Type")
    lines.append("\nShowing the single best configuration for each indicator across all products.")
    
    for indicator in results_df['indicator'].unique():
        ind_results = results_df[results_df['indicator'] == indicator]
        if len(ind_results) == 0:
            continue
        best = ind_results.nlargest(1, 'best_dir_net').iloc[0]
        if best['best_dir_net'] > 0:
            wr = best['wr_long'] if best['best_dir'] == 'LONG' else best['wr_short']
            gross = best['avg_gross_ret'] if best['best_dir'] == 'LONG' else -best['avg_gross_ret']
            lines.append(f"\n**{indicator}**: {best['product']} | {best['bucket']} | "
                        f"{best['best_dir']} {best['hold_sec']:.0f}s | "
                        f"WR={wr:.1%} | gross={gross*100:.3f}% | net={best['best_dir_net']*100:.3f}% | n={best['sample_count']:,}")
    
    # Combination signals
    if len(combo_df) > 0:
        lines.append("\n## 4. Top 10 Combination Signals")
        lines.append("\n| Rank | Product | Combination | Dir | Hold | WR | Gross Ret | Net Ret | Samples |")
        lines.append("|------|---------|-------------|-----|------|----|-----------|---------|---------|")
        
        top_combos = combo_df.nlargest(10, 'avg_net_ret')
        for rank, (i, row) in enumerate(top_combos.iterrows(), 1):
            lines.append(f"| {rank} | {row['product']} | {row['combo'][:50]} | "
                        f"{row['direction']} | {row['hold_sec']:.0f}s | {row['wr']:.1%} | "
                        f"{row['avg_gross_ret']*100:.3f}% | {row['avg_net_ret']*100:.3f}% | {row['sample_count']:,} |")
    
    # Signal formulas
    lines.append("\n## 5. Exact Signal Formulas")
    lines.append("""
### Indicator Definitions (all use PRIOR 5s bars only):

**Order Flow:**
- `flow_ratio` = buy_volume / sell_volume (prior bar)
- `count_ratio` = buy_count / sell_count (prior bar)
- `net_flow_norm` = (buy_vol - sell_vol) / (buy_vol + sell_vol) (prior bar)
- `flow_ratio_N` = N-bar rolling mean of flow_ratio
- `flow_accel` = diff(flow_ratio), shifted 1 bar
- `buy_vol_accel` = diff(buy_volume), shifted 1 bar

**Volume:**
- `vol_surge_N` = prior_bar_volume / N-bar_rolling_avg_volume
- `vol_dryup` = 6-bar_avg_vol / 24-bar_avg_vol
- `buy_pct` = buy_volume / total_volume (prior bar)
- `buy_pct_N` = N-bar rolling mean of buy_pct

**Price Action:**
- `momentum_N` = close[-1] / close[-N-1] - 1 (prior bars)
- `consec_green/red` = count of consecutive up/down bars (prior)
- `volatility_N` = rolling std of returns over N bars (prior)
- `vol_expand` = volatility_6 / volatility_24
- `vwap_zscore_N` = (close[-1] - mean_N) / std_N

**Orderbook:**
- `ob_imbalance` = (bid_size - ask_size) / (bid_size + ask_size) (prior bar)
- `ob_imbalance_N` = N-bar rolling mean of ob_imbalance
- `spread_change` = diff(avg_spread_pct), shifted 1 bar
- `ob_pressure_change` = diff(ob_imbalance)

**Cross-Timeframe:**
- `trend_align` = mean(sign(momentum_6), sign(momentum_12), sign(momentum_60))

**Mean Reversion:**
- `oversold_signal` = momentum_6 < 10th percentile(60-bar) AND vol_surge_12 > 1.5
- `overbought_signal` = momentum_6 > 90th percentile(60-bar) AND vol_surge_12 > 1.5
- `rsi_N` = 100 - 100/(1 + avg_gains_N / avg_losses_N)
""")
    
    # Products analysis
    lines.append("\n## 6. Products Where Signals Work Best")
    lines.append("\nTop 5 products by best achievable net return:")
    
    profitable = results_df[results_df['best_dir_net'] > 0]
    if len(profitable) > 0:
        by_product = profitable.groupby('product')['best_dir_net'].max().sort_values(ascending=False)
        for prod in by_product.head(10).index:
            prod_best = profitable[profitable['product'] == prod].nlargest(3, 'best_dir_net')
            lines.append(f"\n### {prod}")
            for _, row in prod_best.iterrows():
                wr = row['wr_long'] if row['best_dir'] == 'LONG' else row['wr_short']
                lines.append(f"- {row['indicator']} {row['bucket']} → {row['best_dir']} {row['hold_sec']:.0f}s: "
                            f"WR={wr:.1%}, net={row['best_dir_net']*100:.3f}%, n={row['sample_count']:,}")
    
    # Summary
    lines.append("\n## 7. Summary & Recommendations")
    
    n_profitable = len(results_df[results_df['best_dir_net'] > 0])
    n_total = len(results_df)
    lines.append(f"\n- Total signal configurations tested: {n_total:,}")
    lines.append(f"- Configurations profitable after fees: {n_profitable:,} ({n_profitable/max(1,n_total)*100:.1f}%)")
    
    if n_profitable > 0:
        best = results_df.nlargest(1, 'best_dir_net').iloc[0]
        wr = best['wr_long'] if best['best_dir'] == 'LONG' else best['wr_short']
        lines.append(f"- Best single signal: {best['indicator']} on {best['product']} → "
                     f"net {best['best_dir_net']*100:.3f}%, WR={wr:.1%}, n={best['sample_count']:,}")
    
    with open(OUTPUT_PATH, 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"Report written: {len(lines)} lines")


if __name__ == '__main__':
    main()
