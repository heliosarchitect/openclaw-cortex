#!/usr/bin/env python3
"""
ADVANCED PATTERN SEARCH - CHRONOGENESIS SCALE
Test MILLIONS of complex multi-candle patterns to beat $777 baseline
"""

import sqlite3
import pandas as pd
import numpy as np
from multiprocessing import Pool, cpu_count
from itertools import product, combinations
import time
from dataclasses import dataclass
from typing import List, Callable, Tuple
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

class AdvancedPatternGenerator:
    """Generate millions of complex pattern combinations"""
    
    def __init__(self):
        # Features to track
        self.features = ['close', 'high', 'low', 'open', 'volume', 
                        'body', 'upper_wick', 'lower_wick', 'wick_ratio',
                        'body_pct', 'range']
        
        # Window sizes for sequences
        self.window_sizes = [5, 7, 10, 12, 15, 20]
        
        # Comparison operators
        self.comparisons = ['increasing', 'decreasing', 'stable', 
                           'accelerating', 'decelerating', 'reversing']
        
        # Conditional operators
        self.conditions = ['AND', 'OR', 'THEN']
        
        # Thresholds
        self.thresholds = [0.5, 1.0, 1.5, 2.0, 3.0, 5.0]
        
    def generate_sequence_patterns(self):
        """Generate sequential pattern tests"""
        patterns = []
        pattern_id = 0
        
        # 1. SIMPLE TRENDS (baseline expansion)
        for window in self.window_sizes:
            for feature in self.features:
                for comparison in self.comparisons[:3]:  # increasing/decreasing/stable
                    patterns.append({
                        'id': pattern_id,
                        'type': 'trend',
                        'window': window,
                        'feature': feature,
                        'comparison': comparison,
                        'desc': f"{feature}_{comparison}_{window}candles"
                    })
                    pattern_id += 1
        
        # 2. MOMENTUM PATTERNS (acceleration/deceleration)
        for window in self.window_sizes:
            for feature in ['volume', 'body', 'wick_ratio', 'close']:
                for momentum in ['accelerating', 'decelerating']:
                    patterns.append({
                        'id': pattern_id,
                        'type': 'momentum',
                        'window': window,
                        'feature': feature,
                        'comparison': momentum,
                        'desc': f"{feature}_{momentum}_{window}candles"
                    })
                    pattern_id += 1
        
        # 3. REVERSAL PATTERNS
        for window in [5, 7, 10]:
            for feature in self.features:
                patterns.append({
                    'id': pattern_id,
                    'type': 'reversal',
                    'window': window,
                    'feature': feature,
                    'desc': f"{feature}_reversal_after_{window}candles"
                })
                pattern_id += 1
        
        # 4. CONDITIONAL PATTERNS (IF-THEN)
        for window in [5, 7, 10]:
            for feat1, feat2 in combinations(['volume', 'body', 'wick_ratio', 'upper_wick', 'lower_wick'], 2):
                for cond1, cond2 in product(['increasing', 'decreasing'], repeat=2):
                    patterns.append({
                        'id': pattern_id,
                        'type': 'conditional',
                        'window': window,
                        'feature': feat1,
                        'feature2': feat2,
                        'comparison': cond1,
                        'comparison2': cond2,
                        'desc': f"IF_{feat1}_{cond1}_{window}_THEN_{feat2}_{cond2}"
                    })
                    pattern_id += 1
        
        # 5. MULTI-FEATURE AND PATTERNS
        for window in [5, 7, 10, 15]:
            for feat1, feat2, feat3 in combinations(['volume', 'body', 'upper_wick', 'lower_wick', 'wick_ratio'], 3):
                for comp1, comp2, comp3 in product(['increasing', 'decreasing'], repeat=3):
                    patterns.append({
                        'id': pattern_id,
                        'type': 'multi_and',
                        'window': window,
                        'features': [feat1, feat2, feat3],
                        'comparisons': [comp1, comp2, comp3],
                        'desc': f"{feat1}_{comp1}_AND_{feat2}_{comp2}_AND_{feat3}_{comp3}_{window}candles"
                    })
                    pattern_id += 1
        
        # 6. FEATURE INTERACTIONS (multiplication, division, ratio changes)
        for window in [5, 7, 10]:
            for feat1, feat2 in combinations(['volume', 'body', 'wick_ratio', 'upper_wick'], 2):
                for interaction in ['multiply', 'divide', 'ratio_change']:
                    for threshold in self.thresholds:
                        patterns.append({
                            'id': pattern_id,
                            'type': 'interaction',
                            'window': window,
                            'feature': feat1,
                            'feature2': feat2,
                            'interaction': interaction,
                            'threshold': threshold,
                            'desc': f"({feat1}_{interaction}_{feat2})_threshold_{threshold}_{window}candles"
                        })
                        pattern_id += 1
        
        # 7. TIME DECAY PATTERNS
        for window in [7, 10, 15]:
            for feature in ['volume', 'body', 'wick_ratio']:
                for decay_rate in [0.5, 0.7, 0.9]:
                    patterns.append({
                        'id': pattern_id,
                        'type': 'time_decay',
                        'window': window,
                        'feature': feature,
                        'decay_rate': decay_rate,
                        'desc': f"{feature}_time_decay_{decay_rate}_{window}candles"
                    })
                    pattern_id += 1
        
        # 8. VOLATILITY EXPANSION/CONTRACTION
        for window in [5, 10, 15, 20]:
            for pattern_type in ['expansion', 'contraction', 'squeeze']:
                patterns.append({
                    'id': pattern_id,
                    'type': 'volatility',
                    'window': window,
                    'pattern': pattern_type,
                    'desc': f"volatility_{pattern_type}_{window}candles"
                })
                pattern_id += 1
        
        # 9. WICK DIVERGENCE PATTERNS (upper rising while lower falling, etc.)
        for window in [5, 7, 10]:
            for upper_trend, lower_trend in product(['increasing', 'decreasing'], repeat=2):
                if upper_trend != lower_trend:  # Only divergences
                    patterns.append({
                        'id': pattern_id,
                        'type': 'wick_divergence',
                        'window': window,
                        'upper_trend': upper_trend,
                        'lower_trend': lower_trend,
                        'desc': f"upper_wick_{upper_trend}_lower_wick_{lower_trend}_{window}candles"
                    })
                    pattern_id += 1
        
        # 10. COMPLEX COMBOS (building on $777 winner)
        # Base winner was: curr.wick_ratio / max(wick_ratio, 3)
        for window in [5, 7, 10]:
            for divisor_threshold in [2.0, 3.0, 4.0, 5.0]:
                for feature in ['wick_ratio', 'body', 'volume']:
                    patterns.append({
                        'id': pattern_id,
                        'type': 'baseline_variant',
                        'window': window,
                        'feature': feature,
                        'threshold': divisor_threshold,
                        'desc': f"curr_{feature}_div_max_{feature}_{divisor_threshold}_{window}window"
                    })
                    pattern_id += 1
        
        return patterns

