#!/bin/bash
# ==============================================================================
# Script: analyze-logs.sh
# Purpose: Parse Docker application logs, calculate HTTP distributions, and flag errors
# ==============================================================================

set -euo pipefail

CONTAINER_NAME="${1:-devops-flask-app}"
SAMPLE_LINES=200

echo "================================================="
echo " Application Log Health & Traffic Analyzer"
echo " Container: $CONTAINER_NAME (Last $SAMPLE_LINES log lines)"
echo " Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"
echo "================================================="

LOGS=$(docker logs --tail "$SAMPLE_LINES" "$CONTAINER_NAME" 2>&1 || true)
TOTAL_LINES=$(echo "$LOGS" | grep -c . || true)
echo "[INFO] Total analyzed log entries: $TOTAL_LINES"

# Extract HTTP status codes
echo ""
echo "--- HTTP Response Code Distribution ---"
STATUS_2XX=$(echo "$LOGS" | grep -Ec " (200|201|204) " || true)
STATUS_4XX=$(echo "$LOGS" | grep -Ec " (400|401|403|404) " || true)
STATUS_5XX=$(echo "$LOGS" | grep -Ec " (500|502|503|504) " || true)

echo "  [2xx Success] : $STATUS_2XX requests"
echo "  [4xx Client]  : $STATUS_4XX requests"
echo "  [5xx Server]  : $STATUS_5XX requests"

# Flag potential critical exceptions
echo ""
echo "--- Error & Exception Scanner ---"
ERROR_COUNT=$(echo "$LOGS" | grep -Eic "(error|critical|exception|traceback)" || true)

if [ "$ERROR_COUNT" -eq 0 ]; then
  echo "  [CLEAN] No unhandled exceptions or critical errors detected."
else
  echo "  [INFO] Found $ERROR_COUNT log lines mentioning error/exception:"
  echo "$LOGS" | grep -Eic "(error|critical|exception|traceback)" | tail -n 5 || true
fi

echo "================================================="
echo " Log analysis complete."
echo "================================================="
exit 0
