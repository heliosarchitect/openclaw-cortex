# Local LLM Fleet — Vision Document

> *Zero-API-cost intelligence for routine operations through purpose-built local inference endpoints.*

| Field | Value |
|-------|-------|
| **Program** | Local LLM Fleet — Purpose-Built Inference |
| **Parent** | LBF / Helios Operations |
| **Owner** | Matthew (Founder) / Helios (AI CTO) |
| **Status** | Planning |
| **Created** | 2026-02-09 |
| **Last Updated** | 2026-02-09 |
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

### What's Actually Happening

- **Two generic models sit installed.** Neither has been customized. Neither is being used for anything automated.
- **No Modelfiles exist.** The entire value proposition of this project — specialized local models — is at zero.
- **Ollama is running but doing nothing useful.** It's a service consuming resources with no automated consumers.
- **The RTX 5090 is an expensive space heater.** 32GB of VRAM, idle. The most powerful consumer GPU on the market, waiting for someone to give it work.
- **Every automated task burns API tokens.** Heartbeat analysis, health checks, log review, message classification — all of it goes through the API.

---

## 3. Target State

*What "done" looks like. Paint the picture.*

A fleet of 7 specialized local inference endpoints that handle routine operations with zero API dependency. Each Modelfile is a purpose-built tool:

**qa-sweep** reads health check JSON, classifies severity (OK/WARN/CRIT), generates incident summaries. Temperature 0.1, deterministic output, 4K context. Handles 95% of health assessments locally.

**log-analyzer** processes system logs, flags security events and anomalies, ignores operational noise. Catches SSH failures, OOM kills, service crashes. SECURITY findings escalate immediately.

**heartbeat-monitor** makes binary escalation decisions on system heartbeats. Temperature 0.0, fully deterministic. Never misses a CRIT situation. False positives acceptable.

**pattern-evaluator** assesses trading pattern statistics, grades patterns as STRONG/VIABLE/WEAK/REJECT based on win rate, sample size, profit factor. Advisory only, no escalation.

**ansible-writer** generates valid Ansible YAML from plain-language requirements. Uses llama3.1-lexi for better YAML generation capability. Output passes ansible-lint.

**discord-classifier** routes Discord messages by intent (QUESTION/TASK/ALERT/UPDATE/NOISE). Enables automated response routing and priority handling.

**email-triager** classifies email importance (P1_URGENT through P4_IGNORE), suggests actions, drafts brief responses. Surfaces urgent items, auto-archives noise.

**Integration reality:** Agents call `ollama run <model> <input>` and get back structured JSON. No wrapper libraries. No API servers. Just shell calls with reliable output formats.

**Escalation design:** Local models filter the volume (95% handled locally). Complex cases escalate to API automatically. Conservative classification — better to escalate unnecessarily than miss something critical.

**Performance target:** Sub-2-second response for most classification tasks. <10GB VRAM total usage. 95%+ local handling rate for routine operations.

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
┌─────────────────────────────────────────────────┐
│                  Helios Agent Layer              │
│                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
│  │ QA/SRE   │  │ Security │  │ Infra/Ansible│  │
│  │ Agent    │  │ Agent    │  │ Agent        │  │
│  └────┬─────┘  └────┬─────┘  └──────┬───────┘  │
│       │              │               │           │
│       ▼              ▼               ▼           │
│  ┌─────────┐   ┌──────────┐  ┌────────────┐    │
│  │qa-sweep │   │log-      │  │ansible-    │    │
│  │heartbeat│   │analyzer  │  │writer      │    │
│  └────┬────┘   └────┬─────┘  └─────┬──────┘    │
│       │              │              │            │
└───────┼──────────────┼──────────────┼────────────┘
        │              │              │
        ▼              ▼              ▼
   ┌──────────────────────────────────────┐
   │          Ollama Runtime               │
   │          Port 11434                   │
   │          RTX 5090 (32GB VRAM)         │
   │                                       │
   │  ┌──────────────────────────────┐     │
   │  │ qwen2.5:32b (19GB)          │     │
   │  │ Single base, 7 Modelfiles   │     │
   │  └──────────────────────────────┘     │
   └──────────────────────────────────────┘
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
| 2026-02-10 | qwen2.5:32b as single base model for all Modelfiles | 32B params massively raises capability floor. Fits in 19GB VRAM on RTX 5090 (13GB headroom). Eliminates multi-model complexity — one base, seven system prompts. Classification accuracy likely 95%+ vs phi3's estimated 80%. | Matthew/Helios |
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
- **VRAM Budget:** qwen2.5:32b (~19GB) — single model, all Modelfiles share weights
- **Available Headroom:** 13GB of 32GB total VRAM
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