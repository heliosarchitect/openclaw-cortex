# TOOLS.md - Local Notes

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
- ⚠️ Contacts - Needs People API scope

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

Add whatever helps you do your job. This is your cheat sheet.
