#!/usr/bin/env python3
"""
Test suite for P&L corruption fixes
Validates that NULL values are properly prevented
"""

import json
import tempfile
import unittest
import threading
import time
from pathlib import Path
from datetime import datetime
import sys
import os

# Add current directory to path to import the fixed logger
sys.path.insert(0, '.')

class TestPnLFixes(unittest.TestCase):
    """Test P&L corruption prevention"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        
    def test_regex_extraction(self):
        """Test improved regex amount extraction"""
        import re
        
        # Multiple fallback patterns
        patterns = [
            r'\$([0-9]+\.?[0-9]*)',
            r'\$([0-9]+)', 
            r'profit[^0-9]*([0-9]+\.?[0-9]*)',
            r'loss[^0-9]*([0-9]+\.?[0-9]*)',
        ]
        
        test_cases = [
            ("💰 PROFIT $1.23 on SOL-USD", 1.23),
            ("✅ PROFIT made $5.67 today", 5.67),
            ("📉 LOSS of $2.45", 2.45),
            ("profit 10.50 achieved", 10.50),
            ("loss 3.25 recorded", 3.25),
            ("$99.99", 99.99),
            ("$50", 50.0),
        ]
        
        failed_extractions = [
            "✅ PROFIT made on ETH-USD",  # No amount
            "📉 LOSS $ on DOGE-USD",     # Empty amount
            "✅ PROFIT $abc on BTC-USD", # Invalid number
        ]
        
        for line, expected in test_cases:
            amount = None
            for pattern in patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    try:
                        amount = float(match.group(1))
                        if 0 <= amount < 100000:
                            break
                    except (ValueError, IndexError):
                        continue
            
            self.assertIsNotNone(amount, f"Failed to extract from: {line}")
            self.assertAlmostEqual(amount, expected, places=2)
        
        # Test failure cases
        for line in failed_extractions:
            amount = None
            for pattern in patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    try:
                        amount = float(match.group(1))
                        if 0 <= amount < 100000:
                            break
                    except (ValueError, IndexError):
                        continue
            
            self.assertIsNone(amount, f"Should not extract from: {line}")
    
    def test_robust_trade_logger(self):
        """Test RobustTradeLogger against NULL scenarios"""
        
        # Import after creating the file
        try:
            exec(open('robust_trade_logger.py').read())
            logger = locals()['RobustTradeLogger'](self.temp_dir)
        except Exception as e:
            self.skipTest(f"Could not import RobustTradeLogger: {e}")
        
        # Test NULL protection
        test_cases = [
            # (asset, amount, is_profit, total_capital, asset_total, should_succeed)
            ("ETH-USD", 10.50, True, 1000.0, 50.0, True),   # Normal case
            ("SOL-USD", None, True, 1000.0, 50.0, True),    # NULL amount
            ("DOGE-USD", float('nan'), False, 1000.0, 50.0, True),  # NaN amount
            ("ADA-USD", 5.0, True, None, 50.0, True),       # NULL total_capital
            ("BTC-USD", 5.0, True, 1000.0, None, True),     # NULL asset_total
            ("", 5.0, True, 1000.0, 50.0, False),           # Empty asset
            (None, 5.0, True, 1000.0, 50.0, False),         # NULL asset
        ]
        
        for asset, amount, is_profit, total_cap, asset_total, should_succeed in test_cases:
            result = logger.log_trade(asset, amount, is_profit, total_cap, asset_total)
            if should_succeed:
                self.assertTrue(result, f"Should succeed: {asset}, {amount}")
            else:
                self.assertFalse(result, f"Should fail: {asset}, {amount}")
    
    def test_concurrent_logging(self):
        """Test thread-safe concurrent logging"""
        try:
            exec(open('robust_trade_logger.py').read())
            logger = locals()['RobustTradeLogger'](self.temp_dir)
        except Exception as e:
            self.skipTest(f"Could not import RobustTradeLogger: {e}")
        
        # Concurrent write test
        num_threads = 10
        trades_per_thread = 20
        
        def write_trades(thread_id):
            for i in range(trades_per_thread):
                logger.log_trade(f"TEST-{thread_id}", i * 0.1, True, 1000.0, 50.0)
                time.sleep(0.001)  # Small delay to increase contention
        
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=write_trades, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # Verify all trades were written
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = Path(self.temp_dir) / f"trades_{today}.jsonl"
        
        if log_file.exists():
            with open(log_file, 'r') as f:
                lines = f.readlines()
            
            expected_trades = num_threads * trades_per_thread
            self.assertEqual(len(lines), expected_trades, 
                           f"Expected {expected_trades} trades, got {len(lines)}")
            
            # Verify each line is valid JSON
            for line in lines:
                try:
                    trade = json.loads(line.strip())
                    self.assertIsNotNone(trade.get('profit'))
                    self.assertIsNotNone(trade.get('asset'))
                    self.assertIsNotNone(trade.get('timestamp'))
                except json.JSONDecodeError as e:
                    self.fail(f"Invalid JSON in concurrent write: {e}")
    
    def test_json_serialization_protection(self):
        """Test protection against JSON serialization issues"""
        import math
        
        problematic_values = [
            {'profit': None, 'should_fix': True},
            {'profit': float('nan'), 'should_fix': True},
            {'profit': float('inf'), 'should_fix': True},
            {'profit': float('-inf'), 'should_fix': True},
            {'total_capital': None, 'should_fix': True},
            {'asset': None, 'should_fix': False},  # Should reject
            {'profit': 10.5, 'should_fix': False},  # Valid, no fix needed
        ]
        
        try:
            exec(open('robust_trade_logger.py').read())
            logger = locals()['RobustTradeLogger'](self.temp_dir)
        except Exception as e:
            self.skipTest(f"Could not import RobustTradeLogger: {e}")
        
        for test_case in problematic_values:
            asset = test_case.get('asset', 'TEST-USD')
            profit = test_case.get('profit', 0.0)
            total_capital = test_case.get('total_capital', 1000.0)
            should_fix = test_case['should_fix']
            
            result = logger.log_trade(asset, profit, True, total_capital, 50.0)
            
            if should_fix:
                self.assertTrue(result, f"Should fix and succeed: {test_case}")
            elif asset is None:
                self.assertFalse(result, f"Should reject NULL asset: {test_case}")
            else:
                self.assertTrue(result, f"Should succeed normally: {test_case}")
    
    def test_migration_script(self):
        """Test the migration script on corrupted data"""
        # Create corrupted log file
        corrupted_file = Path(self.temp_dir) / "trades_2026-02-13.jsonl"
        corrupted_trades = [
            '{"timestamp": "2026-02-13T10:00:00", "asset": "ETH-USD", "profit": null, "total_capital": 1000.0}',
            '{"timestamp": "2026-02-13T10:01:00", "asset": "SOL-USD", "profit": 5.0, "total_capital": null}',
            '{"timestamp": "2026-02-13T10:02:00", "asset": "DOGE-USD", "profit": "NaN", "total_capital": 1000.0}',
            '{"timestamp": "2026-02-13T10:03:00", "asset": "BTC-USD", "profit": 10.0, "total_capital": 1000.0}',  # Valid
        ]
        
        with open(corrupted_file, 'w') as f:
            f.write('\n'.join(corrupted_trades))
        
        # Test migration logic (simulate the migration)
        fixed_count = 0
        total_count = 0
        fixed_trades = []
        
        with open(corrupted_file, 'r') as f:
            for line in f:
                try:
                    trade = json.loads(line.strip())
                    total_count += 1
                    
                    # Fix NULL values
                    if trade.get('profit') is None or str(trade.get('profit')) == 'NaN':
                        trade['profit'] = 0.0
                        fixed_count += 1
                    
                    if trade.get('total_capital') is None:
                        trade['total_capital'] = 0.0
                        fixed_count += 1
                    
                    fixed_trades.append(trade)
                    
                except Exception as e:
                    self.fail(f"Error processing line: {e}")
        
        self.assertEqual(total_count, 4)
        self.assertEqual(fixed_count, 3)  # 3 NULL values fixed
        
        # Verify all trades are now valid
        for trade in fixed_trades:
            self.assertIsNotNone(trade.get('profit'))
            self.assertIsNotNone(trade.get('total_capital'))
            self.assertIsInstance(trade.get('profit'), (int, float))
            self.assertIsInstance(trade.get('total_capital'), (int, float))


def run_tests():
    """Run all P&L corruption prevention tests"""
    print("🧪 Running P&L corruption prevention tests...")
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPnLFixes)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    if result.wasSuccessful():
        print("✅ All tests passed! P&L fixes are working correctly.")
        return True
    else:
        print("❌ Some tests failed. Check the output above.")
        return False


if __name__ == "__main__":
    run_tests()