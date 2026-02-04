#!/bin/bash
# Start Active Trading Monitor
# Usage: ./start_trading.sh [--dashboard]

set -e

echo "=============================================================="
echo "🎯 ACTIVE TRADING MONITOR STARTUP"
echo "=============================================================="

# Check if we're in the right directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Create logs directory
mkdir -p logs/trades

# Check for required files
echo "Checking prerequisites..."

if [ ! -f "active_trader.py" ]; then
    echo "❌ ERROR: active_trader.py not found"
    exit 1
fi

if [ ! -f "config/active_trader_config.json" ]; then
    echo "❌ ERROR: config/active_trader_config.json not found"
    echo "   Run: python generate_asset_configs.py first"
    exit 1
fi

# Check if configs are generated
CONFIG_COUNT=$(find config -name "active_*_config.yaml" 2>/dev/null | wc -l)
if [ "$CONFIG_COUNT" -lt 1 ]; then
    echo "⚠️  No asset configs found. Generating..."
    python3 generate_asset_configs.py
fi

echo "✅ Prerequisites OK"
echo ""

# Check what mode to run in
if [ "$1" = "--dashboard" ]; then
    echo "Starting with dashboard view..."
    echo "Press Ctrl+C to stop"
    echo ""
    
    # Start active_trader in background
    python3 active_trader.py > logs/active_trader.log 2>&1 &
    TRADER_PID=$!
    echo "✅ Active Trader started (PID: $TRADER_PID)"
    
    # Wait a moment for it to start
    sleep 3
    
    # Start dashboard in foreground
    echo "Starting dashboard..."
    python3 dashboard.py
    
    # When dashboard exits, stop trader
    echo "Stopping active trader..."
    kill $TRADER_PID 2>/dev/null || true
    
else
    echo "Starting active trader (foreground mode)..."
    echo "For dashboard view, run: ./start_trading.sh --dashboard"
    echo ""
    echo "Press Ctrl+C to stop gracefully"
    echo ""
    
    # Run in foreground
    python3 active_trader.py
fi

echo ""
echo "✅ Stopped"
