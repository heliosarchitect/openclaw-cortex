#!/usr/bin/env python3
"""
Multi-Asset Opportunity Scanner
Scans all Coinbase USD pairs for trading opportunities using technical analysis
"""

import asyncio
import aiohttp
import json
import time
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta, timezone
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from market_indicators import (
    calculate_rsi, calculate_macd, calculate_bollinger_bands,
    calculate_volume_profile, analyze_trend, calculate_volatility
)

# Setup logging
log_file = Path(__file__).parent.parent / 'scan_opportunities.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Coinbase API endpoints
COINBASE_API = "https://api.exchange.coinbase.com"
CACHE_DURATION = 300  # 5 minutes

# Cache storage
cache = {
    'products': {'data': None, 'timestamp': 0},
    'candles': {}
}


class OpportunityScanner:
    """Scans Coinbase markets for trading opportunities"""
    
    def __init__(self, top_n_pairs: int = 75):
        """
        Initialize scanner
        
        Args:
            top_n_pairs: Number of top pairs by volume to analyze
        """
        self.top_n_pairs = top_n_pairs
        self.session = None
        self.opportunities = []
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def get_all_products(self) -> List[Dict]:
        """
        Get all USD trading pairs from Coinbase
        
        Returns:
            List of product dictionaries
        """
        # Check cache
        if time.time() - cache['products']['timestamp'] < CACHE_DURATION:
            if cache['products']['data']:
                logger.info(f"Using cached products ({len(cache['products']['data'])} pairs)")
                return cache['products']['data']
        
        logger.info("Fetching all products from Coinbase...")
        url = f"{COINBASE_API}/products"
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    products = await response.json()
                    
                    # Filter for USD pairs only
                    usd_products = [
                        p for p in products 
                        if p.get('quote_currency') == 'USD' 
                        and p.get('status') == 'online'
                        and not p.get('trading_disabled', False)
                    ]
                    
                    # Cache results
                    cache['products']['data'] = usd_products
                    cache['products']['timestamp'] = time.time()
                    
                    logger.info(f"Found {len(usd_products)} active USD pairs")
                    return usd_products
                else:
                    logger.error(f"Failed to fetch products: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error fetching products: {e}")
            return []
    
    async def get_24h_stats(self, product_id: str) -> Optional[Dict]:
        """
        Get 24-hour stats for a product
        
        Args:
            product_id: Product identifier (e.g., 'BTC-USD')
        
        Returns:
            Stats dictionary or None
        """
        url = f"{COINBASE_API}/products/{product_id}/stats"
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return None
        except Exception as e:
            logger.debug(f"Error fetching stats for {product_id}: {e}")
            return None
    
    async def get_candles(self, product_id: str, granularity: int = 3600) -> Optional[List[List]]:
        """
        Get historical candles for a product
        
        Args:
            product_id: Product identifier
            granularity: Candle granularity in seconds (default 1 hour)
        
        Returns:
            List of candles [time, low, high, open, close, volume] or None
        """
        # Check cache
        cache_key = f"{product_id}_{granularity}"
        if cache_key in cache['candles']:
            cached = cache['candles'][cache_key]
            if time.time() - cached['timestamp'] < CACHE_DURATION:
                return cached['data']
        
        # Calculate time range (last 100 candles)
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(seconds=granularity * 100)
        
        url = f"{COINBASE_API}/products/{product_id}/candles"
        params = {
            'granularity': granularity,
            'start': start_time.isoformat(),
            'end': end_time.isoformat()
        }
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    candles = await response.json()
                    
                    # Cache results
                    cache['candles'][cache_key] = {
                        'data': candles,
                        'timestamp': time.time()
                    }
                    
                    return candles
                else:
                    return None
        except Exception as e:
            logger.debug(f"Error fetching candles for {product_id}: {e}")
            return None
    
    async def filter_by_volume(self, products: List[Dict]) -> List[Dict]:
        """
        Filter products by 24h volume and return top N
        
        Args:
            products: List of product dictionaries
        
        Returns:
            Filtered list of top volume products
        """
        logger.info(f"Filtering top {self.top_n_pairs} pairs by volume...")
        
        # Get stats for all products in parallel
        tasks = [self.get_24h_stats(p['id']) for p in products]
        stats_results = await asyncio.gather(*tasks)
        
        # Combine products with stats
        products_with_volume = []
        for product, stats in zip(products, stats_results):
            if stats and 'volume' in stats:
                try:
                    volume = float(stats['volume'])
                    if volume > 0:
                        products_with_volume.append({
                            'product': product,
                            'volume': volume,
                            'stats': stats
                        })
                except (ValueError, TypeError):
                    continue
        
        # Sort by volume and take top N
        products_with_volume.sort(key=lambda x: x['volume'], reverse=True)
        top_products = products_with_volume[:self.top_n_pairs]
        
        logger.info(f"Selected {len(top_products)} pairs for analysis")
        return top_products
    
    async def analyze_opportunity(self, product_data: Dict) -> Optional[Dict]:
        """
        Analyze a product for trading opportunities
        
        Args:
            product_data: Product data with stats
        
        Returns:
            Opportunity dictionary or None
        """
        product = product_data['product']
        product_id = product['id']
        stats = product_data['stats']
        
        # Get candle data
        candles = await self.get_candles(product_id)
        if not candles or len(candles) < 50:
            logger.debug(f"{product_id}: Insufficient candle data ({len(candles) if candles else 0} candles)")
            return None
        
        # Extract prices and volumes
        # Candles format: [time, low, high, open, close, volume]
        prices = [float(c[4]) for c in candles]  # close prices
        volumes = [float(c[5]) for c in candles]  # volumes
        
        # Reverse to chronological order
        prices.reverse()
        volumes.reverse()
        
        current_price = prices[-1]
        
        # Calculate indicators
        rsi = calculate_rsi(prices)
        macd = calculate_macd(prices)
        bb = calculate_bollinger_bands(prices)
        volume_profile = calculate_volume_profile(volumes)
        trend = analyze_trend(prices)
        volatility = calculate_volatility(prices)
        
        if not all([rsi, macd, bb, volume_profile]):
            logger.debug(f"{product_id}: Failed to calculate indicators")
            return None
        
        # Log low-score opportunities for debugging
        score, setup_type, signals = self.score_opportunity(
            rsi, macd, bb, volume_profile, trend, volatility
        )
        
        if score < 30:
            logger.debug(f"{product_id}: Score {score} (RSI:{rsi:.1f}, MACD:{macd['histogram']:.6f}, BB%:{bb['percent_b']:.1f})")
            return None
        
        if score >= 30:  # Minimum threshold (lowered to capture more opportunities)
            opportunity = {
                'symbol': product_id,
                'base_currency': product['base_currency'],
                'price': current_price,
                'volume_24h': product_data['volume'],
                'score': score,
                'setup': setup_type,
                'signals': signals,
                'indicators': {
                    'rsi': round(rsi, 2),
                    'macd': round(macd['macd'], 6),
                    'macd_signal': round(macd['signal'], 6),
                    'macd_histogram': round(macd['histogram'], 6),
                    'bb_upper': round(bb['upper'], 2),
                    'bb_middle': round(bb['middle'], 2),
                    'bb_lower': round(bb['lower'], 2),
                    'bb_percent': round(bb['percent_b'], 2),
                    'volume_ratio': round(volume_profile['volume_ratio'], 2),
                    'volatility': round(volatility, 2) if volatility else None
                },
                'trend': trend,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            return opportunity
        
        return None
    
    def score_opportunity(self, rsi: float, macd: Dict, bb: Dict, 
                         volume_profile: Dict, trend: str, 
                         volatility: Optional[float]) -> Tuple[int, str, List[str]]:
        """
        Score an opportunity based on indicators
        
        Args:
            rsi: RSI value
            macd: MACD dictionary
            bb: Bollinger Bands dictionary
            volume_profile: Volume profile dictionary
            trend: Trend direction
            volatility: Volatility percentage
        
        Returns:
            Tuple of (score, setup_type, signals)
        """
        score = 0
        signals = []
        setup_type = 'none'
        
        # === PRIMARY SETUPS ===
        
        # Strong Mean Reversion Setup (extreme oversold/overbought)
        if rsi < 30 and bb['percent_b'] < 20:
            score += 50
            signals.append('⭐ STRONG OVERSOLD (RSI < 30, BB extreme low)')
            setup_type = 'mean_reversion_long'
        elif rsi > 70 and bb['percent_b'] > 80:
            score += 50
            signals.append('⭐ STRONG OVERBOUGHT (RSI > 70, BB extreme high)')
            setup_type = 'mean_reversion_short'
        
        # Moderate Mean Reversion
        elif rsi < 35 and bb['percent_b'] < 30:
            score += 35
            signals.append('Oversold (RSI < 35, BB low)')
            setup_type = 'mean_reversion_long'
        elif rsi > 65 and bb['percent_b'] > 70:
            score += 35
            signals.append('Overbought (RSI > 65, BB high)')
            setup_type = 'mean_reversion_short'
        
        # Momentum Setup (discovered pattern: RSI 55-65 + positive MACD)
        if 55 <= rsi <= 65 and macd['histogram'] > 0:
            score += 30
            signals.append('Momentum zone (RSI 55-65, positive MACD)')
            if setup_type == 'none':
                setup_type = 'momentum_long'
        
        # === MACD SIGNALS ===
        
        # Strong MACD signals
        if macd['histogram'] > 0 and macd['macd'] > macd['signal']:
            if abs(macd['histogram']) > abs(macd['macd']) * 0.1:  # Strong crossover
                score += 20
                signals.append('MACD strong bullish crossover')
            else:
                score += 12
                signals.append('MACD bullish crossover')
        elif macd['histogram'] < 0 and macd['macd'] < macd['signal']:
            if abs(macd['histogram']) > abs(macd['macd']) * 0.1:  # Strong crossover
                score += 15
                signals.append('MACD strong bearish signal')
            else:
                score += 8
                signals.append('MACD bearish signal')
        
        # === VOLUME CONFIRMATION ===
        
        if volume_profile['volume_ratio'] > 2.0:
            score += 20
            signals.append(f"⚡ Very high volume ({volume_profile['volume_ratio']:.1f}x avg)")
        elif volume_profile['volume_ratio'] > 1.5:
            score += 12
            signals.append(f"High volume ({volume_profile['volume_ratio']:.1f}x avg)")
        elif volume_profile['volume_ratio'] > 1.2:
            score += 5
            signals.append(f"Above average volume ({volume_profile['volume_ratio']:.1f}x)")
        elif volume_profile['volume_ratio'] < 0.5:
            score -= 10
            signals.append('⚠️ Low volume warning')
        
        # === TREND ALIGNMENT ===
        
        if setup_type == 'mean_reversion_long' and trend == 'downtrend':
            score += 15
            signals.append('✓ Trend aligned (catching bottom in downtrend)')
        elif setup_type == 'mean_reversion_short' and trend == 'uptrend':
            score += 15
            signals.append('✓ Trend aligned (catching top in uptrend)')
        elif setup_type == 'momentum_long' and trend == 'uptrend':
            score += 15
            signals.append('✓ Trend aligned (momentum + uptrend)')
        elif setup_type == 'momentum_long' and trend == 'downtrend':
            score -= 10
            signals.append('⚠️ Counter-trend momentum')
        
        # === VOLATILITY FACTOR ===
        
        if volatility:
            if volatility > 5.0:
                score += 10
                signals.append(f'High volatility ({volatility:.1f}% - big moves possible)')
            elif volatility > 3.0:
                score += 5
                signals.append(f'Elevated volatility ({volatility:.1f}%)')
            elif volatility < 1.0:
                score -= 5
                signals.append(f'Low volatility ({volatility:.1f}% - sluggish)')
        
        # === BOLLINGER BAND EXTREMES ===
        
        # Extra points for being at BB extremes (regardless of RSI)
        if bb['percent_b'] < 10:
            score += 10
            signals.append('At lower Bollinger Band extreme')
        elif bb['percent_b'] > 90:
            score += 10
            signals.append('At upper Bollinger Band extreme')
        
        # Cap score at 100
        score = min(score, 100)
        
        return score, setup_type, signals
    
    async def scan_all_opportunities(self) -> List[Dict]:
        """
        Scan all products for opportunities
        
        Returns:
            List of opportunity dictionaries, sorted by score
        """
        start_time = time.time()
        logger.info("=" * 60)
        logger.info("Starting Multi-Asset Opportunity Scan")
        logger.info("=" * 60)
        
        # Get all USD products
        products = await self.get_all_products()
        if not products:
            logger.error("No products found")
            return []
        
        # Filter by volume
        top_products = await self.filter_by_volume(products)
        
        # Analyze each product
        logger.info(f"Analyzing {len(top_products)} pairs for opportunities...")
        
        # Enable debug logging to see why opportunities aren't found
        original_level = logger.level
        if logger.level > logging.DEBUG:
            logger.setLevel(logging.DEBUG)
        
        tasks = [self.analyze_opportunity(p) for p in top_products]
        results = await asyncio.gather(*tasks)
        
        logger.setLevel(original_level)
        
        # Filter out None results and sort by score
        opportunities = [r for r in results if r is not None]
        opportunities.sort(key=lambda x: x['score'], reverse=True)
        
        elapsed = time.time() - start_time
        logger.info("=" * 60)
        logger.info(f"Scan complete in {elapsed:.1f} seconds")
        logger.info(f"Found {len(opportunities)} opportunities (score >= 30)")
        logger.info("=" * 60)
        
        self.opportunities = opportunities
        return opportunities
    
    def save_results(self, output_path: Path, top_n: int = 10):
        """
        Save top opportunities to JSON file
        
        Args:
            output_path: Path to output JSON file
            top_n: Number of top opportunities to save
        """
        top_opportunities = self.opportunities[:top_n]
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(top_opportunities, f, indent=2)
        
        logger.info(f"Saved top {len(top_opportunities)} opportunities to {output_path}")
    
    def print_summary(self, top_n: int = 10):
        """
        Print summary of top opportunities
        
        Args:
            top_n: Number of top opportunities to display
        """
        if not self.opportunities:
            print("\nNo opportunities found (all scores < 30)")
            return
        
        print(f"\n{'=' * 80}")
        print(f"TOP {min(top_n, len(self.opportunities))} TRADING OPPORTUNITIES")
        print(f"{'=' * 80}\n")
        
        for i, opp in enumerate(self.opportunities[:top_n], 1):
            print(f"{i}. {opp['symbol']} - Score: {opp['score']}/100")
            print(f"   Setup: {opp['setup']}")
            print(f"   Price: ${opp['price']:.2f} | RSI: {opp['indicators']['rsi']}")
            print(f"   MACD: {opp['indicators']['macd']:.6f} | Histogram: {opp['indicators']['macd_histogram']:.6f}")
            print(f"   BB%: {opp['indicators']['bb_percent']:.1f}% | Volume: {opp['indicators']['volume_ratio']:.2f}x")
            print(f"   Trend: {opp['trend']}")
            print(f"   Signals:")
            for signal in opp['signals']:
                print(f"     • {signal}")
            print()


async def main():
    """Main entry point for the scanner"""
    try:
        # Initialize scanner
        async with OpportunityScanner(top_n_pairs=75) as scanner:
            # Scan all opportunities
            opportunities = await scanner.scan_all_opportunities()
            
            # Save results
            output_path = Path.home() / '.openclaw' / 'workspace' / 'market_opportunities.json'
            scanner.save_results(output_path, top_n=10)
            
            # Print summary
            scanner.print_summary(top_n=10)
            
            return 0
    
    except KeyboardInterrupt:
        logger.info("Scan interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Scan failed: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
