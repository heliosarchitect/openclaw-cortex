#!/usr/bin/env python3
"""
MILLION-SCALE PATTERN SEARCH - CHRONOGENESIS MODE
Test MILLIONS of pattern combinations with exhaustive parameter sweeps
"""

import sqlite3
import pandas as pd
import numpy as np
from multiprocessing import Pool, cpu_count
from itertools import product, combinations, permutations
import time
from dataclasses import dataclass
import random
import warnings
warnings.filterwarnings('ignore')

@dataclass
class PatternResult:
    pattern_id: int
    pattern_description: str
    total_profit: float
    num_trades: int
    win_rate: float
    avg_profit_per_trade: float
    max_drawdown: float

class ChronogenesisPatternGenerator:
    """Generate MILLIONS of pattern combinations"""
    
    def __init__(self):
        self.features = ['close', 'high', 'low', 'open', 'volume', 
                        'body', 'upper_wick', 'lower_wick', 'wick_ratio',
                        'body_pct', 'range']
        
        # Exhaustive parameter ranges
        self.windows = list(range(3, 21))  # 3-20 candles
        self.thresholds = [0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 1.2, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 7.0, 10.0]
        self.decay_rates = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95]
        self.percentiles = [10, 20, 30, 40, 50, 60, 70, 80, 90, 95]
        
    def generate_all_patterns(self):
        """Generate millions of pattern combinations"""
        patterns = []
        pattern_id = 0
        
        print("Generating pattern space...")
        
        # 1. BASELINE VARIANTS (building on $777 winner) - Exhaustive parameter sweep
        print("  - Baseline variants...")
        for window in self.windows:
            for feature in self.features:
                for threshold in self.thresholds:
                    for comparison in ['divide', 'subtract', 'ratio']:
                        patterns.append({
                            'id': pattern_id,
                            'type': 'baseline_variant',
                            'window': window,
                            'feature': feature,
                            'threshold': threshold,
                            'comparison': comparison,
                            'desc': f"{feature}_{comparison}_max_{threshold}_w{window}"
                        })
                        pattern_id += 1
        
        # 2. DUAL FEATURE INTERACTIONS - All combinations
        print("  - Dual feature interactions...")
        for window in self.windows:
            for f1, f2 in combinations(self.features, 2):
                for op in ['multiply', 'divide', 'add', 'subtract', 'max', 'min']:
                    for threshold in [0.5, 1.0, 1.5, 2.0, 3.0]:
                        patterns.append({
                            'id': pattern_id,
                            'type': 'dual_interaction',
                            'window': window,
                            'feature1': f1,
                            'feature2': f2,
                            'operator': op,
                            'threshold': threshold,
                            'desc': f"{f1}_{op}_{f2}_threshold{threshold}_w{window}"
                        })
                        pattern_id += 1
        
        # 3. TRIPLE FEATURE COMBOS
        print("  - Triple feature combinations...")
        key_features = ['volume', 'body', 'wick_ratio', 'upper_wick', 'lower_wick', 'close']
        for window in [5, 7, 10, 12, 15]:
            for f1, f2, f3 in combinations(key_features, 3):
                for op1, op2 in product(['multiply', 'divide', 'add'], repeat=2):
                    for threshold in [1.0, 2.0, 3.0]:
                        patterns.append({
                            'id': pattern_id,
                            'type': 'triple_combo',
                            'window': window,
                            'features': [f1, f2, f3],
                            'operators': [op1, op2],
                            'threshold': threshold,
                            'desc': f"({f1}_{op1}_{f2})_{op2}_{f3}_t{threshold}_w{window}"
                        })
                        pattern_id += 1
        
        # 4. TIME-WEIGHTED PATTERNS with exhaustive decay rates
        print("  - Time-weighted patterns...")
        for window in self.windows:
            for feature in self.features:
                for decay in self.decay_rates:
                    for threshold in [1.1, 1.2, 1.3, 1.5, 2.0]:
                        patterns.append({
                            'id': pattern_id,
                            'type': 'time_weighted',
                            'window': window,
                            'feature': feature,
                            'decay_rate': decay,
                            'threshold': threshold,
                            'desc': f"{feature}_decay{decay}_t{threshold}_w{window}"
                        })
                        pattern_id += 1
        
        # 5. PERCENTILE-BASED PATTERNS
        print("  - Percentile patterns...")
        for window in [5, 7, 10, 15, 20]:
            for feature in self.features:
                for percentile in self.percentiles:
                    for comparison in ['above', 'below', 'between']:
                        patterns.append({
                            'id': pattern_id,
                            'type': 'percentile',
                            'window': window,
                            'feature': feature,
                            'percentile': percentile,
                            'comparison': comparison,
                            'desc': f"{feature}_{comparison}_p{percentile}_w{window}"
                        })
                        pattern_id += 1
        
        # 6. ACCELERATION PATTERNS with multiple derivatives
        print("  - Acceleration patterns...")
        for window in [5, 7, 10, 12, 15]:
            for feature in ['volume', 'close', 'body', 'wick_ratio']:
                for derivative_order in [1, 2, 3]:  # 1st, 2nd, 3rd derivatives
                    for threshold in [0.01, 0.05, 0.1, 0.2, 0.5]:
                        patterns.append({
                            'id': pattern_id,
                            'type': 'acceleration',
                            'window': window,
                            'feature': feature,
                            'derivative_order': derivative_order,
                            'threshold': threshold,
                            'desc': f"{feature}_derivative{derivative_order}_t{threshold}_w{window}"
                        })
                        pattern_id += 1
        
        # 7. VOLATILITY REGIME PATTERNS
        print("  - Volatility regime patterns...")
        for window in self.windows:
            for lookback in [10, 20, 30, 50]:
                for ratio in [0.3, 0.5, 0.7, 1.0, 1.5, 2.0]:
                    for regime in ['low', 'high', 'expanding', 'contracting']:
                        patterns.append({
                            'id': pattern_id,
                            'type': 'volatility_regime',
                            'window': window,
                            'lookback': lookback,
                            'ratio': ratio,
                            'regime': regime,
                            'desc': f"vol_{regime}_ratio{ratio}_lookback{lookback}_w{window}"
                        })
                        pattern_id += 1
        
        # 8. CONDITIONAL MULTI-STEP PATTERNS
        print("  - Conditional multi-step...")
        key_features = ['volume', 'body', 'wick_ratio', 'close']
        for window in [5, 7, 10]:
            for f1, f2 in product(key_features, repeat=2):
                if f1 != f2:
                    for cond1, cond2 in product(['increasing', 'decreasing', 'stable'], repeat=2):
                        for threshold in [1.1, 1.5, 2.0]:
                            patterns.append({
                                'id': pattern_id,
                                'type': 'conditional',
                                'window': window,
                                'feature1': f1,
                                'feature2': f2,
                                'condition1': cond1,
                                'condition2': cond2,
                                'threshold': threshold,
                                'desc': f"IF_{f1}_{cond1}_THEN_{f2}_{cond2}_t{threshold}_w{window}"
                            })
                            pattern_id += 1
        
        # 9. RATIO PATTERNS - All possible ratios
        print("  - Ratio patterns...")
        for window in [5, 7, 10, 15]:
            for num, denom in permutations(self.features, 2):
                for threshold in self.thresholds[:8]:  # Use first 8 thresholds
                    for comparison in ['above', 'below', 'crossing']:
                        patterns.append({
                            'id': pattern_id,
                            'type': 'ratio',
                            'window': window,
                            'numerator': num,
                            'denominator': denom,
                            'threshold': threshold,
                            'comparison': comparison,
                            'desc': f"({num}/{denom})_{comparison}{threshold}_w{window}"
                        })
                        pattern_id += 1
        
        # 10. SEQUENCE PATTERNS (ordering matters)
        print("  - Sequence patterns...")
        for window in [5, 7, 10]:
            for feature in ['close', 'volume', 'body', 'wick_ratio']:
                for sequence_type in ['monotonic_up', 'monotonic_down', 'V_shape', 'inverse_V', 
                                     'ascending_peaks', 'descending_peaks']:
                    for threshold in [0.01, 0.05, 0.1]:
                        patterns.append({
                            'id': pattern_id,
                            'type': 'sequence',
                            'window': window,
                            'feature': feature,
                            'sequence_type': sequence_type,
                            'threshold': threshold,
                            'desc': f"{feature}_{sequence_type}_t{threshold}_w{window}"
                        })
                        pattern_id += 1
        
        # 11. MOVING AVERAGE CROSSOVERS with many period combinations
        print("  - MA crossover patterns...")
        short_periods = [3, 5, 7, 10, 12]
        long_periods = [10, 15, 20, 30, 50]
        for feature in ['close', 'volume', 'body']:
            for short in short_periods:
                for long in long_periods:
                    if short < long:
                        for signal_type in ['cross_above', 'cross_below', 'diverging', 'converging']:
                            patterns.append({
                                'id': pattern_id,
                                'type': 'ma_crossover',
                                'feature': feature,
                                'short_period': short,
                                'long_period': long,
                                'signal_type': signal_type,
                                'desc': f"{feature}_MA{short}_MA{long}_{signal_type}"
                            })
                            pattern_id += 1
        
        # 12. STATISTICAL PATTERNS
        print("  - Statistical patterns...")
        for window in [5, 7, 10, 15, 20]:
            for feature in self.features:
                for stat_type in ['zscore', 'mad', 'skew', 'kurtosis']:
                    for threshold in [1.0, 1.5, 2.0, 2.5, 3.0]:
                        for direction in ['above', 'below']:
                            patterns.append({
                                'id': pattern_id,
                                'type': 'statistical',
                                'window': window,
                                'feature': feature,
                                'stat_type': stat_type,
                                'threshold': threshold,
                                'direction': direction,
                                'desc': f"{feature}_{stat_type}_{direction}{threshold}_w{window}"
                            })
                            pattern_id += 1
        
        return patterns

