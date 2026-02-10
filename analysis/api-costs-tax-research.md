# LBF Tax Write-Off Research: API Costs, Software, Hardware & Infrastructure

**Prepared:** 2026-02-10  
**For:** Helios Architect LBF (Virginia-registered LLC)  
**Tax Years:** 2025–2026  
**Disclaimer:** This is research, not tax advice. Consult a CPA for filing.

---

## TL;DR — What Matthew Should Track

| Expense Category | Deductible? | How | Schedule C Line |
|---|---|---|---|
| Anthropic/OpenAI API costs | ✅ Yes | Operating expense, full deduction | Line 27a (Other expenses) |
| Cloud hosting (VPS, AWS, etc.) | ✅ Yes | Operating expense | Line 27a |
| SaaS subscriptions (GitHub, etc.) | ✅ Yes | Operating expense | Line 27a |
| Domain registrations | ✅ Yes | Operating expense | Line 27a or Line 8 (Advertising) |
| Web hosting | ✅ Yes | Operating expense | Line 27a |
| Internet service | ✅ Partial | Business-use % only | Line 25 (Utilities) |
| RTX 5090, servers, Raspberry Pis | ✅ Yes | Section 179 or depreciation | Line 13 (Depreciation) |
| Home office | ✅ Yes | Simplified ($5/sqft) or actual | Line 30 |
| Cell phone | ✅ Partial | Business-use % only | Line 25 |
| Electricity (for servers) | ✅ Partial | Business-use % or via home office | Line 25 |

---

## 1. IRS Section 162: The Foundation

All business expense deductions flow from **IRC § 162(a)**: a deduction is allowed for *"ordinary and necessary expenses paid or incurred during the taxable year in carrying on any trade or business."*

**Two tests every expense must pass:**
1. **Ordinary** — Common and accepted in your industry/trade
2. **Necessary** — Helpful and appropriate (not indispensable, just useful)

For a digital services LLC that builds AI-powered tools (AUGUR, BLISS, Helios, LCARS dashboard), API costs, cloud infrastructure, and development tools are clearly ordinary and necessary.

**Key requirement:** The expense must be for a *trade or business*, not a hobby. The IRS applies a "profit motive" test. If the LLC shows a profit in 3 of the last 5 years, there's a presumption of business activity. If not, you need to demonstrate genuine profit intent (business plan, separate accounts, professional conduct, time invested).

> ⚠️ **LBF Consideration:** If the digital services side hasn't generated revenue yet but you're actively developing products for market (AUGUR trading system, BLISS, dashboard), document your business plan, development timeline, and revenue strategy. The nursery side generating revenue helps establish the LLC as a real business.

---

## 2. Software, SaaS & API Costs

### API Usage (Anthropic Claude, OpenAI, etc.)
- **Classification:** Operating expense under § 162
- **Treatment:** Fully deductible in the year paid
- **Rationale:** You're paying for a service (inference), not acquiring an asset. This is analogous to paying for electricity or consulting — it's consumed as used.
- **Schedule C:** Line 27a "Other expenses" — list as "AI/API services" or "Cloud computing services"

### SaaS Subscriptions (GitHub, hosting panels, monitoring tools, etc.)
- **Classification:** Operating expense under § 162
- **Treatment:** Fully deductible in the year paid
- **Note:** SaaS subscriptions are *not* Section 179 property because you don't own the software — you're paying for access. This actually simplifies things: just deduct the full amount as an operating expense.

### Off-the-Shelf Software (purchased licenses)
- **Classification:** Can use **Section 179** for immediate expensing
- **Section 179 limits (2025):** $1,250,000 deduction limit (more than enough)
- **Section 179 limits (2026):** $2,560,000 deduction limit
- **Alternative:** Amortize over 36 months under § 167(f)
- **Must be:** Commercially available, non-exclusive license, not substantially modified

