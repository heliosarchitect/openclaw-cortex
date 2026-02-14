# LBF Enterprise Operating Model
## Helios Architect LBF — Financial Model & Unit Economics
### Prepared: 2026-02-13 | Version 1.0

---

## EXECUTIVE SUMMARY

**Helios Architect LBF** is a Virginia-registered LLC operating in the AI infrastructure and digital services space. The company develops and sells AI-powered tools (MCP servers, trading systems, knowledge management), manages LLM infrastructure, and provides automation consulting.

**Current State (Feb 2026):**
- **Revenue:** Pre-revenue (first product shipped today — WEMS MCP Server v1.5.1 on PyPI)
- **Burn Rate:** ~$2,700/month ($90/day) in API + infrastructure costs
- **Products Shipped:** 1 (WEMS MCP Server — free/open-source, premium tiers pending)
- **Products In Development:** 5 (Brain-DB, ClawHub, LLM Fleet, AUGUR, Consulting)
- **Infrastructure:** 4-node homelab fleet + cloud APIs

**Financial Thesis:** Build to $5K-8K MRR within 6 months via tiered SaaS products (MCP servers, Brain-DB, LLM Fleet), supplemented by consulting revenue, with AUGUR trading as upside optionality.

---

## 1. COST STRUCTURE — CURRENT STATE

### 1.1 Monthly Operating Costs (Actual)

| Category | Monthly Cost | Annual Cost | Notes |
|----------|-------------|-------------|-------|
| **Anthropic Claude API** | $2,100 | $25,200 | ~$70/day avg (Opus 4.6 primary) |
| **OpenAI API (if used)** | $300 | $3,600 | Supplementary usage |
| **Cloud/VPS Hosting** | $40 | $480 | Light cloud footprint |
| **Domain Registrations** | $12 | $144 | Multiple domains |
| **GitHub/SaaS Subscriptions** | $30 | $360 | GitHub, dev tools |
| **Internet Service** | $100 | $1,200 | 85% business use = $1,020 deductible |
| **Electricity (server portion)** | $50 | $600 | 4-node homelab fleet |
| **PyPI / Package Hosting** | $0 | $0 | Free tier |
| **Coinbase Trading Fees** | Variable | Variable | ~0.6-1.2% per trade (maker/taker) |
| **TOTAL FIXED COSTS** | **$2,632** | **$31,584** | |

### 1.2 Infrastructure Assets

| Asset | Role | Status |
|-------|------|--------|
| **giggletits** (primary workstation) | Development, OpenClaw host, AUGUR trading | Active |
| **hpserver1** | LLM fleet (Ollama), model hosting | Active |
| **woodserve1** | Secondary compute, backups | Active |
| **blackview** | Edge/monitoring node | Active |
| **RTX 5090** (planned) | Local inference, fine-tuning | Planned CapEx |

### 1.3 Cost Breakdown by Function

```
API Costs (Claude/OpenAI):   $2,400/mo  ████████████████████████  (82%)
Infrastructure:              $  282/mo  ███                       (10%)
SaaS/Subscriptions:          $  142/mo  █                         ( 5%)
Electricity/Internet:        $  150/mo  █                         ( 5%)
                             --------
TOTAL:                       $2,632/mo  (~$90/day)
```

**Key Insight:** 82% of costs are LLM API spend. This is the primary lever — reducing API costs (via local models, caching, or model routing) directly improves margins on everything.

---

## 2. REVENUE STREAMS — DETAILED UNIT ECONOMICS

### 2.1 WEMS MCP Server (World Event Monitoring System)

**Status:** SHIPPED — v1.5.1 live on PyPI  
**Model:** Freemium SaaS (open-source core + premium tiers)

| Tier | Price | Features | Target Customer |
|------|-------|----------|-----------------|
| **Free** | $0 | 7 monitoring tools, basic thresholds | Developers, hobbyists |
| **Pro** | $9.99/mo | Custom thresholds, webhooks, all sources, priority alerts | Small teams, researchers |
| **Enterprise** | $29.99/mo | SLA, custom regions, API access, bulk alerts | Emergency mgmt, news orgs |

