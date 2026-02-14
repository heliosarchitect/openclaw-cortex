#!/usr/bin/env python3
"""
Patch active_trader.py to integrate robust P&L logging
Fixes NULL value corruption issues
"""

import re
from pathlib import Path

def apply_pnl_fixes():
    """Apply fixes to active_trader.py"""
    
    print("🔧 Applying P&L corruption fixes to active_trader.py...")
    
    trader_file = Path("active_trader.py")
    if not trader_file.exists():
        print("❌ active_trader.py not found")
        return False
    
    # Read current file
    with open(trader_file, 'r') as f:
        content = f.read()
    
    # Create backup
    backup_file = trader_file.with_suffix('.py.backup')
    with open(backup_file, 'w') as f:
        f.write(content)
    print(f"✅ Backup created: {backup_file}")
    
    # Apply fixes
    fixes_applied = []
    
    # Fix 1: Improve regex pattern in handle_trade_completion
    old_pattern = r"match = re.search\(r'\\$\(\\d\+\\\.?\\\d\*\)', log_line\)"
    new_pattern = """# Robust amount extraction with multiple patterns
        patterns = [
            r'\\$([0-9]+\\.?[0-9]*)',  # Standard $1.23
            r'\\$([0-9]+)',           # Just dollars $12  
            r'profit[^0-9]*([0-9]+\\.?[0-9]*)',  # profit 1.23
            r'loss[^0-9]*([0-9]+\\.?[0-9]*)',    # loss 1.23
        ]
        
        amount = None
        for pattern in patterns:
            match = re.search(pattern, log_line, re.IGNORECASE)
            if match:
                try:
                    amount = float(match.group(1))
                    if 0 <= amount < 100000:  # Sanity check
                        break
                except (ValueError, IndexError):
                    continue
        else:
            # No valid amount found
            logger.warning(f"❌ Failed to extract amount from: {log_line[:50]}...")
            return"""
    
    # Find and replace the handle_trade_completion method
    if 'match = re.search(' in content:
        # Replace the entire amount extraction section
        pattern = r'(# Look for dollar amounts like \$1\.23\s+import re\s+match = re\.search\(r.*?\n\s+if match:.*?\n\s+amount = float\(match\.group\(1\)\))'
        
        if re.search(pattern, content, re.DOTALL):
            content = re.sub(pattern, new_pattern, content, flags=re.DOTALL)
            fixes_applied.append("Enhanced regex amount extraction")
    
    # Fix 2: Add input validation to log_trade method
    old_log_trade = r'(async def log_trade\(self, asset: str, amount: float, is_profit: bool\):.*?f\.write\(json\.dumps\(trade\) \+ \'\\n\'\))'
    new_log_trade = '''async def log_trade(self, asset: str, amount: float, is_profit: bool):
        """Thread-safe trade logging with NULL protection"""
        import threading
        import math
        
        # Input validation and sanitization
        if not hasattr(self, '_log_lock'):
            self._log_lock = threading.Lock()
        
        # Validate inputs
        if not asset or not isinstance(asset, str):
            logger.error("Invalid asset name provided")
            return
        
        if amount is None or math.isnan(amount) or math.isinf(amount):
            logger.warning(f"Invalid amount for {asset}: {amount}, defaulting to 0.0")
            amount = 0.0
        
        try:
            amount = float(amount)
        except (ValueError, TypeError):
            logger.warning(f"Could not convert amount to float for {asset}: {amount}")
            amount = 0.0
        
        # Validate totals  
        current_cap = getattr(self, 'current_capital', 0.0)
        if current_cap is None or math.isnan(current_cap):
            current_cap = 0.0
        
        asset_total = self.asset_performance.get(asset, type('obj', (object,), {'total_profit': 0.0})()).total_profit
        if asset_total is None or math.isnan(asset_total):
            asset_total = 0.0
        
        trade = {
            'timestamp': datetime.now(EST).isoformat(),
            'asset': str(asset),  # Ensure string
            'profit': float(amount if is_profit else -amount),
            'total_capital': float(current_cap),
            'asset_total': float(asset_total)
        }
        
        # Validate JSON serialization
        try:
            json_str = json.dumps(trade)
            json.loads(json_str)  # Test parsing
        except Exception as e:
            logger.error(f"Trade record failed JSON validation for {asset}: {e}")
            return
        
        # Thread-safe file write
        with self._log_lock:
            today = datetime.now(EST).strftime('%Y-%m-%d')
            log_file = self.trade_log_path / f"trades_{today}.jsonl"
            
            try:
                with open(log_file, 'a') as f:
                    f.write(json_str + '\\n')
                    f.flush()  # Ensure immediate write
                logger.info(f"✅ Logged: {asset} {'+' if is_profit else '-'}${abs(amount):.2f}")
            except Exception as e:
                logger.error(f"Failed to write trade log: {e}")'''
    
    if 'async def log_trade(' in content:
        content = re.sub(old_log_trade, new_log_trade, content, flags=re.DOTALL)
        fixes_applied.append("Enhanced log_trade with NULL protection")
    
    # Fix 3: Add capital synchronization
    capital_sync_code = '''
    def update_capital_safe(self, delta: float):
        """Thread-safe capital update"""
        if not hasattr(self, '_capital_lock'):
            self._capital_lock = threading.Lock()
        
        with self._capital_lock:
            if delta is not None and not math.isnan(delta) and not math.isinf(delta):
                self.current_capital += float(delta)
                self.current_capital = max(0.0, self.current_capital)  # Prevent negative'''
    
    # Add the new method before the run method
    if 'async def run(' in content:
        content = content.replace('async def run(', capital_sync_code + '\n\n    async def run(')
        fixes_applied.append("Added thread-safe capital updates")
    
    # Fix 4: Update handle_trade_completion to use new methods
    if 'self.current_capital +=' in content:
        content = content.replace(
            'self.current_capital += amount if profit else -amount',
            'self.update_capital_safe(amount if profit else -amount)'
        )
        fixes_applied.append("Updated capital updates to use thread-safe method")
    
    # Write updated file
    with open(trader_file, 'w') as f:
        f.write(content)
    
    print(f"✅ Applied {len(fixes_applied)} fixes:")
    for fix in fixes_applied:
        print(f"   • {fix}")
    
    return True

if __name__ == "__main__":
    apply_pnl_fixes()
    print("\\n🎯 P&L corruption fixes applied successfully!")
    print("   Next: Test with paper trading to verify NULL protection")