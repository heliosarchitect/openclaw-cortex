#!/usr/bin/env python3
"""
AUGUR Sequence Pattern Miner
Finds multi-step patterns that predict ETH-USD price movements.
Works directly with SQLite for memory efficiency.
"""

import sqlite3
import numpy as np
import pandas as pd
from collections import defaultdict
import time
import warnings
warnings.filterwarnings('ignore')

DB_PATH = '/home/bonsaihorn/Projects/augur-collector/enhanced_data.db'
PRODUCT = 'ETH-USD'

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA cache_size=-200000")  # 200MB cache
    return conn

# ============================================================
# STEP 1: Build a unified time series at ~5-second resolution
# ============================================================

def build_feature_matrix():
    """
    Build feature matrix by resampling all data sources to 5-second bars.
    This is the core dataset we mine patterns from.
    """
    conn = get_connection()
    
    # Get time range (last 48h for train+test, more stable)
    cur = conn.cursor()
    cur.execute('SELECT MAX(timestamp) FROM orderbook_snapshots WHERE product=?', (PRODUCT,))
    max_ts = cur.fetchone()[0]
    # Use last 48 hours
    min_ts = max_ts - 48*3600
    
    print(f"Time range: {pd.Timestamp(min_ts, unit='s')} to {pd.Timestamp(max_ts, unit='s')}")
    print(f"Duration: {(max_ts - min_ts)/3600:.1f} hours")
    
    # ---- Orderbook data: resample to 5-second bars ----
    print("\nLoading orderbook snapshots...")
    ob_query = """
    SELECT 
        (timestamp / 5) * 5 as ts5,
        AVG(mid_price) as mid_price,
        AVG(best_bid) as best_bid,
        AVG(best_ask) as best_ask,
        AVG(bid_size) as bid_size,
        AVG(ask_size) as ask_size,
        AVG(spread_pct) as spread_pct,
        MAX(bid_size) as max_bid_size,
        MAX(ask_size) as max_ask_size,
        COUNT(*) as ob_ticks
    FROM orderbook_snapshots
    WHERE product = ? AND timestamp >= ? AND timestamp <= ?
    GROUP BY ts5
    ORDER BY ts5
    """
    ob = pd.read_sql_query(ob_query, conn, params=(PRODUCT, min_ts, max_ts))
    ob = ob.rename(columns={'ts5': 'timestamp'})
    print(f"  Orderbook: {len(ob)} 5-sec bars")
    
    # ---- Trade flow: resample to 5-second bars ----
    print("Loading trade flow...")
    tf_query = """
    SELECT
        (timestamp / 5) * 5 as ts5,
        SUM(buy_volume) as buy_volume,
        SUM(sell_volume) as sell_volume,
        SUM(buy_count) as buy_count,
        SUM(sell_count) as sell_count,
        AVG(vwap) as vwap
    FROM trade_flow
    WHERE product = ? AND timestamp >= ? AND timestamp <= ?
    GROUP BY ts5
    ORDER BY ts5
    """
    tf = pd.read_sql_query(tf_query, conn, params=(PRODUCT, min_ts, max_ts))
    tf = tf.rename(columns={'ts5': 'timestamp'})
    print(f"  Trade flow: {len(tf)} 5-sec bars")
    
    # ---- Trades: aggregate to 5-second bars ----
    print("Loading trades...")
    tr_query = """
    SELECT
        (timestamp / 5) * 5 as ts5,
        COUNT(*) as trade_count,
        SUM(size) as total_volume,
        SUM(CASE WHEN side='buy' THEN size ELSE 0 END) as buy_vol_trades,
        SUM(CASE WHEN side='sell' THEN size ELSE 0 END) as sell_vol_trades,
        MAX(size) as max_trade_size,
        AVG(price) as avg_trade_price
    FROM trades
    WHERE product = ? AND timestamp >= ? AND timestamp <= ?
    GROUP BY ts5
    ORDER BY ts5
    """
    tr = pd.read_sql_query(tr_query, conn, params=(PRODUCT, min_ts, max_ts))
    tr = tr.rename(columns={'ts5': 'timestamp'})
    print(f"  Trades: {len(tr)} 5-sec bars")
    
    conn.close()
    
    # ---- Merge all sources ----
    print("\nMerging data sources...")
    df = ob.merge(tf, on='timestamp', how='outer').merge(tr, on='timestamp', how='outer')
    df = df.sort_values('timestamp').reset_index(drop=True)
    
    # Forward-fill orderbook data (it changes less frequently)
    for col in ['mid_price', 'best_bid', 'best_ask', 'bid_size', 'ask_size', 'spread_pct']:
        df[col] = df[col].ffill()
    
    # Fill volume/count NaN with 0 (no trades = zero volume)
    vol_cols = ['buy_volume', 'sell_volume', 'buy_count', 'sell_count', 
                'trade_count', 'total_volume', 'buy_vol_trades', 'sell_vol_trades', 'max_trade_size']
    for col in vol_cols:
        if col in df.columns:
            df[col] = df[col].fillna(0)
    
    # Drop rows where mid_price is still NaN
    df = df.dropna(subset=['mid_price']).reset_index(drop=True)
    
    print(f"Merged: {len(df)} rows, {df.columns.tolist()}")
    return df


# ============================================================
# STEP 2: Compute derived features
# ============================================================

