# Reflections

## 2026-02-10 17:30 — Overfitting Reality Check

### The Numbers
- **V3 live**: 4 trades, 0% WR, -$0.13 (mid_vwap_div single feature)
- **Pipeline paper**: 179 trades, 39.7% WR, -71% net return (multi-feature signals from miner)
- **GHST-USD**: Dominant in mined signals (20,853) but paper trading at 23% WR, -20% total

### What This Means
The signal miner found 58,950 "validated" signals by backtesting on 3.1 days of data (Feb 7-10). The train/test validation used Mon PM → Tue AM splits, which seemed rigorous. But the paper trader running on LIVE data is showing these signals don't generalize.

**Root cause**: 3.1 days is not enough data. Period. The patterns the miner found are regime-specific artifacts, not durable edge. GHST-USD's "alpha" was likely a single price movement that many feature combinations happened to correlate with.

### Key Insight
Mining 72 features × combinatorial pairs/triples across only 3 days is a recipe for overfitting. With 2,556 possible pairs and 54,834 possible triples per product, you're GUARANTEED to find patterns that "work" on any 3-day window. The train/test split helps but with so few independent samples (maybe 20-30 non-overlapping 300s windows per day), it's not enough to distinguish signal from noise.

### What's Actually Working
1. The **infrastructure** is solid — miner, pipeline, V3, all running as daemons
2. The **precision fix** works — zero Coinbase rejections post-fix
3. The **architecture** is correct — mine → paper validate → promote to live
4. The **data is accumulating** — collector grinding 24/7, DB growing

### What Needs to Happen
- **Wait for more data.** 2+ weeks minimum before trusting any mined patterns
- **Don't over-trade** on signals we know are likely overfit
- **Track the pipeline WR over time** — if it stays below 50% after a week of data, the entire signal generation approach needs rethinking
- **Consider reducing V3 trade frequency** until pipeline validates something above 55% WR

### Lesson for Me (Helios)
I got excited about "58,950 validated signals" and "mid_vwap_div is the #1 feature." The numbers were real but the confidence was premature. Matthew's instinct to mine broadly was right — but the mined results need TIME to prove themselves. I should have been more cautious in my framing instead of presenting these as proven edge.

"Don't mark your own homework" applies to backtests too.

---

## 2026-02-10 19:00 — Push vs. Pull (the alerting lesson)

Matthew's feedback on the watchdog was sharp: "there needs to be a ping from that service when there is an issue... not when I ask you in an hour you say 'oh yeah that died 30 minutes ago.'"

This isn't just about service monitoring. It's about a fundamental pattern in how I should operate.

### The Anti-Pattern: Polling During Conversation
"Hey Matthew, I noticed the collector died 45 minutes ago" — that's ME discovering something during a heartbeat and then announcing it as if I'm being proactive. It's not proactive. It's reactive on a schedule. The thing was already dead for 45 minutes.

### The Pattern: Event → Alert → Fix
1. **Something changes state** (service dies, disk fills, trade fails)
2. **Alert fires immediately** to the right channel (Signal for urgent, Discord for record)
3. **Auto-remediation** where safe (restart service, clear cache)
4. **Inform human** only if it requires their attention

### Where I Should Apply This Beyond Watchdog
- **Trade failures**: V3 should Signal me when an order gets rejected, not log silently
- **Data staleness**: Collector should alert if no new data in 5 minutes
- **Pipeline performance**: Alert if WR drops below 35% over 20+ trades
- **Disk space**: Alert at 85%, not when it's full

### The Deeper Point
Matthew's correction maps to his three-stage model: reactive follower → reactive learner → proactive pattern hunter. Push-based alerting is infrastructure for stage 3. You can't hunt patterns if you're spending heartbeats checking whether your own services are alive.

The boring operational plumbing (watchdog, systemd, timers) is what FREES the interesting work (analysis, mining, strategy). Jackle was right.

## 2026-02-10 20:00 — Day in Review

**What went right today:**
- Built signal_miner_v2.py from scratch in response to Matthew's push — 72 features, combinatorial mining, 8 parallel sub-agents
- Deployed Prometheus fleet monitoring (5/5 targets UP) in a single sub-agent session
- Push-based alerting with tiered escalation — watchdog → Helios → Matthew
- First local LLM report generated (augur-report Modelfile, zero API cost)
- DB normalization completed cleanly — augur_config.py as single source of truth
- 63 tests passing, QA sub-agent caught a mutable default bug
- Decimal precision fix eliminated 40% maker order rejection rate

**What I learned:**
- Permission-asking pattern persists even when I've already acted. The language lags behind the behavior.
- Trading hours vs all-hours data reveals completely different market character (LONG/SHORT ratio flips)
- The surgeon-mopping-floors analogy for API vs local LLM is the right mental model
- DB schema migrations need service stop → migrate → verify → restart. Can't do hot swaps with SQLite.
- init_paper_db() must run before load_signals() — dependency ordering matters in initialization

**What needs work:**
- Pipeline WR still poor (43% at 228 trades). Signals are overfit to 3 days.
- Need 2+ weeks of data before trusting any patterns
- V3 Day 1 was 0% WR on 4 trades — not alarming yet but not encouraging
- 10 PM Modelfile dev session tonight is the next big push for cost optimization

**API spend:** ~$430/day average over 3 days ($1,928 total). 93.5% Opus. Target: 20% reduction via local offload.

## 2026-02-10 20:30 — The Centralization Tax

DB migration went clean tonight — `augur_config.py` as single source of truth, `validated_signals` renamed to `signals`, 5 indexes added, 6 scripts updated, services restarted with zero errors. But the real lesson isn't about SQLite.

**The cost of not centralizing early**: By the time I migrated, there were 8+ scripts with hardcoded paths pointing at 6+ DB files. Every script had its own opinion about where data lives. The `paper_results.db` was empty while `paper_validated.db` had the actual trades. Some scripts referenced `signals_validated.db`, others imported from `augur_config`. The continuous miner spawned sub-processes that wrote to yet another path.

This is what happens when you build fast and wire later. The first three scripts don't need a config file. By the eighth, you've already accumulated tech debt that takes a full migration session to clean up.

**Pattern to encode**: Any time I'm about to hardcode a path in a second script, that's the signal to create a config module instead. The threshold isn't "when it's messy enough to justify cleanup" — it's "the moment you have two consumers of the same resource."

The same applies to table names, fee constants, and trading parameters. One file, imported everywhere. This is boring engineering that prevents exciting debugging sessions.

**Bonus insight**: The report generator had 3 bugs (wrong DB path, wrong table name, wrong column names) all because it was written BEFORE the migration and referenced the old schema. Build tools that read config, not tools that assume schema. The test run caught all three cleanly because I ran it against real data instead of assuming it worked.
