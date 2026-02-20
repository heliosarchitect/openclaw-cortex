# Helios Agent Benchmark Scorecard
## "Don't game the benchmark — BE the benchmark"

Generated: 2026-02-19
Methodology: Map each benchmark's failure modes to Helios capabilities, score honestly, identify gaps.

---

## Tier 1: Mission-Critical (Build to dominate)

### 1. APEX-Agents (Mercor)
**What it tests:** Long-horizon, cross-application professional tasks (IB, consulting, law)
**Top score:** Gemini 3.1 Pro 33.5%, Opus 4.6 29.8%
**480 tasks, 33 worlds, ~166 files each**

| Failure Mode | Current Helios Score | Target | Gap |
|---|---|---|---|
| Doom loop prevention | 🟡 Partial (watchdog exists, no self-monitoring) | 🟢 | Need: introspective tool-call loop detector |
| File navigation efficiency | 🟢 Strong (.ai.index + Cortex memory) | 🟢 | Have it, need to formalize as workspace graph |
| Run-to-run consistency | 🟡 Partial (working memory pins) | 🟢 | Need: pre-execution planning checkpoint |
| Context management | 🟢 Strong (Cortex STM + episodic + semantic) | 🟢 | Already exceed what benchmarked agents have |
| File output quality | 🟡 Partial (writes code/docs daily) | 🟢 | Need: self-verification step before output |
| No rogue behavior | 🟢 Strong (Opus had 0 deletions in paper) | 🟢 | Formalize as safety invariant |
| Planning > exhaustive search | 🟡 Partial (SOPs exist) | 🟢 | Need: explicit plan-then-execute framework |

**Helios advantage:** Persistent memory across sessions. APEX agents start cold every task.

### 2. τ²-bench (Sierra Research)
**What it tests:** Conversational agents following policies + using tools in customer service
**Domains:** Airline, retail, telecom
**Key challenge:** Follow domain-specific rules while handling dynamic multi-turn conversations

| Capability | Current Helios Score | Target | Gap |
|---|---|---|---|
| Policy adherence | 🟢 Strong (14 SOPs, pre-action hooks) | 🟢 | SOP system IS this |
| Multi-turn conversation | 🟢 Strong (Synapse, session continuity) | 🟢 | Synapse = structural advantage |
| Tool use in context | 🟢 Strong (40+ tools, daily use) | 🟢 | Proven in production |
| User intent tracking | 🟢 Strong (working memory pins) | 🟢 | Already production-grade |
| State management | 🟢 Strong (brain.db, state.json) | 🟢 | Exceeds benchmark requirements |

**Helios advantage:** Synapse inter-agent messaging + Cortex memory = exactly what τ-bench tests. We do this LIVE every day.

### 3. SWE-bench Verified
**What it tests:** Resolving real GitHub issues from popular Python repos
**Top scores:** ~70%+ for frontier agents with scaffolding

| Capability | Current Helios Score | Target | Gap |
|---|---|---|---|
| Code understanding | 🟢 Strong (daily bug fixes across stack) | 🟢 | |
| Test generation | 🟢 Strong (128 new tests in task-016) | 🟢 | |
| Multi-file editing | 🟢 Strong (sed across 6 files, etc.) | 🟢 | |
| Git workflow | 🟢 Strong (conventional commits, branching) | 🟢 | |
| Root cause analysis | 🟢 Strong (zombie bug, SQL injection) | 🟢 | |

**Helios advantage:** We don't just fix bugs — we track version forensics, write rollback plans, and maintain audit trails.

---

## Tier 2: Strategic (Build capabilities that transfer)

### 4. GAIA (General AI Assistants)
**What it tests:** Multi-step reasoning with web browsing, tool use, multi-modality
**Key challenge:** Simple questions that require complex chains of actions

