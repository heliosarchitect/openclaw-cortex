# High-Frequency Market Making Backtest Summary

**Date:** February 3, 2026  
**Asset:** ETH-USD  
**Data:** 98,937 1-second candles (69.8 days from Aug 29 - Nov 6, 2025)

## Strategy
- **Type:** Pure market making
- **Method:** Buy at bid, sell at ask when spread exceeds threshold
- **Position Size:** 1 ETH per trade
- **Spread Estimation:** Bid/Ask derived from candle high/low

## Key Findings

### Optimal Configuration
- **Threshold:** 0.05% spread
- **Total Profit:** $377,578.71
- **Opportunities:** 73,081 trades
- **Avg Profit/Trade:** $5.17
- **Max Sustainable Volume:** 0.0121 fills/sec (~43.6 fills/hour)
- **Total Volume:** $303M

### Profitability vs Volume Curve

| Threshold | Opportunities | Profit     | Fills/Sec | Volume       |
|-----------|--------------|------------|-----------|--------------|
| 0.05%     | 73,081       | $377,578   | 0.0121    | $303M        |
| 0.10%     | 35,301       | $261,826   | 0.0059    | $144M        |
| 0.15%     | 17,292       | $171,555   | 0.0029    | $69M         |
| 0.20%     | 9,127        | $114,567   | 0.0015    | $36M         |
| 0.50%     | 716          | $22,698    | 0.0001    | $2.8M        |

### Market Conditions
- **Average Spread:** 0.102%
- **Median Spread:** 0.078%
- **Max Spread Observed:** 4.433%
- **Min Spread Observed:** 0.000%

## Insights

1. **Volume-Profit Tradeoff:**
   - Lower thresholds capture more opportunities but lower profit/trade
   - Higher thresholds increase profit/trade but drastically reduce volume
   - 0.05% threshold provides optimal balance

2. **Maximum Sustainable Throughput:**
   - Peak: 0.0121 fills/sec (43.6 fills/hour) at 0.05% threshold
   - Real-world latency would reduce this significantly
   - Exchange rate limits and order book depth not factored

3. **Profitability:**
   - Pure market making highly profitable in this dataset
   - $5.17 avg profit/trade at optimal threshold
   - 100% win rate assumes perfect fills (unrealistic in production)

## Limitations & Considerations

⚠️ **This is a simplified backtest. Production reality differs:**

1. **No Order Book Depth:** Assumes infinite liquidity at bid/ask
2. **No Slippage:** Assumes fills at exact bid/ask prices
3. **No Latency:** Assumes instant order placement/execution
4. **No Fees:** Exchange fees (maker/taker) not included
5. **No Market Impact:** Assumes orders don't move the market
6. **No Adverse Selection:** Assumes all spreads are tradeable
7. **Spread Estimation:** Derived from high/low (imprecise)

## Recommendations

1. **For Production:**
   - Add realistic fees (~0.02-0.05% per side)
   - Model order book depth from L2 data
   - Include latency simulation (1-50ms)
   - Test adverse selection scenarios
   - Account for inventory risk

2. **Data Enhancement:**
   - Use actual tick data with order book snapshots
   - Include maker/taker fee schedule
   - Model fill probability based on depth

3. **Strategy Refinement:**
   - Dynamic threshold adjustment based on volatility
   - Inventory management (don't accumulate position)
   - Risk limits (max position size, daily loss limits)

## Files Generated
- `backtest_hfv.py` - Main backtesting engine
- `backtest_results.csv` - Detailed results by threshold
- `BACKTEST_SUMMARY.md` - This summary
