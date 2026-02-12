#!/usr/bin/env python3
"""
AUGUR Leading Indicator Analysis
Systematically tests microstructure indicators against forward price movement.
"""
import sqlite3
import time
import numpy as np
from collections import defaultdict
import json

DB_PATH = '/home/bonsaihorn/Projects/augur-collector/enhanced_data.db'
OUTPUT_PATH = '/home/bonsaihorn/.openclaw/workspace/analysis/augur-leading-indicators.md'

def get_db():
    db = sqlite3.connect(DB_PATH)
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA cache_size=-200000")
    return db

def load_orderbook_timeseries(db, product, hours=24):
    """Load orderbook data as numpy arrays for fast computation."""
    t_start = time.time() - hours * 3600
    cur = db.execute("""
        SELECT timestamp, mid_price, bid_size, ask_size, spread_pct, best_bid, best_ask
        FROM orderbook_snapshots
        WHERE product=? AND timestamp > ?
        ORDER BY timestamp
    """, (product, t_start))
    rows = cur.fetchall()
    if not rows:
        return None
    
    data = {
        'timestamp': np.array([r[0] for r in rows], dtype=np.float64),
        'mid_price': np.array([r[1] for r in rows], dtype=np.float64),
        'bid_size': np.array([r[2] for r in rows], dtype=np.float64),
        'ask_size': np.array([r[3] for r in rows], dtype=np.float64),
        'spread_pct': np.array([r[4] for r in rows], dtype=np.float64),
        'best_bid': np.array([r[5] for r in rows], dtype=np.float64),
        'best_ask': np.array([r[6] for r in rows], dtype=np.float64),
    }
    print(f"  Loaded {len(rows)} orderbook snapshots for {product}")
    return data

def load_trade_flow_timeseries(db, product, hours=24):
    """Load trade flow data."""
    t_start = time.time() - hours * 3600
    cur = db.execute("""
        SELECT timestamp, buy_volume, sell_volume, buy_count, sell_count, vwap
        FROM trade_flow
        WHERE product=? AND timestamp > ?
        ORDER BY timestamp
    """, (product, t_start))
    rows = cur.fetchall()
    if not rows:
        return None
    
    data = {
        'timestamp': np.array([r[0] for r in rows], dtype=np.float64),
        'buy_volume': np.array([r[1] for r in rows], dtype=np.float64),
        'sell_volume': np.array([r[2] for r in rows], dtype=np.float64),
        'buy_count': np.array([r[3] for r in rows], dtype=np.float64),
        'sell_count': np.array([r[4] for r in rows], dtype=np.float64),
        'vwap': np.array([r[5] for r in rows], dtype=np.float64),
    }
    print(f"  Loaded {len(rows)} trade flow records for {product}")
    return data

def load_large_trades(db, product, hours=24, min_usd=10000):
    """Load individual large trades."""
    t_start = time.time() - hours * 3600
    cur = db.execute("""
        SELECT timestamp, price, size, side, price * size as usd_value
        FROM trades
        WHERE product=? AND timestamp > ? AND price * size > ?
        ORDER BY timestamp
    """, (product, t_start, min_usd))
    rows = cur.fetchall()
    print(f"  Found {len(rows)} large trades (>${min_usd}) for {product}")
    return rows

def forward_returns(timestamps, prices, lookahead_seconds):
    """For each timestamp, find the price at t + lookahead and compute return.
    Uses binary search for efficiency."""
    n = len(timestamps)
    returns = np.full(n, np.nan)
    
    j = 0
    for i in range(n):
        target_t = timestamps[i] + lookahead_seconds
        # Advance j to find closest timestamp >= target
        while j < n and timestamps[j] < target_t:
            j += 1
        if j < n and (timestamps[j] - target_t) < 5:  # within 5 seconds
            returns[i] = (prices[j] - prices[i]) / prices[i] * 100  # percentage
        # Don't reset j - timestamps are sorted so next i needs j >= current j
        # Actually we need to allow j to stay where it is or advance
        # Reset j to i for correctness (timestamps may have gaps)
    
    # Redo with proper approach - use searchsorted
    target_times = timestamps + lookahead_seconds
    indices = np.searchsorted(timestamps, target_times, side='left')
    
    for i in range(n):
        idx = indices[i]
        if idx < n and abs(timestamps[idx] - target_times[i]) < 5:
            returns[i] = (prices[idx] - prices[i]) / prices[i] * 100
        elif idx > 0 and idx - 1 < n and abs(timestamps[idx-1] - target_times[i]) < 5:
            returns[i] = (prices[idx-1] - prices[i]) / prices[i] * 100
    
    return returns

