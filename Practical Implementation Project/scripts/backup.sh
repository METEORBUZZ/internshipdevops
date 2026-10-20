#!/bin/bash
# ==============================================================================
# Script: backup.sh
# Purpose: Automated archive & backup rotation for DevOps application artifacts
# ==============================================================================

set -euo pipefail

BACKUP_SRC="${1:-./app}"
BACKUP_DEST="${2:-./backups}"
RETENTION_DAYS=7
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
ARCHIVE_NAME="app_backup_${TIMESTAMP}.tar.gz"

echo "=========================================="
echo " Initiating Automated Backup Routine"
echo " Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"
echo " Source: $BACKUP_SRC"
echo " Destination: $BACKUP_DEST"
echo "=========================================="

# Create destination folder if not present
mkdir -p "$BACKUP_DEST"

# Create compressed tarball
tar -czf "${BACKUP_DEST}/${ARCHIVE_NAME}" -C "$(dirname "$BACKUP_SRC")" "$(basename "$BACKUP_SRC")"
echo "[SUCCESS] Created backup archive: ${BACKUP_DEST}/${ARCHIVE_NAME}"

# Cleanup older archives
echo "[INFO] Cleaning archives older than ${RETENTION_DAYS} days..."
find "$BACKUP_DEST" -name "app_backup_*.tar.gz" -mtime +"$RETENTION_DAYS" -exec rm -f {} + 2>/dev/null || true

echo "=========================================="
echo " Backup operation completed."
echo "=========================================="
exit 0
