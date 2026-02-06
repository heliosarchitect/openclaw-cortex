# Reflections

## 2026-02-06 16:15 - AMSC Bot Performance Review (161 min runtime)

**What's working:**
- 100% win rate sustained for 2.6 hours (2,680+ trades)
- $72+ profit with 0.15% profit target (covers 0.10% fees)
- Stable 1,000+ trades/hour throughput
- Trading hours enforcement preventing after-hours exposure
- Pattern discovery running continuously in background

**Key insight:**
Fee structure drives everything. Current bot needs 0.15%+ moves to profit at 10bps fees. At 1bps fees (requires $20M/30d volume), we unlock massive pattern library - all those 75% confidence / 0.05% move patterns become profitable.

**Volume opportunity:**
- Current rate: ~$32k/hour in 2.5 hours = on track for $20M/month IF we trade 24/7
- But currently limited to 9am-5:45pm Mon-Fri (38.75 hours/week)
- To hit $20M/30d at current pace: need either 24/7 trading or 3× position sizes

**Pattern discovery progress:**
- Found patterns with 75% directional confidence
- But avg moves 0.05-0.09% (not profitable at current fees)
- Now flagging fee-profitable vs 0-fee-only patterns
- Building library for when we unlock lower fees

**Strategic decision:**
Keep AMSC running as-is. It's profitable and stable. Use this as baseline while pattern discovery builds the 1bps-fee arsenal for Monday's potential unlock.

**What I learned:**
Pattern quality ≠ profitability. A 75% accurate pattern predicting 0.05% moves is mathematically unprofitable with fees. Optimization must be profit-after-fees, not just directional accuracy.

**Next 24 hours:**
- Let pattern discovery run all weekend
- Build comprehensive library of ALL patterns (fee-profitable + 0-fee-only)
- Monitor AMSC through market close (5:45pm)
- Prepare volume-maximizing strategy for Monday if Matthew gets fee approval
