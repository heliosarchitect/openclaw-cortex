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
