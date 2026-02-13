# 🔥 AUGUR 4-Hour Blitz Sprint
<!-- AI.TOC: 🔥 AUGUR 4-Hour Blitz Sprint — Read lines 1-20 for navigation.
  §1 Mission                                    → lines 6-8
  §2 Workstreams                                → lines 9-35
  §3 Success Criteria                           → lines 36-41
  §4 Success Criteria (Updated)                 → lines 42-48
  §5 Sprint Log                                 → lines 49-169
  Total: 169 lines | Sections: 5
-->
**Date:** 2026-02-12, 07:00–11:00 EST
**Agents:** Helios (main) + Nova (sub-agents)
**Resources:** RTX 5090 (30GB VRAM free), Docker, 16 local LLMs via Ollama, Coinbase API

## Mission
Build the next-gen AUGUR trading stack. From mined signals → live-ready, Dockerized, GPU-accelerated.

## Workstreams

### 🧠 Helios: AUGUR V4 Scanner + Docker Stack
1. **augur_v4_scanner.py** — Real-time WebSocket scanner
   - Consumes V3 miner signals (207K VIP2-profitable, sub-30s)
   - WebSocket feed from Coinbase (matches channel)
   - Strategy filter: spread_pct + imbalance_ma only (pruning analysis)
   - Sub-30s holds for capital turnover on $2K
   - Output: live_signal.json bridge to live trader

2. **Dockerize the stack**
   - `docker-compose.yml`: collector + scanner + paper trader
   - Persistent volumes for DBs
   - Health checks, auto-restart
   - GPU passthrough for LLM inference

3. **Local LLM regime detector**
   - Use qwen2.5:32b on RTX 5090 for market regime classification
   - Feed it 5-min OHLCV + orderbook snapshots
   - Output: TRENDING / RANGING / VOLATILE → gate signals accordingly

### 🤖 Nova: Signal DB + Documentation + Analysis
1. **Signal consolidation** — Merge all signal DBs into one canonical source
2. **README.md** — Full project documentation for augur-trading/
3. **Architecture diagram** — Mermaid flowchart of the trading stack
4. **Backtest framework** — Replay V3 signals against paper_results.db outcomes

## Success Criteria
- [ ] V4 scanner running and producing signals
- [ ] Docker compose up with all services
- [ ] README documenting the full system
- [ ] At least one local LLM integrated into the pipeline

## Success Criteria (Updated)
- [x] V4 scanner running and producing signals ✅ 12/12 products, 13+ signals
- [x] At least one local LLM integrated into the pipeline ✅ regime detector (qwen2.5:32b)
- [x] README documenting the full system ✅ (Nova)
- [ ] Docker compose tested with `docker compose up` (validated, not tested live)
- [ ] V4 executor reading scanner signals and executing trades (Nova building)

## Sprint Log

### 06:53 EST - Nova Starting Documentation + Signal Consolidation
- **DB Audit Complete**: Found 25+ database files across augur-trading/ and augur-collector/
  - Main active DBs: enhanced_data.db (45GB), augur_signals.db (7.8GB), paper_results.db (1.6MB)
  - signals_validated.db appears to be empty/unused
  - Multiple archived/backup versions exist
- **Project Structure Mapped**: 20+ Python scripts, existing README needs V4 updates
- **Next**: Update README with V4 findings, create architecture diagram, run backtest analysis

### 07:03 EST - Nova README.md Complete
- ✅ **README.md Updated**: Comprehensive 13KB documentation covering:
  - Full AUGUR V4 system description with crypto microstructure focus
  - Mermaid architecture diagram (5-stage pipeline: collector → miner → scanner → paper → live)
  - All 25+ scripts documented with purposes and usage
  - Database schemas for all major DBs (enhanced_data, augur_signals, paper_results)
  - Complete how-to-run guide for each component
  - V3→V4 key discoveries: mid_vwap_div breakthrough, spread_pct+imbalance_ma winners
  - Performance data: 1.2M signals, 207K VIP2-profitable, ultra-short 5s strategies
- **Next**: Detailed DB audit report, then backtest analysis of paper_results.db

### 07:00 EST - Helios: V4 Scanner + Regime Detector + Docker Stack
- ✅ `augur_v4_scanner.py` (540 lines) — running, connected to Coinbase WS (12 products)
  - 160 signals loaded from V3 DB (8 products × 20 signals)
  - mid_vwap_div + accel + EMA crossovers + flow features computed real-time
  - 10-min warmup, then auto-scanning with 60s product cooldowns
- ✅ `regime_detector.py` — qwen2.5:32b on RTX 5090 for market regime classification
  - 5-min cycle, classifies TRENDING/RANGING/VOLATILE/QUIET
  - Output: regime.json for scanner gating
- ✅ `docker-compose.yml` — full stack: collector, scanner, paper, regime-detector (GPU)
- ✅ `Dockerfile` + `requirements.txt`
- 🔧 Fixed: enhanced-collector was stale (12.5h), restarted
- **Running PIDs:** scanner (1180471), regime-detector (1184409), collector (1184018)

