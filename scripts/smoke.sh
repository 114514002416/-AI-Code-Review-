#!/usr/bin/env bash
set -euo pipefail

python3 -m pip install -q --upgrade pip
pip3 install -q -e .

echo "Running AICR on current workspace..."
aicr || python3 -m aicr.cli

echo "Done."
