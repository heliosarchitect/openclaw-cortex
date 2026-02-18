#!/usr/bin/env python3
"""
Multi-Asset Indicator Backtester V2 - Simplified & Fast
Downloads 30 days of 1-minute candles and tests HELIOS indicator
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
from dataclasses import dataclass
from typing import List, Tuple
from concurrent.futures import ProcessPoolExecutor

# Add parent directory
sys.path.insert(0, str(Path.home() / 'Projects/Chad2930/Chad_Profit_Bot'))
from core.coinbase_auth import CoinbaseAuth

# Config
PAIRS = ['BTC-USD', 'ETH-USD', 'DOGE-USD', 'SOL-USD', 'ADA-USD', 'MATIC-USD', 'AVAX-USD']
LOOKBACK_DAYS = 30  # Reduced for speed
DB_PATH = Path.home() / 'Projects/Chad_Volume_tracker' / 'multi_asset_backtest.db'
OUTPUT_CSV = 'multi_asset_indicator_results.csv'

# Trading
CAPITAL = 10000
POSITION_SIZE = 0.10
MAKER_FEE = 0.0004
TAKER_FEE = 0.0006

@dataclass
class Result:
    pair: str
    trades: int
    wins: int
    win_rate: float
    pnl: float
    return_pct: float
    sharpe: float
    max_dd: float

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

def download_pair_sync(pair: str, auth: CoinbaseAuth) -> List[dict]:
    """Synchronous download for one pair"""
    end_time = datetime.now()
    start_time = end_time - timedelta(days=LOOKBACK_DAYS)
    
    all_candles = []
    current = start_time
    
    log(f"Downloading {pair}...")
    
    while current < end_time:
        chunk_end = min(current + timedelta(hours=5), end_time)
        
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
                timeout=10
            )
            
            if resp.status_code == 200:
                data = resp.json()
                if 'candles' in data:
                    all_candles.extend(data['candles'])
            elif resp.status_code == 429:
                log(f"  {pair}: Rate limited, waiting...")
                time.sleep(2)
                continue
                
        except Exception as e:
            log(f"  {pair}: Error - {e}")
        
        current = chunk_end
        time.sleep(0.25)
    
    log(f"  ✅ {pair}: {len(all_candles)} candles")
    return all_candles

def init_db():
    """Initialize database"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
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

def store_data(pair: str, candles: List[dict]):
    """Store candles in DB"""
    table = pair.replace('-', '_').lower()
    conn = sqlite3.connect(DB_PATH)
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

def calc_indicator(candles: List[Tuple]) -> List[float]:
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

def backtest_pair(pair: str) -> Result:
    """Backtest one pair"""
    table = pair.replace('-', '_').lower()
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM {table} ORDER BY ts ASC")
        candles = cur.fetchall()
        conn.close()
        
        if len(candles) < 100:
            log(f"⚠️ {pair}: Only {len(candles)} candles")
            return None
        
        signals = calc_indicator(candles)
        
        # Trading
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
                        'size': (capital * POSITION_SIZE) / c,
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
        returns = [t / CAPITAL for t in trades]
        avg_ret = sum(returns) / len(returns)
        std_ret = (sum((r - avg_ret)**2 for r in returns) / len(returns))**0.5
        sharpe = (avg_ret / std_ret * (252**0.5)) if std_ret > 0 else 0
        
        result = Result(
            pair=pair,
            trades=len(trades),
            wins=len(wins),
            win_rate=len(wins) / len(trades),
            pnl=sum(trades),
            return_pct=(capital - CAPITAL) / CAPITAL * 100,
            sharpe=sharpe,
            max_dd=max_dd
        )
        
        return result
        
    except Exception as e:
        log(f"❌ {pair}: Backtest error - {e}")
        return None

def main():
    start = time.time()
    
    log("="*80)
    log("MULTI-ASSET HELIOS BACKTESTER V2")
    log("="*80)
    
    # Load env
    load_env()
    auth = CoinbaseAuth(
        api_key=os.getenv('CHADSQUARED_API_KEY'),
        private_key=os.getenv('CHADSQUARED_API_SECRET')
    )
    
    # Init DB
    log("\n📊 Phase 1: Initialize Database")
    init_db()
    
    # Download data
    log(f"\n📥 Phase 2: Download {LOOKBACK_DAYS} days of data")
    for pair in PAIRS:
        candles = download_pair_sync(pair, auth)
        if candles:
            store_data(pair, candles)
    
    # Backtest
    log("\n🔬 Phase 3: Parallel Backtesting")
    results = []
    
    with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        futures = [executor.submit(backtest_pair, pair) for pair in PAIRS]
        for future in futures:
            try:
                result = future.result()
                if result:
                    results.append(result)
                    log(f"✅ {result.pair}: {result.trades} trades, "
                        f"${result.pnl:.2f} P&L, {result.return_pct:.2f}% return")
            except Exception as e:
                log(f"❌ Backtest failed: {e}")
    
    # Save results
    log("\n💾 Phase 4: Save Results")
    results.sort(key=lambda r: r.pnl, reverse=True)
    
    with open(OUTPUT_CSV, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Rank', 'Pair', 'Trades', 'Win_Rate_%', 'Net_PnL_$',
                        'Return_%', 'Max_DD_%', 'Sharpe'])
        
        for i, r in enumerate(results, 1):
            writer.writerow([i, r.pair, r.trades, f"{r.win_rate*100:.1f}",
                           f"{r.pnl:.2f}", f"{r.return_pct:.2f}",
                           f"{r.max_dd*100:.2f}", f"{r.sharpe:.2f}"])
    
    # Print summary
    log("\n" + "="*80)
    log("RESULTS SUMMARY")
    log("="*80)
    log(f"Indicator: cos(minute) → abs(volume) → sin(body)")
    log(f"Strategy: 1m+5m divergence | Capital: ${CAPITAL:,} | Position: {POSITION_SIZE*100}%")
    log("="*80)
    
    for i, r in enumerate(results, 1):
        log(f"{i}. {r.pair:10s} | {r.trades:3d} trades | Win: {r.win_rate*100:5.1f}% | "
            f"P&L: ${r.pnl:7.2f} | Return: {r.return_pct:6.2f}% | Sharpe: {r.sharpe:5.2f}")
    
    log("="*80)
    log(f"Total P&L: ${sum(r.pnl for r in results):.2f}")
    log(f"Best: {results[0].pair} (${results[0].pnl:.2f})")
    log(f"Results saved to: {OUTPUT_CSV}")
    log(f"Time: {time.time() - start:.1f}s")
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