**Unit Economics:**
| Metric | Value |
|--------|-------|
| COGS per user | ~$0.50/mo (API calls to USGS/NOAA — free public APIs) |
| Gross Margin | ~95% (Pro), ~97% (Enterprise) |
| CAC Estimate | $5-15 (content marketing, MCP directories) |
| LTV (12-mo @ 8% churn) | ~$92 (Pro), ~$276 (Enterprise) |
| LTV:CAC Ratio | 6:1 – 18:1 |
| Breakeven Users | 264 Pro users OR 88 Enterprise users |

**Market Sizing (TAM → SAM → SOM):**
- **TAM:** MCP server market reaching $1.8B+ in 2025 (CData), tens of thousands of servers
- **SAM:** Emergency/weather monitoring niche — ~50,000 potential users (emergency managers, researchers, news desks, weather enthusiasts)
- **SOM (Year 1):** 100-300 paid users (realistic for single-product indie)

**Revenue Projections:**

| Month | Free Users | Pro Users | Enterprise Users | MRR |
|-------|-----------|-----------|-----------------|-----|
| M1 (Mar) | 50 | 5 | 1 | $80 |
| M3 (May) | 200 | 20 | 3 | $290 |
| M6 (Aug) | 500 | 60 | 10 | $900 |
| M12 (Feb 27) | 1,500 | 150 | 30 | $2,399 |

**Assumptions:** 5% free→Pro conversion, 1% free→Enterprise. MCP ecosystem directory listing drives organic growth. No paid advertising.

---

### 2.2 ClawHub Skills Marketplace

**Status:** IN CONCEPT — 10 skills built, marketplace platform needed  
**Model:** Marketplace (transaction fee + subscription bundle)  
**Time to Launch:** 2-3 weeks for MVP

| Revenue Type | Price | LBF Take |
|-------------|-------|----------|
| **Individual Premium Skills** | $5-20 each | 30% platform fee |
| **Subscription Bundle** | $29/mo | 100% (LBF-published skills) |
| **Third-Party Revenue Share** | Variable | 30% commission |

**Unit Economics:**
| Metric | Value |
|--------|-------|
| COGS per transaction | ~$0.10 (Stripe fees + compute) |
| Gross Margin | ~85-90% |
| Platform development cost | ~$3K (self-built) |
| Breakeven | ~50 subscriptions or ~500 skill sales |

**Key Skills Portfolio:**
| Skill | Price | Target |
|-------|-------|--------|
| whale-tracker | $15 one-time | Crypto traders |
| market-sentiment-analyst | $10/mo | Trading teams |
| log-analyst | $20 one-time | DevOps |
| threat-advisory (WEMS extension) | $12/mo | Security teams |

**Revenue Projections:**

| Month | Skill Sales | Subscriptions | MRR |
|-------|------------|---------------|-----|
| M1 | 10 | 3 | $180 |
| M3 | 30 | 12 | $540 |
| M6 | 60 | 30 | $1,100 |
| M12 | 100 | 80 | $2,800 |

**Risk:** OpenClaw adoption is still niche. Market depends on MCP ecosystem growth. Third-party skill supply uncertain.

---

### 2.3 Brain-DB as a Service

**Status:** IN DEVELOPMENT — Working system, needs REST API + multi-tenant  
**Model:** B2B SaaS  
**Time to Launch:** 1-2 weeks for API packaging

| Tier | Price | Features |
|------|-------|----------|
| **Starter** | $19/mo | 1 team, 10K messages, basic search |
| **Pro** | $49/mo | 5 teams, unlimited messages, semantic search, API |
| **Enterprise** | $199/mo | Custom deployment, SSO, analytics, dedicated support |

**Unit Economics:**
| Metric | Value |
|--------|-------|
| COGS per user | $2-8/mo (embedding compute, storage) |
| Gross Margin | ~85% (Starter), ~90% (Pro), ~95% (Enterprise) |
| CAC Estimate | $20-50 (B2B content marketing) |
| LTV (12-mo @ 5% churn) | $205 (Starter), $529 (Pro), $2,149 (Enterprise) |
| LTV:CAC Ratio | 4:1 – 43:1 |

