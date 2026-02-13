# Coinbase 0% Maker Fee Analysis for AUGUR

**Date**: 2026-02-12 22:25 EST  
**Context**: AUGUR V4 has collected 1,885+ signals and current fees are destroying gross edge

## Current Situation

AUGUR is currently using VIP2 fees on Coinbase:
- **Maker**: 0.10% 
- **Taker**: 0.10%
- **Round-trip cost**: 0.20%

This fee structure is destroying the gross edge discovered by AUGUR's pattern mining.

## Coinbase 0% Maker Fee Opportunities

### 1. Stable Pairs (Immediate Opportunity)

Coinbase Advanced offers **0.00% maker fees** for 22 stable pairs. Known pairs include:

**USD-based stable pairs**:
- BUSD-USD, DAI-USD, GUSD-USD, GYEN-USD, MUSD-USD, PAX-USD
- USDT-USD, USDT-EUR, USDT-GBP, USDC-EUR, USDC-GBP, USDT-USDC

**Crypto-backed stable pairs**:
- WBTC-BTC, CBETH-ETH

**Note**: USDT-USDC and USDT-USD lost stablepair pricing as of May 1, 2025.

### 2. High-Volume Tiers (Long-term)

For traditional crypto pairs, 0% maker fees are available at the highest volume tiers:
- **$400+ million** in 30-day trading volume
- **0% maker fees, 0.05% taker fees**

## Strategic Implications for AUGUR

### Immediate Actions Available

1. **Test stable pair arbitrage**: Look for patterns in WBTC-BTC and CBETH-ETH where we have 0% maker fees
2. **USD stablecoin opportunities**: Explore patterns in DAI-USD, GUSD-USD, etc.

### Pattern Mining Focus Areas

1. **WBTC-BTC arbitrage signals**: Look for divergence patterns between wrapped Bitcoin and native Bitcoin
2. **CBETH-ETH arbitrage signals**: Coinbase-staked ETH vs native ETH divergence
3. **Cross-stablecoin patterns**: USD, EUR, GBP stable pairs with forex-style opportunities

### Implementation Considerations

**Pros**:
- 0% maker fees = 100% of gross edge preserved on maker side
- Still have 0.10% taker fees vs 0.20% round-trip currently
- Can test strategies with minimal fee drag

**Cons**:
- Limited to specific pairs
- May have lower volume/liquidity
- Pattern discovery may not transfer from high-volume pairs

## Next Steps

1. **Immediate**: Run signal_miner on WBTC-BTC and CBETH-ETH historical data
2. **Pattern validation**: Backtest existing patterns on 0% fee stable pairs
3. **Live testing**: Deploy limited live trading on stable pairs to validate in live market conditions
4. **Monitor**: Track if pattern quality/frequency differs between high-volume and stable pairs

## Technical Implementation

- Modify AUGUR V4 scanner to include stable pairs in product list
- Update fee calculations in backtesting to use 0% maker fees for stable pairs
- Add stable pair regime detection (different from crypto pair behavior)

---

**Key Insight**: This could be the breakthrough AUGUR needs to transition from simulation to profitable live trading by eliminating the primary cost factor that destroys edge.