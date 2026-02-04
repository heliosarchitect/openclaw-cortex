#!/usr/bin/env python3
"""
Quick test of HELIOS indicator on existing ETH-USD data
"""

import sqlite3
import math
from datetime import datetime
from dataclasses import dataclass

DB_PATH = '/home/bonsaihorn/Projects/Chad_Volume_tracker/trading_data.db'
CAPITAL = 10000
POSITION_SIZE = 0.10
MAKER_FEE = 0.0004
TAKER_FEE = 0.0006

@dataclass
class Result:
    pair: str
    trades: int
    wins: int
    losses: int
    win_rate: float
    total_pnl: float
    net_pnl: float
    return_pct: float
    max_dd: float
    best_trade: float
    worst_trade: float

def calc_indicator(candles):
    """HELIOS: cos(minute) → abs(volume) → sin(body)"""
    signals = []
    
    for row in candles:
        ts, o, h, l, c, v = row[2], row[3], row[4], row[5], row[6], row[7]
        
        minute = datetime.fromtimestamp(ts).minute
        body = c - o
        
        # Transformation pipeline
        t1 = math.cos(minute * math.pi / 30)
        t2 = abs(v) * t1
        body_norm = body / o if o > 0 else 0
        t3 = math.sin(body_norm * 100) * t2
        
        signals.append(t3)
    
    return signals

def backtest(pair='ETH-USD'):
    """Backtest the indicator"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Load 1-minute candles
    cur.execute("""
        SELECT * FROM candles 
        WHERE product = ? AND granularity = 1
        ORDER BY timestamp ASC
    """, (pair,))
    
    candles = cur.fetchall()
    conn.close()
    
    print(f"\n📊 {pair}: Loaded {len(candles)} candles")
    
    if len(candles) < 100:
        print(f"⚠️ Not enough data")
        return None
    
    # Calculate indicator
    signals = calc_indicator(candles)
    
    # Trading logic: 1m + 5m divergence
    capital = CAPITAL
    position = None
    trades = []
    peak = capital
    max_dd = 0
    
    for i in range(5, len(candles)):
        row = candles[i]
        ts, o, h, l, c, v = row[2], row[3], row[4], row[5], row[6], row[7]
        
        sig = signals[i]
        sig_5m = sum(signals[i-4:i+1]) / 5
        div = sig - sig_5m
        
        if position is None:
            # Entry: positive divergence
            if div > 0 and sig > 0:
                position = {
                    'entry': c,
                    'size': (capital * POSITION_SIZE) / c,
                    'target': c * 1.004,  # 0.4% target
                    'stop': c * 0.998      # 0.2% stop
                }
        else:
            # Exit logic
            exit_price = None
            
            if c >= position['target']:
                exit_price = position['target']
            elif c <= position['stop']:
                exit_price = position['stop']
            elif div < -abs(sig * 0.5):  # Reversal
                exit_price = c
            
            if exit_price:
                # Calculate P&L
                pnl = (exit_price - position['entry']) * position['size']
                fees = (position['entry'] * position['size'] * MAKER_FEE +
                       exit_price * position['size'] * TAKER_FEE)
                net_pnl = pnl - fees
                
                capital += net_pnl
                trades.append(net_pnl)
                position = None
                
                # Track drawdown
                if capital > peak:
                    peak = capital
                dd = (peak - capital) / peak
                if dd > max_dd:
                    max_dd = dd
    
    # Results
    if not trades:
        print("⚠️ No trades generated")
        return None
    
    wins = [t for t in trades if t > 0]
    losses = [t for t in trades if t <= 0]
    total_pnl = sum(t for t in trades)
    
    result = Result(
        pair=pair,
        trades=len(trades),
        wins=len(wins),
        losses=len(losses),
        win_rate=len(wins) / len(trades),
        total_pnl=total_pnl,
        net_pnl=total_pnl,  # Already net of fees
        return_pct=(capital - CAPITAL) / CAPITAL * 100,
        max_dd=max_dd,
        best_trade=max(trades),
        worst_trade=min(trades)
    )
    
    return result

def main():
    print("="*80)
    print("HELIOS INDICATOR TEST - ETH-USD")
    print("="*80)
    print(f"Indicator: cos(minute) → abs(volume) → sin(body)")
    print(f"Strategy: 1m+5m divergence, 0.4% target, 0.2% stop")
    print(f"Capital: ${CAPITAL:,} | Position Size: {POSITION_SIZE*100}%")
    
    result = backtest()
    
    if result:
        print("\n" + "="*80)
        print("RESULTS")
        print("="*80)
        print(f"Total Trades:    {result.trades}")
        print(f"Winners:         {result.wins} ({result.win_rate*100:.1f}%)")
        print(f"Losers:          {result.losses}")
        print(f"Net P&L:         ${result.net_pnl:,.2f}")
        print(f"Return:          {result.return_pct:.2f}%")
        print(f"Max Drawdown:    {result.max_dd*100:.2f}%")
        print(f"Best Trade:      ${result.best_trade:.2f}")
        print(f"Worst Trade:     ${result.worst_trade:.2f}")
        print("="*80)
        
        if result.net_pnl > 0:
            print(f"\n✅ PROFITABLE! Made ${result.net_pnl:.2f} on ETH-USD")
        else:
            print(f"\n❌ Unprofitable: Lost ${abs(result.net_pnl):.2f} on ETH-USD")

if __name__ == "__main__":
    main()
