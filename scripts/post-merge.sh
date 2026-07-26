#!/bin/bash
# Post-merge setup for Rosetta — runs automatically after every task merge.
# Must be idempotent and non-interactive (stdin is /dev/null).
set -e

echo "==> Installing Python dependencies..."
pip install -r requirements.txt -q

echo "==> Verifying demo pipeline runs..."
python -c "
from rosetta.demo import run_demo
r = run_demo()
n = r['report']['summary']['total_conflicts']
print(f'  Demo OK: {n} conflicts detected, {len(r[\"steps\"])} pipeline steps')
"

echo "==> Post-merge setup complete."
