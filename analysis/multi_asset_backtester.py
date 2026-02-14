#!/usr/bin/env python3
"""
Multi-Asset Indicator Backtester
Downloads 1-minute candles for multiple crypto pairs and tests
the HELIOS winning indicator (cos(minute) → abs(volume) → sin(body))

Parallel processing for maximum speed
"""

import os
import sys
import asyncio
import sqlite3
import json
import math
import time
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Tuple
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import csv

# Add parent directory to path for imports
sys.path.insert(0, str(Path.home() / 'Projects/Chad2930/Chad_Profit_Bot'))
from core.coinbase_auth import CoinbaseAuth
from core.coinbase_client import CoinbaseClient

# Configuration
PAIRS = ['BTC-USD', 'ETH-USD', 'DOGE-USD', 'SHIB-USD', 'SOL-USD', 'ADA-USD', 'MATIC-USD', 'AVAX-USD']
LOOKBACK_DAYS = 70
DB_PATH = Path.home() / 'Projects/Chad_Volume_tracker' / 'multi_asset_data.db'
OUTPUT_CSV = Path(__file__).parent / 'multi_asset_indicator_results.csv'

# Trading parameters
INITIAL_CAPITAL = 10000
POSITION_SIZE_PCT = 0.10  # 10% of capital per trade
MAKER_FEE = 0.0004
TAKER_FEE = 0.0006

@dataclass
class Trade:
    entry_time: datetime
    exit_time: datetime
    entry_price: float
    exit_price: float
    size: float
    pnl: float
    net_pnl: float
    
@dataclass
class BacktestResult:
    pair: str
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_pnl: float
    net_pnl: float
    max_drawdown: float
    final_capital: float
    return_pct: float
    sharpe_ratio: float
    best_trade: float
    worst_trade: float

def log(msg):
    """Thread-safe logging"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] {msg}", flush=True)

def load_env():
    """Load environment variables from .env file"""
    env_path = Path.home() / 'Projects/Chad2930/Chad_Profit_Bot' / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, val = line.strip().split('=', 1)
                    os.environ[key] = val

async def download_candles(client: CoinbaseClient, product: str, start: datetime, end: datetime) -> List[Dict]:
    """Download 1-minute candles for a product"""
    all_candles = []
    
    # Coinbase API limits to 350 candles per request
    # For 1-minute candles: 350 minutes = ~5.8 hours, so chunk by 5 hours
    current = start
    chunk_size = timedelta(hours=5)
    
    while current < end:
        chunk_end = min(current + chunk_size, end)
        
        try:
            result = await client._request_v3(
                'GET',
                f'/api/v3/brokerage/products/{product}/candles',
                params={
                    'start': int(current.timestamp()),
                    'end': int(chunk_end.timestamp()),
                    'granularity': 'ONE_MINUTE'
                }
            )
            
            if 'candles' in result:
                all_candles.extend(result['candles'])
                if len(all_candles) % 1000 == 0:
                    log(f"  {product}: {len(all_candles)} candles downloaded...")
            
            await asyncio.sleep(0.2)  # Rate limiting
            
        except Exception as e:
            log(f"  {product}: Error downloading chunk: {e}")
            await asyncio.sleep(1)
        
        current = chunk_end
    
    return all_candles

def create_database():
    """Create SQLite database for multi-asset data"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create a table for each pair
    for pair in PAIRS:
        table_name = pair.replace('-', '_').lower()
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                timestamp INTEGER PRIMARY KEY,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume REAL
            )
        """)
    
    conn.commit()
    conn.close()
    log(f"✅ Database created at {DB_PATH}")

def store_candles(pair: str, candles: List[Dict]):
    """Store candles in database"""
    table_name = pair.replace('-', '_').lower()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Insert candles
    for candle in candles:
        try:
            cursor.execute(f"""
                INSERT OR REPLACE INTO {table_name} 
                (timestamp, open, high, low, close, volume)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                int(candle['start']),
                float(candle['open']),
                float(candle['high']),
                float(candle['low']),
                float(candle['close']),
                float(candle['volume'])
            ))
        except Exception as e:
            log(f"  Error inserting candle: {e}")
    
    conn.commit()
    conn.close()

async def download_all_data():
    """Download historical data for all pairs"""
    log("🚀 Starting multi-asset data download...\n")
    
    load_env()
    auth = CoinbaseAuth(
        api_key=os.getenv('CHADSQUARED_API_KEY'),
        private_key=os.getenv('CHADSQUARED_API_SECRET')
    )
    client = CoinbaseClient(auth)
    
    create_database()
    
    end_time = datetime.now()
    start_time = end_time - timedelta(days=LOOKBACK_DAYS)
    
    log(f"Downloading {LOOKBACK_DAYS} days of 1-minute candles")
    log(f"Time range: {start_time.strftime('%Y-%m-%d')} to {end_time.strftime('%Y-%m-%d')}\n")
    
    for pair in PAIRS:
        log(f"📊 Downloading {pair}...")
        candles = await download_candles(client, pair, start_time, end_time)
        
        if candles:
            store_candles(pair, candles)
            log(f"  ✅ Stored {len(candles)} candles for {pair}\n")
        else:
            log(f"  ⚠️ No candles received for {pair}\n")

