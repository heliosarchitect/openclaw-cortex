# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

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

❌ **Known Issue: Audio delivered as text, not audio**
- Tool returns `success: true` but media doesn't route properly
- Generated audio files arrive as text content instead of playable audio
- Tested 2026-02-04 21:20: Sent Elby voice message, arrived as text "just text messages"
- This appears to be a Signal integration issue with the message tool's media routing

**Workaround (when available):**
- Generate audio with XTTS ✅ works
- Upload file manually to Signal ✅ works
- Use message tool for text only ✅ works
- Don't rely on message tool for audio delivery ❌ broken

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
