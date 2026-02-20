# Session State — AI Register
UPDATED: 2026-02-17T12:16-05
## Projects
PRJ: ft991a-control v0.8.1 @ radio.fleet.wood (.179)
  REPO: ~/Projects/lbf-ham-radio | github+gitea synced
  DEPLOY: pip site-packages, scp+restart | Traefik → :8000
  CI: GitHub Actions → PyPI on v* tag
PRJ: Helios v1.0.0 @ giggletits (.163)
PRJ: AUGUR v4.5.0 @ hpserver1 (.104)
  RESET: weekly done 2026-02-17
PRJ: desk-bot v1.0.1 printing PETG @ OctoPrint (.141)
  CRON: c0162d35 every 15min

## Services
SVC: ft991a-web :8000 on .179 (behind Traefik)
SVC: radio-monitor PID 352795 14.270MHz 2min clips
SVC: discord-bot = OpenClaw plugin (NOT standalone)
SVC: n8n on hpserver1 (.104)

## Today 2026-02-17
CHG: v0.6.0→v0.6.1→v0.7.0→v0.7.1→v0.7.2→v0.8.1 (radio)
CHG: AUGUR weekly reset+backup
CHG: QA sweep blip fixes (retries+backoff)
CHG: radio monitoring 14.270 (Spanish speakers, no callsigns)
CHG: diagnosed reduced capability → compaction losing state
CHG: cleaned WM 3 stale pins, merged 50 dupe memories
CHG: created SESSION_STATE.md (this file)
