# Skills Directory

This directory contains OpenClaw agent skills that extend capabilities beyond core tools.

## 🏗️ Infrastructure & System Management

| Skill | Description | Status |
|-------|-------------|---------|
| [agent-council](agent-council/) | Complete toolkit for autonomous AI agents and Discord channel management | ✅ Production |
| [desktop-control](desktop-control/) | Advanced desktop automation with mouse, keyboard, and screen control | ✅ Production |
| [security-monitor](security-monitor/) | Comprehensive security monitoring and SIEM integration for OpenClaw | ✅ Production |
| [task-graph](task-graph/) | Lightweight knowledge graph of systems, APIs, models, and relationships | ✅ Production |

## 🌍 Data & Monitoring

| Skill | Description | Status |
|-------|-------------|---------|
| [earthquake-monitor](earthquake-monitor/) | Monitor global earthquake activity using USGS data | ✅ Production |
| [weather](weather/) | Get current weather and forecasts (no API key required) | ✅ Production |

## 🔧 Development & Productivity

| Skill | Description | Status |
|-------|-------------|---------|
| [clawhub](clawhub/) | Search, install, update, and publish agent skills from clawhub.com | ✅ Production |
| [github](github/) | Interact with GitHub using the `gh` CLI for issues, PRs, and CI runs | ✅ Production |
| [skill-creator](skill-creator/) | Create or update AgentSkills with proper structure and packaging | ✅ Production |
| [todo-scheduler](todo-scheduler/) | Generate cron jobs from a todo list for automated task execution | ✅ Production |

## 🎵 Media & Content

| Skill | Description | Status |
|-------|-------------|---------|
| [openai-image-gen](openai-image-gen/) | Batch-generate images via OpenAI Images API with gallery | ✅ Production |
| [openai-whisper-api](openai-whisper-api/) | Transcribe audio via OpenAI Audio Transcriptions API (Whisper) | ✅ Production |
| [songsee](songsee/) | Generate spectrograms and feature-panel visualizations from audio | ✅ Production |
| [video-frames](video-frames/) | Extract frames or short clips from videos using ffmpeg | ✅ Production |

## 🔐 Authentication & Integration

| Skill | Description | Status |
|-------|-------------|---------|
| [1password](1password/) | Set up and use 1Password CLI for secret management | ✅ Production |
| [bluebubbles](bluebubbles/) | Build or update BlueBubbles external channel plugin for OpenClaw | ✅ Production |
| [gog](gog/) | Google Workspace CLI for Gmail, Calendar, Drive, Contacts, Sheets, Docs | ✅ Production |
| [notion](notion/) | Notion API for creating and managing pages, databases, and blocks | ✅ Production |

## 📊 Analytics & Tools

| Skill | Description | Status |  
|-------|-------------|---------|
| [bird](bird/) | X/Twitter CLI for reading, searching, posting, and engagement | ✅ Production |
| [model-usage](model-usage/) | CodexBar CLI local cost usage for per-model analysis | ✅ Production |
| [summarize](summarize/) | Summarize URLs or files with web, PDFs, images, audio, YouTube | ✅ Production |
| [tmux](tmux/) | Remote-control tmux sessions for interactive CLIs | ✅ Production |

## 📁 Skill Structure

Each skill follows this standard structure:
```
skill-name/
├── SKILL.md              # Main documentation with examples
├── scripts/              # Executable scripts and tools
├── config/               # Configuration templates  
├── references/           # Additional documentation
└── assets/               # Images, data files, etc.
```

## 🔄 Usage Patterns

1. **Read SKILL.md first** - Complete documentation with examples
2. **Check scripts/** - Look for main executable or CLI tools
3. **Review config/** - Configuration templates and examples
4. **Install dependencies** - Skills manage their own requirements

## 🚀 Recent Additions

- **2026-02-13**: security-monitor (Wazuh SIEM integration, system security scanning)
- **2026-02-13**: task-graph expansion (infrastructure endpoints added)
- **2026-02-12**: earthquake-monitor enhancements (alert system, SQLite persistence)

---

*Skills are autonomous capabilities that extend OpenClaw's functionality. Each skill is self-contained with complete documentation and examples.*