def test_pattern_batch(args):
    """Test a batch of patterns - runs in parallel"""
    patterns, db_path = args
    
    # Load data
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("""
        SELECT timestamp, open, high, low, close, volume,
               body, upper_wick, lower_wick, wick_ratio, body_pct, range
        FROM candles 
        ORDER BY timestamp
    """, conn)
    conn.close()
    
    results = []
    
    for pattern in patterns:
        try:
            signals = test_pattern(df, pattern)
            if signals is not None and len(signals) > 0:
                profit, num_trades, win_rate, avg_profit, max_dd = backtest_signals(df, signals)
                
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
            # Skip failed patterns
            pass
    
    return results

def test_pattern(df, pattern):
    """Test a specific pattern and return signal indices"""
    window = pattern['window']
    signals = []
    
    try:
        if pattern['type'] == 'trend':
            signals = test_trend_pattern(df, pattern)
        elif pattern['type'] == 'momentum':
            signals = test_momentum_pattern(df, pattern)
        elif pattern['type'] == 'reversal':
            signals = test_reversal_pattern(df, pattern)
        elif pattern['type'] == 'conditional':
            signals = test_conditional_pattern(df, pattern)
        elif pattern['type'] == 'multi_and':
            signals = test_multi_and_pattern(df, pattern)
        elif pattern['type'] == 'interaction':
            signals = test_interaction_pattern(df, pattern)
        elif pattern['type'] == 'time_decay':
            signals = test_time_decay_pattern(df, pattern)
        elif pattern['type'] == 'volatility':
            signals = test_volatility_pattern(df, pattern)
        elif pattern['type'] == 'wick_divergence':
            signals = test_wick_divergence_pattern(df, pattern)
        elif pattern['type'] == 'baseline_variant':
            signals = test_baseline_variant_pattern(df, pattern)
    except:
        return None
    
    return signals