**Market Sizing:**
- **TAM:** Team knowledge management — $15B+ market (Notion, Slack, Confluence)
- **SAM:** Small AI/dev teams needing unified comms + knowledge — ~200K teams globally
- **SOM (Year 1):** 20-50 paying teams (niche positioning, indie SaaS)

**Revenue Projections:**

| Month | Starter | Pro | Enterprise | MRR |
|-------|---------|-----|-----------|-----|
| M1 | 3 | 1 | 0 | $106 |
| M3 | 10 | 4 | 1 | $585 |
| M6 | 20 | 10 | 2 | $1,268 |
| M12 | 40 | 25 | 5 | $2,980 |

---

### 2.4 LLM Fleet Management Service

**Status:** IN DEVELOPMENT — Working internal system, needs customer-facing packaging  
**Model:** Managed Service SaaS  
**Time to Launch:** 2-3 weeks

| Tier | Price | Features |
|------|-------|----------|
| **Managed Fleet** | $99/mo | Ollama deployment mgmt, model routing, monitoring |
| **Fleet Plus** | $299/mo | Custom models, fine-tuning pipeline, optimization |
| **Enterprise** | $999/mo | Dedicated infrastructure, SLA, custom integrations |

**Unit Economics:**
| Metric | Value |
|--------|-------|
| COGS per customer | $15-50/mo (compute overhead, monitoring) |
| Gross Margin | ~85% (Managed), ~88% (Plus), ~95% (Enterprise) |
| Support cost per customer | $50-200/mo (semi-active, some hand-holding) |
| Net Margin (after support) | ~35% (Managed), ~70% (Plus), ~75% (Enterprise) |

**Market Context:**
- Local LLM deployment becoming mainstream (privacy, cost, latency reasons)
- Mid-size companies want local LLM without DevOps overhead
- Major cloud providers (AWS Bedrock, Azure AI) price at $500-5,000/mo — we undercut significantly

**Revenue Projections:**

| Month | Managed | Plus | Enterprise | MRR |
|-------|---------|------|-----------|-----|
| M1 | 1 | 0 | 0 | $99 |
| M3 | 3 | 1 | 0 | $596 |
| M6 | 5 | 3 | 1 | $2,391 |
| M12 | 10 | 5 | 2 | $4,483 |

**Risk:** Support-heavy, doesn't fully scale without automation. Enterprise competitors can commoditize.

---

### 2.5 AUGUR Trading Signals

**Status:** OPERATIONAL — Live trading on Coinbase, signal miner running  
**Model:** Subscription-based signal service  
**Time to Launch:** 3-4 weeks (regulatory disclaimers, performance tracking, delivery system)

**Current AUGUR Performance (Verified):**
- Signal miner processing 299 products across 105+ hours of data
- Validated signals: BNKR-USD (87.5% WR, +0.347% avg), BERA-USD (72% WR, +0.979%)
- Live trading v4 with no hardcoded values (full abstraction)
- Fee-adjusted returns via FeeLookup integration

| Tier | Price | Features |
|------|-------|----------|
| **Basic Signals** | $49/mo | Daily trend analysis, top signals, email delivery |
| **Premium Signals** | $149/mo | Real-time alerts, full signal database, API access |
| **VIP** | $299/mo | Custom analysis, priority alerts, strategy consultation |

**Unit Economics:**
| Metric | Value |
|--------|-------|
| COGS per subscriber | $5-15/mo (compute for signal mining, delivery) |
| Gross Margin | ~85% |
| Expected Churn | 15-25%/mo (high for signal services) |
| LTV (at 20% monthly churn) | $196 (Basic), $596 (Premium) |
| CAC Estimate | $30-80 (crypto community marketing) |

**Revenue Projections (Conservative — high churn):**

| Month | Basic | Premium | VIP | MRR |
|-------|-------|---------|-----|-----|
| M1 | 3 | 1 | 0 | $296 |
| M3 | 10 | 3 | 1 | $1,236 |
| M6 | 15 | 5 | 2 | $2,078 |
| M12 | 25 | 10 | 3 | $3,612 |

