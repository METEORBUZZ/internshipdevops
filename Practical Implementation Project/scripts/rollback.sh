#!/bin/bash
# ==============================================================================
# Script: rollback.sh
# Purpose: Automated zero-downtime rollback procedure if deployment fails
# ==============================================================================

set -euo pipefail

PREVIOUS_TAG="${1:-devops-monitoring-app:stable}"
TARGET_CONTAINER="devops-flask-app"
HEALTH_URL="http://localhost:5050/health"

echo "================================================="
echo " [ALERT] INITIATING AUTOMATED ROLLBACK PROCEDURE"
echo " Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"
echo " Reverting to target image: $PREVIOUS_TAG"
echo "================================================="

# Stop potentially broken container
echo "[1/4] Stopping unhealthy container $TARGET_CONTAINER..."
docker stop "$TARGET_CONTAINER" || true

# Relaunch using the last known stable image
echo "[2/4] Deploying stable container from $PREVIOUS_TAG..."
docker run -d \
  --name "$TARGET_CONTAINER" \
  -p 5050:5000 \
  --restart always \
  "$PREVIOUS_TAG" 2>/dev/null || docker compose -f docker-compose.prod.yml up -d app

# Verify rollback container health
echo "[3/4] Awaiting rollback health probe..."
sleep 5

STATUS_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$HEALTH_URL" || echo "000")

if [ "$STATUS_CODE" -eq 200 ]; then
  echo "[4/4] [SUCCESS] Rollback verified healthy (HTTP 200). Traffic restored."
  exit 0
else
  echo "[4/4] [CRITICAL] Rollback container failed probe (HTTP $STATUS_CODE)!"
  exit 1
fi
