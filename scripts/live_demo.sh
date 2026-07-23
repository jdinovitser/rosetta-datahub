#!/usr/bin/env bash
#
# live_demo.sh — one command to prove Rosetta's LIVE DataHub write-back.
#
# Run this inside a GitHub Codespace (Docker-in-Docker enabled by .devcontainer).
# It will:
#   1. Boot a real DataHub instance (datahub docker quickstart)
#   2. Ingest Rosetta's sample graph (terms + datasets + lineage)
#   3. Confirm Rosetta connects in LIVE mode
#   4. Detect conflicts against the real graph
#   5. Write canonical glossary terms BACK into DataHub
#
# After it finishes, open the DataHub UI (port 9002, login datahub/datahub)
# and show the new canonical term in Glossary -> this is your money shot.
#
set -euo pipefail

echo "=============================================="
echo " STEP 1/5  Installing DataHub CLI"
echo "=============================================="
pip install --upgrade acryl-datahub >/dev/null
datahub version

echo
echo "=============================================="
echo " STEP 2/5  Booting DataHub (this takes ~5-10 min the first time)"
echo "=============================================="
datahub docker quickstart

# GMS listens on 8080; UI on 9002.
export DATAHUB_GMS_URL="http://localhost:8080"

echo
echo "=============================================="
echo " STEP 3/5  Seeding Rosetta's sample graph into DataHub"
echo "=============================================="
python scripts/ingest_seed_to_datahub.py

echo
echo "=============================================="
echo " STEP 4/5  Rosetta connects to the REAL graph"
echo "=============================================="
python -m rosetta.orchestrator --check-connection
echo
echo "-- Detecting conflicts against LIVE DataHub --"
python -m rosetta.orchestrator --report --live

echo
echo "=============================================="
echo " STEP 5/5  Writing canonical terms BACK into DataHub"
echo "=============================================="
python -m rosetta.orchestrator --apply --live

echo
echo "=============================================="
echo " DONE. Now open the DataHub UI:"
echo "   - Click the forwarded port 9002 (or PORTS tab -> globe icon)"
echo "   - Log in: datahub / datahub"
echo "   -
