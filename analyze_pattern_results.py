#!/usr/bin/env python3
"""
Analyze pattern search results to find common winning characteristics
"""

import pandas as pd
import re
from collections import Counter

def extract_pattern_features(pattern_str):
    """Extract features from pattern description"""
    features = {
        'window': None,
        'features_used': [],
        'operators': [],
        'thresholds': [],
        'pattern_type': None
    }
    
    # Extract window size
    window_match = re.search(r'(\d+)candles?|w(\d+)|window', pattern_str)
    if window_match:
        features['window'] = int(window_match.group(1) or window_match.group(2) or 0)
    
    # Extract thresholds
    threshold_matches = re.findall(r'threshold[_]?([\d.]+)|t([\d.]+)', pattern_str)
    for match in threshold_matches:
        val = match[0] or match[1]
        features['thresholds'].append(float(val))
    
    # Extract features used
    feature_keywords = ['volume', 'body', 'wick_ratio', 'upper_wick', 'lower_wick', 
                       'close', 'high', 'low', 'open', 'body_pct', 'range']
    for feat in feature_keywords:
        if feat in pattern_str.lower():
            features['features_used'].append(feat)
    
    # Extract operators
    operator_keywords = ['multiply', 'divide', 'add', 'subtract', 'ratio', 'decay', 
                        'increasing', 'decreasing', 'accelerating', 'decelerating']
    for op in operator_keywords:
        if op in pattern_str.lower():
            features['operators'].append(op)
    
    # Determine pattern type
    if 'IF' in pattern_str or 'THEN' in pattern_str:
        features['pattern_type'] = 'conditional'
    elif 'multiply' in pattern_str or 'divide' in pattern_str:
        features['pattern_type'] = 'interaction'
    elif 'decay' in pattern_str:
        features['pattern_type'] = 'time_weighted'
    elif 'increasing' in pattern_str or 'decreasing' in pattern_str:
        features['pattern_type'] = 'trend'
    elif 'MA' in pattern_str:
        features['pattern_type'] = 'ma_crossover'
    else:
        features['pattern_type'] = 'other'
    
    return features

def analyze_results(csv_path, top_n=50):
    """Analyze top performing patterns"""
    
    print("="*80)
    print("PATTERN ANALYSIS")
    print("="*80)
    print()
    
    df = pd.read_csv(csv_path)
    
    # Focus on profitable patterns
    profitable = df[df['total_profit'] > 0].copy()
    print(f"Total patterns: {len(df)}")
    print(f"Profitable patterns: {len(profitable)} ({len(profitable)/len(df)*100:.1f}%)")
    print(f"Patterns beating $777: {len(df[df['total_profit'] > 777])}")
    print()
    
    # Analyze top N
    top_patterns = df.nlargest(top_n, 'total_profit')
    
    # Extract features
    all_features = []
    for pattern in top_patterns['pattern']:
        all_features.append(extract_pattern_features(pattern))
    
    # Window size analysis
    print("="*80)
    print("WINDOW SIZE DISTRIBUTION (Top 50)")
    print("="*80)
    windows = [f['window'] for f in all_features if f['window'] is not None]
    window_counts = Counter(windows)
    for window, count in sorted(window_counts.items()):
        bar = "█" * (count * 2)
        print(f"  {window:2d} candles: {bar} ({count})")
    print()
    
    # Feature usage
    print("="*80)
    print("MOST VALUABLE FEATURES (Top 50)")
    print("="*80)
    all_features_used = []
    for f in all_features:
        all_features_used.extend(f['features_used'])
    feature_counts = Counter(all_features_used)
    for feature, count in feature_counts.most_common(10):
        bar = "█" * count
        print(f"  {feature:15s}: {bar} ({count})")
    print()
    
    # Operator usage
    print("="*80)
    print("MOST EFFECTIVE OPERATORS (Top 50)")
    print("="*80)
    all_operators = []
    for f in all_features:
        all_operators.extend(f['operators'])
    operator_counts = Counter(all_operators)
    for operator, count in operator_counts.most_common(10):
        bar = "█" * count
        print(f"  {operator:15s}: {bar} ({count})")
    print()
    
    # Pattern type distribution
    print("="*80)
    print("PATTERN TYPE DISTRIBUTION (Top 50)")
    print("="*80)
    pattern_types = [f['pattern_type'] for f in all_features]
    type_counts = Counter(pattern_types)
    for ptype, count in sorted(type_counts.items(), key=lambda x: -x[1]):
        bar = "█" * (count * 2)
        print(f"  {ptype:15s}: {bar} ({count})")
    print()
    
    # Threshold analysis
    print("="*80)
    print("THRESHOLD SWEET SPOTS (Top 50)")
    print("="*80)
    all_thresholds = []
    for f in all_features:
        all_thresholds.extend(f['thresholds'])
    if all_thresholds:
        threshold_counts = Counter(all_thresholds)
        for threshold, count in sorted(threshold_counts.items()):
            if count >= 2:
                bar = "█" * (count * 2)
                print(f"  {threshold:5.1f}: {bar} ({count})")
    print()
    
    # Win rate analysis
    print("="*80)
    print("WIN RATE vs PROFIT CORRELATION")
    print("="*80)
    high_profit = top_patterns.nlargest(10, 'total_profit')
    print("Top 10 by Profit:")
    print(f"  Avg Win Rate: {high_profit['win_rate'].mean()*100:.1f}%")
    print(f"  Avg Trades: {high_profit['num_trades'].mean():.0f}")
    print()
    
    high_wr = top_patterns.nlargest(10, 'win_rate')
    print("Top 10 by Win Rate:")
    print(f"  Avg Win Rate: {high_wr['win_rate'].mean()*100:.1f}%")
    print(f"  Avg Profit: ${high_wr['total_profit'].mean():.2f}")
    print()
    
    # Feature combinations that work
    print("="*80)
    print("WINNING FEATURE COMBINATIONS (Top 20)")
    print("="*80)
    for i, row in top_patterns.head(20).iterrows():
        features = extract_pattern_features(row['pattern'])
        if len(features['features_used']) >= 2:
            combo = " + ".join(features['features_used'][:3])
            print(f"  ${row['total_profit']:6.0f} | {combo:40s} | {row['pattern'][:50]}")
    print()
    
    # Recommendations
    print("="*80)
    print("🎯 KEY INSIGHTS")
    print("="*80)
    
    # Best window
    if windows:
        best_window = max(set(windows), key=windows.count)
        print(f"✓ Optimal window size: {best_window} candles")
    
    # Best features
    top_features = [f for f, c in feature_counts.most_common(3)]
    print(f"✓ Most valuable features: {', '.join(top_features)}")
    
    # Best operators
    top_ops = [o for o, c in operator_counts.most_common(2)]
    print(f"✓ Most effective operations: {', '.join(top_ops)}")
    
    # Best pattern type
    best_type = max(type_counts.items(), key=lambda x: x[1])[0]
    print(f"✓ Best pattern category: {best_type}")
    
    print()
    print("="*80)

if __name__ == '__main__':
    csv_path = '/home/bonsaihorn/.openclaw/workspace/advanced_pattern_results.csv'
    analyze_results(csv_path, top_n=50)
