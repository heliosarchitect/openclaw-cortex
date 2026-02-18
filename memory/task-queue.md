# Task Queue — Helios Build Queue

When nothing's broken, BUILD. Pull from here, don't cycle HEARTBEAT_OK.

## In Progress (v0.3.0 Sprint — 2026-02-14)
- [🔄] WEMS v1.7.3 — Adding space weather + drought monitoring (nova-wems-features)
- [🔄] brain.py test suite expansion — delete_stm tests, edge cases (nova-brain-tests)

## Priority (do next)
- [ ] **AUGUR V4**: Investigate 0 paper trades — scanner producing signals (6314) but executor not trading
- [ ] **Ansible**: Complete fleet hardening audit (#6) — SSH keys done, Wazuh operational
- [ ] **n8n Integration**: Connect OpenClaw events to n8n workflows (event-driven architecture)
- [ ] **CHANGELOG Automation**: Generate from conventional commits (#7)

## Available (grab any)
- [ ] Audit remaining stm.json references in loadSTMDirect, CLI stats command
- [ ] Build Twilio integration (Matthew wanted call capability since psilocybin session)
- [ ] WEMS: Submit to awesome-mcp-servers list (PR pending review)
- [ ] Create OpenClaw skill for AUGUR trading management
- [ ] Explore ClawHub for useful skills to install
- [ ] LBF Operating Model — revenue projections, pricing strategy

## Completed (v0.3.0 Sprint)
- [x] **CRITICAL**: Fixed cortex_dedupe, cortex_update, cortex_edit, cortex_move (stm.json → brain.db)
- [x] **CRITICAL**: Fixed conversation-summarizer + self-reflection extensions (stm.json → brain.db)
- [x] Pruned 334 duplicate memories, cleaned api_filter_test pollution
- [x] GitHub release monitor — 9 repos, 4h polling
- [x] Memory hygiene cron — daily 4AM dedup+prune
- [x] Workspace cleanup — 50 files organized
- [x] Pattern audit — 5 failure modes documented
- [x] Cron output validator script
- [x] Cron hygiene — disabled duplicate job, removed Sonnet overrides
- [x] Vision document sync
- [x] 9 GitHub issues filed, 6 closed

## Completed (v0.2.0 and earlier) — archived
See CHANGELOG.md for full history.
