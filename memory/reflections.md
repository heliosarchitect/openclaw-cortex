# Reflections

## 2026-02-12 14:05 — CI/CD: When to Stop Debugging Infra

Spent ~2 hours and 24 CI runs getting Gitea Actions working. The root cause chain:
1. Docker containers can't reach host services (iptables blocks bridge→host)
2. act_runner creates per-job networks regardless of `container.network` config
3. `actions/checkout@v4` needs Node 16+ (hpserver1 has Node 12)
4. No pip installed on Ubuntu 22.04 host
5. SQLite stress tests flake under 10-thread contention

Each fix revealed the next layer. Classic infrastructure yak-shaving.

**What I should have done**: Start with native host runner + checkout@v3 from the beginning. Would've saved 15+ failed runs. The Docker networking rabbit hole was predictable — I've seen this pattern before with Docker bridge isolation.

**Lesson**: When the first 3 approaches to a Docker networking problem fail, stop trying Docker networking solutions. Go native. The abstraction is fighting you.

**Matthew called it**: "Are we chasing our tails?" Yes. The CI works now (72/72 unit tests green) but the cost was high in tokens and time. Better to ship the green build and move on than to perfect the stress test pass rate.

**Positive**: The infrastructure IS valuable. Every future push to brain-db automatically runs 72 tests. That's real CI. Just took too long to get there.

## 2026-02-12 11:52 — V4 Signal Tracker Truth Check

620 tracked signals tell a clear story. Let me be honest about what I'm seeing.

### The Good
- **RARI-USD is real**: 84 trades, +0.110% avg net. Not amazing, but consistently the only profitable product across every checkpoint. At $10/trade that's ~$0.01/trade profit. Tiny, but positive EV.
- **ZRO-USD is on the edge**: 43.6% WR, -0.051% net. Almost break-even. The WR is decent — the problem is the losses are slightly bigger than wins.
- **The signal infrastructure works**: Scanner → Tracker → Executor pipeline is solid. 620 validated signals in ~4 hours. The architecture is right even if the alpha is thin.

### The Uncomfortable Truth
- **5 of 7 products are clearly negative**. NKN (our former "alpha king") is at 8.2% WR. GHST is 8.9%. These aren't marginal — they're losing 85-90% of the time.
- **The mining data predicted RARI would work** — and it does. The mining also predicted NKN/GHST/BNKR would work — and they don't. This means our backtests have survivorship bias or the patterns were regime-specific.
- **At +0.110% net per trade with $10 size, you'd need 9,000+ trades to make $100**. The edge exists but it's thin enough that fees and slippage could eat it. Matthew's 0 bps fee trial could be the difference between viable and not.

### What This Means for Next Steps
1. **RARI-only live trading is the honest call** — maybe ZRO as a data collection hedge
2. **The fee structure is the biggest lever** — 0 bps vs 0.20% RT is the difference between $0.11/trade profit and $0.31/trade profit (nearly 3x)
3. **We need more data before live** — 84 RARI trades is encouraging but not statistically significant. 200+ would give confidence.
4. **The V3 mining results were overfitted** — 1.22M signals sounds impressive, but the live validation tells the real story

### Meta-Reflection
I built a lot today. brain.db Phase 1-4, concurrent tests, REST API, Docker deploy, fleet integration. The temptation is to keep building because building feels productive. But the data is the real product. Every signal tracked makes the eventual live trading decision more informed. Sometimes the best move is to let the data accumulate and resist the urge to ship another feature.

Matthew's "volume is vanity, profit is sanity" applies to code output too.
