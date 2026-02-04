#!/usr/bin/env python3
"""
Complete Multi-Asset Indicator Test
Downloads fresh data and tests HELIOS indicator across all pairs
"""

import os
import sys
import requests
import sqlite3
import math
import time
import csv
from datetime import datetime, timedelta
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

sys.path.insert(0, str(Path.home() / 'Projects/Chad2930/Chad_Profit_Bot'))
from core.coinbase_auth import CoinbaseAuth

# Config
PAIRS = ['BTC-USD', 'ETH-USD', 'DOGE-USD', 'SHIB-USD', 'SOL-USD', 'ADA-USD', 'MATIC-USD', 'AVAX-USD']
DAYS = 30
DB_FILE = 'multi_asset_data.db'
OUTPUT_CSV = 'multi_asset_indicator_results.csv'

CAPITAL = 10000
POS_SIZE = 0.10
MAKER_FEE = 0.0004
TAKER_FEE = 0.0006

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def load_env():
    env_path = Path.home() / 'Projects/Chad2930/Chad_Profit_Bot' / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    k, v = line.strip().split('=', 1)
                    os.environ[k] = v

def download_pair(pair, auth):
    """Download 1-minute candles for a pair"""
    log(f"Downloading {pair}...")
    
    end = datetime.now()
    start = end - timedelta(days=DAYS)
    
    all_candles = []
    current = start
    
    while current < end:
        chunk_end = min(current + timedelta(hours=5), end)
        
        headers = auth.get_auth_headers('GET', f'/api/v3/brokerage/products/{pair}/candles')
        params = {
            'start': int(current.timestamp()),
            'end': int(chunk_end.timestamp()),
            'granularity': 'ONE_MINUTE'
        }
        
        try:
            resp = requests.get(
                f'https://api.coinbase.com/api/v3/brokerage/products/{pair}/candles',
                headers=headers,
                params=params,
                timeout=15
            )
            
            if resp.status_code == 200:
                data = resp.json()
                if 'candles' in data:
                    all_candles.extend(data['candles'])
            elif resp.status_code == 429:
                time.sleep(2)
                continue
            
        except Exception as e:
            log(f"  {pair} error: {e}")
        
        current = chunk_end
        time.sleep(0.3)
    
    log(f"  ✅ {pair}: {len(all_candles)} candles")
    return pair, all_candles

