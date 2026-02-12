# Volatility-Calibrated Trailing Stop Data
*Generated: 2026-02-11 22:09*

## Method
60-second returns from enhanced_data.db trades table. Suggested trail = 2x avg absolute 60s return.

## Results

| Product | Data Points | Avg |Return| (60s) | Variance | Suggested Trail |
|---------|-------------|---------------------|----------|-----------------|
| NKN-USD | 1,042 | 0.926% | 1.564 | **1.85%** |
| GHST-USD | 1,550 | 0.748% | 1.078 | **1.50%** |
| BNKR-USD | 3,038 | 0.379% | 0.312 | **0.76%** |
| ZRO-USD | 2,307 | 0.247% | 0.140 | **0.49%** |
| SKR-USD | 2,971 | 0.211% | 0.082 | **0.42%** |
| AXS-USD | 2,365 | 0.200% | 0.081 | **0.40%** |
| BIRB-USD | 1,585 | 0.188% | 0.067 | **0.38%** |
| ETH-USD | 5,296 | 0.068% | 0.009 | **0.14%** |
| XRP-USD | 3,933 | 0.068% | 0.009 | **0.14%** |
| BTC-USD | 5,263 | 0.053% | 0.005 | **0.11%** |

## Key Insight
Current trailing stop is a flat 0.3% for all products. This is:
- **6x too tight for NKN-USD** (0.3% vs 1.85% suggested) — noise-stopped constantly
- **3x too wide for BTC-USD** (0.3% vs 0.11% suggested) — gives back too much profit
- **About right for BIRB/SKR** (0.3% vs 0.38-0.42%)

## Implementation
```python
# Per-product volatility-scaled trailing stop
suggested_trail = 2 * avg_abs_60s_return_for_product
trail_pct = max(0.1, min(suggested_trail, 3.0))  # Floor 0.1%, cap 3%
```

Precompute and cache per product. Update every hour from rolling 60s returns.