**Critical Risks:**
- ⚠️ **Regulatory:** Potential SEC/CFTC issues with selling trading signals. Need disclaimers, "not financial advice" framing
- ⚠️ **Performance pressure:** Signals underperform → mass churn
- ⚠️ **Liability:** Subscribers lose money → reputational/legal risk
- ⚠️ **High churn:** Signal services typically see 15-25% monthly churn

**Mitigations:** Educational framing ("market intelligence"), strong disclaimers, free trial period, performance transparency dashboard.

---

### 2.6 Automation Consulting Services

**Status:** READY — Expertise exists, needs service packaging  
**Model:** Hourly + project-based + retainer  
**Time to Launch:** 1 week (portfolio page, rate card)

| Service | Price | Scope |
|---------|-------|-------|
| **OpenClaw Setup** | $500-1,500 flat | Custom deployment, configuration, integration |
| **Agent Development** | $150/hr | Custom MCP skills, automation workflows |
| **Architecture Review** | $2,000 flat | AI infrastructure audit + recommendations |
| **Monthly Retainer** | $2,000/mo | Ongoing support, feature development, maintenance |

**Unit Economics:**
| Metric | Value |
|--------|-------|
| COGS | ~$0 (time-for-money, no material costs) |
| Gross Margin | ~95%+ |
| Effective Hourly | $150-200/hr |
| Hours Available | 10-15 hrs/week (without impacting product development) |
| Max Monthly Revenue (solo) | $6,000-9,000 |

**Revenue Projections:**

| Month | Projects | Retainers | Revenue |
|-------|----------|-----------|---------|
| M1 | 1 × $1,000 | 0 | $1,000 |
| M3 | 2 × $1,500 | 1 | $5,000 |
| M6 | 2 × $2,000 | 2 | $8,000 |
| M12 | 3 × $2,000 | 3 | $12,000 |

**Key Advantage:** Highest immediate ROI, lowest risk, fastest to revenue. **Disadvantage:** Doesn't scale, time-for-money trap.

---

## 3. CONSOLIDATED FINANCIAL PROJECTIONS

### 3.1 Revenue Forecast — Monthly Recurring Revenue (MRR)

| Stream | M1 | M3 | M6 | M12 |
|--------|-----|-----|------|------|
| WEMS MCP Server | $80 | $290 | $900 | $2,399 |
| ClawHub Marketplace | $180 | $540 | $1,100 | $2,800 |
| Brain-DB SaaS | $106 | $585 | $1,268 | $2,980 |
| LLM Fleet Mgmt | $99 | $596 | $2,391 | $4,483 |
| AUGUR Signals | $296 | $1,236 | $2,078 | $3,612 |
| Consulting | $1,000 | $5,000 | $8,000 | $12,000 |
| **TOTAL MRR** | **$1,761** | **$8,247** | **$15,737** | **$28,274** |

### 3.2 Annual Revenue Projection (Year 1 Cumulative)

```
Conservative (60% of projections):  $102,000/year  (~$8,500/mo avg)
Base Case (100% of projections):    $170,000/year  (~$14,200/mo avg)
Optimistic (150% of projections):   $255,000/year  (~$21,300/mo avg)
```

### 3.3 Expense Forecast

| Category | M1 | M3 | M6 | M12 |
|----------|-----|-----|------|------|
| API Costs (Claude/OpenAI) | $2,400 | $2,400 | $2,800 | $3,200 |
| Infrastructure | $282 | $300 | $400 | $500 |
| SaaS/Subscriptions | $142 | $160 | $200 | $250 |
| Stripe/Payment Processing (2.9%) | $51 | $239 | $456 | $820 |
| Utilities (Internet/Electric) | $150 | $150 | $150 | $150 |
| Marketing/CAC | $100 | $300 | $500 | $800 |
| Legal/Compliance | $0 | $200 | $200 | $200 |
| **TOTAL EXPENSES** | **$3,125** | **$3,749** | **$4,706** | **$5,920** |

**Note:** API costs scale sub-linearly with revenue because most products use free public APIs (WEMS) or local compute (Brain-DB, LLM Fleet). Consulting has near-zero marginal cost.

### 3.4 Profitability Timeline

