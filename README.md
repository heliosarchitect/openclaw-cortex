# Helios — OpenClaw Cortex Workspace

**An AI Agent Workspace for Advanced Automation & Analysis**

This repository contains the complete workspace for **Helios**, an autonomous AI agent that serves as CTO/COO for LBF (Let's Build the Future). Helios combines trading automation, system monitoring, memory management, and strategic planning into a unified intelligent system.

> **Version:** v0.3.0 (February 2026)  
> **Agent:** Helios  
> **Remote:** [heliosarchitect/openclaw-cortex](https://github.com/heliosarchitect/openclaw-cortex)

## 🧠 What is Helios?

Helios is an advanced AI agent built on OpenClaw that:
- **Trades cryptocurrency** with autonomous decision-making
- **Manages infrastructure** across multiple systems and services  
- **Maintains persistent memory** using Cortex STM and atomic knowledge
- **Conducts research** and generates actionable intelligence
- **Communicates proactively** via Signal, email, and voice calls
- **Self-improves** through structured sprints and capability expansion

See [HELIOS_VISION.md](./HELIOS_VISION.md) for the complete program roadmap.

## 📁 Directory Structure

### 🔗 Core Identity & Configuration
```
AGENTS.md           # Agent interaction guidelines
IDENTITY.md         # Core identity and purpose 
SOUL.md             # Personality and behavioral traits
USER.md             # User preferences and context
MEMORY.md           # Memory management principles
TOOLS.md            # Tool usage guidelines
HEARTBEAT.md        # Autonomous heartbeat behavior
HELIOS_VISION.md    # Program vision and roadmap
CHANGELOG.md        # Version history and updates
```

### 🧠 Memory & Intelligence
```
memory/
├── brain.db                # Cortex long-term memory database
├── stm.json               # Short-term memory cache
├── synapse.json           # Inter-agent messaging
├── working_memory.json    # Pinned context items
├── 2026-02-*.md          # Daily logs and reflections
├── pattern-audit-*.md    # Memory pattern analysis
└── collections/          # Specialized memory collections
```

### 🔧 Operational Scripts
```
scripts/
├── system-health-check.sh      # Infrastructure monitoring
├── memory-hygiene.sh          # Memory cleanup & optimization
├── workspace-cleanup.sh       # File organization
├── backup_to_drive.sh         # Google Drive backups
├── token-efficiency-tracker.py # AI model usage analysis
├── end_of_day.py              # Daily trading reports
├── skylight.py                # Market scanning & alerts
├── github-release-monitor/    # Software update tracking
├── helios-monitor/            # Self-monitoring tools
└── memory-consolidation/      # Memory management utilities
```

### 🎯 Skills & Capabilities
```
skills/                        # ClawHub skill packages
├── task-decomposer/          # Breaking down complex tasks
├── task-graph/               # Task dependency management
├── security-monitor/         # Security event monitoring
├── model-usage/              # AI usage optimization
├── session-logs/             # Session analysis
├── agent-council/            # Multi-agent coordination
├── clawnance/                # Financial governance
└── [14 more specialized skills]
```

### 📊 Analysis & Research
```
analysis/
├── eod/                      # End-of-day analysis
├── h0-5-budget-analysis/     # Budget optimization research
└── scripts/                  # Analysis utilities

reports/
├── security/                 # Security assessments
└── [Generated reports and documentation]
```

### 🔮 Vision & Planning
```
vision/                       # Detailed vision documents
sprints/                      # Sprint planning and status
docs/                         # Technical documentation
├── SYNAPSE_V2.md            # Inter-agent messaging protocol
└── [Other technical specs]
```

### 🏛️ Infrastructure
```
cortex/                       # Cortex memory system (submodule)
data/                         # Data storage and processing
config/                       # Configuration files
keys/                         # API keys and credentials
archive/                      # Historical data and backups
```

## 🚀 Key Capabilities

### 💰 Trading & Finance
- **Autonomous trading** across 44+ cryptocurrency pairs
- **Market analysis** using AUGUR signals and technical indicators
- **Risk management** with position sizing and stop losses
- **Performance tracking** with detailed P&L analysis

### 🔍 Monitoring & Intelligence  
- **System health monitoring** across multiple servers
- **Security event detection** via Wazuh integration
- **Market scanning** for opportunities and anomalies
- **Release monitoring** for software dependencies

### 🧠 Memory & Learning
- **Persistent memory** using Cortex STM with 15,000+ entries
- **Atomic knowledge** representation for causal reasoning
- **Pattern recognition** and behavioral analysis
- **Self-improvement** through structured learning

### 🤖 Automation & Integration
- **Cron-based scheduling** for autonomous operations
- **Multi-channel communication** (Signal, email, voice)
- **API integrations** with 20+ external services
- **Sub-agent spawning** for complex task execution

## 🛠️ Usage

### Daily Operations
```bash
# Health check and system status
./scripts/system-health-check.sh

# Memory maintenance
./scripts/memory-hygiene.sh

# End of day reports
./scripts/end_of_day.py
```

### Memory Management
```bash
# Check Cortex status
python memory/cortex_cli.py stats

# Pattern analysis
python memory/cortex_cli.py audit

# Memory consolidation  
./scripts/memory-consolidation/consolidate.py
```

### Skill Management
```bash
# List available skills
ls skills/

# Install new skill
openclaw skill install <skill-name>
```

## 📈 Current Status (v0.3.0)

### ✅ Completed Features
- **Memory system overhaul** — Fixed Cortex tools and optimized storage
- **Token efficiency** — Reduced context size by 5,200 tokens/turn
- **File organization** — Trimmed and consolidated core files
- **Pattern auditing** — Automated memory pattern recognition

### 🔄 Active Development
- **Phase H0-4:** OpenClaw source code internalization
- **Budget optimization** — Dynamic context sizing
- **Turn counter integration** — Conversation flow tracking
- **AUGUR V4** — Next-generation trading signals

### 🎯 Upcoming Features
- **Multi-agent coordination** via SYNAPSE protocol
- **Advanced task decomposition** with dependency graphs
- **Enhanced security monitoring** and threat response
- **Expanded skill ecosystem** and capability sharing

## 📚 Key Documentation

- **[HELIOS_VISION.md](./HELIOS_VISION.md)** — Complete program vision and roadmap
- **[CHANGELOG.md](./CHANGELOG.md)** — Version history and feature updates
- **[memory/README.md](./memory/README.md)** — Memory system documentation
- **[skills/README.md](./skills/README.md)** — Skill development guide
- **[docs/SYNAPSE_V2.md](./docs/SYNAPSE_V2.md)** — Inter-agent messaging protocol

## 🔐 Security & Privacy

- **Credentials** stored in encrypted `keys/` directory
- **Sensitive data** excluded from version control via `.gitignore`
- **Access controls** implemented for all external integrations
- **Audit logging** for all automated operations

## 🤝 Contributing

This is a private workspace for Helios operations. For skill contributions or feature requests:

1. Check existing capabilities in `skills/`
2. Review the vision documents in `vision/`
3. Follow the development patterns in `sprints/`

## 📞 Contact

**Primary User:** Matthew  
**Communication:** Signal, Email, Voice  
**System:** OpenClaw v2026.2.13+  
**Environment:** Linux (giggletits)

---

*Helios — Becoming the partner, not the tool.*