# Task Queue — Helios Build Queue

BUILD mode now triggered by n8n event injection, not heartbeat polling.
HEARTBEAT.md is comments-only → isHeartbeatContentEffectivelyEmpty() skips LLM calls.

## In Progress (v0.3.0 Sprint — 2026-02-14)
- [🔄] WEMS v1.7.3 — Adding space weather + drought monitoring (nova-wems-features)
- [🔄] brain.py test suite expansion — delete_stm tests, edge cases (nova-brain-tests)
- [🔄] **OpenClaw Upstream Sync** — merging 2,889 upstream commits, 16 conflicts remaining (helios-merge-finish)
- [🔄] **Ansible**: Fleet hardening audit (#6) — sub-agent running (ansible-security-audit)

## Priority (do next)
- [x] **AUGUR V4**: Fixed database disconnect — added v4_scanner_loop() to paper_augur.py (v4.5.0, 267a242)
- [x] **stm.json Migration Audit**: All stm.json references eliminated, brain.db migration 100% complete
- [x] **Heartbeat Optimization**: Stripped HEARTBEAT.md to comments-only, moved all logic to cron/n8n events
- [ ] **CHANGELOG Automation**: Generate from conventional commits (#7)

## Backlog
- [ ] **RTSP Cameras**: Give Helios security-type vision — research RTSP camera options, integrate streams into Helios for real-time visual monitoring (indoor/outdoor), motion detection, object recognition. Phone node + RC vehicle tie-in potential.
- [ ] **Lightweight Heartbeat Mode (H0-4)**: Two-stage heartbeat — cheap flag/webhook check before expensive agent turn. Requires OpenClaw source changes.

## Available (grab any)
- [ ] Build Twilio integration (Matthew wanted call capability since psilocybin session)
- [ ] WEMS: Submit to awesome-mcp-servers list (PR pending review)
- [ ] Create OpenClaw skill for AUGUR trading management
- [ ] Explore ClawHub for useful skills to install
- [ ] LBF Operating Model — revenue projections, pricing strategy

## Completed (v0.3.0 Sprint)
- [x] **n8n Integration**: Complete event-driven architecture — event dispatcher, webhook endpoints, integration hooks, workflow templates, comprehensive testing suite (2026-02-16)
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
