#!/usr/bin/env python3
"""
Pre-flight Check - Verify system is ready for trading
Run this before first launch to catch configuration issues
"""

import os
import sys
import json
from pathlib import Path
import yaml


class PreflightCheck:
    """Verify trading system is ready"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.passed = 0
        self.failed = 0
        
    def check(self, name: str, test_func, critical=True):
        """Run a check"""
        try:
            result = test_func()
            if result:
                self.passed += 1
                print(f"✅ {name}")
                return True
            else:
                if critical:
                    self.failed += 1
                    self.errors.append(name)
                    print(f"❌ {name}")
                else:
                    self.warnings.append(name)
                    print(f"⚠️  {name}")
                return False
        except Exception as e:
            if critical:
                self.failed += 1
                self.errors.append(f"{name}: {e}")
                print(f"❌ {name}: {e}")
            else:
                self.warnings.append(f"{name}: {e}")
                print(f"⚠️  {name}: {e}")
            return False
    
    def print_summary(self):
        """Print final summary"""
        print()
        print("=" * 70)
        print(f"PREFLIGHT CHECK SUMMARY")
        print("=" * 70)
        print(f"Passed:   {self.passed}")
        print(f"Failed:   {self.failed}")
        print(f"Warnings: {len(self.warnings)}")
        print()
        
        if self.errors:
            print("❌ ERRORS (must fix):")
            for error in self.errors:
                print(f"   • {error}")
            print()
        
        if self.warnings:
            print("⚠️  WARNINGS (review):")
            for warning in self.warnings:
                print(f"   • {warning}")
            print()
        
        if self.failed == 0:
            print("✅ READY TO TRADE!")
            print()
            print("Next steps:")
            print("  1. Review config/active_trader_config.json one more time")
            print("  2. Start with 2-3 assets for first session")
            print("  3. Run: ./start_trading.sh --dashboard")
        else:
            print("❌ NOT READY - Fix errors above before trading")
        
        print("=" * 70)
        
        return self.failed == 0


def run_checks():
    """Run all preflight checks"""
    checker = PreflightCheck()
    
    print("=" * 70)
    print("🚀 ACTIVE TRADER PREFLIGHT CHECK")
    print("=" * 70)
    print()
    
    # File existence checks
    print("📁 FILE CHECKS")
    print("-" * 70)
    
    checker.check(
        "active_trader.py exists",
        lambda: Path("active_trader.py").exists()
    )
    
    checker.check(
        "alert_manager.py exists",
        lambda: Path("alert_manager.py").exists()
    )
    
    checker.check(
        "dashboard.py exists",
        lambda: Path("dashboard.py").exists()
    )
    
    checker.check(
        "generate_asset_configs.py exists",
        lambda: Path("generate_asset_configs.py").exists()
    )
    
    checker.check(
        "start_trading.sh exists and executable",
        lambda: Path("start_trading.sh").exists() and os.access("start_trading.sh", os.X_OK)
    )
    
    print()
    
    # Config checks
    print("⚙️  CONFIGURATION CHECKS")
    print("-" * 70)
    
    def check_master_config():
        config_file = Path("config/active_trader_config.json")
        if not config_file.exists():
            return False
        
        with open(config_file) as f:
            config = json.load(f)
        
        # Check required fields
        required = ['bot_directory', 'starting_capital', 'assets']
        for field in required:
            if field not in config:
                print(f"      Missing field: {field}")
                return False
        
        return True
    
    checker.check(
        "Master config valid (config/active_trader_config.json)",
        check_master_config
    )
    
    def check_bot_directory():
        config_file = Path("config/active_trader_config.json")
        if not config_file.exists():
            return False
        
        with open(config_file) as f:
            config = json.load(f)
        
        bot_dir = Path(config.get('bot_directory', ''))
        bot_file = bot_dir / "profit_aware_bot.py"
        
        if not bot_file.exists():
            print(f"      Bot not found: {bot_file}")
            return False
        
        return True
    
    checker.check(
        "Bot directory path is correct",
        check_bot_directory
    )
    
    def check_asset_configs():
        config_file = Path("config/active_trader_config.json")
        if not config_file.exists():
            return True  # Already failed above
        
        with open(config_file) as f:
            config = json.load(f)
        
        assets = config.get('assets', [])
        if not assets:
            print("      No assets configured")
            return False
        
        missing = []
        for asset in assets:
            asset_symbol = asset.split('-')[0].lower()
            config_file = Path(f"config/active_{asset_symbol}_config.yaml")
            if not config_file.exists():
                missing.append(asset)
        
        if missing:
            print(f"      Missing configs: {', '.join(missing)}")
            print(f"      Run: python generate_asset_configs.py")
            return False
        
        return True
    
    checker.check(
        "Asset configs generated",
        check_asset_configs
    )
    
    def check_starting_capital():
        config_file = Path("config/active_trader_config.json")
        if not config_file.exists():
            return True  # Already failed
        
        with open(config_file) as f:
            config = json.load(f)
        
        capital = config.get('starting_capital', 0)
        if capital < 100:
            print(f"      Capital too low: ${capital}")
            return False
        
        return True
    
    checker.check(
        "Starting capital configured (≥$100)",
        check_starting_capital
    )
    
    def check_signal_target():
        config_file = Path("config/active_trader_config.json")
        if not config_file.exists():
            return True
        
        with open(config_file) as f:
            config = json.load(f)
        
        signal_config = config.get('signal_notifications', {})
        target = signal_config.get('target')
        
        if not target or target == "YOUR_PHONE_NUMBER":
            print("      Signal target not set")
            return False
        
        if not target.startswith('+'):
            print(f"      Signal target should start with +: {target}")
            return False
        
        return True
    
    checker.check(
        "Signal notification target set",
        check_signal_target,
        critical=False  # Warning only
    )
    
    print()
    
    # Environment checks
    print("🔐 ENVIRONMENT CHECKS")
    print("-" * 70)
    
    checker.check(
        "COINBASE_API_KEY set",
        lambda: os.getenv('COINBASE_API_KEY') is not None
    )
    
    checker.check(
        "COINBASE_API_SECRET set",
        lambda: os.getenv('COINBASE_API_SECRET') is not None
    )
    
    print()
    
    # Directory checks
    print("📂 DIRECTORY CHECKS")
    print("-" * 70)
    
    def check_logs_dir():
        logs_dir = Path("logs")
        if not logs_dir.exists():
            logs_dir.mkdir(parents=True)
            print("      Created logs/ directory")
        
        trades_dir = logs_dir / "trades"
        if not trades_dir.exists():
            trades_dir.mkdir(parents=True)
            print("      Created logs/trades/ directory")
        
        return True
    
    checker.check(
        "Logs directory structure",
        check_logs_dir,
        critical=False
    )
    
    print()
    
    # Asset config validation
    print("🎯 ASSET CONFIG VALIDATION")
    print("-" * 70)
    
    def validate_asset_configs():
        config_file = Path("config/active_trader_config.json")
        if not config_file.exists():
            return True  # Already failed
        
        with open(config_file) as f:
            config = json.load(f)
        
        assets = config.get('assets', [])
        
        issues = []
        for asset in assets:
            asset_symbol = asset.split('-')[0].lower()
            config_path = Path(f"config/active_{asset_symbol}_config.yaml")
            
            if not config_path.exists():
                continue
            
            with open(config_path) as f:
                asset_config = yaml.safe_load(f)
            
            # Check critical fields
            if asset_config.get('symbol') != asset:
                issues.append(f"{asset}: symbol mismatch")
            
            if asset_config.get('min_profit_ticks', 0) < 1:
                issues.append(f"{asset}: min_profit_ticks too low")
            
            if asset_config.get('base_profit_target_bps', 0) < 5:
                issues.append(f"{asset}: profit target too tight")
        
        if issues:
            for issue in issues:
                print(f"      {issue}")
            return False
        
        return True
    
    checker.check(
        "Asset configs have valid parameters",
        validate_asset_configs,
        critical=False
    )
    
    print()
    
    # Recommendations
    print("💡 RECOMMENDATIONS")
    print("-" * 70)
    
    def check_asset_count():
        config_file = Path("config/active_trader_config.json")
        if not config_file.exists():
            return True
        
        with open(config_file) as f:
            config = json.load(f)
        
        asset_count = len(config.get('assets', []))
        
        if asset_count > 3:
            print(f"      Trading {asset_count} assets - consider starting with 2-3")
            return False
        
        return True
    
    checker.check(
        "Asset count is reasonable for first session",
        check_asset_count,
        critical=False
    )
    
    def check_capital_per_asset():
        config_file = Path("config/active_trader_config.json")
        if not config_file.exists():
            return True
        
        with open(config_file) as f:
            config = json.load(f)
        
        capital = config.get('starting_capital', 0)
        asset_count = len(config.get('assets', []))
        
        if asset_count == 0:
            return True
        
        per_asset = (capital * 0.9) / asset_count  # 90% trading capital
        
        if per_asset < 200:
            print(f"      Only ${per_asset:.0f} per asset - consider fewer assets")
            return False
        
        return True
    
    checker.check(
        "Sufficient capital per asset (≥$200)",
        check_capital_per_asset,
        critical=False
    )
    
    print()
    
    # Print summary
    return checker.print_summary()


def main():
    """Main entry point"""
    ready = run_checks()
    sys.exit(0 if ready else 1)


if __name__ == "__main__":
    main()