def test_trend_pattern(df, pattern):
    """Test simple trend patterns"""
    window = pattern['window']
    feature = pattern['feature']
    comparison = pattern['comparison']
    signals = []
    
    for i in range(window, len(df)):
        window_data = df[feature].iloc[i-window:i].values
        
        if comparison == 'increasing':
            if np.all(np.diff(window_data) > 0):
                signals.append(i)
        elif comparison == 'decreasing':
            if np.all(np.diff(window_data) < 0):
                signals.append(i)
        elif comparison == 'stable':
            if np.std(window_data) < np.mean(window_data) * 0.01:
                signals.append(i)
    
    return signals

def test_momentum_pattern(df, pattern):
    """Test acceleration/deceleration patterns"""
    window = pattern['window']
    feature = pattern['feature']
    comparison = pattern['comparison']
    signals = []
    
    for i in range(window, len(df)):
        window_data = df[feature].iloc[i-window:i].values
        
        # Calculate first and second derivatives
        first_diff = np.diff(window_data)
        second_diff = np.diff(first_diff)
        
        if comparison == 'accelerating':
            if np.all(second_diff > 0):  # Acceleration
                signals.append(i)
        elif comparison == 'decelerating':
            if np.all(second_diff < 0):  # Deceleration
                signals.append(i)
    
    return signals

def test_reversal_pattern(df, pattern):
    """Test reversal patterns"""
    window = pattern['window']
    feature = pattern['feature']
    signals = []
    
    for i in range(window, len(df)):
        window_data = df[feature].iloc[i-window:i].values
        
        # Check if first half decreasing and second half increasing (or vice versa)
        mid = window // 2
        first_half = window_data[:mid]
        second_half = window_data[mid:]
        
        first_trend = np.mean(np.diff(first_half))
        second_trend = np.mean(np.diff(second_half))
        
        # Reversal: opposite signs and significant magnitude
        if first_trend * second_trend < 0 and abs(first_trend - second_trend) > 0:
            signals.append(i)
    
    return signals

def test_conditional_pattern(df, pattern):
    """Test IF-THEN conditional patterns"""
    window = pattern['window']
    feat1 = pattern['feature']
    feat2 = pattern['feature2']
    comp1 = pattern['comparison']
    comp2 = pattern['comparison2']
    signals = []
    
    for i in range(window, len(df)):
        window_data1 = df[feat1].iloc[i-window:i].values
        window_data2 = df[feat2].iloc[i-window:i].values
        
        # Check condition 1
        cond1_met = False
        if comp1 == 'increasing' and np.all(np.diff(window_data1) > 0):
            cond1_met = True
        elif comp1 == 'decreasing' and np.all(np.diff(window_data1) < 0):
            cond1_met = True
        
        # If condition 1 met, check condition 2
        if cond1_met:
            if comp2 == 'increasing' and np.all(np.diff(window_data2) > 0):
                signals.append(i)
            elif comp2 == 'decreasing' and np.all(np.diff(window_data2) < 0):
                signals.append(i)
    
    return signals

def test_multi_and_pattern(df, pattern):
    """Test multi-feature AND patterns"""
    window = pattern['window']
    features = pattern['features']
    comparisons = pattern['comparisons']
    signals = []
    
    for i in range(window, len(df)):
        all_conditions_met = True
        
        for feat, comp in zip(features, comparisons):
            window_data = df[feat].iloc[i-window:i].values
            
            if comp == 'increasing':
                if not np.all(np.diff(window_data) > 0):
                    all_conditions_met = False
                    break
            elif comp == 'decreasing':
                if not np.all(np.diff(window_data) < 0):
                    all_conditions_met = False
                    break
        
        if all_conditions_met:
            signals.append(i)
    
    return signals

def test_interaction_pattern(df, pattern):
    """Test feature interaction patterns"""
    window = pattern['window']
    feat1 = pattern['feature']
    feat2 = pattern['feature2']
    interaction = pattern['interaction']
    threshold = pattern['threshold']
    signals = []
    
    for i in range(window, len(df)):
        data1 = df[feat1].iloc[i-window:i].values
        data2 = df[feat2].iloc[i-window:i].values
        
        if interaction == 'multiply':
            result = data1[-1] * data2[-1]
            avg_result = np.mean(data1 * data2)
            if result > avg_result * threshold:
                signals.append(i)
        
        elif interaction == 'divide':
            if data2[-1] != 0:
                result = data1[-1] / data2[-1]
                avg_result = np.mean(data1 / (data2 + 1e-9))
                if result > avg_result * threshold:
                    signals.append(i)
        
        elif interaction == 'ratio_change':
            if len(data1) > 1 and data2[-2] != 0 and data1[-2] != 0:
                ratio_now = data1[-1] / (data2[-1] + 1e-9)
                ratio_before = data1[-2] / (data2[-2] + 1e-9)
                if ratio_now > ratio_before * threshold:
                    signals.append(i)
    
    return signals

