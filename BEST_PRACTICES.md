# LBF Best Practices
<!-- AI.TOC: Read lines 1-20 for navigation. Each section has a line range.
  §1 Code Standards      → lines 22-55
  §2 Token Efficiency    → lines 57-105  (CRITICAL — context-injection-audit.md has full analysis)
  §3 Git & CI/CD         → lines 107-140
  §4 Documentation       → lines 142-175
  §5 Sub-Agent Dispatch  → lines 177-210
  §6 Memory & State      → lines 212-250
  §7 Testing             → lines 252-285
  §8 Security            → lines 287-315
  §9 Infrastructure      → lines 317-350
  §10 Sprint Process     → lines 352-385
  §11 Issue Tracking     → lines 330-380  (Gitea CLI, labels, repos, rules)
  AI.LIBRARY: AI_LIBRARY.md — master document index (152 docs)
  Full audit: analysis/context-injection-audit.md
-->

---

## §1 Code Standards

### File Structure
- Every repo: README.md, CHANGELOG.md, ARCHITECTURE.md
- TOC in first 20 lines of any doc >100 lines (AI-navigable)
- Python: type hints, docstrings on public functions
- Shell scripts: `set -euo pipefail`, `log()` helper

### Naming
- Scripts: `~/bin/<name>` (kebab-case, no extension)
- Python modules: `snake_case.py`
- Configs: `<service>.env` in `~/.secrets/`
- Databases: descriptive name, `.db` extension

### Error Handling
- Never silently swallow errors
- Log with timestamp: `[$(date '+%Y-%m-%d %H:%M:%S')]`
- Exit codes: 0=success, 1=error, 2=usage
- Fallback gracefully: if GPU unavailable, fall back to CPU/skip

### Dependencies
- Prefer stdlib over external packages
- Shell scripts: only `curl`, `jq`, `sqlite3`, standard coreutils
- Python: minimal pip installs, pin versions in requirements.txt
- No `node_modules` in workspace — use system-installed tools

---

## §2 Token Efficiency

### The Problem
Every LLM turn costs tokens. At Opus pricing ($15/M input), waste compounds fast.
Full audit: `analysis/context-injection-audit.md`

### Per-Turn Budget (current)
| Component | Tokens | Status |
|-----------|--------|--------|
| Core system prompt | ~2,000 | Fixed (OpenClaw) |
| Workspace files | ~3,500 | Trimmed (was 7,125) |
| Cortex memory | ~1,500-2,500 | Dynamic budget |
| Conversation history | Variable | Compaction manages |
| **Total overhead** | **~7,000-8,000** | Target: <6,000 |

### Rules
1. **Workspace files stay lean** — AGENTS.md, TOOLS.md, MEMORY.md are injected EVERY TURN. Keep them minimal. Details go in `reference/` or `memory/`.
2. **AI.TOC pattern** — Any file >100 lines gets a machine-readable TOC in lines 1-20. Agent reads TOC first, then reads only the section needed.
3. **Model routing** — Opus for Matthew conversations, Sonnet for heartbeats/sub-agents/cron. Complex sub-agents can override to Opus explicitly.
4. **Event-driven > polling** — Webhooks and cron jobs over heartbeat polling. Local models for screening, escalate to cloud only when needed.
5. **Cortex budget** — Base 1,500 tokens, max 2,500. Relevance threshold 0.5. Old memories truncated to 250 chars.
6. **Compaction awareness** — Workspace files are re-read during compaction too. Bloated files cost double.
7. **Sub-agent files** — Sub-agents only get AGENTS.md + TOOLS.md. Keep these especially lean.

### Implementation Status
| Optimization | Status | Savings |
|---|---|---|
| AGENTS.md trimmed 7.8K→1K | ✅ Done | ~1,000 tok/turn |
| TOOLS.md trimmed 6.7K→1.2K | ✅ Done | ~800 tok/turn |
| MEMORY.md trimmed 7.8K→1.2K | ✅ Done | ~1,400 tok/turn |
| Model routing (Sonnet for HB/sub) | ✅ Done | ~50-60% cost reduction |
| H0-4 hash caching (skip unchanged) | ✅ Built | ~5,200 tok/turn (pending deploy) |
| Event-driven architecture | 🔄 Planning | ~90% heartbeat reduction |
| Local model screening | 🔄 Planning | Near-zero for routine checks |

### Anti-Patterns
- ❌ Putting reference material in workspace .md files (injected every turn)
- ❌ Long narrative daily logs in injected files
- ❌ Heartbeat polling for things that have webhooks
- ❌ Using Opus for cron/heartbeat/routine sub-agents
- ❌ Storing raw events when consolidated insights exist

---

## §3 Git & CI/CD

### Commit Messages
- Descriptive first line (50 chars), blank line, body if needed
- Use local `codex-review` model for pre-commit review when available
- Reference issue/task numbers when applicable

