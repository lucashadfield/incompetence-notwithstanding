# Incompetence Notwithstanding

A blog about language models and adjacent things. Static site built with
[Hugo](https://gohugo.io/) on a bespoke theme — no third-party theme, nothing
to override. The look: a printed book. Warm paper, Spectral for body copy,
Cormorant Garamond for display, black text with a rubric red for structure, an
ornate Goudy initial at the head of every post, and **no images anywhere**.

## Layout

```
content/
  _index.md                 the home page — statement, portrait, about copy
  posts/                    one page bundle per post
    first-post/index.md
  posts/_index.md           section stub — `build: {render: never}`, /posts/ is not a page
  archives.md               /archives/   (layout: archives)
  search.md                 /search/     (layout: search)
tools/
  clockwork_initials.py     mechanical drop-cap generator — NOT part of the build
  fonts/                    a font the generator needs; never shipped to a browser
layouts/
  baseof.html               shell: header, main, footer, search overlay
  home.html                 statement, portrait, about copy, contents list
  posts/single.html         post: centred title block, drop cap
  single.html               standalone pages (none at present; kept for the next one)
  list.html                 tag term pages (contents list)
  taxonomy.html             /tags/
  archives.html             year-grouped index
  search.html               /search/ page
  404.html
  index.json                search index (JSON output of the home page)
  home.rss.xml              the feed — overrides Hugo's built-in RSS
  robots.txt                robots + Sitemap: line, both derived from baseURL
  _markup/                  render hooks: image, link, heading
  _partials/
    head, header, footer, scripts, icon
    ornament.html           the fleuron, as inline SVG
    corner.html             the vine flourish on a contents plate
    entry.html              one framed plate in a contents list (replaced tile.html)
    social.html             the contact bar, centred under the about copy: one
                            row of hairline-divided cells, address then marks
    post_nav.html           prev / next, titles only
    func/roman.html         roman numeral for the contents list
    func/tagname.html       tag display name (acronym-safe)
assets/
  css/parts/*.css           concatenated in filename order → one stylesheet
  js/site.js                search, back-to-top, code copy, email copy
  js/vendor/fuse.basic.min.js
  img/portrait.jpg          the one photograph on the site — in assets/, not a
                            page bundle, because branch-bundle resources are
                            copied into public/ referenced or not
  img/favicon.svg           the Goudy "I" block
  img/favicon-32.png        raster fallback, rasterised from the SVG
  img/apple-touch-icon.png  180×180, paper-filled (iOS composites on black)
  fonts/*.woff2             Spectral, Cormorant Garamond, Space Mono
static/
  fonts/goudy/*.ttf         26 single-glyph initial files (see below)
hugo.toml
```

## Running locally

Hugo **extended** ≥ 0.146 (0.165.0 in use, at `/usr/local/bin/hugo`).

```bash
hugo server --port 1314              # dev server, live reload
hugo                                 # production build → public/
```

On the tailnet, bind and pin the baseURL or Hugo rewrites asset URLs to
localhost:

```bash
hugo server --bind 0.0.0.0 --port 1314 \
  --baseURL "http://lucas-server.axolotl-major.ts.net:1314/" --buildDrafts
```

## Deploying

`hugo` emits a static `public/`. Point any file server at it. No runtime, no
database.

**The domain lives in exactly one place: `baseURL` on line 6 of `hugo.toml`.**
Canonicals, `og:url`, the feed, the sitemap, `robots.txt` and every absolute
asset URL derive from it, and nothing else in the repo hardcodes a host. When
the real domain is up it is a one-line edit. For a one-off build against a
different host, override it instead of editing:

```bash
hugo -b "https://example.com/"
```

## Design system

Everything lives in `assets/css/parts/`, split by concern and concatenated in
filename order (`00-tokens` → `90-media`). Tokens are the only place colours
and type sizes are defined.

| Token | Value | Used for |
|---|---|---|
| `--paper` | `#FCFAF4` | page background |
| `--paper-2` | `#F7F3E9` | masthead and footer band. Mirrored in the hardcoded `theme-color` meta in `_partials/head.html` — change both |
| `--paper-raised` / `--sunken` / `--wash` | `#FFFDF7` / `#F2EEE4` / `#F7F2E6` | panels, figure backing, hover |
| `--ink` / `--ink-2` / `--ink-3` | `#1E1C1A` / `#4B4741` / `#8C857B` | text, secondary, labels |
| `--rubric` | `#8A2F1F` | **structure**: initials, kickers, ornaments, list markers, rules |
| `--link` | `#2F5D57` | running-text links only, so they do not read as rubrication |

Two colours of ink, as a hand-press would have them. This replaced a pastel
palette (`--mist`, `--peach`, `--sage`, `--sand`, `--stone`) and a teal accent
that were median-cut sampled from ten cover illustrations. There are no
illustrations any more, so there was nothing left for that palette to agree
with; red is the historically correct second colour and it is what makes the
initial work.

Type: **Spectral** for body copy at `1.0625rem/1.66`, **Cormorant Garamond**
for display (page titles, headings, entry titles, archive rows), **Space Mono**
for code only. No sans-serif anywhere. Every label is `.u-micro`: serif,
uppercase, `0.72rem`, `0.17em` tracking.

**One type scale, and nothing outside it.** No rule sets a bare rem size for
type that has a level; if a new element needs a size, it takes a token or the
scale gets a new one.

| Token | Value | Used by |
|---|---|---|
| `--t-h1` | `clamp(1.55rem, 1.25rem + 1.1vw, 2.1rem)` | every page title: the homepage statement, post titles, list/archive/tag/search titles, 404 |
| `--t-h2` | `1.55rem` | prose `h2`, contents-plate titles, archive year labels |
| `--t-h3` | `1.25rem` | prose `h3`, archive rows, tag names, prev/next, search results and the search field |
| `--t-h4` | `0.95rem` | the uppercase subhead inside prose |
| `--t-lead` | `1.075rem` | standfirst |
| `--t-body` | `1.0625rem` | body copy |
| `--t-small` | `0.85rem` | entry blurbs, tables, footnotes, figure captions, the email address |
| `--t-code` | `0.8125rem` | code blocks |
| `--t-micro` | `0.72rem` | every label, kicker and meta line |
| `--t-mast` | `clamp(1.25rem, 1rem + 1vw, 1.6rem)` | the wordmark |

`--t-h1` used to be `clamp(2.1rem → 3.1rem)` for post titles while the homepage
statement had its own smaller ramp, so the two pages disagreed by a full step.
The post title now takes the homepage size, and `--t-h1` at 2.1rem is the
largest type on the site.

Layout tokens: `--wrap: 52rem` (masthead, footer, index pages) and `--measure:
35rem` (the reading column). Article-width pages get the measure by overriding
`--wrap` on their own parts — `.post__runhead` / `.post__head` / `.post__main`
/ `.post__foot` and `.page-single__grid` — which is why they can all still
share `.wrap`.

There is no separate `/about/` page: the home page carries the statement, a
round portrait and the about copy from `content/_index.md`, then the contents
list. One page fewer to maintain, and the first thing a reader sees is who is
writing.

The masthead block is **one column with the portrait floated right**, capped
at 45rem: wide enough that the statement sits on one line beside the portrait,
narrow enough that the copy closing under it stays readable. `shape-outside:
circle(50%)` makes the copy follow the circle rather than the square box it
sits in, and `.hero__inner::after` clears the float before the ornament. Below
560px the float is dropped and the portrait centres, because a 144px float
leaves a three-word measure beside it.

It was a two-column grid before, which left a column of empty paper beside the
second and third paragraphs. Note `.hero .hero__prose` has to out-specify
`.prose`, which caps itself at `--measure` and loads later in the cascade. It was one centred column with a 2.6rem title, which put
the contents list below the fold on a laptop.

Navigation lives in exactly one place, the site header: menu entries, Search
and RSS. `_partials/footer.html` is an empty end block — a band of paper with
a rule. It used to repeat the same five links and a copyright line, which was
all it did.

The masthead sets each word's initial one size up (`.wordmark__cap`, applied by
a `replaceRE` in `_partials/header.html`) so the uppercase wordmark reads as
caps and small caps. Cormorant Garamond has no true small caps and synthesised
ones look like shrunken capitals.

