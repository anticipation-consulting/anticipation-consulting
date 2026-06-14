# Security Policy

Anticipation Consulting welcomes good-faith reports of security or privacy
issues in this website or its code.

## Reporting a vulnerability

- **Email:** contact@anticipationconsulting.com
- **Encrypt (for sensitive reports):** PGP public key —
  https://www.anticipationconsulting.com/assets/anticipation-consulting-pgp.asc
  - Fingerprint: `DD86 B677 8532 C67E 4D92  FEA7 83B7 98C4 0C12 BDA6`
- **Signal / other channels:** https://www.anticipationconsulting.com/contact/
- **Machine-readable:** https://www.anticipationconsulting.com/.well-known/security.txt

Please give us a reasonable opportunity to remediate before any public
disclosure. We'll acknowledge good-faith reports promptly.

## Scope

This is a static marketing site — no user accounts, database, or server-side
application code. The most security-relevant surfaces are:

- the Content-Security-Policy meta tag (`_includes/head.html`),
- the build and release automation (`.github/workflows/`),
- the absence of third-party resources, enforced by `scripts/privacy-scan.sh`,
- the brand/image pipeline integrity check (`brand/check_assets.py`).

## Safe harbor

We will not pursue or support legal action against researchers who act in good
faith, avoid privacy violations and service disruption, and do not access or
destroy data that isn't theirs.
