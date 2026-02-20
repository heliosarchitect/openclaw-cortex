# AUGUR Trading Management Skill

## Overview
AUGUR is a crypto trading system with multiple components for signal detection, paper trading, and live execution.

**System Location**: `~/Projects/augur-trading/`  
**Branch**: `ev-halt-gate-layer`

## Core Components

### Services (systemd --user)
- `paper-augur` - Paper trading engine
- `augur-v4-scanner` - V4 signal detection
- `augur-v4-executor` - V4 trade execution
- `augur-signal-tracker` - Signal tracking system
- `enhanced-collector` - Market data collection

### Databases
- `augur_trades.db` - Trade execution records
- `scanner_signals.db` - V4 scanner signals
- `enhanced_data.db` - Market data and analysis

### Key Files
- `live_signal.json` - Current live trading signal
- `reports/` - Daily performance reports

---

## 1. Service Status Checks

### Check All AUGUR Services
```bash
cd ~/Projects/augur-trading/
systemctl --user status paper-augur augur-v4-scanner augur-v4-executor augur-signal-tracker enhanced-collector
```

### Individual Service Status
```bash
systemctl --user status paper-augur
systemctl --user status augur-v4-scanner
systemctl --user status augur-v4-executor
systemctl --user status augur-signal-tracker
systemctl --user status enhanced-collector
```

### Service Logs (Last 50 lines)
```bash
journalctl --user -u paper-augur -n 50
journalctl --user -u augur-v4-scanner -n 50
journalctl --user -u augur-v4-executor -n 50
journalctl --user -u augur-signal-tracker -n 50
journalctl --user -u enhanced-collector -n 50
```

---

## 2. Trade Performance Queries

### Paper Trading Performance (augur_trades.db)
```bash
cd ~/Projects/augur-trading/
sqlite3 augur_trades.db "
SELECT 
    COUNT(*) as total_trades,
    ROUND(AVG(CASE WHEN pnl > 0 THEN 1.0 ELSE 0.0 END) * 100, 2) as win_rate_pct,
    ROUND(SUM(pnl), 2) as total_pnl,
    ROUND(AVG(pnl), 4) as avg_pnl_per_trade
FROM trades 
WHERE type = 'paper';"
```

### Recent Paper Trades (Last 24 Hours)
```bash
sqlite3 augur_trades.db "
SELECT 
    datetime(timestamp, 'unixepoch') as trade_time,
    symbol,
    side,
    quantity,
    price,
    ROUND(pnl, 4) as pnl
FROM trades 
WHERE type = 'paper' 
  AND timestamp > unixepoch('now', '-1 day')
ORDER BY timestamp DESC 
LIMIT 20;"
```

### Top Performing Symbols
```bash
sqlite3 augur_trades.db "
SELECT 
    symbol,
    COUNT(*) as trades,
    ROUND(AVG(CASE WHEN pnl > 0 THEN 1.0 ELSE 0.0 END) * 100, 2) as win_rate_pct,
    ROUND(SUM(pnl), 2) as total_pnl
FROM trades 
WHERE type = 'paper'
GROUP BY symbol
HAVING trades >= 10
ORDER BY total_pnl DESC 
LIMIT 10;"
```

### V4 Scanner Signals (scanner_signals.db)
```bash
sqlite3 scanner_signals.db "
SELECT 
    COUNT(*) as total_signals,
    COUNT(DISTINCT symbol) as unique_symbols,
    datetime(MAX(timestamp), 'unixepoch') as latest_signal
FROM signals;"
```

### Recent V4 Signals
```bash
sqlite3 scanner_signals.db "
SELECT 
    datetime(timestamp, 'unixepoch') as signal_time,
    symbol,
    signal_type,
    confidence,
    price
FROM signals 
ORDER BY timestamp DESC 
LIMIT 20;"
```

---

## 3. Live Signal Monitoring

### Check Current Live Signal
```bash
cd ~/Projects/augur-trading/
cat live_signal.json | jq '.'
```

### Monitor Live Signal Changes
```bash
cd ~/Projects/augur-trading/
watch -n 5 'cat live_signal.json | jq "."'
```

### Live Signal Summary
```bash
cd ~/Projects/augur-trading/
jq -r '"Symbol: \(.symbol // "none") | Side: \(.side // "none") | Confidence: \(.confidence // "none") | Updated: \(.timestamp // "none")"' live_signal.json
```

---

## 4. Service Restart Commands

### Restart All AUGUR Services
```bash
systemctl --user restart paper-augur augur-v4-scanner augur-v4-executor augur-signal-tracker enhanced-collector
```

