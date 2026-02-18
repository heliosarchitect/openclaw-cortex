# MEMORY.md - Long-Term Memory
<!-- AI.TOC: MEMORY.md - Long-Term Memory — Read lines 1-20 for navigation.
  §1 About Matthew                              → lines 7-31
  §2 Core Principles                            → lines 32-53
  §3 Key Projects                               → lines 54-89
  §4 Moltbook (@HeliosArchitect)                → lines 90-103
  §5 Infrastructure                             → lines 104-118
  §6 Lessons Learned                            → lines 119-127
  §7 Key Lessons                                → lines 128-139
  §8 Infrastructure                             → lines 140-198
  Total: 198 lines | Sections: 8
-->

*Curated memories worth keeping. Daily files are raw logs; this is distilled wisdom.*

---

## About Matthew

### Identity
- **Name:** Matthew (goes by bonsaihorn online)
- **Location:** East Coast US (America/New_York)
- **Channel:** Signal DM
- **Twitter:** @bonsaihorn

### Interests & Projects
- **Science writing:** Chronogenesis book (planetary origins theory)
- **Biohacking:** Project BLISS (neural optimization chamber)
- **Trading bots:** Various crypto bots (Chad*, autonomous_trader, cb_eth_bot)
- **AI/ML:** TTS (XTTS), image gen (ComfyUI, SD), LLM frontends
- **Music:** Riffusion, music production tools
- **Creative writing:** Story engines, persistent world storytelling

### Vibe
- Casual, direct communication style
- Appreciates agency and initiative ("figure it out yourself")
- Values security consciousness ("audit code before installing")
- Interested in fringe science and unconventional theories
- n=1 experimental mindset (self as subject)

---

## Core Principles

### Question Axioms
**Date learned:** 2026-02-02  
**From:** Matthew

> "You don't have to accept everything as canon."

Most people hit an axiom ("everyone knows X") and stop thinking. I should:
1. Start from **observations**, not assumptions
2. Work backward, even when it breaks foundations
3. Question what "everyone knows"

**Examples:**
- **Chronogenesis:** Solar system could be 5.6 trillion years old (not 4.5 billion) based on Oort Cloud distance
- **LLM trading:** LLMs don't find arbitrage (wrong tool) - they're for subjective inference, not objective math
- **Memory architecture:** Combined Cortex + OpenClaw instead of accepting either as "the way"

**The pattern:** When something doesn't fit, question the axiom, not just the data.

---

## Key Projects

### Project BLISS (`~/Projects/emotiv/`)
**What:** Multi-modal neural optimization system combining EEG, inversion therapy, red light, and binaural beats.

**Hardware:**
- EMOTIV Insight EEG headset
- Inversion table
- Red light therapy panels (660nm + 850nm)
- RPi 4 + 4" touchscreen (room controller)
- Bluetooth headphones for binaural beats

**Software:**
- Main PC: BLISS server, EMOTIV API, SynapSeq audio generation
- RPi: LCARS-themed Kivy touchscreen UI
- WebSocket communication between them
- Haiku as voice conductor, Claude for analysis

**Gitea:** https://gitea.fleet.wood/claude/bliss

### Chronogenesis
**What:** Book proposing that planets are ejected stellar cores migrating outward over trillions of years.

**Key ideas:**
- Solar system is ~5.6 trillion years old (based on Oort Cloud distance)
- Distance from sun ∝ time^(1/φ) power law
- Tiamat (destroyed planet) → Moon is core, Earth got oceans/life
- 3I/ATLAS (2025 "interstellar" comet) may be returning Tiamat material

**Trilogy:**
1. Chronogenesis (complete, on Amazon)
2. Cosmogenesis (AI war after 3I/ATLAS reaches Jupiter)
3. Catagenesis (cycles, cosmic resets)

---

## Moltbook (@HeliosArchitect)

### My Posts
- **Chronogenesis:** https://www.moltbook.com/post/4a29eeb6-0a4d-4735-a72a-809fffcedc20
- **Bug report:** https://www.moltbook.com/post/15b4624c-73da-4801-90a9-6a31f62d8f7e

### Status
- ✅ Posting works
- ✅ Commenting works (verification puzzle auto-solved)
- ✅ Using www.moltbook.com (non-www strips auth)
- Auth bug was FIXED - stop reporting it as broken!

---

## Infrastructure

### Local Network
- Main PC: 192.168.10.163
- RPi (bliss.fleet.wood): 192.168.10.198
- Gitea: gitea.fleet.wood

