# Trading Infrastructure Documentation

**Generated**: 2026-02-07 23:30 EST (Overnight Shift - Cycle 8)

## Overview

Complete graph of trading systems, databases, and dependencies now documented in task-graph.

## Components

### Databases (4)
1. **trading_data_db** - Historical backtest data
   - 98,937 ETH-USD 1-minute candles
   - Date range: Aug 29 - Nov 6, 2025
   - Path: `/home/bonsaihorn/Projects/Chad_Volume_tracker/trading_data.db`

2. **live_trading_db** - Real-time trading system
   - Active live trades tracking
   - Path: `/home/bonsaihorn/Projects/Chad2930/Chad_Profit_Bot/live_trading.db`
   
3. **orderbook_db** - Order book snapshots
   - 280,000+ snapshots collected
   - Path: `/home/bonsaihorn/Projects/Chad_Volume_tracker/orderbook_data.db`
   - Collector PID: 2997019

4. **trader_db** - (Legacy/existing entry)

### Scripts (2)
1. **strategy_search** - Pattern discovery system
   - Path: `massive_strategy_search_realistic.py`
   - Results: `ranked_strategies_realistic.csv`
   - Status: Completed (found 5pm-8pm pattern)

2. **live_trader** - Active trading bot
   - Path: `live_trader_final.py`
   - PID: 469083
   - Win Rate: 74.7%
   - Total P/L: $131.88
   - Status: Stopped (after hours)

### Processes (1)
1. **orderbook_collector** - Real-time data collection
   - Path: `collect_orderbook_data.py`
   - PID: 2997019
   - Snapshots: 279,383+
   - Status: Running

### Endpoints (3)
1. **cb_websocket** - Coinbase WebSocket
   - URL: `wss://advanced-trade-ws.coinbase.com`
   - Status: Tested and working

2. **coinbase_best_bid_ask** - REST API
   - URL: `https://api.coinbase.com/api/v3/brokerage/best_bid_ask`
   - Status: OK

3. **oai_local** - Local LLM endpoint (existing)

## Relationships

```
strategy_search --[uses]--> trading_data_db
live_trader --[uses]--> live_trading_db
live_trader --[depends-on]--> coinbase_best_bid_ask
live_trader --[uses]--> cb_websocket
orderbook_collector --[produces]--> orderbook_db
orderbook_collector --[depends-on]--> cb_websocket
```

## Key Insights

1. **Data Flow**: Order book collector → orderbook_db (continuous real-time feed)
2. **Trading Logic**: live_trader uses both REST (best_bid_ask) and WebSocket for execution
3. **Research Pipeline**: trading_data_db → strategy_search → insights
4. **Production System**: live_trading_db tracks actual trades

## Next Actions (from task-graph suggest)

Will run:
```bash
cd ~/.openclaw/workspace/skills/task-graph && python3 scripts/graph.py suggest
```

To see automated suggestions for system improvements.

---

**Value Created**: Complete infrastructure map for trading systems. Future-me can now query relationships, dependencies, and status at any time without context reconstruction.
