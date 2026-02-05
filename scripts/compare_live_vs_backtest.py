#!/usr/bin/env python3
"""Compare live trading performance vs backtest predictions"""
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

# Live DB
live_db = '/home/bonsaihorn/Projects/Chad2930/Chad_Profit_Bot/live_trading.db'
live_conn = sqlite3.connect(live_db)

# Get today's closed trades
today = datetime.now().strftime('%Y-%m-%d')
query = f"""
SELECT 
    COUNT(*) as trades,
    SUM(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END) as wins,
    SUM(CASE WHEN profit_loss < 0 THEN 1 ELSE 0 END) as losses,
    SUM(profit_loss) as total_profit
FROM trades 
WHERE status='CLOSED' 
AND date(timestamp) = '{today}'
"""

df = pd.read_sql_query(query, live_conn)
live_conn.close()

if df['trades'].iloc[0] == 0:
    print("No closed trades today yet")
else:
    trades = df['trades'].iloc[0]
    wins = df['wins'].iloc[0]
    losses = df['losses'].iloc[0]
    profit = df['total_profit'].iloc[0]
    wr = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0
    
    # Trading hours so far (9am to now)
    now = datetime.now()
    if now.hour >= 9:
        hours = (now.hour - 9) + (now.minute / 60)
    else:
        hours = 0
    
    tph = trades / hours if hours > 0 else 0
    
    print("="*60)
    print("LIVE TRADING TODAY")
    print("="*60)
    print(f"Trades: {trades} ({tph:.1f} TPH)")
    print(f"Win Rate: {wr:.1f}% ({wins}W/{losses}L)")
    print(f"Profit: ${profit:.2f}")
    print()
    print("BACKTEST PREDICTION (Volume Strategy)")
    print("="*60)
    print(f"Expected TPH: 1487")
    print(f"Expected WR: 74.4%")
    print(f"Expected Profit: $12,939 (29 days)")
    print()
    print("COMPARISON")
    print("="*60)
    print(f"TPH: {tph:.1f} vs 1487 expected ({(tph/1487*100):.1f}%)")
    print(f"WR: {wr:.1f}% vs 74.4% expected")