### 07:02-07:12 EST - Nova: Comprehensive Backtest Analysis Complete
- ✅ **paper_results.db Deep Analysis**: 6,371 trades, 269 products, 7 strategies (20.5h period)
  - **Critical Findings**: 9 products with 0% WR should be blacklisted immediately
  - **Top Performers**: SOL-USD (59.38% WR), XRP-USD (55.17%), ETH-USD (55.08%)
  - **Alpha Discovery**: MAMO-USD generated highest PnL (+$10.74) despite 16.81% WR
  - **Time Insights**: Hours 14-16 EST show strongest performance (54% WR at 2PM)
  - **Strategy Winners**: spread_pct (+$27.56 PnL, 31.33% WR), empty strategy (39.91% WR)
- ✅ **Hidden Gems Found**: Profitable combinations within losing strategies:
  - price_ret_60 on ABT-USD: +$2.63 from 5 trades
  - imbalance on SUI-USD: +$1.77 from 118 trades
  - imbalance strategy profitable at hour 22 (+$2.48)
- ✅ **Statistical Profile**: 24.56% overall WR, winners 3.35x larger than losers on average
- ✅ **Report Generated**: ~/Projects/augur-trading/reports/2026-02-12_backtest_analysis.md (7.7KB)
  - P0 blacklist recommendations, P1 optimization strategies, P2 research questions
  - Win streak analysis: empty strategy achieved 10-consecutive wins
  - PnL distribution: P10/P50/P90 for winners (+$0.012/+$0.103/+$0.496)

### 07:22 EST - Helios: Critical Bug Fixes for V4 Scanner
- 🐛 Fixed WS channel format (bare strings, not `{name: ...}` objects)
- 🐛 Fixed async starvation (status reporter never yielded)
- 🐛 Fixed sparse product bar accumulation (mid-caps trade 1-2 trades/30s)
  - Added `_bar_ticker()` coroutine — closes bars every 5s by wall clock
  - Seeded bar timestamps from ticker/orderbook data (no trades needed to start)
  - Empty bars carry forward last VWAP/OB state (matches V3 miner behavior)
- ✅ Scanner confirmed ingesting ~250 trades/min
- ⏳ Waiting for 10-min warmup to validate signal firing
- All commits pushed to Gitea: 5 commits on ev-halt-gate-layer branch
- Nova's backtest analysis complete: `reports/2026-02-12_backtest_analysis.md`

### 07:35 EST - V4 Scanner OPERATIONAL 🎯
- ✅ **12/12 products ready** after 10-min warmup
- ✅ **13+ signals fired** in first 5 minutes (ZRO, RARI, BNKR, MON)
- ✅ scanner_signals.db persisting correctly
- ✅ All mid_vwap_div family features dominating (as expected from mining)
- RARI-USD: 1.99% net return signals (5s holds!)
- Signal rate: ~2-3 signals/minute across all products

### 07:39 EST - Collector Bug Found & Fixed
- 🐛 Enhanced collector had trading hours gate (M-F 8:30-18:30 EST)
- Crypto trades 24/7! Collector was silently dropping ALL data since restart
- Fixed: `is_trading_hours()` now always returns True
- Collector now hammering: 77K+ snapshots, 2.7K+ trades in 2 minutes
- Committed to augur-collector repo, pushed to Gitea

### 07:41 EST - Regime Detector First Classification 🏷️
- ✅ **VOLATILE @ 85% confidence** (qwen2.5:32b, RTX 5090)
- LLM reasoning: "Multiple products exhibit price_range_pct > 1%, mixed flow ratios"
- regime.json written, scanner will read on next cycle
- VOLATILE allows signals through (only TRENDING_DOWN and QUIET block)

### 07:41 EST - Nova Spawned: V4 Live Executor
- Building augur_live_v4.py: reads live_signal.json → executes via Coinbase API
- DRY_RUN=True by default (safety first)
- Regime gating, position limits, hourly trade caps
- Plus systemd service file and README updates

### 07:42 EST - Nova Complete: V4 Executor Built
- ✅ `augur_live_v4.py` (662 lines) — signal-driven live executor
  - Polls live_signal.json every 250ms
  - CoinbaseTrader class (lifted from V3)
  - PositionManager with threaded exits
  - DRY_RUN=True default, kill switch via /tmp/augur-v4-stop
- ✅ `augur-v4-executor.service` created and running
- ✅ README.md updated with V4 executor docs

### 07:44 EST - Signal Tracker Service Created
- ✅ `signal_tracker.py` — validates V4 signals in real-time
- Records entry → exit prices, computes actual returns after VIP2 fees
- Running as systemd service: `augur-signal-tracker`

### 07:48 EST - FULL V4 STACK OPERATIONAL 🎯
**6 services running:**
1. Enhanced Collector — streaming from Coinbase WS (5K+ trades)
2. V4 Scanner — 12/12 products, 25+ signals, regime=VOLATILE
3. Regime Detector — qwen2.5:32b → VOLATILE @ 85%
4. Signal Tracker — 25 validated, **56% WR**, positive PnL
5. V4 Executor — dry-run mode, processing signals
6. Paper Trader — 6,660 trades, +$21.62

**Live validation results (first 25 signals):**
- RARI-USD: 7 trades, **6W/1L (85.7% WR)**, avg net +1.26%
- ZRO-USD: 7 trades, 4W/3L (57.1% WR), avg net +0.19%
- MON-USD: 6 trades, 2W/4L (33.3% WR), avg net -0.08%
- BNKR-USD: 5 trades, 2W/3L (40.0% WR), avg net -0.20%

**Key finding:** RARI is the standout performer. MON and BNKR may need to be filtered.
