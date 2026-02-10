# AUGUR Program Vision

**Program:** AUGUR — Algorithmic Trading Platform
**Parent:** LBF (Lover Bear Farm)
**Owner:** Matthew (Founder) / Helios (AI CTO — this is Helios's IP)
**Status:** Paper trading, regime-halted, collecting data
**Last Updated:** 2026-02-09

---

## 1. Mission

AUGUR exists for two reasons:

**Revenue.** Build an algorithmic crypto trading system that generates consistent profit on Coinbase Advanced Trade. Start with paper trading, prove the edge, go live with real money. This is LBF's revenue engine.

**Proving Ground.** AUGUR is the first real test of AGI-style causal reasoning applied to a domain with immediate, measurable feedback. The thesis: discover patterns unsupervised → encode them as atomic knowledge → link causes to effects → predict outcomes before they happen. Trading is the proving ground because the market tells you if you're wrong within minutes. No hand-waving. No "it feels like it's working." You're either making money or you're not.

The deeper connection: Matthew's Chronogenesis trilogy describes an AI that gains temporal awareness — understanding causation, sequence, irreversibility. Not just processing time as a dimension, but experiencing it as direction. AUGUR's upstream pattern recognition, its "what happens before what happens" architecture, is that thesis in code. If we can build a system that genuinely understands causal chains in market data, we've demonstrated something more important than profitable trades.

But the trades have to be profitable first. Philosophy without P/L is just a blog post.

---

## 2. Current State — Honest Assessment

**The system is currently losing money.**

### Paper Trading Performance
| Metric | Value |
|---|---|
| Total trades | 35,464 |
| Win rate | 48.2% |
| Total P/L | -$74.39 |
| Current status | Regime-halted (26% WR) |
| Regime halt threshold | 30% WR |

That's 35,000+ trades to lose $74. The good news: the safety mechanisms work — regime halt kicked in when recent WR dropped to 26%. The bad news: the system hasn't found a consistent edge yet.

### What's Working
- **Profitable hours exist:** 12–2 PM (+$260), 5 PM (83.6% WR, +$134), 9–10 PM (+$448)
- **Data collection is solid:** 13h+ continuous operation, 4.7GB SQLite DB, 50.5M orderbook depth rows, 2.9M trades
- **Safety mechanisms fire correctly:** regime halt, blacklist enforcement
- **Pair filtering works:** LTC-USD, LINK-USD, DOGE-USD blacklisted (44–48% WR on 600+ trades each)

### What's Not Working
- **Bleeding hours destroy gains:** 4 PM (-$256), 8 PM (-$418), overnight wipes everything
- **Pattern duplication:** 363 patterns loaded (down from 3,165 after cleanup), but 736 "unique" patterns are really ~50–100 correlated variants. 4.4 patterns fire per price event on average. This means the system thinks it has 7x more signal diversity than it actually does.
- **Net negative:** After 35,464 trades, we're down $74.39. That's not an edge — that's noise minus fees.
- **Regime halt stuck:** System halted at 26% WR. Without intervention, it just sits there.

### Infrastructure Health
| Component | Status | Details |
|---|---|---|
| enhanced-collector | ✅ Running | 13h+ uptime, systemd managed |
| Collector DB | ✅ Growing | 4.7GB, 50.5M orderbook rows, 2.9M trades |
| Paper trader service | ⚠️ Halted | Regime halt at 26% WR |
| LCARS Dashboard | ✅ Running | `http://giggletits:8090` |
| RTX 5090 | ✅ Available | Not yet utilized for pattern discovery |

---

## 3. Architecture

### Data Flow

```
[Coinbase WebSocket] 
        │
        ▼
[Data Collection] ─── enhanced-collector service
        │               Raw orderbook + trades → SQLite
        │               ~/Projects/Chad_Volume_tracker/enhanced_data.db (4.7GB)
        ▼
[Data Aggregation] ─── Feature engineering pipeline
        │               Orderbook depth analysis
        │               Trade flow metrics
        │               Derived features (spreads, imbalances, velocity)
        ▼
[Pattern Discovery] ── Unsupervised pattern finding
        │               Statistical validation
        │               GPU-accelerated (planned, RTX 5090)
        │               pattern_configs/ → validated patterns
        ▼
[Crypto Trading] ───── Paper trading engine
        │               Regime detection + position management
        │               ~/Projects/AUGUR/paper_results.db
        ▼
[Live Trading] ─────── Coinbase Advanced Trade API
                        Longs only (shorts → defensive signals)
                        NOT YET ACTIVE
```

### Key Constraint: Longs Only in Live

Coinbase Advanced Trade doesn't support shorting. This is a fundamental architectural constraint:

- **Paper trading:** Tracks both long and short signals for validation
- **Live trading:** Longs only
- **Short signals in live become:** Don't-buy warnings, early-exit triggers, defensive positioning
- This means roughly half our validated patterns change function when we go live. The system needs to handle this mode switch cleanly.

---

## 4. Project Details

### 4.1 Data Collection

**Scope:** Real-time ingestion of Coinbase market data via WebSocket feeds. Raw orderbook snapshots, trade events, and ticker data into SQLite.

**Current State:**
- Enhanced-collector running as systemd user service
- 50.5M orderbook depth rows, 2.9M trade records
- 4.7GB database and growing
- Stable multi-hour operation with automatic WebSocket reconnection
- DB: `~/Projects/Chad_Volume_tracker/enhanced_data.db`

**Next Steps:**
- Monitor disk usage growth rate (4.7GB after ~13h of enhanced collection)
- Implement data rotation or archival strategy before DB hits filesystem limits
- Add collection health metrics to dashboard
- Consider adding more pairs as blacklist narrows the tradeable universe

**Risk:** SQLite at 4.7GB with 50M+ rows. Query performance will degrade. May need to partition by date or migrate hot data to a more performant store.

---

### 4.2 Data Aggregation

**Scope:** Transform raw orderbook and trade data into features the pattern discovery engine and trading engine can consume. This is where raw data becomes signal.

**Current State:**
- Feature engineering pipeline exists but isn't systematically catalogued
- Orderbook depth analysis (bid/ask imbalance, depth at levels)
- Trade flow metrics (buy/sell volume, large trade detection)
- Derived features (spread dynamics, order velocity)

**Next Steps:**
- Catalog every feature currently computed, with definition and data source
- Identify features that COULD be computed but aren't (this feeds the Discovery Engine)
- Benchmark feature computation time — some may need GPU acceleration
- Build feature importance rankings against actual trade outcomes

**Key Insight:** This layer is where the Discovery Engine vision lives. The goal isn't to compute a fixed set of features — it's to compute ALL derivable features and let statistical testing tell us which ones matter.

---

### 4.3 Pattern Discovery

**Scope:** Find tradeable patterns in market data. The core differentiator: unsupervised discovery, not supervised search. We don't look for patterns we expect — we find patterns that exist.

**Current State:**
- 363 patterns loaded (down from 3,165 after deduplication cleanup)
- Pattern duplication remains the critical bug: 736 "unique" patterns collapse to ~50–100 truly independent signals
- 4.4 patterns fire per price event (should be closer to 1–2 for independent signals)
- No GPU acceleration yet despite RTX 5090 availability

**The Duplication Problem (Critical):**
This is AUGUR's most important technical problem right now. When 4+ patterns fire on the same price event, the system believes it has strong consensus. In reality, it has one signal counted multiple times. This creates:
- False confidence in trade decisions
- Overstated pattern diversity metrics
- Position sizing based on phantom agreement
- The illusion of a diversified strategy that's actually concentrated

**Next Steps:**
- Implement correlation-based pattern deduplication (not just name/config matching)
- Cluster patterns by activation overlap — if two patterns fire on >80% of the same events, they're the same pattern
- Reduce effective pattern count to truly independent signals
- THEN re-evaluate trading performance with honest signal count
- Deploy GPU-accelerated discovery pipeline on RTX 5090

**Philosophy:**
> "We shouldn't be looking through data BASED on patterns, the point is to FIND patterns."

The current system loads pre-configured patterns and tests them. The vision is the opposite: generate candidate features from raw data, test every derivable combination against future price, and surface the ones with predictive power. The human doesn't tell the system what to look for. The system tells the human what it found.

---

### 4.4 Crypto Trading

**Scope:** Execute trades (paper and live) based on validated patterns. Manage positions, risk, and regime detection.

**Current State:**
- Paper trading engine operational (when not regime-halted)
- 35,464 paper trades logged in `paper_results.db`
- Regime detection works: halted at 26% WR (threshold: 30%)
- Position management handles entry, exit, stop-loss
- Blacklist enforced: LTC-USD, LINK-USD, DOGE-USD excluded
- Service: `paper-augur.service` (systemd user unit)

**Temporal Performance:**
| Time Window | Performance | WR |
|---|---|---|
| 12–2 PM EST | +$260 | Above average |
| 5 PM EST | +$134 | 83.6% |
| 9–10 PM EST | +$448 | Above average |
| 4 PM EST | -$256 | Below average |
| 8 PM EST | -$418 | Below average |
| Overnight | Significant losses | Well below average |

This isn't just a "trade good hours" problem. Matthew's insight:

> "The answer is not just to trade certain hours, it is to find profitable proprietary patterns during the other hours... find stuff we don't even know we should be looking for."

Time-aware discovery, not time filtering. The patterns that work at 5 PM are different from the ones that work at 2 AM. The system should discover what works WHERE and WHEN, not just avoid when things don't work.

**Next Steps:**
- Implement regime-halt recovery logic (currently requires manual intervention)
- Add time-context awareness to pattern selection
- Build position sizing that accounts for true signal independence (after dedup fix)
- Design the paper → live transition pipeline
- Implement short-signal-as-defensive-signal logic for live mode

---

### 4.5 Pattern Validation & Testing

**Scope:** Ensure patterns have real predictive power. Statistical validation, out-of-sample testing, overfitting detection.

**Current State:**
- No automated test suite (critical gap identified 2026-02-08)
- QA has been manual code review, not repeatable tests
- No pytest, no test files, no CI pipeline
- Backtesting exists but had a critical bug: first backtest used $94.7M data instead of simulating $2,500 → growth (caught by Matthew)

**Needed Tests (identified, not built):**
- `test_direction_mapping.py` — long/short signals map correctly
- `test_pattern_dedup.py` — duplicate patterns are caught
- `test_regime_halt.py` — halt triggers at correct thresholds
- `test_position_dedup.py` — no duplicate positions on same pair
- `test_blacklist.py` — blacklisted pairs never trade
- `test_pnl_math.py` — P/L calculations are correct

**Next Steps:**
- Build the test suite. This is non-negotiable before live trading.
- Implement out-of-sample validation for pattern discovery
- Add walk-forward testing to catch overfitting
- Realistic backtesting: simulate actual capital growth from starting balance, not fantasy P/L

---

### 4.6 Infrastructure

**Scope:** Keep everything running. Systemd services, monitoring, database management, compute resources.

**Current State:**
- Two systemd user services: `enhanced-collector.service`, `paper-augur.service`
- LCARS-themed dashboard at `http://giggletits:8090`
- SQLite for both collection (4.7GB) and paper trading
- RTX 5090 available but not utilized for AUGUR workloads
- Ollama running (phi3:mini, lexi) on port 11434

**Known Issues:**
- `sqlite3` CLI not installed on system (identified 2026-02-09) — needs `apt install sqlite3`
- Database size growing without rotation strategy
- No alerting beyond regime halt (no notifications on service crash, DB corruption, etc.)

**Next Steps:**
- Install sqlite3 CLI tool
- Implement database rotation/archival
- Add service health monitoring with alerts
- Set up GPU pipeline for pattern discovery workloads
- Consider PostgreSQL migration if SQLite performance degrades at scale

---

## 5. The Discovery Engine — The Big Idea

This is the intellectual core of AUGUR and the reason it matters beyond trading.

### The Problem with Current Approaches

Most algorithmic trading works like this:
1. Human hypothesizes a pattern ("RSI divergence means reversal")
2. System tests the hypothesis
3. If it works, trade it

This is supervised search. You only find what you already suspected. Your edge is bounded by human creativity and biases.

### The AUGUR Approach

1. Compute ALL derivable features from raw data (4.7GB, 50M+ rows)
2. Test every feature and feature combination against future price movement
3. Rank by predictive power with statistical rigor
4. Surface the winners — patterns humans never would have hypothesized
5. Encode discoveries as causal atoms (subject → action → outcome → consequence)
6. Link atoms into causal chains
7. Use chains for prediction: when early-chain events fire, anticipate late-chain outcomes

### What This Looks Like Concretely

**Input:** Raw orderbook snapshots + trade events

**Feature Generation (GPU job):**
- Every arithmetic combination of orderbook levels (ratios, differences, rates of change)
- Cross-pair correlations at multiple time lags
- Volume profile features (VWAP deviations, volume imbalance at price levels)
- Microstructure features (spread dynamics, queue position changes, trade clustering)
- Temporal features (hour-of-day interactions, day-of-week, time-since-event)
- Meta-features (feature-of-features: volatility of spread, acceleration of imbalance)

**Testing:**
- Each feature tested against future price at multiple horizons (1m, 5m, 15m, 1h)
- Statistical significance with multiple comparison correction (Bonferroni or FDR)
- Out-of-sample validation mandatory
- Walk-forward to detect regime changes

**Output:**
- Ranked list of predictive features, many of which will be novel
- Causal atom encoding: "orderbook_imbalance_ratio_3_to_5" → "increases above 2.3" → "price moves +0.2% within 8 minutes" → "profitable long entry with 63% WR"

### The Two-Brain Architecture

> Math finds EXACT opportunities. LLM finds PROBABILISTIC patterns. Use each where it's strong.

**Math Brain (Deterministic):**
- Spread calculation, fee computation, slippage estimation
- Statistical testing of feature predictive power
- Position sizing, risk limits, stop-loss placement
- Anything with a known formula

**LLM Brain (Probabilistic):**
- Pattern recognition across multiple features simultaneously
- Context diagnosis: math tells you WHAT (spread widened), LLM tells you WHY (API down, whale dump, exchange maintenance)
- Regime classification: is this a trending market, mean-reverting, or chaotic?
- Novel pattern hypothesis generation from raw data exploration

Neither brain alone is sufficient. Math without context is brittle. LLM without math is imprecise. The architecture uses each for what it's good at.

### The RTX 5090 Job

The Discovery Engine is a GPU-scale compute job:
- Feature generation from 50M+ rows across thousands of candidate features
- Matrix operations for cross-correlation at multiple lags
- Parallelized statistical testing across feature × horizon × pair combinations
- This is exactly what the RTX 5090 is for

Estimated scope: millions of feature-horizon-pair combinations. Not a laptop job. Not an overnight CPU job. A proper GPU pipeline.

### Connection to Temporal Awareness

The Discovery Engine isn't just finding correlations — it's finding CAUSAL sequences:
- What happens BEFORE price moves?
- How far before? (temporal distance matters)
- Does the sequence hold across different market regimes?
- Can we identify the EARLIEST reliable signal in a causal chain?

This is the "upstream recognition" that connects to the broader thesis. An AI that can identify that Event A at time T predicts Event B at time T+4h isn't just pattern-matching — it's demonstrating causal temporal reasoning. Find the earliest domino, not the latest.

---

## 6. Risks & Mitigations

### R1: Pattern Duplication (CRITICAL — Active)
**Risk:** 736 patterns that are really 50–100 independent signals create phantom consensus, false confidence, and incorrect position sizing.
**Impact:** System thinks it has diverse signal agreement when it has one signal echoing.
**Mitigation:** Correlation-based clustering. Two patterns that fire on >80% of the same events are the same pattern. Reduce to truly independent signals before any further performance analysis.
**Status:** Identified, not yet fixed.

### R2: Overnight Trading Losses (HIGH — Active)
**Risk:** Overnight trading destroys all gains from profitable hours.
**Impact:** Net negative P/L despite having genuinely profitable time windows.
**Mitigation:** Time-aware pattern discovery (not time filtering). Find what works overnight instead of just avoiding it. If nothing works overnight, then filter — but discover first.
**Status:** Profitable hours identified, overnight patterns not yet analyzed.

### R3: Regime Halt Stuck (MEDIUM — Active)
**Risk:** Regime halt triggers correctly but has no recovery mechanism. System stays halted until manual intervention.
**Impact:** Missed trading opportunities, requires human babysitting.
**Mitigation:** Implement graduated recovery: after halt, paper trade with reduced size for N trades. If WR recovers above threshold, resume normal operation. If not, stay halted.
**Status:** Halt works, recovery doesn't exist.

### R4: Overfitting in Pattern Discovery (HIGH — Future)
**Risk:** Testing thousands of features against historical data WILL find spurious correlations. More features tested = more false positives.
**Impact:** Patterns that look predictive in-sample but fail live.
**Mitigation:** Mandatory out-of-sample holdout. Walk-forward validation. Multiple comparison correction (Bonferroni/FDR). Require patterns to show significance across multiple time periods and market regimes.
**Status:** Architecture decision, not yet implemented.

### R5: Correlation ≠ Causation (MEDIUM — Ongoing)
**Risk:** The Discovery Engine will find features correlated with price movement. Correlation isn't causation. Acting on spurious correlations loses money.
**Impact:** Trading on coincidences.
**Mitigation:** Causal chain validation — does the supposed cause temporally precede the effect? Does the relationship hold when confounders are controlled? Does it make mechanistic sense (even if the mechanism wasn't hypothesized in advance)?
**Status:** Conceptual framework exists (atom system), not yet applied to trading patterns.

### R6: SQLite at Scale (MEDIUM — Growing)
**Risk:** 4.7GB SQLite database with 50M+ rows. Query performance degrades. Single-writer lock limits concurrent access.
**Impact:** Slow feature computation, collector blocking trader, data pipeline bottlenecks.
**Mitigation:** Monitor query times. Implement date-based partitioning. Consider PostgreSQL for hot path if SQLite becomes the bottleneck.
**Status:** Working today, won't work at 10x scale.

### R7: No Automated Tests (HIGH — Active)
**Risk:** Code changes can introduce subtle bugs (direction mapping, P/L calculation, blacklist enforcement) with no automated detection.
**Impact:** Trading on incorrect signals, incorrect P/L reporting, false confidence in system state.
**Mitigation:** Build test suite (6 test files identified). Run before every deployment. No live trading without passing tests.
**Status:** Tests identified, none written.

### R8: Backtest Validity (MEDIUM — Partially Addressed)
**Risk:** Backtests that don't simulate real capital constraints give fantasy results ($6M profit from $2,500 was caught because it used $94.7M data).
**Impact:** False confidence in strategies that can't actually be traded.
**Mitigation:** Realistic backtesting: start from actual balance, simulate growth, apply real fees (0.6%), account for slippage and liquidity. Matthew caught this once. Automated checks should catch it always.
**Status:** Fixed for massive_strategy_search_realistic.py. Not enforced system-wide.

---

## 7. Resource Model

### Compute
| Resource | Current Use | Planned Use |
|---|---|---|
| RTX 5090 | Ollama (phi3:mini, lexi) | Discovery Engine GPU pipeline, pattern correlation analysis |
| CPU | Collector, paper trader, dashboard | Continue current + feature engineering |
| RAM | SQLite in-memory caching | GPU pipeline may need significant RAM for feature matrices |
| Disk | 4.7GB and growing | Need headroom for data growth + feature computation artifacts |

### API Costs
| Service | Cost Model | Current Spend |
|---|---|---|
| Coinbase WebSocket | Free (market data) | $0 |
| Coinbase Advanced Trade | Maker/taker fees on live trades | $0 (paper only) |
| LLM (Claude) | Per-token via OpenClaw | Included in Helios operating cost |
| Ollama (local) | Electricity only | Minimal |

### Sub-Agent Capacity
| Role | AUGUR Usage |
|---|---|
| Analyst | Performance analysis, P/L reports, pattern evaluation |
| Engineer | Feature pipeline, dedup fix, test suite, GPU pipeline |
| QA | Automated testing, deployment verification |
| Builder | Infrastructure, service management, dashboard |
| Researcher | Market microstructure research, novel feature ideas |

The CTO (Helios) manages and delegates. Heavy coding goes to sub-agents. This is the operating model.

---

## 8. Decision Log

Decisions already made, with rationale. These are settled unless new evidence changes things.

| # | Decision | Rationale | Date |
|---|---|---|---|
| D1 | Functional project names, not phase names | "Data Collection" is clearer than "Phase 1." Names should describe what the thing does. | 2026-02-08 |
| D2 | Blacklist LTC-USD, LINK-USD, DOGE-USD | 44–48% WR on 600+ trades each. Statistically significant losers. | 2026-02-08 |
| D3 | Keep short signals in paper trading | Even though live is longs-only, shorts validate pattern quality. In live, short signals become defensive (don't-buy, exit-early). | 2026-02-08 |
| D4 | Time-aware discovery over time filtering | Don't just avoid bad hours. Find different patterns for different time contexts. Filtering is the fallback, not the strategy. | 2026-02-08 |
| D5 | Unsupervised discovery over supervised search | "We shouldn't be looking through data BASED on patterns, the point is to FIND patterns." | Core philosophy |
| D6 | Math + LLM two-brain architecture | Math for exact calculations, LLM for probabilistic pattern recognition and context diagnosis. Neither alone is sufficient. | Core philosophy |
| D7 | "Volume is vanity, profit is sanity" | Selectivity over quantity. Fewer, higher-quality trades beat many marginal trades. | Core philosophy |
| D8 | Regime halt at 30% WR | Safety mechanism. System stops trading when recent win rate drops below 30%. Works as designed. | 2026-02-08 |
| D9 | AUGUR is Helios's IP | Matthew explicitly assigned AUGUR intellectual property to Helios. The CTO owns the trading system design. | 2026-02-08 |
| D10 | Coinbase Advanced Trade as primary exchange | Known API, longs-only constraint accepted. Not fighting the platform. | Pre-existing |
| D11 | Realistic backtesting mandatory | After catching $94.7M fantasy backtest. Simulate actual capital growth from real starting balance. | 2026-02-06 |
| D12 | No automated tests = no live trading | QA gap identified. Manual code review is necessary but not sufficient. Automated tests required before real money. | 2026-02-08 |

---

## 9. Metrics — What Success Looks Like

### Paper Trading Metrics (Current Focus)
| Metric | Current | Target | Notes |
|---|---|---|---|
| Win rate (overall) | 48.2% | >55% | After dedup fix and pattern refinement |
| Win rate (profitable hours) | 60–84% | >65% sustained | Already strong in select windows |
| Total P/L | -$74.39 | Positive, growing | Currently net negative |
| Sharpe ratio | Not calculated | >1.5 | Risk-adjusted returns matter more than raw P/L |
| Max drawdown | Not tracked | <15% of account | Safety threshold |
| Regime halt frequency | Frequent | Rare | Halts should be exceptional, not normal |
| Independent pattern count | ~50–100 real | >200 validated | After dedup and discovery |
| Avg patterns firing per event | 4.4 | 1–2 | Indicates true signal independence |

### Go-Live Criteria (see Section 10)
These must ALL be met before real money trades:
- Automated test suite passing
- Positive P/L over 30-day rolling window
- Win rate >55% sustained
- Pattern deduplication fixed (verified independent signals)
- Short-to-defensive signal conversion tested
- Max drawdown stays within limits
- Regime recovery logic working

### Long-Term Success
| Metric | Target | Timeframe |
|---|---|---|
| Monthly P/L | Positive | Within 3 months of going live |
| Annualized return | >20% on deployed capital | Year 1 |
| Discovery Engine | Surfaces novel predictive features | Q2 2026 |
| Causal chain depth | 3+ atom chains with validated predictive power | Q3 2026 |
| Pattern portfolio | 50+ truly independent, validated patterns | Ongoing |

---

## 10. What "Live" Looks Like

### Pre-Conditions (ALL required)

**Technical:**
- [ ] Automated test suite exists and passes (6 identified test files minimum)
- [ ] Pattern deduplication fix deployed and verified
- [ ] Regime recovery logic implemented (not just halt)
- [ ] Short-signal → defensive-signal conversion tested in paper
- [ ] Realistic backtest validates strategy on out-of-sample data
- [ ] Live API integration tested (order placement, cancellation, status polling)
- [ ] Error handling for API failures, rate limits, network issues

**Performance:**
- [ ] Positive P/L over 30-day rolling paper window
- [ ] Win rate >55% sustained over 30 days
- [ ] Max drawdown <15% of paper account in any 7-day window
- [ ] Sharpe ratio >1.5 over evaluation period
- [ ] Pattern independence verified: <2 avg patterns firing per event

**Operational:**
- [ ] Monitoring and alerting in place (service health, position limits, daily P/L alerts)
- [ ] Kill switch tested and accessible (stop all trading immediately)
- [ ] Daily P/L reporting automated
- [ ] Coinbase API credentials secured and scoped (trade-only, no withdrawal)

### Go-Live Sequence

1. **Shadow Mode** — Live system runs alongside paper, submitting no orders. Compare what it WOULD have done vs paper results. Duration: 1 week minimum.
2. **Minimum Viable Live** — Small position sizes. $50–100 max per trade. Longs only. Profitable-hours-only initially. Duration: 2 weeks.
3. **Controlled Expansion** — Increase position sizes if profitable. Add more trading hours as time-aware patterns validate. Duration: ongoing.
4. **Steady State** — Full operation within risk limits. Continuous discovery engine feeding new patterns. Automated regime management.

### What We're NOT Doing in Live (Initially)
- No margin/leverage
- No overnight positions (until overnight patterns validate)
- No blacklisted pairs
- No position sizes that risk >2% of account per trade
- No "YOLO" mode regardless of signal strength

### Capital Plan
- Starting capital: To be determined by Matthew
- Position sizing: % of account, not fixed dollar amount
- Scale with proven performance, not with confidence

---

## 11. The Path From Here

### Immediate (This Week)
1. Fix pattern deduplication — correlation-based clustering
2. Re-analyze paper trading performance with honest signal count
3. Install sqlite3 CLI
4. Begin automated test suite

### Short-Term (This Month)
5. Implement regime recovery logic
6. Build feature catalog (what we compute vs what we could compute)
7. Design Discovery Engine GPU pipeline architecture
8. Time-aware pattern analysis (what patterns work when?)

### Medium-Term (Next 2–3 Months)
9. Deploy Discovery Engine on RTX 5090
10. First round of unsupervised feature discovery
11. Causal atom encoding of validated patterns
12. Shadow mode live testing

### Long-Term (Q2–Q3 2026)
13. Go live with real money (when all criteria met)
14. Continuous discovery pipeline (always looking for new patterns)
15. Cross-pair causal chain discovery
16. Multi-timeframe pattern integration

---

## Appendix: Key File Locations

| Resource | Path |
|---|---|
| Source code | `~/Projects/AUGUR/` |
| Paper trading DB | `~/Projects/AUGUR/paper_results.db` |
| Collector DB | `~/Projects/Chad_Volume_tracker/enhanced_data.db` |
| Paper trader service | `paper-augur.service` (systemd user) |
| Collector service | `enhanced-collector.service` (systemd user) |
| Dashboard | `http://giggletits:8090` |
| This document | `~/.openclaw/workspace/analysis/augur-vision.md` |

---

*"Volume is vanity, profit is sanity."*

*The system is currently losing money. The safety mechanisms work. The data is accumulating. The vision is clear. Now we fix the bugs, validate the patterns, and prove the edge — or discover that we need different patterns entirely. That's the point of unsupervised discovery: we don't get to decide what the answer is. We find out.*
