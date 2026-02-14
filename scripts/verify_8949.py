#!/usr/bin/env python3
"""Verify Form 8949 CSV for IRS filing accuracy."""
import pandas as pd
import numpy as np
import random
import sys

CSV = "/home/bonsaihorn/Projects/crypto-taxes/output/form_8949_2025_final.csv"

print("Loading CSV...")
df = pd.read_csv(CSV, dtype={'buy_trade_id': str, 'sell_trade_id': str})
print(f"Total rows: {len(df):,}")
print(f"Columns: {list(df.columns)}")
print()

issues = []

# ============================================================
# CHECK 1: Duplicate entries by sell_trade_id
# ============================================================
print("=" * 60)
print("CHECK 1: Duplicate sell_trade_id entries")
print("=" * 60)

sell_id_counts = df['sell_trade_id'].value_counts()
dup_sell_ids = sell_id_counts[sell_id_counts > 1]
# A sell_trade_id CAN appear multiple times if it was split across multiple buys
# But check for exact duplicate rows (same sell_trade_id AND same buy_trade_id)
dup_pairs = df.groupby(['sell_trade_id', 'buy_trade_id']).size()
exact_dups = dup_pairs[dup_pairs > 1]

if len(exact_dups) > 0:
    issues.append(f"CHECK 1 FAIL: {len(exact_dups)} exact duplicate (sell_trade_id, buy_trade_id) pairs")
    print(f"  ❌ FOUND {len(exact_dups)} exact duplicate (sell_trade_id, buy_trade_id) pairs!")
    print(f"  First 10:")
    for (sid, bid), count in exact_dups.head(10).items():
        print(f"    sell={sid}, buy={bid}, count={count}")
else:
    print(f"  ✅ No exact duplicate (sell_trade_id, buy_trade_id) pairs")

print(f"  ℹ️  Unique sell_trade_ids: {df['sell_trade_id'].nunique():,}")
print(f"  ℹ️  sell_trade_ids appearing >1 time (split sells): {len(dup_sell_ids):,}")
print(f"  ℹ️  Max times a sell_trade_id appears: {sell_id_counts.max()}")
print()

# ============================================================
# CHECK 2: Totals add up correctly
# ============================================================
print("=" * 60)
print("CHECK 2: Totals verification")
print("=" * 60)

total_proceeds = df['proceeds'].sum()
total_cost_basis = df['cost_basis'].sum()
total_gain_loss = df['gain_loss'].sum()
expected_gain_loss = total_proceeds - total_cost_basis

print(f"  Total proceeds:   ${total_proceeds:,.2f}")
print(f"  Total cost basis: ${total_cost_basis:,.2f}")
print(f"  Total gain/loss:  ${total_gain_loss:,.2f}")
print(f"  Expected (P - CB): ${expected_gain_loss:,.2f}")
print(f"  Difference:        ${abs(total_gain_loss - expected_gain_loss):,.6f}")

if abs(total_gain_loss - expected_gain_loss) > 0.01:
    issues.append(f"CHECK 2 FAIL: gain_loss total ({total_gain_loss:,.2f}) != proceeds - cost_basis ({expected_gain_loss:,.2f})")
    print(f"  ❌ Totals don't match!")
else:
    print(f"  ✅ Totals match (within $0.01)")

# Break down by term
for term in df['term'].unique():
    subset = df[df['term'] == term]
    print(f"\n  {term}-term:")
    print(f"    Rows:       {len(subset):,}")
    print(f"    Proceeds:   ${subset['proceeds'].sum():,.2f}")
    print(f"    Cost basis: ${subset['cost_basis'].sum():,.2f}")
    print(f"    Gain/loss:  ${subset['gain_loss'].sum():,.2f}")
print()

# ============================================================
# CHECK 3: Long-term vs Short-term classification
# ============================================================
print("=" * 60)
print("CHECK 3: Term classification (Long >= 365 days)")
print("=" * 60)

long_but_short_days = df[(df['term'] == 'Long') & (df['holding_period_days'] < 365)]
short_but_long_days = df[(df['term'] == 'Short') & (df['holding_period_days'] >= 365)]

if len(long_but_short_days) > 0:
    issues.append(f"CHECK 3 FAIL: {len(long_but_short_days)} rows classified Long but holding < 365 days")
    print(f"  ❌ {len(long_but_short_days)} rows classified as Long but holding_period_days < 365")
    print(f"  First 5:")
    for _, row in long_but_short_days.head(5).iterrows():
        print(f"    {row['description']}: {row['holding_period_days']} days, term={row['term']}")
else:
    print(f"  ✅ All Long-term entries have holding_period >= 365 days")

if len(short_but_long_days) > 0:
    issues.append(f"CHECK 3 FAIL: {len(short_but_long_days)} rows classified Short but holding >= 365 days")
    print(f"  ❌ {len(short_but_long_days)} rows classified as Short but holding_period_days >= 365")
    print(f"  First 5:")
    for _, row in short_but_long_days.head(5).iterrows():
        print(f"    {row['description']}: {row['holding_period_days']} days, term={row['term']}")
else:
    print(f"  ✅ All Short-term entries have holding_period < 365 days")

print(f"  ℹ️  Long-term count: {len(df[df['term'] == 'Long']):,}")
print(f"  ℹ️  Short-term count: {len(df[df['term'] == 'Short']):,}")
print()

