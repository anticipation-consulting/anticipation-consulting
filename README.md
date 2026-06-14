# Anticipation Consulting

The website for **Anticipation Consulting** — a boutique data science and AI
consultancy led by Brian C. Keegan, Ph.D. Built with [Jekyll](https://jekyllrb.com/)
using a bespoke, self-contained theme (no external theme dependency).

> *We find questions you didn't know to ask and deliver evidence designed to be challenged.*

🔗 **Live site:** https://www.anticipationconsulting.com

> **Contributing, or using an AI agent?** Start with **[AGENTS.md](AGENTS.md)** —
> the canonical context for architecture, design system, mission, and brand.

## Design system

- **Type** — Spectral (serif display) · IBM Plex Sans (body) · IBM Plex Mono
  (labels/eyebrows) · Cormorant Garamond + GFS Didot (wordmark). **Self-hosted**
  in `assets/fonts/` (no third-party CDN); see *Security & privacy* in
  [AGENTS.md](AGENTS.md).
- **Palettes** — three palettes are defined as `html[data-palette="signal|ink|field"]`
  blocks of CSS custom properties in `assets/site.css`. **Signal** (charcoal +
  electric blue) is the default.
- **Logo** — a tilted Didot “A” (electric blue, −30°) set against
  `nticipation Consulting`, so the mark itself is the leading “A”.
- **Interactive background** — `assets/site.js` injects one fixed, full-viewport
  `<canvas id="net-bg">`: a drifting node-link field (triangular nodes in the
  brand triad) that links toward the cursor. It is palette-aware, pauses when
  the tab is hidden, and renders **statically** under `prefers-reduced-motion`.
  Dark `.ink-section` bands carry their own static `hero-motif` canvas.

## Structure

```
.
├── _config.yml              # Site config (URL, title, SEO defaults)
├── _data/
│   └── services.yml         # The nine services (single source of truth)
├── _includes/
│   ├── head.html            # Per-page SEO: meta, Open Graph, Twitter, fonts, CSS
│   ├── header.html          # Sticky nav + wordmark
│   ├── footer.html          # Site footer
│   └── schema/              # JSON-LD partials (home, services, service, about, contact)
├── _layouts/
│   └── default.html         # The single shared page shell
├── assets/
│   ├── site.css             # Design system + components (tokens, layout, all components)
│   ├── site.js              # Network background, mobile nav, palette persistence, reveals
│   └── favicon.svg          # Tilted Didot “A” favicon
├── images/                  # og-image.png, headshot
├── index.html               # Home
├── services.html            # Services overview (tiles + 9 anchored sections, data-driven)
├── services/data-science.html  # Flagship service detail
├── about.html · expertise.html · insights.html · contact.html
├── sitemap.xml · robots.txt # Generated from page front matter
├── .github/workflows/ci.yml # Builds the site on every push / PR
├── brand/                   # Reproducible brand kit (see brand/README.md)
└── AGENTS.md · CLAUDE.md    # Agent/contributor context (excluded from the build)
```

The nine services are defined once in `_data/services.yml` and drive the home
page grid, the Services overview page, and the `ItemList` structured data.

## SEO

Per-page `<title>`, meta description, canonical, robots, Open Graph + Twitter
cards, and JSON-LD are emitted from `_includes/head.html` driven by each page's
front matter (`seo_title`, `description`, `og_*`, `schema`, …). `sitemap.xml`
and `robots.txt` are generated from front matter. Content is kept honest — no
fabricated clients, logos, metrics, or case outcomes.

## Local development

Requires Ruby and [Bundler](https://bundler.io/).

```bash
bundle install            # install dependencies
bundle exec jekyll serve  # serve locally at http://localhost:4000
bundle exec jekyll build  # build the production site into _site/
```

## Deployment

The production site is built with `jekyll build` (`JEKYLL_ENV=production`) and
served from the `_site/` directory (see `netlify.toml`). `.github/workflows/ci.yml`
builds the site on every push and pull request to catch regressions.

## License

[MIT](LICENSE) © Brian C. Keegan — Anticipation Consulting.