def init_db():
    """Create database"""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    
    for pair in PAIRS:
        table = pair.replace('-', '_').lower()
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {table} (
                ts INTEGER PRIMARY KEY,
                open REAL, high REAL, low REAL, close REAL, volume REAL
            )
        """)
    
    conn.commit()
    conn.close()

def store_candles(pair, candles):
    """Store candles in DB"""
    table = pair.replace('-', '_').lower()
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    
    for c in candles:
        try:
            cur.execute(f"""
                INSERT OR REPLACE INTO {table} VALUES (?, ?, ?, ?, ?, ?)
            """, (int(c['start']), float(c['open']), float(c['high']),
                  float(c['low']), float(c['close']), float(c['volume'])))
        except:
            pass
    
    conn.commit()
    conn.close()

def calc_indicator(candles):
    """HELIOS: cos(minute) → abs(volume) → sin(body)"""
    signals = []
    
    for ts, o, h, l, c, v in candles:
        minute = datetime.fromtimestamp(ts).minute
        body = c - o
        
        t1 = math.cos(minute * math.pi / 30)
        t2 = abs(v) * t1
        body_norm = body / o if o > 0 else 0
        t3 = math.sin(body_norm * 100) * t2
        
        signals.append(t3)
    
    return signals

def backtest_pair(pair):
    """Backtest one pair"""
    table = pair.replace('-', '_').lower()
    
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM {table} ORDER BY ts ASC")
        candles = cur.fetchall()
        conn.close()
        
        if len(candles) < 100:
            return None
        
        signals = calc_indicator(candles)
        
        capital = CAPITAL
        position = None
        trades = []
        peak = capital
        max_dd = 0
        
        for i in range(5, len(candles)):
            ts, o, h, l, c, v = candles[i]
            
            sig = signals[i]
            sig_5m = sum(signals[i-4:i+1]) / 5
            div = sig - sig_5m
            
            if position is None:
                if div > 0 and sig > 0:
                    position = {
                        'entry': c,
                        'size': (capital * POS_SIZE) / c,
                        'target': c * 1.004,
                        'stop': c * 0.998
                    }
            else:
                exit_price = None
                
                if c >= position['target']:
                    exit_price = position['target']
                elif c <= position['stop']:
                    exit_price = position['stop']
                elif div < -abs(sig * 0.5):
                    exit_price = c
                
                if exit_price:
                    pnl = (exit_price - position['entry']) * position['size']
                    fees = (position['entry'] * position['size'] * MAKER_FEE +
                           exit_price * position['size'] * TAKER_FEE)
                    net_pnl = pnl - fees
                    
                    capital += net_pnl
                    trades.append(net_pnl)
                    position = None
                    
                    if capital > peak:
                        peak = capital
                    dd = (peak - capital) / peak
                    if dd > max_dd:
                        max_dd = dd
        
        if not trades:
            return None
        
        wins = [t for t in trades if t > 0]
        
        return {
            'pair': pair,
            'trades': len(trades),
            'wins': len(wins),
            'win_rate': len(wins) / len(trades),
            'pnl': sum(trades),
            'return_pct': (capital - CAPITAL) / CAPITAL * 100,
            'max_dd': max_dd,
            'final_capital': capital,
            'best': max(trades),
            'worst': min(trades)
        }
        
    except Exception as e:
        log(f"❌ {pair} backtest error: {e}")
        return None

def main():
    start_time = time.time()
    
    log("="*80)
    log("MULTI-ASSET HELIOS INDICATOR BACKTESTER")
    log("="*80)
    
    # Load credentials
    load_env()
    auth = CoinbaseAuth(
        api_key=os.getenv('CHADSQUARED_API_KEY'),
        private_key=os.getenv('CHADSQUARED_API_SECRET')
    )
    
    # Initialize DB
    log("\n📊 Phase 1: Initialize Database")
    init_db()
    
    # Download data for all pairs
    log(f"\n📥 Phase 2: Download {DAYS} days of 1-minute candles")
    
    for pair in PAIRS:
        pair_name, candles = download_pair(pair, auth)
        if candles:
            store_candles(pair_name, candles)
        time.sleep(1)  # Rate limit between pairs
    
    # Backtest all pairs in parallel
    log("\n🔬 Phase 3: Parallel Backtesting")
    
    results = []
    with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        futures = {executor.submit(backtest_pair, pair): pair for pair in PAIRS}
        
        for future in as_completed(futures):
            pair = futures[future]
            try:
                result = future.result()
                if result:
                    results.append(result)
                    log(f"✅ {result['pair']}: {result['trades']} trades, "
                        f"${result['pnl']:.2f} P&L ({result['return_pct']:.2f}%)")
                else:
                    log(f"⚠️ {pair}: No results")
            except Exception as e:
                log(f"❌ {pair}: {e}")
    
    # Save results
    log("\n💾 Phase 4: Save Results")
    
    results.sort(key=lambda r: r['pnl'], reverse=True)
    
    with open(OUTPUT_CSV, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Rank', 'Pair', 'Trades', 'Win_Rate_%', 'Net_PnL_$',
                        'Return_%', 'Max_DD_%', 'Best_Trade_$', 'Worst_Trade_$'])
        
        for i, r in enumerate(results, 1):
            writer.writerow([
                i, r['pair'], r['trades'], f"{r['win_rate']*100:.1f}",
                f"{r['pnl']:.2f}", f"{r['return_pct']:.2f}",
                f"{r['max_dd']*100:.2f}", f"{r['best']:.2f}", f"{r['worst']:.2f}"
            ])
    
    # Print summary
    log("\n" + "="*80)
    log("RESULTS SUMMARY")
    log("="*80)
    log(f"Indicator: cos(minute) → abs(volume) → sin(body)")
    log(f"Strategy: 1m+5m divergence | Capital: ${CAPITAL:,}")
    log("="*80)
    
    for i, r in enumerate(results, 1):
        log(f"{i}. {r['pair']:10s} | {r['trades']:4d} trades | "
            f"Win: {r['win_rate']*100:5.1f}% | P&L: ${r['pnl']:8.2f} | "
            f"Return: {r['return_pct']:7.2f}%")
    
    log("="*80)
    
    if results:
        total_pnl = sum(r['pnl'] for r in results)
        log(f"Total P&L (all pairs): ${total_pnl:.2f}")
        log(f"Best Performer: {results[0]['pair']} (${results[0]['pnl']:.2f})")
        log(f"Worst Performer: {results[-1]['pair']} (${results[-1]['pnl']:.2f})")
    
    log(f"\n✅ Results saved to: {OUTPUT_CSV}")
    log(f"⏱️  Total time: {time.time() - start_time:.1f}s")
    log("="*80)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("\n🛑 Stopped")
    except Exception as e:
        log(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
