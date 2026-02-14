#!/usr/bin/env python3
"""
Direct test of P&L fixes without complex exec() 
"""

import tempfile
import json
import threading
import time
from pathlib import Path
from datetime import datetime
from robust_trade_logger import RobustTradeLogger

def test_null_protection():
    """Test NULL value protection"""
    print("🧪 Testing NULL protection...")
    
    temp_dir = tempfile.mkdtemp()
    logger = RobustTradeLogger(temp_dir)
    
    # Test cases that should work
    test_cases = [
        ("ETH-USD", 10.5, True, 1000.0, 50.0),    # Normal
        ("SOL-USD", None, True, 1000.0, 50.0),    # NULL amount  
        ("DOGE-USD", float('nan'), False, 1000.0, 50.0),  # NaN amount
        ("ADA-USD", 5.0, True, None, 50.0),       # NULL total_capital
        ("BTC-USD", 5.0, True, 1000.0, None),     # NULL asset_total
    ]
    
    success_count = 0
    for asset, amount, is_profit, total_cap, asset_total in test_cases:
        result = logger.log_trade(asset, amount, is_profit, total_cap, asset_total)
        if result:
            success_count += 1
            print(f"  ✅ {asset}: amount={amount}, profit={is_profit}")
        else:
            print(f"  ❌ {asset}: Failed")
    
    print(f"Passed: {success_count}/{len(test_cases)}")
    return success_count == len(test_cases)

def test_concurrent_logging():
    """Test thread-safe logging"""
    print("🧪 Testing concurrent logging...")
    
    temp_dir = tempfile.mkdtemp()
    logger = RobustTradeLogger(temp_dir)
    
    num_threads = 5
    trades_per_thread = 10
    
    def write_trades(thread_id):
        for i in range(trades_per_thread):
            logger.log_trade(f"TEST-{thread_id}", i * 0.1, True, 1000.0, 50.0)
            time.sleep(0.001)
    
    threads = []
    for i in range(num_threads):
        thread = threading.Thread(target=write_trades, args=(i,))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    # Check results
    today = datetime.now().strftime('%Y-%m-%d')
    log_file = Path(temp_dir) / f"trades_{today}.jsonl"
    
    if log_file.exists():
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        expected = num_threads * trades_per_thread
        actual = len(lines)
        print(f"  Expected: {expected}, Got: {actual}")
        
        # Validate JSON
        json_errors = 0
        for line in lines:
            try:
                json.loads(line.strip())
            except:
                json_errors += 1
        
        print(f"  JSON errors: {json_errors}")
        return actual == expected and json_errors == 0
    else:
        print("  ❌ No log file created")
        return False

def test_amount_extraction():
    """Test regex amount extraction"""
    print("🧪 Testing amount extraction...")
    
    temp_dir = tempfile.mkdtemp()
    logger = RobustTradeLogger(temp_dir)
    
    test_cases = [
        ("💰 PROFIT $1.23 on SOL-USD", 1.23),
        ("✅ PROFIT made $5.67 today", 5.67), 
        ("📉 LOSS of $2.45", 2.45),
        ("profit 10.50 achieved", 10.50),
        ("$99.99", 99.99),
    ]
    
    success_count = 0
    for line, expected in test_cases:
        result = logger.extract_amount_from_log(line)
        if result is not None and abs(result - expected) < 0.01:
            print(f"  ✅ '{line[:30]}...' → ${result:.2f}")
            success_count += 1
        else:
            print(f"  ❌ '{line[:30]}...' → {result} (expected {expected})")
    
    print(f"Passed: {success_count}/{len(test_cases)}")
    return success_count == len(test_cases)

def run_all_tests():
    """Run all direct tests"""
    print("🚀 Running direct P&L corruption tests...")
    
    tests = [
        test_null_protection,
        test_concurrent_logging, 
        test_amount_extraction
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
                print("✅ PASSED\n")
            else:
                print("❌ FAILED\n")
        except Exception as e:
            print(f"❌ ERROR: {e}\n")
    
    print(f"🎯 SUMMARY: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("✅ All P&L corruption fixes are working correctly!")
        return True
    else:
        print("❌ Some fixes need attention")
        return False

if __name__ == "__main__":
    run_all_tests()