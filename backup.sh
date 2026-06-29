#!/usr/bin/env bash
# =============================================================================
# ECO-IA – Automated Backup Script
# =============================================================================
set -euo pipefail

# Load environment
ECO_IA_DIR="${ECO_IA_DIR:-/opt/eco-ia}"
# shellcheck source=/dev/null
[[ -f "$ECO_IA_DIR/.env" ]] && source "$ECO_IA_DIR/.env"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="eco-ia-backup-$TIMESTAMP"
REMOTE_PATH="${HETZNER_STORAGE_BOX_USER:-}@${HETZNER_STORAGE_BOX_HOST:-}:/backups/eco-ia"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"
LOCAL_BACKUP_DIR="${LOCAL_BACKUP_DIR:-}"
if [[ -z "$LOCAL_BACKUP_DIR" ]]; then
    LOCAL_BACKUP_DIR=$(mktemp -d -t eco-ia-backups-XXXXXX)
    CLEANUP_TMPDIR=1
else
    mkdir -p "$LOCAL_BACKUP_DIR"
    CLEANUP_TMPDIR=0
fi

echo "[$TIMESTAMP] Starting ECO-IA backup…"

# ── 1. PostgreSQL dump ───────────────────────────────────────────────────────
echo "Dumping PostgreSQL database…"
docker exec eco-ia-postgres pg_dump -U eco_ia eco_ia \
    | gzip > "$LOCAL_BACKUP_DIR/${BACKUP_NAME}-db.sql.gz" \
    && echo "✅ Database dump complete." \
    || echo "❌ Database dump FAILED."

# ── 2. Configuration backup ──────────────────────────────────────────────────
echo "Backing up configuration…"
tar -czf "$LOCAL_BACKUP_DIR/${BACKUP_NAME}-config.tar.gz" \
    "$ECO_IA_DIR/.env" \
    "$ECO_IA_DIR/config/" \
    2>/dev/null \
    && echo "✅ Config backup complete." \
    || echo "❌ Config backup FAILED."

# ── 3. Upload to Hetzner Storage Box ─────────────────────────────────────────
if [[ -n "${HETZNER_STORAGE_BOX_HOST:-}" && -n "${HETZNER_STORAGE_BOX_USER:-}" ]]; then
    echo "Uploading to Hetzner Storage Box…"
    rsync -az --delete \
        -e "ssh -o StrictHostKeyChecking=no -p 23" \
        "$LOCAL_BACKUP_DIR/" \
        "$REMOTE_PATH/" \
        && echo "✅ Upload complete." \
        || echo "❌ Upload FAILED."
else
    echo "⚠  Hetzner Storage Box not configured; keeping local backup only."
fi

# ── 4. Clean old local backups ────────────────────────────────────────────────
echo "Cleaning backups older than $RETENTION_DAYS days…"
find "$LOCAL_BACKUP_DIR" -name "eco-ia-backup-*" -mtime "+$RETENTION_DAYS" -delete
echo "✅ Cleanup complete."

echo "[$TIMESTAMP] Backup finished: $BACKUP_NAME"

# ── 5. Clean up temporary directory if created by mktemp ──────────────────────
if [[ "$CLEANUP_TMPDIR" -eq 1 ]]; then
    rm -rf "$LOCAL_BACKUP_DIR"
fi
