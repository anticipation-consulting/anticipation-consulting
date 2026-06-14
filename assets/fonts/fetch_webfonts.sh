#!/usr/bin/env bash
# Self-hosted web fonts for the site — removes the Google Fonts (third-party CDN)
# dependency so no visitor IP/User-Agent is sent to Google on page load.
#
# Pulls the latin-subset WOFF2 for exactly the families/weights/styles the site
# uses (mirrors the old Google Fonts request) from Fontsource via jsDelivr. The
# fonts are OFL-licensed, so redistribution/self-hosting is permitted. The
# downloaded .woff2 are committed; re-run this only to refresh them.
set -euo pipefail
cd "$(dirname "$0")"
B="https://cdn.jsdelivr.net/fontsource/fonts"
fetch() { curl -fsSL -o "$2" "$B/$1"; printf '  %-32s %6s bytes\n' "$2" "$(stat -c%s "$2")"; }

# Spectral — serif display/headings (+ italics for <em>)
fetch "spectral@latest/latin-400-normal.woff2"            spectral-400.woff2
fetch "spectral@latest/latin-500-normal.woff2"            spectral-500.woff2
fetch "spectral@latest/latin-600-normal.woff2"            spectral-600.woff2
fetch "spectral@latest/latin-400-italic.woff2"           spectral-400-italic.woff2
fetch "spectral@latest/latin-500-italic.woff2"           spectral-500-italic.woff2
# IBM Plex Sans — body
fetch "ibm-plex-sans@latest/latin-400-normal.woff2"      ibm-plex-sans-400.woff2
fetch "ibm-plex-sans@latest/latin-500-normal.woff2"      ibm-plex-sans-500.woff2
fetch "ibm-plex-sans@latest/latin-600-normal.woff2"      ibm-plex-sans-600.woff2
# IBM Plex Mono — eyebrows/labels
fetch "ibm-plex-mono@latest/latin-400-normal.woff2"      ibm-plex-mono-400.woff2
fetch "ibm-plex-mono@latest/latin-500-normal.woff2"      ibm-plex-mono-500.woff2
# Cormorant Garamond — header wordmark
fetch "cormorant-garamond@latest/latin-300-normal.woff2" cormorant-garamond-300.woff2
fetch "cormorant-garamond@latest/latin-400-normal.woff2" cormorant-garamond-400.woff2
fetch "cormorant-garamond@latest/latin-600-normal.woff2" cormorant-garamond-600.woff2
fetch "cormorant-garamond@latest/latin-300-italic.woff2" cormorant-garamond-300-italic.woff2
fetch "cormorant-garamond@latest/latin-400-italic.woff2" cormorant-garamond-400-italic.woff2
# GFS Didot — the logo "A" (header SVG)
fetch "gfs-didot@latest/latin-400-normal.woff2"          gfs-didot-400.woff2
echo "Self-hosted web fonts fetched into assets/fonts/"
