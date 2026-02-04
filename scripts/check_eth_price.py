#!/usr/bin/env python3
"""Check current ETH price using public Coinbase API."""

import json
import urllib.request
import urllib.error

def check_eth_price():
    """Get current ETH-USD price from Coinbase."""
    # Use public v2 API (no auth required)
    url = "https://api.coinbase.com/v2/prices/ETH-USD/spot"
    
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
        
        if 'data' not in data:
            print("⚠️ No price data available")
            return
        
        price = float(data['data'].get('amount', 0))
        currency = data['data'].get('currency', 'USD')
        
        if price == 0:
            print("⚠️ No price data available")
            return
        
        print(f"💰 ETH: ${price:,.2f}")
        
    except urllib.error.URLError as e:
        print(f"⚠️ Coinbase API unavailable: {e.reason}")
    except json.JSONDecodeError:
        print(f"⚠️ Invalid response from Coinbase API")
    except Exception as e:
        print(f"⚠️ Error checking ETH price: {type(e).__name__}")

if __name__ == "__main__":
    check_eth_price()
