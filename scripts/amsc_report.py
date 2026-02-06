#!/usr/bin/env python3
"""
AMSC Trading Report
Report volume and trades every 15 minutes
"""
import sqlite3
import sys
import os
from datetime import datetime, timedelta

# Add bot path for auth
sys.path.insert(0, '/home/bonsaihorn/Projects/Chad2930/Chad_Profit_Bot')
from core.coinbase_auth import CoinbaseAuth
import requests

# Load Coinbase credentials
env_path = '/home/bonsaihorn/Projects/Chad2930/Chad_Profit_Bot/.env'
with open(env_path) as f:
    env = dict(line.strip().split('=', 1) for line in f if '=' in line and not line.startswith('#'))
    
auth = CoinbaseAuth(env['CHADSQUARED_API_KEY'], env['CHADSQUARED_API_SECRET'])

db = sqlite3.connect('/home/bonsaihorn/Projects/Chad2930/Chad_Profit_Bot/live_amsc_trading.db')
cursor = db.cursor()

# Get all-time stats
cursor.execute('''
    SELECT 
        COUNT(*) as trades,
        COALESCE(SUM(pnl), 0) as profit,
        AVG(CASE WHEN pnl > 0 THEN 1.0 ELSE 0.0 END)*100 as win_rate
    FROM trades 
    WHERE pnl IS NOT NULL
''')
total_trades, total_profit, win_rate = cursor.fetchone()

# Get last 15 min stats
fifteen_min_ago = int((datetime.now() - timedelta(minutes=15)).timestamp())
cursor.execute('''
    SELECT 
        COUNT(*) as trades,
        COALESCE(SUM(pnl), 0) as profit
    FROM trades 
    WHERE timestamp > ? AND pnl IS NOT NULL
''', (fifteen_min_ago,))
recent_trades, recent_profit = cursor.fetchone()

# Get 30-day stats
thirty_days_ago = int((datetime.now() - timedelta(days=30)).timestamp())
cursor.execute('''
    SELECT 
        COUNT(*) as trades,
        COALESCE(SUM(pnl), 0) as profit
    FROM trades 
    WHERE timestamp > ? AND pnl IS NOT NULL
''', (thirty_days_ago,))
month_trades, month_profit = cursor.fetchone()

# Open positions
cursor.execute('SELECT COUNT(*) FROM orders')
open_pos = cursor.fetchone()[0]

# Get 30-day volume from Coinbase transaction summary
try:
    headers = auth.get_auth_headers('GET', '/api/v3/brokerage/transaction_summary', '')
    response = requests.get(
        'https://api.coinbase.com/api/v3/brokerage/transaction_summary',
        headers=headers,
        timeout=5
    )
    
    if response.status_code == 200:
        data = response.json()
        cb_30d_volume = float(data.get('total_volume', 0))
    else:
        cb_30d_volume = 0
            
except Exception as e:
    cb_30d_volume = 0

# Calculate dollar volume (approximate: trades * $10 position size * 2 for round-trip)
dollar_volume_15min = recent_trades * 10 * 2
dollar_volume_total = total_trades * 10 * 2

print(f"📊 AMSC TRADING REPORT [{datetime.now().strftime('%H:%M:%S')}]")
print(f"=" * 60)
print(f"Last 15 min: {recent_trades} trades | ${recent_profit:.2f} P/L | ${dollar_volume_15min:,} volume")
print(f"Total:       {total_trades} trades | ${total_profit:.2f} P/L | ${dollar_volume_total:,} volume")
print(f"30-day (CB): ${cb_30d_volume:,.2f} volume")
print(f"Open positions: {open_pos} | Win rate: {win_rate:.1f}%")
print(f"=" * 60)

db.close()