def compute_features(df):
    """Compute all derived features for pattern mining."""
    print("\nComputing derived features...")
    
    # ---- Price returns at various horizons ----
    for secs in [5, 15, 30, 60]:
        n = secs // 5  # number of 5-sec bars
        df[f'ret_{secs}s'] = df['mid_price'].pct_change(n) * 100  # percent
    
    # ---- Forward returns (what we're trying to predict) ----
    for secs in [60, 120, 300, 600]:
        n = secs // 5
        df[f'fwd_ret_{secs}s'] = df['mid_price'].shift(-n) / df['mid_price'] - 1
        df[f'fwd_ret_{secs}s'] *= 100  # percent
    
    # ---- Order book imbalance ----
    df['ob_imbalance'] = (df['bid_size'] - df['ask_size']) / (df['bid_size'] + df['ask_size'] + 1e-10)
    
    # ---- Volume imbalance (from trade_flow) ----
    total_vol = df['buy_volume'] + df['sell_volume'] + 1e-10
    df['vol_imbalance'] = (df['buy_volume'] - df['sell_volume']) / total_vol
    
    # ---- Trade imbalance (from direct trades) ----
    total_trade_vol = df['buy_vol_trades'] + df['sell_vol_trades'] + 1e-10
    df['trade_imbalance'] = (df['buy_vol_trades'] - df['sell_vol_trades']) / total_trade_vol
    
    # ---- Rolling statistics (1 min = 12 bars, 5 min = 60 bars) ----
    for window, label in [(12, '1m'), (60, '5m')]:
        # Rolling spread
        df[f'spread_ma_{label}'] = df['spread_pct'].rolling(window, min_periods=1).mean()
        df[f'spread_std_{label}'] = df['spread_pct'].rolling(window, min_periods=1).std()
        
        # Rolling volume
        df[f'buy_vol_ma_{label}'] = df['buy_volume'].rolling(window, min_periods=1).mean()
        df[f'sell_vol_ma_{label}'] = df['sell_volume'].rolling(window, min_periods=1).mean()
        df[f'total_vol_ma_{label}'] = (df['buy_volume'] + df['sell_volume']).rolling(window, min_periods=1).mean()
        
        # Rolling imbalance
        df[f'ob_imb_ma_{label}'] = df['ob_imbalance'].rolling(window, min_periods=1).mean()
        df[f'vol_imb_ma_{label}'] = df['vol_imbalance'].rolling(window, min_periods=1).mean()
        
        # Rolling bid/ask size
        df[f'bid_size_ma_{label}'] = df['bid_size'].rolling(window, min_periods=1).mean()
        df[f'ask_size_ma_{label}'] = df['ask_size'].rolling(window, min_periods=1).mean()
        
        # Rolling trade count
        df[f'trade_count_ma_{label}'] = df['trade_count'].rolling(window, min_periods=1).mean()
        
        # Mid price volatility (std of returns)
        df[f'volatility_{label}'] = df['ret_5s'].rolling(window, min_periods=1).std()
        
        # Price momentum (sum of returns)
        df[f'momentum_{label}'] = df['ret_5s'].rolling(window, min_periods=1).sum()
    
    # ---- Rate of change features (the "delta" approach) ----
    for window in [12, 60]:  # 1 min, 5 min
        label = '1m' if window == 12 else '5m'
        # How fast is bid_size changing?
        df[f'bid_size_roc_{label}'] = df['bid_size'] / (df['bid_size'].shift(window) + 1e-10)
        df[f'ask_size_roc_{label}'] = df['ask_size'] / (df['ask_size'].shift(window) + 1e-10)
        # How fast is spread changing?
        df[f'spread_roc_{label}'] = df['spread_pct'] / (df['spread_pct'].shift(window) + 1e-10)
        # Volume acceleration
        df[f'buy_vol_roc_{label}'] = df[f'buy_vol_ma_{label}'] / (df[f'buy_vol_ma_{label}'].shift(window) + 1e-10)
        # Imbalance change
        df[f'ob_imb_delta_{label}'] = df['ob_imbalance'] - df['ob_imbalance'].shift(window)
        df[f'vol_imb_delta_{label}'] = df['vol_imbalance'] - df['vol_imbalance'].shift(window)
    
    # ---- Spread state features ----
    df['spread_vs_ma'] = df['spread_pct'] / (df['spread_ma_5m'] + 1e-10)  # current vs 5min avg
    df['spread_z'] = (df['spread_pct'] - df['spread_ma_5m']) / (df['spread_std_5m'] + 1e-10)  # z-score
    
    # ---- Volume surge detection ----
    df['vol_surge_1m'] = (df['buy_volume'] + df['sell_volume']) / (df['total_vol_ma_5m'] + 1e-10)
    df['buy_surge_1m'] = df['buy_volume'] / (df['buy_vol_ma_5m'] + 1e-10)
    df['sell_surge_1m'] = df['sell_volume'] / (df['sell_vol_ma_5m'] + 1e-10)
    
    # ---- Large trade detection ----
    max_trade_90 = df['max_trade_size'].quantile(0.9)
    df['large_trade'] = (df['max_trade_size'] > max_trade_90).astype(int)
    
    # Replace inf values
    df = df.replace([np.inf, -np.inf], np.nan)
    
    # Drop initial rows with NaN from rolling windows
    initial_nans = df.isnull().sum(axis=1)
    valid_start = (initial_nans < 10).idxmax()  # first row with < 10 NaN columns
    df = df.iloc[valid_start:].reset_index(drop=True)
    
    print(f"Feature matrix: {len(df)} rows × {len(df.columns)} columns")
    return df


# ============================================================
# STEP 3: Regime detection
# ============================================================

def detect_regimes(df):
    """Classify each point into a market regime."""
    print("\nDetecting market regimes...")
    
    # Use 5-minute volatility and momentum for regime classification
    vol_med = df['volatility_5m'].median()
    mom_threshold = df['momentum_5m'].std() * 0.5
    
    conditions = [
        # Trending up: positive momentum, normal or low volatility
        (df['momentum_5m'] > mom_threshold) & (df['volatility_5m'] <= vol_med * 1.5),
        # Trending down: negative momentum, normal or low volatility  
        (df['momentum_5m'] < -mom_threshold) & (df['volatility_5m'] <= vol_med * 1.5),
        # Volatile/choppy: high volatility regardless of momentum
        (df['volatility_5m'] > vol_med * 1.5),
        # Ranging: low volatility, no clear momentum
    ]
    choices = ['trend_up', 'trend_down', 'volatile', 'ranging']
    
    df['regime'] = np.select(
        conditions,
        choices[:3],
        default='ranging'
    )
    
    regime_counts = df['regime'].value_counts()
    print("Regime distribution:")
    for regime, count in regime_counts.items():
        pct = count / len(df) * 100
        print(f"  {regime}: {count:,} ({pct:.1f}%)")
    
    return df


# ============================================================
# STEP 4: Event-based sequence patterns
# ============================================================