def test_pattern_chunk(args):
    """Test a chunk of patterns"""
    patterns, db_path = args
    
    # Load data once per process
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT timestamp, open, high, low, close, volume FROM candles ORDER BY timestamp", conn)
    conn.close()
    
    # Calculate derived features
    df['body'] = abs(df['close'] - df['open'])
    df['upper_wick'] = df['high'] - df[['open', 'close']].max(axis=1)
    df['lower_wick'] = df[['open', 'close']].min(axis=1) - df['low']
    df['range'] = df['high'] - df['low']
    df['wick_ratio'] = (df['upper_wick'] + df['lower_wick']) / (df['body'] + 1e-9)
    df['body_pct'] = df['body'] / (df['range'] + 1e-9)
    
    results = []
    
    for pattern in patterns:
        try:
            signals = generate_signals(df, pattern)
            if signals is not None and len(signals) > 5:  # Minimum 5 trades
                profit, num_trades, win_rate, avg_profit, max_dd = backtest_simple(df, signals)
                
                if profit > 0:  # Only keep profitable ones
                    results.append(PatternResult(
                        pattern_id=pattern['id'],
                        pattern_description=pattern['desc'],
                        total_profit=profit,
                        num_trades=num_trades,
                        win_rate=win_rate,
                        avg_profit_per_trade=avg_profit,
                        max_drawdown=max_dd
                    ))
        except Exception as e:
            pass  # Skip failed patterns
    
    return results

