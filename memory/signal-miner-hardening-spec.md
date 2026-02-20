# AUGUR Signal Miner Hardening Specification

**Date**: 2026-02-16  
**Task**: Harden signal miner with MIN_TEST_TRADES=50 and Sharpe>0.5 filter  
**File Modified**: `~/Projects/augur-trading/signal_miner_v3.py`

## Overview
Enhanced the AUGUR signal miner v3 with statistical significance filters to reduce false positives and ensure risk-adjusted returns. This hardening improves signal quality by requiring larger test samples and minimum risk-adjusted performance.

## Changes Implemented

### 1. Minimum Test Trades Filter
- **Added**: `MIN_TEST_TRADES = 50` constant
- **Changed**: Test set validation from 15 to 50 minimum trades
- **Impact**: Ensures statistical significance before signals are considered valid
- **Locations**:
  - Line 26: Added `MIN_TEST_TRADES = 50` constant
  - Line 349: `if tr_cnt < 15 or te_cnt < MIN_TEST_TRADES:` (single signals)
  - Line 431: `if np.sum(tr_m) < 15 or np.sum(te_m) < MIN_TEST_TRADES:` (pair signals)

### 2. Sharpe Ratio Filter
- **Added**: `MIN_SHARPE_RATIO = 0.5` constant
- **Added**: `calculate_sharpe_ratio()` function for risk-adjusted returns
- **Implementation**: Sharpe ratio calculated on test set returns (risk-free rate = 0)
- **Impact**: Filters out signals with poor risk-adjusted returns
- **Locations**:
  - Line 27: Added `MIN_SHARPE_RATIO = 0.5` constant
  - Line 85: Added `calculate_sharpe_ratio()` function
  - Line 362: Sharpe filter for single LONG/SHORT signals
  - Line 449: Sharpe filter for pair LONG signals
  - Line 476: Sharpe filter for pair SHORT signals

### 3. Documentation Updates
- **Updated**: Docstring to include hardening description
- **Updated**: Main function output to show new parameters
- **Added**: Clear indication this is for "Pattern Discovery Enhancement"

## Function Details

### `calculate_sharpe_ratio(returns)`
```python
def calculate_sharpe_ratio(returns):
    """Calculate Sharpe ratio for a series of returns (risk-free rate = 0)."""
    if len(returns) < 2:
        return 0.0
    
    mean_return = np.mean(returns)
    std_return = np.std(returns, ddof=1)  # Sample standard deviation
    
    if std_return == 0 or np.isnan(std_return):
        return 0.0
    
    return mean_return / std_return
```

## Filtering Logic

### Before (Original)
- Minimum 30 total trades
- Minimum 15 train trades, 15 test trades
- Positive gross return in both train and test
- Win rate improvement above base

### After (Hardened)
- Minimum 30 total trades
- Minimum 15 train trades, **50 test trades**
- Positive gross return in both train and test
- **Sharpe ratio > 0.5 on test set**
- Win rate improvement above base

## Expected Impact

### Signal Quality
- **Reduced false positives**: 50-trade minimum increases statistical confidence
- **Better risk-adjusted performance**: Sharpe filter ensures returns justify volatility
- **More robust signals**: Higher sample size reduces noise sensitivity

### Signal Quantity
- **Expected reduction**: 30-50% fewer signals due to stricter requirements
- **Quality over quantity**: Remaining signals should have higher success rates
- **Improved backtest stability**: Less overfitting to small samples

## Testing
The hardened signal miner can be tested with:
```bash
cd ~/Projects/augur-trading/
python signal_miner_v3.py
```

Results will be stored in `augur_signals_v3.db` with the enhanced filtering applied.

## Validation
Compare signal performance before and after hardening:
- Count reduction in total signals
- Improved Sharpe ratios in live testing
- Better out-of-sample performance stability
- Reduced signal decay over time

---

**Status**: ✅ IMPLEMENTED  
**Next Step**: Move LBF task 29 (project 22) from spec → build