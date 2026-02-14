#!/usr/bin/env python3
"""
Generate optimal config files for each trading asset
Based on volatility, typical spread, and volume characteristics
"""

import yaml
from pathlib import Path

# Asset-specific parameters (optimized for 0.1% scalps with VIP2 fees)
ASSET_CONFIGS = {
    'ETH-USD': {
        'crypto_symbol': 'ETH',
        'crypto_name': 'Ethereum',
        'tick_size': 0.01,
        'min_profit_ticks': 3,  # $0.03 min profit
        'min_order_size': 0.01,
        'max_order_size': 0.05,
        'order_levels': 3,
        'base_profit_target_bps': 10,  # 0.10% = 10 bps
        'min_profit_bps': 7,
        'max_position_percent': 40,  # ETH is stable, allow bigger position
        'rebalance_check_interval_seconds': 15,  # Fast, liquid market
        'volatility': 'medium',
        'priority': 'high'
    },
    'SOL-USD': {
        'crypto_symbol': 'SOL',
        'crypto_name': 'Solana',
        'tick_size': 0.01,
        'min_profit_ticks': 2,
        'min_order_size': 0.1,
        'max_order_size': 1.0,
        'order_levels': 4,
        'base_profit_target_bps': 12,  # More volatile = wider targets
        'min_profit_bps': 8,
        'max_position_percent': 30,
        'rebalance_check_interval_seconds': 20,
        'volatility': 'high',
        'priority': 'high'
    },
    'DOGE-USD': {
        'crypto_symbol': 'DOGE',
        'crypto_name': 'Dogecoin',
        'tick_size': 0.00001,
        'min_profit_ticks': 5,
        'min_order_size': 10,
        'max_order_size': 100,
        'order_levels': 5,
        'base_profit_target_bps': 15,  # Meme coin = wider spreads
        'min_profit_bps': 10,
        'max_position_percent': 20,
        'rebalance_check_interval_seconds': 25,
        'volatility': 'very_high',
        'priority': 'medium'
    },
    'XRP-USD': {
        'crypto_symbol': 'XRP',
        'crypto_name': 'Ripple',
        'tick_size': 0.0001,
        'min_profit_ticks': 5,
        'min_order_size': 1,
        'max_order_size': 10,
        'order_levels': 4,
        'base_profit_target_bps': 12,
        'min_profit_bps': 8,
        'max_position_percent': 25,
        'rebalance_check_interval_seconds': 20,
        'volatility': 'medium',
        'priority': 'medium'
    },
    'ADA-USD': {
        'crypto_symbol': 'ADA',
        'crypto_name': 'Cardano',
        'tick_size': 0.0001,
        'min_profit_ticks': 4,
        'min_order_size': 1,
        'max_order_size': 20,
        'order_levels': 4,
        'base_profit_target_bps': 13,
        'min_profit_bps': 9,
        'max_position_percent': 25,
        'rebalance_check_interval_seconds': 25,
        'volatility': 'medium',
        'priority': 'medium'
    },
    'LINK-USD': {
        'crypto_symbol': 'LINK',
        'crypto_name': 'Chainlink',
        'tick_size': 0.001,
        'min_profit_ticks': 3,
        'min_order_size': 0.1,
        'max_order_size': 2.0,
        'order_levels': 3,
        'base_profit_target_bps': 11,
        'min_profit_bps': 8,
        'max_position_percent': 25,
        'rebalance_check_interval_seconds': 20,
        'volatility': 'medium',
        'priority': 'medium'
    },
    'DOT-USD': {
        'crypto_symbol': 'DOT',
        'crypto_name': 'Polkadot',
        'tick_size': 0.001,
        'min_profit_ticks': 3,
        'min_order_size': 0.1,
        'max_order_size': 3.0,
        'order_levels': 4,
        'base_profit_target_bps': 12,
        'min_profit_bps': 8,
        'max_position_percent': 20,
        'rebalance_check_interval_seconds': 25,
        'volatility': 'medium',
        'priority': 'low'
    },
    'AVAX-USD': {
        'crypto_symbol': 'AVAX',
        'crypto_name': 'Avalanche',
        'tick_size': 0.01,
        'min_profit_ticks': 2,
        'min_order_size': 0.1,
        'max_order_size': 1.5,
        'order_levels': 4,
        'base_profit_target_bps': 13,
        'min_profit_bps': 9,
        'max_position_percent': 20,
        'rebalance_check_interval_seconds': 25,
        'volatility': 'high',
        'priority': 'low'
    },
    'ATOM-USD': {
        'crypto_symbol': 'ATOM',
        'crypto_name': 'Cosmos',
        'tick_size': 0.001,
        'min_profit_ticks': 3,
        'min_order_size': 0.1,
        'max_order_size': 2.0,
        'order_levels': 4,
        'base_profit_target_bps': 12,
        'min_profit_bps': 8,
        'max_position_percent': 20,
        'rebalance_check_interval_seconds': 25,
        'volatility': 'medium',
        'priority': 'low'
    },
    'NEAR-USD': {
        'crypto_symbol': 'NEAR',
        'crypto_name': 'Near Protocol',
        'tick_size': 0.001,
        'min_profit_ticks': 3,
        'min_order_size': 0.1,
        'max_order_size': 3.0,
        'order_levels': 4,
        'base_profit_target_bps': 13,
        'min_profit_bps': 9,
        'max_position_percent': 20,
        'rebalance_check_interval_seconds': 30,
        'volatility': 'medium',
        'priority': 'low'
    }
}

