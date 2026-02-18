# GitHub Release Monitor

A Python script to monitor GitHub repositories for new releases and track state.

## Features

- Monitors multiple GitHub repositories for new releases
- Tracks last-seen releases in a JSON state file
- Rate limit awareness (uses GitHub CLI)
- Supports one-shot checking and continuous watching
- Clean output format suitable for notifications
- Configurable repository list and check intervals

## Requirements

- Python 3.6+
- GitHub CLI (`gh`) installed and authenticated
- Access to the repositories you want to monitor

## Usage

### Initial Setup

First, initialize the state with current releases (prevents notifications for existing releases):

```bash
./github-release-monitor.py --init
```

### One-time Check

Check for new releases once:

```bash
./github-release-monitor.py --check
```

Add `--verbose` for detailed output:

```bash
./github-release-monitor.py --check --verbose
```

### Continuous Monitoring

Run continuous monitoring (default 1-hour interval):

```bash
./github-release-monitor.py --watch
```

With custom interval (in seconds):

```bash
./github-release-monitor.py --watch --interval 3600
```

### Custom Repository List

Override the default repository list:

```bash
./github-release-monitor.py --check --repos openclaw/openclaw n8n-io/n8n
```

## Configuration

The script creates two files:

- `config.json`: Contains repository list and default settings
- `releases_state.json`: Tracks the last seen release for each repository

## Default Monitored Repositories

- openclaw/openclaw
- n8n-io/n8n
- ansible/ansible
- hashicorp/terraform
- hashicorp/vault
- grafana/grafana
- prometheus/prometheus
- heliosarchitect/openclaw-cortex
- heliosarchitect/wems-mcp-server

## Rate Limiting

The script checks GitHub API rate limits before making requests and will warn or stop if limits are exceeded. The GitHub CLI typically has higher rate limits when authenticated.

## Integration with OpenClaw

This script is designed to be run as a cron job that can report new releases as system events to OpenClaw.