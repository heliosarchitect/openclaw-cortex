#!/usr/bin/env python3
"""
AUGUR Monday Market Hours Backtest
Stacked signal strategy on 5-second bars, all products
Monday Feb 9, 2026 9:00 AM - 6:00 PM Eastern (14:00-23:00 UTC)

Uses orderbook_snapshots (bid_size/ask_size at top of book) for OB imbalance.
"""

import sqlite3
import datetime
import time
import sys
from collections import defaultdict

DB_PATH = '/home/bonsaihorn/Projects/augur-collector/enhanced_data.db'
RT_FEE = 0.0020  # 0.20% round-trip (VIP 2: 0.10% each way)
WIN_THRESHOLD = 0.0020  # 0.20% gross to cover RT fees
HOLD_PERIODS = [15, 30, 60, 120, 300]  # seconds
BAR_SIZE = 5  # seconds

# Monday Feb 9, 2026 9:00 AM - 6:00 PM ET = 14:00-23:00 UTC
MON_START = int(datetime.datetime(2026, 2, 9, 14, 0, 0, tzinfo=datetime.timezone.utc).timestamp())
MON_END = int(datetime.datetime(2026, 2, 9, 23, 0, 0, tzinfo=datetime.timezone.utc).timestamp())

# Weekend Feb 7-8 (Sat 00:00 - Mon 00:00 UTC)
WKD_START = int(datetime.datetime(2026, 2, 7, 0, 0, 0, tzinfo=datetime.timezone.utc).timestamp())
WKD_END = int(datetime.datetime(2026, 2, 9, 0, 0, 0, tzinfo=datetime.timezone.utc).timestamp())


def get_connection():
    conn = sqlite3.connect(f'file://{DB_PATH}?mode=ro', uri=True)
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA cache_size=-200000')  # 200MB cache
    return conn


def get_products(conn, start, end):
    c = conn.cursor()
    c.execute('SELECT DISTINCT product FROM trade_flow WHERE timestamp >= ? AND timestamp < ?', (start, end))
    return [r[0] for r in c.fetchall()]


