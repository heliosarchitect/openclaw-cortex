# Ham Radio Session — 2026-02-16 Evening

## Timeline
- **21:00** — Ubuntu Server installing on HP ProDesk 600 G1
- **21:10** — SSH hardened (port 2222, key auth, NOPASSWD sudo)
- **21:15** — FT-991A serial confirmed: FA007490000; (7.490 MHz, 40m band)
- **21:20** — 6 sub-agents dispatched: CW, scanner, broadcast, digital, APRS, OpenClaw skill
- **21:25** — Web GUI discovered live at :8000, LCARS theme requested
- **21:27** — Traefik HTTPS and LCARS theme agents launched
- **21:30** — Fine tuning confirmed (100 Hz resolution), CW demo (KO4TUV)
- **21:33** — LCARS theme deployed, Pi-hole DNS entry added
- **21:36** — Tab batches 1 & 2 dispatched (all 10 tabs)
- **21:40** — Setup wizard agent launched
- **21:45** — Batch 1 deployed (VFO, Mode, Band, TX, Meters)
- **21:51** — Matthew: "dockable is premium" — monetization idea
- **21:54** — Batch 2 deployed (Audio, System, Diagnostics, Config, Status)
- **21:58** — Waterfall display agent launched
- **22:00** — Pi-hole DNS fixed (needed /etc/hosts, not custom.list)
- **22:04** — Waterfall deployed
- **22:10** — Mobile nav fix (sidebar hidden on mobile, added horizontal tab bar)
- **22:13** — Mobile nav deployed

## Key Decisions
- **LCARS theme** — reuse CSS from lbf-dashboard
- **Tabs over dockable windows** — dockable = premium feature
- **Pi-hole DNS** — v6 reads /etc/hosts, not custom.list or dnsmasq host-records
- **Audio waterfall** — PCM2903B → arecord → WebSocket → Web Audio API FFT → canvas
- **No TX without Matthew** — hard rule, all TX controls have safety confirmations

## Sub-Agents Shipped (13)
1. band-scanner — BandScanner class, CLI scan commands
2. cw-module — Morse encode/decode/keyer, v0.6.0
3. broadcast-module — TTS to radio pipeline
4. digital-modes — FT8/FT4/JS8Call setup
5. aprs-module — APRS encode/decode, emergency freqs
6. openclaw-skill — ham-radio skill for Helios
7. lcars-theme-v2 — Star Trek LCARS CSS/HTML redesign
8. traefik-route — HTTPS route on hpserver1
9. gui-tabs-batch1 — VFO, Mode, Band, TX, Meters
10. gui-tabs-batch2 — Audio, System, Diagnostics, Config, Status
11. setup-wizard — 6-step first-run configuration wizard
12. waterfall-display — Audio FFT waterfall with canvas rendering
13. mobile-nav-fix — Horizontal scrollable mobile tab bar

## Architecture
```
Phone/Browser → Pi-hole DNS → radio.fleet.wood
  → Traefik (.104, HTTPS) → radio server (.179:8000)
    → FastAPI + WebSocket (ft991a-web)
      → FT991A class → serial (/dev/ttyUSB0, 38400 baud)
      → PCM2903B CODEC → audio WebSocket → browser FFT waterfall
```

## Files Modified
- `src/ft991a/static/index.html` — LCARS GUI (multiple iterations)
- `src/ft991a/web.py` — FastAPI backend, setup wizard endpoints, audio streaming
- `src/ft991a/cw.py` — CW module
- `src/ft991a/scanner.py` — Band scanner
- `src/ft991a/broadcast.py` — TTS broadcast
- `src/ft991a/digital.py` — Digital modes
- `src/ft991a/aprs.py` — APRS module

## Next Steps
- [ ] Fix PyPI publishing (twine metadata issue)
- [ ] Test audio waterfall with real PCM2903B capture
- [ ] Add systemd service for ft991a-web
- [ ] Memory channel API endpoints (backend)
- [ ] Dockable window manager (premium feature)
- [ ] Version bump and tag release
