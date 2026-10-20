#!/bin/bash
# ==============================================================================
# Script: health-check.sh
# Purpose: Automated health, resource monitoring, and alerting script.
# ==============================================================================

set -euo pipefail

TARGET_URL="${1:-http://localhost:5050/api/health}"
DISK_ALERT_THRESHOLD=90
MEM_ALERT_THRESHOLD=90

echo "=========================================="
echo " Starting DevOps Automated Health Check"
echo " Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"
echo "=========================================="

STATUS_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$TARGET_URL" || echo "000")

if [ "$STATUS_CODE" -eq 200 ]; then
  echo "[OK] Application endpoint $TARGET_URL responded with HTTP 200 (Healthy)."
else
  echo "[CRITICAL] Application health check failed at $TARGET_URL (Status: $STATUS_CODE)"
  exit 1
fi

# Check root filesystem disk usage
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | tr -d '%')
echo "[INFO] Current Root Disk Usage: ${DISK_USAGE}%"
if [ "$DISK_USAGE" -ge "$DISK_ALERT_THRESHOLD" ]; then
  echo "[WARNING] Disk usage exceeds threshold (${DISK_ALERT_THRESHOLD}%)!"
fi

echo "=========================================="
echo " Health check completed successfully."
echo "=========================================="
exit 0