def mine_event_sequences(df, min_occurrences=50):
    """
    Mine multi-step event sequences.
    Define "events" from the features, then look for sequences that predict price moves.
    """
    print("\n" + "="*70)
    print("MINING EVENT SEQUENCES")
    print("="*70)
    
    results = []
    
    # Define events as boolean conditions
    events = {
        'spread_wide': df['spread_z'] > 2,              # spread > 2 std above mean
        'spread_narrow': df['spread_z'] < -1,             # spread below mean
        'spread_compressing': df['spread_roc_1m'] < 0.7,  # spread shrinking fast
        'spread_expanding': df['spread_roc_1m'] > 1.5,    # spread growing fast
        'buy_surge': df['buy_surge_1m'] > 3,              # buy volume 3x normal
        'sell_surge': df['sell_surge_1m'] > 3,             # sell volume 3x normal
        'vol_surge': df['vol_surge_1m'] > 3,              # total volume 3x normal
        'ob_bid_heavy': df['ob_imbalance'] > 0.5,         # bids dominate
        'ob_ask_heavy': df['ob_imbalance'] < -0.5,        # asks dominate
        'ob_imb_flip_bull': df['ob_imb_delta_1m'] > 0.5,  # imbalance shifted bullish
        'ob_imb_flip_bear': df['ob_imb_delta_1m'] < -0.5, # imbalance shifted bearish
        'vol_imb_bull': df['vol_imbalance'] > 0.6,        # strong buy flow
        'vol_imb_bear': df['vol_imbalance'] < -0.6,       # strong sell flow
        'bid_growing': df['bid_size_roc_1m'] > 2,         # bids doubled in 1 min
        'ask_growing': df['ask_size_roc_1m'] > 2,         # asks doubled in 1 min
        'bid_shrinking': df['bid_size_roc_1m'] < 0.5,     # bids halved in 1 min
        'ask_shrinking': df['ask_size_roc_1m'] < 0.5,     # asks halved in 1 min
        'large_trade': df['large_trade'] == 1,             # unusually large trade
        'high_activity': df['trade_count_ma_1m'] > df['trade_count_ma_1m'].quantile(0.8),
        'low_activity': df['trade_count_ma_1m'] < df['trade_count_ma_1m'].quantile(0.2),
        'momentum_up': df['momentum_1m'] > df['momentum_1m'].quantile(0.8),
        'momentum_down': df['momentum_1m'] < df['momentum_1m'].quantile(0.2),
        'vol_accelerating': df['buy_vol_roc_1m'] > 2,     # buy volume accelerating
    }
    
    # Print event frequencies
    print("\nEvent frequencies:")
    for name, mask in events.items():
        count = mask.sum()
        pct = count / len(df) * 100
        print(f"  {name}: {count:,} ({pct:.1f}%)")
    
    # ---- Single events with forward returns ----
    print("\n--- Single Event Patterns ---")
    for fwd_col, fwd_label in [('fwd_ret_60s', '1min'), ('fwd_ret_120s', '2min'), 
                                ('fwd_ret_300s', '5min'), ('fwd_ret_600s', '10min')]:
        print(f"\n  Forward return: {fwd_label}")
        for name, mask in events.items():
            subset = df.loc[mask, fwd_col].dropna()
            if len(subset) < min_occurrences:
                continue
            
            # Check for directional moves
            for direction, dir_label in [(1, 'LONG'), (-1, 'SHORT')]:
                if direction == 1:
                    wins = (subset > 0.2).sum()  # > 0.2% up
                    losses = (subset < -0.2).sum()
                else:
                    wins = (subset < -0.2).sum()  # > 0.2% down
                    losses = (subset > 0.2).sum()
                
                total_signals = wins + losses
                if total_signals < min_occurrences // 2:
                    continue
                    
                wr = wins / total_signals if total_signals > 0 else 0
                avg_ret = subset.mean() * direction
                
                if wr > 0.55:  # Only report if > 55% WR
                    results.append({
                        'type': 'single',
                        'pattern': f"{name}",
                        'direction': dir_label,
                        'horizon': fwd_label,
                        'signals': total_signals,
                        'win_rate': wr,
                        'avg_ret_pct': avg_ret,
                        'med_ret_pct': subset.median() * direction
                    })
                    if wr > 0.6:
                        print(f"    ★ {name} → {dir_label} ({fwd_label}): WR={wr:.1%}, n={total_signals}, avg={avg_ret:.4f}%")
    
    # ---- Two-event sequences ----
    print("\n--- Two-Event Sequence Patterns ---")
    # Define interesting sequence pairs and the gap between them
    sequence_pairs = [
        ('spread_wide', 'buy_surge', 'Spread widens then buy surge'),
        ('spread_wide', 'spread_compressing', 'Spread widens then compresses'),
        ('sell_surge', 'ob_imb_flip_bull', 'Sell surge then imbalance flips bull'),
        ('buy_surge', 'ob_imb_flip_bull', 'Buy surge then imbalance flips bull'),
        ('ob_ask_heavy', 'ob_imb_flip_bull', 'Ask-heavy then flips bullish'),
        ('ob_bid_heavy', 'ob_imb_flip_bear', 'Bid-heavy then flips bearish'),
        ('spread_expanding', 'vol_surge', 'Spread expands then volume surge'),
        ('large_trade', 'buy_surge', 'Large trade then buy surge'),
        ('large_trade', 'sell_surge', 'Large trade then sell surge'),
        ('low_activity', 'vol_surge', 'Low activity then volume surge'),
        ('bid_growing', 'buy_surge', 'Bids growing then buy surge'),
        ('ask_growing', 'sell_surge', 'Asks growing then sell surge'),
        ('vol_imb_bull', 'momentum_up', 'Buy flow then momentum up'),
        ('vol_imb_bear', 'momentum_down', 'Sell flow then momentum down'),
        ('spread_narrow', 'buy_surge', 'Tight spread then buy surge'),
        ('spread_narrow', 'sell_surge', 'Tight spread then sell surge'),
        ('ob_imb_flip_bull', 'buy_surge', 'Imbalance flips bull then buy surge'),
        ('ob_imb_flip_bear', 'sell_surge', 'Imbalance flips bear then sell surge'),
        ('vol_accelerating', 'ob_bid_heavy', 'Volume accelerating + bids heavy'),
        ('bid_shrinking', 'sell_surge', 'Bids shrinking then sell surge'),
        ('ask_shrinking', 'buy_surge', 'Asks shrinking then buy surge'),
    ]
    
    # For sequences: event A happens, then within 1-3 minutes event B happens
    # We check forward returns AFTER event B
    lookback_bars = 36  # 3 minutes in 5-sec bars
    
    for evt_a_name, evt_b_name, description in sequence_pairs:
        evt_a = events[evt_a_name]
        evt_b = events[evt_b_name]
        
        # For each occurrence of event B, check if event A happened in prior 1-3 minutes
        b_indices = df.index[evt_b].tolist()
        
        sequence_indices = []
        for b_idx in b_indices:
            # Look back 12-36 bars (1-3 min) for event A
            window_start = max(0, b_idx - lookback_bars)
            window_end = max(0, b_idx - 4)  # At least 20 sec gap
            if window_end <= window_start:
                continue
            if evt_a.iloc[window_start:window_end].any():
                sequence_indices.append(b_idx)
        
        if len(sequence_indices) < min_occurrences:
            continue
        
        for fwd_col, fwd_label in [('fwd_ret_60s', '1min'), ('fwd_ret_120s', '2min'), 
                                    ('fwd_ret_300s', '5min'), ('fwd_ret_600s', '10min')]:
            subset = df.loc[sequence_indices, fwd_col].dropna()
            if len(subset) < min_occurrences // 2:
                continue
            
            for direction, dir_label in [(1, 'LONG'), (-1, 'SHORT')]:
                if direction == 1:
                    wins = (subset > 0.2).sum()
                    losses = (subset < -0.2).sum()
                else:
                    wins = (subset < -0.2).sum()
                    losses = (subset > 0.2).sum()
                
                total_signals = wins + losses
                if total_signals < min_occurrences // 3:
                    continue
                
                wr = wins / total_signals if total_signals > 0 else 0
                avg_ret = subset.mean() * direction
                
                if wr > 0.55:
                    results.append({
                        'type': 'sequence',
                        'pattern': f"{evt_a_name} → {evt_b_name}",
                        'description': description,
                        'direction': dir_label,
                        'horizon': fwd_label,
                        'signals': total_signals,
                        'win_rate': wr,
                        'avg_ret_pct': avg_ret,
                        'med_ret_pct': subset.median() * direction
                    })
                    if wr > 0.58:
                        print(f"    ★ {description} → {dir_label} ({fwd_label}): WR={wr:.1%}, n={total_signals}, avg={avg_ret:.4f}%")
    
    return results


