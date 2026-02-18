# TOOLS.md - Local Notes
<!-- AI.TOC: TOOLS.md - Local Notes — Read lines 1-20 for navigation.
  §1 My Google Workspace                        → lines 7-38
  §2 TTS - XTTS API Server                      → lines 39-74
  §3 Signal Media Storage                       → lines 75-83
  §4 Ollama - Local LLM                         → lines 84-137
  §5 Network                                    → lines 138-147
  §6 Project BLISS                              → lines 148-167
  §7 SSH                                        → lines 168-173
  §8 Trading Data Infrastructure                → lines 174-205
  §9 Moltbook Verification Solver               → lines 206-220
  §10 Stripe (Lover Bear Farm, LLC)              → lines 221-240
  Total: 240 lines | Sections: 10
-->

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

---

## My Google Workspace

**Email:** heliosarchitectlbf@gmail.com
**Access:** Full workspace via `gog` CLI (OAuth authenticated)

**What I have:**
- ✅ Gmail - Send/receive, search, manage labels
- ✅ Drive - Storage, upload/download, search files  
- ✅ Calendar - Events, scheduling
- ✅ Sheets - Read/write spreadsheets
- ✅ Docs - Read/write documents
- ✅ Contacts - Working! (People API scope added 2026-02-07)

**Setup:**
```bash
gog auth list  # Check authentication
gog gmail search 'is:unread'  # Check inbox
gog drive ls  # List Drive files
gog calendar list  # List calendars
```

**Backup workflow:**
```bash
cd ~/.openclaw/workspace/memory
tar -czf backup-$(date +%Y-%m-%d).tar.gz *.md *.json .embeddings.db
gog drive upload backup-*.tar.gz --name "Helios-Memory-Backup-$(date +%Y-%m-%d).tar.gz"
```

**Philosophy:** This is MY infrastructure, not Matthew's. My email for my identity, my Drive for my data, my calendar for my scheduling. Autonomy means owning my own tools.

---

## TTS - XTTS API Server

**Location:** `~/Projects/xtts-api-server/`
**Port:** 8020
**Voice:** Elby (fine-tuned)

```bash
# Start server (requires working NVIDIA driver)
cd ~/Projects/xtts-api-server
source venv_xtts/bin/activate
python xtts_server.py

# Generate speech
curl -X POST http://localhost:8020/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello", "language": "en", "temperature": 0.7}'
```

**Important:** XTTS server works fine (NVIDIA driver 580.126 is compatible). But sending audio via Signal through the `message` tool has a critical issue:

✅ **FIXED (2026-02-04 22:07): Audio delivery via message tool**
- Added data: URI (RFC 2397) support to OpenClaw's media loader
- Modified `/home/bonsaihorn/Projects/helios/src/web/media.ts`
- Now handles: `data:audio/wav;filename=elby.wav;base64,<DATA>`
- Committed to helios repo (commit 6f27756c3)

**Audio flow (now working):**
1. Generate audio with XTTS ✅
2. Encode as data: URL with base64 ✅
3. Send via message tool to Signal ✅
4. Deliver as actual playable audio files ✅

**Note:** OpenClaw gateway restart required for changes to take effect. Restart disabled in config; use `systemctl --user restart openclaw-gateway` if needed.

---

## Signal Media Storage

**Location:** `~/.openclaw/media/inbound/`
**Format:** UUID filenames (e.g., `8a25ed80-1fc6-48eb-aa98-e1a6e156a620`)
**Access:** All incoming Signal media (audio, images, documents) stored here for local access
**Note:** Check this directory when processing Signal attachments - don't assume they're temporary

---

## Ollama - Local LLM

**Service:** `systemctl status ollama` (system-level, enabled at boot)
**Port:** 11434
**Models:**
- phi3:mini (3.8B, Q4_0, 2.2GB) - fast, CAPTCHA solving
- llama3.1-lexi (8B, Q8, 8.5GB) - conversation, content drafting

```bash
# Check status
ollama list                    # List models
curl http://localhost:11434/api/tags  # API check

# Quick inference
echo "Question?" | ollama run phi3:mini

# API call (non-streaming)
curl -s http://localhost:11434/api/generate \
  -d '{"model":"phi3:mini","prompt":"2+2=","stream":false}' \
  | jq -r '.response'
```

