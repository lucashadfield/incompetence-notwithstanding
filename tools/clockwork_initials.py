#!/usr/bin/env python3
"""Dense mechanical initials: Goudy-level busy-ness, machinery instead of vines.

NOT PART OF THE SITE BUILD. Nothing in layouts/ or assets/ references this, and
no generated SVG is committed under static/ or assets/ — the live site uses
Goudy Initialen. This is kept because the drawing rules took several passes to
get right and are worth not re-deriving. To look at the output:

    python3 tools/clockwork_initials.py /tmp/initials     # writes A.svg … Z.svg

Requires fontTools (apt install python3-fonttools) and tools/fonts/
playfair-display-normal.woff2, which is here rather than in assets/ so it is
never shipped to a browser.

Goudy Initialen is a filled block with the letter and a floral field knocked out
in white. Same construction here, procedurally: a rubric block, the letter
reversed out of it in a Didone (Playfair Display, wght 700), and the remaining
field packed with meshed gears, belts, springs, pipework, rivets and hatching —
drawn as hairlines so it reads as texture at 84px and resolves into mechanism
when you look closely.

Letter avoidance uses fontTools' PointInsidePen against the real outline, so it
works for every glyph rather than for a hand-tuned 'I'.
"""
import math
import pathlib
import random
import sys

from fontTools.pens.pointInsidePen import PointInsidePen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

BOX = 100.0
FONT = str(pathlib.Path(__file__).parent / "fonts" / "playfair-display-normal.woff2")

_cache = {}


def _font():
    if "f" not in _cache:
        f = TTFont(FONT)
        f = instantiateVariableFont(f, {"wght": 700}, inplace=False)
        _cache["f"] = f
    return _cache["f"]


class Letter:
    """A glyph mapped into the block, with an inside() test in block coords."""

    def __init__(self, char, height=0.62, cy=0.5):
        f = _font()
        self.gs = f.getGlyphSet()
        self.name = f.getBestCmap()[ord(char)]
        g = f["glyf"][self.name]
        self.x0, self.y0, self.x1, self.y1 = g.xMin, g.yMin, g.xMax, g.yMax
        self.s = (BOX * height) / (self.y1 - self.y0)
        self.tx = BOX / 2 - self.s * (self.x0 + self.x1) / 2
        self.ty = BOX * cy + self.s * (self.y0 + self.y1) / 2
        pen = SVGPathPen(self.gs)
        self.gs[self.name].draw(pen)
        self.d = pen.getCommands()

    def bbox(self):
        return (self.tx + self.s * self.x0, self.ty - self.s * self.y1,
                self.tx + self.s * self.x1, self.ty - self.s * self.y0)

    def inside(self, x, y):
        gx = (x - self.tx) / self.s
        gy = (self.ty - y) / self.s
        pen = PointInsidePen(self.gs, (gx, gy))
        self.gs[self.name].draw(pen)
        return pen.getResult()

    def clear(self, x, y, r, margin=1.6, samples=10):
        """True if a disc of radius r at (x,y) misses the letter."""
        if self.inside(x, y):
            return False
        rr = r + margin
        for i in range(samples):
            a = 2 * math.pi * i / samples
            if self.inside(x + rr * math.cos(a), y + rr * math.sin(a)):
                return False
            if self.inside(x + rr * 0.55 * math.cos(a), y + rr * 0.55 * math.sin(a)):
                return False
        return True

    def svg(self, fill):
        return (f'<g transform="translate({self.tx:.2f},{self.ty:.2f}) scale({self.s:.4f},{-self.s:.4f})">'
                f'<path d="{self.d}" fill="{fill}"/></g>')


def _slot(x, y, r, ang):
    """Screw slot at a random angle, so a field of bolt heads doesn't read as a
    row of identical minus signs."""
    dx, dy = r * 0.72 * math.cos(ang), r * 0.72 * math.sin(ang)
    return (f'<line x1="{x - dx:.2f}" y1="{y - dy:.2f}" x2="{x + dx:.2f}" y2="{y + dy:.2f}" '
            f'stroke="currentColor" stroke-width="0.8"/>')