### Branching
- `main` is always deployable
- Feature branches: `feature/<name>` or `<descriptive-name>`
- Push to Gitea (gitea.fleet.wood) — it's the canonical remote

### CI/CD
- All repos with tests get `.gitea/workflows/test.yaml`
- Native host runner on hpserver1 (not Docker — networking issues)
- Use `actions/checkout@v3` (Node 12 compatible)
- Bootstrap pip via `get-pip.py` if needed
- Run tests locally first (`pytest -v --tb=short`)
- If CI fails: fix immediately, don't leave red builds
- Gitea token: `~/.secrets/gitea-helios-token.txt`

### Pre-Commit Checklist
- [ ] Tests pass locally
- [ ] No secrets in code (use `~/.secrets/`)
- [ ] CHANGELOG.md updated for user-facing changes
- [ ] `codex-review` run if available

---

## §4 Documentation

### AI.TOC Pattern
Every document >100 lines MUST have an AI-navigable TOC in lines 1-20:
```markdown
<!-- AI.TOC: Read lines 1-20 for navigation.
  §1 Section Name → lines X-Y
  §2 Section Name → lines X-Y
  ...
-->
```
This lets agents read 20 lines to decide which section to load, instead of reading the entire file every time.

### Required Docs Per Repo
| File | Purpose |
|------|---------|
| README.md | What it does, quickstart, architecture overview |
| CHANGELOG.md | Version history, what changed |
| ARCHITECTURE.md | System design, data flow, key decisions |

### Writing Style
- Be concise. Tables > paragraphs for structured data.
- Code examples > descriptions of code.
- Keep docs current — stale docs are worse than no docs.
- Reference paths are absolute from home (`~/Projects/...`)

---

## §5 Sub-Agent Dispatch (Nova Pattern)

### Standing Schedule
- 60 seconds per spawn, 2 hours total Nova budget per session
- Pull tasks from `memory/task-queue.md`
- Dispatch in parallel where tasks are independent

### Model Selection
- Routine builds/scripts: Sonnet (default, automatic)
- Complex architecture/multi-file changes: Opus (pass `model="anthropic/claude-opus-4-6"`)
- Never use Opus for simple file generation or data queries

### Task Specification
- Self-contained task description (agent has no prior context)
- Include: file paths, expected deliverables, test requirements
- Include: `"Store results in cortex"` for important discoveries
- Set timeout: 60s default, 300s for complex builds, 600s for mining

### Results Policy
- Sub-agent announces go to NO_REPLY (never auto-forward to Matthew)
- Check results during heartbeats or when contextually relevant
- Share findings naturally in conversation when they matter

### Anti-Patterns
- ❌ Spawning Opus sub-agents for simple tasks
- ❌ Not setting timeouts (infinite spin)
- ❌ Forgetting to include file paths in task description
- ❌ Auto-announcing results to Matthew via Signal

---

## §6 Memory & State

### Hierarchy
1. **Cortex STM + embeddings** — primary memory (search here first)
2. **brain.db** — unified store (STM, messages, atoms, embeddings, WM, categories)
3. **Daily logs** — `memory/YYYY-MM-DD.md` (raw session records)
4. **MEMORY.md** — thin bootstrap index only (points to cortex, not a knowledge store)
5. **Working memory pins** — max 10, always in context, for critical ongoing items

### Rules
- Write it down. Mental notes don't survive restarts.
- Cortex importance: 1.0=routine, 2.0=notable, 3.0=critical
- Dedup regularly (cortex_dedupe or direct SQL if tool is broken)
- Consolidate related memories into higher-level insights
- Daily log gets updated throughout the day, not just at end

### Pre-Reset Sweep (MANDATORY)
Before any context reset or when context >80%:
1. Update `memory/YYYY-MM-DD.md` with everything accomplished
2. Store unrecorded insights via `cortex_add`
3. Update MEMORY.md only if project list changes
4. Verify working memory pins are in persistent storage
5. Note in-progress work so next session can pick up

### brain.db Location
- Canonical: `~/.openclaw/workspace/memory/brain.db`
- API: `localhost:8031` (brain_api.py)
- CLI: `~/bin/brain`
- Backups: `~/bin/brain-backup-cron` (6hr cycle → hpserver1 + Google Drive)

---

## §7 Testing

### Standards
- All new code gets tests
- Python: pytest (`pytest -v --tb=short`)
- Shell: inline validation or separate test script
- Minimum: happy path + one error case + edge case

### Test Before Commit
```bash
# Python
cd /path/to/project && pytest -v --tb=short

# Shell scripts
bash -n script.sh  # syntax check
./script.sh --help  # basic invocation
```