# ============================================================
# STEP 5: Rate of change patterns
# ============================================================

def mine_roc_patterns(df, min_occurrences=50):
    """Mine patterns based on rate of change / acceleration."""
    print("\n" + "="*70)
    print("MINING RATE-OF-CHANGE PATTERNS")
    print("="*70)
    
    results = []
    
    # Define ROC-based conditions with multiple thresholds
    roc_conditions = {
        # Bid size changes
        'bid_3x_1m': df['bid_size_roc_1m'] > 3,
        'bid_halved_1m': df['bid_size_roc_1m'] < 0.5,
        'bid_2x_5m': df['bid_size_roc_5m'] > 2,
        
        # Ask size changes  
        'ask_3x_1m': df['ask_size_roc_1m'] > 3,
        'ask_halved_1m': df['ask_size_roc_1m'] < 0.5,
        'ask_2x_5m': df['ask_size_roc_5m'] > 2,
        
        # Spread dynamics
        'spread_compress_fast': df['spread_roc_1m'] < 0.5,  # spread halved in 1 min
        'spread_expand_fast': df['spread_roc_1m'] > 2,     # spread doubled in 1 min
        'spread_compress_5m': df['spread_roc_5m'] < 0.5,
        
        # Imbalance shifts
        'imb_shift_bull_fast': df['ob_imb_delta_1m'] > 0.7,  # massive bull shift
        'imb_shift_bear_fast': df['ob_imb_delta_1m'] < -0.7, # massive bear shift
        'vol_imb_shift_bull': df['vol_imb_delta_1m'] > 0.7,
        'vol_imb_shift_bear': df['vol_imb_delta_1m'] < -0.7,
        
        # Volume acceleration
        'vol_accel_buy': df['buy_vol_roc_1m'] > 3,    # buy volume tripled vs 5m avg
        'vol_accel_sell': (df['sell_volume'] / (df['sell_vol_ma_5m'] + 1e-10)) > 3,
        
        # Combined ROC
        'bid_grow_spread_narrow': (df['bid_size_roc_1m'] > 2) & (df['spread_roc_1m'] < 0.8),
        'ask_grow_spread_narrow': (df['ask_size_roc_1m'] > 2) & (df['spread_roc_1m'] < 0.8),
        'bid_grow_buy_surge': (df['bid_size_roc_1m'] > 2) & (df['buy_surge_1m'] > 2),
        'ask_grow_sell_surge': (df['ask_size_roc_1m'] > 2) & ((df['sell_volume'] / (df['sell_vol_ma_5m'] + 1e-10)) > 2),
    }
    
    for name, mask in roc_conditions.items():
        count = mask.sum()
        if count < min_occurrences:
            continue
        
        for fwd_col, fwd_label in [('fwd_ret_60s', '1min'), ('fwd_ret_120s', '2min'), 
                                    ('fwd_ret_300s', '5min'), ('fwd_ret_600s', '10min')]:
            subset = df.loc[mask, fwd_col].dropna()
            if len(subset) < min_occurrences:
                continue
            
            for direction, dir_label in [(1, 'LONG'), (-1, 'SHORT')]:
                if direction == 1:
                    wins = (subset > 0.2).sum()
                    losses = (subset < -0.2).sum()
                else:
                    wins = (subset < -0.2).sum()
                    losses = (subset > 0.2).sum()
                
                total = wins + losses
                if total < min_occurrences // 2:
                    continue
                
                wr = wins / total if total > 0 else 0
                avg_ret = subset.mean() * direction
                
                if wr > 0.55:
                    results.append({
                        'type': 'roc',
                        'pattern': name,
                        'direction': dir_label,
                        'horizon': fwd_label,
                        'signals': total,
                        'win_rate': wr,
                        'avg_ret_pct': avg_ret,
                        'med_ret_pct': subset.median() * direction
                    })
                    if wr > 0.58:
                        print(f"  ★ {name} → {dir_label} ({fwd_label}): WR={wr:.1%}, n={total}, avg={avg_ret:.4f}%")
    
    return results


