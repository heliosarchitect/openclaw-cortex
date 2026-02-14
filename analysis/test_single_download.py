#!/usr/bin/env python3
import os
import sys
import requests
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path.home() / 'Projects/Chad2930/Chad_Profit_Bot'))
from core.coinbase_auth import CoinbaseAuth

# Load env
env_path = Path.home() / 'Projects/Chad2930/Chad_Profit_Bot' / '.env'
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                k, v = line.strip().split('=', 1)
                os.environ[k] = v

auth = CoinbaseAuth(
    api_key=os.getenv('CHADSQUARED_API_KEY'),
    private_key=os.getenv('CHADSQUARED_API_SECRET')
)

# Test single request
end_time = datetime.now()
start_time = end_time - timedelta(hours=5)

print(f"Testing BTC-USD download...")
print(f"Start: {start_time}")
print(f"End: {end_time}")

headers = auth.get_auth_headers('GET', '/api/v3/brokerage/products/BTC-USD/candles')
params = {
    'start': int(start_time.timestamp()),
    'end': int(end_time.timestamp()),
    'granularity': 'ONE_MINUTE'
}

print(f"\nHeaders: {headers}")
print(f"Params: {params}")

try:
    resp = requests.get(
        'https://api.coinbase.com/api/v3/brokerage/products/BTC-USD/candles',
        headers=headers,
        params=params,
        timeout=15
    )
    
    print(f"\nStatus: {resp.status_code}")
    print(f"Response: {resp.text[:500]}")
    
    if resp.status_code == 200:
        data = resp.json()
        if 'candles' in data:
            print(f"\n✅ Got {len(data['candles'])} candles!")
        else:
            print(f"\n❌ No candles in response: {data}")
    else:
        print(f"\n❌ Failed: {resp.status_code}")
        
except Exception as e:
    print(f"\n❌ Exception: {e}")
    import traceback
    traceback.print_exc()