| Month | Revenue | Expenses | Net Income | Cumulative |
|-------|---------|----------|------------|------------|
| M1 (Mar) | $1,761 | $3,125 | **-$1,364** | -$1,364 |
| M2 (Apr) | $3,500 | $3,200 | **$300** | -$1,064 |
| M3 (May) | $8,247 | $3,749 | **$4,498** | $3,434 |
| M4 (Jun) | $10,000 | $4,000 | **$6,000** | $9,434 |
| M5 (Jul) | $12,500 | $4,300 | **$8,200** | $17,634 |
| M6 (Aug) | $15,737 | $4,706 | **$11,031** | $28,665 |
| M12 (Feb 27) | $28,274 | $5,920 | **$22,354** | $120,000+ |

**Cash-flow positive: Month 2 (April 2026)**  
**Breakeven on cumulative losses: Month 3 (May 2026)**

---

## 4. UNIT ECONOMICS SUMMARY

### 4.1 Blended Metrics (At M6 Scale)

| Metric | Value |
|--------|-------|
| **Blended Gross Margin** | ~88% |
| **Blended Net Margin** | ~70% |
| **Average Revenue Per User (ARPU)** | $52/mo |
| **Weighted Average CAC** | $25 |
| **Weighted Average LTV** | $410 |
| **LTV:CAC Ratio** | 16:1 |
| **Payback Period** | < 1 month |
| **Monthly Burn Rate (current)** | $2,632 |
| **Months of Runway (at current burn)** | Indefinite (funded by consulting) |

### 4.2 Revenue Mix at Maturity (M12)

```
Consulting:           $12,000/mo  ████████████████████████████  (42%)
LLM Fleet:            $ 4,483/mo  ████████████                  (16%)
AUGUR Signals:        $ 3,612/mo  ██████████                    (13%)
Brain-DB:             $ 2,980/mo  ████████                      (11%)
ClawHub:              $ 2,800/mo  ████████                      (10%)
WEMS:                 $ 2,399/mo  ███████                       ( 8%)
                      ---------
TOTAL:                $28,274/mo
```

**Dependency Warning:** 42% of M12 revenue is consulting (non-scalable). Strategic goal: reduce consulting dependency to <25% by M18 as SaaS products scale.

---

## 5. STRATEGIC ANALYSIS

### 5.1 Cost Optimization Levers

| Lever | Savings | Effort | Timeline |
|-------|---------|--------|----------|
| **Local LLM routing** (Ollama for routine tasks) | -$800/mo (33% API reduction) | Medium | 2-4 weeks |
| **Prompt caching** (Claude cache hits) | -$300/mo (12% reduction) | Low | 1 week |
| **Model downgrade** (Sonnet for non-critical) | -$500/mo (20% reduction) | Low | Immediate |
| **RTX 5090 purchase** (local Opus-class) | -$1,200/mo long-term | High ($2K+ CapEx) | 4-8 weeks |
| **Total potential savings** | **-$2,800/mo** | | |

Current burn: $2,632/mo → Optimized burn: ~$800/mo (69% reduction possible)

### 5.2 Revenue Acceleration Opportunities

| Opportunity | Impact | Probability |
|-------------|--------|-------------|
| **WEMS listed on awesome-mcp-servers** | +500-1K downloads, 20-50 conversions | High (PR ready) |
| **MCP.so / mcpmarket.com listing** | +300-500 installs/month | High |
| **HackerNews/Reddit launch post** | +1K-5K eyeballs, 10-50 conversions | Medium |
| **Threat Advisory MCP (new product)** | +$500-1K MRR | High (DHS API free) |
| **Enterprise MCP bundle** (WEMS + Threat + custom) | +$2K-5K MRR | Medium |

### 5.3 Competitive Moat Assessment

| Moat Type | Strength | Notes |
|-----------|----------|-------|
| **Technical depth** | ★★★★☆ | Full-stack AI + trading + infrastructure |
| **Speed to market** | ★★★★★ | 3 releases in one day (proven today) |
| **Switching costs** | ★★☆☆☆ | Low for individual tools, higher for integrated suite |
| **Network effects** | ★★☆☆☆ | ClawHub marketplace could build this |
| **Data moat** | ★★★☆☆ | AUGUR signal library, Brain-DB knowledge graphs |
| **Brand/reputation** | ★☆☆☆☆ | Pre-revenue, no track record yet |