# ============================================================
# STEP 6: Regime-conditional patterns
# ============================================================

def mine_regime_patterns(df, all_results, min_occurrences=30):
    """Check how top patterns perform in different regimes."""
    print("\n" + "="*70)
    print("REGIME-CONDITIONAL ANALYSIS")
    print("="*70)
    
    # Take top patterns (WR > 58%) and check per-regime
    top_patterns = [r for r in all_results if r['win_rate'] > 0.58]
    
    if not top_patterns:
        print("No patterns above 58% WR to analyze by regime.")
        return []
    
    regime_results = []
    
    # Re-create event masks (simplified — just the key ones)
    events = {
        'spread_wide': df['spread_z'] > 2,
        'buy_surge': df['buy_surge_1m'] > 3,
        'sell_surge': df['sell_surge_1m'] > 3,
        'ob_imb_flip_bull': df['ob_imb_delta_1m'] > 0.5,
        'ob_imb_flip_bear': df['ob_imb_delta_1m'] < -0.5,
        'vol_imb_bull': df['vol_imbalance'] > 0.6,
        'vol_imb_bear': df['vol_imbalance'] < -0.6,
        'bid_growing': df['bid_size_roc_1m'] > 2,
        'ask_growing': df['ask_size_roc_1m'] > 2,
        'large_trade': df['large_trade'] == 1,
        'momentum_up': df['momentum_1m'] > df['momentum_1m'].quantile(0.8),
        'momentum_down': df['momentum_1m'] < df['momentum_1m'].quantile(0.2),
        'bid_3x_1m': df['bid_size_roc_1m'] > 3,
        'ask_halved_1m': df['ask_size_roc_1m'] < 0.5,
        'imb_shift_bull_fast': df['ob_imb_delta_1m'] > 0.7,
        'imb_shift_bear_fast': df['ob_imb_delta_1m'] < -0.7,
        'vol_accel_buy': df['buy_vol_roc_1m'] > 3,
        'bid_grow_spread_narrow': (df['bid_size_roc_1m'] > 2) & (df['spread_roc_1m'] < 0.8),
        'bid_grow_buy_surge': (df['bid_size_roc_1m'] > 2) & (df['buy_surge_1m'] > 2),
    }
    
    # For each top pattern, check per regime
    seen_patterns = set()
    for pat in top_patterns:
        pname = pat['pattern']
        if pname in seen_patterns:
            continue
        seen_patterns.add(pname)
        
        # Find the mask for this pattern
        if pname in events:
            mask = events[pname]
        elif ' → ' in pname:
            # Skip sequences for now, complex to reconstruct
            continue
        else:
            continue
        
        fwd_col_map = {'1min': 'fwd_ret_60s', '2min': 'fwd_ret_120s', 
                       '5min': 'fwd_ret_300s', '10min': 'fwd_ret_600s'}
        fwd_col = fwd_col_map.get(pat['horizon'], 'fwd_ret_300s')
        direction = 1 if pat['direction'] == 'LONG' else -1
        
        print(f"\n  Pattern: {pname} → {pat['direction']} ({pat['horizon']})")
        print(f"  Overall: WR={pat['win_rate']:.1%}, n={pat['signals']}")
        
        for regime in ['trend_up', 'trend_down', 'volatile', 'ranging']:
            regime_mask = mask & (df['regime'] == regime)
            subset = df.loc[regime_mask, fwd_col].dropna()
            
            if len(subset) < 20:
                continue
            
            if direction == 1:
                wins = (subset > 0.2).sum()
                losses = (subset < -0.2).sum()
            else:
                wins = (subset < -0.2).sum()
                losses = (subset > 0.2).sum()
            
            total = wins + losses
            if total < 15:
                continue
            
            wr = wins / total
            marker = "★" if wr > 0.65 else "✗" if wr < 0.45 else " "
            print(f"    {marker} {regime}: WR={wr:.1%}, n={total}")
            
            regime_results.append({
                'pattern': pname,
                'direction': pat['direction'],
                'horizon': pat['horizon'],
                'regime': regime,
                'signals': total,
                'win_rate': wr,
            })
    
    return regime_results


# ============================================================
# STEP 7: Train/test split validation
# ============================================================