### Individual Service Restarts
```bash
systemctl --user restart paper-augur
systemctl --user restart augur-v4-scanner
systemctl --user restart augur-v4-executor
systemctl --user restart augur-signal-tracker
systemctl --user restart enhanced-collector
```

### Stop All Services
```bash
systemctl --user stop paper-augur augur-v4-scanner augur-v4-executor augur-signal-tracker enhanced-collector
```

### Start All Services
```bash
systemctl --user start paper-augur augur-v4-scanner augur-v4-executor augur-signal-tracker enhanced-collector
```

---

## 5. Daily Reports

### List Recent Reports
```bash
cd ~/Projects/augur-trading/reports/
ls -la *.txt | tail -10
```

### View Latest Report
```bash
cd ~/Projects/augur-trading/reports/
cat $(ls -t *.txt | head -1)
```

### View Specific Date Report
```bash
cd ~/Projects/augur-trading/reports/
cat augur_report_2026-02-16.txt
```

### Search Reports for Keywords
```bash
cd ~/Projects/augur-trading/reports/
grep -l "profit\|loss\|error" *.txt | tail -5
```

---

## 6. Common Troubleshooting

### Database Connection Issues
**Problem**: Services can't connect to databases  
**Check**:
```bash
cd ~/Projects/augur-trading/
ls -la *.db
sqlite3 augur_trades.db ".schema" | head -5
sqlite3 scanner_signals.db ".schema" | head -5
sqlite3 enhanced_data.db ".schema" | head -5
```

**Fix**: Restart affected services
```bash
systemctl --user restart paper-augur augur-v4-scanner
```

### Signal Miner CPU Spikes
**Problem**: High CPU usage from signal processing  
**Check**:
```bash
ps aux | grep -E "(augur|signal)" | grep -v grep
top -p $(pgrep -d, -f augur)
```

**Monitor**: Watch CPU usage for AUGUR processes
```bash
watch -n 2 'ps aux | grep -E "(augur|signal)" | grep -v grep | awk "{print \$3, \$4, \$11}"'
```

**Fix**: Restart signal-related services
```bash
systemctl --user restart augur-signal-tracker augur-v4-scanner
```

### Runaway Processes
**Problem**: Processes consuming excessive resources  
**Check**:
```bash
ps aux | grep augur | awk '$3 > 50.0 || $4 > 10.0 {print $2, $3, $4, $11}'
```

**Kill**: Force stop problematic processes
```bash
pkill -f "augur"
systemctl --user restart paper-augur augur-v4-scanner augur-v4-executor augur-signal-tracker enhanced-collector
```

### Database Locks
**Problem**: Database operations hanging  
**Check**:
```bash
cd ~/Projects/augur-trading/
fuser augur_trades.db scanner_signals.db enhanced_data.db
```

**Fix**: Stop services, clear locks, restart
```bash
systemctl --user stop paper-augur augur-v4-scanner augur-v4-executor
sleep 5
systemctl --user start paper-augur augur-v4-scanner augur-v4-executor
```

### Log Analysis
**Problem**: Need to diagnose service issues  
**Recent errors**:
```bash
journalctl --user -u paper-augur --since "1 hour ago" | grep -i error
journalctl --user -u augur-v4-scanner --since "1 hour ago" | grep -i error
```

**Full diagnostic**:
```bash
cd ~/Projects/augur-trading/
echo "=== Service Status ==="
systemctl --user status paper-augur augur-v4-scanner augur-v4-executor augur-signal-tracker enhanced-collector

echo "=== Database Status ==="
ls -la *.db

echo "=== Live Signal ==="
cat live_signal.json | jq '.'

echo "=== Recent Trades ==="
sqlite3 augur_trades.db "SELECT COUNT(*) FROM trades WHERE timestamp > unixepoch('now', '-1 hour');"

echo "=== Process Status ==="
ps aux | grep -E "(augur|signal)" | grep -v grep
```

---

## Quick Health Check
Run this comprehensive health check:
```bash
cd ~/Projects/augur-trading/
echo "AUGUR Health Check - $(date)"
echo "================================"
echo "Services:"
systemctl --user is-active paper-augur augur-v4-scanner augur-v4-executor augur-signal-tracker enhanced-collector
echo ""
echo "Recent Trades (last hour):"
sqlite3 augur_trades.db "SELECT COUNT(*) FROM trades WHERE timestamp > unixepoch('now', '-1 hour');"
echo ""
echo "Live Signal:"
jq -r '"Symbol: \(.symbol // "none") | Updated: \(.timestamp // "none")"' live_signal.json
echo ""
echo "CPU Usage:"
ps aux | grep -E "(augur|signal)" | grep -v grep | awk '{sum+=$3} END {printf "Total AUGUR CPU: %.1f%%\n", sum}'
```