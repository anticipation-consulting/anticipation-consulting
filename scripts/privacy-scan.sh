#!/usr/bin/env bash
# Privacy regression guard.
#
# Fails if the BUILT site pulls in any third-party subresource — a CDN font,
# external stylesheet/script, off-site image/iframe, or a preconnect/@import to
# another origin. These are the things that leak a visitor's IP/User-Agent to a
# third party on page load. Navigational <a> links (e.g. social profiles in the
# footer) are exempt: they only contact the destination when a user clicks.
#
# Usage:  scripts/privacy-scan.sh [SITE_DIR]   (default: _site; build first)
set -euo pipefail
SITE="${1:-_site}"
SELF='anticipationconsulting\.com'   # the site's own origin (allowed)

[ -d "$SITE" ] || { echo "privacy-scan: '$SITE' not found — run 'jekyll build' first" >&2; exit 2; }

host_of() { grep -oE 'https?://[^"'\'' )]+' | sed -E 's#(https?://[^/]+).*#\1#'; }

# (a) External URLs loaded by resource elements — NOT <a> links.
html_ext=$(grep -rhoE '<(link|script|img|iframe|source|audio|video|embed|object|track)\b[^>]*\b(src|href)="https?://[^"]+"' \
  "$SITE" --include='*.html' | host_of | grep -viE "$SELF" | sort -u || true)

# (b) External URLs referenced from CSS (@import / url()).
css_ext=$(grep -rhoE '(@import|url\()[^);]*https?://[^"'\'' )]+' \
  "$SITE" --include='*.css' | host_of | grep -viE "$SELF" | sort -u || true)

# (c) preconnect / dns-prefetch hints to third parties.
hint_ext=$(grep -rhoE '<link[^>]+rel="(preconnect|dns-prefetch)"[^>]*href="https?://[^"]+"' \
  "$SITE" --include='*.html' | host_of | grep -viE "$SELF" | sort -u || true)

offenders=$(printf '%s\n%s\n%s\n' "$html_ext" "$css_ext" "$hint_ext" | sed '/^[[:space:]]*$/d' | sort -u)

if [ -n "$offenders" ]; then
  echo "✗ privacy-scan: the built site pulls third-party resources:" >&2
  echo "$offenders" | sed 's/^/    /' >&2
  echo "  -> self-host the asset or remove it (navigational <a> links are exempt)." >&2
  exit 1
fi
echo "✓ privacy-scan: no third-party subresources — the site loads only same-origin assets"
