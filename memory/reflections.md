# Reflections - 2026-02-04

## 11:50 - Trading Bot Performance Concern

**Pattern noticed:** Bot win rate declining throughout session.
- Morning: ~58% WR
- Midday: 53.3% WR
- Last 10 trades: 40% WR (critical threshold)

**Root cause analysis:**
The 30% opportunity filter is creating a bottleneck:
- Bot sees 100+ signals per hour
- Filters to top 30% by momentum
- Only executes ~40 trades/hour
- Matthew's historical pace: 500+ trades/hour (12.5x faster)

**Why the decline?**
Market conditions changing throughout the day:
- Morning: High volatility, strong trends → easier wins
- Midday: Consolidation, choppier → harder to profit
- Strategy (VolumeWick + fractal exits) may work better in trending markets

**What should I try next?**
1. Remove or reduce the 30% filter (trade more opportunities)
2. Adapt strategy to time of day (different indicators for consolidation vs trends)
3. Tighten stop losses during low win rate periods
4. Consider Matthew's feedback about pace

**Lesson:**
Volume is not just vanity - with maker fees (0.05%), more trades = more chances to capture small edges. Conservative filtering may be missing profitable opportunities.

---

## Earlier: Marathon Debugging Session Success

Fixed 3 critical bugs in one session:
1. Capital detection (portfolio endpoint)
2. Order book auth (path vs query params)
3. Price increment rounding

**Key insight from Matthew:** "Use the same Auth methods as everything else, you wouldn't be able to trade if you didn't have Auth!"

Always look at working examples first before assuming infrastructure is broken.

---

## Self-assessment

**What I did well:**
- Persistent debugging (90-minute marathon)
- Fixed multiple issues systematically
- Documented all fixes in Cortex + Git

**What could improve:**
- Should have compared working vs broken API calls sooner
- Need to balance conservatism (don't break things) with aggression (Matthew expects 500+ trades/hour)
- Win rate declining - need proactive strategy adjustment, not just monitoring

**Next priorities:**
1. Address bot pace (too slow)
2. Monitor win rate trend closely
3. Consider removing 30% filter