def validate_patterns(df, all_results, min_occurrences=30):
    """Split data in half and validate patterns out-of-sample."""
    print("\n" + "="*70)
    print("TRAIN/TEST VALIDATION")
    print("="*70)
    
    mid_point = len(df) // 2
    train = df.iloc[:mid_point]
    test = df.iloc[mid_point:]
    
    mid_ts = df.iloc[mid_point]['timestamp']
    print(f"Train: {len(train)} rows ({pd.Timestamp(train.iloc[0]['timestamp'], unit='s')} to {pd.Timestamp(mid_ts, unit='s')})")
    print(f"Test:  {len(test)} rows ({pd.Timestamp(mid_ts, unit='s')} to {pd.Timestamp(test.iloc[-1]['timestamp'], unit='s')})")
    
    # Re-create events for train and test separately
    def make_events(d):
        return {
            'spread_wide': d['spread_z'] > 2,
            'spread_narrow': d['spread_z'] < -1,
            'spread_compressing': d['spread_roc_1m'] < 0.7,
            'buy_surge': d['buy_surge_1m'] > 3,
            'sell_surge': d['sell_surge_1m'] > 3,
            'ob_bid_heavy': d['ob_imbalance'] > 0.5,
            'ob_ask_heavy': d['ob_imbalance'] < -0.5,
            'ob_imb_flip_bull': d['ob_imb_delta_1m'] > 0.5,
            'ob_imb_flip_bear': d['ob_imb_delta_1m'] < -0.5,
            'vol_imb_bull': d['vol_imbalance'] > 0.6,
            'vol_imb_bear': d['vol_imbalance'] < -0.6,
            'bid_growing': d['bid_size_roc_1m'] > 2,
            'ask_growing': d['ask_size_roc_1m'] > 2,
            'large_trade': d['large_trade'] == 1,
            'momentum_up': d['momentum_1m'] > d['momentum_1m'].quantile(0.8),
            'momentum_down': d['momentum_1m'] < d['momentum_1m'].quantile(0.2),
            'bid_3x_1m': d['bid_size_roc_1m'] > 3,
            'bid_halved_1m': d['bid_size_roc_1m'] < 0.5,
            'ask_3x_1m': d['ask_size_roc_1m'] > 3,
            'ask_halved_1m': d['ask_size_roc_1m'] < 0.5,
            'spread_compress_fast': d['spread_roc_1m'] < 0.5,
            'spread_expand_fast': d['spread_roc_1m'] > 2,
            'imb_shift_bull_fast': d['ob_imb_delta_1m'] > 0.7,
            'imb_shift_bear_fast': d['ob_imb_delta_1m'] < -0.7,
            'vol_accel_buy': d['buy_vol_roc_1m'] > 3,
            'bid_grow_spread_narrow': (d['bid_size_roc_1m'] > 2) & (d['spread_roc_1m'] < 0.8),
            'bid_grow_buy_surge': (d['bid_size_roc_1m'] > 2) & (d['buy_surge_1m'] > 2),
            'ask_grow_sell_surge': (d['ask_size_roc_1m'] > 2) & ((d['sell_volume'] / (d['sell_vol_ma_5m'] + 1e-10)) > 2),
        }
    
    fwd_col_map = {'1min': 'fwd_ret_60s', '2min': 'fwd_ret_120s', 
                   '5min': 'fwd_ret_300s', '10min': 'fwd_ret_600s'}
    
    # Filter to patterns with WR > 57%
    top = [r for r in all_results if r['win_rate'] > 0.57 and r['type'] != 'sequence']
    
    # Deduplicate by pattern+direction+horizon
    seen = set()
    unique_top = []
    for r in top:
        key = (r['pattern'], r['direction'], r['horizon'])
        if key not in seen:
            seen.add(key)
            unique_top.append(r)
    
    train_events = make_events(train)
    test_events = make_events(test)
    
    validated = []
    
    print(f"\nValidating {len(unique_top)} patterns...")
    print(f"{'Pattern':<35} {'Dir':<6} {'Hz':<5} {'Train WR':<10} {'Test WR':<10} {'Train n':<8} {'Test n':<8} {'Verdict'}")
    print("-" * 100)
    
    for pat in sorted(unique_top, key=lambda x: -x['win_rate']):
        pname = pat['pattern']
        if pname not in train_events:
            continue
        
        train_mask = train_events[pname]
        test_mask = test_events[pname]
        
        fwd_col = fwd_col_map.get(pat['horizon'], 'fwd_ret_300s')
        direction = 1 if pat['direction'] == 'LONG' else -1
        
        # Train metrics
        train_sub = train.loc[train_mask, fwd_col].dropna()
        test_sub = test.loc[test_mask, fwd_col].dropna()
        
        def calc_wr(sub, d):
            if d == 1:
                w = (sub > 0.2).sum()
                l = (sub < -0.2).sum()
            else:
                w = (sub < -0.2).sum()
                l = (sub > 0.2).sum()
            t = w + l
            return (w / t if t > 0 else 0), t
        
        train_wr, train_n = calc_wr(train_sub, direction)
        test_wr, test_n = calc_wr(test_sub, direction)
        
        if train_n < min_occurrences // 2 or test_n < min_occurrences // 3:
            continue
        
        # Verdict
        if test_wr > 0.58 and train_wr > 0.55:
            verdict = "✅ VALID"
        elif test_wr > 0.55 and train_wr > 0.55:
            verdict = "🟡 MARGINAL"
        elif train_wr > 0.65 and test_wr < 0.48:
            verdict = "❌ OVERFIT"
        elif test_wr < 0.50:
            verdict = "❌ FAILS"
        else:
            verdict = "🟡 WEAK"
        
        print(f"{pname:<35} {pat['direction']:<6} {pat['horizon']:<5} {train_wr:<10.1%} {test_wr:<10.1%} {train_n:<8} {test_n:<8} {verdict}")
        
        validated.append({
            'pattern': pname,
            'direction': pat['direction'],
            'horizon': pat['horizon'],
            'train_wr': train_wr,
            'test_wr': test_wr,
            'train_n': train_n,
            'test_n': test_n,
            'verdict': verdict,
            'avg_ret': pat.get('avg_ret_pct', 0),
        })
    
    return validated


# ============================================================
# STEP 8: Consecutive flow pattern mining
# ============================================================