### Custom/Self-Developed Software (AUGUR, BLISS, Helios)
- **Classification:** Development costs
- **Treatment:** Can either (1) deduct as current expenses in the year incurred, or (2) capitalize and amortize over 60 months
- **Important (post-2022):** Under § 174 as amended by TCJA, R&D expenses (including software development) must be capitalized and amortized over 5 years (domestic) or 15 years (foreign). This is a significant change — your own development time and API costs used for development may need to be capitalized rather than immediately expensed.
- **Practical note:** API costs for *operating* a business tool vs. *developing* it may be treated differently. Once AUGUR is "in production," API costs for running it are operating expenses. During development, they could be § 174 R&D costs.

---

## 3. Hardware Depreciation

### RTX 5090, Servers, Raspberry Pis, Networking Equipment

**Section 179 Immediate Expensing (recommended for LBF):**
- Deduct the **entire cost** in the year placed in service
- 2025 limit: $1,250,000 | 2026 limit: $2,560,000
- Must be used **>50% for business**
- If mixed use (personal + business), deduction is proportional to business-use %

**100% Bonus Depreciation (reinstated by One Big Beautiful Bill, July 2025):**
- Property acquired and placed in service **after January 19, 2025**: 100% bonus depreciation
- Property acquired **before** Jan 20, 2025: 40% in 2025, 20% in 2026
- Applies to new AND used equipment (new to your business)
- No dollar cap (unlike Section 179)

**MACRS Regular Depreciation (fallback):**
- Computers and peripherals: **5-year property**
- Straight-line or accelerated (200% declining balance)

### LBF Hardware Inventory to Track:

| Item | Est. Cost | Business Use % | Deduction Method |
|---|---|---|---|
| RTX 5090 (giggletits) | ~$2,000+ | Estimate honestly (70-90%?) | Section 179 or Bonus |
| HP Server (.104) | varies | 100% (dedicated server) | Section 179 or Bonus |
| HP Server (.107) | varies | 100% (dedicated server) | Section 179 or Bonus |
| HP Server (.143 — Wazuh) | varies | 100% (dedicated server) | Section 179 or Bonus |
| Raspberry Pi (BLISS) | ~$75-150 | 100% (dedicated) | Section 179 or expense |
| Networking equipment | varies | Business-use % | Section 179 |
| 3D Printer / OctoPrint | varies | Business-use % | Section 179 |

> **Important:** If the RTX 5090 is in a personal gaming PC that also runs business workloads, you MUST estimate and document the business-use percentage honestly. A time log (even rough) helps defend this. Running Ollama/AUGUR 18 hours a day while gaming 2 hours = ~90% business use.

---

## 4. Home Office Deduction

### Requirements (same for both methods):
- A portion of your home must be used **exclusively and regularly** as your principal place of business
- "Exclusive use" means that area is *only* for business — no dual-purpose rooms (exception: if you have a dedicated desk/area in a room, some argue for partial allocation, but this is risky)
- You must be self-employed (LLC member ✅)

### Simplified Method:
- **$5 per square foot**, max 300 sq ft = **$1,500 max deduction**
- No depreciation, no recapture on home sale
- Dead simple, minimal audit risk
- Good if your actual expenses are low or you don't want to track them

### Regular Method (Form 8829):
- Calculate actual expenses × business-use percentage
- Includes: mortgage interest/rent, property taxes, insurance, utilities, repairs, depreciation
- Business-use % = office square footage ÷ total home square footage
- Can yield much larger deductions but requires detailed records
- Depreciation must be recaptured if you sell the home

### Recommendation for LBF:
If you have a dedicated office/server room, the **regular method** likely yields more (especially with multiple servers running 24/7 consuming electricity). But the simplified method is defensible and low-maintenance.

---

## 5. Internet & Utilities (Partial Business Use)

### Internet Service:
- Deductible at your **business-use percentage**
- If you work from home full-time and the internet is essential for API calls, server management, trading systems — **50-80% business use** is defensible
- Document: keep one month's detailed log per year showing business vs personal usage patterns, then apply that ratio annually

### Electricity:
- Can be deducted via the **home office deduction** (regular method) — it's included in the utility calculation
- Or, if you have sub-metered server equipment, you could argue for a direct utility deduction
- Servers running 24/7 consume meaningful power — worth tracking

