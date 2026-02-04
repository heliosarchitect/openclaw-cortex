#!/usr/bin/env python3
"""Test if we can access Coinbase order book data."""
import requests
import json
import time

# Public order book endpoint (no auth needed)
url = "https://api.coinbase.com/api/v3/brokerage/market/product_book"
params = {
    "product_id": "ETH-USD",
    "limit": 10  # Top 10 bids/asks
}

print("Testing Coinbase order book access...")
start = time.time()
response = requests.get(url, params=params)
elapsed = time.time() - start

print(f"Status: {response.status_code}")
print(f"Latency: {elapsed*1000:.1f}ms")

if response.status_code == 200:
    data = response.json()
    
    if 'pricebook' in data:
        book = data['pricebook']
        print("\n📊 Order Book Snapshot:")
        print(f"Product: {book.get('product_id')}")
        print(f"Time: {book.get('time')}")
        
        if 'bids' in book and 'asks' in book:
            bids = book['bids'][:5]
            asks = book['asks'][:5]
            
            print(f"\nTop 5 Bids:")
            for bid in bids:
                print(f"  ${float(bid['price']):.2f} x {float(bid['size']):.4f}")
            
            print(f"\nTop 5 Asks:")
            for ask in asks:
                print(f"  ${float(ask['price']):.2f} x {float(ask['size']):.4f}")
            
            # Calculate spread
            best_bid = float(bids[0]['price'])
            best_ask = float(asks[0]['price'])
            spread = best_ask - best_bid
            spread_pct = (spread / best_bid) * 100
            
            print(f"\n💰 Spread: ${spread:.2f} ({spread_pct:.4f}%)")
            print(f"Mid: ${(best_bid + best_ask)/2:.2f}")
            
            print("\n✅ Order book access working!")
            print(f"Can poll at ~{1/elapsed:.1f} req/sec")
        else:
            print("No bids/asks in response")
            print(json.dumps(data, indent=2))
    else:
        print("Unexpected response format:")
        print(json.dumps(data, indent=2)[:500])
else:
    print(f"Error: {response.text}")

