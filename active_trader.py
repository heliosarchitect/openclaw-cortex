#!/usr/bin/env python3
"""
Active Trading Monitor - Wraps profit_aware_bot.py for multiple assets
Manages portfolio across ETH, SOL, DOGE, ADA, LINK, XRP, DOT, AVAX, ATOM, NEAR
"""

import asyncio
import logging
import os
import sys
import json
import signal
import subprocess
from datetime import datetime, time as dt_time, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import pytz

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/active_trader.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

EST = pytz.timezone('America/New_York')

@dataclass
class AssetPerformance:
    """Track performance metrics for each asset"""
    symbol: str
    total_profit: float = 0.0
    total_trades: int = 0
    win_rate: float = 0.0
    avg_profit: float = 0.0
    last_trade_time: Optional[datetime] = None
    consecutive_losses: int = 0
    is_active: bool = False
    restart_count: int = 0
    last_restart: Optional[datetime] = None
    allocated_capital: float = 0.0
    current_position_value: float = 0.0


@dataclass
class TradeLog:
    """Individual trade record"""
    timestamp: datetime
    symbol: str
    side: str  # BUY or SELL
    size: float
    price: float
    profit: float = 0.0
    position_size_after: float = 0.0


class ActiveTrader:
    """Master controller for multi-asset trading"""
    
    def __init__(self, config_path='config/active_trader_config.json'):
        """Initialize the active trader"""
        self.config = self.load_config(config_path)
        self.bot_dir = Path(self.config['bot_directory'])
        self.assets = self.config['assets']
        
        # Portfolio management
        self.starting_capital = self.config['starting_capital']
        self.current_capital = self.starting_capital
        self.reserved_capital = self.starting_capital * self.config['reserve_percent']
        self.trading_capital = self.starting_capital - self.reserved_capital
        
        # Asset tracking
        self.asset_performance: Dict[str, AssetPerformance] = {}
        for asset in self.assets:
            self.asset_performance[asset] = AssetPerformance(symbol=asset)
        
        # Bot process management
        self.bot_processes: Dict[str, subprocess.Popen] = {}
        self.bot_restarts: Dict[str, int] = defaultdict(int)
        
        # Trade logging
        self.trade_log_path = Path('logs/trades')
        self.trade_log_path.mkdir(parents=True, exist_ok=True)
        self.session_trades: List[TradeLog] = []
        
        # Alert manager for Signal notifications
        from alert_manager import AlertManager
        signal_config = self.config.get('signal_notifications', {})
        self.signal_target = signal_config.get('target', None)
        self.alert_manager = AlertManager(
            signal_target=self.signal_target,
            config=signal_config
        ) if self.signal_target else None
        
        # Time-based management
        self.trading_hours_start = dt_time(9, 0)  # 9 AM EST
        self.trading_hours_end = dt_time(18, 0)   # 6 PM EST
        self.exit_all_time = dt_time(17, 45)      # 5:45 PM EST - start exit
        self.last_status_report = datetime.now(EST)
        
        # Running state
        self.running = False
        self.shutdown_requested = False
        
        logger.info(f"🚀 Active Trader initialized")
        logger.info(f"   Starting capital: ${self.starting_capital:,.2f}")
        logger.info(f"   Trading capital: ${self.trading_capital:,.2f}")
        logger.info(f"   Reserve: ${self.reserved_capital:,.2f}")
        logger.info(f"   Monitoring {len(self.assets)} assets: {', '.join(self.assets)}")
    
    def load_config(self, config_path: str) -> dict:
        """Load configuration from JSON file"""
        with open(config_path, 'r') as f:
            return json.load(f)
    
    def get_est_time(self) -> datetime:
        """Get current time in EST"""
        return datetime.now(EST)
    
    def is_trading_hours(self) -> bool:
        """Check if we're in trading hours (9am-6pm EST)"""
        now = self.get_est_time()
        current_time = now.time()
        return self.trading_hours_start <= current_time <= self.trading_hours_end
    
    def should_exit_all_positions(self) -> bool:
        """Check if we should exit all positions (17:45 EST)"""
        now = self.get_est_time()
        current_time = now.time()
        return current_time >= self.exit_all_time
    
    def allocate_capital(self) -> Dict[str, float]:
        """Dynamically allocate capital based on performance"""
        # Simple equal allocation to start
        # Can be made more sophisticated based on win rates
        active_assets = [a for a in self.assets if self.asset_performance[a].consecutive_losses < 3]
        
        if not active_assets:
            logger.warning("⚠️  No active assets available!")
            return {}
        
        capital_per_asset = self.trading_capital / len(active_assets)
        
        allocations = {}
        for asset in active_assets:
            perf = self.asset_performance[asset]
            
            # Boost allocation for winners
            multiplier = 1.0
            if perf.win_rate > 0.7 and perf.total_trades > 10:
                multiplier = 1.3
            elif perf.consecutive_losses >= 2:
                multiplier = 0.5
            
            allocations[asset] = capital_per_asset * multiplier
            perf.allocated_capital = allocations[asset]
        
        # Normalize to ensure we don't over-allocate
        total_allocated = sum(allocations.values())
        if total_allocated > self.trading_capital:
            scale_factor = self.trading_capital / total_allocated
            allocations = {k: v * scale_factor for k, v in allocations.items()}
        
        return allocations
    
    async def start_bot(self, asset: str, allocated_capital: float):
        """Start a bot instance for an asset"""
        config_file = self.bot_dir / f"config/active_{asset.lower()}_config.yaml"
        
        if not config_file.exists():
            logger.error(f"❌ Config file not found: {config_file}")
            return False
        
        cmd = [
            sys.executable,
            str(self.bot_dir / "profit_aware_bot.py"),
            "--config", str(config_file)
        ]
        
        try:
            # Start bot as subprocess
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(self.bot_dir),
                text=True,
                bufsize=1  # Line buffered
            )
            
            self.bot_processes[asset] = process
            self.asset_performance[asset].is_active = True
            self.asset_performance[asset].restart_count += 1
            self.asset_performance[asset].last_restart = datetime.now(EST)
            
            logger.info(f"✅ Started bot for {asset} (PID: {process.pid}, Capital: ${allocated_capital:,.2f})")
            
            # Start monitoring task
            asyncio.create_task(self.monitor_bot_output(asset, process))
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start bot for {asset}: {e}")
            return False
    
    async def monitor_bot_output(self, asset: str, process: subprocess.Popen):
        """Monitor bot output for trades and errors"""
        try:
            # Read stdout line by line
            for line in iter(process.stdout.readline, ''):
                if not line:
                    break
                
                line = line.strip()
                
                # Parse trade completions
                if '✅ PROFIT' in line or '💰 PROFIT' in line:
                    await self.handle_trade_completion(asset, line, profit=True)
                elif '📉 LOSS' in line or '❌ LOSS' in line:
                    await self.handle_trade_completion(asset, line, profit=False)
                
                # Log important events
                if any(keyword in line for keyword in ['ERROR', 'CRITICAL', 'WARNING']):
                    logger.warning(f"[{asset}] {line}")
            
            # Process ended
            exit_code = process.wait()
            logger.warning(f"⚠️  Bot for {asset} exited with code {exit_code}")
            self.asset_performance[asset].is_active = False
            
            # Restart if not shutting down and within trading hours
            if not self.shutdown_requested and self.is_trading_hours():
                await self.restart_bot(asset)
                
        except Exception as e:
            logger.error(f"❌ Error monitoring {asset}: {e}")
            self.asset_performance[asset].is_active = False
    
    async def handle_trade_completion(self, asset: str, log_line: str, profit: bool):
        """Parse and record trade completion"""
        perf = self.asset_performance[asset]
        
        # Simple profit extraction (would need more sophisticated parsing)
        try:
            # Look for dollar amounts like $1.23
            import re
            match = re.search(r'\$(\d+\.?\d*)', log_line)
            if match:
                amount = float(match.group(1))
                
                if profit:
                    perf.total_profit += amount
                    perf.consecutive_losses = 0
                else:
                    perf.total_profit -= amount
                    perf.consecutive_losses += 1
                
                # Send alert via AlertManager
                if self.alert_manager:
                    await self.alert_manager.notify_trade(
                        asset=asset,
                        amount=amount if profit else -amount,
                        is_profit=profit,
                        total_profit=perf.total_profit,
                        total_capital=self.current_capital
                    )
                
                perf.total_trades += 1
                perf.last_trade_time = datetime.now(EST)
                
                # Update capital
                self.current_capital += amount if profit else -amount
                
                # Log trade
                await self.log_trade(asset, amount, profit)
                
        except Exception as e:
            logger.error(f"❌ Error parsing trade: {e}")
    
    async def log_trade(self, asset: str, amount: float, is_profit: bool):
        """Log trade to file"""
        trade = {
            'timestamp': datetime.now(EST).isoformat(),
            'asset': asset,
            'profit': amount if is_profit else -amount,
            'total_capital': self.current_capital,
            'asset_total': self.asset_performance[asset].total_profit
        }
        
        # Append to daily log
        today = datetime.now(EST).strftime('%Y-%m-%d')
        log_file = self.trade_log_path / f"trades_{today}.jsonl"
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(trade) + '\n')
    
    async def send_notification(self, message: str, threshold: float = 0):
        """Deprecated - use alert_manager instead"""
        if self.alert_manager:
            logger.info(f"📱 {message}")
        else:
            logger.info(f"📱 (No Signal configured) {message}")
    
    async def restart_bot(self, asset: str):
        """Restart a failed bot"""
        logger.info(f"🔄 Restarting bot for {asset}...")
        
        # Check restart count
        max_restarts = self.config.get('bot_management', {}).get('max_restarts_per_session', 5)
        if self.bot_restarts[asset] >= max_restarts:
            logger.error(f"❌ {asset} exceeded max restarts, pausing")
            self.asset_performance[asset].consecutive_losses = 999  # Effectively disable
            return
        
        self.bot_restarts[asset] += 1
        
        # Notify on restart if significant
        if self.alert_manager:
            await self.alert_manager.notify_bot_restart(
                asset=asset,
                restart_count=self.bot_restarts[asset],
                reason="crashed"
            )
        
        await asyncio.sleep(5)  # Brief cooldown
        
        allocations = self.allocate_capital()
        if asset in allocations:
            await self.start_bot(asset, allocations[asset])
    
    async def exit_all_positions(self):
        """Emergency exit - stop all bots and cancel buy orders"""
        logger.warning("🚨 EXITING ALL POSITIONS - Market close approaching")
        
        if self.alert_manager:
            await self.alert_manager.notify_emergency_exit(
                reason="Market close (17:45 EST)",
                current_capital=self.current_capital
            )
        
        # Stop all bots gracefully (they'll cancel buy orders on shutdown)
        for asset, process in list(self.bot_processes.items()):
            try:
                logger.info(f"   Stopping {asset}...")
                process.terminate()
                process.wait(timeout=10)
            except Exception as e:
                logger.error(f"❌ Error stopping {asset}: {e}")
                process.kill()
        
        self.bot_processes.clear()
        
        # Wait for sell orders to complete (give 5 minutes)
        logger.info("⏳ Waiting for sell orders to complete...")
        await asyncio.sleep(300)
        
        # Generate final report
        await self.generate_session_report()
    
    async def generate_session_report(self):
        """Generate end-of-day performance report"""
        report = [
            "=" * 60,
            "📊 TRADING SESSION REPORT",
            "=" * 60,
            f"Start Capital: ${self.starting_capital:,.2f}",
            f"Final Capital: ${self.current_capital:,.2f}",
            f"Net P&L: ${self.current_capital - self.starting_capital:,.2f}",
            f"Return: {((self.current_capital - self.starting_capital) / self.starting_capital * 100):.2f}%",
            "",
            "Per-Asset Performance:",
            "-" * 60
        ]
        
        for asset in self.assets:
            perf = self.asset_performance[asset]
            report.append(
                f"{asset:8} | Profit: ${perf.total_profit:8.2f} | "
                f"Trades: {perf.total_trades:4} | "
                f"Restarts: {perf.restart_count:2}"
            )
        
        report.append("=" * 60)
        
        report_text = "\n".join(report)
        logger.info("\n" + report_text)
        
        # Save report
        today = datetime.now(EST).strftime('%Y-%m-%d')
        report_file = Path('logs') / f"session_report_{today}.txt"
        report_file.write_text(report_text)
        
        # Send to Signal via AlertManager
        if self.alert_manager:
            await self.alert_manager.notify_shutdown(
                final_capital=self.current_capital,
                starting_capital=self.starting_capital,
                asset_performance=self.asset_performance
            )
    
    async def status_check(self):
        """Periodic status check and reporting"""
        while self.running:
            try:
                await asyncio.sleep(300)  # Every 5 minutes
                
                # Check if bots are running
                for asset, process in list(self.bot_processes.items()):
                    if process.poll() is not None:
                        logger.warning(f"⚠️  Bot {asset} died, restarting...")
                        await self.restart_bot(asset)
                
                # Periodic status report (every 30 min)
                now = self.get_est_time()
                if (now - self.last_status_report).seconds >= 1800:
                    await self.send_status_update()
                    self.last_status_report = now
                
                # Check if we should exit
                if self.should_exit_all_positions():
                    await self.exit_all_positions()
                    self.running = False
                    
            except Exception as e:
                logger.error(f"❌ Status check error: {e}")
    
    async def send_status_update(self):
        """Send periodic status update"""
        active_count = sum(1 for p in self.asset_performance.values() if p.is_active)
        total_profit = sum(p.total_profit for p in self.asset_performance.values())
        
        if self.alert_manager:
            await self.alert_manager.notify_status(
                active_count=active_count,
                total_assets=len(self.assets),
                total_profit=total_profit,
                current_capital=self.current_capital,
                starting_capital=self.starting_capital
            )
    
    async def run(self):
        """Main control loop"""
        logger.info("🚀 Starting Active Trader...")
        
        # Wait for trading hours if needed
        while not self.is_trading_hours() and not self.shutdown_requested:
            next_start = self.get_est_time().replace(
                hour=self.trading_hours_start.hour,
                minute=self.trading_hours_start.minute,
                second=0
            )
            wait_seconds = (next_start - self.get_est_time()).seconds
            logger.info(f"⏰ Waiting for trading hours... (starts in {wait_seconds/3600:.1f}h)")
            await asyncio.sleep(min(300, wait_seconds))  # Check every 5 min
        
        if self.shutdown_requested:
            return
        
        # Allocate capital and start bots
        allocations = self.allocate_capital()
        for asset, capital in allocations.items():
            await self.start_bot(asset, capital)
            await asyncio.sleep(2)  # Stagger starts
        
        # Send startup notification
        if self.alert_manager:
            await self.alert_manager.notify_startup(
                assets=list(allocations.keys()),
                trading_capital=self.trading_capital
            )
        
        # Start status monitoring
        self.running = True
        status_task = asyncio.create_task(self.status_check())
        
        try:
            await status_task
        except asyncio.CancelledError:
            logger.info("⚠️  Main loop cancelled")
        
        # Cleanup
        await self.exit_all_positions()
        logger.info("✅ Active Trader stopped")


async def main():
    """Entry point"""
    # Create logs directory
    Path('logs').mkdir(exist_ok=True)
    
    trader = ActiveTrader()
    
    # Setup signal handlers
    def signal_handler():
        logger.info("⚠️  Shutdown signal received")
        trader.shutdown_requested = True
        trader.running = False
    
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, signal_handler)
    
    try:
        await trader.run()
    except KeyboardInterrupt:
        logger.info("⚠️  KeyboardInterrupt")
        trader.shutdown_requested = True
    finally:
        # Final cleanup
        for process in trader.bot_processes.values():
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                process.kill()


if __name__ == "__main__":
    print("=" * 70)
    print("🎯 ACTIVE TRADING MONITOR")
    print("=" * 70)
    print("Features:")
    print("  ✅ Multi-asset portfolio management")
    print("  ✅ Auto-restart failed bots")
    print("  ✅ Time-based position exit (17:45 EST)")
    print("  ✅ Signal notifications on significant P&L")
    print("  ✅ Comprehensive trade logging")
    print("  ✅ Dynamic capital allocation")
    print("=" * 70)
    
    asyncio.run(main())
