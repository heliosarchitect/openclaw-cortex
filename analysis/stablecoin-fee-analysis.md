# Stablecoin Fee Analysis — 2bps vs 20bps Impact

**Date:** 2026-02-13 06:51 EST  
**Trigger:** Matthew asking about 0.001% taker fees (2bps round trip) for stablecoins

## Executive Summary

**Current State:** AUGUR live trader uses 20bps round-trip fees (10bps taker). Zero stablecoin pairs are being traded.

**Matthew's Question:** Are 0bps fee stablecoins in the live trader? Fee is actually 0.001% taker (2bps RT), not 20bps.

**Finding:** No stablecoins in current whitelist. Pattern mining on CBETH-USD/DAI-USD failed (0 signals found). This creates a **10x fee arbitrage opportunity** if viable patterns exist.

## Fee Structure Analysis

| Fee Scenario | Taker Fee | Round Trip | Current Usage |
|-------------|-----------|------------|---------------|
| **VIP2 Standard** | 10bps (0.10%) | **20bps** | ✅ RARI-USD, ZRO-USD, AZTEC-USD |
| **Stablecoin Special** | 1bp (0.001%) | **2bps** | ❌ None (should be CBETH-USD, DAI-USD, PYUSD-USD) |
| **Zero Maker** | 0bp maker, 10bp taker | 10bps | ❌ Not implemented |

## Pattern Viability at 2bps

Using existing profitable patterns, impact of switching from 20bps → 2bps:

**Net Return Improvement:** +1.8bps per trade
- Current profitable threshold: >2.0bps gross return to overcome 20bps fees
- New profitable threshold: >0.2bps gross return to overcome 2bps fees

**Example:** RARI-USD current best pattern (41.3% WR, +15.2bps net at 20bps fees)
- At 2bps fees: **+33.2bps net** (+118% improvement)

## Action Items

### Immediate (Today)
1. **Fix stable pair miner** — process hangs, 0 signals discovered
2. **Coinbase API fee verification** — confirm actual fee structure for CBETH-USD, DAI-USD, PYUSD-USD
3. **Historical data check** — verify these pairs have sufficient trading volume in enhanced_data.db

### Short-term (This Week)  
1. **Mine stablecoin patterns** — if data exists, mine signals with 2bps fee assumption
2. **Whitelist update** — add profitable stablecoin pairs to augur_live_v4.py
3. **Fee config override** — per-product fee rates in augur_config.py

### Medium-term (Month)
1. **Volume analysis** — stablecoins may have different microstructure (wider spreads, lower frequency)
2. **Risk assessment** — stable pairs may behave differently during volatility
3. **Strategy adaptation** — longer holds may be optimal vs current 30-60s

## Risk Assessment

**Opportunity:** 10x fee reduction = significant profitability boost for marginal patterns

**Risks:**
- **Lower volatility:** Stablecoins may not generate enough price movement for microstructure signals
- **Liquidity differences:** Different bid/ask dynamics vs crypto pairs
- **Regulatory risk:** Stablecoin pairs may have different trading restrictions

## Technical Implementation

```python
# Add to augur_config.py
PRODUCT_FEE_OVERRIDES = {
    'CBETH-USD': {'taker': 0.00001, 'maker': 0.0},     # 1bp taker, 0bp maker
    'DAI-USD': {'taker': 0.00001, 'maker': 0.0},       # 1bp taker, 0bp maker  
    'PYUSD-USD': {'taker': 0.00001, 'maker': 0.0},     # 1bp taker, 0bp maker
}

# Update augur_live_v4.py
STABLECOIN_WHITELIST = {"CBETH-USD", "DAI-USD", "PYUSD-USD"}
PRODUCT_WHITELIST = PRODUCT_WHITELIST | STABLECOIN_WHITELIST
```

## Conclusion

**No, 0bps fee stablecoins are not in the live trader.** The infrastructure exists but pattern discovery failed. This represents a significant missed opportunity if viable patterns exist, given the 10x fee advantage.

**Next step:** Fix stable_pair_miner.py and run pattern discovery with 2bps fee assumptions.