def calculate_helios_indicator(candles: List[Tuple]) -> List[float]:
    """
    Calculate HELIOS indicator: cos(minute) → abs(volume) → sin(body)
    
    Transformation pipeline:
    1. cos(minute_of_hour) - time-based component
    2. abs(volume) - volume magnitude
    3. sin(body) - price movement direction
    
    Returns signal values for each candle
    """
    signals = []
    
    for timestamp, open_p, high, low, close, volume in candles:
        # Extract minute component (0-59)
        dt = datetime.fromtimestamp(timestamp)
        minute = dt.minute
        
        # Calculate body (close - open)
        body = close - open_p
        
        # Apply transformation pipeline
        # cos(minute) → maps minute to oscillating value
        t1 = math.cos(minute * math.pi / 30)  # Normalize to 0-2π range
        
        # abs(volume) → volume magnitude
        t2 = abs(volume) * t1
        
        # sin(body) → directional signal from price movement
        # Normalize body to prevent extreme values
        body_norm = body / open_p if open_p > 0 else 0
        t3 = math.sin(body_norm * 100) * t2  # Scale for sensitivity
        
        signals.append(t3)
    
    return signals

def backtest_pair(pair: str) -> BacktestResult:
    """Run backtest on a single pair using HELIOS indicator"""
    table_name = pair.replace('-', '_').lower()
    
    # Load candles from database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT timestamp, open, high, low, close, volume
        FROM {table_name}
        ORDER BY timestamp ASC
    """)
    candles = cursor.fetchall()
    conn.close()
    
    if len(candles) < 100:
        log(f"⚠️ {pair}: Insufficient data ({len(candles)} candles)")
        return None
    
    # Calculate indicator
    signals = calculate_helios_indicator(candles)
    
    # Trading logic: 1m + 5m divergence strategy
    capital = INITIAL_CAPITAL
    position = None
    trades = []
    peak_capital = capital
    max_drawdown = 0
    
    for i in range(5, len(candles)):
        timestamp, open_p, high, low, close, volume = candles[i]
        signal = signals[i]
        
        # Calculate 5-minute signal (average of last 5 signals)
        signal_5m = sum(signals[i-4:i+1]) / 5
        
        # Detect divergence: 1m vs 5m
        divergence = signal - signal_5m
        
        if position is None:
            # Entry logic: Strong positive divergence
            if divergence > 0 and signal > 0:
                position = {
                    'entry_time': datetime.fromtimestamp(timestamp),
                    'entry_price': close,
                    'size': (capital * POSITION_SIZE_PCT) / close,
                    'target': close * 1.004,  # 0.4% target
                    'stop': close * 0.998     # 0.2% stop
                }
        else:
            # Exit logic
            exit_triggered = False
            exit_price = close
            
            # Target hit
            if close >= position['target']:
                exit_triggered = True
                exit_price = position['target']
            
            # Stop hit
            elif close <= position['stop']:
                exit_triggered = True
                exit_price = position['stop']
            
            # Negative divergence reversal
            elif divergence < -abs(signal * 0.5):
                exit_triggered = True
            
            if exit_triggered:
                # Calculate P&L
                pnl = (exit_price - position['entry_price']) * position['size']
                fees = (position['entry_price'] * position['size'] * MAKER_FEE + 
                       exit_price * position['size'] * TAKER_FEE)
                net_pnl = pnl - fees
                
                capital += net_pnl
                
                trades.append(Trade(
                    entry_time=position['entry_time'],
                    exit_time=datetime.fromtimestamp(timestamp),
                    entry_price=position['entry_price'],
                    exit_price=exit_price,
                    size=position['size'],
                    pnl=pnl,
                    net_pnl=net_pnl
                ))
                
                position = None
                
                # Track drawdown
                if capital > peak_capital:
                    peak_capital = capital
                dd = (peak_capital - capital) / peak_capital
                if dd > max_drawdown:
                    max_drawdown = dd
    
    # Calculate results
    if not trades:
        log(f"⚠️ {pair}: No trades generated")
        return None
    
    winning = [t for t in trades if t.net_pnl > 0]
    losing = [t for t in trades if t.net_pnl <= 0]
    total_pnl = sum(t.pnl for t in trades)
    net_pnl = sum(t.net_pnl for t in trades)
    
    # Sharpe ratio (simplified)
    returns = [t.net_pnl / INITIAL_CAPITAL for t in trades]
    avg_return = sum(returns) / len(returns)
    std_return = (sum((r - avg_return)**2 for r in returns) / len(returns))**0.5
    sharpe = (avg_return / std_return * (252**0.5)) if std_return > 0 else 0
    
    result = BacktestResult(
        pair=pair,
        total_trades=len(trades),
        winning_trades=len(winning),
        losing_trades=len(losing),
        win_rate=len(winning) / len(trades),
        total_pnl=total_pnl,
        net_pnl=net_pnl,
        max_drawdown=max_drawdown,
        final_capital=capital,
        return_pct=(capital - INITIAL_CAPITAL) / INITIAL_CAPITAL * 100,
        sharpe_ratio=sharpe,
        best_trade=max(t.net_pnl for t in trades),
        worst_trade=min(t.net_pnl for t in trades)
    )
    
    return result

def run_backtests_parallel():
    """Run backtests on all pairs in parallel"""
    log(f"\n🔬 Running backtests on {len(PAIRS)} pairs (parallel)...\n")
    
    # Use all available cores
    num_workers = os.cpu_count()
    log(f"Using {num_workers} CPU cores for parallel processing")
    
    results = []
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = {executor.submit(backtest_pair, pair): pair for pair in PAIRS}
        
        for future in futures:
            pair = futures[future]
            try:
                result = future.result()
                if result:
                    results.append(result)
                    log(f"✅ {pair}: {result.total_trades} trades, ${result.net_pnl:.2f} P&L, {result.return_pct:.2f}% return")
            except Exception as e:
                log(f"❌ {pair}: Backtest failed - {e}")
    
    return results

def save_results(results: List[BacktestResult]):
    """Save results to CSV"""
    if not results:
        log("⚠️ No results to save")
        return
    
    # Sort by net P&L
    results.sort(key=lambda r: r.net_pnl, reverse=True)
    
    # Write to CSV
    with open(OUTPUT_CSV, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Rank', 'Pair', 'Trades', 'Win_Rate_%', 'Net_PnL_$', 
            'Return_%', 'Max_Drawdown_%', 'Sharpe_Ratio',
            'Best_Trade_$', 'Worst_Trade_$', 'Final_Capital_$'
        ])
        
        for i, r in enumerate(results, 1):
            writer.writerow([
                i, r.pair, r.total_trades, f"{r.win_rate*100:.1f}",
                f"{r.net_pnl:.2f}", f"{r.return_pct:.2f}",
                f"{r.max_drawdown*100:.2f}", f"{r.sharpe_ratio:.2f}",
                f"{r.best_trade:.2f}", f"{r.worst_trade:.2f}",
                f"{r.final_capital:.2f}"
            ])
    
    log(f"\n✅ Results saved to {OUTPUT_CSV}")
    
    # Print summary
    log("\n" + "="*80)
    log("HELIOS INDICATOR PERFORMANCE SUMMARY")
    log("="*80)
    log(f"Indicator: cos(minute) → abs(volume) → sin(body)")
    log(f"Strategy: 1m + 5m divergence with 0.4% target / 0.2% stop")
    log(f"Capital: ${INITIAL_CAPITAL:,} | Position Size: {POSITION_SIZE_PCT*100}%")
    log("="*80)
    
    for i, r in enumerate(results[:10], 1):
        log(f"{i:2d}. {r.pair:12s} | Trades: {r.total_trades:4d} | "
            f"Win%: {r.win_rate*100:5.1f}% | P&L: ${r.net_pnl:8.2f} | "
            f"Return: {r.return_pct:6.2f}% | Sharpe: {r.sharpe_ratio:5.2f}")
    
    log("="*80)
    
    # Overall statistics
    total_pnl = sum(r.net_pnl for r in results)
    avg_return = sum(r.return_pct for r in results) / len(results)
    
    log(f"\nTotal Net P&L (all pairs): ${total_pnl:.2f}")
    log(f"Average Return: {avg_return:.2f}%")
    log(f"Best Pair: {results[0].pair} (${results[0].net_pnl:.2f})")
    log(f"Worst Pair: {results[-1].pair} (${results[-1].net_pnl:.2f})")

async def main():
    """Main execution"""
    start_time = time.time()
    
    log("="*80)
    log("MULTI-ASSET HELIOS INDICATOR BACKTESTER")
    log("="*80)
    
    # Step 1: Download data
    log("\n📥 PHASE 1: Data Download")
    await download_all_data()
    
    # Step 2: Run backtests in parallel
    log("\n🔬 PHASE 2: Parallel Backtesting")
    results = run_backtests_parallel()
    
    # Step 3: Save and display results
    log("\n💾 PHASE 3: Results")
    save_results(results)
    
    elapsed = time.time() - start_time
    log(f"\n⏱️ Total execution time: {elapsed:.1f} seconds")
    log("="*80)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log("\n🛑 Stopped by user")
    except Exception as e:
        log(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