A contents entry is a framed plate: hairline double frame, a vine flourish in
each corner (`_partials/corner.html`, one SVG rotated four times), the title in
the display face. Hover darkens the plate to `--sunken` with a 1px box-shadow
in the same colour, so the 4px gutter between the two frame rules fills too,
drops the frame and flourishes to grey, and moves the rubric onto the title.
The first version lifted to `--paper-raised`, which is a 3% step off the page
and read as no change at all. Below 520px the flourishes are hidden; at 40px on
a ~290px plate they crowd the text instead of framing it.

The body column is centre-axis: title block, kicker, standfirst, ornaments,
contents entries and archive year labels all centre; body copy is ragged right,
never justified. CSS hyphenation is not good enough for justified setting at
this measure.

Ornaments are **inline SVG** (`_partials/ornament.html`), not Unicode
dingbats: U+2766 and its relatives are missing from both text faces and fell
back to whatever the OS had, which rendered as a blob.

Light only, deliberately. No theme toggle to maintain.

## The drop cap

Goudy Initialen — Frederic Goudy, 1913, for the Cloister types — in rubric red
at the head of every post. Turned on by `prose--dropcap` on the body div in
`layouts/posts/single.html`; all the CSS is in `assets/css/parts/05-initials.css`.

Three details do the work, and it will look broken if any is changed casually:

- **One file per letter.** `static/fonts/goudy/GoudyInitialen-A.ttf` … `-Z.ttf`,
  each holding a single glyph, declared as 26 `@font-face` rules with a
  one-codepoint `unicode-range`. A page fetches only the initial it uses: ~8 KB
  instead of the 420 KB set. They live in `static/` rather than `assets/`
  because the URLs are written by hand in CSS rather than resolved by Hugo,
  which also means a baseURL with a path prefix would need them rewritten.
- **`initial-letter: 3`**, with a `float` fallback for Firefox behind
  `@supports`. The float version needs its size and leading eyeballed;
  `initial-letter` gets cap-height alignment and line sinking right for free.
  Below 420px it drops to 2 lines, or the sunk cap eats a third of the column.
- **`font-weight: 400; font-synthesis: none`** on the `::first-letter`. The
  glyph's ink *is* the block and the letter and filigree are counters, so
  synthetic bold fills the white lines in and the initial renders as a plain
  red slab. This is also why the favicon works: filling the same path in rubric
  on a paper ground gives the printed look directly.

The favicon is that same Goudy `I`. `assets/img/favicon.svg` is the glyph
outline filled `#8A2F1F` on a `#FCFAF4` rect; the PNG fallbacks are rasterised
from it with headless Chrome, because PIL cannot render SVG:

```bash
# serve assets/img, point Chrome at a page containing <img src="favicon.svg" width=180>
google-chrome --headless=new --disable-gpu --no-sandbox --hide-scrollbars \
  --window-size=180,180 --screenshot=/tmp/fav180.png http://127.0.0.1:8907/fav-preview.html
python3 -c "from PIL import Image; im=Image.open('/tmp/fav180.png').convert('RGB'); \
  im.save('assets/img/apple-touch-icon.png'); \
  im.resize((32,32), Image.LANCZOS).save('assets/img/favicon-32.png')"
```

Licensing: Goudy Initialen is a Dieter Steffmann digitisation, distributed
free for personal use rather than under a libre licence — fine for a personal
blog. Spectral, Cormorant Garamond and Space Mono are OFL.

### tools/clockwork_initials.py

A procedural alternative to Goudy, kept in the repo and **deliberately not
wired into the build** — nothing in `layouts/` or `assets/` references it and no
generated SVG is committed, so a browser never downloads any of it.

```bash
python3 tools/clockwork_initials.py /tmp/initials          # A.svg … Z.svg, rubric block
python3 tools/clockwork_initials.py /tmp/initials open     # no ground, red on paper
```

It draws Goudy's *construction* with machinery instead of vines: a rubric
block, a Playfair Display letter reversed out of it, and the field packed with
meshed gears, drive belts, chains, con-rods, springs, washers and bolt heads.
At 84px it reads as a dense ornamented block; the mechanism only resolves above
~168px. Roughly 66 KB of SVG per letter, 16 KB gzipped. Needs `fontTools`
(`apt install python3-fonttools`).

What took several passes to get right, and is worth not re-deriving:

- **Solid discs only below r7.** A large filled gear is the heaviest mark in
  the block and beats the letter for attention; C, E, F, G and U read as a gear
  with a letter next to it until large wheels were forced to hairline outlines.
- **A gear train on a fixed ring, not a random scatter.** Wheels walk a
  rectangular path 9 units in from the edge at `1.92r` spacing so consecutive
  wheels mesh, skipping forward where the letter is in the way. Then two graded
  interior passes (mid-size, then small) so the field has hierarchy.
- **Letter clearance of 2.6 units**, enforced by sampling a ring of points
  against the real outline with fontTools' `PointInsidePen`, which is what makes
  it work for all 26 glyphs rather than a hand-packed `I`.
- **Interlacing** is what stops the letter looking framed rather than
  overgrown: a run is drawn in full *behind* the letter, then the stretch that
  crosses a stroke is redrawn on top over a fat keyline in the ground colour.
  A crossing must be a shaft between two train wheels that face each other
  across the letter (axis-aligned within 5.5 units, ≥34 apart), and crossings
  within 17 units of the block centre are rejected — a run through the middle of
  a stem reads as a strikethrough. Springs are excluded from crossings; a coil
  over a letter looks like a scribble.

## No images (except one)

The exception is `assets/img/portrait.jpg`, set as a book sets a frontispiece:
144px, round, double-ruled with an ink hairline inside and a rubric ring
outside, and slightly desaturated. Floated right in the masthead block with the
copy running around it; the contact bar is centred underneath.

