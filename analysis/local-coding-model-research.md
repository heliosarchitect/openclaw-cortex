# Local Coding Model Research: RTX 5090 Fleet Companion
<!-- AI.TOC: Local Coding Model Research: RTX 5090 Fleet Companion — Read lines 1-20 for navigation.
  §1 1. Candidate Comparison Table              → lines 10-31
  §2 2. Detailed Analysis                       → lines 32-88
  §3 3. Top Recommendation: Qwen2.5-Coder-7B-   → lines 89-111
  §4 4. Runner-Up: Qwen2.5-Coder-14B-Instruct   → lines 112-119
  §5 5. Suggested Modelfile Configurations      → lines 120-209
  §6 6. Installation Commands                   → lines 210-230
  §7 7. VRAM Budget Summary                     → lines 231-243
  §8 8. Fleet Architecture: One Generalist vs   → lines 244-356
  §9 9. Sources                                 → lines 357-368
  Total: 368 lines | Sections: 9
-->

**Date:** 2026-02-10
**Constraint:** Must fit alongside qwen2.5:32b (19GB) — max ~13GB VRAM
**Use Cases:** Linting, test generation, syntax validation, diff review, simple code review
**Languages:** Python, YAML, Bash/shell, JSON output

---

## 1. Candidate Comparison Table

| Model | Params | Active Params | Architecture | VRAM (Q4) | HumanEval (base) | HumanEval+ (instruct) | MBPP (base) | Ollama | Context | License |
|-------|--------|---------------|-------------|-----------|-------------------|----------------------|-------------|--------|---------|---------|
| **Qwen2.5-Coder-7B-Instruct** | 7.6B | 7.6B (dense) | Transformer | **~5.5GB** | 61.6 | **88.4** | 76.9 | ✅ `qwen2.5-coder:7b` | 128K | Apache 2.0 |
| **Qwen2.5-Coder-14B-Instruct** | 14.7B | 14.7B (dense) | Transformer | **~9.9GB** | 80.5 (base) | **~92+** | 91.0 (base) | ✅ `qwen2.5-coder:14b` | 128K | Apache 2.0 |
| DeepSeek-Coder-V2-Lite-Instruct | 16B | 2.4B (MoE) | MoE (64 experts, 6 active) | **~9-10GB** | 40.9 (base) | ~81.1 (Python) | 71.9 (base) | ✅ `deepseek-coder-v2:16b` | 128K | MIT-ish |
| CodeLlama-13B-Instruct | 13B | 13B (dense) | Llama2 | ~8GB | ~36 | ~53 | ~55 | ✅ `codellama:13b-instruct` | 16K | Llama 2 |
| CodeLlama-7B-Instruct | 7B | 7B (dense) | Llama2 | ~4.5GB | ~33.5 | ~34 | ~41 | ✅ `codellama:7b-instruct` | 16K | Llama 2 |
| StarCoder2-15B | 15B | 15B (dense) | Transformer | ~9.5GB | 46.3 | N/A (base only) | 66.2 | ✅ `starcoder2:15b` | 16K | BigCode OpenRAIL-M |
| StarCoder2-7B | 7B | 7B (dense) | Transformer | ~4.5GB | 35.4 | N/A (base only) | 54.4 | ✅ `starcoder2:7b` | 16K | BigCode OpenRAIL-M |
| Phi-4 | 14B | 14B (dense) | Transformer | **~9.7GB** | N/A | 82.6 | N/A | ✅ `phi4:14b` | 16K | MIT |
| Qwen3-Coder | 480B | 35B (MoE) | MoE | **~24GB+ (Q4)** | N/A | SWE-Bench SOTA | N/A | ✅ `qwen3-coder` | 256K | Apache 2.0 |

**Notes:**
- VRAM figures are for Q4_K_M quantization with ~4K context. Longer contexts add significant KV cache overhead.
- HumanEval+ scores use greedy decoding (pass@1). The "instruct" column uses chat-formatted evaluation where available.
- Qwen2.5-Coder-7B-Instruct scored **84.1% on HumanEval+** — the only sub-20B model to exceed 80% at time of release.
- Qwen2.5-Coder-14B base scored 80.5/91.0 on HumanEval/MBPP, surpassing StarCoder2-15B and CodeStral-22B.

---

## 2. Detailed Analysis

### Tier 1: Clear Winners

