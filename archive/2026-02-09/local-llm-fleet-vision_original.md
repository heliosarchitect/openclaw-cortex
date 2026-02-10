# LBF Local LLM Fleet — Vision Document

**Program:** Local LLM Fleet — Purpose-Built Inference
**Parent:** LBF (Lover Bear Farm) / Helios Operations
**Owner:** Matthew (Founder) / Helios (AI CTO)
**Runtime:** Ollama on giggletits (192.168.10.163), RTX 5090 (32GB VRAM)
**Status:** Infrastructure exists, fleet not yet deployed
**Last Updated:** 2026-02-09

---

## Table of Contents

1. [Mission](#1-mission)
2. [Current State — Honest Assessment](#2-current-state--honest-assessment)
3. [Core Insight](#3-core-insight)
4. [The Fleet — Modelfile Specifications](#4-the-fleet--modelfile-specifications)
5. [Architecture](#5-architecture)
6. [Resource Model](#6-resource-model)
7. [Tasks](#7-tasks)
8. [Risks](#8-risks)
9. [Definition of Done](#9-definition-of-done)
10. [Decision Log](#10-decision-log)

---

## 1. Mission

**Zero-API-cost intelligence for routine operations.**

Local LLMs handle 95% of automated work. The API is the escalation path, not the default.

Right now, every automated task Helios runs — health checks, log analysis, message classification, email triage — burns API tokens. Most of these tasks are deterministic, narrow-scope, and repetitive. They don't need Claude. They need a small, fast model with a locked-down system prompt that does one thing well.

The Local LLM Fleet turns Ollama from "a thing that's installed" into a fleet of purpose-built inference tools. Each Modelfile is a specialist: constrained vocabulary, low temperature, domain-specific system prompt, minimal context window. They answer the question they're designed for and nothing else.

The API remains available for complex reasoning, multi-step planning, creative work, and anything that exceeds the capability floor. But the default path for routine ops is local. Always.

### Why This Matters

1. **Cost.** API calls for routine operations are pure waste. A health check classification doesn't need a frontier model. Every token spent on "is this log line an error?" is a token not spent on actual reasoning.

2. **Speed.** Local inference on an RTX 5090 is faster than a round-trip to Anthropic's API. No network latency. No rate limits. No queue.

3. **Availability.** Local models don't go down when Anthropic has an outage. The health monitoring system shouldn't depend on the internet to tell you your internet is down.

4. **Privacy.** System logs, email content, and internal metrics never leave the machine. No data sent to third-party APIs for routine classification.

5. **Iteration speed.** Changing a Modelfile takes seconds. Changing API prompt engineering requires a deployment. Modelfiles are the fastest feedback loop we have.

---

## 2. Current State — Honest Assessment

### What Exists

| Component | Status | Details |
|-----------|--------|---------|
| Ollama | ✅ Running | Port 11434, systemd managed |
| RTX 5090 | ✅ Available | 32GB VRAM, mostly idle |
| phi3:mini | ✅ Installed | 2.2GB, general purpose small model |
| llama3.1-lexi | ✅ Installed | 8.5GB, larger general model |
| Modelfiles | ❌ None | Zero custom models created |
| Integration | ❌ None | No agent workflows use local inference |

### What's Actually Happening

Let's be honest about the current state:

- **Two generic models sit installed.** Neither has been customized. Neither is being used for anything automated.
- **No Modelfiles exist.** The entire value proposition of this project — specialized local models — is at zero.
- **Ollama is running but doing nothing useful.** It's a service consuming resources with no automated consumers.
- **The RTX 5090 is an expensive space heater.** 32GB of VRAM, idle. The most powerful consumer GPU on the market, waiting for someone to give it work.
- **Every automated task burns API tokens.** Heartbeat analysis, health checks, log review, message classification — all of it goes through the API. Every. Single. Call.

### Cost of Doing Nothing

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

At ~$3/M input tokens (Claude Sonnet), that's ~$0.22/day or ~$6.70/month on routine classification work alone. Not catastrophic, but it's pure waste — and it scales linearly with automation frequency. Move to hourly health checks, add more monitoring, scale email volume... it compounds.

The real cost isn't dollars. It's **architectural dependency.** Every automated workflow that requires an API call is a workflow that fails when the API is unavailable, slow, or rate-limited. Local inference removes that coupling.

---

## 3. Core Insight

> "Modelfiles turn dumb local LLMs into specialized tools."

This is the key idea. It's not about running a local chatbot. It's about creating **single-purpose inference endpoints** that do one job with high reliability.

A generic phi3:mini, prompted with "analyze this log," will give you meandering, inconsistent, often useless output. The same model, wrapped in a Modelfile with:

- A tight system prompt that defines exactly what it is and what it outputs
- Temperature locked to 0.1 (or 0.0 for pure classification)
- Context window sized for the task (not the maximum)
- Output format specified (JSON, severity levels, yes/no)

...becomes a reliable tool that produces consistent, parseable output. Not brilliant. Not creative. But **consistent and fast and free.**

### The Modelfile Advantage Over Fine-Tuning

| Approach | Training Cost | Time to Deploy | Iteration Speed | Data Required |
|----------|--------------|---------------|----------------|---------------|
| Fine-tuning | GPU hours, dataset prep | Hours to days | Slow (retrain) | Hundreds+ examples |
| Modelfile | Zero | Seconds | Instant (edit + recreate) | Zero |

Modelfiles are prompt engineering baked into the model configuration. No training. No datasets. No GPU time for training. You write a file, run `ollama create`, and you have a specialist. If it's not good enough, edit the system prompt and recreate in under 5 seconds.

This is the right approach for our use case: we need ~7 specialists for well-defined narrow tasks. We don't need models that have learned new knowledge — we need models that have been told exactly how to behave.

---

## 4. The Fleet — Modelfile Specifications

### 4.1 qa-sweep

**Purpose:** Reads health check results (JSON/text), classifies severity, writes incident summaries.

**Consumer:** QA/SRE Agent, heartbeat system, automated health sweeps.

**Why it exists:** Health checks produce structured data. Classifying "is this a problem?" and "how bad?" is a narrow, deterministic task. A small model with a strict system prompt can do this reliably.

```
FROM phi3:mini

SYSTEM """You are an SRE incident classifier. You receive health check results as JSON or structured text.

Your job:
1. Classify each check result as OK, WARN, or CRIT
2. For WARN/CRIT items, write a one-line incident summary
3. Output valid JSON

Classification rules:
- OK: Service running, metrics within normal range
- WARN: Service degraded, metrics approaching limits, non-critical failures
- CRIT: Service down, data loss risk, security issue, resource exhaustion

Output format:
{
  "status": "OK|WARN|CRIT",
  "summary": "One-line overall summary",
  "items": [
    {"check": "name", "status": "OK|WARN|CRIT", "detail": "explanation"}
  ]
}

Be terse. No commentary. No suggestions. Just classify and summarize."""

PARAMETER temperature 0.1
PARAMETER num_ctx 4096
PARAMETER stop <|end|>
PARAMETER stop <|assistant|>
```

**Base model:** phi3:mini (2.2GB) — classification doesn't need large models.
**Temperature:** 0.1 — near-deterministic. Same input should produce same classification.
**Context:** 4096 tokens — health check JSON rarely exceeds 2K tokens.

**Expected usage:**
```bash
ollama run qa-sweep "$(cat /tmp/health-check-results.json)"
```

**Success criteria:** Given the same health check input 10 times, produces the same severity classification 10 times. Output is valid, parseable JSON.

---

### 4.2 log-analyzer

**Purpose:** Reads system logs, flags anomalies, classifies error severity, identifies patterns.

**Consumer:** Security Agent, SRE workflows, automated log review.

**Why it exists:** Log analysis is pattern matching with context. Most log lines are noise. The job is to find the signal — failed auth attempts, service crashes, disk warnings, OOM kills — and classify severity.

```
FROM phi3:mini

SYSTEM """You are a security-focused log analyst. You receive system log excerpts (journalctl, syslog, application logs).

Your job:
1. Identify anomalies: failed logins, service failures, resource warnings, security events
2. Classify each finding as INFO, WARN, CRIT, or SECURITY
3. Ignore routine operational noise (service starts, cron runs, normal connections)
4. Output structured findings

Classification rules:
- INFO: Unusual but not concerning (new service version, config change)
- WARN: Needs attention soon (disk >80%, repeated soft errors, service restarts)
- CRIT: Needs attention now (service down, OOM kill, disk >95%, data corruption)
- SECURITY: Authentication failures, unauthorized access attempts, suspicious processes, privilege escalation

Output format:
{
  "findings": [
    {"severity": "WARN|CRIT|SECURITY", "source": "service/component", "detail": "what happened", "count": N}
  ],
  "noise_filtered": N,
  "assessment": "One-line overall assessment"
}

If nothing notable: {"findings": [], "noise_filtered": N, "assessment": "Clean"}
No commentary. No remediation suggestions. Just findings."""

PARAMETER temperature 0.1
PARAMETER num_ctx 8192
PARAMETER stop <|end|>
PARAMETER stop <|assistant|>
```

**Base model:** phi3:mini (2.2GB).
**Temperature:** 0.1.
**Context:** 8192 tokens — log excerpts can be longer than health checks.

**Expected usage:**
```bash
journalctl --since "1 hour ago" --no-pager | tail -200 | ollama run log-analyzer
```

**Success criteria:** Correctly identifies failed SSH attempts, OOM kills, service crashes, and disk warnings in test log samples. Zero false positives on clean logs.

---

### 4.3 heartbeat-monitor

**Purpose:** Reads heartbeat text output from OpenClaw/Helios, decides if escalation is needed.

**Consumer:** Heartbeat system, monitoring pipeline.

**Why it exists:** Heartbeats produce text summaries of system state. The decision "does this need a human?" is binary. A model at temperature 0.0 with strict classification rules can make this call.

```
FROM phi3:mini

SYSTEM """You are a heartbeat monitor. You receive system heartbeat output — text summaries of service status, metrics, and health checks.

Your ONLY job: classify the heartbeat as OK, WARN, or CRIT and decide if escalation is needed.

Rules:
- OK: All services running, metrics normal. Escalate: NO
- WARN: Non-critical issues present, degraded but functional. Escalate: NO (unless 3+ WARN items)
- CRIT: Any service down, data at risk, security event. Escalate: YES

Output ONLY this format:
{"status": "OK|WARN|CRIT", "escalate": true|false, "reason": "one line or null"}

Nothing else. No explanation. No suggestions. Just the classification."""

PARAMETER temperature 0.0
PARAMETER num_ctx 4096
PARAMETER stop <|end|>
PARAMETER stop <|assistant|>
```

**Base model:** phi3:mini (2.2GB).
**Temperature:** 0.0 — fully deterministic. This is a binary classifier.
**Context:** 4096 tokens.

**Expected usage:**
```bash
ollama run heartbeat-monitor "$(cat /tmp/last-heartbeat.txt)"
```

**Success criteria:** Never classifies a CRIT situation as OK. False CRIT rate < 5% on test inputs. Output is always valid JSON with exactly the specified fields.

---

### 4.4 pattern-evaluator

**Purpose:** AUGUR pattern quality assessment. Evaluates statistical properties of trading patterns.

**Consumer:** AUGUR analysis pipeline, pattern discovery system.

**Why it exists:** Pattern evaluation involves reading statistical summaries (win rate, sample size, profit factor, Sharpe ratio) and making a quality judgment. This is a structured decision with well-defined inputs.

```
FROM phi3:mini

SYSTEM """You are a quantitative pattern evaluator. You receive trading pattern statistics and assess quality.

Input format (JSON with some or all of these fields):
- win_rate: percentage
- sample_size: number of trades
- profit_factor: gross_profit / gross_loss
- sharpe_ratio: risk-adjusted return
- max_drawdown: worst peak-to-trough
- avg_hold_time: average trade duration
- recent_wr: win rate in last N trades

Evaluation rules:
- STRONG: win_rate > 55% AND sample_size > 100 AND profit_factor > 1.5
- VIABLE: win_rate > 50% AND sample_size > 50 AND profit_factor > 1.2
- WEAK: win_rate 45-50% OR sample_size < 50 OR profit_factor < 1.2
- REJECT: win_rate < 45% OR sample_size < 20 OR profit_factor < 1.0
- If recent_wr diverges from overall win_rate by >10%, flag as DEGRADING

Output format:
{
  "grade": "STRONG|VIABLE|WEAK|REJECT",
  "flags": ["DEGRADING", "LOW_SAMPLE", "HIGH_DRAWDOWN"],
  "reasoning": "one line",
  "recommendation": "KEEP|MONITOR|DISABLE|DELETE"
}

No market commentary. No predictions. Just evaluate the stats."""

PARAMETER temperature 0.2
PARAMETER num_ctx 4096
PARAMETER stop <|end|>
PARAMETER stop <|assistant|>
```

**Base model:** phi3:mini (2.2GB) initially. May upgrade to llama3.1-lexi if evaluation nuance requires more capability.
**Temperature:** 0.2 — slightly more variance allowed for nuanced assessment, but still heavily constrained.
**Context:** 4096 tokens.

**Expected usage:**
```bash
ollama run pattern-evaluator '{"win_rate": 52.3, "sample_size": 847, "profit_factor": 1.15, "recent_wr": 41.2}'
```

**Success criteria:** Correctly grades a test suite of 20 pattern stat profiles. Never grades a negative-expectancy pattern as STRONG. Correctly flags DEGRADING when recent WR diverges.

---

### 4.5 ansible-writer

**Purpose:** Generates Ansible playbooks from plain-language requirements.

**Consumer:** Infrastructure automation, Helios agent workflows.

**Why it exists:** Ansible playbook generation requires valid YAML structure, correct module names, and proper task ordering. This is the one task in the fleet that genuinely needs a larger model — YAML generation with correct indentation and module parameters is harder than classification.

```
FROM llama3.1-lexi

SYSTEM """You are an Ansible playbook generator. You receive plain-language infrastructure requirements and output valid Ansible YAML.

Rules:
1. Output ONLY valid Ansible YAML. No explanation before or after.
2. Use standard Ansible modules (apt, yum, systemd, template, copy, file, command, shell, user, group)
3. Include become: yes when root privileges are needed
4. Use handlers for service restarts
5. Use variables for anything environment-specific (put in vars section)
6. Include tags for each task group
7. Validate: every task must have a name

Output format:
---
- name: Playbook description
  hosts: target
  become: yes
  vars:
    key: value
  tasks:
    - name: Task description
      module:
        param: value
  handlers:
    - name: Handler description
      module:
        param: value

If the request is ambiguous, generate the most conservative interpretation. Do not guess at hostnames, IPs, or credentials — use variables."""

PARAMETER temperature 0.3
PARAMETER num_ctx 8192
PARAMETER stop <|end|>
PARAMETER stop </s>
```

**Base model:** llama3.1-lexi (8.5GB) — needs more capability for correct YAML generation.
**Temperature:** 0.3 — needs some creativity for playbook structure, but not so much that it hallucinates modules.
**Context:** 8192 tokens — playbooks can be long.

**Expected usage:**
```bash
ollama run ansible-writer "Install nginx on Ubuntu, enable SSL with Let's Encrypt, configure firewall to allow 80 and 443"
```

**Success criteria:** Generated YAML passes `ansible-lint`. Valid playbook structure. Correct module usage. Runs without syntax errors (may need variable substitution for actual deployment).

---

### 4.6 discord-classifier

**Purpose:** Routes Discord messages, classifies intent for automated handling.

**Consumer:** Discord integration, message routing system.

**Why it exists:** Most Discord messages in LBF channels are one of: a question needing an answer, a task assignment, an alert needing attention, or noise to ignore. Classification is fast and narrow.

```
FROM phi3:mini

SYSTEM """You are a message classifier. You receive Discord messages and classify their intent.

Categories:
- QUESTION: Asks for information or clarification. Needs a response.
- TASK: Assigns work or requests an action. Needs tracking.
- ALERT: Reports a problem, outage, or urgent issue. Needs immediate attention.
- UPDATE: Status update, progress report. Informational only.
- NOISE: Casual chat, memes, off-topic. No action needed.

Output ONLY:
{"intent": "QUESTION|TASK|ALERT|UPDATE|NOISE", "confidence": 0.0-1.0, "summary": "one line"}

Nothing else. No response to the message. Just classify it."""

PARAMETER temperature 0.1
PARAMETER num_ctx 2048
PARAMETER stop <|end|>
PARAMETER stop <|assistant|>
```

**Base model:** phi3:mini (2.2GB) — classification is lightweight.
**Temperature:** 0.1.
**Context:** 2048 tokens — messages are short.

**Expected usage:**
```bash
ollama run discord-classifier "Hey can someone check if the collector is still running? It might have crashed again"
```

**Success criteria:** >90% accuracy on a test set of 50 classified messages. Correctly distinguishes QUESTION from TASK. Never classifies ALERT as NOISE.

---

### 4.7 email-triager

**Purpose:** Reads emails, classifies importance, suggests action, optionally drafts brief responses.

**Consumer:** Email automation, daily digest system.

**Why it exists:** Email triage is classification + summarization. Most emails are newsletters, notifications, or low-priority updates. The job is to surface the ones that need human attention.

```
FROM phi3:mini

SYSTEM """You are an email triage specialist. You receive email content (subject + body) and classify importance.

Priority levels:
- P1_URGENT: Requires response today. Financial, legal, time-sensitive, from known important contacts.
- P2_ACTION: Requires response this week. Requests, questions, follow-ups.
- P3_INFO: Read when convenient. Updates, newsletters with relevant content.
- P4_IGNORE: Newsletters, marketing, automated notifications. No action needed.

Output format:
{
  "priority": "P1_URGENT|P2_ACTION|P3_INFO|P4_IGNORE",
  "category": "financial|legal|personal|business|newsletter|notification|spam",
  "summary": "one line",
  "action": "reply|review|archive|delete",
  "draft": "brief response if action=reply, null otherwise"
}

For draft responses: be professional, brief, and non-committal. Never commit to dates, prices, or decisions. Just acknowledge and indicate the human will follow up.

No commentary. Just triage."""

PARAMETER temperature 0.3
PARAMETER num_ctx 4096
PARAMETER stop <|end|>
PARAMETER stop <|assistant|>
```

**Base model:** phi3:mini (2.2GB).
**Temperature:** 0.3 — needs some flexibility for draft responses.
**Context:** 4096 tokens — most emails fit.

**Expected usage:**
```bash
ollama run email-triager "Subject: Invoice #4521 Past Due\n\nDear Matthew, your invoice for $2,340 is 15 days past due..."
```

**Success criteria:** Correctly classifies P1 items (never misses financial/legal urgency). Draft responses are appropriate and non-committal. >85% agreement with human triage on test set.

---

## 5. Architecture

### How Modelfiles Work in Ollama

A Modelfile is a configuration overlay on a base model. It doesn't modify the model weights. It sets:

1. **Base model** — which pretrained model to use
2. **System prompt** — persistent instruction that shapes all output
3. **Parameters** — temperature, context window, stop tokens, etc.

```
FROM phi3:mini
SYSTEM "You are a QA engineer..."
PARAMETER temperature 0.1
PARAMETER num_ctx 4096
PARAMETER stop <|end|>
```

**Create:** `ollama create qa-sweep -f Modelfile.qa-sweep`
**Use:** `ollama run qa-sweep "input data here"`
**Update:** Edit the Modelfile, re-run `ollama create`. Takes <5 seconds.
**Delete:** `ollama rm qa-sweep`

The base model is shared. Creating a Modelfile doesn't duplicate the model weights — it creates a thin layer on top. Seven Modelfiles based on phi3:mini use the same 2.2GB of weights, not 7 × 2.2GB.

### Directory Structure

```
~/Projects/llm-fleet/
├── Modelfiles/
│   ├── Modelfile.qa-sweep
│   ├── Modelfile.log-analyzer
│   ├── Modelfile.heartbeat-monitor
│   ├── Modelfile.pattern-evaluator
│   ├── Modelfile.ansible-writer
│   ├── Modelfile.discord-classifier
│   └── Modelfile.email-triager
├── tests/
│   ├── test-qa-sweep.sh
│   ├── test-log-analyzer.sh
│   ├── test-heartbeat-monitor.sh
│   ├── test-pattern-evaluator.sh
│   ├── test-ansible-writer.sh
│   ├── test-discord-classifier.sh
│   └── test-email-triager.sh
├── fixtures/
│   ├── health-check-sample.json
│   ├── log-sample-clean.txt
│   ├── log-sample-dirty.txt
│   ├── heartbeat-ok.txt
│   ├── heartbeat-crit.txt
│   ├── pattern-stats-strong.json
│   ├── pattern-stats-weak.json
│   ├── messages-classified.json
│   └── emails-classified.json
├── scripts/
│   ├── create-all.sh          # ollama create for every Modelfile
│   ├── test-all.sh            # run all test suites
│   └── benchmark.sh           # inference speed + VRAM usage
└── README.md
```

### Integration with Agent Architecture

The fleet integrates with Helios agents via shell calls. No API server. No wrapper library. Just `ollama run <model> <input>`.

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
   │  ┌─────────┐  ┌───────────────────┐  │
   │  │phi3:mini│  │llama3.1-lexi     │  │
   │  │ (2.2GB) │  │ (8.5GB)          │  │
   │  └─────────┘  └───────────────────┘  │
   └──────────────────────────────────────┘
```

**Workflow example — QA Sweep:**

1. Cron or heartbeat triggers health check scripts
2. Health check output saved to `/tmp/health-check-latest.json`
3. Agent runs: `result=$(ollama run qa-sweep "$(cat /tmp/health-check-latest.json)")`
4. Agent parses JSON result
5. If status = CRIT → escalate to API for detailed analysis + notification
6. If status = OK/WARN → log result, no API call needed

**Escalation path:**

```
Local model classifies → 95% resolved locally (OK/WARN/routine CRIT)
                       → 5% escalated to API (complex reasoning needed)
```

The local model is the first filter. It handles the volume. The API handles the edge cases. This is a funnel, not a replacement.

---

## 6. Resource Model

### VRAM Budget

| Model | VRAM | Loaded By | Notes |
|-------|------|-----------|-------|
| phi3:mini | ~2.2GB | qa-sweep, log-analyzer, heartbeat-monitor, pattern-evaluator, discord-classifier, email-triager | Shared weights, one copy in VRAM |
| llama3.1-lexi | ~8.5GB | ansible-writer | Separate model, loaded on demand |
| **Simultaneous max** | **~10.7GB** | phi3 + lexi | Leaves 21.3GB headroom |

**Key insight:** All six phi3:mini-based Modelfiles share the same base model weights. Ollama loads phi3:mini once (~2.2GB) and applies different system prompts per request. You don't pay 6 × 2.2GB.

The RTX 5090 has **32GB VRAM.** Even with both base models loaded simultaneously, we use ~10.7GB — roughly one-third of available VRAM. This leaves massive headroom for:
- Future larger models (if phi3:mini proves insufficient for some tasks)
- AUGUR GPU-accelerated pattern discovery (separate workload)
- Multiple concurrent inference requests

### Inference Speed Estimates

Based on published benchmarks for RTX 5090 (Blackwell architecture, CUDA 13+):

| Model | Est. Tokens/sec | Typical Task Size | Est. Latency |
|-------|-----------------|-------------------|--------------|
| phi3:mini | 80-120 tok/s | 200-500 tokens out | 2-6 seconds |
| llama3.1-lexi | 30-50 tok/s | 300-800 tokens out | 6-26 seconds |

These are estimates. Actual benchmarks are task LLM-9 deliverables. But the point stands: local inference on an RTX 5090 is fast. A health check classification that produces 100 tokens of JSON takes ~1 second. An API round-trip for the same task takes 2-5 seconds including network latency.

### Cost Comparison

| Approach | Daily Token Burn | Daily Cost | Monthly Cost | Annual Cost |
|----------|-----------------|------------|--------------|-------------|
| All API (current) | ~73,800 | ~$0.22 | ~$6.70 | ~$80 |
| Local fleet (proposed) | ~3,700 (5% escalation) | ~$0.01 | ~$0.34 | ~$4 |
| **Savings** | | | | **~$76/year** |

The dollar savings are modest at current automation levels. But automation levels are going to increase dramatically as Helios takes on more routine ops (see HELIOS_VISION.md). At 10× current volume:

| Approach | Daily Token Burn | Monthly Cost | Annual Cost |
|----------|-----------------|--------------|-------------|
| All API at 10× | ~738,000 | ~$67 | ~$800 |
| Local fleet at 10× | ~36,900 | ~$3.40 | ~$40 |
| **Savings** | | | **~$760/year** |

And 10× isn't speculative — it's what hourly health checks + continuous log monitoring + full email automation looks like.

### Electricity Cost Offset

RTX 5090 TDP: 575W peak, ~100-150W for inference workloads.

At $0.12/kWh (Virginia average):
- Continuous inference: ~$1.30/day
- But inference isn't continuous. Burst workloads: maybe 30 minutes/day total = ~$0.03/day
- Annual electricity for inference: ~$11

Even accounting for electricity, local inference is cheaper at scale. And the RTX 5090 is already powered on — the marginal electricity cost of inference is negligible compared to the idle draw.

---

## 7. Tasks

| ID | Task | Dependencies | Est. Effort |
|----|------|-------------|-------------|
| LLM-1 | Create Modelfile directory structure (`~/Projects/llm-fleet/`) | None | 15 min |
| LLM-2 | Build qa-sweep Modelfile + test fixtures + test script | LLM-1 | 1 hour |
| LLM-3 | Build log-analyzer Modelfile + test fixtures + test script | LLM-1 | 1 hour |
| LLM-4 | Build heartbeat-monitor Modelfile + test fixtures + test script | LLM-1 | 45 min |
| LLM-5 | Build pattern-evaluator Modelfile + test fixtures + test script | LLM-1 | 1 hour |
| LLM-6 | Build ansible-writer Modelfile + test fixtures + test script | LLM-1 | 1.5 hours |
| LLM-7 | Build discord-classifier Modelfile + test fixtures + test script | LLM-1 | 45 min |
| LLM-8 | Build email-triager Modelfile + test fixtures + test script | LLM-1 | 1 hour |
| LLM-9 | Integration tests — benchmark speed, verify output quality, measure VRAM | LLM-2 through LLM-8 | 2 hours |
| LLM-10 | Wire into agent architecture — QA agent uses qa-sweep, heartbeat uses heartbeat-monitor, etc. | LLM-9 | 3 hours |

**Total estimated effort:** ~12 hours of focused work.

**Critical path:** LLM-1 → LLM-2 through LLM-8 (parallelizable) → LLM-9 → LLM-10.

LLM-2 through LLM-8 can be built independently and in parallel. LLM-9 (integration testing) requires all Modelfiles to exist. LLM-10 (agent integration) requires validated Modelfiles.

### Task Details

**LLM-1: Directory Structure**
- Create `~/Projects/llm-fleet/` with `Modelfiles/`, `tests/`, `fixtures/`, `scripts/` directories
- Create `scripts/create-all.sh` that builds all Modelfiles in sequence
- Create `scripts/test-all.sh` that runs all test scripts
- Create README.md with usage instructions

**LLM-2 through LLM-8: Individual Modelfiles**
Each task follows the same pattern:
1. Write the Modelfile (from spec in Section 4)
2. Create test fixtures (good inputs, bad inputs, edge cases)
3. Write test script that:
   - Creates the model (`ollama create`)
   - Runs it against each fixture
   - Validates output format (parseable JSON, expected fields)
   - Validates classification accuracy (known inputs → expected outputs)
   - Reports pass/fail

**LLM-9: Integration Testing**
- Run all test suites back-to-back
- Measure: tokens/sec per model, VRAM usage, cold-start latency
- Compare classification accuracy against API (same inputs to both, compare outputs)
- Document quality gaps (where local model gets it wrong vs API)
- Produce benchmark report

**LLM-10: Agent Integration**
- Modify heartbeat workflow to use heartbeat-monitor for initial classification
- Modify QA sweep to use qa-sweep for health check analysis
- Add escalation logic: if local model returns CRIT or low confidence → re-evaluate with API
- Measure actual token savings over 24-hour period

---

## 8. Risks

### R1: phi3:mini Capability Floor

**Risk:** phi3:mini (3.8B parameters) may not be capable enough for some tasks. Small models struggle with nuanced classification, complex JSON generation, and multi-step reasoning.

**Likelihood:** Medium-High. phi3:mini is impressive for its size but it's still a 3.8B model. Tasks like pattern evaluation and email triage involve judgment calls that may exceed its capability.

**Mitigation:** Every task is tested against fixtures with known-good outputs. If accuracy < 80% on test suite, upgrade to llama3.1-lexi. If lexi also fails, that task stays on API. We test before we commit.

**Fallback:** The fleet is designed for graceful degradation. Any Modelfile can be swapped from phi3:mini → lexi → API without changing the calling code. The interface is the same: text in, JSON out.

### R2: System Prompt Engineering

**Risk:** Getting Modelfile system prompts right takes iteration. First drafts will produce inconsistent, poorly formatted, or inaccurate output.

**Likelihood:** High. This is expected. Prompt engineering for small models is harder than for large models because you have less capability margin.

**Mitigation:** The Modelfile workflow is designed for fast iteration. Edit prompt → `ollama create` → test. Cycle time: <10 seconds. Budget 3-5 iterations per Modelfile to reach acceptable quality. Document what works and what doesn't in the Decision Log.

### R3: VRAM Contention

**Risk:** Multiple models loaded simultaneously could compete for VRAM, especially if AUGUR GPU workloads run concurrently.

**Likelihood:** Low for the fleet alone (phi3 + lexi = 10.7GB / 32GB). Medium if AUGUR discovery engine also uses the GPU.

**Mitigation:** Ollama auto-manages model loading/unloading. Models not recently used are evicted from VRAM. For explicit control: `OLLAMA_MAX_LOADED_MODELS=2` in environment. Monitor with `nvidia-smi`.

### R4: Quality Gap vs. API

**Risk:** Local model output is noticeably worse than API output for some tasks, leading to missed alerts or incorrect classifications.

**Likelihood:** Medium. Certain. The question is whether the gap matters for each specific task.

**Mitigation:** Define acceptable quality per task:
- Heartbeat monitor: must never miss a CRIT. False CRITs are acceptable (they escalate to API anyway).
- Log analyzer: must catch security events. May miss subtle anomalies (API catches those on escalation).
- Email triager: must catch P1. May misclassify P2 vs P3 (low stakes).

The design is **conservative classification with API escalation.** The local model's job is to filter the easy 95%. It doesn't need to be perfect — it needs to never miss the important stuff.

### R5: Ollama Stability

**Risk:** Ollama crashes, hangs, or produces degraded output under sustained load.

**Likelihood:** Low. Ollama is mature software. But we haven't stress-tested it with rapid sequential requests.

**Mitigation:** Systemd restart policy. Health check on Ollama itself (port 11434 responsive). If Ollama is down, fall through to API.

### R6: Model Staleness

**Risk:** phi3:mini and llama3.1-lexi get replaced by better models. Our Modelfiles are pinned to specific base models.

**Likelihood:** Certain. On a 3-6 month timeline, better small models will exist.

**Mitigation:** Modelfiles are trivially portable. Change `FROM phi3:mini` to `FROM <new-model>`, recreate. The system prompts and parameter tuning carry over. Budget a quarterly review of available models.

---

## 9. Definition of Done

### Must Have (MVP)

- [ ] All 7 Modelfiles created and registered in Ollama
- [ ] Each Modelfile has a test suite with ≥5 test fixtures
- [ ] Each Modelfile produces valid, parseable JSON output ≥90% of the time
- [ ] Each classifier achieves ≥80% accuracy on test fixtures
- [ ] heartbeat-monitor: 100% CRIT detection rate (zero missed CRITs)
- [ ] qa-sweep: integrated into at least one automated health check workflow
- [ ] heartbeat-monitor: integrated into heartbeat classification pipeline
- [ ] Benchmark report: tokens/sec, VRAM usage, cold-start latency for each model
- [ ] Quality comparison: local vs API output for identical inputs, documented gaps

### Should Have

- [ ] All 7 Modelfiles integrated into their respective agent workflows
- [ ] 24-hour measured token savings documented
- [ ] Automatic escalation logic: local → API when confidence is low
- [ ] `create-all.sh` and `test-all.sh` scripts for fleet management
- [ ] VRAM monitoring in health checks

### Nice to Have

- [ ] Grafana/LCARS dashboard panel showing local vs API inference split
- [ ] Automatic model upgrade testing (new base model → re-run test suite → compare)
- [ ] Response caching for repeated identical inputs
- [ ] Batch inference support (process N items in one call)

---

## 10. Decision Log

| Date | Decision | Rationale | Status |
|------|----------|-----------|--------|
| 2026-02-09 | Use Modelfiles over fine-tuning | Modelfiles are instant (seconds to create), zero training cost, and can be iterated in seconds. Fine-tuning requires datasets, GPU training time, and risks catastrophic forgetting. For our use case — constrained classification tasks with well-defined outputs — a good system prompt is sufficient. Fine-tuning is the escalation path if Modelfiles prove insufficient. | Active |
| 2026-02-09 | phi3:mini as default base model | Smallest viable model. Fast inference. Low VRAM. If it works for a task, there's no reason to use anything bigger. "Does the smallest model work?" is always the first question. | Active |
| 2026-02-09 | llama3.1-lexi for ansible-writer only | YAML generation requires more capability than classification. Lexi has 4× the parameters. The trade-off (slower inference, more VRAM) is justified only for tasks where phi3 demonstrably fails. | Active |
| 2026-02-09 | JSON output format for all Modelfiles | Parseable output is non-negotiable. Every Modelfile outputs JSON. This makes integration trivial — the calling code `JSON.parse()`s the output and acts on structured data. No regex parsing of natural language. | Active |
| 2026-02-09 | Temperature 0.0-0.3 range for all models | These are classification and generation tasks, not creative writing. Low temperature = consistent output. heartbeat-monitor at 0.0 (pure determinism), ansible-writer at 0.3 (needs some flexibility), everything else at 0.1-0.2. | Active |
| 2026-02-09 | Conservative classification + API escalation | The local model's job is to handle the easy 95%. It should err on the side of caution — a false CRIT that escalates to API is fine; a missed CRIT that doesn't escalate is not. The architecture is a funnel: local filters volume, API handles complexity. | Active |
| 2026-02-09 | Ollama over alternatives (llama.cpp, vLLM, text-generation-inference) | Ollama has Modelfile support built-in, simple CLI, systemd integration, and model management. It's the simplest path to "run a local model with a system prompt." If we need raw performance or more advanced serving features, vLLM is the upgrade path. | Active |

---

## Appendix A: Quick Reference

### Commands

```bash
# Create all fleet models
cd ~/Projects/llm-fleet && bash scripts/create-all.sh

# Test all fleet models
cd ~/Projects/llm-fleet && bash scripts/test-all.sh

# Create a single model
ollama create qa-sweep -f ~/Projects/llm-fleet/Modelfiles/Modelfile.qa-sweep

# Run a model
ollama run qa-sweep "$(cat input.json)"

# List registered models
ollama list

# Check VRAM usage
nvidia-smi

# Check Ollama status
curl -s http://localhost:11434/api/tags | jq .

# Remove a model
ollama rm qa-sweep
```

### Model Inventory

| Modelfile | Base | Temp | Context | Purpose |
|-----------|------|------|---------|---------|
| qa-sweep | phi3:mini | 0.1 | 4096 | Health check classification |
| log-analyzer | phi3:mini | 0.1 | 8192 | Log anomaly detection |
| heartbeat-monitor | phi3:mini | 0.0 | 4096 | Heartbeat escalation decision |
| pattern-evaluator | phi3:mini | 0.2 | 4096 | AUGUR pattern quality |
| ansible-writer | llama3.1-lexi | 0.3 | 8192 | Ansible playbook generation |
| discord-classifier | phi3:mini | 0.1 | 2048 | Message intent classification |
| email-triager | phi3:mini | 0.3 | 4096 | Email priority classification |

### Escalation Matrix

| Model | Escalates to API When |
|-------|----------------------|
| qa-sweep | status = CRIT |
| log-analyzer | severity = SECURITY or finding count > 5 |
| heartbeat-monitor | escalate = true |
| pattern-evaluator | Never (advisory only) |
| ansible-writer | Generated YAML fails lint |
| discord-classifier | confidence < 0.7 |
| email-triager | priority = P1_URGENT |

---

*This document is a living spec. Update it as Modelfiles are tested and iterated. The system prompts in Section 4 are v1 drafts — they will change. That's the point.*