def generate_signals(df, pattern):
    """Generate trading signals for a pattern"""
    ptype = pattern['type']
    
    try:
        if ptype == 'baseline_variant':
            return signals_baseline_variant(df, pattern)
        elif ptype == 'dual_interaction':
            return signals_dual_interaction(df, pattern)
        elif ptype == 'triple_combo':
            return signals_triple_combo(df, pattern)
        elif ptype == 'time_weighted':
            return signals_time_weighted(df, pattern)
        elif ptype == 'percentile':
            return signals_percentile(df, pattern)
        elif ptype == 'acceleration':
            return signals_acceleration(df, pattern)
        elif ptype == 'volatility_regime':
            return signals_volatility_regime(df, pattern)
        elif ptype == 'conditional':
            return signals_conditional(df, pattern)
        elif ptype == 'ratio':
            return signals_ratio(df, pattern)
        elif ptype == 'sequence':
            return signals_sequence(df, pattern)
        elif ptype == 'ma_crossover':
            return signals_ma_crossover(df, pattern)
        elif ptype == 'statistical':
            return signals_statistical(df, pattern)
    except:
        return None
    
    return None

def signals_baseline_variant(df, p):
    """Based on $777 winner: curr / max(window, threshold)"""
    window, feature = p['window'], p['feature']
    threshold, comparison = p['threshold'], p['comparison']
    signals = []
    
    for i in range(window, len(df)):
        window_vals = df[feature].iloc[i-window:i].values
        curr = df[feature].iloc[i]
        
        if comparison == 'divide':
            max_val = max(window_vals.max(), threshold)
            ratio = curr / max_val if max_val > 0 else 0
            if 0.2 < ratio < 0.8:  # Sweet spot from original
                signals.append(i)
        
        elif comparison == 'subtract':
            max_val = max(window_vals.max(), threshold)
            diff = curr - max_val
            if -threshold < diff < 0:
                signals.append(i)
        
        elif comparison == 'ratio':
            mean_val = window_vals.mean()
            if mean_val > 0 and abs(curr / mean_val - 1) < threshold:
                signals.append(i)
    
    return signals