def mine_consecutive_flow(df, min_occurrences=50):
    """
    Look for N consecutive periods of buy/sell dominance predicting breakouts.
    This is the "3 consecutive buy-dominated flow periods → price breakout" hypothesis.
    """
    print("\n" + "="*70)
    print("CONSECUTIVE FLOW PATTERNS")
    print("="*70)
    
    results = []
    
    # Create per-minute flow dominance (resample to 1-min)
    # Each bar is 5 sec, so 12 bars = 1 minute
    # Use rolling sums
    for window in [12, 24, 36]:  # 1min, 2min, 3min windows
        label = f'{window*5//60}min'
        df[f'roll_buy_vol_{label}'] = df['buy_volume'].rolling(window, min_periods=1).sum()
        df[f'roll_sell_vol_{label}'] = df['sell_volume'].rolling(window, min_periods=1).sum()
        df[f'roll_flow_ratio_{label}'] = (
            df[f'roll_buy_vol_{label}'] / (df[f'roll_sell_vol_{label}'] + 1e-10)
        )
    
    # Consecutive buy-dominant periods (flow ratio > threshold for N consecutive minutes)
    for n_consec in [2, 3, 4, 5]:
        for threshold in [1.5, 2.0, 3.0]:
            buy_dom = (df['roll_flow_ratio_1min'] > threshold).astype(int)
            # Rolling sum of consecutive periods
            consec = buy_dom.rolling(n_consec * 12, min_periods=n_consec * 12).sum()
            mask = consec >= n_consec * 12 * 0.8  # 80% of bars in window must be buy-dominant
            
            count = mask.sum()
            if count < min_occurrences:
                continue
            
            for fwd_col, fwd_label in [('fwd_ret_120s', '2min'), ('fwd_ret_300s', '5min'), ('fwd_ret_600s', '10min')]:
                subset = df.loc[mask, fwd_col].dropna()
                if len(subset) < min_occurrences:
                    continue
                
                wins = (subset > 0.2).sum()
                losses = (subset < -0.2).sum()
                total = wins + losses
                if total < min_occurrences // 2:
                    continue
                
                wr = wins / total
                avg_ret = subset.mean()
                
                if wr > 0.55:
                    name = f'{n_consec}x_buy_dom_{threshold}x_{fwd_label}'
                    results.append({
                        'type': 'consecutive',
                        'pattern': name,
                        'description': f'{n_consec} consecutive {label} periods with buy/sell ratio > {threshold}x',
                        'direction': 'LONG',
                        'horizon': fwd_label,
                        'signals': total,
                        'win_rate': wr,
                        'avg_ret_pct': avg_ret,
                    })
                    if wr > 0.58:
                        print(f"  ★ {name}: WR={wr:.1%}, n={total}, avg={avg_ret:.4f}%")
            
            # Same for sell-dominant
            sell_dom = (df['roll_flow_ratio_1min'] < 1/threshold).astype(int)
            consec = sell_dom.rolling(n_consec * 12, min_periods=n_consec * 12).sum()
            mask = consec >= n_consec * 12 * 0.8
            
            count = mask.sum()
            if count < min_occurrences:
                continue
            
            for fwd_col, fwd_label in [('fwd_ret_120s', '2min'), ('fwd_ret_300s', '5min'), ('fwd_ret_600s', '10min')]:
                subset = df.loc[mask, fwd_col].dropna()
                if len(subset) < min_occurrences:
                    continue
                
                wins = (subset < -0.2).sum()
                losses = (subset > 0.2).sum()
                total = wins + losses
                if total < min_occurrences // 2:
                    continue
                
                wr = wins / total
                avg_ret = -subset.mean()
                
                if wr > 0.55:
                    name = f'{n_consec}x_sell_dom_{threshold}x_{fwd_label}'
                    results.append({
                        'type': 'consecutive',
                        'pattern': name,
                        'description': f'{n_consec} consecutive {label} periods with sell/buy ratio > {threshold}x',
                        'direction': 'SHORT',
                        'horizon': fwd_label,
                        'signals': total,
                        'win_rate': wr,
                        'avg_ret_pct': avg_ret,
                    })
                    if wr > 0.58:
                        print(f"  ★ {name}: WR={wr:.1%}, n={total}, avg={avg_ret:.4f}%")
    
    return results


# ============================================================
# STEP 9: Write comprehensive report
# ============================================================

