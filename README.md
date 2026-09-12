# Incompetence Notwithstanding

A blog about language models and adjacent things. Static site built with
[Hugo](https://gohugo.io/) on a bespoke theme — no third-party theme, nothing
to override. The look: calm pastels on warm paper, one typeface, square
corners, a 1-bit dither for texture, and 90s-flavoured cover illustrations that
carry all the colour.

## Layout

```
content/
  posts/                    one page bundle per post
    first-post/             index.md + cover.svg (page resources)
  _index.md                 section stub — `build: {render: never}`, /posts/ is not a page
  about.md                  /about/
  archives.md               /archives/   (layout: archives)
  search.md                 /search/     (layout: search)
tools/upload_server.py      phone → box image upload, for covers
layouts/
  baseof.html               shell: header, main, footer, search overlay
  home.html                 hero statement + tiles
  posts/single.html         post: full-bleed cover, single centred column
  single.html               standalone pages (about)
  list.html                 tag term pages (tile grid)
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
    social.html             the "Elsewhere" module (right column)
    poster.html             cover image (raster srcset, pastel fallback)
    tile.html               homepage / list card
    post_nav.html           prev / next
    func/cover_resource.html
    func/tagname.html       tag display name (acronym-safe)
assets/
  css/parts/*.css           concatenated in filename order → one stylesheet
  js/site.js                nav, search, reading progress, code copy
  js/vendor/fuse.basic.min.js
  img/favicon.svg           the wordmark mark: ink square + accent-teal offset shadow
  img/favicon-32.png        raster fallback (transparent)
  img/apple-touch-icon.png  180×180, paper-filled (iOS composites on black)
  fonts/*.woff2             self-hosted Space Grotesk + Space Mono
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
  --baseURL "http://pi-server.axolotl-major.ts.net:1314/" --buildDrafts
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
| `--paper` | `#FAF6EA` | page background — warm cream a touch above the cover art's own ground (`#F0EDD6`), so illustrations read as slightly deeper panels rather than dissolving into the page. Mirrored in the hardcoded `theme-color` meta in `_partials/head.html` — change both |
| `--paper-raised` | `#FFFDF6` | panels, blockquotes, search overlay |
| `--sunken` | `#EFEADA` | footer, image backing |
| `--mist` `--peach` `--sage` `--sand` `--stone` | `#A9CFD2` `#E4C0A0` `#C3D3C3` `#DCCFAE` `#C2C6B2` | tints: hover shadows, tag chips, empty covers |
| `--accent` | `#26706C` | the single accent: rules, links, hovers, progress bar. 5.4:1 on paper |
| `--mark` / `--mark-shadow` | `#1F2E2B` / `#26706C` | logo square and its hard offset shadow: an ink chip casting a teal ghost |
| `--ink` / `--ink-2` / `--ink-3` | `#1F2E2B` / `#4E635E` / `#8A9A94` | text, secondary, labels |

The palette is sampled from the ten covers in `covers/`, not chosen
independently: median-cut quantisation over all ten images gives water blue,
peach, sage, sand and olive stone as the recurring families, and deep
slate-green as the outline ink.

The accent is the poolside cover's deepest water tone. Alternatives were
measured and passed over: night-window blue-teal `#33595D` (7.1:1, too close to
the current accent to be worth the change), foliage green `#1F4331` (10.2:1, so
dark that links stop reading as links), wood brown `#755D46` (5.7:1 but only
21% saturation, reads muddy), and terracotta `#8C4F2C` (5.9:1) — which was
tried site-wide and pulled back to the logo alone. Nothing in the art is warm,
dark and saturated at once, so a warm accent has to be extrapolated rather than
sampled, and at link-text scale it fought the covers instead of complementing
them.

`--mark` is a separate pair so the logo can be recoloured without touching
links. Two versions were rejected before the current one: solid accent with a
pale-water shadow (teal on teal on cream — the mark had nothing to do), and
terracotta on pale water (too much colour for a 10px square, and it read as a
bathroom tile). It is now ink `#1F2E2B` with a teal `#26706C` ghost — a chip
dark enough to hold its shape at 10px, with the accent doing the offset. Hover
lightens the ghost to `--mist` and closes the offset by a pixel.

Type: **Space Grotesk** for everything — display, headings, body, UI — and
**Space Mono**, its sibling, for labels, numbers and code. One family, no
serif/sans pairing. Self-hosted woff2 (~55 KB), preloaded, no external
requests. Every label uses `.u-micro`: 11px mono, uppercase, `0.14em` tracking.

Layout tokens: `--wrap: 1240px` (page), `--measure: 42rem` (the reading
column), and `--cover-ar: 21 / 9`, the single place every cover crop is
defined. Post pages have no TOC rail: body copy is one centred column.

There is **one** measure, not two. `--measure` is both the article wrap and the
`.prose` cap, so a rule drawn at wrap width always lands exactly where the text
column ends. Article-width pages get it by overriding `--wrap` on their own
parts — `.post__head` / `.post__main` / `.post__foot` and `.page-single__grid` —
which is why they can all still share `.wrap`. Pages that keep the full 1240px
wrap (home, tag lists, archive) rely on the `.prose` max-width instead.

A standalone page carrying `social: true` gets a second column:
`.page-single__grid--aside` widens `--wrap` to `--measure + 18.5rem` and grids
it `[--measure] 3.5rem [15rem]`, centred as a unit, collapsing to one column
below 1000px. The text column stays exactly `--measure`, so the accent rule
still ends where the copy does. The trade-off is that `/about/` sits further
left than a post does — the pair is centred, not the prose. The top padding
lives on the grid rather than the header so the module's label starts level
with the page kicker. This replaced a `--measure: 35rem` / `--post-wrap: 42rem`
split plus a `.prose--narrow` class of `62ch`: three different measures, which
left the accent rule on `/about/` running ~500px past the end of the text.

Other rules the design leans on: `--radius: 0` (nothing is rounded), a `--pixel:
4px` grid that hard offset shadows and accent bars snap to, and `.dither` — a
4px checkerboard at 6% opacity, the only texture in the system.

Light only, deliberately. The palette is the identity and there is no theme
toggle to maintain.

## Editing

- New post:
  ```bash
  hugo new content content/posts/my-post/index.md
  ```
  Page bundle, so the cover lives next to `index.md`.
- Cover image — frontmatter:
  ```yaml
  cover:
    image: "cover.png"        # raster only — png / jpg / webp
    alt: "Optional alt text"
  ```
  It becomes the full-bleed post header and the homepage tile, resized to webp
  with a srcset automatically. A post with no cover falls back to a flat pastel
  block, not a grey box.
- Homepage statement: `intro` / `introKicker` in `hugo.toml`. The homepage has
  no decorative art of its own — the tiles carry it.
- Favicon: `assets/img/favicon.svg` is the same two squares as
  `.wordmark__mark` (ink `#1F2E2B` square, accent-teal `#26706C` hard
  shadow offset by 3/16 of the canvas). The PNG fallbacks are generated from
  the same geometry with PIL — regenerate them if the mark changes:
  ```python
  from PIL import Image, ImageDraw
  def draw(size, bg):
      img = Image.new("RGBA", (size, size), bg); d = ImageDraw.Draw(img)
      s, off, x0 = round(size*0.625), round(size*0.1875), round(size*0.09375)
      d.rectangle([x0+off, x0+off, x0+off+s-1, x0+off+s-1], fill=(0x26,0x70,0x6C,255))  # --mark-shadow
      d.rectangle([x0, x0, x0+s-1, x0+s-1], fill=(0x1F,0x2E,0x2B,255))  # --mark
      return img
  draw(32, (0,0,0,0)).save("assets/img/favicon-32.png")
  draw(180, (0xFA,0xF6,0xEA,255)).convert("RGB").save("assets/img/apple-touch-icon.png")
  ```
- Nav: `[[menu.main]]` blocks in `hugo.toml`. There is no `/posts/` page — the
  archive is the full index, and `content/posts/_index.md` carries
  `build: {render: never, list: never}` so the section list page is never
  emitted. Posts keep their `/posts/<slug>/` URLs; "all posts" links point at
  `/archives/`. Hugo removed the old `_build` spelling in 0.145 — it must be
  `build:`, or the build fails with a deprecation error.
- Search: fuse.js over `/index.json`, loaded lazily on first use. Press `/` or
  `⌘K` anywhere, or use `/search/`. Don't remove `home = [..., "JSON"]` from
  `[outputs]` or the index disappears. `/search/` carries `noindex: true` and
  `sitemap.disable` — a search box is not a search result.
- Tag display names: `[params.tagNames]` in `hugo.toml`, keyed by the
  lower-cased tag. Hugo title-cases taxonomy terms, which turns `llms` into
  `Llms`; anything in the map wins, everything else falls back to title-casing.
  Every surface goes through `_partials/func/tagname.html` — the taxonomy page,
  the tile chips, the post kicker and the archive meta previously rendered the
  same tag three different ways.
- Elsewhere links: `[[params.social]]` in `hugo.toml` (`name`, `url`, `icon`,
  `tint`). Turn the module on for a page with `social: true` in front matter;
  `single.html` then renders `_partials/social.html` into a right-hand column.
  It is chrome, not body copy, so it is rendered from the layout rather than a
  shortcode inside `.prose` — an earlier shortcode version inherited the prose
  list markers and link underlines.

  One box, two rows: `mailto:` entries become the address row (Space Mono, the
  address itself rather than the word "Email"), everything else becomes an
  icon-only cell in a hairline-divided strip. `tint` is one of the five palette
  families and fills that cell on hover — no brand colours, four foreign
  palettes would swamp the page. Icons live in
  `_partials/icon.html`: brand and contact marks are **filled**, unlike the
  stroked utility icons, because a stroked Octocat does not exist. GitHub and
  Letterboxd are [Simple Icons](https://simpleicons.org/) (CC0); LinkedIn and
  the envelope are [Bootstrap Icons](https://icons.getbootstrap.com/) (MIT) —
  Simple Icons dropped the LinkedIn mark on trademark request. LinkedIn renders
  at 16px against the others' 18px: a solid square carries more ink and reads a
  size larger at matched dimensions.
- Feed: `layouts/home.rss.xml`. Posts only, full `.Content`, and the cover as
  both an `<enclosure>` and the lead image. Hugo's built-in RSS enumerates every
  regular page, so About / Archive / Search were showing up as items.
- Social cards: `og:image` is a 1200×630 JPEG cropped from the cover by
  `_partials/head.html`, never the original. The `[[cascade]]` block in
  `hugo.toml` sets `build.publishResources = false` on `/posts/**` so the ~2.5 MB
  source PNGs stop being copied into `public/` — derivatives still publish,
  because their `.RelPermalink` is called. One post's output went 2.9 MB → 405 KB.

## Cover art

The library is `covers/` — ten 2400×1024 PNGs, the only illustrations the site
uses. They are the source of the CSS palette, not the other way round:
`cartographers-table`, `clock-tower-mechanism`, `darkroom-bench`,
`flat-rooftop`, `robot-arm-bench`, `electronics-bench`, `observatory-dome`,
`home-office-night`, `books-and-bookshelf`, `poolside-desk`. Copy one into a
post bundle as `cover.png`. The originals (3376×1440, 5–9 MB each) stay in the
gitignored `uploads/`; `covers/` holds the 2400-wide re-encodes, still above
the 2200px hero srcset step, which cuts the set from ~62 MB to ~34 MB.

The generation-ready prompts live in `cover-prompts.md` — 28 of them, one
recipe, one scene sentence each. Read that file before writing a new one; the
notes at its top record which clauses are keeping the frame and the cartoon out.

Covers are **raster only** — PNG, JPG or WebP, no SVG. 21:9 landscape, 1680×720
or larger. Tiles, feature tile and prev/next thumbnails all crop to `--cover-ar`
(21:9); the post header is thinner still at 16:5 and capped at
`min(30vh, 300px)`, so it never owns the first screen. Hugo resizes them to
webp with a srcset automatically. A post with no cover gets a flat pastel block
keyed off its title hash, so the grid never breaks.

Composition: subject centred, nothing important within 8% of any edge (the post
header crops ~30% vertically off a 21:9 source), low contrast — the tile title
sits directly beneath the image.

The covers are generated with Midjourney (v7). Prompt recipe: write one dense
object list as the first sentence, then keep the rest verbatim so every cover
matches. Hex codes are the site tokens; pair each with its colour name, since
models read the name and treat the hex as a nudge.

> Cheerful full-bleed high-key risograph illustration of **[SUBJECT]** in a
> gentle three-quarter view: **[DENSE OBJECT LIST, chunky and rounded, with a
> different palette colour named for each major object's body, every screen
> switched on and filled with a flat glowing field of coral pink or mint
> green]**. **[SECOND LIST filling the upper third: shelf, pegboard, hanging
> cables, one plant described by leaf shape in flat pale sage, lit lamp]**.
> Objects overlap in a dense friendly cluster, busy but calm, filling the canvas
> edge to edge on warm cream paper. 1990s Japanese software packaging art
> crossed with a cosy children's picture book. Loose hand-inked outlines with
> slightly wobbly varying line weight, chunky toy-like proportions, soft rounded
> corners. Outlines kept hairline-thin in a soft muted slate, never black and
> never heavy. Saturated riso inks: warm cream paper #FAF6EA, water blue
> #A9CFD2, soft peach #E4C0A0, sage green #C3D3C3, warm sand #DCCFAE, plenty of
> deep teal #26706C. Flat two-tone shading where the shadow tone is a
> warmer tint of the object's own ink, never grey. Fine subtle halftone texture
> on small areas only, most surfaces left as clean flat colour. All fills in the
> bright upper half of the value range, no large dark areas anywhere. Warm cream
> light washing in from the left, sunny, cheerful and inviting. `--ar 21:9
> --stylize 350 --chaos 0 --no thick outlines, black outlines, heavy ink, coarse
> dithering, dense halftone, dark halftone, dark shadows, grey shadows, olive,
> olive green, dark green foliage, charcoal, near-black fills, muddy shading,
> low-key lighting, dim, blank screens, black screens, off screens, border,
> frame, margin, caption, credit line, signature, text, lettering, gibberish
> text, faux lettering, scribbles, labels, numbers, logos, watermark, people,
> faces, photorealism, 3D render, technical drawing, blueprint, CAD,
> ruler-straight lines, architectural elevation, perspective grid, gloss, neon,
> bloom, lens flare, grey, greyscale, desaturated, washed out, drab, dull,
> sepia, gloomy, dusty, abandoned, decay, e-waste`

Midjourney needs the warmth spelled out. Left to its defaults it returns a
cold, washed-out, half-empty frame full of dead grey hardware. What counters it:

- **No `--style raw`.** Raw strips exactly the charm this style needs. Default
  mode at `--stylize 250` is warmer; `--chaos 0` makes the four grid variants
  converge so you're choosing a composition rather than rolling dice.
- **Don't stack desaturators.** `pastel` + `muted` + `soft` + `low contrast`
  compound into grey. Say `saturated riso inks`, keep the palette hexes, and
  put `grey, greyscale, desaturated, washed out, drab` in `--no`.
- **Assign colours to objects by name.** MJ won't spend a palette it isn't told
  where to use — teal boards, sky-blue cables, peach disk boxes. Say
  `plenty of` teal, not `tiny accents of`, or it disappears entirely.
- **Fill the upper third.** "Generous negative space above the objects" reads
  as abandonment at 21:9. Give it a pegboard, a shelf, a plant, a lit lamp.
- **State the mood.** `cheerful`, `well-loved`, `cosy and inviting`, `every
  screen lit`, and `gloomy, dusty, abandoned, decay, e-waste` in `--no`. A
  "cramped workshop with tangled cables" is an e-waste pile to MJ.
- **Pin the SHADOW tone, not just the palette.** This is the root of the
  "depressing undercurrent" that survives every other fix. Palette hexes only
  control the lit side; MJ chooses the second tone of "flat two-tone shading"
  itself and always picks desaturated dark grey-olive, so every object gets a
  muddy dark side. Write `the shadow tone is a warmer tint of the object's own
  ink, never grey — halftone dots in coral pink and powder blue only`.
- **Say `high-key` and constrain the value range.** `All fills in the bright
  upper half of the value range, no large dark areas anywhere`, with `dark
  shadows, grey shadows, charcoal, near-black fills, dark halftone, muddy
  shading, low-key lighting, dim` in `--no`. Cheerful vs sad in flat
  illustration is mostly value distribution and shadow hue, not palette.
- **Every screen must be explicitly lit and coloured**, or MJ fills CRTs
  near-black: `every screen switched on and filled with a flat glowing field of
  coral pink or mint green`, plus `blank screens, off screens` in `--no`.
- **Foliage ignores hexes.** Even `drawn in flat sage green #C3D3C3` comes back
  naturalistic dark olive and becomes the darkest mass in frame. Use one plant,
  describe it by shape (`simple rounded leaves in flat pale sage`), and exclude
  `olive, olive green, dark green foliage`.
- **Coarse dither and heavy outlines are the last two dark masses.** Dithering
  over large areas lowers apparent value everywhere, so use `fine subtle
  halftone texture on small areas only, most surfaces left as clean flat
  colour` and exclude `coarse dithering, dense halftone`. Likewise drop the
  `#1F2E2B` hex from the outline clause — the token anchors MJ to near-black
  and it draws the line thick, doubling it in vents and pegboard holes. Say
  `outlines hairline-thin in a soft muted slate, never black and never heavy`
  and exclude `thick outlines, black outlines, heavy ink`. Both cost some riso
  character; there is no version that keeps heavy dither and reads sunny.
- **If the mood survives all of the above, it's the subject, not the render.**
  `beige`, `repair bench` and `case open` describe a repair-shop autopsy, and
  the more faithfully MJ renders "beige 90s PC" the more it reads as
  equipment disposal. Gemini escaped it because its cases were pink and blue
  toys. Describe a workbench mid-project rather than a machine opened up.
- **`seen straight on` produces a technical elevation** — ruler-straight uniform
  hairlines, dimensionally accurate cases, zero charm. Use `gentle
  three-quarter view` plus `loose hand-inked outlines with slightly wobbly
  varying line weight, chunky toy-like proportions, soft rounded corners`, and
  exclude `technical drawing, blueprint, CAD, ruler-straight lines,
  architectural elevation, perspective grid`. Superseded in practice: the ten
  covers in `covers/` are all straight-on, and the flat elevation reads as
  deliberate once the whole set shares it and every scene is dense with
  objects. Consistency across the set does the work the three-quarter view was
  meant to do.
- **Colour the object bodies, not just the props.** The Gemini covers gave each
  machine its own case colour (one pink, one powder blue, one sand). MJ leaves
  every chassis beige and spends the palette on screens and small items, which
  reads cold even with the right hexes. Name a body colour per object.
- **`--stylize` is the charm dial.** 350 for hand-drawn wobble, 250 for tidier
  work, ~100 only for flat vector. It spends the extra latitude on linework.
- **Don't write `Studio Ghibli`.** It pulls painterly watercolour and anime
  faces, both of which fight the flat riso print. `cosy children's picture
  book` gets the warmth with no render-style collision.
- **Never say `poster`.** With `packaging art` alongside it, MJ renders a
  framed print: cream margin on all four sides plus a bottom caption bar full
  of garbled faux-lettering. Say `full-bleed illustration ... filling the
  entire canvas edge to edge` and put the whole `border, frame, margin, white
  edge, caption, credit line, signature` family in `--no`. Killing the caption
  bar removes most of the fake text as a side effect.
- **Warm the largest surface.** MJ defaults the back wall to grey-blue, which
  is the single coldest thing in frame because it has the most area. Name it:
  `warm cream and pale peach back wall`.
- **Pin organic objects to a hex.** Houseplants and wood come out
  naturalistic olive/brown unless told `drawn in flat sage green #C3D3C3`.
- Prose negatives are ignored — "no glow" reads as *glow*. Everything goes
  after `--no`. Note `glow` itself can't go there: it kills the lit screens and
  the lamp. Use `bloom, lens flare` instead.
- `--ar` is mandatory; MJ will not infer the frame from "wide 2:1 landscape
  composition", so drop that clause from the prose.
- Style consistency across covers comes from `--sref <url of an existing cover>
  --sw 100`, not from adjectives — point it at one of the ten in `covers/`,
  which are all `--sref`-locked to each other. Drop `--sw` to ~60 if it starts
  copying the reference layout instead of its style.
- Generate at 21:9 and the tiles show it uncropped; only the post header crops,
  and it crops vertically, not horizontally. The current set is 3376×1440
  (2.34:1) straight out of MJ, which crops cleanly.

Subjects that work in this style: a cluttered 90s desk; a lone server rack; a
bench of half-disassembled machines; stacked marked-up printouts; cassette
tapes and minidiscs; a keyboard from directly above; cables running off-frame.

Getting images off a phone: `python3 tools/upload_server.py 8787 uploads`
serves a mobile upload form on the tailnet at
`http://pi-server.axolotl-major.ts.net:8787/`. Files land in `uploads/`
(gitignored); slug-rename it into `covers/` at 2400 wide, then copy it into the
post bundle as `cover.png` and add the `cover:` frontmatter. Kill the server
afterwards.

## Gotchas

- Posts dated in the future (UTC) are silently excluded from the build.
- `hardWraps = true` is **deliberate** — it is what makes one-line-per-sentence
  staccato passages render as written. The cost is that any hard-wrapped
  paragraph renders with `<br>` at each source newline, so **write markdown one
  long line per paragraph**. Do not reflow content files at 80 columns.
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