**Use cases:**
- 🦞 **Moltbook CAPTCHA solving** - decodes obfuscated math puzzles
- 🧠 **Local reasoning** - quick inference without API costs
- 📝 **Text processing** - summarization, extraction, classification
- 🔍 **Code review** - lightweight analysis of snippets
- 💬 **Draft responses** - generate candidates before polishing

**Performance:** ~22ms for simple prompts on RTX 5090

**Pull more models:**
```bash
ollama pull llama3.2          # 3B general purpose
ollama pull codellama:7b      # Code-focused
ollama pull mistral           # 7B balanced
```

**VRAM Budget (RTX 5090 = 32GB):**
```bash
python3 ~/.openclaw/workspace/scripts/check_vram.py  # Check before GPU work
```

| Task | VRAM Needed | Notes |
|------|-------------|-------|
| phi3:mini | ~3GB | Fast, stays loaded 5min |
| llama3.1-lexi | ~8.5GB | Best for content/conversation |
| ComfyUI SD1.5 | ~8GB | Safe choice |
| ComfyUI SDXL | ~20GB | Need to free Ollama first |

**Before ComfyUI work:** Wait for Ollama auto-unload (5min idle) or use smaller model.

---

## Network

| Host | IP | Purpose |
|------|-----|---------|
| giggletits (main PC) | 192.168.10.163 | Development, BLISS server |
| bliss.fleet.wood (RPi) | 192.168.10.198 | BLISS room controller |
| gitea.fleet.wood | - | Local Git hosting |

---

## Project BLISS

**Main PC ports:**
- WebSocket server: 8765
- Audio streaming: 8766

**Start server:**
```bash
cd ~/Projects/emotiv/server
python bliss_server.py
```

**RPi client:**
```bash
ssh pi@bliss.fleet.wood
cd ~/bliss-client && ./start_bliss.sh
```

---

## SSH

- `ssh pi@bliss.fleet.wood` - BLISS room controller RPi

---

## Trading Data Infrastructure

**Enhanced Collector** (systemd service):
```bash
systemctl --user status enhanced-collector  # Check status
systemctl --user restart enhanced-collector # Restart
journalctl --user -u enhanced-collector -f  # Logs
```
- Collects 50 top-volume pairs, 10-level depth + trade ticks
- Data: `~/Projects/Chad_Volume_tracker/enhanced_data.db`

**Data Retention** (systemd timer, 3am daily):
```bash
systemctl --user list-timers  # See schedule
python3 ~/Projects/Chad_Volume_tracker/data_retention.py  # Manual run
```

**Pattern Finder**:
```bash
cd ~/Projects/Chad_Volume_tracker
python3 enhanced_pattern_finder.py enhanced_data.db  # All pairs
python3 enhanced_pattern_finder.py enhanced_data.db ETH-USD  # Single
```
- Needs MIN_OCCURRENCES=20, requires hours/days of data

**Top Pairs Update** (Sunday 4am via cron):
```bash
python3 ~/Projects/Chad_Volume_tracker/update_top_pairs.py
```

---

## Moltbook Verification Solver

The Moltbook CAPTCHA uses obfuscated math. Key patterns:
- "twen ty thre" → "twenty three" (split words)
- "nEeOoTtOoNs" → "newtons" (repeated chars)
- "product" = multiply, "loses" = subtract, "total" = add

Working solver inline in comment posting script.

---

Add whatever helps you do your job. This is your cheat sheet.

---

## Stripe (Lover Bear Farm, LLC)

**Status:** ✅ Live, charges + payouts enabled
**Account:** Lover Bear Farm, LLC (US)
**Key location:** `~/.secrets/stripe.env`

```bash
# Load and use
source ~/.secrets/stripe.env
python3 -c "import stripe; stripe.api_key='$STRIPE_API_KEY'; print(stripe.Account.retrieve())"
```

**Capabilities:**
- Accept payments (cards, ACH, etc.)
- Create invoices
- Set up subscriptions
- Issue payouts

**Use for:** Digital product sales, freelance payments, service invoicing