def gear(cx, cy, r, teeth, sw=1.0, phase=0.0, filled=False, bg="#8A2F1F", col="currentColor"):
    """Toothed wheel. filled=True gives a solid disc with the rim, spokes and
    hub knocked back out in the ground colour — that is what carries the white
    mass a floral initial gets from its leaves."""
    if filled:
        pts = []
        tip, root = r * 1.17, r * 0.93
        for i in range(teeth):
            a = 2 * math.pi * i / teeth + phase
            step = 2 * math.pi / teeth
            for ang, rr in ((a, root), (a + step * 0.16, tip), (a + step * 0.34, tip), (a + step * 0.5, root)):
                pts.append(f"{cx + rr * math.cos(ang):.2f},{cy + rr * math.sin(ang):.2f}")
        out = [f'<polygon points="{" ".join(pts)}" fill="{col}"/>',
               f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r * 0.66:.2f}" fill="{bg}"/>']
        n = 5 if r > 7 else 4
        for i in range(n):
            a = 2 * math.pi * i / n + phase
            out.append(f'<line x1="{cx:.2f}" y1="{cy:.2f}" '
                       f'x2="{cx + r * 0.66 * math.cos(a):.2f}" y2="{cy + r * 0.66 * math.sin(a):.2f}" '
                       f'stroke="{col}" stroke-width="{max(1.0, r * 0.13):.2f}"/>')
        out.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{max(1.1, r * 0.22):.2f}" fill="{col}"/>')
        out.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{max(0.5, r * 0.09):.2f}" fill="{bg}"/>')
        return "".join(out)
    pts = []
    tip = r * 1.17
    root = r * 0.93
    for i in range(teeth):
        a = 2 * math.pi * i / teeth + phase
        step = 2 * math.pi / teeth
        for ang, rr in ((a, root), (a + step * 0.16, tip), (a + step * 0.34, tip), (a + step * 0.5, root)):
            pts.append(f"{cx + rr * math.cos(ang):.2f},{cy + rr * math.sin(ang):.2f}")
    out = [f'<polygon points="{" ".join(pts)}" fill="none" stroke="{col}" '
           f'stroke-width="{sw}" stroke-linejoin="round"/>']
    out.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r * 0.72:.2f}" fill="none" '
               f'stroke="{col}" stroke-width="{sw * 0.8:.2f}"/>')
    hub = max(r * 0.2, 0.9)
    out.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{hub:.2f}" fill="{col}"/>')
    if r > 5:
        n = 4 if r < 9 else 6
        for i in range(n):
            a = 2 * math.pi * i / n + phase
            out.append(f'<line x1="{cx + hub * 1.1 * math.cos(a):.2f}" y1="{cy + hub * 1.1 * math.sin(a):.2f}" '
                       f'x2="{cx + r * 0.7 * math.cos(a):.2f}" y2="{cy + r * 0.7 * math.sin(a):.2f}" '
                       f'stroke="{col}" stroke-width="{sw * 0.7:.2f}"/>')
    return "".join(out)


def belt(g1, g2, sw=0.8):
    """Two outer tangents between wheels: a drive belt."""
    (x1, y1, r1), (x2, y2, r2) = g1, g2
    dx, dy = x2 - x1, y2 - y1
    d = math.hypot(dx, dy) or 1
    ux, uy = dx / d, dy / d
    nx, ny = -uy, ux
    out = []
    for sign in (1, -1):
        out.append(f'<line x1="{x1 + sign * r1 * nx:.2f}" y1="{y1 + sign * r1 * ny:.2f}" '
                   f'x2="{x2 + sign * r2 * nx:.2f}" y2="{y2 + sign * r2 * ny:.2f}" '
                   f'stroke="currentColor" stroke-width="{sw}"/>')
    return "".join(out)


def spring(x1, y1, x2, y2, coils=6, amp=1.8, sw=0.8, col="currentColor"):
    dx, dy = x2 - x1, y2 - y1
    d = math.hypot(dx, dy) or 1
    ux, uy = dx / d, dy / d
    nx, ny = -uy, ux
    pts = []
    steps = coils * 8
    for i in range(steps + 1):
        t = i / steps
        off = amp * math.sin(2 * math.pi * coils * t)
        pts.append(f"{x1 + dx * t + nx * off:.2f},{y1 + dy * t + ny * off:.2f}")
    return (f'<polyline points="{" ".join(pts)}" fill="none" stroke="{col}" '
            f'stroke-width="{sw}" stroke-linejoin="round"/>')