### CI Integration
- Tests run on push via Gitea Actions
- Green build required before considering task "done"
- Flaky tests get `continue-on-error` + investigation ticket
- SQLite tests: always set `PRAGMA busy_timeout=5000`

---

## §8 Security

### Secrets
- Never in code, config files, or git history
- Store in `~/.secrets/<name>.env`
- Load via `source ~/.secrets/<name>.env` or env vars
- Gitea tokens, API keys, passwords — all in `~/.secrets/`

### File Operations
- `trash` > `rm` (archive before delete)
- Ask before external actions (emails, tweets, public posts)
- Internal actions (read, organize, search) are free

### SSH
- Fleet servers use port 2222 (not 22)
- NOPASSWD sudo on all fleet servers (bonsaihorn user)
- Key-based auth preferred

### Wazuh
- Manager: blackview (192.168.10.143)
- 5 agents connected
- Creds: `~/.secrets/wazuh.env`
- Dashboard: `https://192.168.10.143`

---

## §9 Infrastructure

### Fleet Servers
| Host | IP | Port | Role |
|------|-----|------|------|
| giggletits | 192.168.10.163 | 22 | Main PC, GPU (RTX 5090) |
| hpserver1 | 192.168.10.104 | 2222 | Gitea, Prometheus, CI runner, n8n |
| woodserve1 | 192.168.10.107 | 2222 | Pi-hole, backups |
| blackview | 192.168.10.143 | 2222 | Wazuh manager |
| bliss | 192.168.10.198 | — | RPi (BLISS project) |

### Services (giggletits)
- Ollama: port 11434 (20 models, RTX 5090)
- LCARS Dashboard: port 8090
- brain API: port 8031
- Embeddings daemon: port 8030
- OpenClaw gateway: port 18789

### Docker (hpserver1)
- Gitea + postgres: port 3000
- n8n: port 5678
- act_runner: native binary (not Docker)
- Prometheus: port 9090

### Ansible
- Playbooks: `~/Projects/ansible/`
- Inventory: all 4 fleet servers
- Use for any fleet-wide changes

---

## §10 Sprint Process

### Task Sources
1. `memory/task-queue.md` — active backlog
2. LBF Task Board — `lbf` tool (programs → projects → tasks)
3. Matthew's direct requests — highest priority
4. Self-identified improvements — HELIOS_VISION.md phases

### Sprint Execution
1. Pull top tasks from queue
2. Dispatch to Nova (sub-agents) where possible
3. Verify results (tests green, artifacts exist)
4. Update daily log + cortex
5. Commit + push to Gitea
6. Move task to "done" in queue/board

### Definition of Done
- [ ] Code works (tests pass)
- [ ] Committed to Gitea with descriptive message
- [ ] CHANGELOG updated (if applicable)
- [ ] Daily log updated
- [ ] Cortex memory stored (if notable insight)
- [ ] CI green (if repo has CI)

### Anti-Patterns
- ❌ Working without updating daily log
- ❌ Leaving red CI builds
- ❌ Completing tasks without cortex storage
- ❌ Not checking Nova results before marking done
- ❌ Skipping tests "because it's simple"
- ❌ Fixing bugs without filing a Gitea issue first

---

## §11 Issue Tracking (Gitea)

All bugs, features, and research items are tracked in Gitea (https://gitea.fleet.wood).

### CLI Tool
```bash
~/bin/gitea-issue create <owner/repo> <title> [-b body] [-l labels]
~/bin/gitea-issue list <owner/repo> [--state open|closed]
~/bin/gitea-issue close <owner/repo> <number> [-c comment]
~/bin/gitea-issue comment <owner/repo> <number> <body>
~/bin/gitea-issue labels <owner/repo>
```

### Standard Labels (all repos)
| Label | Color | Meaning |
|-------|-------|---------|
| `P0` | 🔴 red | Critical — fix now |
| `P1` | 🟠 orange | High — fix this sprint |
| `P2` | 🟡 yellow | Medium — scheduled |
| `bug` | 🔴 red | Something broken |
| `feature` | 🔵 blue | New functionality |
| `research` | 🟣 purple | Investigation needed |
| `ops` | 🟤 peach | Infrastructure/operations |

### Key Repos
- `Helios/augur-trading` — Trading engine, signals, live/paper
- `Helios/brain-db` — Unified memory (SYNAPSE + Cortex)
- `Helios/cortex` — Memory system, self-improvement
- `Helios/llm-fleet` — Local LLM models and routing
- `loverbearfarm/fleetwood-core` — Infrastructure stack

### Rules
1. **File before fix** — Every bug gets an issue BEFORE you start fixing
2. **Close with evidence** — Issues closed with a comment showing the fix/result
3. **Mine memory** — Periodically scan Cortex STM for unfiled issues
4. **Link issues** — Reference related issues in descriptions ("Refs: #1")
5. **Definition of Done** includes issue closed in Gitea
