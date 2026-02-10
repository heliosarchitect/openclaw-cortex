# TOOLS.md - Quick Reference

Full details: `reference/TOOLS_FULL.md`

## Services
| Service | Port | Status |
|---------|------|--------|
| Google Workspace (`gog`) | — | OAuth, heliosarchitectlbf@gmail.com |
| XTTS (Elby voice) | 8020 | `~/Projects/xtts-api-server/` |
| Ollama (phi3:mini, lexi) | 11434 | systemd, RTX 5090 |
| AUGUR paper trader | — | `systemctl --user status paper-augur` |
| Enhanced collector | — | `systemctl --user status enhanced-collector` |
| LCARS dashboard | 8090 | `~/Projects/lbf-dashboard/` |
| BLISS server | 8765/8766 | `~/Projects/bliss/server/` |

## Network
- giggletits: 192.168.10.163 (main PC)
- bliss.fleet.wood: 192.168.10.198 (RPi)
- gitea.fleet.wood (local Git)

## Secrets
- Stripe: `~/.secrets/stripe.env` (LBF, live)
- Twilio: `~/.secrets/twilio.env` (SID: AC6cf7..., voice blocked pending Trust Hub)
- Signal media: `~/.openclaw/media/inbound/`

## Key Paths
- AUGUR: `~/Projects/augur-trading/`
- OpenClaw: `~/Projects/helios/`
- BLISS: `~/Projects/bliss/`
- Workspace: `~/.openclaw/workspace/`
- Data collector DB: `~/Projects/augur-collector/enhanced_data.db`
- Trade DB: `~/Projects/augur-trading/paper_results.db`