def signals_dual_interaction(df, p):
    """Two features interacting"""
    window, f1, f2 = p['window'], p['feature1'], p['feature2']
    op, threshold = p['operator'], p['threshold']
    signals = []
    
    for i in range(window, len(df)):
        v1 = df[f1].iloc[i]
        v2 = df[f2].iloc[i]
        v1_avg = df[f1].iloc[i-window:i].mean()
        v2_avg = df[f2].iloc[i-window:i].mean()
        
        if op == 'multiply':
            if v1 * v2 > v1_avg * v2_avg * threshold:
                signals.append(i)
        elif op == 'divide' and v2 > 1e-9:
            if v1 / v2 > v1_avg / (v2_avg + 1e-9) * threshold:
                signals.append(i)
        elif op == 'add':
            if v1 + v2 > (v1_avg + v2_avg) * threshold:
                signals.append(i)
        elif op == 'subtract':
            if v1 - v2 > (v1_avg - v2_avg) * threshold:
                signals.append(i)
        elif op == 'max':
            if max(v1, v2) > max(v1_avg, v2_avg) * threshold:
                signals.append(i)
        elif op == 'min':
            if min(v1, v2) < min(v1_avg, v2_avg) / threshold:
                signals.append(i)
    
    return signals

def signals_triple_combo(df, p):
    """Three features combined"""
    window, features = p['window'], p['features']
    ops, threshold = p['operators'], p['threshold']
    signals = []
    
    f1, f2, f3 = features
    op1, op2 = ops
    
    for i in range(window, len(df)):
        v1, v2, v3 = df[f1].iloc[i], df[f2].iloc[i], df[f3].iloc[i]
        
        # Calculate: (f1 op1 f2) op2 f3
        if op1 == 'multiply':
            intermediate = v1 * v2
        elif op1 == 'divide':
            intermediate = v1 / (v2 + 1e-9)
        else:  # add
            intermediate = v1 + v2
        
        if op2 == 'multiply':
            result = intermediate * v3
        elif op2 == 'divide':
            result = intermediate / (v3 + 1e-9)
        else:  # add
            result = intermediate + v3
        
        # Compare to window average
        avg_result = df[f1].iloc[i-window:i].mean()
        if result > avg_result * threshold:
            signals.append(i)
    
    return signals

def signals_time_weighted(df, p):
    """Exponentially weighted patterns"""
    window, feature = p['window'], p['feature']
    decay, threshold = p['decay_rate'], p['threshold']
    signals = []
    
    for i in range(window, len(df)):
        window_data = df[feature].iloc[i-window:i].values
        weights = np.array([decay ** (window - j - 1) for j in range(window)])
        weighted_avg = np.average(window_data, weights=weights)
        
        if df[feature].iloc[i] > weighted_avg * threshold:
            signals.append(i)
    
    return signals

