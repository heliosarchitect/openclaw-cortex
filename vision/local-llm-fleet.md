# Local LLM Fleet — Vision Document
<!-- AI.TOC: Local LLM Fleet — Vision Document — Read lines 1-20 for navigation.
  §1 Table of Contents                          → lines 17-31
  §2 1. Purpose & Scope                         → lines 32-76
  §3 2. Current State                           → lines 77-117
  §4 3. Target State                            → lines 118-166
  §5 4. Architecture                            → lines 167-247
  §6 5. Service Level Targets                   → lines 248-278
  §7 6. Tasks & Milestones                      → lines 279-307
  §8 7. Risks & Blockers                        → lines 308-322
  §9 8. Decision Log                            → lines 323-341
  §10 9. Configuration Items                     → lines 342-369
  §11 10. Definition of Done                     → lines 370-401
  Total: 401 lines | Sections: 11
-->

> *A concurrent fleet of specialist AI agents running as GPU daemons — always on, always watching, zero API cost.*

| Field | Value |
|-------|-------|
| **Program** | Local LLM Fleet — Purpose-Built Inference |
| **Parent** | LBF / Helios Operations |
| **Owner** | Matthew (Founder) / Helios (AI CTO) |
| **Status** | Phase 1 Active — 7 Modelfiles deployed |
| **Created** | 2026-02-09 |
| **Last Updated** | 2026-02-10 |
| **ITIL Process** | Service Design |

---

## Table of Contents

