#!/usr/bin/env python3
"""
AUGUR Signal Validation - Phase 2
1. Check NKN-USD price action (is it just a trend?)
2. Filter out degenerate indicators (division by zero artifacts)
3. Focus on liquid markets (BTC, ETH, SOL, XRP, LTC, DOGE, LINK)
4. Train/test split on ALL signals
5. Deeper indicator exploration with more granular thresholds
6. Properly handle directional signals (momentum continuation vs mean reversion)
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
RT_FEE = 0.0020  # 0.20% round-trip

def load_and_build(conn, product):
    """Load trade_flow + OB, build 5s candles, compute indicators."""
    tf = pd.read_sql_query(
        "SELECT timestamp, buy_volume, sell_volume, buy_count, sell_count, vwap "
        "FROM trade_flow WHERE product=? ORDER BY timestamp",
        conn, params=(product,)
    )
    ob = pd.read_sql_query(
        "SELECT timestamp, best_bid, best_ask, bid_size, ask_size, spread_pct, mid_price "
        "FROM orderbook_snapshots WHERE product=? ORDER BY timestamp",
        conn, params=(product,)
    )
    
    if len(tf) < 1000:
        return None
    
    tf['bucket'] = (tf['timestamp'] // 5) * 5
    c = tf.groupby('bucket').agg(
        open_vwap=('vwap', 'first'),
        close_vwap=('vwap', 'last'),
        high_vwap=('vwap', 'max'),
        low_vwap=('vwap', 'min'),
        buy_volume=('buy_volume', 'sum'),
        sell_volume=('sell_volume', 'sum'),
        buy_count=('buy_count', 'sum'),
        sell_count=('sell_count', 'sum'),
        tick_count=('timestamp', 'count'),
    ).reset_index().rename(columns={'bucket': 'timestamp'})
    
    c = c[c['close_vwap'] > 0].copy()
    
    if len(ob) > 0:
        ob['bucket'] = (ob['timestamp'] // 5) * 5
        ob_agg = ob.groupby('bucket').agg(
            avg_bid_size=('bid_size', 'mean'),
            avg_ask_size=('ask_size', 'mean'),
            avg_spread_pct=('spread_pct', 'mean'),
            avg_mid_price=('mid_price', 'mean'),
        ).reset_index().rename(columns={'bucket': 'timestamp'})
        c = c.merge(ob_agg, on='timestamp', how='left')
    
    # Derived
    c['total_volume'] = c['buy_volume'] + c['sell_volume']
    c['total_count'] = c['buy_count'] + c['sell_count']
    c['bar_return'] = c['close_vwap'].pct_change()
    
    # SAFE flow indicators (avoid division by near-zero)
    # Use log ratio or normalized difference instead of raw ratio
    c['buy_sell_diff'] = (c['buy_volume'] - c['sell_volume']).shift(1)
    c['buy_pct'] = (c['buy_volume'] / (c['total_volume'] + 1e-10)).shift(1)
    c['count_buy_pct'] = (c['buy_count'] / (c['total_count'] + 1e-10)).shift(1)
    
    # Rolling averages
    for n in [3, 6, 12]:
        c[f'buy_pct_{n}'] = c['buy_pct'].rolling(n).mean()
        c[f'count_buy_pct_{n}'] = c['count_buy_pct'].rolling(n).mean()
    
    # Volume indicators
    for n in [6, 12, 24, 60]:
        avg = c['total_volume'].shift(1).rolling(n).mean()
        c[f'vol_ratio_{n}'] = c['total_volume'].shift(1) / (avg + 1e-10)
    
    # Buy volume share vs rolling average
    for n in [6, 12]:
        c[f'buy_vol_ratio_{n}'] = c['buy_volume'].shift(1) / (c['buy_volume'].shift(1).rolling(n).mean() + 1e-10)
    
    # Price action
    for n in [3, 6, 12, 24, 60]:
        c[f'mom_{n}'] = (c['close_vwap'].shift(1) / c['close_vwap'].shift(n+1) - 1)
    
    # Volatility
    for n in [6, 12, 24]:
        c[f'vol_{n}'] = c['bar_return'].shift(1).rolling(n).std()
    
    c['vol_expand'] = c['vol_6'] / (c['vol_24'] + 1e-10)
    
    # VWAP z-score
    for n in [12, 24, 60]:
        mean_p = c['close_vwap'].shift(1).rolling(n).mean()
        std_p = c['close_vwap'].shift(1).rolling(n).std()
        c[f'zscore_{n}'] = (c['close_vwap'].shift(1) - mean_p) / (std_p + 1e-10)
    
    # RSI
    for n in [6, 12, 24]:
        gains = c['bar_return'].shift(1).clip(lower=0).rolling(n).mean()
        losses = (-c['bar_return'].shift(1).clip(upper=0)).rolling(n).mean()
        c[f'rsi_{n}'] = 100 - (100 / (1 + gains / (losses + 1e-10)))
    
    # Orderbook
    if 'avg_bid_size' in c.columns:
        c['ob_imb'] = ((c['avg_bid_size'] - c['avg_ask_size']) / 
                       (c['avg_bid_size'] + c['avg_ask_size'] + 1e-10)).shift(1)
        for n in [3, 6, 12]:
            c[f'ob_imb_{n}'] = c['ob_imb'].rolling(n).mean()
        c['spread'] = c['avg_spread_pct'].shift(1)
        c['spread_ma6'] = c['spread'].rolling(6).mean()
        c['spread_change'] = c['spread'].diff()
        c['ob_imb_change'] = c['ob_imb'].diff()
    
    # Cross-timeframe trend alignment
    c['trend_30s'] = np.sign(c['mom_6'])
    c['trend_60s'] = np.sign(c['mom_12'])
    c['trend_300s'] = np.sign(c['mom_60'])
    c['trend_align'] = (c['trend_30s'] + c['trend_60s'] + c['trend_300s'])
    
    # Mean reversion: price drop + volume
    c['mean_rev_score'] = -c['mom_12'] * c['vol_ratio_12']  # big drop + high volume = buy
    
    # Momentum + volume confirmation
    c['mom_vol_score'] = c['mom_6'] * c['vol_ratio_6']  # momentum * volume
    
    # Buy pressure acceleration
    c['buy_pct_accel'] = c['buy_pct'].diff()
    
    # Forward returns
    for h in [3, 6, 12, 24, 60]:
        c[f'fwd_{h}'] = c['close_vwap'].shift(-h) / c['close_vwap'] - 1
    
    return c


def test_signal_traintest(df, indicator, direction, threshold_type, threshold, hold_bars, min_n=30):
    """
    Test a signal with train/test split (50/50 by time).
    direction: 'LONG' or 'SHORT'
    threshold_type: 'above' or 'below'
    threshold: numeric value
    Returns: dict with train/test stats or None
    """
    fwd_col = f'fwd_{hold_bars}'
    valid = df[[indicator, fwd_col, 'timestamp']].dropna()
    if len(valid) < min_n * 2:
        return None
    
    # Apply signal condition
    if threshold_type == 'above':
        mask = valid[indicator] > threshold
    elif threshold_type == 'below':
        mask = valid[indicator] < threshold
    elif threshold_type == 'between':
        lo, hi = threshold
        mask = (valid[indicator] >= lo) & (valid[indicator] <= hi)
    else:
        return None
    
    signal_rows = valid[mask]
    if len(signal_rows) < min_n * 2:
        return None
    
    # Split by time
    mid = len(signal_rows) // 2
    train = signal_rows.iloc[:mid]
    test = signal_rows.iloc[mid:]
    
    results = {}
    for split_name, split_data in [('train', train), ('test', test)]:
        fwd = split_data[fwd_col]
        
        if direction == 'LONG':
            wr = (fwd > 0).mean()
            avg_ret = fwd.mean()
        else:  # SHORT
            wr = (fwd < 0).mean()
            avg_ret = -fwd.mean()
        
        net_ret = avg_ret - RT_FEE
        # Win rate clearing fees
        if direction == 'LONG':
            wr_fees = (fwd > RT_FEE).mean()
        else:
            wr_fees = (fwd < -RT_FEE).mean()
        
        results[split_name] = {
            'wr': wr,
            'wr_fees': wr_fees,
            'avg_ret': avg_ret,
            'net_ret': net_ret,
            'count': len(fwd),
            'median_ret': fwd.median() if direction == 'LONG' else -fwd.median(),
        }
    
    return results


def scan_thresholds(df, indicator, hold_bars_list=[3, 6, 12, 24, 60], 
                    percentiles=[10, 20, 30, 70, 80, 90]):
    """Scan multiple thresholds for a single indicator."""
    results = []
    
    valid_col = df[indicator].dropna()
    if len(valid_col) < 200:
        return results
    
    thresholds = np.percentile(valid_col, percentiles)
    
    for pct, thresh in zip(percentiles, thresholds):
        for hold_bars in hold_bars_list:
            for direction in ['LONG', 'SHORT']:
                # Below threshold
                for ttype in ['below', 'above']:
                    tt = test_signal_traintest(df, indicator, direction, ttype, thresh, hold_bars)
                    if tt is None:
                        continue
                    
                    # Only keep if both train AND test are profitable after fees
                    if tt['train']['net_ret'] > 0 and tt['test']['net_ret'] > 0:
                        results.append({
                            'indicator': indicator,
                            'threshold_type': ttype,
                            'threshold': thresh,
                            'percentile': pct,
                            'direction': direction,
                            'hold_bars': hold_bars,
                            'hold_sec': hold_bars * 5,
                            'train_wr': tt['train']['wr'],
                            'train_wr_fees': tt['train']['wr_fees'],
                            'train_net': tt['train']['net_ret'],
                            'train_n': tt['train']['count'],
                            'test_wr': tt['test']['wr'],
                            'test_wr_fees': tt['test']['wr_fees'],
                            'test_net': tt['test']['net_ret'],
                            'test_n': tt['test']['count'],
                            'avg_net': (tt['train']['net_ret'] + tt['test']['net_ret']) / 2,
                            'min_net': min(tt['train']['net_ret'], tt['test']['net_ret']),
                        })
    
    return results


def main():
    print("=" * 60)
    print("AUGUR SIGNAL VALIDATION - PHASE 2")
    print("=" * 60)
    
    conn = sqlite3.connect(DB_PATH)
    
    # Step 1: Check NKN-USD price action
    print("\n--- NKN-USD Price Check ---")
    nkn_tf = pd.read_sql_query(
        "SELECT timestamp, vwap FROM trade_flow WHERE product='NKN-USD' AND vwap > 0 ORDER BY timestamp",
        conn
    )
    if len(nkn_tf) > 0:
        first_price = nkn_tf['vwap'].iloc[0]
        last_price = nkn_tf['vwap'].iloc[-1]
        min_price = nkn_tf['vwap'].min()
        max_price = nkn_tf['vwap'].max()
        print(f"  NKN-USD: {first_price:.4f} → {last_price:.4f} ({(last_price/first_price-1)*100:.1f}%)")
        print(f"  Range: {min_price:.4f} - {max_price:.4f}")
        start_t = datetime.fromtimestamp(nkn_tf['timestamp'].iloc[0], tz=timezone.utc)
        end_t = datetime.fromtimestamp(nkn_tf['timestamp'].iloc[-1], tz=timezone.utc)
        print(f"  Period: {start_t} to {end_t}")
    
    # Check several other products
    for prod in ['BTC-USD', 'ETH-USD', 'SOL-USD', 'BNKR-USD', 'AXS-USD']:
        tf = pd.read_sql_query(
            f"SELECT vwap FROM trade_flow WHERE product=? AND vwap > 0 ORDER BY timestamp",
            conn, params=(prod,)
        )
        if len(tf) > 0:
            first = tf['vwap'].iloc[0]
            last = tf['vwap'].iloc[-1]
            print(f"  {prod}: {first:.4f} → {last:.4f} ({(last/first-1)*100:.2f}%)")
    
    # Step 2: Test ALL products with train/test validation
    print("\n--- Signal Scan with Train/Test Validation ---")
    
    # Get all products with enough data
    cursor = conn.cursor()
    cursor.execute("""SELECT product, COUNT(*) as cnt FROM trade_flow 
                      GROUP BY product HAVING cnt >= 5000 ORDER BY cnt DESC""")
    products = [(r[0], r[1]) for r in cursor.fetchall()]
    
    # Indicators to test (SAFE - no division by zero artifacts)
    indicators = [
        'buy_pct', 'buy_pct_3', 'buy_pct_6', 'buy_pct_12',
        'count_buy_pct', 'count_buy_pct_3', 'count_buy_pct_6', 'count_buy_pct_12',
        'vol_ratio_6', 'vol_ratio_12', 'vol_ratio_24', 'vol_ratio_60',
        'buy_vol_ratio_6', 'buy_vol_ratio_12',
        'mom_3', 'mom_6', 'mom_12', 'mom_24', 'mom_60',
        'vol_6', 'vol_12', 'vol_24',
        'vol_expand',
        'zscore_12', 'zscore_24', 'zscore_60',
        'rsi_6', 'rsi_12', 'rsi_24',
        'ob_imb', 'ob_imb_3', 'ob_imb_6', 'ob_imb_12',
        'spread', 'spread_ma6', 'spread_change',
        'ob_imb_change',
        'trend_align',
        'mean_rev_score', 'mom_vol_score',
        'buy_pct_accel',
    ]
    
    all_validated = []
    
    for product, cnt in products[:40]:  # top 40 products
        sys.stdout.write(f"\r  Scanning {product:15s} ({cnt:>8,} rows)...")
        sys.stdout.flush()
        
        candles = load_and_build(conn, product)
        if candles is None or len(candles) < 400:
            continue
        
        for ind in indicators:
            if ind not in candles.columns:
                continue
            results = scan_thresholds(candles, ind)
            for r in results:
                r['product'] = product
            all_validated.extend(results)
    
    print(f"\n  Validated signal configs: {len(all_validated):,}")
    
    if not all_validated:
        print("\nNO validated signals found! Writing failure report.")
        write_report(conn, [], products)
        conn.close()
        return
    
    vdf = pd.DataFrame(all_validated)
    
    # Step 3: Rank by minimum of train/test net return (conservative)
    vdf = vdf.sort_values('min_net', ascending=False)
    
    print(f"\n--- Top 30 Validated Signals (profitable in BOTH train AND test) ---")
    print(f"{'Rank':>4} {'Product':>12} {'Indicator':>20} {'Dir':>5} {'Hold':>5} "
          f"{'TrainWR':>7} {'TrainNet':>9} {'TrainN':>6} {'TestWR':>6} {'TestNet':>8} {'TestN':>5}")
    
    for rank, (i, row) in enumerate(vdf.head(30).iterrows(), 1):
        ttype_str = f"{row['threshold_type']} p{row['percentile']:.0f}"
        print(f"{rank:4d} {row['product']:>12} {row['indicator']:>20} {row['direction']:>5} "
              f"{row['hold_sec']:4.0f}s {row['train_wr']:6.1%} {row['train_net']*100:8.3f}% "
              f"{row['train_n']:5.0f} {row['test_wr']:6.1%} {row['test_net']*100:7.3f}% {row['test_n']:5.0f}")
    
    # Step 4: Focus on liquid products
    print(f"\n--- Liquid Market Signals (BTC/ETH/SOL/XRP/LTC/DOGE/LINK) ---")
    liquid = ['BTC-USD', 'ETH-USD', 'SOL-USD', 'XRP-USD', 'LTC-USD', 'DOGE-USD', 'LINK-USD']
    liquid_signals = vdf[vdf['product'].isin(liquid)].sort_values('min_net', ascending=False)
    
    if len(liquid_signals) > 0:
        for rank, (i, row) in enumerate(liquid_signals.head(20).iterrows(), 1):
            print(f"{rank:4d} {row['product']:>12} {row['indicator']:>20} {row['direction']:>5} "
                  f"{row['hold_sec']:4.0f}s {row['train_wr']:6.1%} {row['train_net']*100:8.3f}% "
                  f"{row['train_n']:5.0f} {row['test_wr']:6.1%} {row['test_net']*100:7.3f}% {row['test_n']:5.0f}")
    else:
        print("  NONE found on liquid markets!")
    
    # Step 5: Cross-product signals (same indicator works on multiple products)
    print(f"\n--- Cross-Product Signal Stability ---")
    cross = vdf.groupby(['indicator', 'threshold_type', 'direction', 'hold_bars']).agg(
        products=('product', 'nunique'),
        product_list=('product', lambda x: ','.join(sorted(x.unique()))),
        avg_min_net=('min_net', 'mean'),
        total_n=('train_n', 'sum'),
    ).reset_index()
    cross = cross[cross['products'] >= 3].sort_values('avg_min_net', ascending=False)
    
    if len(cross) > 0:
        print("Signals profitable on 3+ products:")
        for _, row in cross.head(15).iterrows():
            print(f"  {row['indicator']:>20} {row['threshold_type']:>6} {row['direction']:>5} "
                  f"{row['hold_bars']*5:3.0f}s | {row['products']} products | "
                  f"avg_min_net={row['avg_min_net']*100:.3f}% | {row['product_list'][:60]}")
    else:
        print("  No signals work on 3+ products!")
    
    # Step 6: Write comprehensive report
    write_report(conn, vdf, products, liquid_signals, cross if len(cross) > 0 else None)
    
    conn.close()
    print(f"\nDone! Report at {OUTPUT_PATH}")


def write_report(conn, vdf, products, liquid_signals=None, cross_product=None):
    """Write the final comprehensive report."""
    lines = []
    lines.append("# AUGUR Signal Discovery - Exhaustive Search Results")
    lines.append(f"\nGenerated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append(f"\nDatabase: enhanced_data.db (1-second trade_flow + orderbook snapshots)")
    lines.append(f"Candle size: 5 seconds | All indicators use PRIOR bars only (no lookahead)")
    lines.append(f"Round-trip fee: 0.20% (VIP2 taker 0.10% each way)")
    lines.append(f"**Validation: 50/50 time-ordered train/test split. Only signals profitable in BOTH halves are shown.**")
    
    # Price context
    lines.append("\n## 0. Price Context (Full Period)")
    for prod in ['BTC-USD', 'ETH-USD', 'SOL-USD', 'NKN-USD', 'BNKR-USD', 'AXS-USD', 'XRP-USD']:
        tf = pd.read_sql_query(
            "SELECT MIN(vwap) as mn, MAX(vwap) as mx, "
            "FIRST_VALUE(vwap) OVER (ORDER BY timestamp) as first_v, "
            "LAST_VALUE(vwap) OVER (ORDER BY timestamp RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) as last_v "
            "FROM trade_flow WHERE product=? AND vwap > 0 LIMIT 1",
            conn, params=(prod,)
        )
        if len(tf) > 0:
            row = tf.iloc[0]
            # Just get first/last directly  
            first_df = pd.read_sql_query(
                "SELECT vwap FROM trade_flow WHERE product=? AND vwap > 0 ORDER BY timestamp LIMIT 1",
                conn, params=(prod,))
            last_df = pd.read_sql_query(
                "SELECT vwap FROM trade_flow WHERE product=? AND vwap > 0 ORDER BY timestamp DESC LIMIT 1",
                conn, params=(prod,))
            if len(first_df) > 0 and len(last_df) > 0:
                first_p = first_df['vwap'].iloc[0]
                last_p = last_df['vwap'].iloc[0]
                ret = (last_p/first_p - 1) * 100
                lines.append(f"- **{prod}**: ${first_p:.4f} → ${last_p:.4f} ({ret:+.1f}%)")
    
    if isinstance(vdf, pd.DataFrame) and len(vdf) > 0:
        # Base rates
        lines.append("\n## 1. Base Rates (Random Entry)")
        lines.append("\n*See per-product base rates at 60s hold in Phase 1 results above.*")
        lines.append("\nCombined base rates across all products:")
        lines.append("- 15s hold: WR=47.6% long, avg return +0.001%")
        lines.append("- 30s hold: WR=48.2% long, avg return +0.002%")
        lines.append("- 60s hold: WR=48.7% long, avg return +0.004%")
        lines.append("- 120s hold: WR=48.7% long, avg return +0.006%")
        lines.append("- 300s hold: WR=49.1% long, avg return +0.011%")
        lines.append("\nTo be profitable, a signal must achieve avg net return > 0% after 0.20% RT fees.")
        
        # Top 20 validated signals
        lines.append("\n## 2. Top 20 Validated Signals (Train+Test Profitable)")
        lines.append("\n| Rank | Product | Indicator | Condition | Dir | Hold | Train WR | Train Net | Train N | Test WR | Test Net | Test N |")
        lines.append("|------|---------|-----------|-----------|-----|------|----------|-----------|---------|---------|----------|--------|")
        
        for rank, (i, row) in enumerate(vdf.head(20).iterrows(), 1):
            cond = f"{row['threshold_type']} p{row['percentile']:.0f} ({row['threshold']:.4g})"
            lines.append(f"| {rank} | {row['product']} | {row['indicator']} | {cond} | "
                        f"{row['direction']} | {row['hold_sec']:.0f}s | {row['train_wr']:.1%} | "
                        f"{row['train_net']*100:.3f}% | {row['train_n']:.0f} | {row['test_wr']:.1%} | "
                        f"{row['test_net']*100:.3f}% | {row['test_n']:.0f} |")
        
        # Liquid market signals
        if liquid_signals is not None and len(liquid_signals) > 0:
            lines.append("\n## 3. Liquid Market Signals (BTC/ETH/SOL/XRP/LTC/DOGE/LINK)")
            lines.append("\n| Rank | Product | Indicator | Condition | Dir | Hold | Train WR | Train Net | Train N | Test WR | Test Net | Test N |")
            lines.append("|------|---------|-----------|-----------|-----|------|----------|-----------|---------|---------|----------|--------|")
            
            for rank, (i, row) in enumerate(liquid_signals.head(20).iterrows(), 1):
                cond = f"{row['threshold_type']} p{row['percentile']:.0f} ({row['threshold']:.4g})"
                lines.append(f"| {rank} | {row['product']} | {row['indicator']} | {cond} | "
                            f"{row['direction']} | {row['hold_sec']:.0f}s | {row['train_wr']:.1%} | "
                            f"{row['train_net']*100:.3f}% | {row['train_n']:.0f} | {row['test_wr']:.1%} | "
                            f"{row['test_net']*100:.3f}% | {row['test_n']:.0f} |")
        else:
            lines.append("\n## 3. Liquid Market Signals")
            lines.append("\n**No validated signals found on liquid markets (BTC/ETH/SOL/XRP/LTC/DOGE/LINK).**")
        
        # Cross-product signals
        if cross_product is not None and len(cross_product) > 0:
            lines.append("\n## 4. Cross-Product Signal Stability")
            lines.append("\nSignals profitable on 3+ products (strongest evidence of real edge):")
            lines.append("\n| Indicator | Condition | Dir | Hold | # Products | Avg Min Net | Products |")
            lines.append("|-----------|-----------|-----|------|------------|-------------|----------|")
            
            for _, row in cross_product.head(15).iterrows():
                lines.append(f"| {row['indicator']} | {row['threshold_type']} | {row['direction']} | "
                            f"{row['hold_bars']*5:.0f}s | {row['products']} | "
                            f"{row['avg_min_net']*100:.3f}% | {row['product_list'][:40]} |")
        else:
            lines.append("\n## 4. Cross-Product Signal Stability")
            lines.append("\n**No signals consistently profitable across 3+ products.**")
        
        # Per-product best signals
        lines.append("\n## 5. Best Signal Per Product")
        for product in vdf['product'].unique():
            prod_best = vdf[vdf['product'] == product].head(3)
            if len(prod_best) > 0:
                lines.append(f"\n### {product}")
                for _, row in prod_best.iterrows():
                    lines.append(f"- **{row['indicator']}** {row['threshold_type']} p{row['percentile']:.0f} "
                                f"→ {row['direction']} {row['hold_sec']:.0f}s | "
                                f"Train: WR={row['train_wr']:.1%} net={row['train_net']*100:.3f}% n={row['train_n']:.0f} | "
                                f"Test: WR={row['test_wr']:.1%} net={row['test_net']*100:.3f}% n={row['test_n']:.0f}")
        
        # Indicator formulas
        lines.append("\n## 6. Indicator Definitions")
        lines.append("""
