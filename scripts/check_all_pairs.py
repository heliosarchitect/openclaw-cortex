#!/usr/bin/env python3
"""Check prices for all trading pairs the bot monitors."""

import json
import sys
from pathlib import Path

# Import the crypto price checker
sys.path.insert(0, str(Path(__file__).parent))
from check_crypto_price import check_crypto_price

def load_bot_pairs():
    """Load trading pairs from the bot's config."""
    bot_config = Path.home() / "Projects/Chad2930/Chad_Profit_Bot/all_liquid_assets.json"
    
    if not bot_config.exists():
        print(f"⚠️ Bot config not found: {bot_config}")
        return []
    
    with open(bot_config) as f:
        assets = json.load(f)
    
    # Extract just the product symbols
    return [asset['product'] for asset in assets]

def main():
    """Check prices for all bot pairs or a specified number."""
    # Allow limiting the number of pairs (default: top 10)
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    
    pairs = load_bot_pairs()
    
    if not pairs:
        print("No trading pairs found")
        return
    
    print(f"💹 Top {min(limit, len(pairs))} Bot Trading Pairs:\n")
    
    for pair in pairs[:limit]:
        try:
            check_crypto_price(pair)
        except Exception as e:
            print(f"⚠️ Error checking {pair}: {e}")

if __name__ == "__main__":
    main()