def analyze_indicator(indicator_values, forward_rets, thresholds, indicator_name, direction='long'):
    """
    For each threshold, calculate win rate and average return.
    direction='long': indicator > threshold predicts price UP
    direction='short': indicator > threshold predicts price DOWN  
    direction='both': test both sides
    """
    results = []
    valid = ~np.isnan(forward_rets) & ~np.isnan(indicator_values)
    
    for thresh in thresholds:
        if direction == 'long':
            mask = valid & (indicator_values > thresh)
            if mask.sum() < 20:
                continue
            rets = forward_rets[mask]
            wins = (rets > 0.2).sum()  # >0.2% gain
            win_rate = wins / len(rets) * 100
            avg_ret = rets.mean()
            med_ret = np.median(rets)
            results.append({
                'indicator': indicator_name,
                'threshold': f'> {thresh}',
                'direction': 'LONG',
                'sample_size': int(len(rets)),
                'win_rate_02': round(win_rate, 1),
                'avg_return': round(avg_ret, 4),
                'median_return': round(med_ret, 4),
                'max_return': round(rets.max(), 4),
                'min_return': round(rets.min(), 4),
            })
        elif direction == 'short':
            mask = valid & (indicator_values > thresh)
            if mask.sum() < 20:
                continue
            rets = forward_rets[mask]
            wins = (rets < -0.2).sum()  # >0.2% drop (short wins)
            win_rate = wins / len(rets) * 100
            avg_ret = -rets.mean()  # invert for short
            med_ret = -np.median(rets)
            results.append({
                'indicator': indicator_name,
                'threshold': f'> {thresh}',
                'direction': 'SHORT',
                'sample_size': int(len(rets)),
                'win_rate_02': round(win_rate, 1),
                'avg_return': round(avg_ret, 4),
                'median_return': round(med_ret, 4),
                'max_return': round(-rets.min(), 4),
                'min_return': round(-rets.max(), 4),
            })
        elif direction == 'both':
            # Test long side
            mask_long = valid & (indicator_values > thresh)
            if mask_long.sum() >= 20:
                rets = forward_rets[mask_long]
                wins = (rets > 0.2).sum()
                results.append({
                    'indicator': indicator_name,
                    'threshold': f'> {thresh}',
                    'direction': 'LONG',
                    'sample_size': int(len(rets)),
                    'win_rate_02': round(wins / len(rets) * 100, 1),
                    'avg_return': round(rets.mean(), 4),
                    'median_return': round(np.median(rets), 4),
                })
            # Test short side
            mask_short = valid & (indicator_values < -thresh)
            if mask_short.sum() >= 20:
                rets = forward_rets[mask_short]
                wins = (rets < -0.2).sum()
                results.append({
                    'indicator': indicator_name,
                    'threshold': f'< -{thresh}',
                    'direction': 'SHORT',
                    'sample_size': int(len(rets)),
                    'win_rate_02': round(wins / len(rets) * 100, 1),
                    'avg_return': round(-rets.mean(), 4),
                    'median_return': round(-np.median(rets), 4),
                })
    
    return results

