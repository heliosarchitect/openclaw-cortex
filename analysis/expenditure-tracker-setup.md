# LBF Expenditure Tracker 2026

## Spreadsheet Info
- **Title:** LBF Expenditure Tracker 2026
- **Spreadsheet ID:** `1SeZ9fTqekfgyRabJOChe0QpwP1LzpQMkxkwyArfS8UM`
- **URL:** https://docs.google.com/spreadsheets/d/1SeZ9fTqekfgyRabJOChe0QpwP1LzpQMkxkwyArfS8UM/edit
- **Owner:** heliosarchitectlbf@gmail.com
- **Shared with:** bonsaihorn@gmail.com (editor)
- **Created:** 2026-02-10

## Structure

### Sheet 1: Expenditures
Columns:
| Column | Field | Notes |
|--------|-------|-------|
| A | Date | Formatted yyyy-mm-dd |
| B | Category | Use valid categories below |
| C | Description | Free text |
| D | Amount | Currency formatted ($#,##0.00) |
| E | Payment Method | Free text |
| F | Receipt (Y/N) | Y or N |
| G | Tax Deductible (Y/N) | Y or N |
| H | Notes | Free text |

### Sheet 2: Summary
Auto-calculated from Expenditures sheet:
- **Totals by Category** (rows 3-13) — SUMIFS on category column
- **Monthly Totals** (rows 15-28) — SUMPRODUCT on month/year
- **YTD Total** (row 28)
- **Tax Deductible Total** (row 31) — SUMIFS where Tax Deductible = "Y"
- **Valid Categories reference** (column D)

### Valid Categories
- Infrastructure
- Software/API
- Hardware
- Domain/Hosting
- Marketing
- Professional Services
- Office/Supplies
- Travel
- Other

## Pre-populated Expenses
9 entries added for Jan-Feb 2026:
- Anthropic API (monthly, $20/mo est.)
- Domain registration ($12 annual)
- Server electricity ($15/mo est.)
- Twilio, Stripe, BLISS Pi (zero-cost entries for tracking)
- OpenClaw/gog (open source, $0)

**Current YTD Total: $82.00**

## CLI Quick Reference
```bash
# Add a new expense
gog sheets append "1SeZ9fTqekfgyRabJOChe0QpwP1LzpQMkxkwyArfS8UM" "Expenditures!A:H" \
  --values-json '[["2026-02-10","Software/API","Service Name","25.00","Credit Card","Y","Y","Notes"]]' \
  --input USER_ENTERED \
  --account heliosarchitectlbf@gmail.com

# View current data
gog sheets get "1SeZ9fTqekfgyRabJOChe0QpwP1LzpQMkxkwyArfS8UM" "Expenditures!A:H" \
  --account heliosarchitectlbf@gmail.com

# View summary
gog sheets get "1SeZ9fTqekfgyRabJOChe0QpwP1LzpQMkxkwyArfS8UM" "Summary!A:D" \
  --account heliosarchitectlbf@gmail.com
```

## Notes
- Data validation dropdowns for Category column not available via `gog` CLI — categories listed in Summary!D4:D12 as reference. Can be added manually in the Sheets UI via Data → Data validation.
- Amounts for Anthropic API and electricity are estimates — update with actual billing amounts as they come in.
- Zero-cost entries included for services that are active but not yet billing (Twilio, Stripe) to ensure they're tracked when charges begin.
