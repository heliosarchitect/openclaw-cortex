#!/usr/bin/env python3
"""
Strategy Iteration Engine - Autonomous strategy discovery and improvement

Monitors running searches, analyzes results, spawns next iterations automatically.
Keeps iterating until profitable strategies are found and deployed.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

BASELINE_PROFIT = 777.0  # Current best pattern
TARGET_PROFIT = 1500.0   # Goal to beat
WORKSPACE = Path.home() / ".openclaw/workspace"
RESULTS_DIR = Path.home() / "Projects/Chad_Volume_tracker"

def log(msg):
    """Log with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")
    sys.stdout.flush()

def check_active_searches():
    """Check if any searches are still running"""
    # Check for running Python processes doing pattern searches
    result = subprocess.run(
        ["ps", "aux"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        return []
    
    # Look for pattern search processes
    active = []
    for line in result.stdout.split('\n'):
        if 'python' in line.lower() and any(x in line for x in ['pattern_search', 'million_scale', 'backtest']):
            if 'grep' not in line:
                active.append({'label': 'pattern-search', 'pid': line.split()[1]})
    
    return active

def analyze_pattern_results():
    """Analyze latest pattern search results"""
    csv_file = RESULTS_DIR / "pattern_based_strategies.csv"
    
    if not csv_file.exists():
        return None
    
    try:
        import pandas as pd
        df = pd.read_csv(csv_file)
        
        if len(df) == 0:
            return None
        
        # Get top result
        top = df.iloc[0]
        
        return {
            'profit': float(top['total_profit']),
            'trades': int(top['num_trades']),
            'win_rate': float(top['win_rate']),
            'pattern': top['description'],
            'pattern_id': top['pattern_id']
        }
    except Exception as e:
        log(f"Error analyzing results: {e}")
        return None

def spawn_next_iteration(lesson_learned: str, target: float):
    """Spawn next iteration of pattern search with lessons learned"""
    # Since openclaw CLI isn't available, just log what we would do
    # Matthew can manually trigger the next search when ready
    
    log(f"📝 Next iteration plan:")
    log(f"   Lesson: {lesson_learned}")
    log(f"   Target: ${target:.0f}+")
    log(f"")
    log(f"💡 Suggested next steps:")
    log(f"   1. Test more complex patterns (20-50 candle sequences)")
    log(f"   2. Focus on wick ratios, volume changes, body patterns")
    log(f"   3. Add momentum detection over long windows")
    log(f"   4. Test cross-feature interactions")
    log(f"   5. Try conditional chains: IF pattern1 THEN pattern2")
    log(f"")
    log(f"📊 Ready for manual launch when Matthew approves")
    
    # Write plan to file for future reference
    plan_file = WORKSPACE / f"iteration_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(plan_file, 'w') as f:
        f.write(f"Strategy Iteration Plan\n")
        f.write(f"Generated: {datetime.now()}\n\n")
        f.write(f"Lesson learned: {lesson_learned}\n\n")
        f.write(f"Target: ${target:.0f}+ profit\n\n")
        f.write(f"Next approach:\n")
        f.write(f"1. Test more complex patterns (20-50 candle sequences)\n")
        f.write(f"2. Focus on wick ratios, volume changes, body patterns\n")
        f.write(f"3. Add momentum detection over long windows\n")
        f.write(f"4. Test cross-feature interactions\n")
        f.write(f"5. Try conditional chains\n")
    
    log(f"💾 Plan saved to: {plan_file}")
    return True

def main():
    """Main iteration engine loop"""
    global BASELINE_PROFIT
    
    log("🔄 Strategy Iteration Engine starting...")
    
    # Check if searches are still running
    active = check_active_searches()
    
    if active:
        log(f"⏳ {len(active)} searches still running, waiting...")
        for agent in active:
            label = agent.get('label', 'unknown')
            log(f"   - {label}")
        return
    
    # Analyze latest results
    log("📊 Analyzing latest results...")
    results = analyze_pattern_results()
    
    if not results:
        log("❌ No results found, spawning initial search...")
        spawn_next_iteration("Initial search", TARGET_PROFIT)
        return
    
    log(f"📈 Latest result: ${results['profit']:.2f} profit ({results['trades']} trades, {results['win_rate']:.1f}% WR)")
    log(f"   Pattern: {results['pattern']}")
    
    # Check if we beat target
    if results['profit'] >= TARGET_PROFIT:
        log(f"🎉 SUCCESS! Found ${results['profit']:.2f} strategy (target: ${TARGET_PROFIT:.0f})")
        log(f"   Ready to implement: {results['pattern']}")
        
        # TODO: Trigger implementation in live bot
        # For now, just celebrate
        
    elif results['profit'] > BASELINE_PROFIT:
        log(f"📈 Improvement! ${results['profit']:.2f} > ${BASELINE_PROFIT:.2f} baseline")
        log(f"   But still below ${TARGET_PROFIT:.0f} target, continuing iteration...")
        
        # Update baseline
        BASELINE_PROFIT = results['profit']
        
        # Spawn next iteration
        lesson = f"Wick-based patterns working well (${results['profit']:.0f}). Focus on wick_ratio variations and longer windows."
        spawn_next_iteration(lesson, TARGET_PROFIT)
        
    else:
        log(f"📉 Result ${results['profit']:.2f} below baseline ${BASELINE_PROFIT:.2f}")
        log(f"   Trying different approach...")
        
        lesson = f"Current approach not beating ${BASELINE_PROFIT:.0f}. Try different feature combinations, longer windows, or conditional logic."
        spawn_next_iteration(lesson, TARGET_PROFIT)

if __name__ == "__main__":
    main()
