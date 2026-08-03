#!/usr/bin/env bash
# scripts/setup_datahub_local.sh
#
# Sets up a local DataHub instance and runs Rosetta's full Connected Mode
# evidence flow: seed → detect → propose → approve → execute → verify.
#
# Prerequisites:
#   • Docker Desktop 4.x+ (macOS/Windows) or Docker Engine 20+ (Linux)
#   • 16 GB RAM recommended (8 GB minimum — DataHub GMS + Elasticsearch + Kafka)
#   • 10 GB free disk for Docker images
#   • Python 3.10+ with pip
#
# Usage:
#   chmod +x scripts/setup_datahub_local.sh
#   ./scripts/setup_datahub_local.sh
#
# Cleanup:
#   datahub docker quickstart --stop
#   docker system prune -f

set -euo pipefail

BOLD="\033[1m"
GREEN="\033[32m"
YELLOW="\033[33m"
RED="\033[31m"
RESET="\033[0m"

ok()   { echo -e "${GREEN}✓${RESET}  $*"; }
info() { echo -e "${BOLD}▶${RESET}  $*"; }
warn() { echo -e "${YELLOW}⚠${RESET}  $*"; }
die()  { echo -e "${RED}✗${RESET}  $*" >&2; exit 1; }

# ── 0. Prerequisites check ───────────────────────────────────────────────────

info "Checking prerequisites …"

command -v docker >/dev/null 2>&1   || die "Docker not found. Install from https://docs.docker.com/get-docker/"
command -v python3 >/dev/null 2>&1  || die "python3 not found."
command -v pip >/dev/null 2>&1      || die "pip not found."
command -v datahub >/dev/null 2>&1  || { info "Installing acryl-datahub …"; pip install -q acryl-datahub; }

# Memory check
AVAIL_MEM_KB=$(grep MemAvailable /proc/meminfo 2>/dev/null | awk '{print $2}' || sysctl -n hw.memsize 2>/dev/null | awk '{print int($1/1024)}')
AVAIL_MEM_GB=$((AVAIL_MEM_KB / 1024 / 1024))
if [ "${AVAIL_MEM_GB}" -lt 8 ]; then
    warn "Only ${AVAIL_MEM_GB} GB RAM available. DataHub requires 8 GB minimum."
    warn "You may encounter OOM errors. Increase Docker Desktop memory allocation."
    read -r -p "Continue anyway? [y/N] " REPLY
    [[ "${REPLY}" =~ ^[Yy]$ ]] || exit 0
else
    ok "Memory: ${AVAIL_MEM_GB} GB available"
fi

ok "All prerequisites met"

# ── 1. Start DataHub quickstart ───────────────────────────────────────────────

info "Starting DataHub quickstart (this pulls ~4 GB of images the first time) …"
datahub docker quickstart

# ── 2. Wait for GMS to be healthy ────────────────────────────────────────────

info "Waiting for DataHub GMS to be healthy …"
MAX_WAIT=180
WAITED=0
until curl -sf http://localhost:8080/health >/dev/null 2>&1; do
    sleep 5
    WAITED=$((WAITED + 5))
    if [ "${WAITED}" -ge "${MAX_WAIT}" ]; then
        die "DataHub GMS did not become healthy within ${MAX_WAIT}s. Check: docker ps && docker logs datahub-gms-1"
    fi
    echo -n "."
done
echo
ok "DataHub GMS is healthy at http://localhost:8080"

# ── 3. Generate a personal access token ──────────────────────────────────────

info "Generating a DataHub personal access token …"
# The default admin credentials for a freshly started quickstart are:
#   username: datahub
#   password: datahub
TOKEN_JSON=$(curl -sf -X POST http://localhost:8080/openapi/v3/auth/generateToken \
    -H "Content-Type: application/json" \
    -d '{"actorUrn":"urn:li:corpuser:datahub","duration":{"value":7,"unit":"DAYS"},"name":"rosetta-evidence"}' \
    --user "datahub:datahub" 2>/dev/null || echo '{"accessToken": ""}')
TOKEN=$(echo "${TOKEN_JSON}" | python3 -c "import sys,json; print(json.load(sys.stdin).get('accessToken',''))" 2>/dev/null || true)

if [ -z "${TOKEN}" ]; then
    warn "Could not auto-generate a token via the API. Try the UI instead:"
    warn "  1. Open http://localhost:9002 (DataHub UI)"
    warn "  2. Settings → Access Tokens → Generate new token"
    warn "  3. Copy the token and export it:"
    warn "     export DATAHUB_GMS_TOKEN=<your-token>"
else
    ok "Access token generated (not printed here for security)"
    export DATAHUB_GMS_TOKEN="${TOKEN}"
fi

export DATAHUB_GMS_URL="http://localhost:8080"

# ── 4. Run the evidence script ────────────────────────────────────────────────

info "Running Rosetta Connected Mode evidence generator …"
python3 scripts/generate_connected_mode_evidence.py

ok "Evidence run complete. Check the evidence/ directory for output files."

# ── 5. Summary ────────────────────────────────────────────────────────────────

echo ""
echo "═══════════════════════════════════════════════════════"
echo "  DataHub is still running at http://localhost:8080"
echo "  DataHub UI at http://localhost:9002 (admin/datahub)"
echo ""
echo "  To stop:  datahub docker quickstart --stop"
echo "═══════════════════════════════════════════════════════"
