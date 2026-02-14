#!/bin/bash
# AUGUR P&L Corruption Fixes - Deployment Script

echo "🚀 Deploying AUGUR P&L corruption fixes..."

# 1. Backup existing files
echo "📁 Creating backups..."
cp active_trader.py active_trader.py.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null || echo "   No active_trader.py found"

# 2. Test new logging system
echo "🧪 Testing fixes..."
if python3 test_direct_pnl.py > test_results.log 2>&1; then
    echo "   ✅ All tests passed"
else
    echo "   ❌ Tests failed - check test_results.log"
    exit 1
fi

# 3. Run migration if trade logs exist
echo "🔄 Migrating existing trade logs..."
if [ -d "logs/trades" ]; then
    python3 migrate_pnl_corruption.py
    echo "   ✅ Migration complete"
else
    echo "   ℹ️  No existing trade logs found"
fi

# 4. Apply patches to active trader
echo "🔧 Applying patches..."
if [ -f "active_trader.py" ]; then
    python3 fix_active_trader_pnl.py
    echo "   ✅ Patches applied"
else
    echo "   ⚠️  active_trader.py not found - manual integration required"
fi

echo "✅ Deployment complete!"
echo "📋 Next steps:"
echo "   1. Test paper trading session"
echo "   2. Monitor logs for 24h"
echo "   3. Validate P&L accuracy"
