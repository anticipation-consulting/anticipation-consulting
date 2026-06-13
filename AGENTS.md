# AGENTS.md

Orientation for AI agents and human contributors working in this repository.
It summarizes the site architecture, design choices, mission and values, and
brand identity, and points to the single sources of truth for each. Read this
before making changes, and keep it current when those things change.

> **This is the project's canonical context file.** `CLAUDE.md` and the
> READMEs point here. If you change the mission, tagline, design system, or
> structure, update this file in the same change.

---

## Mission & values

**Mission** — *We find questions you didn't know to ask and deliver evidence
designed to be challenged.*

**Tagline** (short form, used in lockups/slogan) — *What you didn't know to ask.*

The tagline is the first clause of the mission: foresight (the questions you
didn't know to ask) plus rigor (evidence built to withstand scrutiny). Both are
defined once in `_config.yml` (`mission`, `tagline`) and surfaced through
templates — never hard-code a divergent wording.

**What the practice is.** A boutique data science and AI consultancy led by
**Brian C. Keegan, Ph.D.**, a computational social scientist (faculty at CU
Boulder; training at MIT, Northwestern, Northeastern, Harvard Business School).
One doctoral-trained scientist does the work end to end — framing, code, and
conclusion — for high-stakes decisions that can't be redone.

**Values / commitments** (the standard on every engagement):

- **Honesty over confidence** — an honest answer, not just a confident one. If
  the data can't answer the question, the client hears that first.
- **Reproducible by default** — every result ships with code and documented data
  lineage that the client (or a third party) can re-run. No black boxes.
- **Documented for scrutiny** — work is written as if an opposing expert will
  read it, because sometimes one will. Evidence is *designed to be challenged*.
- **Independent judgment** — no platform to sell, no product to push. The only
  thing on offer is the analysis.

**Content honesty rule (applies to all copy & assets).** No fabricated clients,
logos, metrics, testimonials, or case outcomes. Claims about credentials and
experience must be true. This is a hard constraint — prefer an empty section to
an invented one.

---

## Architecture

A static site built with **Jekyll 4** using a bespoke, self-contained theme (no
external theme gem). Plain HTML + Liquid, one stylesheet, one script.

```
.
├── _config.yml              # Site config + single source of truth for mission/tagline/SEO defaults
├── _data/
│   └── services.yml         # The nine services — single source of truth
├── _includes/
│   ├── head.html            # Per-page SEO: meta, Open Graph, Twitter, fonts, CSS, JSON-LD include
│   ├── header.html          # Sticky nav + wordmark
│   ├── footer.html          # Site footer (renders site.mission)
│   └── schema/              # JSON-LD partials: home, services, service, about, contact
├── _layouts/
│   └── default.html         # The single shared page shell
├── assets/
│   ├── site.css             # Design system: palette tokens, layout, every component
│   ├── site.js              # Network background, mobile nav, palette persistence, scroll reveals
│   └── favicon.svg          # Tilted Didot "A"
├── images/                  # og-image.png, headshot
├── index.html · about.html · services.html · expertise.html · insights.html · contact.html
├── services/data-science.html   # Flagship service detail page
├── sitemap.xml · robots.txt # Generated from page front matter
├── brand/                   # Reproducible brand kit (see brand/README.md)
├── .github/workflows/ci.yml # Builds the site on every push / PR
├── README.md                # Human-facing project readme
└── AGENTS.md / CLAUDE.md    # Agent/contributor context (excluded from the build)
```

- **Data-driven services.** The nine services are defined once in
  `_data/services.yml` and drive (1) the home-page grid, (2) the Services
  overview page (tiles + anchored sections), and (3) the `ItemList` JSON-LD.
  Edit the YAML, not three pages.
- **SEO & structured data.** `_includes/head.html` emits per-page `<title>`,
  meta description, canonical, robots, Open Graph + Twitter cards, and includes
  the matching `_includes/schema/<page.schema>.html` JSON-LD. Driven by each
  page's front matter (`seo_title`, `description`, `og_*`, `schema`, `keywords`).
- **Build & deploy.** `JEKYLL_ENV=production bundle exec jekyll build` → `_site/`,
  served via Netlify (`netlify.toml`). CI (`.github/workflows/ci.yml`) builds on
  every push and PR to catch regressions. `AGENTS.md`, `CLAUDE.md`, `README.md`,
  and `LICENSE` are listed under `exclude` so they don't publish.

---

## Design system & choices

- **Palettes.** Three palettes are defined as `html[data-palette="signal|ink|field"]`
  blocks of CSS custom properties at the top of `assets/site.css`. **Signal**
  (cool charcoal + electric blue) is the default; **Ink** (warm copper) and
  **Field** (forest + ochre) are alternates. `site.js` persists the visitor's
  choice (the floating "tweaks" panel). All component colors reference tokens
  (`--paper`, `--ink`, `--accent`, `--line`, …) so the whole site re-themes from
  those blocks — never hard-code a hex in a component.
- **Typography.** Spectral (serif display) · IBM Plex Sans (body) · IBM Plex Mono
  (eyebrows/labels) · Cormorant Garamond + GFS Didot (wordmark). Loaded from
  Google Fonts in `head.html`.
- **Logo & favicon.** A tilted GFS Didot "A" (electric blue, −30°) set against
  "nticipation Consulting", so the mark itself is the leading "A".
- **Network background.** `site.js` injects one fixed, full-viewport
  `<canvas id="net-bg">`: a drifting node-link field — triangular nodes in the
  brand triad (blue/copper/green), gradient links that fade with distance, and
  links that reach toward the cursor. It is palette-aware, pauses when the tab is
  hidden, and renders **statically** under `prefers-reduced-motion`. It sits at
  **one consistent low opacity (`#net-bg { opacity: 0.4 }`)** so it reads as a
  faint, uniform texture behind every section rather than competing with copy —
  this is the single knob for background visibility. Dark `.ink-section` bands
  carry their own static `hero-motif` canvas.
- **Layout & components.** Content sits in `.wrap` / `.wrap-narrow` containers in
  full-width `.section` bands (transparent, so the network shows through),
  with `.ink-section` dark bands for emphasis (testimony, CTAs). Cards, metrics,
  feature lists, steps, and the nav/footer are all token-driven components in
  `site.css`.
- **Accessibility.** Semantic landmarks, `aria-hidden` on decorative canvases,
  full `prefers-reduced-motion` support, and color tokens chosen for contrast.

---

## Brand identity

Full guidelines and the reproducible kit live in **`brand/`** (see
`brand/README.md`). Essentials:

- **Marks.** The "A" is GFS Didot rotated −30°; the wordmark sets "NTICIPATION"
  in Cormorant Garamond SemiBold (tracked) + "Consulting" in Cormorant Light.
- **Palette.** Brand blue `#2f6fe0`, copper `#b5783f`, green `#2f7d54` (the
  network triad); ink `#1a1d22`, paper `#f7f6f2`.
- **Tagline lockup.** Brand banners set the **short tagline** ("WHAT YOU DIDN'T
  KNOW TO ASK") under the wordmark — the full mission is intentionally reserved
  for prose, as it's too long for a tracked lockup.
- **Voice.** Direct, understated, precise, and intellectually honest. Plain
  strong nouns and verbs; em-dashes for rhythm. Avoid hype and filler
  ("leverage", "cutting-edge", "empower", "synergy", "data-driven insights").
  Be honest about uncertainty; never oversell what the numbers support.

---

## Working in this repo

**Local development** (requires Ruby + Bundler):

```bash
bundle install                                   # install dependencies
bundle exec jekyll serve                         # http://localhost:4000
JEKYLL_ENV=production bundle exec jekyll build    # build into _site/
```

Always run a production build before committing — CI runs the same build.

**Single sources of truth** — change these, not their many render sites:

| Concern | Source of truth |
| --- | --- |
| Mission, tagline, SEO defaults | `_config.yml` (`mission`, `tagline`, `description`) |
| The nine services | `_data/services.yml` |
| Design tokens / palettes / components | `assets/site.css` |
| Network background, nav, palette, reveals | `assets/site.js` |
| Brand kit (marks, banners, palette) | `brand/generate_assets.py` → `brand/dist/` |

**Conventions**

- Match the existing voice and the content honesty rule above.
- Keep mission/tagline wording consistent everywhere; surface via `site.mission`
  / `site.tagline` rather than re-typing the string.
- Don't add an external Jekyll theme or heavy JS framework — the site is
  deliberately self-contained (one CSS file, one JS file).
- Color in components must reference palette tokens, not literal hexes.
- Regenerate brand assets only via `brand/generate_assets.py` so the kit stays
  reproducible and consistent with the site.

## References

- `README.md` — project overview, structure, local dev, deployment.
- `brand/README.md` — brand kit, marks, palette, mission/voice/values, usage.
- `_config.yml` — mission, tagline, and SEO defaults.
- `assets/site.css` / `assets/site.js` — the design system and behavior.