def signals_percentile(df, p):
    """Percentile-based signals"""
    window, feature = p['window'], p['feature']
    percentile, comparison = p['percentile'], p['comparison']
    signals = []
    
    for i in range(window, len(df)):
        window_data = df[feature].iloc[i-window:i].values
        pct_value = np.percentile(window_data, percentile)
        curr = df[feature].iloc[i]
        
        if comparison == 'above' and curr > pct_value:
            signals.append(i)
        elif comparison == 'below' and curr < pct_value:
            signals.append(i)
        elif comparison == 'between':
            p25 = np.percentile(window_data, 25)
            p75 = np.percentile(window_data, 75)
            if p25 < curr < p75:
                signals.append(i)
    
    return signals

def signals_acceleration(df, p):
    """Higher-order derivatives"""
    window, feature = p['window'], p['feature']
    order, threshold = p['derivative_order'], p['threshold']
    signals = []
    
    for i in range(window, len(df)):
        window_data = df[feature].iloc[i-window:i].values
        
        # Calculate derivative
        derivative = window_data
        for _ in range(order):
            derivative = np.diff(derivative)
        
        if len(derivative) > 0 and abs(derivative[-1]) > threshold:
            signals.append(i)
    
    return signals

def signals_volatility_regime(df, p):
    """Volatility regime detection"""
    window, lookback = p['window'], p['lookback']
    ratio, regime = p['ratio'], p['regime']
    signals = []
    
    for i in range(max(window, lookback), len(df)):
        recent_vol = df['range'].iloc[i-window:i].std()
        historical_vol = df['range'].iloc[i-lookback:i-window].std()
        
        if historical_vol > 0:
            vol_ratio = recent_vol / historical_vol
            
            if regime == 'low' and vol_ratio < 1 / ratio:
                signals.append(i)
            elif regime == 'high' and vol_ratio > ratio:
                signals.append(i)
            elif regime == 'expanding' and vol_ratio > ratio:
                signals.append(i)
            elif regime == 'contracting' and vol_ratio < 1 / ratio:
                signals.append(i)
    
    return signals

def signals_conditional(df, p):
    """IF-THEN patterns"""
    window = p['window']
    f1, f2 = p['feature1'], p['feature2']
    c1, c2 = p['condition1'], p['condition2']
    threshold = p['threshold']
    signals = []
    
    for i in range(window, len(df)):
        data1 = df[f1].iloc[i-window:i].values
        data2 = df[f2].iloc[i-window:i].values
        
        # Check condition 1
        cond1_met = False
        if c1 == 'increasing':
            cond1_met = np.all(np.diff(data1) > 0)
        elif c1 == 'decreasing':
            cond1_met = np.all(np.diff(data1) < 0)
        elif c1 == 'stable':
            cond1_met = np.std(data1) < np.mean(data1) * 0.1
        
        # If condition 1 met, check condition 2
        if cond1_met:
            if c2 == 'increasing' and np.all(np.diff(data2) > 0):
                if df[f2].iloc[i] > np.mean(data2) * threshold:
                    signals.append(i)
            elif c2 == 'decreasing' and np.all(np.diff(data2) < 0):
                if df[f2].iloc[i] < np.mean(data2) / threshold:
                    signals.append(i)
    
    return signals

def signals_ratio(df, p):
    """Ratio patterns"""
    window = p['window']
    num, denom = p['numerator'], p['denominator']
    threshold, comparison = p['threshold'], p['comparison']
    signals = []
    
    for i in range(window, len(df)):
        num_val = df[num].iloc[i]
        denom_val = df[denom].iloc[i]
        
        if denom_val > 1e-9:
            ratio = num_val / denom_val
            avg_ratio = (df[num].iloc[i-window:i] / (df[denom].iloc[i-window:i] + 1e-9)).mean()
            
            if comparison == 'above' and ratio > avg_ratio * threshold:
                signals.append(i)
            elif comparison == 'below' and ratio < avg_ratio / threshold:
                signals.append(i)
            elif comparison == 'crossing':
                if i > window and ratio > threshold and (df[num].iloc[i-1] / (df[denom].iloc[i-1] + 1e-9)) < threshold:
                    signals.append(i)
    
    return signals