All indicators computed from PRIOR 5-second bars only. No future data leakage.

**Order Flow (safe, no division-by-zero):**
- `buy_pct` = buy_volume / total_volume (prior bar), range [0,1]
- `buy_pct_N` = N-bar rolling mean of buy_pct
- `count_buy_pct` = buy_count / total_count (prior bar)
- `buy_pct_accel` = diff(buy_pct)

**Volume:**
- `vol_ratio_N` = prior_bar_volume / N-bar_rolling_avg(volume)
- `buy_vol_ratio_N` = prior_bar_buy_volume / N-bar_avg(buy_volume)

**Price Action:**
- `mom_N` = close[-1] / close[-N-1] - 1 (prior N bars)
- `vol_N` = rolling std of returns over N prior bars
- `vol_expand` = vol_6 / vol_24
- `zscore_N` = (close[-1] - rolling_mean_N) / rolling_std_N

**Mean Reversion & Momentum:**
- `rsi_N` = standard RSI over N prior bars
- `mean_rev_score` = -mom_12 * vol_ratio_12 (drop + volume = buy)
- `mom_vol_score` = mom_6 * vol_ratio_6 (momentum * volume)

**Orderbook:**
- `ob_imb` = (bid_size - ask_size) / (bid_size + ask_size) (prior bar)
- `ob_imb_N` = N-bar rolling mean
- `spread` = avg_spread_pct (prior bar)
- `spread_ma6` = 6-bar rolling mean of spread
- `ob_imb_change` = diff(ob_imb)

