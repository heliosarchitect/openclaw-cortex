#!/usr/bin/env python3
"""
Market Indicators Module
Technical indicator calculations for opportunity scanning
"""

import numpy as np
from typing import List, Dict, Tuple, Optional


def calculate_rsi(prices: List[float], period: int = 14) -> Optional[float]:
    """
    Calculate Relative Strength Index
    
    Args:
        prices: List of closing prices
        period: RSI period (default 14)
    
    Returns:
        RSI value (0-100) or None if insufficient data
    """
    if len(prices) < period + 1:
        return None
    
    # Calculate price changes
    deltas = np.diff(prices)
    
    # Separate gains and losses
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    
    # Calculate average gain and loss
    avg_gain = np.mean(gains[-period:])
    avg_loss = np.mean(losses[-period:])
    
    if avg_loss == 0:
        return 100.0
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return float(rsi)


def calculate_macd(prices: List[float], 
                   fast_period: int = 12, 
                   slow_period: int = 26, 
                   signal_period: int = 9) -> Optional[Dict[str, float]]:
    """
    Calculate MACD (Moving Average Convergence Divergence)
    
    Args:
        prices: List of closing prices
        fast_period: Fast EMA period (default 12)
        slow_period: Slow EMA period (default 26)
        signal_period: Signal line period (default 9)
    
    Returns:
        Dict with macd, signal, histogram or None if insufficient data
    """
    if len(prices) < slow_period + signal_period:
        return None
    
    prices_array = np.array(prices)
    
    # Calculate EMAs
    ema_fast = _calculate_ema(prices_array, fast_period)
    ema_slow = _calculate_ema(prices_array, slow_period)
    
    # MACD line
    macd_line = ema_fast - ema_slow
    
    # Signal line
    signal_line = _calculate_ema(macd_line, signal_period)
    
    # Histogram
    histogram = macd_line[-1] - signal_line[-1]
    
    return {
        'macd': float(macd_line[-1]),
        'signal': float(signal_line[-1]),
        'histogram': float(histogram)
    }


def calculate_bollinger_bands(prices: List[float], 
                               period: int = 20, 
                               std_dev: float = 2.0) -> Optional[Dict[str, float]]:
    """
    Calculate Bollinger Bands
    
    Args:
        prices: List of closing prices
        period: Moving average period (default 20)
        std_dev: Standard deviations for bands (default 2.0)
    
    Returns:
        Dict with upper, middle, lower bands and percentage position
    """
    if len(prices) < period:
        return None
    
    recent_prices = np.array(prices[-period:])
    
    middle = np.mean(recent_prices)
    std = np.std(recent_prices)
    
    upper = middle + (std_dev * std)
    lower = middle - (std_dev * std)
    
    current_price = prices[-1]
    
    # Calculate percentage position within bands (0 = lower, 50 = middle, 100 = upper)
    if upper != lower:
        percent_b = ((current_price - lower) / (upper - lower)) * 100
    else:
        percent_b = 50.0
    
    return {
        'upper': float(upper),
        'middle': float(middle),
        'lower': float(lower),
        'current': float(current_price),
        'percent_b': float(percent_b)
    }


def calculate_volume_profile(volumes: List[float], 
                             period: int = 20) -> Optional[Dict[str, float]]:
    """
    Calculate volume profile metrics
    
    Args:
        volumes: List of volume values
        period: Lookback period
    
    Returns:
        Dict with average volume and current vs average ratio
    """
    if len(volumes) < period:
        return None
    
    recent_volumes = np.array(volumes[-period:])
    avg_volume = np.mean(recent_volumes)
    current_volume = volumes[-1]
    
    volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
    
    return {
        'avg_volume': float(avg_volume),
        'current_volume': float(current_volume),
        'volume_ratio': float(volume_ratio)
    }


def _calculate_ema(data: np.ndarray, period: int) -> np.ndarray:
    """
    Calculate Exponential Moving Average
    
    Args:
        data: Price data array
        period: EMA period
    
    Returns:
        EMA values as numpy array
    """
    ema = np.zeros_like(data)
    multiplier = 2 / (period + 1)
    
    # Start with SMA
    ema[period - 1] = np.mean(data[:period])
    
    # Calculate EMA
    for i in range(period, len(data)):
        ema[i] = (data[i] - ema[i - 1]) * multiplier + ema[i - 1]
    
    return ema


def analyze_trend(prices: List[float], period: int = 20) -> str:
    """
    Analyze price trend
    
    Args:
        prices: List of closing prices
        period: Lookback period
    
    Returns:
        'uptrend', 'downtrend', or 'sideways'
    """
    if len(prices) < period:
        return 'unknown'
    
    recent_prices = np.array(prices[-period:])
    
    # Calculate linear regression slope
    x = np.arange(len(recent_prices))
    slope = np.polyfit(x, recent_prices, 1)[0]
    
    # Normalize by price
    slope_percent = (slope / recent_prices[0]) * 100
    
    if slope_percent > 0.5:
        return 'uptrend'
    elif slope_percent < -0.5:
        return 'downtrend'
    else:
        return 'sideways'


def calculate_volatility(prices: List[float], period: int = 20) -> Optional[float]:
    """
    Calculate price volatility (standard deviation of returns)
    
    Args:
        prices: List of closing prices
        period: Lookback period
    
    Returns:
        Volatility as percentage
    """
    if len(prices) < period + 1:
        return None
    
    recent_prices = np.array(prices[-period:])
    returns = np.diff(recent_prices) / recent_prices[:-1]
    
    volatility = np.std(returns) * 100  # Convert to percentage
    
    return float(volatility)
