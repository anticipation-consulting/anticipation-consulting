#!/usr/bin/env bash
# Fetch the open-source brand typefaces (OFL) into brand/fonts/.
# Run before generate_assets.py if the fonts aren't present.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p fonts
B="https://raw.githubusercontent.com/google/fonts/main/ofl"
curl -fsSL -o fonts/GFSDidot-Regular.ttf      "$B/gfsdidot/GFSDidot-Regular.ttf"
curl -fsSL -o fonts/CormorantGaramond-VF.ttf  "$B/cormorantgaramond/CormorantGaramond%5Bwght%5D.ttf"
curl -fsSL -o fonts/IBMPlexMono-Regular.ttf   "$B/ibmplexmono/IBMPlexMono-Regular.ttf"
echo "Fonts fetched into brand/fonts/"
