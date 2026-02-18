
import json
import threading
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Union, Dict, List
import logging
import math

class RobustTradeLogger:
    """Thread-safe trade logger that prevents NULL P&L values"""
    
    def __init__(self, log_dir: str = "logs/trades"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
    
    def safe_float(self, value: Union[str, float, None], default: float = 0.0) -> float:
        """Safely convert value to float, handling NULL/NaN cases"""
        if value is None:
            return default
        
        if isinstance(value, str):
            try:
                value = float(value)
            except (ValueError, TypeError):
                return default
        
        if math.isnan(value) or math.isinf(value):
            return default
        
        return float(value)
    
    def extract_amount_from_log(self, log_line: str) -> Optional[float]:
        """Robust amount extraction with multiple fallback patterns"""
        if not log_line:
            return None
        
        # Try multiple patterns
        patterns = [
            r'\$([0-9]+\.?[0-9]*)',  # Standard $1.23
            r'\$([0-9]+)',           # Just dollars $12
            r'profit[^0-9]*([0-9]+\.?[0-9]*)',  # profit 1.23
            r'loss[^0-9]*([0-9]+\.?[0-9]*)',    # loss 1.23
        ]
        
        for pattern in patterns:
            match = re.search(pattern, log_line, re.IGNORECASE)
            if match:
                try:
                    amount = float(match.group(1))
                    if amount >= 0 and amount < 100000:  # Sanity check
                        return amount
                except (ValueError, IndexError):
                    continue
        
        return None
    
    def log_trade(self, 
                  asset: str, 
                  amount: Optional[float], 
                  is_profit: bool, 
                  total_capital: Optional[float] = None,
                  asset_total: Optional[float] = None) -> bool:
        """Thread-safe trade logging with NULL protection"""
        
        try:
            # Validate and sanitize inputs
            clean_amount = self.safe_float(amount, 0.0)
            clean_total_capital = self.safe_float(total_capital, 0.0)
            clean_asset_total = self.safe_float(asset_total, 0.0)
            
            if not asset or not isinstance(asset, str):
                self.logger.error("Invalid asset name provided")
                return False
            
            # Create trade record with guaranteed non-NULL values
            trade = {
                'timestamp': datetime.now().isoformat(),
                'asset': asset,
                'profit': clean_amount if is_profit else -clean_amount,
                'total_capital': clean_total_capital,
                'asset_total': clean_asset_total,
                'is_profit': is_profit,
                'raw_amount': clean_amount
            }
            
            # Validate JSON serialization
            try:
                json_str = json.dumps(trade)
                # Test parsing
                json.loads(json_str)
            except Exception as e:
                self.logger.error(f"Trade record failed JSON validation: {e}")
                return False
            
            # Thread-safe file write
            with self._lock:
                today = datetime.now().strftime('%Y-%m-%d')
                log_file = self.log_dir / f"trades_{today}.jsonl"
                
                try:
                    with open(log_file, 'a') as f:
                        f.write(json_str + '\n')
                        f.flush()  # Ensure immediate write
                    
                    self.logger.info(f"✅ Logged trade: {asset} {'+' if is_profit else '-'}${clean_amount:.2f}")
                    return True
                    
                except Exception as e:
                    self.logger.error(f"Failed to write trade log: {e}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Trade logging error: {e}")
            return False
    
    def validate_existing_logs(self, log_file: Path) -> Dict[str, List]:
        """Validate existing log files for corruption"""
        issues = []
        valid_trades = []
        
        if not log_file.exists():
            return {'issues': [], 'valid_trades': []}
        
        with open(log_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    trade = json.loads(line)
                    
                    # Check for NULL values
                    if trade.get('profit') is None:
                        issues.append(f"Line {line_num}: NULL profit value")
                    elif math.isnan(float(trade.get('profit', 0))):
                        issues.append(f"Line {line_num}: NaN profit value")
                    
                    if trade.get('total_capital') is None:
                        issues.append(f"Line {line_num}: NULL total_capital")
                    
                    if not trade.get('asset'):
                        issues.append(f"Line {line_num}: Missing asset")
                    
                    if not trade.get('timestamp'):
                        issues.append(f"Line {line_num}: Missing timestamp")
                    
                    valid_trades.append(trade)
                    
                except json.JSONDecodeError as e:
                    issues.append(f"Line {line_num}: Invalid JSON: {e}")
                except Exception as e:
                    issues.append(f"Line {line_num}: Validation error: {e}")
        
        return {'issues': issues, 'valid_trades': valid_trades}
        