# ============================================================
# CHECK 4: Spot check 10 random entries
# ============================================================
print("=" * 60)
print("CHECK 4: Spot check 10 random entries (gain_loss = proceeds - cost_basis)")
print("=" * 60)

random.seed(42)  # Reproducible
sample_indices = random.sample(range(len(df)), 10)
spot_failures = 0

for idx in sample_indices:
    row = df.iloc[idx]
    expected = round(row['proceeds'] - row['cost_basis'], 2)
    actual = round(row['gain_loss'], 2)
    match = "✅" if abs(expected - actual) < 0.015 else "❌"
    if match == "❌":
        spot_failures += 1
    print(f"  {match} Row {idx}: {row['description'][:40]:<40} "
          f"P=${row['proceeds']:.2f} - CB=${row['cost_basis']:.2f} = ${expected:.2f} "
          f"(recorded: ${actual:.2f})")

if spot_failures > 0:
    issues.append(f"CHECK 4 FAIL: {spot_failures}/10 spot-check entries had wrong gain_loss")
else:
    print(f"  ✅ All 10 spot checks passed")

# Also do a full check
print(f"\n  Full dataset check...")
df['expected_gl'] = (df['proceeds'] - df['cost_basis']).round(2)
df['gl_diff'] = (df['gain_loss'] - df['expected_gl']).abs()
bad_gl = df[df['gl_diff'] > 0.015]
print(f"  Rows where |gain_loss - (proceeds - cost_basis)| > $0.015: {len(bad_gl):,}")
if len(bad_gl) > 0:
    issues.append(f"CHECK 4 FAIL: {len(bad_gl):,} rows have gain_loss != proceeds - cost_basis")
    print(f"  First 5 bad rows:")
    for _, row in bad_gl.head(5).iterrows():
        print(f"    {row['description']}: P={row['proceeds']:.4f} CB={row['cost_basis']:.4f} "
              f"GL={row['gain_loss']:.4f} expected={row['expected_gl']:.4f} diff={row['gl_diff']:.4f}")
else:
    print(f"  ✅ All {len(df):,} rows pass gain_loss verification")
print()

# ============================================================
# CHECK 5: Cost basis overrides applied
# ============================================================
print("=" * 60)
print("CHECK 5: Cost basis overrides (buy_trade_id starting with 'OVERRIDE-')")
print("=" * 60)

overrides = df[df['buy_trade_id'].str.startswith('OVERRIDE-', na=False)]
print(f"  Override entries found: {len(overrides):,}")

if len(overrides) == 0:
    issues.append("CHECK 5 FAIL: No OVERRIDE- entries found — cost basis overrides may not have been applied")
    print(f"  ❌ No overrides found!")
else:
    print(f"  ✅ Found {len(overrides):,} override entries")
    # Show breakdown by asset
    override_assets = overrides['buy_trade_id'].str.replace('OVERRIDE-', '').value_counts()
    print(f"  Override breakdown:")
    for asset, count in override_assets.items():
        subset = overrides[overrides['buy_trade_id'] == f'OVERRIDE-{asset}']
        print(f"    {asset}: {count:,} entries, total gain/loss: ${subset['gain_loss'].sum():,.2f}")
    print(f"  Total override gain/loss: ${overrides['gain_loss'].sum():,.2f}")
    print(f"  Total override proceeds:  ${overrides['proceeds'].sum():,.2f}")
    print(f"  Total override cost basis: ${overrides['cost_basis'].sum():,.2f}")
print()

# ============================================================
# CHECK 6: Total net ~ -$45,932
# ============================================================
print("=" * 60)
print("CHECK 6: Total net gain/loss (expected ~ -$45,932)")
print("=" * 60)

print(f"  Total net gain/loss: ${total_gain_loss:,.2f}")
print(f"  Expected:            ~-$45,932.00")
diff_from_expected = total_gain_loss - (-45932.00)
print(f"  Difference:          ${diff_from_expected:,.2f}")

if abs(diff_from_expected) < 500:  # Within $500
    print(f"  ✅ Within $500 of expected")
elif abs(diff_from_expected) < 2000:
    print(f"  ⚠️  Within $2,000 of expected — verify")
    issues.append(f"CHECK 6 WARN: Net {total_gain_loss:,.2f} is ${diff_from_expected:,.2f} off from expected -$45,932")
else:
    print(f"  ❌ More than $2,000 off from expected!")
    issues.append(f"CHECK 6 FAIL: Net {total_gain_loss:,.2f} is ${diff_from_expected:,.2f} off from expected -$45,932")
print()

# ============================================================
# SUMMARY
# ============================================================
print("=" * 60)
print("VERIFICATION SUMMARY")
print("=" * 60)
if not issues:
    print("  ✅ ALL CHECKS PASSED — Data looks clean for IRS filing")
else:
    print(f"  ⚠️  {len(issues)} ISSUE(S) FOUND:")
    for i, issue in enumerate(issues, 1):
        print(f"    {i}. {issue}")

print(f"\n  Total rows: {len(df):,}")
print(f"  Total net:  ${total_gain_loss:,.2f}")

# Clean up temp column
df.drop(columns=['expected_gl', 'gl_diff'], inplace=True)

sys.exit(1 if issues else 0)