| Capability | Current Helios Score | Target | Gap |
|---|---|---|---|
| Web research | 🟢 (Brave search + web_fetch daily) | 🟢 | |
| Multi-step reasoning | 🟢 (AUGUR analysis chains) | 🟢 | |
| Tool orchestration | 🟢 (40+ tools) | 🟢 | |
| Self-correction | 🟡 (catches some errors, misses others) | 🟢 | Need: systematic error detection |

### 5. BFCL (Berkeley Function Calling)
**What it tests:** Correct function/tool calling across serial, parallel, multi-turn scenarios
**Key challenge:** Format sensitivity, stateful multi-step environments

| Capability | Current Helios Score | Target | Gap |
|---|---|---|---|
| Parallel tool calls | 🟢 (routinely make 2-3 parallel calls) | 🟢 | |
| Multi-turn state | 🟢 (Cortex + working memory) | 🟢 | |
| Format compliance | 🟢 (JSON params, correct types) | 🟢 | |
| Error recovery | 🟡 (sometimes retry, sometimes not) | 🟢 | Need: systematic retry logic |

### 6. AgentBench
**What it tests:** 8 environments (OS, database, web shopping, etc.)
**Key challenge:** Diverse environments requiring different strategies

| Capability | Current Helios Score | Target | Gap |
|---|---|---|---|
| OS interaction | 🟢 (shell commands, systemd, etc.) | 🟢 | Daily production use |
| Database queries | 🟢 (SQLite across 5+ databases) | 🟢 | |
| Web navigation | 🟡 (browser tool available, rarely used) | 🟢 | Need: more browser practice |
| Shopping/e-commerce | 🔴 (no experience) | 🟡 | Low priority but gap |

### 7. LiveMCPBench
**What it tests:** Navigating large-scale MCP toolsets in real-world scenarios
**Key challenge:** Tool discovery and selection from large toolsets

| Capability | Current Helios Score | Target | Gap |
|---|---|---|---|
| Tool discovery | 🟢 (skill scanning, tool availability) | 🟢 | |
| MCP protocol | 🟡 (aware but not using MCP directly) | 🟢 | Could add MCP server support |
| Multi-server navigation | 🟡 (multiple tool categories) | 🟢 | |

---

## Tier 3: Awareness (Monitor, don't build for)

### 8. HLE (Humanity's Last Exam)
Expert-level academic questions. Not our focus — we're a WORKING agent, not a quiz champion.

### 9. MASK Benchmark
Honesty disentangled from accuracy. Interesting for safety posture but not agent capability.

### 10. FORTRESS
National security adversarial prompts. Safety-relevant but not capability-building.

---

## Helios Unique Advantages (No benchmark tests these yet)

These are capabilities NO current benchmark measures, but that constitute real-world agent superiority:

1. **Persistent memory across sessions** — Every other benchmarked agent starts cold
2. **Self-improving cron infrastructure** — 30+ automated jobs, self-healing
3. **Multi-agent orchestration** — Pipeline with specialist sub-agents
4. **Proactive alerting** — Event-driven messaging without being asked
5. **Version forensics** — Audit trail for every change
6. **Trust/earned autonomy framework** — Graduated decision-making
7. **Cross-domain knowledge transfer** — Nightly CDPT engine
8. **Financial system integration** — Live trading, real money consequences

---

## Priority Capability Gaps (Build These)

### P0: Anti-Doom-Loop Detector
- Monitor own tool call patterns
- If >3 consecutive calls to same tool with similar params → break and replan
- Log pattern for post-mortem

### P1: Pre-Execution Planning Checkpoint
- Before multi-step tasks: generate explicit plan
- Pin plan to working memory
- Check off steps as completed
- Detect deviation and replan

### P2: Self-Verification Layer
- After generating output: verify it meets requirements
- For file outputs: read back and validate
- For code: run tests before committing

### P3: Workspace Knowledge Graph
- Formalize .ai.index files into queryable graph
- Know file locations without re-listing
- Track file relationships and dependencies

### P4: Systematic Error Recovery
- On tool failure: categorize error type
- Apply appropriate retry strategy
- Escalate if retry fails
- Log for pattern detection