def run_analysis(product):
    """Run all analyses for a product."""
    print(f"\n{'='*60}")
    print(f"ANALYZING {product}")
    print(f"{'='*60}")
    
    db = get_db()
    
    # Load data
    print("\nLoading data...")
    ob = load_orderbook_timeseries(db, product)
    flow = load_trade_flow_timeseries(db, product)
    
    if ob is None:
        print(f"No orderbook data for {product}")
        return {}
    
    all_results = []
    
    # Precompute forward returns at different lookaheads
    print("\nComputing forward returns...")
    lookaheads = {
        '1min': 60,
        '2min': 120,
        '5min': 300,
        '10min': 600,
    }
    fwd_returns = {}
    for label, secs in lookaheads.items():
        fwd_returns[label] = forward_returns(ob['timestamp'], ob['mid_price'], secs)
        valid = ~np.isnan(fwd_returns[label])
        print(f"  {label}: {valid.sum()} valid samples, avg={fwd_returns[label][valid].mean():.5f}%")
    
    # ==========================================================
    # 1. ORDER BOOK IMBALANCE
    # ==========================================================
    print("\n--- 1. Order Book Imbalance ---")
    
    # Raw imbalance ratio: bid_size / ask_size
    imbalance_ratio = ob['bid_size'] / np.maximum(ob['ask_size'], 1e-10)
    # Log imbalance (more normally distributed)
    log_imbalance = np.log(imbalance_ratio)
    # Normalized imbalance: (bid - ask) / (bid + ask)
    norm_imbalance = (ob['bid_size'] - ob['ask_size']) / (ob['bid_size'] + ob['ask_size'])
    
    print(f"  Imbalance ratio stats: mean={np.nanmean(imbalance_ratio):.2f}, "
          f"median={np.nanmedian(imbalance_ratio):.2f}, "
          f"p95={np.nanpercentile(imbalance_ratio, 95):.2f}")
    
    for la_label, la_secs in lookaheads.items():
        fr = fwd_returns[la_label]
        
        # Test ratio thresholds for LONG (bid >> ask → expect price up)
        for thresh in [1.5, 2.0, 3.0, 5.0, 8.0, 10.0]:
            results = analyze_indicator(
                imbalance_ratio, fr, [thresh],
                f'OB_Imbalance_Ratio_{la_label}', direction='long'
            )
            all_results.extend(results)
        
        # Test ratio thresholds for SHORT (ask >> bid → expect price down)
        inv_ratio = ob['ask_size'] / np.maximum(ob['bid_size'], 1e-10)
        for thresh in [1.5, 2.0, 3.0, 5.0, 8.0, 10.0]:
            results = analyze_indicator(
                inv_ratio, fr, [thresh],
                f'OB_InvImbalance_Ratio_{la_label}', direction='short'
            )
            all_results.extend(results)
        
        # Test normalized imbalance
        results = analyze_indicator(
            norm_imbalance, fr, [0.2, 0.3, 0.5, 0.7],
            f'OB_NormImbalance_{la_label}', direction='both'
        )
        all_results.extend(results)
    
    # Rolling average imbalance (smoothed signal)
    print("  Computing rolling imbalance (30s, 60s windows)...")
    for window in [30, 60]:
        # Simple rolling mean using cumsum trick
        cumsum = np.cumsum(np.insert(norm_imbalance, 0, 0))
        rolling_imb = (cumsum[window:] - cumsum[:-window]) / window
        # Pad front with NaN
        padded = np.full(len(norm_imbalance), np.nan)
        padded[window-1:] = rolling_imb[:len(padded)-window+1]
        
        for la_label, la_secs in lookaheads.items():
            fr = fwd_returns[la_label]
            results = analyze_indicator(
                padded, fr, [0.2, 0.3, 0.5, 0.7],
                f'OB_RollingImb_{window}s_{la_label}', direction='both'
            )
            all_results.extend(results)
    
    # ==========================================================
    # 2. TRADE FLOW MOMENTUM
    # ==========================================================
    print("\n--- 2. Trade Flow Momentum ---")
    
    if flow is not None:
        # Align flow data to orderbook timestamps using nearest-neighbor
        flow_buy_ratio = flow['buy_volume'] / np.maximum(flow['sell_volume'], 1e-10)
        flow_net = flow['buy_volume'] - flow['sell_volume']
        flow_total = flow['buy_volume'] + flow['sell_volume']
        flow_norm = flow_net / np.maximum(flow_total, 1e-10)
        
        # Compute forward returns on flow timestamps
        # Need to map flow timestamps to orderbook prices
        flow_fwd = {}
        for la_label, la_secs in lookaheads.items():
            flow_fwd[la_label] = np.full(len(flow['timestamp']), np.nan)
            for i, ts in enumerate(flow['timestamp']):
                # Find price at ts
                idx_now = np.searchsorted(ob['timestamp'], ts)
                idx_future = np.searchsorted(ob['timestamp'], ts + la_secs)
                if idx_now < len(ob['timestamp']) and idx_future < len(ob['timestamp']):
                    if abs(ob['timestamp'][idx_now] - ts) < 3 and abs(ob['timestamp'][idx_future] - (ts + la_secs)) < 5:
                        p0 = ob['mid_price'][idx_now]
                        p1 = ob['mid_price'][idx_future]
                        flow_fwd[la_label][i] = (p1 - p0) / p0 * 100
        
        print(f"  Buy/sell ratio stats: mean={np.nanmean(flow_buy_ratio):.2f}, "
              f"median={np.nanmedian(flow_buy_ratio):.2f}, "
              f"p95={np.nanpercentile(flow_buy_ratio, 95):.2f}")
        
        for la_label in lookaheads:
            fr = flow_fwd[la_label]
            valid_count = (~np.isnan(fr)).sum()
            print(f"  {la_label}: {valid_count} valid flow samples")
            
            # Buy/sell volume ratio
            for thresh in [1.5, 2.0, 3.0, 5.0]:
                results = analyze_indicator(
                    flow_buy_ratio, fr, [thresh],
                    f'Flow_BuySellRatio_{la_label}', direction='long'
                )
                all_results.extend(results)
                
                # Inverse for short
                inv = flow['sell_volume'] / np.maximum(flow['buy_volume'], 1e-10)
                results = analyze_indicator(
                    inv, fr, [thresh],
                    f'Flow_SellBuyRatio_{la_label}', direction='short'
                )
                all_results.extend(results)
            
            # Normalized flow
            results = analyze_indicator(
                flow_norm, fr, [0.3, 0.5, 0.7, 0.9],
                f'Flow_NormNet_{la_label}', direction='both'
            )
            all_results.extend(results)
        
        # Rolling flow momentum (cumulative over N seconds)
        print("  Computing rolling flow momentum...")
        for window in [10, 30, 60]:
            if len(flow_net) > window:
                cumsum = np.cumsum(np.insert(flow_net, 0, 0))
                rolling = cumsum[window:] - cumsum[:-window]
                padded = np.full(len(flow_net), np.nan)
                padded[window-1:] = rolling[:len(padded)-window+1]
                
                # Normalize by rolling total volume
                cumsum_total = np.cumsum(np.insert(flow_total, 0, 0))
                rolling_total = cumsum_total[window:] - cumsum_total[:-window]
                padded_total = np.full(len(flow_total), np.nan)
                padded_total[window-1:] = rolling_total[:len(padded_total)-window+1]
                
                rolling_norm = padded / np.maximum(padded_total, 1e-10)
                
                for la_label in lookaheads:
                    fr = flow_fwd[la_label]
                    results = analyze_indicator(
                        rolling_norm, fr, [0.3, 0.5, 0.7],
                        f'Flow_RollingNet_{window}s_{la_label}', direction='both'
                    )
                    all_results.extend(results)
    
    # ==========================================================
    # 3. SPREAD ANALYSIS
    # ==========================================================
    print("\n--- 3. Spread Analysis ---")
    
    spread = ob['spread_pct']
    print(f"  Spread stats: mean={np.nanmean(spread):.5f}%, "
          f"median={np.nanmedian(spread):.5f}%, "
          f"p95={np.nanpercentile(spread, 95):.5f}%")
    
    # Spread z-score (relative to rolling average)
    for window in [60, 300]:
        cumsum = np.cumsum(np.insert(spread, 0, 0))
        rolling_mean = (cumsum[window:] - cumsum[:-window]) / window
        padded_mean = np.full(len(spread), np.nan)
        padded_mean[window-1:] = rolling_mean[:len(padded_mean)-window+1]
        
        cumsum_sq = np.cumsum(np.insert(spread**2, 0, 0))
        rolling_sq = (cumsum_sq[window:] - cumsum_sq[:-window]) / window
        padded_sq = np.full(len(spread), np.nan)
        padded_sq[window-1:] = rolling_sq[:len(padded_sq)-window+1]
        
        rolling_std = np.sqrt(np.maximum(padded_sq - padded_mean**2, 0))
        spread_zscore = (spread - padded_mean) / np.maximum(rolling_std, 1e-10)
        
        # Does spread expansion predict absolute volatility?
        for la_label in lookaheads:
            fr = fwd_returns[la_label]
            abs_fr = np.abs(fr)
            
            for thresh in [1.0, 2.0, 3.0]:
                mask = ~np.isnan(abs_fr) & ~np.isnan(spread_zscore) & (spread_zscore > thresh)
                if mask.sum() >= 20:
                    baseline_vol = np.nanmean(np.abs(fr[~np.isnan(fr)]))
                    signal_vol = np.nanmean(abs_fr[mask])
                    all_results.append({
                        'indicator': f'Spread_ZScore_{window}s_{la_label}',
                        'threshold': f'> {thresh}',
                        'direction': 'VOL_EXPANSION',
                        'sample_size': int(mask.sum()),
                        'win_rate_02': round(signal_vol / baseline_vol * 100 - 100, 1),  # % increase in vol
                        'avg_return': round(signal_vol, 4),
                        'median_return': round(np.nanmedian(abs_fr[mask]), 4),
                    })
        
        # Spread compression after expansion → directional?
        # After spread expands then contracts, use order book imbalance for direction
        spread_change = np.diff(spread_zscore)
        spread_change = np.insert(spread_change, 0, 0)
        
        # Spread was high, now dropping (compression)
        compressing = (spread_zscore > 1.0) & (spread_change < -0.5)
        for la_label in lookaheads:
            fr = fwd_returns[la_label]
            mask = ~np.isnan(fr) & compressing
            if mask.sum() >= 20:
                rets = fr[mask]
                # Use concurrent imbalance for direction
                imb_at_compression = norm_imbalance[mask]
                long_mask_sub = imb_at_compression > 0.2
                short_mask_sub = imb_at_compression < -0.2
                
                if long_mask_sub.sum() >= 10:
                    lr = rets[long_mask_sub]
                    all_results.append({
                        'indicator': f'SpreadCompress+BidImb_{window}s_{la_label}',
                        'threshold': 'compress + bid>ask',
                        'direction': 'LONG',
                        'sample_size': int(len(lr)),
                        'win_rate_02': round((lr > 0.2).sum() / len(lr) * 100, 1),
                        'avg_return': round(lr.mean(), 4),
                        'median_return': round(np.median(lr), 4),
                    })
                if short_mask_sub.sum() >= 10:
                    sr = rets[short_mask_sub]
                    all_results.append({
                        'indicator': f'SpreadCompress+AskImb_{window}s_{la_label}',
                        'threshold': 'compress + ask>bid',
                        'direction': 'SHORT',
                        'sample_size': int(len(sr)),
                        'win_rate_02': round((sr < -0.2).sum() / len(sr) * 100, 1),
                        'avg_return': round(-sr.mean(), 4),
                        'median_return': round(-np.median(sr), 4),
                    })
    
    # ==========================================================
    # 4. VOLUME SURGE DETECTION
    # ==========================================================
    print("\n--- 4. Volume Surge Detection ---")
    
    if flow is not None:
        total_vol = flow['buy_volume'] + flow['sell_volume']
        
        for window in [30, 60, 120]:
            if len(total_vol) > window:
                cumsum = np.cumsum(np.insert(total_vol, 0, 0))
                rolling_avg = (cumsum[window:] - cumsum[:-window]) / window
                padded_avg = np.full(len(total_vol), np.nan)
                padded_avg[window-1:] = rolling_avg[:len(padded_avg)-window+1]
                
                vol_ratio = total_vol / np.maximum(padded_avg, 1e-10)
                
                # Directional volume surge (buy or sell dominated)
                buy_surge = flow['buy_volume'] / np.maximum(padded_avg, 1e-10)
                sell_surge = flow['sell_volume'] / np.maximum(padded_avg, 1e-10)
                
                for la_label in lookaheads:
                    fr = flow_fwd[la_label]
                    
                    # Any volume surge → volatility
                    for thresh in [2.0, 3.0, 5.0]:
                        mask = ~np.isnan(fr) & ~np.isnan(vol_ratio) & (vol_ratio > thresh)
                        if mask.sum() >= 20:
                            abs_rets = np.abs(fr[mask])
                            baseline = np.nanmean(np.abs(fr[~np.isnan(fr)]))
                            all_results.append({
                                'indicator': f'VolSurge_{window}s_{la_label}',
                                'threshold': f'> {thresh}x',
                                'direction': 'VOL',
                                'sample_size': int(mask.sum()),
                                'win_rate_02': round(np.nanmean(abs_rets) / baseline * 100 - 100, 1),
                                'avg_return': round(np.nanmean(abs_rets), 4),
                                'median_return': round(np.nanmedian(abs_rets), 4),
                            })
                    
                    # Buy-dominated surge → LONG
                    for thresh in [2.0, 3.0, 5.0]:
                        # High buy volume AND buy > sell
                        mask = (~np.isnan(fr) & ~np.isnan(buy_surge) & 
                                (buy_surge > thresh) & (flow['buy_volume'] > flow['sell_volume'] * 1.5))
                        if mask.sum() >= 20:
                            rets = fr[mask]
                            all_results.append({
                                'indicator': f'BuySurge_{window}s_{la_label}',
                                'threshold': f'> {thresh}x + buy>1.5*sell',
                                'direction': 'LONG',
                                'sample_size': int(len(rets)),
                                'win_rate_02': round((rets > 0.2).sum() / len(rets) * 100, 1),
                                'avg_return': round(rets.mean(), 4),
                                'median_return': round(np.median(rets), 4),
                            })
                    
                    # Sell-dominated surge → SHORT
                    for thresh in [2.0, 3.0, 5.0]:
                        mask = (~np.isnan(fr) & ~np.isnan(sell_surge) & 
                                (sell_surge > thresh) & (flow['sell_volume'] > flow['buy_volume'] * 1.5))
                        if mask.sum() >= 20:
                            rets = fr[mask]
                            all_results.append({
                                'indicator': f'SellSurge_{window}s_{la_label}',
                                'threshold': f'> {thresh}x + sell>1.5*buy',
                                'direction': 'SHORT',
                                'sample_size': int(len(rets)),
                                'win_rate_02': round((rets < -0.2).sum() / len(rets) * 100, 1),
                                'avg_return': round(-rets.mean(), 4),
                                'median_return': round(-np.median(rets), 4),
                            })
    
    # ==========================================================
    # 5. MICRO-STRUCTURE PATTERNS
    # ==========================================================
    print("\n--- 5. Micro-structure Patterns ---")
    
    # 5a. Price momentum (recent price change predicts continuation or reversal)
    for lookback in [30, 60, 120, 300]:
        past_returns = np.full(len(ob['timestamp']), np.nan)
        target_times = ob['timestamp'] - lookback
        indices = np.searchsorted(ob['timestamp'], target_times, side='left')
        
        for i in range(len(ob['timestamp'])):
            idx = indices[i]
            if idx < len(ob['timestamp']) and abs(ob['timestamp'][idx] - target_times[i]) < 5:
                past_returns[i] = (ob['mid_price'][i] - ob['mid_price'][idx]) / ob['mid_price'][idx] * 100
        
        for la_label in lookaheads:
            fr = fwd_returns[la_label]
            # Momentum (continuation)
            for thresh in [0.1, 0.2, 0.3, 0.5]:
                # Up momentum → continues up?
                mask = ~np.isnan(fr) & ~np.isnan(past_returns) & (past_returns > thresh)
                if mask.sum() >= 20:
                    rets = fr[mask]
                    all_results.append({
                        'indicator': f'Momentum_{lookback}s_{la_label}',
                        'threshold': f'past_ret > {thresh}%',
                        'direction': 'LONG (continuation)',
                        'sample_size': int(len(rets)),
                        'win_rate_02': round((rets > 0.2).sum() / len(rets) * 100, 1),
                        'avg_return': round(rets.mean(), 4),
                        'median_return': round(np.median(rets), 4),
                    })
                # Down momentum → continues down?
                mask = ~np.isnan(fr) & ~np.isnan(past_returns) & (past_returns < -thresh)
                if mask.sum() >= 20:
                    rets = fr[mask]
                    all_results.append({
                        'indicator': f'Momentum_{lookback}s_{la_label}',
                        'threshold': f'past_ret < -{thresh}%',
                        'direction': 'SHORT (continuation)',
                        'sample_size': int(len(rets)),
                        'win_rate_02': round((rets < -0.2).sum() / len(rets) * 100, 1),
                        'avg_return': round(-rets.mean(), 4),
                        'median_return': round(-np.median(rets), 4),
                    })
                # Mean reversion: down → bounce?
                mask = ~np.isnan(fr) & ~np.isnan(past_returns) & (past_returns < -thresh)
                if mask.sum() >= 20:
                    rets = fr[mask]
                    all_results.append({
                        'indicator': f'MeanRevert_{lookback}s_{la_label}',
                        'threshold': f'past_ret < -{thresh}%',
                        'direction': 'LONG (reversal)',
                        'sample_size': int(len(rets)),
                        'win_rate_02': round((rets > 0.2).sum() / len(rets) * 100, 1),
                        'avg_return': round(rets.mean(), 4),
                        'median_return': round(np.median(rets), 4),
                    })
    
    # 5b. Composite: Imbalance + Flow + Momentum
    print("  Computing composite indicators...")
    if flow is not None:
        # Map flow to orderbook timestamps
        flow_interp = np.full(len(ob['timestamp']), np.nan)
        for i, ts in enumerate(ob['timestamp']):
            idx = np.searchsorted(flow['timestamp'], ts, side='right') - 1
            if 0 <= idx < len(flow['timestamp']) and abs(flow['timestamp'][idx] - ts) < 5:
                flow_interp[i] = flow_norm[idx] if idx < len(flow_norm) else np.nan
        
        # Composite: imbalance AND flow agree
        composite_bull = (norm_imbalance > 0.3) & (flow_interp > 0.3)
        composite_bear = (norm_imbalance < -0.3) & (flow_interp < -0.3)
        
        for la_label in lookaheads:
            fr = fwd_returns[la_label]
            
            mask = ~np.isnan(fr) & composite_bull
            if mask.sum() >= 20:
                rets = fr[mask]
                all_results.append({
                    'indicator': f'Composite_BullConfluence_{la_label}',
                    'threshold': 'imb>0.3 AND flow>0.3',
                    'direction': 'LONG',
                    'sample_size': int(len(rets)),
                    'win_rate_02': round((rets > 0.2).sum() / len(rets) * 100, 1),
                    'avg_return': round(rets.mean(), 4),
                    'median_return': round(np.median(rets), 4),
                })
            
            mask = ~np.isnan(fr) & composite_bear
            if mask.sum() >= 20:
                rets = fr[mask]
                all_results.append({
                    'indicator': f'Composite_BearConfluence_{la_label}',
                    'threshold': 'imb<-0.3 AND flow<-0.3',
                    'direction': 'SHORT',
                    'sample_size': int(len(rets)),
                    'win_rate_02': round((rets < -0.2).sum() / len(rets) * 100, 1),
                    'avg_return': round(-rets.mean(), 4),
                    'median_return': round(-np.median(rets), 4),
                })
    
    # ==========================================================
    # 6. BASELINE: Random timing
    # ==========================================================
    print("\n--- Baseline (random entry) ---")
    for la_label in lookaheads:
        fr = fwd_returns[la_label]
        valid = ~np.isnan(fr)
        rets = fr[valid]
        if len(rets) > 0:
            long_wr = (rets > 0.2).sum() / len(rets) * 100
            short_wr = (rets < -0.2).sum() / len(rets) * 100
            print(f"  {la_label}: N={len(rets)}, long_wr(>0.2%)={long_wr:.1f}%, "
                  f"short_wr(>0.2%)={short_wr:.1f}%, avg={rets.mean():.5f}%")
            all_results.append({
                'indicator': f'BASELINE_Random_{la_label}',
                'threshold': 'none',
                'direction': 'LONG',
                'sample_size': int(len(rets)),
                'win_rate_02': round(long_wr, 1),
                'avg_return': round(rets.mean(), 4),
                'median_return': round(np.median(rets), 4),
            })
    
    db.close()
    return all_results