### Cell Phone:
- Business-use percentage is deductible
- Keep a log or estimate honestly (e.g., "I use my phone for 2FA, server monitoring alerts, and business communications approximately 60% of the time")

---

## 6. Domain Registration & Hosting

### Domain Registration (annual renewals):
- **Fully deductible** as an operating or advertising expense
- Schedule C Line 8 (Advertising) or Line 27a (Other expenses)
- Just keep the receipt/invoice

### Premium Domain Purchases (buying a domain for $1,000+):
- May need to be treated as an **intangible asset** and amortized over 15 years under § 197
- Standard $10-15/year registrations: just expense them

### Web Hosting:
- **Fully deductible** as an operating expense
- Same treatment as any utility or service cost

---

## 7. Sole Proprietor vs LLC (Single-Member)

For tax purposes, a **single-member LLC is a "disregarded entity"** — the IRS treats it identically to a sole proprietorship. You file **Schedule C** on your personal Form 1040.

**Key implications:**
- All deductions go on Schedule C
- You pay **self-employment tax** (15.3%) on net profit
- You can deduct 50% of self-employment tax on Form 1040
- The LLC provides **legal liability protection** but no tax difference vs sole prop
- Consider **S-Corp election** if net profit exceeds ~$40-50K — you can pay yourself a "reasonable salary" and take remaining profit as distributions, avoiding SE tax on the distribution portion

### QBI Deduction (Section 199A):
- As a pass-through entity, you may qualify for the **20% Qualified Business Income deduction**
- Phases out at higher income levels for certain service businesses
- Software/digital services may or may not be a "specified service trade or business" — consult CPA

---

## 8. Virginia-Specific Considerations

### State Income Tax:
- Virginia income tax: **2% to 5.75%** (progressive)
- Virginia generally conforms to federal tax treatment of business expenses
- LLC income flows through to your personal Virginia return (Form 760)

### Annual LLC Fee:
- **$50/year** annual registration fee (due by last day of anniversary month)
- This fee is itself a deductible business expense

### Pass-Through Entity Tax (PTET):
- Virginia offers an **elective PTE tax** (Form 502PTET) as a SALT cap workaround
- Effective for tax years 2021–2025 (check if extended)
- Allows the entity to pay state tax at entity level, members get a credit
- Mostly benefits multi-member LLCs or those hitting the $10K SALT deduction cap
- **For single-member LLC:** Less relevant unless your state tax exceeds $10K

### BPOL Tax:
- Some Virginia localities impose a **Business, Professional, and Occupational License (BPOL) tax**
- Based on gross receipts, not net income
- Check your county/city — rates and thresholds vary
- May have a minimum threshold below which you're exempt

---

## 9. Documentation Requirements

### What to Keep (for ALL deductions):

| Document | Retention Period | Notes |
|---|---|---|
| Receipts/invoices | **7 years minimum** | Digital copies (photos/PDFs) are fine |
| Bank/credit card statements | 7 years | Highlight business expenses |
| API usage logs/dashboards | 7 years | Screenshot monthly totals |
| Hardware purchase receipts | Life of asset + 7 years | Include specs, date, price |
| Home office measurements | Update annually | Floor plan sketch with dimensions |
| Business-use time logs | Keep sample periods | One month per quarter is defensible |
| Mileage log (if applicable) | 7 years | For nursery supply runs, etc. |
| Business plan / revenue docs | Ongoing | Proves profit motive |

### Best Practices:
1. **Separate bank account** for LBF business — never commingle personal/business funds
2. **Separate credit card** for business purchases (makes tracking trivial)
3. **Monthly categorization** — don't wait until tax time
4. **Screenshot API billing pages** monthly (Anthropic, OpenAI dashboards)
5. **Save all domain/hosting renewal emails**
6. **Photograph hardware** when placed in service (proves date and existence)

---

## 10. Recommended Tracking Approach

### Simple System (what Matthew should do):