Otherwise there is no cover art, no tile grid, no `og:image`, and the feed carries no
enclosure. Removing it took out `_partials/poster.html`,
`_partials/func/cover_resource.html`, `_partials/tile.html`,
`assets/css/parts/50-tiles.css`, the `[[cascade]]` block that kept 2.5 MB
source PNGs out of `public/`, and the five palette tints.

What remains: `_markup/render-image.html` still renders an in-post
`![alt](file.png)` as a `.fig` figure with a webp srcset, so a chart or a
screenshot inside a post works. Nothing decorative goes in.

Link previews are therefore text-only (`twitter:card` is always `summary`). If
that ever matters, the fix is a generated type-only card, not a return to
illustration.

The cover library (`covers/`, ten 2400px PNGs), its Midjourney prompt recipe
(`cover-prompts.md`), the 61 MB of `uploads/` they were staged through and
`tools/upload_server.py`, which existed to get phone photos onto the box, are
all deleted. Anything needed is in git history at `0716990^`.

## Editing

- New post:
  ```bash
  hugo new content content/posts/my-post/index.md
  ```
- Frontmatter that matters: `title`, `date`, `tags`, `description` (the
  standfirst under the title *and* the meta description), `summary` (the
  contents-list blurb).
- Homepage statement: `intro` in `hugo.toml`. The last word is dimmed by a
  `replaceRE` in `home.html`.
- Contents numbering: `_partials/func/roman.html` turns the position into a
  roman numeral (1–99). Hugo has no such function, and a contents page numbered
  1, 2, 3 looks like a list of search results.
- Nav: `[[menu.main]]` blocks in `hugo.toml`; the header appends Search itself.
  There is no `/posts/` page — the archive is the full index, and
  `content/posts/_index.md` carries `build: {render: never, list: never}`.
- Search: fuse.js over `/index.json`, loaded lazily on first use. Press `/` or
  `⌘K` anywhere, or use `/search/`. Don't remove `home = [..., "JSON"]` from
  `[outputs]` or the index disappears.
- Tag display names: `[params.tagNames]` in `hugo.toml`, keyed by the
  lower-cased tag. Hugo title-cases taxonomy terms, which turns `llms` into
  `Llms`; every surface goes through `_partials/func/tagname.html`, including a
  term page's own `<h1>`, which has to use `.Data.Term` rather than `.Title`.
- Contact links: `[[params.social]]` in `hugo.toml` (`name`, `url`, `icon`).
  Turn the row on for a page with `social: true` — currently the home page. `mailto:` entries become
  the address row; everything else becomes an icon cell. Icons live in
  `_partials/icon.html`: GitHub and Letterboxd are
  [Simple Icons](https://simpleicons.org/) (CC0); LinkedIn and the envelope are
  [Bootstrap Icons](https://icons.getbootstrap.com/) (MIT) — Simple Icons
  dropped the LinkedIn mark on trademark request. LinkedIn renders at 16px
  against the others' 18px: a solid square carries more ink and reads a size
  larger at matched dimensions.
- Feed: `layouts/home.rss.xml`. Posts only, full `.Content`. Hugo's built-in
  RSS enumerates every regular page, so About / Archive / Search were showing
  up as items.

## Gotchas

- Posts dated in the future (UTC) are silently excluded from the build.
- `hardWraps = true` is **deliberate** — it is what makes one-line-per-sentence
  staccato passages render as written. The cost is that any hard-wrapped
  paragraph renders with `<br>` at each source newline, so **write markdown one
  long line per paragraph**. Do not reflow content files at 80 columns. It also
  means the sunk initial is beside three short lines rather than three full
  ones; that staircase is intentional, not a bug.
- `::first-line` is unusable for a small-caps opening: it styles the *rendered*
  line, so a narrow viewport cuts it mid-sentence. If that treatment is ever
  wanted, wrap the first sentence in a span with a `replaceRE` over `.Content`.
- Cascade uses `[cascade.target]`, not `[cascade._target]` — the underscore
  spelling was deprecated in 0.156 and warns on every build.
- `.Language.LanguageCode` was deprecated in 0.158; use `.Language.Locale`.
- Hugo lower-cases TOML param keys. `layouts/_partials/scripts.html` maps them
  back to Fuse's camelCase explicitly — without that, `ignoreLocation` is never
  set and search only matches text near the start of a document.
- Don't put `wrap` and `prose` on the same element: `.wrap` sets
  `margin-inline: auto`, so the narrower `prose` max-width centres the text
  column. Nest a `.prose` div inside a `.wrap` div instead.
- The heading anchor's `#` is drawn with CSS `::after` on purpose, so it never
  ends up in `.Plain` and pollutes the search index.