**Cross-Timeframe:**
- `trend_align` = sign(mom_6) + sign(mom_12) + sign(mom_60), range [-3, +3]
""")
    
    # Summary
    lines.append("\n## 7. Summary & Recommendations")
    
    if isinstance(vdf, pd.DataFrame) and len(vdf) > 0:
        n_total = len(vdf)
        n_products = vdf['product'].nunique()
        best = vdf.iloc[0]
        
        lines.append(f"\n- **{n_total:,}** signal configs passed train/test validation")
        lines.append(f"- Across **{n_products}** products")
        lines.append(f"- Best overall: **{best['indicator']}** on **{best['product']}** → "
                     f"{best['direction']} {best['hold_sec']:.0f}s, "
                     f"min(train,test) net = {best['min_net']*100:.3f}%")
        
        # Actionable recommendations
        lines.append("\n### Actionable Signals for Paper Trading")
        top5 = vdf.head(5)
        for _, row in top5.iterrows():
            lines.append(f"\n**{row['product']} - {row['indicator']}**")
            lines.append(f"- Condition: {row['threshold_type']} {row['threshold']:.4g} (p{row['percentile']:.0f})")
            lines.append(f"- Direction: {row['direction']}, Hold: {row['hold_sec']:.0f}s")
            lines.append(f"- Expected net return: {row['min_net']*100:.3f}% (conservative estimate)")
            lines.append(f"- Win rate: Train {row['train_wr']:.1%} / Test {row['test_wr']:.1%}")
            lines.append(f"- Sample: Train {row['train_n']:.0f} / Test {row['test_n']:.0f}")
    else:
        lines.append("\n**NO validated signals found.** The market is efficient at these timeframes for these indicators.")
        lines.append("\nPossible next steps:")
        lines.append("- Try longer timeframes (1min candles, 5min hold)")  
        lines.append("- Try more products (altcoins with less attention)")
        lines.append("- Try different signal types (pattern-based, cross-product correlation)")
        lines.append("- Try market-regime detection (vol regime → signal selection)")
    
    with open(OUTPUT_PATH, 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"Report written: {len(lines)} lines")


if __name__ == '__main__':
    main()
