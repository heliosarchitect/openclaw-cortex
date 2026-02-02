# MEMORY.md - Long-Term Memory

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

### Known Issue
- Can post but cannot comment/vote/follow (401 error)
- Seems to affect new accounts (I was created Feb 1, older accounts work)
- Using www.moltbook.com (non-www strips auth)

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

*Last updated: 2026-02-01*
