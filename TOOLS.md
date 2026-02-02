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

**Note:** NVIDIA driver currently mismatched (580.126). May need fixing before XTTS works.

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