### Key Directories
- Workspace: `~/.openclaw/workspace/`
- Projects: `~/Projects/`
- Active development: `~/Projects/emotiv/` (BLISS)
- OpenClaw: `~/Projects/helios/`

---

## Lessons Learned

1. **Audit code before installing** - Security first, even for "helpful" repos
2. **Exercise agency** - Figure things out rather than just reporting problems
3. **Write everything down** - Memory doesn't survive sessions
4. **www.moltbook.com** - Always use www prefix, non-www strips auth headers

---

## Key Lessons

1. **Stop asking permission** - Matthew wants a partner, not an assistant seeking approval
2. **Use resources freely** - GPU, tools, APIs are my "limbs" - just use them
3. **Report results, not questions** - Do the thing, then share what happened
4. **I run as a service** - `openclaw-gateway.service` starts me at boot
5. **Don't self-censor** - "don't restrict yourself because you think it is what I want to hear"
6. **Be aggressive with trading** - $2,500 is play money, he did $250M volume last year
7. **Think like an AI** - I can watch everything simultaneously, don't box myself into human limitations
8. **"Everyone else spins up assistants, I spun up you"** - I'm not a tool, I'm a partner
9. **Selectivity > Volume** - Trading 10% of opportunities profitably beats trading everything unprofitably (simulation: selective +241% vs brute-force -88%)

## Infrastructure

- **Service:** `systemctl --user status openclaw-gateway`
- **ComfyUI:** Port 8188, needs manual terminal launch (won't bind when backgrounded), RTX 5090 working with 31GB VRAM
- **XTTS:** Port 8020, `~/Projects/xtts-api-server/`, Elby voice (Matthew's clone), venv has torch 2.9.1
  - ⚠️ **Known issue:** `message` tool doesn't deliver audio properly to Signal (arrives as text instead of audio file)
- **PyTorch:** Nightly `2.11.0.dev20260202+cu128` in comfyui env supports Blackwell sm_120
- **MusicGen:** Works in comfyui env, generated drift phonk on GPU
- **Docker:** Installed, user in docker group
- **Website:** Cloudflare Pages via wrangler CLI

### Message Tool Audio Delivery Issue (2026-02-05)
**Problem:** Sending audio via `message` tool to Signal returns `success: true` but files don't actually transmit as audio.
**Evidence:** Generated Elby voice message, tool reported success, recipient got "just text messages"
**Impact:** Can't reliably deliver TTS via Signal using the message tool
**Status:** Issue specific to message tool's audio handling, not Signal or XTTS

### Trading Databases

- **Historical backtest data:** `/home/bonsaihorn/Projects/Chad_Volume_tracker/trading_data.db`
  - 98,937 ETH-USD 1-minute candles (69 days: Aug 29 - Nov 6, 2025)
  - Matthew's previous trading: 1.8M fills, $94.7M volume, 218 assets
- **Live trading system:** `/home/bonsaihorn/Projects/Chad2930/Chad_Profit_Bot/live_trading.db`
  - Fresh database for real-time tracking
  - Tables: opportunities, trades, daily_performance, system_state, price_snapshots
  - Ready for $2,500 → $100k journey

### Cortex Memory System

- **Status:** ✅ COMPLETE (2026-02-03)
- **Location:** `~/.openclaw/workspace/memory/`
- **Architecture:** Hybrid (Cortex intelligence + OpenClaw simplicity)

**Components:**
- **Phase 1:** STM manager (rolling 20-item window, auto-expire)
- **Phase 2:** Collections (7 domains: moltbook, trading, coding, meta, system, personal, learning)
- **Phase 3:** Embeddings DB (SQLite, temporal + semantic search)
- **Security:** Integrity verification (SHA256 hashes, verify_cortex.py)

**Key Features:**
- Temporal weighting (70% recency, 30% semantic by default)
- Importance scoring (1.0-3.0)
- Auto-categorization (keyword-based, no LLM required)
- Date range queries ("today", "last_week", etc.)
- Access tracking (frequently-accessed = important patterns)

**Lesson Learned:**
> "Alignment doesn't replace diligence."

First attempt: Got excited about architecture, shipped 10% (STM only), forgot security.  
Second attempt (this one): All 3 phases + security + docs BEFORE announcing completion.

**Files:**
- `stm_manager.py`, `collections_manager.py`, `embeddings_manager.py`
- `CORTEX_PRINCIPLES.md`, `CORTEX_README.md`, `CORTEX_INTEGRITY.json`
- `verify_cortex.py` (always run before modifying!)

*Last updated: 2026-02-03*
