#!/bin/bash
# Helios BC/DR Backup Script
# Backs up critical state to Google Drive (heliosarchitectlbf@gmail.com)

set -e

WORKSPACE="$HOME/.openclaw/workspace"
BACKUP_DIR="/tmp/helios-backup-$(date +%Y%m%d)"
BACKUP_NAME="helios-backup-$(date +%Y%m%d-%H%M%S).tar.gz"

echo "🔄 Starting Helios backup..."

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Copy critical files
echo "📦 Collecting critical state..."

# Memory files
cp -r "$WORKSPACE/memory" "$BACKUP_DIR/" 2>/dev/null || mkdir -p "$BACKUP_DIR/memory"

# Identity files
mkdir -p "$BACKUP_DIR/identity"
cp "$WORKSPACE/SOUL.md" "$BACKUP_DIR/identity/" 2>/dev/null || true
cp "$WORKSPACE/IDENTITY.md" "$BACKUP_DIR/identity/" 2>/dev/null || true
cp "$WORKSPACE/MEMORY.md" "$BACKUP_DIR/identity/" 2>/dev/null || true
cp "$WORKSPACE/USER.md" "$BACKUP_DIR/identity/" 2>/dev/null || true
cp "$WORKSPACE/TOOLS.md" "$BACKUP_DIR/identity/" 2>/dev/null || true
cp "$WORKSPACE/AGENTS.md" "$BACKUP_DIR/identity/" 2>/dev/null || true
cp "$WORKSPACE/HEARTBEAT.md" "$BACKUP_DIR/identity/" 2>/dev/null || true

# Cortex database
cp "$WORKSPACE/memory/.embeddings.db" "$BACKUP_DIR/cortex.db" 2>/dev/null || true

# Create tarball
echo "📦 Creating archive..."
cd /tmp
tar -czf "$BACKUP_NAME" "helios-backup-$(date +%Y%m%d)"

# Upload to Google Drive
echo "☁️ Uploading to Google Drive..."
# Helios-Backup folder ID: 1hOKp5XvyT68lPpkANxxZooySV7Z74Tu9
gog drive upload "/tmp/$BACKUP_NAME" --name "$BACKUP_NAME" --parent "1hOKp5XvyT68lPpkANxxZooySV7Z74Tu9"

# Cleanup
rm -rf "$BACKUP_DIR" "/tmp/$BACKUP_NAME"

echo "✅ Backup complete: $BACKUP_NAME"