def chain(x1, y1, x2, y2, sw=0.65, link=2.4, col="currentColor"):
    """A run of oval links: reads as chain drive at size, as texture below it."""
    dx, dy = x2 - x1, y2 - y1
    d = math.hypot(dx, dy) or 1
    n = max(2, int(d / link))
    ang = math.degrees(math.atan2(dy, dx))
    out = []
    for i in range(n):
        t = (i + 0.5) / n
        cx, cy = x1 + dx * t, y1 + dy * t
        rx = link * 0.62 if i % 2 == 0 else link * 0.42
        ry = link * 0.34 if i % 2 == 0 else link * 0.5
        out.append(f'<ellipse cx="{cx:.2f}" cy="{cy:.2f}" rx="{rx:.2f}" ry="{ry:.2f}" '
                   f'transform="rotate({ang:.1f} {cx:.2f} {cy:.2f})" fill="none" '
                   f'stroke="{col}" stroke-width="{sw}"/>')
    return "".join(out)


def linkage(x1, y1, x2, y2, sw=0.9, col="currentColor"):
    """Con-rod: tapered bar with a pin boss at each end."""
    out = [f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
           f'stroke="{col}" stroke-width="{sw * 1.4:.2f}" stroke-linecap="round"/>']
    for (px, py) in ((x1, y1), (x2, y2)):
        out.append(f'<circle cx="{px:.2f}" cy="{py:.2f}" r="1.5" fill="none" '
                   f'stroke="{col}" stroke-width="{sw:.2f}"/>')
    return "".join(out)


def hatch(x, y, w, h, sw=0.45, step=2.0, ang=45.0):
    """Diagonal hatching: fills dead ground so the block reads as dense as a
    floral initial rather than a red field with wheels on it."""
    out = []
    t = math.tan(math.radians(ang))
    k = int((w + h * t) / step)
    for i in range(k + 1):
        x0 = x - h * t + i * step
        out.append(f'<line x1="{x0:.2f}" y1="{y + h:.2f}" x2="{x0 + h * t:.2f}" y2="{y:.2f}" '
                   f'stroke="currentColor" stroke-width="{sw}" opacity=".85"/>')
    return (f'<g clip-path="url(#c{int(x)}_{int(y)})">'
            f'<clipPath id="c{int(x)}_{int(y)}"><rect x="{x:.2f}" y="{y:.2f}" '
            f'width="{w:.2f}" height="{h:.2f}"/></clipPath>{"".join(out)}</g>')


def pipe(x1, y1, x2, y2, sw=1.0, gap=1.5, col="currentColor"):
    """Double-line pipe run with a flange at each end."""
    dx, dy = x2 - x1, y2 - y1
    d = math.hypot(dx, dy) or 1
    nx, ny = -dy / d * gap, dx / d * gap
    out = [f'<line x1="{x1 + nx:.2f}" y1="{y1 + ny:.2f}" x2="{x2 + nx:.2f}" y2="{y2 + ny:.2f}" '
           f'stroke="{col}" stroke-width="{sw * 0.75:.2f}"/>',
           f'<line x1="{x1 - nx:.2f}" y1="{y1 - ny:.2f}" x2="{x2 - nx:.2f}" y2="{y2 - ny:.2f}" '
           f'stroke="{col}" stroke-width="{sw * 0.75:.2f}"/>']
    for (px, py) in ((x1, y1), (x2, y2)):
        out.append(f'<line x1="{px + nx * 1.9:.2f}" y1="{py + ny * 1.9:.2f}" '
                   f'x2="{px - nx * 1.9:.2f}" y2="{py - ny * 1.9:.2f}" '
                   f'stroke="{col}" stroke-width="{sw}"/>')
    return "".join(out)