def test_time_decay_pattern(df, pattern):
    """Test time decay weighted patterns"""
    window = pattern['window']
    feature = pattern['feature']
    decay_rate = pattern['decay_rate']
    signals = []
    
    for i in range(window, len(df)):
        window_data = df[feature].iloc[i-window:i].values
        
        # Apply exponential decay weights (recent = more important)
        weights = np.array([decay_rate ** (window - j - 1) for j in range(window)])
        weighted_avg = np.average(window_data, weights=weights)
        
        # Signal if current value significantly above weighted average
        if window_data[-1] > weighted_avg * 1.5:
            signals.append(i)
    
    return signals

def test_volatility_pattern(df, pattern):
    """Test volatility expansion/contraction patterns"""
    window = pattern['window']
    pattern_type = pattern['pattern']
    signals = []
    
    for i in range(window * 2, len(df)):
        # Compare recent volatility to historical
        recent_range = df['range'].iloc[i-window:i].values
        historical_range = df['range'].iloc[i-window*2:i-window].values
        
        recent_vol = np.std(recent_range)
        historical_vol = np.std(historical_range)
        
        if pattern_type == 'expansion':
            if recent_vol > historical_vol * 1.5:
                signals.append(i)
        elif pattern_type == 'contraction':
            if recent_vol < historical_vol * 0.5:
                signals.append(i)
        elif pattern_type == 'squeeze':
            if recent_vol < historical_vol * 0.3:
                signals.append(i)
    
    return signals

def test_wick_divergence_pattern(df, pattern):
    """Test wick divergence patterns"""
    window = pattern['window']
    upper_trend = pattern['upper_trend']
    lower_trend = pattern['lower_trend']
    signals = []
    
    for i in range(window, len(df)):
        upper_wicks = df['upper_wick'].iloc[i-window:i].values
        lower_wicks = df['lower_wick'].iloc[i-window:i].values
        
        upper_increasing = np.all(np.diff(upper_wicks) > 0)
        upper_decreasing = np.all(np.diff(upper_wicks) < 0)
        lower_increasing = np.all(np.diff(lower_wicks) > 0)
        lower_decreasing = np.all(np.diff(lower_wicks) < 0)
        
        if upper_trend == 'increasing' and upper_increasing:
            if lower_trend == 'decreasing' and lower_decreasing:
                signals.append(i)
        elif upper_trend == 'decreasing' and upper_decreasing:
            if lower_trend == 'increasing' and lower_increasing:
                signals.append(i)
    
    return signals

def test_baseline_variant_pattern(df, pattern):
    """Test variants of the $777 baseline winner"""
    window = pattern['window']
    feature = pattern['feature']
    threshold = pattern['threshold']
    signals = []
    
    for i in range(window, len(df)):
        window_data = df[feature].iloc[i-window:i].values
        curr_value = df[feature].iloc[i]
        
        # Baseline: curr.feature / max(feature, threshold)
        max_value = max(window_data.max(), threshold)
        ratio = curr_value / max_value
        
        # Signal if ratio in optimal range (based on $777 winner)
        if 0.2 < ratio < 0.8:
            signals.append(i)
    
    return signals

def backtest_signals(df, signals):
    """Backtest trading signals"""
    if len(signals) == 0:
        return 0, 0, 0, 0, 0
    
    balance = 10000
    position = None
    trades = []
    equity_curve = [balance]
    
    for signal_idx in signals:
        if signal_idx >= len(df):
            continue
        
        if position is None:
            # Enter position
            entry_price = df['close'].iloc[signal_idx]
            position = {
                'entry_price': entry_price,
                'entry_idx': signal_idx,
                'shares': balance / entry_price
            }
        else:
            # Exit position
            exit_price = df['close'].iloc[signal_idx]
            profit = (exit_price - position['entry_price']) * position['shares']
            balance += profit
            
            trades.append({
                'profit': profit,
                'return_pct': (exit_price / position['entry_price'] - 1) * 100
            })
            
            equity_curve.append(balance)
            position = None
    
    # Close any open position
    if position is not None:
        exit_price = df['close'].iloc[-1]
        profit = (exit_price - position['entry_price']) * position['shares']
        balance += profit
        trades.append({'profit': profit})
        equity_curve.append(balance)
    
    if len(trades) == 0:
        return 0, 0, 0, 0, 0
    
    total_profit = balance - 10000
    num_trades = len(trades)
    wins = sum(1 for t in trades if t['profit'] > 0)
    win_rate = wins / num_trades if num_trades > 0 else 0
    avg_profit = total_profit / num_trades
    
    # Calculate max drawdown
    peak = equity_curve[0]
    max_dd = 0
    for equity in equity_curve:
        if equity > peak:
            peak = equity
        dd = (peak - equity) / peak
        if dd > max_dd:
            max_dd = dd
    
    return total_profit, num_trades, win_rate, avg_profit, max_dd