def format_report(eth_results, btc_results):
    """Format results as markdown report."""
    
    # Find baseline
    eth_baselines = {r['indicator']: r for r in eth_results if 'BASELINE' in r['indicator']}
    btc_baselines = {r['indicator']: r for r in btc_results if 'BASELINE' in r['indicator']}
    
    # Filter to directional indicators (not VOL or BASELINE)
    eth_directional = [r for r in eth_results 
                       if r['direction'] in ('LONG', 'SHORT', 'LONG (continuation)', 'SHORT (continuation)', 'LONG (reversal)') 
                       and 'BASELINE' not in r['indicator']
                       and r['sample_size'] >= 50]
    
    # Sort by win rate
    eth_directional.sort(key=lambda r: r['win_rate_02'], reverse=True)
    
    # Find the matching baseline for each
    def get_baseline_wr(indicator):
        for la in ['1min', '2min', '5min', '10min']:
            if la in indicator:
                bl_key = f'BASELINE_Random_{la}'
                if bl_key in eth_baselines:
                    return eth_baselines[bl_key]['win_rate_02']
        return 0
    
    # Add edge over baseline
    for r in eth_directional:
        baseline = get_baseline_wr(r['indicator'])
        r['edge'] = round(r['win_rate_02'] - baseline, 1)
    
    # Top 20 by edge
    eth_by_edge = sorted(eth_directional, key=lambda r: r['edge'], reverse=True)[:20]
    
    # Volatility indicators
    eth_vol = [r for r in eth_results if r['direction'] in ('VOL', 'VOL_EXPANSION') and r['sample_size'] >= 50]
    eth_vol.sort(key=lambda r: r.get('win_rate_02', 0), reverse=True)
    
    # BTC validation
    btc_directional = [r for r in btc_results 
                       if r['direction'] in ('LONG', 'SHORT', 'LONG (continuation)', 'SHORT (continuation)', 'LONG (reversal)')
                       and 'BASELINE' not in r['indicator']
                       and r['sample_size'] >= 50]
    btc_by_name = {(r['indicator'], r['threshold'], r['direction']): r for r in btc_directional}
    
    lines = []
    lines.append("# AUGUR Leading Indicator Analysis")
    lines.append(f"*Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}*")
    lines.append(f"*Data: Last 24 hours of ETH-USD and BTC-USD from enhanced_data.db*")
    lines.append("")
    
    # Baselines
    lines.append("## Baseline (Random Entry)")
    lines.append("")
    lines.append("| Lookahead | N | Long WR (>0.2%) | Avg Return |")
    lines.append("|-----------|---|-----------------|------------|")
    for key, bl in sorted(eth_baselines.items()):
        la = key.split('_')[-1]
        lines.append(f"| {la} | {bl['sample_size']:,} | {bl['win_rate_02']}% | {bl['avg_return']:.4f}% |")
    lines.append("")
    lines.append("*Any indicator must beat these baselines to have real edge.*")
    lines.append("")
    
    # Top directional indicators
    lines.append("## Top 20 Directional Indicators (by Edge over Baseline)")
    lines.append("")
    lines.append("| # | Indicator | Threshold | Dir | N | WR% | Baseline% | Edge | Avg Ret% | Med Ret% |")
    lines.append("|---|-----------|-----------|-----|---|-----|-----------|------|----------|----------|")
    for i, r in enumerate(eth_by_edge, 1):
        bl = get_baseline_wr(r['indicator'])
        # Check BTC validation
        btc_key = (r['indicator'].replace('ETH', 'BTC'), r['threshold'], r['direction'])
        btc_match = btc_by_name.get((r['indicator'], r['threshold'], r['direction']))
        btc_note = ""
        if btc_match:
            btc_bl = 0
            for la in ['1min', '2min', '5min', '10min']:
                if la in r['indicator']:
                    bl_key = f'BASELINE_Random_{la}'
                    if bl_key in btc_baselines:
                        btc_bl = btc_baselines[bl_key]['win_rate_02']
            btc_edge = btc_match['win_rate_02'] - btc_bl
            btc_note = f" (BTC: {btc_match['win_rate_02']}%/{btc_edge:+.1f})"
        
        lines.append(f"| {i} | {r['indicator']} | {r['threshold']} | {r['direction']} | "
                     f"{r['sample_size']:,} | {r['win_rate_02']}% | {bl}% | "
                     f"**{r['edge']:+.1f}%** | {r['avg_return']:.4f}% | {r.get('median_return', 'N/A')}%{btc_note} |")
    lines.append("")
    
    # Top 10 by absolute win rate (with minimum edge)
    eth_good = [r for r in eth_directional if r['edge'] > 2.0 and r['sample_size'] >= 100]
    eth_good.sort(key=lambda r: r['win_rate_02'], reverse=True)
    
    lines.append("## Top Indicators with Real Edge (>2% over baseline, N≥100)")
    lines.append("")
    if eth_good:
        lines.append("| # | Indicator | Threshold | Dir | N | WR% | Edge | Avg Ret% |")
        lines.append("|---|-----------|-----------|-----|---|-----|------|----------|")
        for i, r in enumerate(eth_good[:15], 1):
            lines.append(f"| {i} | {r['indicator']} | {r['threshold']} | {r['direction']} | "
                        f"{r['sample_size']:,} | {r['win_rate_02']}% | **{r['edge']:+.1f}%** | {r['avg_return']:.4f}% |")
    else:
        lines.append("**No indicators found with >2% edge and N≥100. This is telling.**")
    lines.append("")
    
    # Volatility indicators
    lines.append("## Volatility Indicators (does spread/volume predict bigger moves?)")
    lines.append("")
    if eth_vol:
        lines.append("| Indicator | Threshold | N | Vol Increase% | Avg Abs Ret% | Med Abs Ret% |")
        lines.append("|-----------|-----------|---|---------------|--------------|--------------|")
        for r in eth_vol[:10]:
            lines.append(f"| {r['indicator']} | {r['threshold']} | {r['sample_size']:,} | "
                        f"{r['win_rate_02']:+.1f}% | {r['avg_return']:.4f}% | {r.get('median_return', 'N/A')}% |")
    lines.append("")
    
    # BTC validation summary
    lines.append("## BTC-USD Cross-Validation")
    lines.append("")
    lines.append("| Lookahead | N | Long WR (>0.2%) | Avg Return |")
    lines.append("|-----------|---|-----------------|------------|")
    for key, bl in sorted(btc_baselines.items()):
        la = key.split('_')[-1]
        lines.append(f"| {la} | {bl['sample_size']:,} | {bl['win_rate_02']}% | {bl['avg_return']:.4f}% |")
    lines.append("")
    
    # Cross-validate top ETH indicators on BTC
    lines.append("### ETH Top Indicators → BTC Performance")
    lines.append("")
    cross_validated = []
    for r in eth_by_edge[:10]:
        btc_match = btc_by_name.get((r['indicator'], r['threshold'], r['direction']))
        if btc_match:
            btc_bl = 0
            for la in ['1min', '2min', '5min', '10min']:
                if la in r['indicator']:
                    bl_key = f'BASELINE_Random_{la}'
                    if bl_key in btc_baselines:
                        btc_bl = btc_baselines[bl_key]['win_rate_02']
            btc_edge = btc_match['win_rate_02'] - btc_bl
            cross_validated.append({
                'indicator': r['indicator'],
                'threshold': r['threshold'],
                'direction': r['direction'],
                'eth_wr': r['win_rate_02'],
                'eth_edge': r['edge'],
                'btc_wr': btc_match['win_rate_02'],
                'btc_edge': round(btc_edge, 1),
                'eth_n': r['sample_size'],
                'btc_n': btc_match['sample_size'],
            })
    
    if cross_validated:
        lines.append("| Indicator | Dir | ETH WR/Edge | BTC WR/Edge | ETH N | BTC N | Consistent? |")
        lines.append("|-----------|-----|-------------|-------------|-------|-------|-------------|")
        for cv in cross_validated:
            consistent = "✅" if cv['btc_edge'] > 0 and cv['eth_edge'] > 0 else "❌"
            lines.append(f"| {cv['indicator']} | {cv['direction']} | "
                        f"{cv['eth_wr']}%/{cv['eth_edge']:+.1f} | "
                        f"{cv['btc_wr']}%/{cv['btc_edge']:+.1f} | "
                        f"{cv['eth_n']:,} | {cv['btc_n']:,} | {consistent} |")
    lines.append("")
    
    # Honest assessment
    lines.append("## Honest Assessment")
    lines.append("")
    
    # Calculate stats
    any_real_edge = any(r['edge'] > 5.0 and r['sample_size'] >= 200 for r in eth_directional)
    max_edge = max((r['edge'] for r in eth_directional), default=0)
    avg_edge_top10 = np.mean([r['edge'] for r in eth_by_edge[:10]]) if eth_by_edge else 0
    cross_consistent = sum(1 for cv in cross_validated if cv['btc_edge'] > 0 and cv['eth_edge'] > 0)
    
    if any_real_edge:
        lines.append("### 🟢 SIGNAL DETECTED")
        lines.append("")
        lines.append(f"- Maximum edge found: **{max_edge:+.1f}%** over baseline")
        lines.append(f"- Average edge of top 10: **{avg_edge_top10:+.1f}%**")
        lines.append(f"- Cross-validated on BTC: **{cross_consistent}/{len(cross_validated)}** consistent")
        lines.append("")
        lines.append("These results suggest there IS exploitable microstructure signal, but:")
        lines.append("- Edge is thin — needs high-frequency execution")
        lines.append("- Transaction costs (spread + fees) will eat most of the edge")
        lines.append("- Signal may decay as market conditions change")
    elif max_edge > 2.0:
        lines.append("### 🟡 WEAK SIGNAL")
        lines.append("")
        lines.append(f"- Maximum edge found: **{max_edge:+.1f}%** over baseline")
        lines.append(f"- Average edge of top 10: **{avg_edge_top10:+.1f}%**")
        lines.append(f"- Cross-validated on BTC: **{cross_consistent}/{len(cross_validated)}** consistent")
        lines.append("")
        lines.append("There are hints of signal but the edge is marginal. Key concerns:")
        lines.append("- Edge may not survive transaction costs")
        lines.append("- Small sample sizes reduce confidence")
        lines.append("- Results may be overfitted to this 24h window")
    else:
        lines.append("### 🔴 NO MEANINGFUL SIGNAL")
        lines.append("")
        lines.append(f"- Maximum edge found: **{max_edge:+.1f}%** over baseline")
        lines.append(f"- Average edge of top 10: **{avg_edge_top10:+.1f}%**")
        lines.append("")
        lines.append("The tested indicators do not predict short-term price movement")
        lines.append("better than random. The 20.2% win rate in AUGUR's patterns is")
        lines.append("consistent with noise, not signal.")
    
    lines.append("")
    lines.append("## Recommended Next Steps")
    lines.append("")
    lines.append("1. **If signal found**: Paper trade top 3 indicators for 48h, track actual fills vs. predicted")
    lines.append("2. **If weak signal**: Combine top indicators into composite score, test confluence")
    lines.append("3. **If no signal**: Consider longer timeframes (1h+), different assets, or fundamental factors")
    lines.append("4. **Always**: Account for Coinbase fees (0.4-0.6% maker/taker) — any edge <0.5% is unprofitable")
    lines.append("")
    
    return "\n".join(lines)