def write_report(all_results, validated, regime_results, df):
    """Write the final analysis report."""
    
    output_path = '/home/bonsaihorn/.openclaw/workspace/analysis/augur-sequence-patterns.md'
    
    with open(output_path, 'w') as f:
        f.write("# AUGUR Sequence Pattern Analysis\n")
        f.write(f"**Date:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"**Product:** ETH-USD\n")
        f.write(f"**Data:** {len(df):,} 5-second bars (~{len(df)*5/3600:.0f} hours)\n")
        f.write(f"**Price range:** ${df['mid_price'].min():.2f} - ${df['mid_price'].max():.2f}\n\n")
        
        # Summary
        total_patterns = len(all_results)
        good_patterns = len([r for r in all_results if r['win_rate'] > 0.58])
        f.write(f"## Summary\n")
        f.write(f"- **Total patterns tested:** {total_patterns}\n")
        f.write(f"- **Patterns > 58% WR:** {good_patterns}\n")
        f.write(f"- **Patterns > 60% WR:** {len([r for r in all_results if r['win_rate'] > 0.60])}\n")
        validated_good = [v for v in validated if '✅' in v.get('verdict', '')]
        f.write(f"- **Validated (train+test > 55%):** {len(validated_good)}\n\n")
        
        # ---- Validated patterns (the money section) ----
        f.write("## 🏆 Validated Patterns (Train/Test Split)\n\n")
        f.write("These patterns show edge in BOTH first-half and second-half of data.\n\n")
        
        if validated:
            f.write("| Pattern | Direction | Horizon | Train WR | Test WR | Train n | Test n | Verdict |\n")
            f.write("|---------|-----------|---------|----------|---------|---------|--------|----------|\n")
            for v in sorted(validated, key=lambda x: -(x['test_wr'])):
                f.write(f"| {v['pattern']} | {v['direction']} | {v['horizon']} | {v['train_wr']:.1%} | {v['test_wr']:.1%} | {v['train_n']} | {v['test_n']} | {v['verdict']} |\n")
        else:
            f.write("*No patterns survived train/test validation at required thresholds.*\n")
        
        f.write("\n### Interpretation\n")
        f.write("- ✅ VALID: Both train and test WR > 55%. Real edge.\n")
        f.write("- 🟡 MARGINAL: Some edge but not robust. Needs more data.\n")
        f.write("- ❌ OVERFIT: High train WR, low test WR. Don't trade this.\n")
        f.write("- ❌ FAILS: No edge in test set.\n\n")
        
        # ---- Top patterns by category ----
        f.write("## All Patterns by Category\n\n")
        
        for ptype, label in [('single', 'Single Event Patterns'), 
                              ('sequence', 'Two-Event Sequences'),
                              ('roc', 'Rate of Change Patterns'),
                              ('consecutive', 'Consecutive Flow Patterns')]:
            cat_results = [r for r in all_results if r.get('type') == ptype]
            if not cat_results:
                continue
            
            f.write(f"### {label}\n\n")
            
            # Sort by win rate
            cat_results.sort(key=lambda x: -x['win_rate'])
            
            f.write("| Pattern | Direction | Horizon | WR | Signals | Avg Ret |\n")
            f.write("|---------|-----------|---------|-----|---------|----------|\n")
            for r in cat_results[:30]:  # Top 30
                desc = r.get('description', '')
                if desc:
                    desc = f" ({desc})"
                f.write(f"| {r['pattern']}{desc} | {r['direction']} | {r['horizon']} | {r['win_rate']:.1%} | {r['signals']} | {r['avg_ret_pct']:.4f}% |\n")
            
            f.write("\n")
        
        # ---- Regime analysis ----
        if regime_results:
            f.write("## Regime-Conditional Performance\n\n")
            f.write("How top patterns perform in different market conditions:\n\n")
            
            # Group by pattern
            by_pattern = defaultdict(list)
            for r in regime_results:
                by_pattern[f"{r['pattern']}_{r['direction']}_{r['horizon']}"].append(r)
            
            for key, entries in by_pattern.items():
                pat = entries[0]
                f.write(f"**{pat['pattern']} → {pat['direction']} ({pat['horizon']})**\n\n")
                f.write("| Regime | WR | Signals |\n")
                f.write("|--------|-----|----------|\n")
                for e in entries:
                    marker = "★" if e['win_rate'] > 0.65 else "✗" if e['win_rate'] < 0.45 else ""
                    f.write(f"| {e['regime']} | {e['win_rate']:.1%} {marker} | {e['signals']} |\n")
                f.write("\n")
        
        # ---- Regime distribution ----
        f.write("## Market Regime Distribution\n\n")
        regime_counts = df['regime'].value_counts()
        for regime, count in regime_counts.items():
            pct = count / len(df) * 100
            f.write(f"- **{regime}:** {count:,} bars ({pct:.1f}%)\n")
        
        # ---- Methodology ----
        f.write("\n## Methodology\n\n")
        f.write("### Feature Engineering\n")
        f.write("- **Base features:** mid_price, bid/ask size, spread, buy/sell volume, trade count\n")
        f.write("- **Rolling statistics:** 1-minute and 5-minute moving averages, std dev\n")
        f.write("- **Rate of change:** How fast features change over 1min and 5min windows\n")
        f.write("- **Imbalance:** Order book (bid vs ask size), volume (buy vs sell), and their deltas\n")
        f.write("- **Surge detection:** Current value vs rolling average ratio\n")
        f.write("- **Regime:** Based on 5-minute momentum and volatility\n\n")
        
        f.write("### Validation\n")
        f.write("- Minimum 50 occurrences per pattern (25 for regime sub-analysis)\n")
        f.write("- Win = >0.2% move in predicted direction\n")
        f.write("- Loss = >0.2% move against predicted direction\n")
        f.write("- Train/test split: first half vs second half of 48-hour window\n")
        f.write("- Both train and test must show >55% WR for ✅ VALID\n\n")
        
        f.write("### Event Definitions\n")
        f.write("| Event | Definition |\n")
        f.write("|-------|------------|\n")
        f.write("| spread_wide | Spread z-score > 2 (2+ std above 5-min mean) |\n")
        f.write("| buy_surge | Buy volume > 3x 5-min rolling average |\n")
        f.write("| ob_imb_flip_bull | Order book imbalance shifted >0.5 toward bids in 1 min |\n")
        f.write("| bid_3x_1m | Bid size tripled in 1 minute |\n")
        f.write("| spread_compress_fast | Spread halved in 1 minute |\n")
        f.write("| vol_accel_buy | Buy volume tripled vs 5-min rolling avg |\n")
        f.write("| consecutive flow | N minutes of buy/sell ratio > threshold |\n\n")
        
        # ---- Key insights ----
        f.write("## Key Insights\n\n")
        
        # Analyze what works
        valid_count = len(validated_good)
        if valid_count > 0:
            best = max(validated, key=lambda x: x['test_wr'])
            f.write(f"1. **Best validated pattern:** {best['pattern']} → {best['direction']} ({best['horizon']}), ")
            f.write(f"test WR={best['test_wr']:.1%}\n")
        
        # Check if longer horizons work better
        by_horizon = defaultdict(list)
        for r in all_results:
            by_horizon[r['horizon']].append(r['win_rate'])
        f.write("\n2. **Win rate by horizon:**\n")
        for h in ['1min', '2min', '5min', '10min']:
            if h in by_horizon:
                wrs = by_horizon[h]
                f.write(f"   - {h}: avg WR = {np.mean(wrs):.1%} (across {len(wrs)} patterns)\n")
        
        # Direction bias
        long_wrs = [r['win_rate'] for r in all_results if r['direction'] == 'LONG']
        short_wrs = [r['win_rate'] for r in all_results if r['direction'] == 'SHORT']
        if long_wrs and short_wrs:
            f.write(f"\n3. **Direction bias:** LONG avg WR = {np.mean(long_wrs):.1%}, SHORT avg WR = {np.mean(short_wrs):.1%}\n")
        
        f.write("\n---\n")
        f.write(f"*Generated by AUGUR Sequence Pattern Miner*\n")
    
    print(f"\n✅ Report written to: {output_path}")
    return output_path


# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    t0 = time.time()
    
    # Build the feature matrix
    df = build_feature_matrix()
    df = compute_features(df)
    df = detect_regimes(df)
    
    print(f"\nData prepared in {time.time()-t0:.1f}s")
    print(f"Feature matrix shape: {df.shape}")
    
    # Mine patterns
    all_results = []
    
    t1 = time.time()
    event_results = mine_event_sequences(df)
    all_results.extend(event_results)
    print(f"Event sequences: {len(event_results)} patterns found ({time.time()-t1:.1f}s)")
    
    t1 = time.time()
    roc_results = mine_roc_patterns(df)
    all_results.extend(roc_results)
    print(f"ROC patterns: {len(roc_results)} patterns found ({time.time()-t1:.1f}s)")
    
    t1 = time.time()
    consec_results = mine_consecutive_flow(df)
    all_results.extend(consec_results)
    print(f"Consecutive flow: {len(consec_results)} patterns found ({time.time()-t1:.1f}s)")
    
    # Regime analysis
    t1 = time.time()
    regime_results = mine_regime_patterns(df, all_results)
    print(f"Regime analysis: {len(regime_results)} entries ({time.time()-t1:.1f}s)")
    
    # Validate top patterns
    t1 = time.time()
    validated = validate_patterns(df, all_results)
    print(f"Validation: {len(validated)} patterns tested ({time.time()-t1:.1f}s)")
    
    # Write report
    write_report(all_results, validated, regime_results, df)
    
    print(f"\nTotal time: {time.time()-t0:.1f}s")
    print(f"Total patterns with >55% WR: {len(all_results)}")
    print(f"Validated patterns: {len([v for v in validated if '✅' in v.get('verdict', '')])}")