def main():
    print("="*80)
    print("ADVANCED PATTERN SEARCH - CHRONOGENESIS SCALE")
    print("="*80)
    print(f"Target: Beat $777 baseline")
    print(f"CPU Cores: {cpu_count()}")
    print()
    
    db_path = '/home/bonsaihorn/Projects/Chad_Volume_tracker/trading_data.db'
    
    # Generate all patterns
    print("Generating pattern combinations...")
    generator = AdvancedPatternGenerator()
    all_patterns = generator.generate_sequence_patterns()
    print(f"✓ Generated {len(all_patterns):,} pattern combinations")
    print()
    
    # Split into batches for parallel processing
    num_cores = cpu_count()
    batch_size = len(all_patterns) // num_cores + 1
    batches = []
    
    for i in range(0, len(all_patterns), batch_size):
        batch = all_patterns[i:i+batch_size]
        batches.append((batch, db_path))
    
    print(f"Testing patterns across {num_cores} cores...")
    print(f"Batch size: ~{batch_size:,} patterns per core")
    print()
    
    start_time = time.time()
    
    # Parallel processing
    with Pool(num_cores) as pool:
        batch_results = pool.map(test_pattern_batch, batches)
    
    # Flatten results
    all_results = []
    for batch_result in batch_results:
        all_results.extend(batch_result)
    
    elapsed = time.time() - start_time
    
    print(f"✓ Testing complete in {elapsed:.1f} seconds")
    print(f"✓ Tested {len(all_patterns):,} patterns")
    print(f"✓ Found {len(all_results):,} patterns with trades")
    print()
    
    if len(all_results) == 0:
        print("No profitable patterns found!")
        return
    
    # Sort by profit
    all_results.sort(key=lambda x: x.total_profit, reverse=True)
    
    # Show top results
    print("="*80)
    print("TOP 20 PATTERNS")
    print("="*80)
    
    for i, result in enumerate(all_results[:20], 1):
        print(f"\n#{i} - {result.pattern_description}")
        print(f"   Profit: ${result.total_profit:,.2f}")
        print(f"   Trades: {result.num_trades}")
        print(f"   Win Rate: {result.win_rate*100:.1f}%")
        print(f"   Avg Profit/Trade: ${result.avg_profit_per_trade:.2f}")
        print(f"   Max Drawdown: {result.max_drawdown*100:.1f}%")
    
    # Save to CSV
    output_file = '/home/bonsaihorn/.openclaw/workspace/advanced_pattern_results.csv'
    
    results_df = pd.DataFrame([
        {
            'pattern_id': r.pattern_id,
            'pattern': r.pattern_description,
            'total_profit': r.total_profit,
            'num_trades': r.num_trades,
            'win_rate': r.win_rate,
            'avg_profit_per_trade': r.avg_profit_per_trade,
            'max_drawdown': r.max_drawdown
        }
        for r in all_results
    ])
    
    results_df.to_csv(output_file, index=False)
    print(f"\n✓ Results saved to: {output_file}")
    
    # Summary stats
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Patterns tested: {len(all_patterns):,}")
    print(f"Patterns with trades: {len(all_results):,}")
    print(f"Best profit: ${all_results[0].total_profit:,.2f}")
    print(f"Baseline to beat: $777.00")
    
    if all_results[0].total_profit > 777:
        print(f"\n🎉 NEW RECORD! Beat baseline by ${all_results[0].total_profit - 777:.2f}")
    else:
        print(f"\n⚠️  Best result still below baseline")
    
    print(f"\nPatterns above $777:")
    winners = [r for r in all_results if r.total_profit > 777]
    print(f"  {len(winners)} patterns")
    
    if len(winners) > 0:
        print(f"\nTop 5 Above Baseline:")
        for i, r in enumerate(winners[:5], 1):
            print(f"  {i}. ${r.total_profit:,.2f} - {r.pattern}")

if __name__ == '__main__':
    main()
