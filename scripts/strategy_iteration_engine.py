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
    """Check if any sub-agents are still running"""
    result = subprocess.run(
        ["openclaw", "sessions", "list", "--json"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        return []
    
    try:
        data = json.loads(result.stdout)
        subagents = [s for s in data.get('sessions', []) if 'subagent' in s.get('key', '')]
        active = [s for s in subagents if s.get('updatedAt', 0) > (datetime.now().timestamp() - 600) * 1000]
        return active
    except:
        return []

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
    task = f"""Continue iterating on pattern-based strategies. Previous best: ${BASELINE_PROFIT:.0f}.

**Lesson learned:** {lesson_learned}

**New approach:**
1. Test even MORE complex patterns (20-50 candle sequences)
2. Focus on what worked: wick ratios, volume changes, body patterns
3. Add momentum detection: acceleration/deceleration over long windows
4. Test cross-feature interactions: (feature_A_change × feature_B_change) / feature_C
5. Conditional chains: IF pattern1 for N candles THEN pattern2 → trade

**Target:** ${target:.0f}+ profit on 69-day ETH-USD backtest

**Database:** ~/Projects/Chad_Volume_tracker/trading_data.db (98,937 candles)

Use ALL 32 cores. Test MILLIONS of patterns. Scale to Chronogenesis numbers.

Output to: iteration_{datetime.now().strftime('%Y%m%d_%H%M%S')}_results.csv
"""
    
    result = subprocess.run(
        ["openclaw", "spawn", "--task", task, "--label", f"iteration-{datetime.now().strftime('%H%M%S')}"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        log(f"✅ Spawned next iteration targeting ${target:.0f}")
        return True
    else:
        log(f"❌ Failed to spawn iteration: {result.stderr}")
        return False

def main():
    """Main iteration engine loop"""
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
        global BASELINE_PROFIT
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