#### 🏆 Qwen2.5-Coder-7B-Instruct (RECOMMENDED)
- **VRAM:** ~5.5GB at Q4 — **leaves 7.5GB headroom** alongside qwen2.5:32b
- **Performance:** Best-in-class for 7B. HumanEval+ 84.1% surpasses models 3-5x its size
- **Speed (RTX 5090 estimate):** ~60-80 tok/s at Q4 (based on A100 benchmarks of ~43 tok/s at GPTQ-Int4, RTX 5090 is ~1.5-2x faster for small models due to higher clock speeds and GDDR7)
- **Context:** 128K native (YaRN extrapolation)
- **Languages:** 92 programming languages, strong Python/Bash/JS/YAML
- **FIM support:** Yes — fill-in-the-middle for code completion
- **License:** Apache 2.0 (fully permissive)
- **Why it wins:**
  - Fits easily with 32B base model (5.5 + 19 = ~24.5GB, well within 32GB)
  - Fast enough for interactive use (instant lint responses)
  - Code-specific training on 5.5T tokens
  - Instruction-tuned with multilingual sandbox verification
  - Deterministic output with low temperature works well

#### 🥈 Qwen2.5-Coder-14B-Instruct (RUNNER-UP)
- **VRAM:** ~9.9GB at Q4 — **tight but feasible** (9.9 + 19 = ~29GB, leaves ~3GB for KV cache)
- **Performance:** Significantly better than 7B. Base model HumanEval 80.5%, MBPP 91.0% beat models 2x its size
- **Speed (RTX 5090 estimate):** ~35-50 tok/s at Q4 (A100 does ~26 tok/s at GPTQ-Int4)
- **Context:** 128K native
- **Risk:** VRAM is tight. With both models loaded + KV cache for longer prompts, you could hit 32GB ceiling
- **Why it's runner-up:** Better quality but VRAM margin is thin. If qwen2.5:32b is unloaded during coding tasks, 14B is the clear choice.

### Tier 2: Viable Alternatives

