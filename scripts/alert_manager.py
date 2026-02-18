#!/usr/bin/env python3
"""
Alert Manager - Intelligent Signal notifications for trading events
Prevents notification spam while keeping Matthew informed
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
from dataclasses import dataclass
from collections import deque
import pytz

logger = logging.getLogger(__name__)
EST = pytz.timezone('America/New_York')


@dataclass
class Alert:
    """Alert message with metadata"""
    timestamp: datetime
    asset: str
    message: str
    priority: str  # 'critical', 'high', 'medium', 'low'
    amount: float = 0.0


class AlertManager:
    """Manages Signal notifications with smart throttling"""
    
    def __init__(self, signal_target: str, config: dict):
        self.signal_target = signal_target
        self.config = config
        
        # Thresholds
        self.profit_threshold = config.get('notify_on_profit_threshold', 5.0)
        self.loss_threshold = config.get('notify_on_loss_threshold', 3.0)
        
        # Alert history (for throttling)
        self.alert_history = deque(maxlen=100)
        self.last_status_update = datetime.now(EST)
        self.last_asset_alert: Dict[str, datetime] = {}
        
        # Cumulative tracking (for batching small alerts)
        self.pending_profits: Dict[str, float] = {}
        self.pending_losses: Dict[str, float] = {}
        
        # Notification intervals
        self.status_interval = timedelta(minutes=config.get('status_update_interval_minutes', 30))
        self.asset_alert_cooldown = timedelta(minutes=5)  # Min 5 min between alerts per asset
        
        logger.info(f"📱 Alert Manager initialized (target: {signal_target})")
    
    def should_alert(self, asset: str, amount: float, is_profit: bool) -> bool:
        """Determine if we should send an alert"""
        threshold = self.profit_threshold if is_profit else self.loss_threshold
        
        # Check absolute threshold
        if abs(amount) < threshold:
            return False
        
        # Check cooldown per asset
        if asset in self.last_asset_alert:
            time_since_last = datetime.now(EST) - self.last_asset_alert[asset]
            if time_since_last < self.asset_alert_cooldown:
                # Still in cooldown - accumulate instead
                return False
        
        return True
    
    async def notify_trade(self, asset: str, amount: float, is_profit: bool, 
                          total_profit: float, total_capital: float):
        """Send notification for a trade"""
        # Check if we should alert
        if not self.should_alert(asset, amount, is_profit):
            # Accumulate for batch alert later
            if is_profit:
                self.pending_profits[asset] = self.pending_profits.get(asset, 0) + amount
            else:
                self.pending_losses[asset] = self.pending_losses.get(asset, 0) + abs(amount)
            return
        
        # Build message
        emoji = "✅" if is_profit else "📉"
        type_str = "PROFIT" if is_profit else "LOSS"
        
        message = (
            f"{emoji} {asset} {type_str}: ${amount:.2f}\n"
            f"Asset Total: ${total_profit:.2f}\n"
            f"Portfolio: ${total_capital:,.2f}"
        )
        
        # Add pending accumulations if any
        if is_profit and asset in self.pending_profits and self.pending_profits[asset] > 0:
            message += f"\n(+${self.pending_profits[asset]:.2f} accumulated)"
            self.pending_profits[asset] = 0
        elif not is_profit and asset in self.pending_losses and self.pending_losses[asset] > 0:
            message += f"\n(-${self.pending_losses[asset]:.2f} accumulated)"
            self.pending_losses[asset] = 0
        
        await self._send_alert(Alert(
            timestamp=datetime.now(EST),
            asset=asset,
            message=message,
            priority='high' if abs(amount) > 10 else 'medium',
            amount=amount
        ))
        
        # Update last alert time
        self.last_asset_alert[asset] = datetime.now(EST)
    
    async def notify_status(self, active_count: int, total_assets: int, 
                           total_profit: float, current_capital: float, 
                           starting_capital: float):
        """Send periodic status update"""
        now = datetime.now(EST)
        
        # Check if it's time for status update
        if now - self.last_status_update < self.status_interval:
            return
        
        # Calculate return
        net_pnl = current_capital - starting_capital
        return_pct = (net_pnl / starting_capital) * 100
        
        # Build status message
        emoji = "📈" if net_pnl > 0 else "📉" if net_pnl < 0 else "➡️"
        
        message = (
            f"📊 Status Update\n"
            f"{now.strftime('%H:%M EST')}\n"
            f"\n"
            f"Active Bots: {active_count}/{total_assets}\n"
            f"Session P&L: {emoji} ${net_pnl:.2f} ({return_pct:+.2f}%)\n"
            f"Capital: ${current_capital:,.2f}"
        )
        
        # Add pending accumulations if significant
        total_pending_profit = sum(self.pending_profits.values())
        total_pending_loss = sum(self.pending_losses.values())
        
        if total_pending_profit > 1.0 or total_pending_loss > 1.0:
            message += f"\n\nPending (not alerted):"
            if total_pending_profit > 0:
                message += f"\n✅ +${total_pending_profit:.2f}"
            if total_pending_loss > 0:
                message += f"\n📉 -${total_pending_loss:.2f}"
        
        await self._send_alert(Alert(
            timestamp=now,
            asset='ALL',
            message=message,
            priority='medium'
        ))
        
        self.last_status_update = now
    
    async def notify_startup(self, assets: list, trading_capital: float):
        """Send startup notification"""
        message = (
            f"🚀 Active Trader Started\n"
            f"{datetime.now(EST).strftime('%H:%M EST')}\n"
            f"\n"
            f"Trading: {', '.join([a.split('-')[0] for a in assets])}\n"
            f"Capital: ${trading_capital:,.2f}\n"
            f"Assets: {len(assets)}"
        )
        
        await self._send_alert(Alert(
            timestamp=datetime.now(EST),
            asset='SYSTEM',
            message=message,
            priority='high'
        ))
    
    async def notify_shutdown(self, final_capital: float, starting_capital: float,
                            asset_performance: dict):
        """Send shutdown/session report notification"""
        net_pnl = final_capital - starting_capital
        return_pct = (net_pnl / starting_capital) * 100
        
        # Build report
        emoji = "🎯" if net_pnl > 0 else "📉"
        
        message = (
            f"{emoji} Session Complete\n"
            f"{datetime.now(EST).strftime('%H:%M EST')}\n"
            f"\n"
            f"Final P&L: ${net_pnl:.2f} ({return_pct:+.2f}%)\n"
            f"Capital: ${final_capital:,.2f}\n"
            f"\n"
            f"Top Performers:"
        )
        
        # Sort assets by profit
        sorted_assets = sorted(
            asset_performance.items(),
            key=lambda x: x[1].total_profit,
            reverse=True
        )
        
        # Top 3
        for i, (asset, perf) in enumerate(sorted_assets[:3], 1):
            symbol = asset.split('-')[0]
            message += f"\n{i}. {symbol}: ${perf.total_profit:.2f} ({perf.total_trades} trades)"
        
        # Worst performer (if negative)
        if sorted_assets and sorted_assets[-1][1].total_profit < 0:
            worst_asset, worst_perf = sorted_assets[-1]
            worst_symbol = worst_asset.split('-')[0]
            message += f"\n\nWorst: {worst_symbol}: ${worst_perf.total_profit:.2f}"
        
        await self._send_alert(Alert(
            timestamp=datetime.now(EST),
            asset='SYSTEM',
            message=message,
            priority='critical'
        ))
    
    async def notify_emergency_exit(self, reason: str, current_capital: float):
        """Send emergency exit notification"""
        message = (
            f"🚨 EMERGENCY EXIT\n"
            f"{datetime.now(EST).strftime('%H:%M EST')}\n"
            f"\n"
            f"Reason: {reason}\n"
            f"Capital: ${current_capital:,.2f}\n"
            f"\n"
            f"Cancelling all BUY orders..."
        )
        
        await self._send_alert(Alert(
            timestamp=datetime.now(EST),
            asset='SYSTEM',
            message=message,
            priority='critical'
        ))
    
    async def notify_bot_restart(self, asset: str, restart_count: int, reason: str = "crashed"):
        """Send bot restart notification"""
        # Only notify if significant (3+ restarts)
        if restart_count < 3:
            return
        
        message = (
            f"🔄 Bot Restarted\n"
            f"{asset}: {reason}\n"
            f"Restart #{restart_count}"
        )
        
        await self._send_alert(Alert(
            timestamp=datetime.now(EST),
            asset=asset,
            message=message,
            priority='medium' if restart_count < 5 else 'high'
        ))
    
    async def _send_alert(self, alert: Alert):
        """Actually send the alert via Signal"""
        try:
            # Log locally
            logger.info(f"📱 ALERT [{alert.priority}]: {alert.message[:50]}...")
            
            # Add to history
            self.alert_history.append(alert)
            
            # TODO: Integrate with OpenClaw's message tool
            # For now, just log. In production, would call:
            # await message_tool(channel='signal', target=self.signal_target, message=alert.message)
            
            # Placeholder for actual Signal integration
            print(f"\n{'='*60}")
            print(f"SIGNAL MESSAGE TO {self.signal_target}")
            print(f"{'='*60}")
            print(alert.message)
            print(f"{'='*60}\n")
            
        except Exception as e:
            logger.error(f"❌ Failed to send alert: {e}")
    
    def get_alert_stats(self) -> dict:
        """Get statistics about alerts sent"""
        if not self.alert_history:
            return {'total': 0}
        
        return {
            'total': len(self.alert_history),
            'by_priority': {
                'critical': sum(1 for a in self.alert_history if a.priority == 'critical'),
                'high': sum(1 for a in self.alert_history if a.priority == 'high'),
                'medium': sum(1 for a in self.alert_history if a.priority == 'medium'),
                'low': sum(1 for a in self.alert_history if a.priority == 'low'),
            },
            'last_alert': self.alert_history[-1].timestamp if self.alert_history else None
        }