def signals_sequence(df, p):
    """Sequence shape patterns"""
    window, feature = p['window'], p['feature']
    seq_type, threshold = p['sequence_type'], p['threshold']
    signals = []
    
    for i in range(window, len(df)):
        data = df[feature].iloc[i-window:i].values
        
        if seq_type == 'monotonic_up':
            if np.all(np.diff(data) > threshold):
                signals.append(i)
        elif seq_type == 'monotonic_down':
            if np.all(np.diff(data) < -threshold):
                signals.append(i)
        elif seq_type == 'V_shape':
            mid = window // 2
            if np.all(np.diff(data[:mid]) < 0) and np.all(np.diff(data[mid:]) > 0):
                signals.append(i)
        elif seq_type == 'inverse_V':
            mid = window // 2
            if np.all(np.diff(data[:mid]) > 0) and np.all(np.diff(data[mid:]) < 0):
                signals.append(i)
    
    return signals

def signals_ma_crossover(df, p):
    """Moving average crossovers"""
    feature = p['feature']
    short, long = p['short_period'], p['long_period']
    signal_type = p['signal_type']
    signals = []
    
    # Calculate MAs
    ma_short = df[feature].rolling(short).mean()
    ma_long = df[feature].rolling(long).mean()
    
    for i in range(long, len(df)):
        if signal_type == 'cross_above':
            if ma_short.iloc[i] > ma_long.iloc[i] and ma_short.iloc[i-1] <= ma_long.iloc[i-1]:
                signals.append(i)
        elif signal_type == 'cross_below':
            if ma_short.iloc[i] < ma_long.iloc[i] and ma_short.iloc[i-1] >= ma_long.iloc[i-1]:
                signals.append(i)
        elif signal_type == 'diverging':
            if abs(ma_short.iloc[i] - ma_long.iloc[i]) > abs(ma_short.iloc[i-1] - ma_long.iloc[i-1]):
                signals.append(i)
        elif signal_type == 'converging':
            if abs(ma_short.iloc[i] - ma_long.iloc[i]) < abs(ma_short.iloc[i-1] - ma_long.iloc[i-1]):
                signals.append(i)
    
    return signals

def signals_statistical(df, p):
    """Statistical anomaly detection"""
    window, feature = p['window'], p['feature']
    stat_type, threshold = p['stat_type'], p['threshold']
    direction = p['direction']
    signals = []
    
    for i in range(window, len(df)):
        data = df[feature].iloc[i-window:i].values
        curr = df[feature].iloc[i]
        
        if stat_type == 'zscore':
            mean, std = data.mean(), data.std()
            if std > 0:
                zscore = (curr - mean) / std
                if direction == 'above' and zscore > threshold:
                    signals.append(i)
                elif direction == 'below' and zscore < -threshold:
                    signals.append(i)
        
        elif stat_type == 'mad':  # Median absolute deviation
            median = np.median(data)
            mad = np.median(np.abs(data - median))
            if mad > 0:
                score = abs(curr - median) / mad
                if direction == 'above' and score > threshold:
                    signals.append(i)
    
    return signals

def backtest_simple(df, signals):
    """Fast backtest"""
    if len(signals) < 5:
        return 0, 0, 0, 0, 0
    
    balance = 10000
    position = None
    trades = []
    
    for idx in signals:
        if idx >= len(df):
            continue
        
        if position is None:
            position = {'entry': df['close'].iloc[idx], 'shares': balance / df['close'].iloc[idx]}
        else:
            exit_price = df['close'].iloc[idx]
            profit = (exit_price - position['entry']) * position['shares']
            balance += profit
            trades.append(profit)
            position = None
    
    # Close final position
    if position:
        profit = (df['close'].iloc[-1] - position['entry']) * position['shares']
        balance += profit
        trades.append(profit)
    
    if len(trades) == 0:
        return 0, 0, 0, 0, 0
    
    total_profit = balance - 10000
    num_trades = len(trades)
    wins = sum(1 for t in trades if t > 0)
    win_rate = wins / num_trades
    avg_profit = total_profit / num_trades
    max_dd = 0
    
    return total_profit, num_trades, win_rate, avg_profit, max_dd