# Base config template
BASE_CONFIG = {
    'api_key_env': 'COINBASE_API_KEY',
    'api_secret_env': 'COINBASE_API_SECRET',
    
    # Capital management
    'reserve_percent': 0.15,  # Keep 15% reserve
    'averaging_down_decay': 0.8,
    'underwater_size_multiplier': 1.5,  # Aggressive averaging down
    'profitable_size_multiplier': 0.7,
    
    # Profit targets
    'recovery_boost_bps': 5,
    'max_profit_target_bps': 30,
    
    # Adaptive profit (disabled for simplicity - can enable later)
    'adaptive_profit_enabled': False,
    'adaptive_high_divider': 2.5,
    'adaptive_low_multiplier': 2.5,
    'adaptive_rsi_overbought': 70,
    'adaptive_rsi_oversold': 30,
    
    # Smart cancellation (AGGRESSIVE - 30s timeout)
    'min_order_age_seconds': 30,  # Cancel unfilled orders after 30s
    'max_distance_from_spread_ticks': 10,
    'stale_age_seconds': 45,
    'profit_order_protection_seconds': 120,  # Protect profit orders for 2 min
    
    # Recovery mode
    'recovery_mode_loss_percent': 2.0,
    'max_loss_per_position_bps': 15,  # Max 0.15% loss per position
    
    # Layer management
    'max_inventory_layers': 3,
    'layer_spacing_ticks': 5,
    
    # Post-fill behavior
    'buy_delay_after_sell_seconds': 3.0,  # Fast re-entry after sells
    
    # Momentum and filters (disabled for simple scalping)
    'momentum_filter': {
        'enabled': False
    },
    'contrarian_strategy': {
        'enabled': False
    },
    
    # Cooldown management
    'cooldown': {
        'enabled': True,
        'base_cooldown_seconds': 10,
        'max_cooldown_seconds': 60
    }
}


def generate_config(symbol: str, params: dict) -> dict:
    """Generate complete config for an asset"""
    config = BASE_CONFIG.copy()
    
    # Merge asset-specific params
    config['symbol'] = symbol
    config['crypto_symbol'] = params['crypto_symbol']
    config['crypto_name'] = params['crypto_name']
    config['tick_size'] = params['tick_size']
    config['min_profit_ticks'] = params['min_profit_ticks']
    config['min_order_size'] = params['min_order_size']
    config['max_order_size'] = params['max_order_size']
    config['order_levels'] = params['order_levels']
    config['base_profit_target_bps'] = params['base_profit_target_bps']
    config['min_profit_bps'] = params['min_profit_bps']
    config['max_position_percent'] = params['max_position_percent']
    config['rebalance_check_interval_seconds'] = params['rebalance_check_interval_seconds']
    
    return config


def main():
    """Generate all config files"""
    output_dir = Path('config')
    output_dir.mkdir(exist_ok=True)
    
    print("=" * 70)
    print("🎯 GENERATING ASSET CONFIGS")
    print("=" * 70)
    
    for symbol, params in ASSET_CONFIGS.items():
        config = generate_config(symbol, params)
        
        # Output filename
        filename = output_dir / f"active_{symbol.split('-')[0].lower()}_config.yaml"
        
        # Write YAML
        with open(filename, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        
        print(f"✅ {symbol:12} -> {filename}")
        print(f"   Profit target: {params['base_profit_target_bps']} bps")
        print(f"   Position size: {params['min_order_size']}-{params['max_order_size']}")
        print(f"   Priority: {params['priority']}")
        print()
    
    print("=" * 70)
    print("✅ All configs generated!")
    print("\nNext steps:")
    print("  1. Review configs in config/ directory")
    print("  2. Adjust any asset-specific parameters")
    print("  3. Run: python active_trader.py")
    print("=" * 70)


if __name__ == "__main__":
    main()