#### DeepSeek-Coder-V2-Lite (16B, 2.4B active)
- **Pros:** MoE means only 2.4B params active → very fast inference, 128K context
- **Cons:** Despite being MoE, the full 16B weights still need VRAM (~9-10GB Q4). Actual coding benchmarks for the Lite version are significantly below Qwen2.5-Coder-7B (HumanEval+ ~64.6% for base lite vs Qwen's 84.1% instruct). The 90.2% HumanEval score widely cited is for the full 236B model, NOT the 16B Lite version.
- **Verdict:** Not worth it. Worse benchmarks than Qwen2.5-Coder-7B at similar or higher VRAM.

#### Phi-4 (14B)
- **Pros:** Strong general reasoning (82.6% HumanEval), MIT license, good at math
- **Cons:** Not code-specialized. No FIM support. Only 16K context. Not trained specifically on code data like Qwen2.5-Coder. Weaker at code-specific tasks (linting, diff review, shell scripts).
- **Verdict:** Good general model but loses to purpose-built Qwen2.5-Coder for our specific needs.

### Tier 3: Outdated / Not Competitive

#### CodeLlama (7B/13B)
- **Status:** Effectively obsolete for this use case. 53% HumanEval (best) vs 84%+ for modern models.
- Only 16K context. Released Aug 2023, rapidly surpassed.

#### StarCoder2 (7B/15B)
- **Status:** Decent base models but **no instruction-tuned variants** on Ollama. Base-only makes them unsuitable for interactive coding assistant tasks. 46.3% HumanEval (15B) is well below Qwen2.5-Coder-7B.

### Tier 4: Too Large

#### Qwen3-Coder (480B, 35B active)
- Released July 2025. Incredible performance (SWE-Bench SOTA, competitive with Claude Sonnet 4).
- Even at Q4, needs ~24GB+ VRAM. Cannot coexist with qwen2.5:32b.
- **Future option** if you dedicate the full GPU to it during coding sessions.

---

## 3. Top Recommendation: Qwen2.5-Coder-7B-Instruct

### Rationale

| Factor | Score | Notes |
|--------|-------|-------|
| VRAM Fit | ⭐⭐⭐⭐⭐ | 5.5GB at Q4, easily coexists with 32B base |
| Code Quality | ⭐⭐⭐⭐ | 84.1% HumanEval+, beats models 3-5x larger |
| Speed | ⭐⭐⭐⭐⭐ | 60-80 tok/s estimated on RTX 5090 |
| Python/Bash/YAML | ⭐⭐⭐⭐⭐ | 92 language support, code-specific training |
| JSON Output | ⭐⭐⭐⭐ | Instruction-tuned, follows format instructions well |
| Determinism | ⭐⭐⭐⭐⭐ | Works great at temp=0 with greedy decoding |
| Context Window | ⭐⭐⭐⭐⭐ | 128K (can review entire files/modules) |
| Ollama Support | ⭐⭐⭐⭐⭐ | First-class `qwen2.5-coder:7b` |
| License | ⭐⭐⭐⭐⭐ | Apache 2.0, no restrictions |

### When to Consider 14B Instead
- If you implement **model swapping** (unload 32B, load 14B for intensive coding sessions)
- If coding tasks are batch-oriented (not competing for VRAM with classification)
- If you need higher accuracy on complex code generation (not just linting/validation)

---

## 4. Runner-Up: Qwen2.5-Coder-14B-Instruct

Use this if you can afford the VRAM. It's substantially better at complex code tasks. The 14B model's base scores (HumanEval 80.5, MBPP 91.0) already exceed most instruct models in the 7B class. With instruction tuning, it approaches GPT-4-level coding performance.

**Deployment strategy:** Keep 7B loaded as default. Swap to 14B for complex tasks (full module rewrites, test suite generation for large codebases).

---

## 5. Suggested Modelfile Configurations

### Primary: Code Linter / Validator (`codex-lint`)
```modelfile
FROM qwen2.5-coder:7b

PARAMETER temperature 0
PARAMETER top_p 1
PARAMETER num_predict 2048
PARAMETER stop "<|endoftext|>"
PARAMETER stop "<|im_end|>"

SYSTEM """You are a code analysis assistant. Your job is to:
1. Identify syntax errors, bugs, and code smells
2. Suggest specific fixes with line numbers
3. Output structured JSON when asked
4. Be concise and precise — no unnecessary explanation

When reviewing code, focus on:
- Correctness (bugs, logic errors, off-by-one)
- Style (PEP 8 for Python, shellcheck-level for Bash)
- Security (injection, path traversal, hardcoded secrets)
- Performance (obvious N+1, unnecessary allocations)

Always respond with actionable feedback. If the code is clean, say so briefly."""
```

### Secondary: Test Generator (`codex-test`)
```modelfile
FROM qwen2.5-coder:7b

PARAMETER temperature 0.1
PARAMETER top_p 0.95
PARAMETER num_predict 4096
PARAMETER stop "<|endoftext|>"
PARAMETER stop "<|im_end|>"

SYSTEM """You are a test generation assistant. Given a function or module:
1. Generate comprehensive unit tests (pytest for Python, appropriate framework for other languages)
2. Cover edge cases, error paths, and boundary conditions
3. Use descriptive test names that explain the scenario
4. Include setup/teardown when needed
5. Output only the test code, no explanation unless asked

Prioritize:
- Happy path tests first
- Error/exception handling
- Boundary values
- Type edge cases (None, empty string, empty list)"""
```

### Tertiary: Diff Reviewer (`codex-review`)
```modelfile
FROM qwen2.5-coder:7b

PARAMETER temperature 0
PARAMETER top_p 1
PARAMETER num_predict 2048
PARAMETER stop "<|endoftext|>"
PARAMETER stop "<|im_end|>"

SYSTEM """You are a code review assistant analyzing diffs. For each diff:
1. Identify potential bugs introduced by the change
2. Check for style consistency
3. Flag any security implications
4. Note if tests should be added/updated
5. Rate severity: 🔴 critical / 🟡 warning / 🟢 nitpick

Format your review as a list of findings. Be direct and specific.
If the diff is clean, say "LGTM" with a brief note on what was checked."""
```

### JSON Output Mode (`codex-json`)
```modelfile
FROM qwen2.5-coder:7b

PARAMETER temperature 0
PARAMETER top_p 1
PARAMETER num_predict 4096
PARAMETER stop "<|endoftext|>"
PARAMETER stop "<|im_end|>"

SYSTEM """You are a structured output assistant. Always respond with valid JSON.
Never include markdown formatting, code fences, or explanatory text outside the JSON.
If you need to include code in JSON, properly escape it.
Follow any JSON schema provided in the prompt exactly."""
```

---

## 6. Installation Commands

```bash
# Pull the recommended model
ollama pull qwen2.5-coder:7b

# Create the Modelfiles
ollama create codex-lint -f /path/to/codex-lint.modelfile
ollama create codex-test -f /path/to/codex-test.modelfile
ollama create codex-review -f /path/to/codex-review.modelfile
ollama create codex-json -f /path/to/codex-json.modelfile

# Quick smoke test
echo 'def add(a, b): return a + b + 1' | ollama run codex-lint "Review this Python function for bugs:"

# Also pull 14B for swap-in when needed
ollama pull qwen2.5-coder:14b
```

---

## 7. VRAM Budget Summary

| Component | VRAM (Q4) | Notes |
|-----------|-----------|-------|
| qwen2.5:32b (base fleet) | ~19GB | 7 Modelfiles sharing weights |
| qwen2.5-coder:7b (coding) | ~5.5GB | 4 coding Modelfiles sharing weights |
| KV cache overhead | ~2-4GB | Depends on context length |
| **Total** | **~26.5-28.5GB** | **Within 32GB RTX 5090** ✅ |

If both models are loaded simultaneously with moderate context (~8K tokens each), you should stay comfortably within the 32GB VRAM budget.

---

## 8. Fleet Architecture: One Generalist vs. Multi-Model Specialists

### The Question

Instead of one large coding model, should we run 2-3 smaller specialized models?

| Role | Size Target | Temp | Context | Task |
|------|-------------|------|---------|------|
| `codex-lint` | ~3B | 0.0 | 2-4K | Syntax checking, bug finding, style enforcement |
| `codex-test` | ~7B | 0.3 | 8-16K | pytest generation, test fixtures |
| `codex-review` | ~7B | 0.1 | 16-32K | PR review, change impact analysis |

### Critical Insight: How Ollama Actually Handles This

**On disk:** Ollama deduplicates blob layers. Multiple Modelfiles sharing the same `FROM qwen2.5-coder:7b` store only one copy of the weights (~4.4GB on disk), plus tiny metadata for each Modelfile variant.

**In VRAM:** Ollama loads one model at a time by default (5-minute keep_alive). When you call `codex-lint`, then `codex-test`, then `codex-review` — if they all share the same base model (`FROM qwen2.5-coder:7b`), **Ollama recognizes this and reuses the loaded weights**. The system prompt/temperature differences are just parameter overrides, not separate model loads.

**This means:** Multiple Modelfiles from the same base = **zero additional VRAM cost**. The "fleet" is an illusion from the API consumer's perspective — Ollama is smart enough to keep one copy loaded.

Different base models (e.g., 3B + 7B) DO require separate VRAM allocations if loaded concurrently (`OLLAMA_NUM_PARALLEL` or overlapping requests with keep_alive).

### Comparison: Three Strategies

#### Strategy A: Single 14B Generalist
```
qwen2.5-coder:14b → codex-lint, codex-test, codex-review, codex-json
```
| Metric | Value |
|--------|-------|
| VRAM | ~9.9GB (one model) |
| VRAM with 32B base | ~29GB total (tight) |
| Quality | ⭐⭐⭐⭐⭐ Best-in-class for all tasks |
| Speed | ~35-50 tok/s on RTX 5090 |
| Swap latency | None — already loaded |
| Risk | VRAM pressure on long contexts |
| System prompt compensation | Not needed — model is strong enough |

#### Strategy B: Single 7B with Multiple Personas (RECOMMENDED)
```
qwen2.5-coder:7b → codex-lint, codex-test, codex-review, codex-json
```
| Metric | Value |
|--------|-------|
| VRAM | ~5.5GB (one model, all Modelfiles share it) |
| VRAM with 32B base | ~24.5GB total (comfortable) |
| Quality | ⭐⭐⭐⭐ Very strong, HumanEval+ 84.1% |
| Speed | ~60-80 tok/s on RTX 5090 |
| Swap latency | None — all Modelfiles use same base |
| Risk | Low — 7.5GB headroom for KV cache |
| System prompt compensation | Constrained system prompts focus the model effectively |

#### Strategy C: Mixed Fleet (3B lint + 7B complex)
```
qwen2.5-coder:3b → codex-lint (fast, cheap)
qwen2.5-coder:7b → codex-test, codex-review, codex-json
```
| Metric | Value |
|--------|-------|
| VRAM (if both loaded) | ~7.5GB (2GB + 5.5GB) |
| VRAM with 32B base | ~26.5GB total |
| Quality (lint) | ⭐⭐ Steep drop — 3B HumanEval ~45% vs 7B's 84% |
| Quality (complex) | ⭐⭐⭐⭐ Same as Strategy B |
| Speed (lint) | ~100-120 tok/s (faster but... is that useful?) |
| Swap latency | **~2-5 seconds** when switching between 3B/7B |
| Risk | Model swap lag during mixed workflows |
| System prompt compensation | 3B struggles even with perfect prompts |

### The Verdict: Strategy B Wins

**Strategy C (mixed fleet) is a trap.** Here's why:

1. **The 3B quality cliff is real.** Independent benchmarks show Qwen2.5-Coder-3B-Instruct at ~45% HumanEval vs 84% for 7B. That's not "slightly worse for simple tasks" — it means the 3B model will miss real bugs ~40% of the time. For a linter, false negatives are worse than being slow.

2. **System prompts can't compensate for missing knowledge.** A constrained system prompt helps a 7B model focus its existing capability. It can't inject knowledge that a 3B model never learned. Shell script edge cases, YAML indentation traps, Python type coercion bugs — the 3B model simply hasn't seen enough training data to catch these.

3. **The speed difference is irrelevant.** 60-80 tok/s (7B) vs 100-120 tok/s (3B) — for lint responses of ~100-200 tokens, that's 1.5-3 seconds vs 1-2 seconds. Nobody notices.

4. **Swap latency hurts more than speed gains.** If you call `codex-lint` (3B) then `codex-test` (7B), Ollama must unload/load different models. That's 2-5 seconds of dead time — more than the per-token speed advantage over the entire response.

5. **Ollama's same-base optimization makes fleet=single model.** Since all 7B Modelfiles share weights in VRAM, there's zero overhead from having 4 "different" models. You get specialization (via system prompts) for free.

**Strategy A (14B) is the power option** if you can spare the VRAM. Use it when the 32B classification model isn't needed concurrently — swap 32B out, 14B in for deep coding sessions.

**Strategy B (7B fleet) is the daily driver.** Rock-solid VRAM budget, fast inference, strong enough for every automated task we need. The 84% HumanEval+ score means it catches bugs that even 33B-parameter competitors miss.

### Recommended Architecture

```
┌─────────────────────────────────────────────────┐
│              RTX 5090 (32GB VRAM)                │
│                                                   │
│  ┌──────────────┐  ┌──────────────────────────┐  │
│  │ qwen2.5:32b  │  │  qwen2.5-coder:7b        │  │
│  │   ~19GB      │  │      ~5.5GB               │  │
│  │              │  │                            │  │
│  │  7 Modelfiles│  │  codex-lint  (temp=0)      │  │
│  │  (classify,  │  │  codex-test  (temp=0.1)    │  │
│  │   route,     │  │  codex-review (temp=0)     │  │
│  │   etc.)      │  │  codex-json  (temp=0)      │  │
│  └──────────────┘  └──────────────────────────┘  │
│                                                   │
│  Free: ~7.5GB (KV cache, OS, other processes)    │
│                                                   │
│  ┌──────────────────────────────────────────────┐│
│  │ SWAP-IN OPTION: qwen2.5-coder:14b (~9.9GB)  ││
│  │ Load when 32b is idle for complex code tasks ││
│  └──────────────────────────────────────────────┘│
└─────────────────────────────────────────────────┘
```

---

## 9. Sources

- Qwen2.5-Coder Technical Report: https://arxiv.org/abs/2409.12186
- Qwen2.5-Coder Family Blog: https://qwenlm.github.io/blog/qwen2.5-coder-family/
- Qwen2.5 Speed Benchmarks: https://qwen.readthedocs.io/en/v2.5/benchmark/speed_benchmark.html
- DeepSeek-Coder-V2 Paper: https://arxiv.org/abs/2406.11931
- StarCoder2 Paper: https://arxiv.org/abs/2402.19173
- Code Llama Paper: https://arxiv.org/abs/2308.12950
- Phi-4 Benchmarks: Microsoft Community Hub
- Ollama Model Library: https://ollama.com/library/
- EvalPlus Leaderboard: https://evalplus.github.io/leaderboard.html
