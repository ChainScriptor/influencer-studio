#!/usr/bin/env bash
# Rebuild influencer-studio.zip (the file people upload to the Claude app) from the skill folder.
set -euo pipefail
cd "$(dirname "$0")/plugins/influencer-studio/skills"
rm -f ../../../influencer-studio.zip
find influencer-studio -name __pycache__ -prune -exec rm -rf {} +
zip -qr ../../../influencer-studio.zip influencer-studio
echo "Built influencer-studio.zip"
