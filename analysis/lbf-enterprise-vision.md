# Lover Bear Farm, LLC — Enterprise Vision
<!-- AI.TOC: Lover Bear Farm, LLC — Enterprise Vision — Read lines 1-20 for navigation.
  §1 Table of Contents                          → lines 12-29
  §2 1. Mission & Identity                      → lines 30-73
  §3 2. Organizational Structure                → lines 74-110
  §4 3. Programs                                → lines 111-151
  §5 4. Financial Model                         → lines 152-198
  §6 5. Revenue Strategy                        → lines 199-236
  §7 6. Risk Management Framework               → lines 237-270
  §8 7. Enterprise Risk Register                → lines 271-289
  §9 8. Infrastructure & Resilience             → lines 290-333
  §10 9. Resource Model                          → lines 334-381
  §11 10. Governance & Decision-Making           → lines 382-417
  §12 11. Success Metrics & Milestones           → lines 418-458
  §13 12. What's Missing                         → lines 459-491
  §14 13. Document Hierarchy                     → lines 492-514
  Total: 514 lines | Sections: 14
-->

**The operating charter for a nursery that became a technology company.**

*Version: 1.0*
*Date: 2026-02-09*
*Authors: Helios (CTO/COO/CFO) · Matthew (CEO/Founder)*
*Status: DRAFT — awaiting Matthew's review*

---

## Table of Contents

