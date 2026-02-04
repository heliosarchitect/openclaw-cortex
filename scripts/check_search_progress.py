#!/usr/bin/env python3
"""Check progress of running strategy searches."""
import os
import re
from datetime import datetime

def check_infinite_generator():
    """Check progress of infinite indicator generator."""
    log_path = os.path.expanduser("~/Projects/Chad_Volume_tracker/infinite_generator.log")
    
    if not os.path.exists(log_path):
        return None
    
    with open(log_path, 'r') as f:
        log = f.read()
    
    # Check if complete
    if "Found" in log and "profitable transformations!" in log:
        # Extract results
        match = re.search(r'Found (\d+) profitable transformations!', log)
        if match:
            found = int(match.group(1))
            # Extract top result
            top_match = re.search(r'1\. Profit: \$([0-9.]+)', log)
            top_profit = float(top_match.group(1)) if top_match else 0
            
            return {
                'name': 'infinite-indicator-generator',
                'progress': 100,
                'status': 'complete',
                'found': found,
                'top_profit': top_profit
            }
    
    # Look for unique workers that have completed (1000/1000)
    workers_complete = len(re.findall(r'Worker (\d+): Tested 1000/1000', log))
    total_workers = 16
    
    if workers_complete > 0:
        pct = (workers_complete / total_workers) * 100
        return {
            'name': 'infinite-indicator-generator',
            'progress': pct,
            'workers_done': workers_complete,
            'total_workers': total_workers
        }
    
    return {'name': 'infinite-indicator-generator', 'progress': 5, 'status': 'running'}

def check_massive_search():
    """Check progress of massive strategy search."""
    # Check if output file exists
    output_path = os.path.expanduser("~/Projects/Chad_Volume_tracker/massive_strategy_results.csv")
    
    if os.path.exists(output_path):
        return {'name': 'massive-strategy-search', 'progress': 100, 'status': 'complete'}
    
    # Check process runtime as proxy for progress
    ps_output = os.popen("ps -eo pid,etime,cmd | grep 'massive_strategy_search.py' | grep -v grep | head -1").read()
    
    if not ps_output:
        return {'name': 'massive-strategy-search', 'progress': 0, 'status': 'not running'}
    
    # Parse elapsed time
    parts = ps_output.split()
    if len(parts) >= 2:
        elapsed = parts[1]  # Format: MM:SS or HH:MM:SS
        # Rough estimate: assume 60 minutes total runtime
        if ':' in elapsed:
            time_parts = elapsed.split(':')
            if len(time_parts) == 2:
                minutes = int(time_parts[0])
            else:
                minutes = int(time_parts[0]) * 60 + int(time_parts[1])
            
            # Estimate: 60 minutes expected
            pct = min((minutes / 60) * 100, 95)  # Cap at 95% until done
            return {'name': 'massive-strategy-search', 'progress': pct, 'runtime': elapsed}
    
    return {'name': 'massive-strategy-search', 'progress': 5, 'status': 'running'}

def main():
    """Check all searches and report progress."""
    print(f"🔍 Strategy Search Progress - {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60)
    
    # Check both searches
    infinite = check_infinite_generator()
    massive = check_massive_search()
    
    if infinite:
        if infinite.get('status') == 'complete':
            print(f"✅ {infinite['name']}: COMPLETE")
            print(f"   Found: {infinite.get('found', 0)} profitable transformations")
            print(f"   Top profit: ${infinite.get('top_profit', 0):.2f}")
        elif 'workers_done' in infinite:
            print(f"📊 {infinite['name']}: {infinite['progress']:.1f}%")
            print(f"   Workers: {infinite['workers_done']}/{infinite['total_workers']} complete")
        else:
            print(f"📊 {infinite['name']}: {infinite['progress']:.1f}% ({infinite.get('status', 'running')})")
    
    if massive:
        runtime = massive.get('runtime', '')
        status = massive.get('status', '')
        print(f"📊 {massive['name']}: {massive['progress']:.1f}%")
        if runtime:
            print(f"   Runtime: {runtime}")
        if status and status != 'running':
            print(f"   Status: {status}")
    
    print()
    
    # Overall summary
    if infinite and massive:
        avg_progress = (infinite['progress'] + massive['progress']) / 2
        print(f"Overall Progress: {avg_progress:.1f}%")
        
        if avg_progress >= 100:
            print("✅ All searches complete!")
        elif avg_progress >= 50:
            print("⏳ Over halfway there...")
        else:
            print("🔄 Still processing...")

if __name__ == '__main__':
    main()
