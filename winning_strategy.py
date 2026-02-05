
class WinningStrategy:
    """
    Auto-generated from 2026-02-04 trade analysis
    
    Key insights:
    - 81% of wins happen in <2 minutes
    - Exit if not profitable after 1.0 minutes
    - Only trade during hours: [12]
    """
    
    MAX_HOLD_SECONDS = 60
    QUICK_WIN_THRESHOLD = 120
    GOOD_HOURS = [12]
    BAD_HOURS = [11, 14, 15, 16, 17]
    
    def should_enter(self, current_hour):
        # Only trade during proven good hours
        if current_hour in self.BAD_HOURS:
            return False
        return True
    
    def should_exit(self, position, current_time):
        hold_time = (current_time - position.entry_time).total_seconds()
        
        # Exit winners quickly if target hit
        if position.is_profitable() and hold_time >= self.QUICK_WIN_THRESHOLD:
            return True, "quick_win"
        
        # Force exit if held too long without profit
        if hold_time >= self.MAX_HOLD_SECONDS:
            return True, "max_hold_timeout"
        
        return False, None