### 5.4 Risk Matrix

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| MCP adoption stalls | Low | Critical | Diversify beyond MCP-only products |
| API costs spike | Medium | High | Local LLM routing, caching |
| No paying customers M1-M3 | Medium | High | Consulting provides guaranteed revenue |
| AUGUR signals underperform | Medium | Medium | Don't over-invest; keep as optionality |
| Regulatory (trading signals) | Low | Critical | Strong disclaimers, educational framing |
| Solo founder burnout | High | Critical | Automate aggressively, prioritize ruthlessly |
| Major competitor enters niche | Medium | Medium | Speed advantage, niche focus |

---

## 6. 90-DAY EXECUTION ROADMAP

### Phase 1: Quick Wins (Weeks 1-2)
- [x] WEMS MCP Server shipped to PyPI ✅
- [ ] Submit to awesome-mcp-servers, MCP.so, mcpmarket.com
- [ ] Set up Stripe for WEMS Pro/Enterprise tiers
- [ ] Consulting services page + rate card
- [ ] First consulting outreach (LinkedIn, communities)

### Phase 2: Product Expansion (Weeks 3-6)
- [ ] Brain-DB REST API + multi-tenant packaging
- [ ] LLM Fleet customer-facing dashboard
- [ ] ClawHub marketplace MVP (even if just a GitHub repo + Gumroad)
- [ ] Threat Advisory MCP Server (new product, DHS API)
- [ ] AUGUR performance dashboard + signal delivery system

### Phase 3: Scale (Weeks 7-12)
- [ ] Enterprise MCP bundle pricing
- [ ] Content marketing (blog posts, tutorials, case studies)
- [ ] First retainer consulting client
- [ ] AUGUR signal subscription launch (with disclaimers)
- [ ] Evaluate: what's working? Double down on winners.

---

## 7. TAX CONSIDERATIONS

**Estimated Annual Deductions (Schedule C):**

| Category | Annual Deduction |
|----------|-----------------|
| API costs (Anthropic/OpenAI) | $25,200-31,000 |
| Cloud/Hosting | $480-600 |
| SaaS subscriptions | $360-500 |
| Internet (85% business) | $1,020 |
| Home office (simplified) | $1,500 |
| Domains | $144 |
| Hardware (Section 179) | Variable (RTX 5090 = $2K+) |
| **Total Deductions** | **$28,704 - $35,764** |

At a marginal tax rate of ~25%, this saves **$7,176 - $8,941** in taxes annually. API costs alone justify the LLC from a tax perspective.

---

## 8. KEY METRICS TO TRACK

| Metric | Target (M3) | Target (M6) | Target (M12) |
|--------|-------------|-------------|--------------|
| **Total MRR** | $8,247 | $15,737 | $28,274 |
| **Paid Subscribers** | 50 | 150 | 400 |
| **Blended Churn** | <10%/mo | <8%/mo | <6%/mo |
| **API Cost / Revenue** | <50% | <20% | <12% |
| **Consulting % of Revenue** | 60% | 50% | 42% → target <25% |
| **Products Shipped** | 3 | 5 | 6 |
| **Net Profit Margin** | 55% | 70% | 79% |

---

## 9. BOTTOM LINE

**The honest math:**

| Scenario | M6 Monthly | M12 Monthly | Year 1 Total |
|----------|-----------|-------------|--------------|
| **Conservative (60%)** | $9,442 | $16,964 | $102,000 |
| **Base Case** | $15,737 | $28,274 | $170,000 |
| **Optimistic (150%)** | $23,606 | $42,411 | $255,000 |

**Breakeven is Month 2-3.** Even the conservative case covers current burn ($2,632/mo) by Month 2, driven primarily by consulting revenue.

**The real question isn't "can LBF make money?" — it's "how fast can LBF shift from consulting (time-for-money) to SaaS (recurring, scalable)?"**

The SaaS products need to reach ~$16K MRR to replace consulting entirely. At base-case growth, that happens around Month 10-12. Until then, consulting is the bridge that funds everything.

---

*Model prepared by Helios | Last updated: 2026-02-13 | Review quarterly*