def main():
    print("="*80)
    print("MILLION-SCALE PATTERN SEARCH - CHRONOGENESIS MODE")
    print("="*80)
    print(f"Target: Beat $777 baseline with MILLIONS of tests")
    print(f"CPU Cores: {cpu_count()}")
    print()
    
    db_path = '/home/bonsaihorn/Projects/Chad_Volume_tracker/trading_data.db'
    
    # Generate patterns
    generator = ChronogenesisPatternGenerator()
    all_patterns = generator.generate_all_patterns()
    
    print(f"✓ Generated {len(all_patterns):,} pattern combinations")
    print()
    
    # Parallel processing
    num_cores = cpu_count()
    chunk_size = len(all_patterns) // num_cores + 1
    chunks = [(all_patterns[i:i+chunk_size], db_path) for i in range(0, len(all_patterns), chunk_size)]
    
    print(f"Testing across {num_cores} cores...")
    print(f"Chunk size: ~{chunk_size:,} patterns per core")
    print()
    
    start_time = time.time()
    
    with Pool(num_cores) as pool:
        chunk_results = pool.map(test_pattern_chunk, chunks)
    
    # Flatten and sort
    all_results = []
    for chunk in chunk_results:
        all_results.extend(chunk)
    
    all_results.sort(key=lambda x: x.total_profit, reverse=True)
    
    elapsed = time.time() - start_time
    
    print(f"✓ Complete in {elapsed:.1f}s ({len(all_patterns)/elapsed:.0f} patterns/sec)")
    print(f"✓ Tested {len(all_patterns):,} patterns")
    print(f"✓ Found {len(all_results):,} profitable patterns")
    print()
    
    if len(all_results) == 0:
        print("No profitable patterns found!")
        return
    
    # Top results
    print("="*80)
    print("TOP 30 PATTERNS")
    print("="*80)
    
    for i, r in enumerate(all_results[:30], 1):
        print(f"\n#{i} - {r.pattern_description}")
        print(f"   💰 Profit: ${r.total_profit:,.2f}")
        print(f"   📊 Trades: {r.num_trades} | Win Rate: {r.win_rate*100:.1f}% | Avg: ${r.avg_profit_per_trade:.2f}")
    
    # Save results
    output_file = '/home/bonsaihorn/.openclaw/workspace/advanced_pattern_results.csv'
    results_df = pd.DataFrame([{
        'pattern_id': r.pattern_id,
        'pattern': r.pattern_description,
        'total_profit': r.total_profit,
        'num_trades': r.num_trades,
        'win_rate': r.win_rate,
        'avg_profit_per_trade': r.avg_profit_per_trade,
        'max_drawdown': r.max_drawdown
    } for r in all_results])
    results_df.to_csv(output_file, index=False)
    
    print(f"\n✓ Saved to: {output_file}")
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Patterns tested: {len(all_patterns):,}")
    print(f"Profitable patterns: {len(all_results):,}")
    print(f"Best profit: ${all_results[0].total_profit:,.2f}")
    print(f"Baseline: $777.00")
    
    winners = [r for r in all_results if r.total_profit > 777]
    print(f"\n🎯 Patterns beating $777 baseline: {len(winners)}")
    
    if len(winners) > 0:
        print(f"\n🏆 TOP 10 ABOVE BASELINE:")
        for i, r in enumerate(winners[:10], 1):
            improvement = r.total_profit - 777
            print(f"  {i}. ${r.total_profit:,.2f} (+${improvement:.2f}) - {r.pattern}")

if __name__ == '__main__':
    main()
