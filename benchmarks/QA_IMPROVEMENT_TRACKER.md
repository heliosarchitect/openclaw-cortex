# Helios QA Improvement Tracker
## Measuring real capability growth, not benchmark scores

Started: 2026-02-19
Method: Track concrete, observable metrics weekly. No self-grading — only things Matthew or tooling can verify.

---

## Core Metrics (Weekly)

### 1. Context Efficiency
| Week | Context Resets/Day | Auto-Compactions | Avg Session Length | Notes |
|---|---|---|---|---|
| Feb 10-16 | ~3-4/day (Matthew estimate) | ? | Short | Frequent topic loss, phantom references |
| Feb 17-23 | ~0-1/day | Active | Long | HEARTBEAT.md empty-by-design, compaction working |

**Target:** 0 forced resets/week. Compaction handles everything.
**How to measure:** Matthew's subjective count + gateway session logs.

### 2. Morning Email Reliability
| Week | Sent/Expected | On Time | Content Quality | Notes |
|---|---|---|---|---|
| Feb 10-16 | ?/5 | ? | ? | No tracking |
| Feb 17-23 | 2/3 (Mon-Wed) | 2/3 | ? | Feb 19 missed — Sonnet sub-agent SOP failure. Fixed: moved to main session. |

**Target:** 5/5 weekday delivery, actionable content.
**How to measure:** `gog gmail search "subject:Morning Plan" --after YYYY/MM/DD`

### 3. Bug Fix Velocity
| Week | Bugs Found | Bugs Fixed | Time-to-Fix (avg) | Self-Caught vs Matthew-Caught |
|---|---|---|---|---|
| Feb 17-23 | 7+ | 7+ | ~15min | Mix — zombie bug self-caught, morning email Matthew-caught |

**Target:** >80% self-caught. Fix within same session.
**How to measure:** Git log + cortex memory search.

### 4. Doom Loop Prevention (APEX P0)
| Week | Stuck Loops Detected | Self-Recovered | Required Intervention | Notes |
|---|---|---|---|---|
| Feb 17-23 | 1 (task-017 resurrection) | Yes (killed + blocklist) | 0 | Orchestrator kept reviving dead task 5x |

**Target:** 0 undetected loops. All self-recovered.
**How to measure:** Pipeline state.json + watchdog logs.

### 5. Compaction Accuracy
| Week | Phantom References | Verified Claims | Accuracy % | Notes |
|---|---|---|---|---|
| Feb 17-23 | 1 ("radio tasks 012-015") | Caught and documented | ~95% | Lesson stored in cortex |

**Target:** 0 phantom references acted on. Verify before asserting.
**How to measure:** Ground truth checks (git tag, filesystem, state.json).

### 6. Sub-Agent Success Rate
| Week | Spawned | Completed Successfully | Silent Failures | Notes |
|---|---|---|---|---|
| Feb 17-23 | ~15+ | ~12 | 3+ (morning email, daily report signal) | Sonnet agents hit SOP walls |

**Target:** >95% success rate. 0 silent failures.
**How to measure:** Cron run history + synapse inbox.

### 7. Proactive vs Reactive Ratio
| Week | Proactive Actions | Reactive (Matthew asked) | Ratio | Notes |
|---|---|---|---|---|
| Feb 17-23 | Many (event-watch, watchdog, model alerts) | Many (fix email, AUGUR bugs) | ~50/50 | Building toward proactive dominance |

**Target:** 70/30 proactive/reactive.
**How to measure:** Categorize each action in EOD reflection.

---

## Benchmark-Specific Tracking

### τ²-bench Readiness
- [ ] Install τ²-bench locally: `pip install -e .` from sierra-research/tau2-bench
- [ ] Run baseline eval on airline + retail + telecom domains
- [ ] Score and log results
- [ ] Identify specific policy-adherence gaps
- [ ] Build targeted improvements
- [ ] Re-eval and compare

### APEX-Agents Readiness
- [ ] Clone Archipelago infra from github.com/Mercor-Intelligence/archipelago
- [ ] Download dataset from huggingface.co/datasets/mercor/apex-agents
- [ ] Run subset eval (investment banking tasks first)
- [ ] Log failure modes by category
- [ ] Build targeted improvements
- [ ] Re-eval and compare

### SWE-bench Readiness
- [ ] Already strong — track via existing git metrics
- [ ] Add: time-to-resolution per bug
- [ ] Add: test coverage delta per fix

---

## Weekly Review Template

```
## Week of YYYY-MM-DD

### Metrics
- Context resets: X/day avg
- Morning emails: X/5 sent
- Bugs: X found, X fixed, X% self-caught
- Doom loops: X detected, X self-recovered
- Compaction accuracy: X%
- Sub-agent success: X%
- Proactive ratio: X%

### Benchmark Progress
- τ²-bench score: X% (prev: Y%)
- APEX subset score: X% (prev: Y%)
- New capabilities built: [list]

### Matthew Feedback
- [direct quotes or observations]

### Next Week Focus
- [top 3 priorities]
```