1. **Dedicated business checking + credit card** (if not already)
2. **Spreadsheet or accounting app** (Wave is free, GnuCash is FOSS) with categories:
   - API Services (Anthropic, OpenAI, etc.)
   - Cloud/Hosting (VPS, domains, hosting)
   - Software Subscriptions (GitHub, SaaS tools)
   - Hardware (with date placed in service)
   - Internet (monthly × business-use %)
   - Utilities (monthly × business-use %)
   - Office Supplies
   - Home Office
3. **Monthly ritual** (5 minutes): categorize transactions, screenshot API bills
4. **Quarterly:** Review totals, make estimated tax payments if needed (Form 1040-ES)
5. **Year-end:** Export Schedule C numbers, calculate depreciation

### Estimated Tax Payments:
- If you expect to owe **$1,000+ in tax**, you should make quarterly estimated payments
- Due dates: April 15, June 15, September 15, January 15
- Penalty for underpayment — calculate using Form 2210

---

## 11. Audit Red Flags & Risk Mitigation

### Known Red Flags:
| Flag | Risk Level | Mitigation |
|---|---|---|
| Home office deduction | Medium | Use simplified method OR document meticulously |
| Schedule C losses (multiple years) | **High** | Show revenue or clear path to profitability |
| Large deductions relative to income | Medium-High | Ensure all are documented and legitimate |
| Mixed personal/business hardware | Medium | Keep honest time/usage logs |
| 100% business use claims | **High** | Almost nothing is 100% — be realistic |
| Round numbers everywhere | Low-Medium | Use actual amounts, not estimates |

### How to Stay Safe:
1. **Never claim 100% business use** on anything that could conceivably have personal use (computer, phone, internet). 85-90% is the upper bound of credibility for a work-from-home setup.
2. **Show income.** Consecutive years of Schedule C losses with a W-2 income is the #1 audit trigger for self-employed. If nursery sales provide revenue, report them.
3. **Keep contemporaneous records.** The IRS values records made at or near the time of the expense over reconstructed records.
4. **Don't inflate the home office.** A realistic 150-200 sq ft office is much safer than claiming half your house.
5. **Separate accounts.** Commingled funds make every expense questionable.

---

## 12. Specific LBF Deduction Estimate (Annual)

Rough estimate of deductible expenses (Matthew should fill in actuals):

| Category | Est. Annual Cost | Deductible Amount |
|---|---|---|
| Anthropic API | $50-200/mo → $600-2,400 | 100% |
| OpenAI API (if used) | $20-100/mo → $240-1,200 | 100% |
| Cloud/VPS hosting | $20-50/mo → $240-600 | 100% |
| Domain registrations (×N) | $10-15 each → $50-150 | 100% |
| GitHub/SaaS subscriptions | $10-50/mo → $120-600 | 100% |
| Internet service | $80-120/mo → $960-1,440 | 75-85% |
| Electricity (server portion) | varies | Via home office or direct |
| Hardware (Section 179) | one-time purchases | 100% of business-use % |
| Home office (simplified) | — | Up to $1,500 |
| **Estimated total deductions** | | **$3,000-8,000+/year** |

*Hardware purchases (RTX 5090, servers) could add thousands more in the year of purchase via Section 179.*

---

## Key Takeaways

1. **Yes, API costs are fully deductible.** They're ordinary operating expenses for a digital services business.
2. **All SaaS/subscriptions are deductible.** No depreciation needed — they're service expenses.
3. **Hardware can be fully expensed in year 1** via Section 179 or 100% bonus depreciation (post-Jan 2025).
4. **Home office is worth claiming** but be conservative with measurements.
5. **Document everything, separate your finances, and show revenue.**
6. **Consider S-Corp election** once profits are meaningful to save on self-employment tax.
7. **Make estimated quarterly payments** to avoid underpayment penalties.

---

*Sources: IRS § 162, § 167(f), § 174, § 179, IRS Publication 587, IRS Publication 334, IRS Form 8829 Instructions, NerdWallet Section 179 Guide, Section179.org, Virginia Tax (tax.virginia.gov), One Big Beautiful Bill Act (2025). Research current as of February 2026.*