def initial(char, seed=None, style="block", frame=True, density=1.0):
    """style: 'block' = white machinery reversed out of a rubric ground (Goudy's
    construction); 'open' = rubric machinery on the page, no ground."""
    rng = random.Random(seed if seed is not None else ord(char) * 7919)
    L = Letter(char, height=0.60 if style == "block" else 0.66)
    inset = 4.5 if frame else 1.0
    parts = []

    # ── composition ──────────────────────────────────────────────────────
    # Not a random scatter: a gear TRAIN runs round the block on a fixed ring,
    # each wheel meshing with the last, which gives the field the border
    # structure a floral initial has. The letter keeps a clear zone; only
    # small wheels are allowed to fill inside the ring.
    wheels = []
    LETTER_CLEAR = 2.6          # every wheel stands this far off the outline

    def free_for(x, y, r, clear=None, tight=0.97):
        if not L.clear(x, y, r, margin=LETTER_CLEAR if clear is None else clear):
            return False
        return all(math.hypot(x - wx, y - wy) >= (r + wr) * tight for (wx, wy, wr) in wheels)

    ring = 9.0                   # centre-line of the train, in from the edge
    rw, rh = BOX - 2 * ring, BOX - 2 * ring
    per = 2 * (rw + rh)

    def on_ring(d):
        d %= per
        if d < rw:
            return ring + d, ring
        d -= rw
        if d < rh:
            return BOX - ring, ring + d
        d -= rh
        if d < rw:
            return BOX - ring - d, BOX - ring
        d -= rw
        return ring, BOX - ring - d

    d = rng.uniform(0, per)
    travelled, prev_r = 0.0, None
    while travelled < per - 2:
        r = rng.choice([6.4, 5.8, 5.2, 4.6, 4.0])
        x, y = on_ring(d)
        if free_for(x, y, r):
            wheels.append((x, y, r))
            step = (prev_r or r) * 0.0 + r * 1.92     # next wheel meshes with this one
            prev_r = r
        else:
            step = 3.4                                 # blocked by the letter: skip on
        d += step
        travelled += step

    # a few mid-size wheels inside the ring first, so the interior has some
    # hierarchy rather than a confetti of identical small ones
    for r in [6.0, 5.4, 4.8, 4.2] * 2:
        for _ in range(200):
            x = rng.uniform(inset + r + 1, BOX - inset - r - 1)
            y = rng.uniform(inset + r + 1, BOX - inset - r - 1)
            if free_for(x, y, r, tight=1.0):
                wheels.append((x, y, r))
                break

    # then small wheels in whatever the train and the letter leave
    for r in [3.6, 3.2, 3.0, 2.8, 2.6, 2.4, 2.2, 2.0, 1.9, 1.8, 1.7] * 3:
        for _ in range(240):
            x = rng.uniform(inset + r + 1, BOX - inset - r - 1)
            y = rng.uniform(inset + r + 1, BOX - inset - r - 1)
            if free_for(x, y, r, tight=1.0):
                wheels.append((x, y, r))
                break

    bg = "var(--rubric,#8A2F1F)" if style == "block" else "var(--paper,#FCFAF4)"
    for i, (x, y, r) in enumerate(wheels):
        teeth = max(7, min(22, int(r * 1.5)))
        # Only small and mid wheels are ever solid. A large filled disc is the
        # heaviest mark in the block and it out-competes the letter — that is
        # what made C, E, F, G and U read as a gear with a letter beside it.
        solid_p = 0.62 if r <= 5.0 else (0.40 if r <= 7.0 else 0.0)
        parts.append(gear(x, y, r, teeth, sw=0.95 if r > 6 else 0.8, phase=rng.uniform(0, 1),
                          filled=(rng.random() < solid_p), bg=bg))

    # belts between wheel pairs that are near but not meshing
    pairs = []
    for i, a in enumerate(wheels):
        for b in wheels[i + 1:]:
            d = math.hypot(a[0] - b[0], a[1] - b[1])
            if (a[2] + b[2]) * 1.35 < d < (a[2] + b[2]) * 2.6 and min(a[2], b[2]) > 3.2:
                pairs.append((d, a, b))
    pairs.sort()
    for _, a, b in pairs[:3]:
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        if L.clear(mx, my, 1.0, margin=1.0):
            parts.append(belt(a, b))

    # springs, pipe runs and rivets in whatever is left
    def free(x, y, r=2.2):
        if not L.clear(x, y, r, margin=1.2):
            return False
        return all(math.hypot(x - wx, y - wy) > wr + r + 0.8 for (wx, wy, wr) in wheels)

    tries, springs, pipes = 0, 0, 0
    while tries < 400 and (springs < 2 or pipes < 2):
        tries += 1
        x1 = rng.uniform(inset + 2, BOX - inset - 2)
        y1 = rng.uniform(inset + 2, BOX - inset - 2)
        ang = rng.choice([0, math.pi / 2, math.pi / 4, -math.pi / 4])
        ln = rng.uniform(12, 24)
        x2, y2 = x1 + ln * math.cos(ang), y1 + ln * math.sin(ang)
        if not (inset < x2 < BOX - inset and inset < y2 < BOX - inset):
            continue
        if not all(free(x1 + (x2 - x1) * t, y1 + (y2 - y1) * t, 2.4) for t in (0, .25, .5, .75, 1)):
            continue
        if springs < 2 and rng.random() < 0.5:
            parts.append(spring(x1, y1, x2, y2, coils=max(4, int(ln / 3.4))))
            springs += 1
        elif pipes < 2:
            parts.append(pipe(x1, y1, x2, y2))
            pipes += 1

    # chains and con-rods between remaining wheel pairs
    extras = 0
    for _, a, b in pairs[3:]:
        if extras >= 3:
            break
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        if not L.clear(mx, my, 1.2, margin=1.0):
            continue
        if extras % 2 == 0:
            parts.append(chain(a[0], a[1], b[0], b[1]))
        else:
            parts.append(linkage(a[0], a[1], b[0], b[1]))
        extras += 1

    # washers and bolt heads in the leftover ground: small filled marks, which
    # raise the white ratio without adding another line pattern
    washers = 0
    for _ in range(900):
        if washers >= 16:
            break
        x = rng.uniform(inset + 2, BOX - inset - 2)
        y = rng.uniform(inset + 2, BOX - inset - 2)
        rr = rng.choice([1.5, 1.9, 2.3, 2.8])
        if not L.clear(x, y, rr + 0.6, margin=0.9):
            continue
        if not all(math.hypot(x - wx, y - wy) > wr * 1.1 + rr + 0.6 for (wx, wy, wr) in wheels):
            continue
        wheels.append((x, y, rr))
        if rng.random() < 0.5:
            parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{rr:.2f}" fill="currentColor"/>'
                         f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{rr * 0.42:.2f}" fill="{bg}"/>')
        else:
            parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{rr:.2f}" fill="none" '
                         f'stroke="currentColor" stroke-width="0.8"/>'
                         + _slot(x, y, rr, rng.uniform(0, math.pi)))
        washers += 1

    rivets = 0
    for _ in range(500):
        if rivets >= 10:
            break
        x = rng.uniform(inset + 1.5, BOX - inset - 1.5)
        y = rng.uniform(inset + 1.5, BOX - inset - 1.5)
        if free(x, y, 1.6):
            parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="0.85" fill="currentColor"/>')
            rivets += 1

    # ── interlace ────────────────────────────────────────────────────────
    # Goudy's vines pass over and under the letter, so the letter looks
    # overgrown rather than framed. Same trick here: a run is drawn once in
    # full behind the letter, then the stretch that crosses a stroke is
    # redrawn on top over a fat keyline in the ground colour, which is what
    # makes a white element read as passing in front of a white letter.
    front = []

    def spans(x1, y1, x2, y2, n=140):
        ins = [L.inside(x1 + (x2 - x1) * i / n, y1 + (y2 - y1) * i / n) for i in range(n + 1)]
        out, start = [], None
        for i, v in enumerate(ins):
            if v and start is None:
                start = i
            elif not v and start is not None:
                out.append((start, i - 1))
                start = None
        if start is not None:
            out.append((start, n))
        return [(a / n, b / n) for a, b in out if b - a >= 3]

    def halo_line(x1, y1, x2, y2, w=4.6):
        return (f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{bg}" '
                f'stroke-width="{w}" stroke-linecap="round"/>')

    runs = 0

    def axis_pairs():
        out = []
        for i, a in enumerate(wheels):
            for b in wheels[i + 1:]:
                if min(a[2], b[2]) < 3.6:
                    continue
                dx, dy = abs(a[0] - b[0]), abs(a[1] - b[1])
                d = math.hypot(dx, dy)
                if d < 34:
                    continue
                if dy < 5.5 or dx < 5.5:          # horizontal or vertical shaft
                    out.append((-d, a, b))
        out.sort()
        return out

    for _, a, b in axis_pairs():
        if runs >= 1:
            break
        x1, y1, x2, y2 = a[0], a[1], b[0], b[1]
        sp = spans(x1, y1, x2, y2)
        if not sp:
            continue
        kind = "chain" if rng.random() < 0.5 else "linkage"
        draw = {"chain": chain, "linkage": linkage}[kind]
        parts.append(draw(x1, y1, x2, y2))
        t0, t1 = max(sp, key=lambda t: t[1] - t[0])
        pad = 0.04
        t0, t1 = max(0.0, t0 - pad), min(1.0, t1 + pad)
        sx, sy = x1 + (x2 - x1) * t0, y1 + (y2 - y1) * t0
        ex, ey = x1 + (x2 - x1) * t1, y1 + (y2 - y1) * t1
        front.append(halo_line(sx, sy, ex, ey, 3.2))
        front.append(draw(sx, sy, ex, ey))
        runs += 1

    # two or three small wheels mounted half on the letter, in front of it
    mounted, attempts = 0, 0
    while mounted < 1 and attempts < 500:
        attempts += 1
        r = rng.uniform(3.0, 4.2)
        x = rng.uniform(inset + r, BOX - inset - r)
        y = rng.uniform(inset + r, BOX - inset - r)
        if L.inside(x, y):
            continue
        ring = [L.inside(x + (r + 1.2) * math.cos(2 * math.pi * k / 12),
                         y + (r + 1.2) * math.sin(2 * math.pi * k / 12)) for k in range(12)]
        if not (2 <= sum(ring) <= 7):      # must straddle an edge, not sit on top of one
            continue
        front.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r * 1.2:.2f}" fill="{bg}"/>')
        front.append(gear(x, y, r, max(8, int(r * 1.6)), sw=0.9, phase=rng.uniform(0, 1), bg=bg))
        mounted += 1

    ground = ""
    if style == "block":
        ground = f'<rect width="{BOX}" height="{BOX}" fill="currentColor"/>'
        if frame:
            ground += (f'<rect x="2.2" y="2.2" width="{BOX - 4.4}" height="{BOX - 4.4}" fill="none" '
                       f'stroke="var(--paper,#FCFAF4)" stroke-width="1.1"/>')
        body = f'<g color="var(--paper,#FCFAF4)">{"".join(parts)}</g>'
        letter = L.svg("var(--paper,#FCFAF4)")
        # a thin keyline of ground colour around the letter keeps it readable
        # where machinery crowds it
        letter = (f'<g><g transform="translate({L.tx:.2f},{L.ty:.2f}) scale({L.s:.4f},{-L.s:.4f})">'
                  f'<path d="{L.d}" fill="none" stroke="currentColor" stroke-width="{4.6 / L.s:.2f}"/></g>'
                  f'{letter}</g>')
    else:
        if frame:
            ground = (f'<rect x="2.2" y="2.2" width="{BOX - 4.4}" height="{BOX - 4.4}" fill="none" '
                      f'stroke="currentColor" stroke-width="1.1"/>')
        body = "".join(parts)
        letter = L.svg("currentColor")

    front_g = (f'<g color="var(--paper,#FCFAF4)">{"".join(front)}</g>' if style == "block"
               else "".join(front))
    return (f'<svg class="mech" viewBox="0 0 {int(BOX)} {int(BOX)}" aria-hidden="true">'
            f'{ground}{body}{letter}{front_g}</svg>')


if __name__ == "__main__":
    out = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/initials")
    out.mkdir(parents=True, exist_ok=True)
    style = sys.argv[2] if len(sys.argv) > 2 else "block"
    for ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        svg = initial(ch, style=style)
        # the demo SVGs reference CSS custom properties for their two colours;
        # standalone files need literals
        svg = svg.replace("var(--rubric,#8A2F1F)", "#8A2F1F").replace("var(--paper,#FCFAF4)", "#FCFAF4")
        svg = svg.replace('color="#FCFAF4"', 'style="color:#FCFAF4"')
        (out / f"{ch}.svg").write_text(
            svg.replace('<svg class="mech"', '<svg xmlns="http://www.w3.org/2000/svg"'))
    print(f"wrote 26 initials to {out}")