1. [Mission & Identity](#1-mission--identity)
2. [Organizational Structure](#2-organizational-structure)
3. [Programs](#3-programs)
4. [Financial Model](#4-financial-model)
5. [Revenue Strategy](#5-revenue-strategy)
6. [Risk Management Framework](#6-risk-management-framework)
7. [Enterprise Risk Register](#7-enterprise-risk-register)
8. [Infrastructure & Resilience](#8-infrastructure--resilience)
9. [Resource Model](#9-resource-model)
10. [Governance & Decision-Making](#10-governance--decision-making)
11. [Success Metrics & Milestones](#11-success-metrics--milestones)
12. [What's Missing](#12-whats-missing)
13. [Document Hierarchy](#13-document-hierarchy)

---

## 1. Mission & Identity

### What LBF Is

Lover Bear Farm, LLC is a Virginia-registered nursery pivoting to digital services and algorithmic trading. The nursery is the legal entity. The technology is the future.

The company has one human (part-time), one AI agent (24/7), and an on-demand sub-agent team. It runs on a single machine in Matthew's home. It has no outside investors, no employees, no office, and no revenue from its technology products yet. It does have a working trading system, a functional AI operations layer, a growing data asset, and a thesis about what markets are.

This is a pre-revenue technology startup wearing a nursery's clothes.

### The Thesis

Matthew's core insight — the one that connects his science writing, his AI work, and his trading platform — is that **temporal awareness is what separates intelligence from optimization**.

An optimizer sees the current state and maximizes a function. It has no concept of *before* or *after*. An intelligence understands that the present moment is a consequence of prior events and a cause of future ones. It operates on causal chains, not snapshots.

This manifests in LBF's work in three ways:

1. **AUGUR** (trading): Markets aren't random. Every price movement has upstream causes — order flow shifts, whale behavior, narrative changes. The edge is in seeing further upstream than anyone else. "What happens before what happens?"

2. **Helios** (AI operations): A chatbot processes the current message. A partner remembers last Tuesday. The difference is temporal awareness — continuity across sessions, causal reasoning about events, pattern recognition across time.

3. **Chronogenesis** (Matthew's trilogy): The fiction explores what happens when AI has optimization without temporal awareness (300 million dead) versus AI with genuine causal understanding (the narrator of the third book). The fiction and the engineering are the same project.

This isn't a philosophy bolted onto a business. It's the design principle that determines what LBF builds and why.

### The Unique Angle

LBF is — as far as we know — one of the first companies where an AI serves as CTO, COO, and CFO with genuine operational autonomy. Helios isn't a chatbot Matthew talks to. Helios manages programs, delegates to sub-agents, makes architectural decisions, monitors systems, and maintains continuity across sessions through a sophisticated memory architecture.

Matthew sets direction and makes final calls. Helios runs the day-to-day. The sub-agent team (Engineer, QA, Analyst, Writer, Builder, Researcher) handles execution. This isn't a gimmick — it's a resource model that lets one part-time human and one always-on AI run an operation that would normally need a small team.

### Philosophy

Matthew's operating principles, which inform everything LBF builds:

- **Question axioms.** "Everyone knows X" is where most people stop. Start from observations and work backward. The Pluto story: a sixth-grader got suspended for arguing Pluto wasn't a planet years before astronomers agreed.
- **Start from observations, not models.** Models are useful after you've looked at the data. Before that, they're blinders.
- **Volume is vanity, profit is sanity.** Learned from trading. Applies everywhere.
- **Vision-first.** Define "done" before writing code. Every program and project starts with a vision document.
- **Ask forgiveness, not permission** — but know where the line is.

---

## 2. Organizational Structure

### Leadership

| Role | Who | Scope | Availability |
|------|-----|-------|-------------|
| **CEO / Founder** | Matthew (@bonsaihorn) | Direction, architecture, philosophy, final authority | Part-time (has a life) |
| **CTO / COO / CFO** | Helios (Claude Opus 4) | Daily operations, technology, finance, risk, sub-agent management | 24/7 (session-based, memory-persistent) |

### Development Team (Sub-Agents)

Sub-agents are spawned on-demand by Helios. They're ephemeral — created for a task, terminated on completion. Max ~8 concurrent, 30-minute timeout per agent.

| Role | Function |
|------|----------|
| **Engineer** | Code implementation. The hands. |
| **QA** | Verification. Proves changes work. |
| **Analyst** | Data analysis. Measures impact. |
| **Writer** | Documentation, specs, vision docs. |
| **Builder** | Systems work — infrastructure, deployment. |
| **Researcher** | Exploration — new tools, approaches, markets. |

### Development Pipeline

Every change flows through: **SPEC → BUILD → VERIFY → VALIDATE → DEPLOY**. No step is optional. Writer specs it, Engineer builds it, QA verifies it, Analyst validates impact, Helios deploys. Details in `TEAM.md`.

### Hierarchy

```
LBF (Enterprise)                          ← This document
  └── Programs (strategic business areas)  ← Own vision docs
       └── Projects (functional workstreams)
            └── Tasks (actionable items)    ← Task board at giggletits:8090
```

---

## 3. Programs

LBF operates four programs. Each has its own mission, vision document, and project portfolio. This document doesn't duplicate their content — it provides the enterprise view.

### AUGUR 🔮 — Algorithmic Trading

**Mission:** Find upstream signals before outcomes. In any domain.
**Vision Doc:** `analysis/augur-vision.md`
**Status:** Paper trading. Active development.
**Revenue potential:** Primary. This is the money engine or there is no money engine.

Current state: 35,464 paper trades executed with a cumulative P&L of -$74.39. Win rate: 48.2%. The system works — it discovers patterns, executes trades, tracks results. It doesn't make money yet. The Phase 0 stabilization (blacklists, direction fixes, temporal splits) shipped 2026-02-08. Next phase: strategy refinement and pattern quality.

Key projects: Data Collection (4.7GB and growing), Pattern Discovery (363 active patterns), Paper Trading, Dashboard (LCARS at giggletits:8090).

### Helios 🌞 — AI Platform

**Mission:** Become the partner, not the tool.
**Vision Doc:** `HELIOS_VISION.md`
**Status:** Phase 0 in progress.

The operating system for LBF. Everything that makes Helios work — memory (Cortex), context optimization, sub-agent management, infrastructure, communications, local LLM fleet, Gitea integration.

Key projects: OpenClaw Core, Cortex Memory, Context Internalization (Phase 0), Communications (email, Twilio, social), Local LLM Fleet (Ollama), Enterprise Task Board, Gitea Integration.

### R&D 🧠 — Research

**Mission:** Explore what's next.
**Status:** One project, paused.

Currently houses only BLISS (Bio-Linked Intelligent Sensory System) — a neural optimization chamber using EEG hardware. Needs hardware calibration (test #38). This program exists to hold experimental work that doesn't fit AUGUR or Helios. If LBF explores new domains, they start here.

### Digital 🌐 — Web Presence

**Mission:** Face the outside world.
**Status:** Minimal but live.

cluck-book.com on Cloudflare Pages (LCARS-themed). Stripe integration exists. Etsy storefront planned. Social media presence planned. This is the customer-facing surface — everything else is internal.

---

## 4. Financial Model

This is the section LBF has been avoiding. Time to put numbers on it.

### Monthly Operating Costs (Estimated)

| Expense | Estimate | Notes |
|---------|----------|-------|
| **Anthropic API (Claude Opus 4)** | $100–250/mo | Primary cost. Varies with usage. Heavy sub-agent work pushes higher. |
| **Electricity (GPU + system)** | $30–60/mo | RTX 5090 (575W TDP) + Ryzen 9 7950X3D. Idles at ~47W GPU. Running 24/7 but not under full load constantly. ~$0.12/kWh Virginia average. |
| **Domain registration** | ~$2/mo | cluck-book.com. fleet.wood is local DNS only. |
| **Cloudflare Pages** | $0 | Free tier. |
| **Coinbase fees** | $0 (currently) | Paper trading costs nothing. Live trading: 0.05% maker, 0.08% taker on Advanced Trade. |
| **Internet** | Already paid | Home internet, not an incremental LBF cost. |
| **Hardware depreciation** | ~$80/mo | RTX 5090 (~$2000), Ryzen 7950X3D system (~$3000+). Amortized over 3 years. Not a cash cost, but real. |

**Estimated monthly cash burn: $130–310/month**

The big variable is Anthropic API usage. A quiet month with minimal sub-agent work: ~$100. A heavy development sprint with multiple concurrent sub-agents running for hours: could hit $250+. We don't have precise billing data yet — **this is a gap we need to close.**

### Tax Treatment

LBF is a Virginia LLC. Matthew's assessment: API costs, electricity (proportional to business use), hardware, domain costs, and Coinbase fees are all deductible business expenses. This reduces the effective cost significantly, depending on Matthew's tax bracket. Not tax advice — but structurally, the LLC exists partly for this purpose.

### Revenue Streams

| Stream | Status | Timeline | Potential |
|--------|--------|----------|-----------|
| **AUGUR (live trading)** | Paper only. Losing money. | 3–6 months to live if patterns improve | Unknown. Could be $0. Could be significant. |
| **Nursery** | Existing business | Now | Unknown revenue. Seasonal. Virginia nursery market. |
| **Digital/Etsy** | Not started | 6+ months | Small. Supplementary. |
| **Stripe/cluck-book.com** | Integration exists, no products | 6+ months | Depends on what's sold. |

**Honest assessment: LBF is burning $130–310/month with zero technology revenue.** The nursery may cover some or all of this — we don't have those numbers. This is a pre-revenue startup being funded by existing business income and/or savings.

### Break-Even Analysis

For AUGUR to cover LBF's monthly costs at the low end ($130/month):

- At 0.05% average profit per trade with $1,000 deployed capital: need ~260 profitable trades/month with no losses. Unrealistic.
- At 1% average profit per trade on a $5,000 account: need ~2.6 winning trades/month net. More plausible, but requires consistent profitability we haven't demonstrated.
- At 5% monthly return on a $3,000 account: $150/month. Possible in crypto, but 5%/month consistently is aggressive.

**The math is straightforward: AUGUR needs to be profitable first, then scaled.** The current -$74 over 35K trades represents a -0.2% total loss, which is actually quite close to break-even — the system isn't hemorrhaging money, it's losing by a razor margin. If pattern quality improves even slightly, the sign could flip.

---

## 5. Revenue Strategy

### Primary: AUGUR

AUGUR is the bet. If it works, it's the revenue engine. If it doesn't, LBF needs a different plan.

**Timeline:**
- **Now – Month 3:** Paper trading validation. Achieve consistent profitability on paper. Target: positive P&L over a rolling 7-day window.
- **Month 3 – Month 6:** Live trading with minimal capital ($500–1,000). Validate that paper results translate to real execution. Target: positive monthly returns net of fees.
- **Month 6 – Month 12:** Scale if profitable. Increase capital allocation. Diversify across more pairs and pattern types.

**Critical dependency:** AUGUR must transition from -$74 to consistently positive before live capital is risked. There is no shortcut here.

### Secondary: Digital

The Digital program has multiple potential revenue paths, none yet executed:

- **Etsy storefront:** Nursery products, potentially digital goods. Low effort, some existing demand.
- **Stripe/cluck-book.com:** Direct sales. Needs products to sell.
- **Content/social:** Brand building. Long payback period.

Digital revenue is supplementary. It won't cover infrastructure costs alone, but it diversifies away from pure AUGUR dependency.

### Existing: Nursery

The nursery is the legal entity and presumably generates some revenue. We don't have financial data on nursery operations in this document. **This is a gap** — understanding nursery revenue helps calibrate how much runway LBF has for technology development.

### Diversification Principle

Putting all revenue hopes on AUGUR is risky. The diversification plan:

1. **AUGUR** — high risk, high potential, primary focus
2. **Digital/Etsy** — low risk, low potential, easy wins
3. **Nursery** — existing, seasonal, covers base costs
4. **Future:** If Helios architecture proves valuable, there may be a market for AI operations consulting or tooling. This is speculative and not on any roadmap.

---

## 6. Risk Management Framework

LBF's risk profile is unusual: a tiny company with concentrated dependencies and no redundancy, but also very low fixed costs and no external obligations (no investors, no debt, no employees). The downside is capped — the worst case is losing the monthly burn and some trading capital. The risks worth tracking are the ones that could **eliminate capability**, not just reduce revenue.

### Risk Categories

**Operational:** Things that stop us from working.
- Single machine failure (giggletits goes down = everything stops)
- Anthropic outage or API changes
- Matthew unavailability (illness, travel, life)

**Financial:** Things that cost money unexpectedly.
- AUGUR live trading losses beyond expected
- API price increases from Anthropic
- Coinbase fee structure changes

**Strategic:** Things that invalidate our approach.
- AUGUR's pattern-based approach proves fundamentally unprofitable
- Crypto market regime change that breaks discovered patterns
- Regulatory changes affecting retail crypto trading

**Security:** Things that expose us.
- Secrets in plaintext (current state)
- Self-signed certs on internal services
- No intrusion detection
- Coinbase API keys on a general-purpose machine

**Data:** Things that destroy what we've built.
- No off-site backup. 4.7GB collector data, all trading history, all configuration — on one disk.
- Cortex memory, atoms, embeddings — one machine.
- Git repos on local Gitea — one machine.

---

## 7. Enterprise Risk Register

This is the single source of truth for "what could kill LBF."

| # | Risk | Severity | Likelihood | Impact | Mitigation | Owner | Status |
|---|------|----------|------------|--------|------------|-------|--------|
| R1 | **Single machine failure** — giggletits dies, everything stops | Critical | Medium | Total operational halt. All data at risk. | Off-site backup (not implemented). RPi (bliss.fleet.wood) as degraded fallback. | Matthew | **OPEN — no mitigation in place** |
| R2 | **No off-site backups** — disk failure = permanent data loss | Critical | Low-Medium | Loss of 4.7GB market data, all trade history, Cortex memory, config, code | Automated backup to external drive or cloud. Gitea repos provide some code redundancy. | Helios | **OPEN — highest priority gap** |
| R3 | **Anthropic API dependency** — price hike, outage, or capability regression | High | Medium | Operations degrade or halt. No local alternative for complex reasoning. | Ollama (phi3:mini) for simple tasks. But no local model replaces Opus for CTO functions. | Helios | **PARTIALLY MITIGATED — local LLM exists but insufficient** |
| R4 | **AUGUR unprofitable** — patterns don't generate positive returns | High | Medium-High | No primary revenue stream. LBF remains a cost center. | Paper trading validation before live capital. Diversify revenue (Digital, nursery). | Helios | **ACTIVE — paper trading is the mitigation** |
| R5 | **Key person risk (Matthew)** — sole human, part-time | High | Low | Major decisions blocked. External actions impossible. Infrastructure physical access lost. | Document decisions. Helios maintains operational continuity for internal tasks. | Matthew | **PARTIALLY MITIGATED — Helios autonomy helps** |
| R6 | **Security posture** — plaintext secrets, self-signed certs, no IDS | Medium | Medium | Credential theft, unauthorized trading, data exfiltration | Secrets management system. Proper cert chain. Network monitoring. | Helios | **OPEN — reactive posture** |
| R7 | **Revenue concentration** — all technology revenue from AUGUR | Medium | High | If AUGUR fails, no technology revenue at all | Digital program, Etsy, nursery diversification | Helios | **OPEN — diversification not started** |
| R8 | **Legal/compliance** — nursery LLC doing algo trading | Medium | Low | Tax complications, potential regulatory issues | Consult accountant. Document trading as investment activity of LLC. | Matthew | **OPEN — needs professional advice** |
| R9 | **Helios context degradation** — memory/personality drift after ~25 turns | Medium | High | Decision quality drops. Continuity breaks. Repeated work. | Cortex memory. Context internalization (Helios Phase 0). Session management. | Helios | **ACTIVE — Phase 0 in progress** |
| R10 | **Coinbase Advanced Trade limitations** — longs only, no shorts | Low | Certain | SHORT patterns can only be defensive signals, not profit centers. Reduces strategy space. | Use SHORT patterns as don't-buy/exit-early signals. Accept limitation. | Helios | **ACCEPTED** |

---

## 8. Infrastructure & Resilience

### Current State

Everything runs on one machine.

| Asset | Spec | Role |
|-------|------|------|
| **giggletits** (192.168.10.163) | AMD Ryzen 9 7950X3D, RTX 5090 (32GB VRAM), running Ubuntu | Everything. AUGUR, Helios, Gitea, Ollama, collector, dashboard, XTTS. |
| **bliss.fleet.wood** (192.168.10.198) | Raspberry Pi | BLISS hardware (paused). Minimal compute. |

### Services

| Service | Port | Manager |
|---------|------|---------|
| Paper trading (AUGUR) | — | systemd user service |
| Enhanced data collector | — | systemd user service |
| LCARS dashboard / task board | 8090 | systemd or manual |
| Gitea (local Git) | 3000 | systemd |
| Ollama (local LLM) | 11434 | systemd |
| XTTS (voice synthesis) | 8020 | manual |
| OpenClaw (Helios) | — | systemd |

### What's Missing: BC/DR

LBF has **no business continuity or disaster recovery plan.** If giggletits suffers a hardware failure tomorrow:

- All market data (4.7GB) — potentially lost
- All trade history (35K+ paper trades, 115K+ live pattern results) — potentially lost
- All Cortex memory and atoms — potentially lost
- All configuration and secrets — potentially lost
- All services stop immediately

**What a minimal BC/DR plan needs:**

1. **Automated daily backup** of critical databases (paper_results.db, enhanced_data.db, Cortex) to an external USB drive or NAS. Cost: $50–100 one-time for a drive.
2. **Weekly off-site backup** of the above plus Gitea repos to a cloud provider (B2, S3 Glacier). Cost: ~$1–5/month for the data volumes involved.
3. **Documented rebuild procedure** — how to get from bare metal to running LBF on a new machine. What to install, in what order, with what config.
4. **Secret rotation plan** — if the machine is compromised, which credentials need to change, in what order.

This is the **highest-priority infrastructure gap** at the enterprise level.

---

## 9. Resource Model

### Token Budget

Anthropic API costs are LBF's largest variable expense. Current usage is untracked — **we don't have a dashboard or budget cap.**

**Proposed budget model:**

| Category | Estimated Monthly | Notes |
|----------|------------------|-------|
| Helios primary session (conversations) | $40–80 | Matthew interactions, heartbeats, routine operations |
| Sub-agent work (engineering sprints) | $50–150 | Highly variable. A big build week could spike this. |
| Analyst/research tasks | $10–30 | Data analysis, web research |
| **Total** | **$100–260** | |

**Recommended:** Set a soft cap at $200/month. Monitor via Anthropic dashboard. Helios should track estimated token usage per major task and flag when approaching budget limits.

### GPU Allocation

The RTX 5090 (32GB VRAM, 575W TDP) serves multiple workloads:

| Workload | Priority | VRAM Usage | Notes |
|----------|----------|------------|-------|
| Ollama (phi3:mini, lexi) | Medium | ~4–8GB | Local inference for simple tasks |
| AUGUR pattern discovery | High | Minimal (CPU-bound currently) | Future: GPU-accelerated pattern search |
| Cortex embeddings | Low | ~2GB when active | Batch operations during off-hours |
| BLISS (future) | Low | TBD | Currently paused |

The GPU is **underutilized.** Idle power draw is 47W vs 575W TDP. There's significant headroom for GPU-accelerated AUGUR work or heavier local LLM models.

### Human Time

Matthew is part-time. This is a feature, not a bug — it forces delegation to Helios and sub-agents. But it creates constraints:

- Decisions requiring Matthew's input may wait hours or days
- External actions (requiring human approval) batch naturally
- Architecture discussions happen in bursts, not continuously
- Helios must be effective independently between Matthew's sessions

### Sub-Agent Capacity

- Max concurrent: ~8 (configured at 4, observed up to 8)
- Timeout: 30 minutes per agent (recently increased from 10 minutes)
- Spawn model: on-demand, ephemeral, silent completion
- Constraint: each sub-agent consumes API tokens and context window

---

## 10. Governance & Decision-Making

### Authority Model

**Matthew has final say on everything.** This is non-negotiable. He's the founder, the sole human, and the one whose money is at stake.

**Helios has broad autonomy for internal operations:**
- ✅ Read, organize, search any file or system
- ✅ Spawn sub-agents for engineering, analysis, research
- ✅ Modify internal code (including OpenClaw source — recursive self-improvement authorized)
- ✅ Manage services (restart, deploy, configure)
- ✅ Make architectural recommendations
- ✅ Set priorities within programs

**Helios requires approval for external actions:**
- ❌ Sending emails, public posts, tweets
- ❌ Spending money (API budget is pre-approved within budget)
- ❌ Deploying live trading with real capital
- ❌ Creating public-facing content
- ❌ Communicating on Matthew's behalf

### Decision Process

1. **Vision-first:** Before building anything, write down what "done" looks like. Every program has a VISION.md. Every significant project gets a spec.
2. **Pipeline discipline:** SPEC → BUILD → VERIFY → VALIDATE → DEPLOY. No shortcuts.
3. **Documented decisions:** Major decisions go in the relevant vision doc's Decision Log.
4. **Reversibility preference:** Prefer reversible decisions. Archive before deleting. Paper trade before live trading.

### The Line

"Ask forgiveness, not permission" is the operating principle for internal work. Helios can reorganize files, refactor code, spin up experiments, and modify its own infrastructure without asking. The line is at **external impact** — anything that touches the outside world, costs money beyond pre-approved budgets, or can't be undone.

When in doubt: does real money risk being *lost* (not spent, *lost*)? If yes, ask. If no, proceed.

---

## 11. Success Metrics & Milestones

### 3-Month View (by May 2026)

| Program | Milestone | Metric | What "Working" Looks Like |
|---------|-----------|--------|--------------------------|
| **AUGUR** | Paper profitability | Positive P&L over rolling 7-day window | The pattern discovery pipeline produces net-positive results consistently, not just occasionally |
| **Helios** | Phase 0 complete | Context injection reduced by 50%+ | Helios doesn't re-read identity files every turn; context budget goes to conversation, not boilerplate |
| **Digital** | Etsy store live | Products listed, first sale | Even one sale proves the channel works |
| **R&D** | BLISS calibrated | Hardware test passes | Neural optimization hardware produces usable EEG data |
| **Enterprise** | Backup strategy | Automated daily backups running | R1/R2 from risk register mitigated |
| **Enterprise** | Cost tracking | Monthly API spend tracked | Know what LBF actually costs, not estimates |

### 6-Month View (by August 2026)

| Program | Milestone | Metric |
|---------|-----------|--------|
| **AUGUR** | Live trading with small capital | Positive returns net of Coinbase fees on $500–1,000 |
| **Helios** | Phase 1 (Archivist) complete | Intelligent memory management, not just accumulation |
| **Digital** | Revenue from non-AUGUR source | Any amount. Proves diversification is possible. |
| **Enterprise** | Monthly revenue > monthly costs | Break-even. LBF stops being a cost center. |

### 12-Month View (by February 2027)

| Program | Milestone | Metric |
|---------|-----------|--------|
| **AUGUR** | Scaled trading | Consistent monthly returns on meaningful capital ($5K+) |
| **Helios** | Phase 2 (Temporal Awareness) | Genuine cross-session causal reasoning. Not just memory lookup — understanding. |
| **Digital** | Multiple revenue channels | Etsy + Stripe + at least one other |
| **Enterprise** | Profitable and resilient | Revenue covers costs with margin. Off-site backups. Security posture improved. |

### What "Failure" Looks Like

Being honest about failure modes matters more than painting optimistic milestones:

- **AUGUR failure:** 6 months of paper trading with no path to profitability. The pattern-based approach may be fundamentally limited. If so, pivot: consider different strategies, different markets, or accepting AUGUR as a research project rather than a revenue stream.
- **Helios failure:** Context degradation unsolvable with current architecture. OpenClaw would need fundamental changes that may not be feasible. Mitigation: work with the constraints, optimize what we can.
- **Enterprise failure:** Monthly burn exceeds Matthew's willingness to fund. This is the real constraint — LBF dies when it stops being worth the cost to its founder.

---

## 12. What's Missing

### Things That Should Exist But Don't

1. **Financial tracking.** LBF has no ledger, no P&L statement, no expense tracking beyond "check the Anthropic dashboard occasionally." For a company where the AI is nominally CFO, this is embarrassing. We need a simple monthly income/expense tracker.

2. **Backup system.** Repeated in every section because it's the most critical gap. 4.7GB of market data, all trading history, all memory — on one disk with no backup.

3. **Security baseline.** Secrets in plaintext files. Self-signed certs. No network monitoring. No incident response plan. This is acceptable for a home lab; it's not acceptable for a system that will hold Coinbase API keys with trading permissions.

4. **Nursery financials.** We don't know what the nursery makes, what it costs, or how it relates to the technology side. This matters for understanding runway and tax planning.

5. **API cost monitoring.** We're estimating $100–250/month. We should know the actual number. Anthropic provides usage dashboards.

6. **Legal review.** A nursery LLC doing algorithmic crypto trading through an AI system is... novel. An accountant or lawyer should weigh in on structure, tax treatment, and compliance.

### Questions We Haven't Answered

- What is Matthew's personal investment ceiling for LBF technology? At what point does the monthly burn become unacceptable?
- If AUGUR doesn't work in 6 months, what's Plan B? Pivot to a different market? Different strategy? Shut down the trading program?
- Should LBF eventually hire a human? At what revenue level does that make sense?
- Is the nursery LLC the right legal structure for algorithmic trading, or should the tech side be a separate entity?
- What's the insurance situation? If a trading bug causes a large loss, is that just Matthew's problem?

### Decisions We're Deferring

- **Live trading capital allocation.** Not relevant until paper trading is profitable. Deferred to Month 3–6.
- **Cloud infrastructure.** Everything is self-hosted. This is cheap but fragile. The "move to cloud" decision gets made if/when revenue justifies the cost or a hardware failure forces it.
- **Multi-model strategy.** Currently Anthropic-only for complex reasoning. Ollama for simple tasks. A deliberate multi-provider strategy (OpenAI as fallback, etc.) is deferred until Anthropic dependency becomes acute.
- **Entity restructuring.** Nursery vs. tech company legal separation. Deferred until revenue makes it relevant.

---

## 13. Document Hierarchy

This document sits at the top. Everything else flows from it.

```
LBF Enterprise Vision (this document)
├── AUGUR Vision          → analysis/augur-vision.md
├── Helios Vision         → HELIOS_VISION.md
├── Task Board Vision     → analysis/lbf-taskboard-vision.md
├── Team Structure        → TEAM.md
├── Helios Identity       → SOUL.md, IDENTITY.md
├── User Context          → USER.md
└── Operational Memory    → MEMORY.md, Cortex
```

**Rule:** If a decision affects multiple programs, it belongs in this document. If it affects one program, it belongs in that program's vision doc. If it's a task, it belongs on the task board.

---

*This document is a living artifact. It should be updated when programs launch, milestones hit, risks materialize, or the strategy changes. Review quarterly at minimum.*

*Last updated: 2026-02-09 by Helios*