1. [Purpose & Scope](#1-purpose--scope)
2. [Current State](#2-current-state)
3. [Target State](#3-target-state)
4. [Architecture](#4-architecture)
5. [Service Level Targets](#5-service-level-targets)
6. [Tasks & Milestones](#6-tasks--milestones)
7. [Risks & Blockers](#7-risks--blockers)
8. [Decision Log](#8-decision-log)
9. [Configuration Items](#9-configuration-items)
10. [Definition of Done](#10-definition-of-done)

---

## 1. Purpose & Scope

### What
Local LLMs handle 95% of automated work. The API is the escalation path, not the default.

Right now, every automated task Helios runs — health checks, log analysis, message classification, email triage — burns API tokens. Most of these tasks are deterministic, narrow-scope, and repetitive. They don't need Claude. They need a small, fast model with a locked-down system prompt that does one thing well.

The Local LLM Fleet turns Ollama from "a thing that's installed" into a fleet of purpose-built inference tools. Each Modelfile is a specialist: constrained vocabulary, low temperature, domain-specific system prompt, minimal context window. They answer the question they're designed for and nothing else.

### Why
The API remains available for complex reasoning, multi-step planning, creative work, and anything that exceeds the capability floor. But the default path for routine ops is local. Always.

**Cost.** API calls for routine operations are pure waste. A health check classification doesn't need a frontier model. Every token spent on "is this log line an error?" is a token not spent on actual reasoning.

**Speed.** Local inference on an RTX 5090 is faster than a round-trip to Anthropic's API. No network latency. No rate limits. No queue.

**Availability.** Local models don't go down when Anthropic has an outage. The health monitoring system shouldn't depend on the internet to tell you your internet is down.

**Privacy.** System logs, email content, and internal metrics never leave the machine. No data sent to third-party APIs for routine classification.

**Iteration speed.** Changing a Modelfile takes seconds. Changing API prompt engineering requires a deployment. Modelfiles are the fastest feedback loop we have.

### Scope
- **In scope:** 
  - 7 specialized Modelfiles for classification and routine automation
  - Health check analysis (qa-sweep)
  - Log anomaly detection (log-analyzer)
  - Heartbeat monitoring (heartbeat-monitor)
  - Trading pattern evaluation (pattern-evaluator)
  - Ansible playbook generation (ansible-writer)
  - Discord message classification (discord-classifier)
  - Email triage automation (email-triager)
  - Integration with existing Helios agent workflows
  - Conservative escalation to API for complex cases

- **Out of scope:** 
  - Complex multi-step reasoning (remains API)
  - Creative writing or open-ended generation
  - Fine-tuning or custom model training
  - Real-time conversational AI
  - Tasks requiring >8K context window
  - Non-English language processing

---

## 2. Current State

*Honest assessment — what exists today, what doesn't.*

| Component | Status | Notes |
|-----------|--------|-------|
| Ollama | ✅ Live | Port 11434, systemd managed |
| RTX 5090 | ✅ Available | 32GB VRAM, mostly idle |
| qwen2.5:32b | ✅ Installed | 19GB, primary fleet model |
| phi3:mini | ✅ Installed | 2.2GB, legacy small model (replaced by qwen2.5) |
| llama3.1-lexi | ✅ Installed | 8.5GB, legacy general model (replaced by qwen2.5) |
| Modelfiles | ❌ Missing | Zero custom models created |
| Integration | ❌ Missing | No agent workflows use local inference |

### Current Token Burn Analysis

Conservative estimate of API tokens burned on tasks that could be local:

| Task | Frequency | Est. Tokens/Call | Daily Token Burn |
|------|-----------|-----------------|-----------------|
| Heartbeat analysis | 24/day | ~500 | 12,000 |
| Health check classification | 24/day | ~800 | 19,200 |
| Log anomaly detection | 12/day | ~1,000 | 12,000 |
| Message classification | 50/day | ~300 | 15,000 |
| Email triage | 10/day | ~600 | 6,000 |
| Pattern evaluation | 24/day | ~400 | 9,600 |
| **Total** | | | **~73,800 tokens/day** |

At ~$3/M input tokens (Claude Sonnet), that's ~$0.22/day or ~$6.70/month on routine classification work alone. The real cost isn't dollars — it's **architectural dependency.** Every automated workflow that requires an API call is a workflow that fails when the API is unavailable, slow, or rate-limited.

### What's Actually Happening (Updated 2026-02-10)

- **7 Modelfiles deployed and registered** in Ollama, all on qwen2.5:32b base ✅
- **LLM Fleet panel live** on ITSM dashboard showing all model statuses ✅
- **Modelfile TEMPLATE** created with every parameter documented ✅
- **Not yet wired** into agent workflows — models exist but no automated callers
- **No concurrent daemon architecture** yet — models available but not running as persistent agents
- **API still handles everything** — the fleet is deployed but not integrated

---

## 3. Target State

*What "done" looks like. Paint the picture.*

**Not a batch processing system. A concurrent operating system.**

Multiple small specialist models loaded in VRAM simultaneously, each running as a daemon — always on, always watching its domain. The GPU isn't a single-task processor; it's a parallel fleet of agents.

### The Fleet (Always-On Daemons)

| Agent | Model | VRAM | Role | Trigger |
|-------|-------|------|------|---------|
| **Security** | log-analyzer (3B) | ~2GB | Tails Wazuh/syslog, flags intrusions | Continuous |
| **QA** | qa-sweep (3B) | ~2GB | Health checks, service monitoring | Every 5 min |
| **Heartbeat** | heartbeat-monitor (3B) | ~2GB | Binary escalation decisions | On heartbeat |
| **Pattern Watch** | pattern-evaluator (3B) | ~2GB | Scores new pattern discoveries | On discovery |
| **Email** | email-triager (3B) | ~2GB | Classifies incoming email | On arrival |
| **Discord** | discord-classifier (3B) | ~2GB | Routes messages by intent | On message |
| **XTTS** | voice model | ~3GB | Text-to-speech for calls | On demand |

**Total concurrent VRAM: ~15GB of 32GB.** Leaves 17GB headroom for on-demand large models.

### On-Demand Models (Loaded When Needed)

| Model | VRAM | Role | When |
|-------|------|------|------|
| qwen2.5:32b | ~19GB | Complex classification, Ansible generation | Sub-agent tasks |
| coding model (TBD) | ~4-19GB | Linting, testing, code review | Engineering tasks |

Ollama dynamically loads/unloads on-demand models. Small daemon models stay resident; large models swap in for specific tasks then get evicted.

### Architecture Principles

1. **Small daemons are concurrent.** Multiple 2-3GB models fit in VRAM simultaneously. They don't compete — they cooperate.
2. **Large models are on-demand.** qwen2.5:32b or a coding model loads when needed, evicts when idle. Ollama manages this automatically.
3. **The metric is token offload rate.** Every task type handled locally = fewer API tokens = money saved. Maximize coverage, not per-model quality.
4. **Conservative escalation.** Local models handle the 90%. Claude handles the 10% that requires complex reasoning. Better to over-escalate than miss something.
5. **LoRAs add accuracy without VRAM.** Fine-tune on our specific data (fleet topology, trading vocabulary, email patterns) to reduce API escalations further.

### Integration

Agents call `ollama run <model> <input>` and get structured JSON. No wrapper libraries. No API servers. Just shell calls with reliable output formats. Daemon agents run as systemd services or long-running processes that watch their input sources (log files, message queues, API endpoints).

### The Vision

Sub-agents running 24/7 on local models = zero-cost autonomous productivity. The API becomes the escalation path, not the default. The RTX 5090 becomes a fleet of always-on crew members, each watching their station on the bridge.

---

## 4. Architecture

*How it works or will work. Include diagrams if useful.*

### 4.1 Components

**Modelfile Architecture:**
A Modelfile is a configuration overlay on a base model. It doesn't modify weights — it sets system prompt, temperature, context window, stop tokens.

```
FROM qwen2.5:32b
SYSTEM "You are a QA engineer..."
PARAMETER temperature 0.1
PARAMETER num_ctx 4096
PARAMETER stop <|end|>
```

**Seven Specialized Models:**

1. **qa-sweep** (qwen2.5:32b, temp 0.1, 4K ctx) — Health check classification
2. **log-analyzer** (qwen2.5:32b, temp 0.1, 8K ctx) — Log anomaly detection  
3. **heartbeat-monitor** (qwen2.5:32b, temp 0.0, 4K ctx) — Escalation decisions
4. **pattern-evaluator** (qwen2.5:32b, temp 0.2, 4K ctx) — Pattern quality assessment
5. **ansible-writer** (qwen2.5:32b, temp 0.3, 8K ctx) — YAML generation
6. **discord-classifier** (qwen2.5:32b, temp 0.1, 2K ctx) — Message routing
7. **email-triager** (qwen2.5:32b, temp 0.3, 4K ctx) — Email priority classification

### 4.2 Dependencies

**Hardware:** RTX 5090 (32GB VRAM) on giggletits (192.168.10.163)
**Runtime:** Ollama service on port 11434, systemd managed
**Base Model:** qwen2.5:32b (19GB) — single base model for all Modelfiles
**Integration:** Shell calls from Helios agents, JSON parsing of output

### 4.3 Integration Points

```
┌──────────────────────────────────────────────────────────┐
│                    Helios Agent Layer                      │
│                                                            │
│  ┌──────────┐ ┌──────────┐ ┌────────┐ ┌──────────────┐  │
│  │ QA/SRE   │ │ Security │ │ Comms  │ │ Infra/Ansible│  │
│  │ Agent    │ │ Agent    │ │ Agent  │ │ Agent        │  │
│  └────┬─────┘ └────┬─────┘ └───┬────┘ └──────┬───────┘  │
│       │             │           │              │           │
└───────┼─────────────┼───────────┼──────────────┼──────────┘
        │             │           │              │
        ▼             ▼           ▼              ▼
   ┌────────────────────────────────────────────────────┐
   │              Ollama Runtime — Port 11434            │
   │              RTX 5090 (32GB VRAM)                   │
   │                                                     │
   │  ┌─── ALWAYS-ON DAEMONS (concurrent, ~15GB) ────┐  │
   │  │                                                │  │
   │  │  qa-sweep (2GB)    log-analyzer (2GB)          │  │
   │  │  heartbeat (2GB)   discord-clf (2GB)           │  │
   │  │  email-triage (2GB) pattern-eval (2GB)         │  │
   │  │  XTTS voice (3GB)                              │  │
   │  │                                                │  │
   │  └────────────────────────────────────────────────┘  │
   │                                                      │
   │  ┌─── ON-DEMAND (swap in/out, up to 32GB) ──────┐  │
   │  │                                                │  │
   │  │  qwen2.5:32b (19GB) — complex tasks            │  │
   │  │  coding model (TBD) — linting, tests           │  │
   │  │  (evicts daemons temporarily if needed)        │  │
   │  │                                                │  │
   │  └────────────────────────────────────────────────┘  │
   └──────────────────────────────────────────────────────┘
```

**Workflow Example — QA Sweep:**
1. Cron triggers health check scripts
2. Health check output → `/tmp/health-check-latest.json`
3. Agent: `result=$(ollama run qa-sweep "$(cat /tmp/health-check-latest.json)")`
4. Agent parses JSON result
5. If status = CRIT → escalate to API
6. If status = OK/WARN → log, no API call

---

## 5. Service Level Targets

*ITIL SLA alignment — what are the measurable service commitments?*

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| Availability | 99.5% | Ollama service uptime monitoring |
| Response Time | < 2s for classification tasks | Median inference latency |
| Response Time | < 6s for generation tasks | Median inference latency |
| Local Handling Rate | > 95% | Ratio of local vs API escalations |
| Classification Accuracy | > 80% per model | Test suite validation |
| CRIT Detection Rate | 100% (heartbeat-monitor) | Never miss critical alerts |
| VRAM Utilization | < 15GB simultaneous | nvidia-smi monitoring |
| Model Load Time | < 5s cold start | Time to first inference |

**Performance Estimates:**

| Model | Est. Tokens/sec | Typical Output | Est. Latency |
|-------|-----------------|----------------|--------------|
| qwen2.5:32b | 40-70 tok/s | 200-500 tokens | 3-12 seconds |

**Cost Targets:**

| Approach | Monthly Cost | Annual Savings |
|----------|--------------|----------------|
| Current (all API) | ~$6.70 | — |
| Local fleet | ~$0.34 | ~$76 |
| At 10× automation | API: ~$67, Local: ~$3.40 | ~$760 |

---

## 6. Tasks & Milestones

*Numbered, checkboxed. What's done, what's next.*

### Phase 1 — Foundation & Modelfile Creation
- [ ] LLM-1: Create directory structure (`~/Projects/llm-fleet/`) (15 min)
- [ ] LLM-2: Build qa-sweep Modelfile + tests (1 hour)
- [ ] LLM-3: Build log-analyzer Modelfile + tests (1 hour)
- [ ] LLM-4: Build heartbeat-monitor Modelfile + tests (45 min)
- [ ] LLM-5: Build pattern-evaluator Modelfile + tests (1 hour)
- [ ] LLM-6: Build ansible-writer Modelfile + tests (1.5 hours)
- [ ] LLM-7: Build discord-classifier Modelfile + tests (45 min)
- [ ] LLM-8: Build email-triager Modelfile + tests (1 hour)

### Phase 2 — Integration & Validation
- [ ] LLM-9: Integration tests — benchmark speed, verify output quality, measure VRAM (2 hours)
- [ ] LLM-10: Wire into agent architecture (3 hours)

**Total estimated effort:** ~12 hours

**Critical path:** LLM-1 → (LLM-2 through LLM-8 in parallel) → LLM-9 → LLM-10

**Task Details:**
- Each Modelfile task includes: write spec, create test fixtures (good/bad inputs), test script with validation
- LLM-9 benchmarks all models, measures token savings, quality comparison vs API
- LLM-10 integrates with QA agent (qa-sweep), heartbeat system (heartbeat-monitor), adds escalation logic

---

## 7. Risks & Blockers

| ID | Risk/Blocker | Impact | Mitigation | Status |
|----|-------------|--------|------------|--------|
| R-1 | qwen2.5:32b capability floor — unlikely given 32B params but monitor | Low | Test against fixtures, already using largest viable local model | Mitigated |
| R-2 | System prompt engineering requires multiple iterations | Medium | Fast iteration cycle (<10s edit→test), document what works | Open |
| R-3 | VRAM contention with AUGUR GPU workloads | Low | Ollama auto-evicts unused models, monitor with nvidia-smi | Open |
| R-4 | Quality gap vs API leads to missed alerts | High | Conservative classification + API escalation, never miss CRITs | Open |
| R-5 | Ollama instability under sustained load | Low | Systemd restart policy, health checks, API fallback | Open |
| R-6 | Model staleness as better small models emerge | Low | Quarterly model review, Modelfiles easily portable | Open |

**Key Risk Mitigation Strategy:** Conservative classification with API escalation. Local models handle easy 95%, API handles complexity. Better to over-escalate than miss critical issues.

---

## 8. Decision Log

*Append-only. Never edit past entries.*

| Date | Decision | Rationale | Who |
|------|----------|-----------|-----|
| 2026-02-09 | Use Modelfiles over fine-tuning | Instant creation (seconds), zero training cost, fast iteration. Fine-tuning requires datasets and GPU time. System prompts sufficient for constrained tasks. | Matthew/Helios |
| 2026-02-09 | phi3:mini as default base model | ~~Smallest viable model~~ **Superseded 2026-02-10** | Matthew/Helios |
| 2026-02-09 | llama3.1-lexi for ansible-writer only | ~~YAML generation needs more capability~~ **Superseded 2026-02-10** | Matthew/Helios |
| 2026-02-10 | qwen2.5:32b as single base model for all Modelfiles | 32B params massively raises capability floor. Fits in 19GB VRAM on RTX 5090. Eliminates multi-model complexity — one base, seven system prompts. Classification accuracy likely 95%+ vs phi3's estimated 80%. | Matthew/Helios |
| 2026-02-10 | Dynamic VRAM — don't shoehorn into leftover space | Ollama evicts idle models automatically. Full 32GB available to active model. Coding models can be 32B+ — just not simultaneously with classification models. Sequential sub-agent execution means one model at a time. VRAM budget = 32GB total, not "what's left after qwen." | Matthew/Helios |
| 2026-02-10 | Metric is token offload rate, not VRAM efficiency | Every token running locally = money saved. Maximize task type coverage with specialist models. More models = more tasks handled locally = higher offload %. Goal: 90%+ local. | Matthew/Helios |
| 2026-02-09 | JSON output format mandatory | Parseable output non-negotiable. All Modelfiles output structured data for reliable integration. | Matthew/Helios |
| 2026-02-09 | Temperature 0.0-0.3 for consistency | Classification tasks need consistent output. heartbeat-monitor at 0.0 (deterministic), others 0.1-0.3. | Matthew/Helios |
| 2026-02-09 | Conservative classification + escalation | Local filters volume, API handles complexity. False positives acceptable, false negatives not. | Matthew/Helios |
| 2026-02-09 | Ollama over alternatives | Built-in Modelfile support, simple CLI, systemd integration. vLLM available if raw performance needed. | Matthew/Helios |

---

## 9. Configuration Items

*ITIL CMDB alignment — what infrastructure does this program touch?*

| CI Name | Type | Location | Owner | Status |
|---------|------|----------|-------|--------|
| giggletits | Server | 192.168.10.163 | Matthew | Live |
| RTX 5090 | Hardware | giggletits slot 1 | Matthew | Live |
| Ollama | Service | giggletits:11434 | Helios | Live |
| qwen2.5:32b | Model | Ollama registry | Helios | Live |
| phi3:mini | Model | Ollama registry | Helios | Legacy |
| llama3.1-lexi | Model | Ollama registry | Helios | Legacy |
| ~/Projects/llm-fleet/ | Directory | giggletits filesystem | Helios | Planned |
| qa-sweep | Modelfile | Ollama registry | Helios | Planned |
| log-analyzer | Modelfile | Ollama registry | Helios | Planned |
| heartbeat-monitor | Modelfile | Ollama registry | Helios | Planned |
| pattern-evaluator | Modelfile | Ollama registry | Helios | Planned |
| ansible-writer | Modelfile | Ollama registry | Helios | Planned |
| discord-classifier | Modelfile | Ollama registry | Helios | Planned |
| email-triager | Modelfile | Ollama registry | Helios | Planned |

**Resource Specifications:**
- **VRAM Budget:** 32GB total (RTX 5090) — Ollama dynamically loads/unloads models
- **Key insight:** Models don't need to fit simultaneously. Ollama evicts idle models and loads active ones on demand. Full 32GB available to whichever model is running. Sequential task execution (sub-agents) means only one model active at a time.
- **Electricity:** ~30min/day burst inference = ~$0.03/day marginal cost

---

## 10. Definition of Done

*How we know this program is complete. Measurable criteria.*

### Must Have (MVP)
- [ ] All 7 Modelfiles created and registered in Ollama
- [ ] Each Modelfile has test suite with ≥5 test fixtures  
- [ ] Valid JSON output ≥90% of the time per model
- [ ] Classification accuracy ≥80% per model on test fixtures
- [ ] heartbeat-monitor: 100% CRIT detection rate (zero false negatives)
- [ ] qa-sweep integrated into ≥1 health check workflow
- [ ] heartbeat-monitor integrated into heartbeat pipeline
- [ ] Benchmark report: tokens/sec, VRAM usage, latency per model
- [ ] Quality comparison documented: local vs API on identical inputs

### Should Have
- [ ] All 7 Modelfiles integrated into respective agent workflows
- [ ] 24-hour token savings measured and documented
- [ ] Automatic escalation logic: local → API on low confidence
- [ ] Fleet management scripts: `create-all.sh`, `test-all.sh`
- [ ] VRAM monitoring in health checks

### Nice to Have
- [ ] Dashboard panel showing local vs API split
- [ ] Automatic model upgrade testing
- [ ] Response caching for repeated inputs
- [ ] Batch inference support

---

*Template version: 1.0 — Based on ITIL 4 Service Design Package*
*LBF standard. All vision documents follow this structure.*