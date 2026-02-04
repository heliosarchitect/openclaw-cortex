#!/usr/bin/env python3
"""Check current crypto price using public Coinbase API."""

import json
import urllib.request
import urllib.error
import sys

def check_crypto_price(symbol="ETH-USD"):
    """Get current price from Coinbase.
    
    Args:
        symbol: Trading pair (e.g., 'ETH-USD', 'BTC-USD', 'SOL-USD')
    """
    # Use public v2 API (no auth required)
    url = f"https://api.coinbase.com/v2/prices/{symbol}/spot"
    
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
        
        if 'data' not in data:
            print(f"⚠️ No price data available for {symbol}")
            return
        
        price = float(data['data'].get('amount', 0))
        base = data['data'].get('base', symbol.split('-')[0])
        currency = data['data'].get('currency', 'USD')
        
        if price == 0:
            print(f"⚠️ No price data available for {symbol}")
            return
        
        print(f"💰 {base}: ${price:,.2f}")
        
    except urllib.error.URLError as e:
        print(f"⚠️ Coinbase API unavailable: {e.reason}")
    except json.JSONDecodeError:
        print(f"⚠️ Invalid response from Coinbase API")
    except Exception as e:
        print(f"⚠️ Error checking ETH price: {type(e).__name__}")

if __name__ == "__main__":
    # Default to ETH-USD, but accept symbol as argument
    symbol = sys.argv[1] if len(sys.argv) > 1 else "ETH-USD"
    check_crypto_price(symbol)
