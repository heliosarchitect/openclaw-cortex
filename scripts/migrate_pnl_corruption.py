
#!/usr/bin/env python3
"""
Migrate corrupted P&L records to clean format
"""
import json
import sqlite3
from pathlib import Path
from datetime import datetime
import logging

def migrate_corrupted_logs():
    """Migrate existing logs with NULL values"""
    log_dir = Path("logs/trades")
    if not log_dir.exists():
        print("No trade logs found to migrate")
        return
    
    fixed_count = 0
    total_count = 0
    
    for log_file in log_dir.glob("trades_*.jsonl"):
        print(f"Processing {log_file.name}...")
        
        # Read all trades
        trades = []
        with open(log_file, 'r') as f:
            for line in f:
                try:
                    trade = json.loads(line.strip())
                    total_count += 1
                    
                    # Fix NULL values
                    if trade.get('profit') is None:
                        trade['profit'] = 0.0
                        fixed_count += 1
                    
                    if trade.get('total_capital') is None:
                        trade['total_capital'] = 0.0
                        fixed_count += 1
                    
                    if trade.get('asset_total') is None:
                        trade['asset_total'] = 0.0
                        fixed_count += 1
                    
                    trades.append(trade)
                    
                except Exception as e:
                    print(f"  Error processing line: {e}")
        
        # Write back clean version
        backup_file = log_file.with_suffix('.jsonl.backup')
        log_file.rename(backup_file)
        
        with open(log_file, 'w') as f:
            for trade in trades:
                f.write(json.dumps(trade) + '\n')
        
        print(f"  Backed up to {backup_file.name}")
        print(f"  Fixed {fixed_count}/{total_count} records")
    
    print(f"Migration complete: {fixed_count} NULL values fixed")

if __name__ == "__main__":
    migrate_corrupted_logs()