if __name__ == '__main__':
    print("Starting AUGUR Leading Indicator Analysis...")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    eth_results = run_analysis('ETH-USD')
    btc_results = run_analysis('BTC-USD')
    
    print(f"\n{'='*60}")
    print(f"GENERATING REPORT")
    print(f"{'='*60}")
    print(f"ETH results: {len(eth_results)} indicator/threshold combos tested")
    print(f"BTC results: {len(btc_results)} indicator/threshold combos tested")
    
    report = format_report(eth_results, btc_results)
    
    with open(OUTPUT_PATH, 'w') as f:
        f.write(report)
    
    print(f"\nReport written to: {OUTPUT_PATH}")
    
    # Quick summary
    eth_directional = [r for r in eth_results 
                       if r['direction'] in ('LONG', 'SHORT', 'LONG (continuation)', 'SHORT (continuation)', 'LONG (reversal)')
                       and 'BASELINE' not in r['indicator'] and r['sample_size'] >= 50]
    eth_baselines = {r['indicator']: r for r in eth_results if 'BASELINE' in r['indicator']}
    
    for r in eth_directional:
        bl = 0
        for la in ['1min', '2min', '5min', '10min']:
            if la in r['indicator']:
                bl_key = f'BASELINE_Random_{la}'
                if bl_key in eth_baselines:
                    bl = eth_baselines[bl_key]['win_rate_02']
        r['edge'] = r['win_rate_02'] - bl
    
    eth_directional.sort(key=lambda r: r['edge'], reverse=True)
    
    print(f"\n--- TOP 5 BY EDGE ---")
    for r in eth_directional[:5]:
        print(f"  {r['indicator']} {r['threshold']} {r['direction']}: "
              f"WR={r['win_rate_02']}%, edge={r['edge']:+.1f}%, N={r['sample_size']}")