def process_product(conn, product, start, end):
    """Load data, build bars, compute signals, evaluate — all in one pass per product."""
    c = conn.cursor()
    
    # Load trade_flow
    c.execute('''
        SELECT timestamp, buy_volume, sell_volume, buy_count, sell_count, vwap
        FROM trade_flow
        WHERE product = ? AND timestamp >= ? AND timestamp < ?
        ORDER BY timestamp
    ''', (product, start, end))
    tf_data = c.fetchall()
    
    if len(tf_data) < 20:
        return None
    
    # Load orderbook snapshots (top-of-book bid/ask size for imbalance)
    c.execute('''
        SELECT timestamp, bid_size, ask_size
        FROM orderbook_snapshots
        WHERE product = ? AND timestamp >= ? AND timestamp < ?
        ORDER BY timestamp
    ''', (product, start, end))
    ob_raw = c.fetchall()
    
    # Build OB imbalance map (keyed by timestamp)
    ob_imbalance = {}
    for ts, bid_sz, ask_sz in ob_raw:
        total = (bid_sz or 0) + (ask_sz or 0)
        if total > 0:
            ob_imbalance[ts] = (bid_sz or 0) / total
    
    # Build 5-second bars
    bars = []
    current_bar_ts = None
    buy_vol = sell_vol = 0.0
    buy_cnt = sell_cnt = 0
    vwap_sum = vwap_weight = 0.0
    
    def flush_bar():
        nonlocal buy_vol, sell_vol, buy_cnt, sell_cnt, vwap_sum, vwap_weight
        bar_vwap = vwap_sum / vwap_weight if vwap_weight > 0 else 0
        bars.append((current_bar_ts, buy_vol, sell_vol, buy_cnt, sell_cnt, bar_vwap, buy_vol + sell_vol))
        buy_vol = sell_vol = 0.0
        buy_cnt = sell_cnt = 0
        vwap_sum = vwap_weight = 0.0
    
    for ts, bv, sv, bc, sc, vw in tf_data:
        bar_ts = (ts // BAR_SIZE) * BAR_SIZE
        if current_bar_ts is not None and bar_ts != current_bar_ts:
            flush_bar()
        current_bar_ts = bar_ts
        bv = bv or 0
        sv = sv or 0
        buy_vol += bv
        sell_vol += sv
        buy_cnt += (bc or 0)
        sell_cnt += (sc or 0)
        w = bv + sv
        if vw and w > 0:
            vwap_sum += vw * w
            vwap_weight += w
    
    if current_bar_ts is not None:
        flush_bar()
    
    if len(bars) < 10:
        return None
    
    # bars: (ts, buy_vol, sell_vol, buy_cnt, sell_cnt, vwap, total_vol)
    # Index: 0=ts, 1=buy_vol, 2=sell_vol, 3=buy_cnt, 4=sell_cnt, 5=vwap, 6=total_vol
    
    # Build ts -> index map for exit lookup
    ts_to_idx = {bar[0]: i for i, bar in enumerate(bars)}
    
    # Compute signals and evaluate in one pass
    results = defaultdict(lambda: {'trades': 0, 'wins': 0, 'gross_returns': [], 'net_returns': []})
    signal_count = 0
    
    for i in range(1, len(bars)):
        bar = bars[i]
        prev = bars[i-1]
        
        if bar[5] <= 0 or bar[6] == 0 or prev[5] <= 0 or prev[6] == 0:
            continue
        
        bv, sv = bar[1], bar[2]
        pbv, psv = prev[1], prev[2]
        
        # Flow ratios
        fr = bv / sv if sv > 0 else (999.0 if bv > 0 else 1.0)
        pfr = pbv / psv if psv > 0 else (999.0 if pbv > 0 else 1.0)
        ifr = sv / bv if bv > 0 else (999.0 if sv > 0 else 1.0)
        ipfr = psv / pbv if pbv > 0 else (999.0 if psv > 0 else 1.0)
        
        # OB imbalance — find nearest snapshot within bar window
        ob_imb = None
        for offset in range(BAR_SIZE):
            ts_check = bar[0] + offset
            if ts_check in ob_imbalance:
                ob_imb = ob_imbalance[ts_check]
                break
        
        # LONG stack
        long_stack = 0
        if fr >= 2.0: long_stack += 1
        if pfr >= 2.0: long_stack += 1
        if ob_imb is not None and ob_imb > 0.55: long_stack += 1
        if fr > pfr: long_stack += 1  # acceleration
        
        # SHORT stack
        short_stack = 0
        if ifr >= 2.0: short_stack += 1
        if ipfr >= 2.0: short_stack += 1
        if ob_imb is not None and ob_imb < 0.45: short_stack += 1
        if ifr > ipfr: short_stack += 1  # sell acceleration
        
        entry_price = bar[5]
        
        for direction, stack in [('LONG', long_stack), ('SHORT', short_stack)]:
            if stack < 3:
                continue
            
            signal_count += 1
            
            for hold in HOLD_PERIODS:
                exit_ts = bar[0] + hold
                exit_bar_ts = (exit_ts // BAR_SIZE) * BAR_SIZE
                
                exit_idx = ts_to_idx.get(exit_bar_ts)
                if exit_idx is None:
                    for delta in [-BAR_SIZE, BAR_SIZE, 2*BAR_SIZE]:
                        eidx = ts_to_idx.get(exit_bar_ts + delta)
                        if eidx is not None:
                            exit_idx = eidx
                            break
                
                if exit_idx is None:
                    continue
                
                exit_price = bars[exit_idx][5]
                if exit_price <= 0:
                    continue
                
                gross_ret = (exit_price - entry_price) / entry_price
                if direction == 'SHORT':
                    gross_ret = -gross_ret
                
                net_ret = gross_ret - RT_FEE
                is_win = gross_ret > WIN_THRESHOLD
                
                for threshold in [3, 4]:
                    if stack >= threshold:
                        key = (direction, threshold, hold)
                        results[key]['trades'] += 1
                        if is_win:
                            results[key]['wins'] += 1
                        results[key]['gross_returns'].append(gross_ret)
                        results[key]['net_returns'].append(net_ret)
    
    if not results:
        return None
    
    return {
        'results': dict(results),
        'num_bars': len(bars),
        'num_signals': signal_count,
        'ob_coverage': len(ob_imbalance) / max(len(tf_data), 1) * 100,
    }


def run_backtest(conn, start, end, label=""):
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"Running: {label}", file=sys.stderr)
    start_dt = datetime.datetime.fromtimestamp(start, tz=datetime.timezone.utc)
    end_dt = datetime.datetime.fromtimestamp(end, tz=datetime.timezone.utc)
    print(f"Window: {start_dt} to {end_dt}", file=sys.stderr)
    
    products = get_products(conn, start, end)
    print(f"Found {len(products)} products", file=sys.stderr)
    
    all_results = {}
    t0 = time.time()
    
    for i, product in enumerate(products):
        if (i+1) % 50 == 0:
            elapsed = time.time() - t0
            rate = (i+1) / elapsed
            remaining = (len(products) - i - 1) / rate
            print(f"  {i+1}/{len(products)} ({elapsed:.0f}s elapsed, ~{remaining:.0f}s remaining)", file=sys.stderr)
        
        result = process_product(conn, product, start, end)
        if result:
            all_results[product] = result
    
    elapsed = time.time() - t0
    print(f"Completed {len(products)} products in {elapsed:.1f}s, {len(all_results)} with signals", file=sys.stderr)
    
    return all_results


def format_results(results, label=""):
    lines = []
    
    if not results:
        lines.append(f"No results for {label}")
        return '\n'.join(lines)
    
    # Aggregate by config
    config_totals = defaultdict(lambda: {'trades': 0, 'wins': 0, 'gross_sum': 0, 'net_sum': 0, 'products': 0})
    
    for product, pdata in results.items():
        seen_configs = set()
        for (direction, threshold, hold), stats in pdata['results'].items():
            if stats['trades'] == 0:
                continue
            key = (direction, threshold, hold)
            config_totals[key]['trades'] += stats['trades']
            config_totals[key]['wins'] += stats['wins']
            config_totals[key]['gross_sum'] += sum(stats['gross_returns'])
            config_totals[key]['net_sum'] += sum(stats['net_returns'])
            if key not in seen_configs:
                config_totals[key]['products'] += 1
                seen_configs.add(key)
    
    # Summary table sorted by net PnL
    lines.append(f"\n### Signal Configuration Summary — {label}")
    lines.append("")
    lines.append("| Direction | Stack | Hold(s) | Products | Trades | Win Rate | Avg Gross% | Avg Net% | Total Net PnL% |")
    lines.append("|-----------|-------|---------|----------|--------|----------|------------|----------|----------------|")
    
    sorted_configs = sorted(config_totals.items(), key=lambda x: x[1]['net_sum'], reverse=True)
    
    for (direction, threshold, hold), stats in sorted_configs:
        if stats['trades'] == 0:
            continue
        wr = stats['wins'] / stats['trades'] * 100
        avg_gross = stats['gross_sum'] / stats['trades'] * 100
        avg_net = stats['net_sum'] / stats['trades'] * 100
        total_net = stats['net_sum'] * 100
        lines.append(f"| {direction} | ≥{threshold} | {hold} | {stats['products']} | {stats['trades']} | {wr:.1f}% | {avg_gross:+.4f}% | {avg_net:+.4f}% | {total_net:+.2f}% |")
    
    # Top 10 products by best net PnL across any config (min 3 trades)
    lines.append(f"\n### Top 10 Products by Net PnL — {label}")
    lines.append("")
    
    product_best = {}
    for product, pdata in results.items():
        best_net = float('-inf')
        best_cfg = None
        best_stats = None
        for (direction, threshold, hold), stats in pdata['results'].items():
            if stats['trades'] >= 3:
                total_net = sum(stats['net_returns']) * 100
                if total_net > best_net:
                    best_net = total_net
                    best_cfg = (direction, threshold, hold)
                    best_stats = stats
        if best_cfg and best_stats:
            product_best[product] = {
                'config': best_cfg,
                'stats': best_stats,
                'total_net': best_net,
                'ob_coverage': pdata['ob_coverage'],
                'num_signals': pdata['num_signals'],
            }
    
    sorted_products = sorted(product_best.items(), key=lambda x: x[1]['total_net'], reverse=True)
    
    lines.append("| # | Product | Config | Trades | WR | Avg Gross% | Avg Net% | Total Net% | OB Cov |")
    lines.append("|---|---------|--------|--------|----|------------|----------|------------|--------|")
    
    for i, (product, pdata) in enumerate(sorted_products[:10]):
        d, t, h = pdata['config']
        stats = pdata['stats']
        trades = stats['trades']
        wr = stats['wins'] / trades * 100
        avg_gross = sum(stats['gross_returns']) / trades * 100
        avg_net = sum(stats['net_returns']) / trades * 100
        lines.append(f"| {i+1} | {product} | {d} ≥{t} {h}s | {trades} | {wr:.1f}% | {avg_gross:+.4f}% | {avg_net:+.4f}% | {pdata['total_net']:+.3f}% | {pdata['ob_coverage']:.0f}% |")
    
    # Bottom 10 (worst)
    lines.append(f"\n### Bottom 10 Products by Net PnL — {label}")
    lines.append("")
    lines.append("| # | Product | Config | Trades | WR | Avg Gross% | Avg Net% | Total Net% | OB Cov |")
    lines.append("|---|---------|--------|--------|----|------------|----------|------------|--------|")
    
    for i, (product, pdata) in enumerate(sorted_products[-10:]):
        d, t, h = pdata['config']
        stats = pdata['stats']
        trades = stats['trades']
        wr = stats['wins'] / trades * 100
        avg_gross = sum(stats['gross_returns']) / trades * 100
        avg_net = sum(stats['net_returns']) / trades * 100
        lines.append(f"| {i+1} | {product} | {d} ≥{t} {h}s | {trades} | {wr:.1f}% | {avg_gross:+.4f}% | {avg_net:+.4f}% | {pdata['total_net']:+.3f}% | {pdata['ob_coverage']:.0f}% |")
    
    # Full product table (all products sorted by net PnL)
    lines.append(f"\n### All Products Sorted by Net PnL — {label}")
    lines.append("")
    lines.append("| # | Product | Config | Trades | WR | Avg Gross% | Avg Net% | Total Net% |")
    lines.append("|---|---------|--------|--------|----|------------|----------|------------|")
    
    for i, (product, pdata) in enumerate(sorted_products):
        d, t, h = pdata['config']
        stats = pdata['stats']
        trades = stats['trades']
        wr = stats['wins'] / trades * 100
        avg_gross = sum(stats['gross_returns']) / trades * 100
        avg_net = sum(stats['net_returns']) / trades * 100
        lines.append(f"| {i+1} | {product} | {d} ≥{t} {h}s | {trades} | {wr:.1f}% | {avg_gross:+.4f}% | {avg_net:+.4f}% | {pdata['total_net']:+.3f}% |")
    
    return '\n'.join(lines)


def main():
    t0 = time.time()
    conn = get_connection()
    
    # Monday backtest
    monday_results = run_backtest(conn, MON_START, MON_END, "Monday Feb 9 (9AM-6PM ET)")
    
    # Weekend backtest for comparison
    weekend_results = run_backtest(conn, WKD_START, WKD_END, "Weekend Feb 7-8")
    
    elapsed = time.time() - t0
    
    # Build report
    report = []
    report.append("# AUGUR Monday Market Hours Backtest")
    report.append(f"*Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    report.append(f"*Runtime: {elapsed:.1f}s*")
    report.append("")
    report.append("## Strategy")
    report.append("- **Bars:** 5-second aggregated from 1s trade_flow")
    report.append("- **OB Imbalance:** bid_size / (bid_size + ask_size) from orderbook_snapshots (top-of-book)")
    report.append("- **LONG signals:** flow_ratio ≥ 2.0, prev flow_ratio ≥ 2.0, OB imbalance > 0.55, acceleration (FR > prev FR)")
    report.append("- **SHORT signals:** sell_flow_ratio ≥ 2.0, prev ≥ 2.0, OB imbalance < 0.45, sell acceleration")
    report.append("- **Thresholds:** ≥3/4 and 4/4 stacked conditions")
    report.append(f"- **Hold periods:** {HOLD_PERIODS}")
    report.append(f"- **Fees:** {RT_FEE*100:.2f}% round-trip (VIP 2 taker: 0.10% each way)")
    report.append(f"- **Win definition:** gross return > {WIN_THRESHOLD*100:.2f}% (covers RT fees)")
    report.append("")
    
    # Monday
    report.append("---")
    report.append("")
    report.append("## Monday Results (Feb 9, 9:00 AM - 6:00 PM ET)")
    report.append(f"- Products with signals: **{len(monday_results)}**")
    total_sigs = sum(p['num_signals'] for p in monday_results.values())
    report.append(f"- Total signals fired: **{total_sigs}**")
    report.append("")
    report.append(format_results(monday_results, "Monday"))
    
    # Weekend
    report.append("")
    report.append("---")
    report.append("")
    report.append("## Weekend Results (Feb 7-8) — Comparison Baseline")
    report.append(f"- Products with signals: **{len(weekend_results)}**")
    total_sigs_wkd = sum(p['num_signals'] for p in weekend_results.values())
    report.append(f"- Total signals fired: **{total_sigs_wkd}**")
    report.append("")
    report.append(format_results(weekend_results, "Weekend"))
    
    # Monday vs Weekend comparison
    report.append("")
    report.append("---")
    report.append("")
    report.append("## Monday vs Weekend Comparison")
    report.append("")
    
    common = set(monday_results.keys()) & set(weekend_results.keys())
    report.append(f"Products in both periods: **{len(common)}**")
    report.append("")
    
    if common:
        comparison = []
        for product in common:
            mon = monday_results[product]
            wkd = weekend_results[product]
            
            # Find best config per product on Monday (min 3 trades)
            best_net_mon = float('-inf')
            best_cfg = None
            for key, stats in mon['results'].items():
                if stats['trades'] >= 3:
                    net = sum(stats['net_returns']) * 100
                    if net > best_net_mon:
                        best_net_mon = net
                        best_cfg = key
            
            if best_cfg is None:
                continue
            
            mon_stats = mon['results'][best_cfg]
            mon_wr = mon_stats['wins'] / mon_stats['trades'] * 100
            
            # Same config on weekend
            wkd_stats = wkd['results'].get(best_cfg)
            if wkd_stats and wkd_stats['trades'] >= 3:
                wkd_net = sum(wkd_stats['net_returns']) * 100
                wkd_wr = wkd_stats['wins'] / wkd_stats['trades'] * 100
                comparison.append({
                    'product': product,
                    'config': best_cfg,
                    'mon_trades': mon_stats['trades'],
                    'mon_wr': mon_wr,
                    'mon_net': best_net_mon,
                    'wkd_trades': wkd_stats['trades'],
                    'wkd_wr': wkd_wr,
                    'wkd_net': wkd_net,
                    'diff': best_net_mon - wkd_net,
                })
        
        if comparison:
            comparison.sort(key=lambda x: x['diff'], reverse=True)
            
            report.append("### Products that improved Monday vs Weekend")
            report.append("")
            report.append("| Product | Config | Mon Trades | Mon WR | Mon Net% | Wkd Trades | Wkd WR | Wkd Net% | Δ Net% |")
            report.append("|---------|--------|-----------|--------|----------|-----------|--------|----------|--------|")
            
            for c in comparison:
                d, t, h = c['config']
                marker = " ⬆" if c['diff'] > 0 else (" ⬇" if c['diff'] < 0 else "")
                report.append(f"| {c['product']} | {d}≥{t} {h}s | {c['mon_trades']} | {c['mon_wr']:.1f}% | {c['mon_net']:+.3f}% | {c['wkd_trades']} | {c['wkd_wr']:.1f}% | {c['wkd_net']:+.3f}% | {c['diff']:+.3f}%{marker} |")
    
    # Key findings
    report.append("")
    report.append("---")
    report.append("")
    report.append("## Key Findings")
    report.append("")
    
    # Profitable products Monday
    mon_profitable = set()
    for product, pdata in monday_results.items():
        for key, stats in pdata['results'].items():
            if stats['trades'] >= 3 and sum(stats['net_returns']) > 0:
                mon_profitable.add(product)
                break
    
    report.append(f"- **Profitable products (Monday, ≥3 trades, net > 0):** {len(mon_profitable)}/{len(monday_results)}")
    
    # Aggregate PnL
    total_mon_net = 0
    total_mon_trades = 0
    for product, pdata in monday_results.items():
        for key, stats in pdata['results'].items():
            total_mon_net += sum(stats['net_returns']) * 100
            total_mon_trades += stats['trades']
    
    # De-duplicate: each signal is counted multiple times across configs
    # Just report the best-config aggregate
    agg_net = 0
    agg_trades = 0
    for product, pdata in monday_results.items():
        best_net = float('-inf')
        best_trades = 0
        for key, stats in pdata['results'].items():
            if stats['trades'] >= 3:
                net = sum(stats['net_returns']) * 100
                if net > best_net:
                    best_net = net
                    best_trades = stats['trades']
        if best_net > float('-inf'):
            agg_net += best_net
            agg_trades += best_trades
    
    report.append(f"- **Aggregate net PnL (best config per product, ≥3 trades):** {agg_net:+.2f}% across {agg_trades} trades")
    
    # Same for weekend
    wkd_profitable = set()
    for product, pdata in weekend_results.items():
        for key, stats in pdata['results'].items():
            if stats['trades'] >= 3 and sum(stats['net_returns']) > 0:
                wkd_profitable.add(product)
                break
    
    agg_net_wkd = 0
    agg_trades_wkd = 0
    for product, pdata in weekend_results.items():
        best_net = float('-inf')
        best_trades = 0
        for key, stats in pdata['results'].items():
            if stats['trades'] >= 3:
                net = sum(stats['net_returns']) * 100
                if net > best_net:
                    best_net = net
                    best_trades = stats['trades']
        if best_net > float('-inf'):
            agg_net_wkd += best_net
            agg_trades_wkd += best_trades
    
    report.append(f"- **Profitable products (Weekend, ≥3 trades):** {len(wkd_profitable)}/{len(weekend_results)}")
    report.append(f"- **Aggregate net PnL (Weekend, best config per product):** {agg_net_wkd:+.2f}% across {agg_trades_wkd} trades")
    
    # Monday vs Weekend overall
    report.append("")
    if agg_net > agg_net_wkd:
        report.append(f"**Monday outperformed Weekend by {agg_net - agg_net_wkd:+.2f}% aggregate net PnL**")
    else:
        report.append(f"**Weekend outperformed Monday by {agg_net_wkd - agg_net:+.2f}% aggregate net PnL**")
    
    report_text = '\n'.join(report)
    
    out_path = '/home/bonsaihorn/.openclaw/workspace/analysis/augur-monday-backtest.md'
    with open(out_path, 'w') as f:
        f.write(report_text)
    
    print(report_text)
    print(f"\n\nReport saved to {out_path}", file=sys.stderr)
    print(f"Total runtime: {elapsed:.1f}s", file=sys.stderr)


if __name__ == '__main__':
    main()
