import sys
try:
    from PIL import Image, ImageDraw, ImageFont
except Exception as exc:  # pragma: no cover
    raise SystemExit("pillow required: " + repr(exc))

# deterministic, no randomness, no network, no wall-clock usage

BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# palette (paper #F7F1E3, ink #14213D, accent red, navy, teal, gold)
PAPER = (247, 241, 227)
INK = (20, 33, 61)
RED = (193, 39, 45)
NAVY = (27, 42, 74)
TEAL = (14, 124, 123)
GOLD = (217, 164, 65)
WHITE = (255, 255, 255)

W = 1024
H = 1024

_font_cache = {}

def font(path, size):
    key = (path, size)
    f = _font_cache.get(key)
    if f is None:
        f = ImageFont.truetype(path, size)
        _font_cache[key] = f
    return f

def text_w(d, text, f):
    return d.textlength(text, font=f)

def wrap_text(d, text, f, max_width):
    words = text.split(" ")
    lines = []
    cur = ""
    for w_ in words:
        trial = (cur + " " + w_).strip() if cur else w_
        if text_w(d, trial, f) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines or [""]

def draw_wrapped(d, xy, lines, f, fill, leading):
    x, y = xy
    w = 0
    for ln in lines:
        d.text((x, y), ln, font=f, fill=fill)
        y += leading
    return y - leading

def rrect(d, box, r, fill=None, outline=None, width=1):
    d.rounded_rectangle([int(box[0]), int(box[1]), int(box[2]), int(box[3])], radius=int(r), fill=fill, outline=outline, width=int(width))

def circle(d, center, rad, fill=None, outline=None, width=1):
    d.ellipse([int(center[0] - rad), int(center[1] - rad), int(center[0] + rad), int(center[1] + rad)],
              fill=fill, outline=outline, width=int(width))

def diamond(d, center, half, fill=None):
    d.polygon([(int(center[0]), int(center[1] - half)),
               (int(center[0] + half), int(center[1])),
               (int(center[0]), int(center[1] + half)),
               (int(center[0] - half), int(center[1]))], fill=fill)

def triangle(d, top, base_half, hgt, fill, flip=False):
    x, y = top
    if flip:
        d.polygon([(int(x - base_half), int(y)), (int(x + base_half), int(y)), (int(x), int(y + hgt))], fill=fill)
    else:
        d.polygon([(int(x - base_half), int(y)), (int(x + base_half), int(y)), (int(x), int(y - hgt))], fill=fill)

def arc_span(d, c, r, a0, a1, width, fill):
    d.arc([int(c[0] - r), int(c[1] - r), int(c[0] + r), int(c[1] + r)], start=a0, end=a1,
          width=int(width), fill=fill)

def pie(d, c, r, a0, a1, fill):
    d.pieslice([int(c[0] - r), int(c[1] - r), int(c[0] + r), int(c[1] + r)], start=a0, end=a1, fill=fill)

def line(d, *args):
    # Support both calling conventions:
    # 1. line(d, (x1, y1), (x2, y2), width, fill)  -- two points
    # 2. line(d, (x1, y1, x2, y2), width, fill)    -- single 4-tuple
    if len(args) == 4:
        p1, p2, width, fill = args
        d.line([(int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1]))], width=int(width), fill=fill)
    elif len(args) == 3:
        box, width, fill = args
        if isinstance(box, (tuple, list)) and len(box) == 4:
            x1, y1, x2, y2 = box
            d.line([(int(x1), int(y1)), (int(x2), int(y2))], width=int(width), fill=fill)
        else:
            raise ValueError("Invalid arguments to line()")
    else:
        raise ValueError("Invalid arguments to line()")

def rect(d, box, fill=None, outline=None, width=1):
    d.rectangle([int(box[0]), int(box[1]), int(box[2]), int(box[3])], fill=fill, outline=outline, width=int(width))

def dot(d, c, r=3):
    d.ellipse([int(c[0] - r), int(c[1] - r), int(c[0] + r), int(c[1] + r)], fill=INK)

def icon_lead(d, x, y, s):
    # three overlapping seals with connecting beam = the three-way meeting
    cols = [RED, GOLD, NAVY]
    for i in range(3):
        dx = (i - 1) * s * 0.28
        cx, cy = x + s * 0.5 + dx, y + s * 0.5
        circle(d, (cx, cy), s * 0.26, fill=cols[i])
    line(d, (x + s * 0.5 - s * 0.3, y + s * 0.5), (x + s * 0.5 + s * 0.3, y + s * 0.5),
         max(2, s * 0.05), INK)
    dot(d, (x + s * 0.5, y + s * 0.5), s * 0.06)

def icon_justice(d, x, y, s):
    # balanced scales = the ICJ ruling
    line(d, (x + s * 0.5, y + s * 0.15), (x + s * 0.5, y + s * 0.62), s * 0.06, INK)
    line(d, (x + s * 0.5, y + s * 0.62), (x + s * 0.33, y + s * 0.62), s * 0.06, INK)
    line(d, (x + s * 0.5, y + s * 0.62), (x + s * 0.67, y + s * 0.62), s * 0.06, INK)
    line(d, (x + s * 0.24, y + s * 0.6), (x + s * 0.76, y + s * 0.6), s * 0.05, INK)
    tx = [x + s * 0.3, x + s * 0.7]
    for cx in tx:
        line(d, (cx - s * 0.13, y + s * 0.40), (cx, y + s * 0.6), max(2, s * 0.022), INK)
        line(d, (cx + s * 0.13, y + s * 0.40), (cx, y + s * 0.6), max(2, s * 0.022), INK)
        pie(d, (cx, y + s * 0.42), s * 0.13, 0, 180, GOLD)

def icon_weather(d, x, y, s):
    # cyclone = spiral bands around a centre
    c = (x + s * 0.5, y + s * 0.5)
    pie(d, c, s * 0.4, 0, 180, TEAL)
    for i, rr in enumerate((s * 0.33, s * 0.26, s * 0.19)):
        arc_span(d, c, rr, 180 + i * 18, 180 + 176, max(2, s * 0.05), NAVY)
    circle(d, c, s * 0.1, fill=RED)

def icon_space(d, x, y, s):
    # deep-space probe with dish, signal waves and star field
    ox, oy = x, y
    dot(d, (ox + s * 0.18, oy + s * 0.2), max(2, s * 0.018))
    dot(d, (ox + s * 0.3, oy + s * 0.12), max(2, s * 0.018))
    dot(d, (ox + s * 0.42, oy + s * 0.36), max(2, s * 0.018))
    line(d, (ox + s * 0.52, oy + s * 0.14), (ox + s * 0.7, oy + s * 0.14), max(2, s * 0.03), INK)
    pie(d, (ox + s * 0.7, oy + s * 0.14), s * 0.09, 0, 90, RED)
    line(d, (ox + s * 0.7, oy + s * 0.14), (ox + s * 0.7, oy + s * 0.88), s * 0.05, INK)
    line(d, (ox + s * 0.56, oy + s * 0.6), (ox + s * 0.84, oy + s * 0.6), max(2, s * 0.035), INK)
    for rr in (s * 0.1, s * 0.17, s * 0.24):
        arc_span(d, (ox + s * 0.7, oy + s * 0.6), rr, -45, 45, max(2, s * 0.022), TEAL)
    pie(d, (ox + s * 0.7, oy + s * 0.74), s * 0.05, 0, 360, GOLD)

def icon_americas(d, x, y, s):
    # handshake = restored cooperation, with a pulsing star
    ox, oy = x, y
    line(d, (ox + s * 0.74, oy + s * 0.58), (ox + s * 0.42, oy + s * 0.54),
         max(2, s * 0.09), RED)
    line(d, (ox + s * 0.26, oy + s * 0.58), (ox + s * 0.58, oy + s * 0.54),
         max(2, s * 0.09), NAVY)
    pie(d, (ox + s * 0.4, oy + s * 0.4), s * 0.09, 0, 360, INK)
    pie(d, (ox + s * 0.6, oy + s * 0.4), s * 0.09, 0, 360, INK)
    line(d, (ox + s * 0.4, oy + s * 0.4), (ox + s * 0.5, oy + s * 0.34), max(2, s * 0.03), INK)
    line(d, (ox + s * 0.6, oy + s * 0.4), (ox + s * 0.5, oy + s * 0.34), max(2, s * 0.03), INK)
    cx, cy = ox + s * 0.5, oy + s * 0.16
    pts = []
    for k in range(10):
        ang = -90 + k * 36
        rr = s * 0.09 if k % 2 == 0 else s * 0.04
        import math as _m
        pts.append((cx + rr * _m.cos(_m.radians(ang)), cy + rr * _m.sin(_m.radians(ang))))
    d.polygon(pts, fill=GOLD)

def chip(d, x, y, maxw, label, col):
    f = font(BOLD, 15)
    tw = text_w(d, label, f)
    cw = int(tw) + 24
    chh = 26
    rrect(d, (x, y, x + cw, y + chh), 13, fill=col)
    d.text((x + 12, y + 4), label, font=f, fill=WHITE)
    return (x, y + chh), (x + cw, y + chh)

def story_header(d, corner_x, corner_y, label, col, headline, sub, left, right):
    fchip = font(BOLD, 15)
    _, bry = chip(d, corner_x, corner_y, right - left - 2, label, col)
    bry = bry[1]
    hh = bry + 4
    fh = font(BOLD, 24)
    lines = wrap_text(d, headline, fh, right - left)
    for ln in lines[:2]:
        d.text((left, hh), ln, font=fh, fill=INK)
        hh += 33
    hs = font(REG, 14)
    slines = wrap_text(d, sub, hs, right - left)
    for ln in slines[:2]:
        d.text((left, hh), ln, font=hs, fill=INK)
        hh += 20
    return hh

def draw_north_star(d, x, y, r_outer):
    r_inner = r_outer * 0.4
    import math as _m
    pts = []
    for k in range(8):
        ang = -90 + k * 45
        rr = r_outer if k % 2 == 0 else r_inner
        pts.append((x + rr * _m.cos(_m.radians(ang)), y + rr * _m.sin(_m.radians(ang))))
    d.polygon(pts, fill=GOLD)

def draw_variant1(d):
    d.rectangle([0, 0, W, H], fill=PAPER)

    # ---------------- masthead (navy band) ----------------
    rect(d, (0, 0, W, 108), fill=NAVY)
    line(d, (0, 107, W, 107), 3, GOLD)
    f_mast = font(BOLD, 38)
    mast = "THE WORLD IN ONE IMAGE"
    y0 = 18
    tw = text_w(d, mast, f_mast)
    x0 = int((W - tw) / 2)
    d.text((x0, y0), mast, font=f_mast, fill=WHITE)
    y1 = y0 + 50
    f_date = font(BOLD, 30)
    date_s = "FRIDAY  20  NOVEMBER  2026"
    tw2 = text_w(d, date_s, f_date)
    d.text((int((W - tw2) / 2), y1), date_s, font=f_date, fill=GOLD)

    # ---------------- lead story (full width) ----------------
    lead_top = 108
    y = lead_top + 18
    chip(d, 18, y, 220, "LEAD  \u2022  DIPLOMACY", RED)
    y += 40
    fh = font(BOLD, 44)
    lines = wrap_text(d, "Trump, Xi and putin hold first three-way meeting in Shenzhen",
                      fh, W - 36)
    for ln in lines[:2]:
        d.text((18, y), ln, font=fh, fill=INK)
        y += 56
    fs = font(REG, 24)
    sllines = wrap_text(d,
        "At the APEC summit the three leaders released a joint \u201cpeace declaration\u201d "
        "on nuclear arms control and global security.",
        fs, W - 36)
    for ln in sllines[:2]:
        d.text((18, y), ln, font=fs, fill=INK)
        y += 34

    # ---------------- 2x2 grid (stories 2-5) ----------------
    x0 = 12
    grid_top = y + 8
    gap = 8
    panel_w = (W - 2 * x0 - gap) // 2
    panel_h = 156
    cells = {"one": (x0, grid_top), "two": (x0 + panel_w + gap, grid_top),
             "three": (x0, grid_top + panel_h + gap),
             "four": (x0 + panel_w + gap, grid_top + panel_h + gap)}
    panel_font = font(REG, 18)
    icon_s = 46
    for key, (px, py) in cells.items():
        rect(d, (px, py, px + panel_w, py + panel_h), outline=INK, width=1)
        if key == "one":
            label, col, headline, sub, icon = (
                "JUSTICE", NAVY, "ICJ rules Myanmar sought to destroy the Rohingya",
                "The court found the military likely intended to destroy a substantial "
                "part of the 2017 crackdown's minority.", icon_justice)
        elif key == "two":
            label, col, headline, sub, icon = (
                "WEATHER", TEAL, "Cyclone Akvan bears down on India's Odisha coast",
                "Landfall expected 20 Nov; schools closed and evacuations under way.",
                icon_weather)
        elif key == "three":
            label, col, headline, sub, icon = (
                "CULTURE", GOLD, "Van Gogh sells for a record $190.4 million",
                "Record auction price fell after a dispute over its Nazi-era history.",
                None)
        else:
            label, col, headline, sub, icon = (
                "SPACE", RED, "Voyager 1 hits one light-day from Earth",
                "First human-made object that far out; a radio signal now takes 24 hours.",
                icon_space)
        ix = px + 12
        iy = py + 26
        icon_box = (ix, iy, ix + icon_s, iy + icon_s)
        if key == "three":
            draw_north_star(d, ix + icon_s // 2, iy + icon_s // 2, icon_s // 2)
        elif key == "one":
            icon_justice(d, ix, iy, icon_s)
        elif key == "two":
            icon_weather(d, ix, iy, icon_s)
        else:
            icon_space(d, ix, iy, icon_s)
        try:
            rrect(d, icon_box, 8, outline=None)
        except Exception:
            pass
        rh = story_header(d, px + panel_w - 150, py + 16, label, col,
                          headline, sub, ix + icon_s + 12, px + panel_w - 12)

    # ---------------- bottom ticker strip ----------------
    tick_top = grid_top + 2 * panel_h + gap + 10
    tick_h = 58
    rect(d, (0, tick_top, W, tick_top + tick_h), fill=NAVY)
    line(d, (0, tick_top, W, tick_top), 2, GOLD)
    f_tick = font(BOLD, 15)
    fr = font(REG, 15)
    tx = 14
    ty = tick_top + 9
    d.text((tx, ty), "AMERICAS", font=f_tick, fill=GOLD)
    tx += int(text_w(d, "AMERICAS", f_tick)) + 12
    d.text((tx, ty), "U.S. and Venezuela sign deal to restore military cooperation",
           font=fr, fill=WHITE)
    tx += int(text_w(d, "U.S. and Venezuela sign deal to restore military cooperation", fr)) + 16
    d.text((tx, ty), "///", font=f_tick, fill=GOLD)
    tx += int(text_w(d, "///", f_tick)) + 12
    d.text((tx, ty), "Fiji declares national disaster over drought and water shortages",
           font=fr, fill=WHITE)
    tx += int(text_w(d, "Fiji declares national disaster over drought and water shortages", fr)) + 16
    d.text((tx, ty), "///", font=f_tick, fill=GOLD)
    tx += int(text_w(d, "///", f_tick)) + 12
    d.text((tx, ty), "UN: North Korea expanding uranium enrichment at Yongbyon",
           font=fr, fill=WHITE)
    ty2 = tick_top + 34
    tx = 14
    d.text((tx, ty2), "WHATS NEXT", font=f_tick, fill=GOLD)
    tx += int(text_w(d, "WHATS NEXT", f_tick)) + 12
    d.text((tx, ty2), "Anthropic valuation reportedly reaches $1.5 trillion",
           font=fr, fill=WHITE)
    tx += int(text_w(d, "Anthropic valuation reportedly reaches $1.5 trillion", fr)) + 16
    d.text((tx, ty2), "///", font=f_tick, fill=GOLD)
    tx += int(text_w(d, "///", f_tick)) + 12
    d.text((tx, ty2), "Musk to NYT: \u201cI'm not MAGA\u201d; funded ~$500m for 2026 midterms",
           font=fr, fill=WHITE)

    # ---------------- footer ----------------
    btm = tick_top + tick_h + 10
    f_foot = font(REG, 15)
    ftxt = "All stories first reported 20 November 2026"
    twf = text_w(d, ftxt, f_foot)
    d.text((int((W - twf) / 2), btm), ftxt, font=f_foot, fill=INK)
    line(d, (int((W - twf) / 2) - 10, btm + 8), (int((W + twf) / 2) + 10, btm + 8),
         1, INK)

import sys
try:
    from PIL import Image, ImageDraw, ImageFont
except Exception as exc:  # pragma: no cover
    raise SystemExit("pillow required: " + repr(exc))

# deterministic, no randomness, no network, no wall-clock usage

BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# palette (paper #F7F1E3, ink #14213D, accent red, navy, teal, gold)
PAPER = (247, 241, 227)
INK = (20, 33, 61)
RED = (193, 39, 45)
NAVY = (27, 42, 74)
TEAL = (14, 124, 123)
GOLD = (217, 164, 65)
WHITE = (255, 255, 255)

W = 1024
H = 1024

_font_cache = {}

def font(path, size):
    key = (path, size)
    f = _font_cache.get(key)
    if f is None:
        f = ImageFont.truetype(path, size)
        _font_cache[key] = f
    return f

def text_w(d, text, f):
    return d.textlength(text, font=f)

def wrap_text(d, text, f, max_width):
    words = text.split(" ")
    lines = []
    cur = ""
    for w_ in words:
        trial = (cur + " " + w_).strip() if cur else w_
        if text_w(d, trial, f) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines or [""]

def draw_wrapped(d, xy, lines, f, fill, leading):
    x, y = xy
    w = 0
    for ln in lines:
        d.text((x, y), ln, font=f, fill=fill)
        y += leading
    return y - leading

def rrect(d, box, r, fill=None, outline=None, width=1):
    d.rounded_rectangle([int(box[0]), int(box[1]), int(box[2]), int(box[3])], radius=int(r), fill=fill, outline=outline, width=int(width))

def circle(d, center, rad, fill=None, outline=None, width=1):
    d.ellipse([int(center[0] - rad), int(center[1] - rad), int(center[0] + rad), int(center[1] + rad)],
              fill=fill, outline=outline, width=int(width))

def diamond(d, center, half, fill=None):
    d.polygon([(int(center[0]), int(center[1] - half)),
               (int(center[0] + half), int(center[1])),
               (int(center[0]), int(center[1] + half)),
               (int(center[0] - half), int(center[1]))], fill=fill)

def triangle(d, top, base_half, hgt, fill, flip=False):
    x, y = top
    if flip:
        d.polygon([(int(x - base_half), int(y)), (int(x + base_half), int(y)), (int(x), int(y + hgt))], fill=fill)
    else:
        d.polygon([(int(x - base_half), int(y)), (int(x + base_half), int(y)), (int(x), int(y - hgt))], fill=fill)

def arc_span(d, c, r, a0, a1, width, fill):
    d.arc([int(c[0] - r), int(c[1] - r), int(c[0] + r), int(c[1] + r)], start=a0, end=a1,
          width=int(width), fill=fill)

def pie(d, c, r, a0, a1, fill):
    d.pieslice([int(c[0] - r), int(c[1] - r), int(c[0] + r), int(c[1] + r)], start=a0, end=a1, fill=fill)

def line(d, *args):
    # Support both calling conventions:
    # 1. line(d, (x1, y1), (x2, y2), width, fill)  -- two points
    # 2. line(d, (x1, y1, x2, y2), width, fill)    -- single 4-tuple
    if len(args) == 4:
        p1, p2, width, fill = args
        d.line([(int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1]))], width=int(width), fill=fill)
    elif len(args) == 3:
        box, width, fill = args
        if isinstance(box, (tuple, list)) and len(box) == 4:
            x1, y1, x2, y2 = box
            d.line([(int(x1), int(y1)), (int(x2), int(y2))], width=int(width), fill=fill)
        else:
            raise ValueError("Invalid arguments to line()")
    else:
        raise ValueError("Invalid arguments to line()")

def rect(d, box, fill=None, outline=None, width=1):
    d.rectangle([int(box[0]), int(box[1]), int(box[2]), int(box[3])], fill=fill, outline=outline, width=int(width))

def dot(d, c, r=3):
    d.ellipse([int(c[0] - r), int(c[1] - r), int(c[0] + r), int(c[1] + r)], fill=INK)

def icon_lead(d, x, y, s):
    # three overlapping seals with connecting beam = the three-way meeting
    cols = [RED, GOLD, NAVY]
    for i in range(3):
        dx = (i - 1) * s * 0.28
        cx, cy = x + s * 0.5 + dx, y + s * 0.5
        circle(d, (cx, cy), s * 0.26, fill=cols[i])
    line(d, (x + s * 0.5 - s * 0.3, y + s * 0.5), (x + s * 0.5 + s * 0.3, y + s * 0.5),
         max(2, s * 0.05), INK)
    dot(d, (x + s * 0.5, y + s * 0.5), s * 0.06)

def icon_justice(d, x, y, s):
    # balanced scales = the ICJ ruling
    line(d, (x + s * 0.5, y + s * 0.15), (x + s * 0.5, y + s * 0.62), s * 0.06, INK)
    line(d, (x + s * 0.5, y + s * 0.62), (x + s * 0.33, y + s * 0.62), s * 0.06, INK)
    line(d, (x + s * 0.5, y + s * 0.62), (x + s * 0.67, y + s * 0.62), s * 0.06, INK)
    line(d, (x + s * 0.24, y + s * 0.6), (x + s * 0.76, y + s * 0.6), s * 0.05, INK)
    tx = [x + s * 0.3, x + s * 0.7]
    for cx in tx:
        line(d, (cx - s * 0.13, y + s * 0.40), (cx, y + s * 0.6), max(2, s * 0.022), INK)
        line(d, (cx + s * 0.13, y + s * 0.40), (cx, y + s * 0.6), max(2, s * 0.022), INK)
        pie(d, (cx, y + s * 0.42), s * 0.13, 0, 180, GOLD)

def icon_weather(d, x, y, s):
    # cyclone = spiral bands around a centre
    c = (x + s * 0.5, y + s * 0.5)
    pie(d, c, s * 0.4, 0, 180, TEAL)
    for i, rr in enumerate((s * 0.33, s * 0.26, s * 0.19)):
        arc_span(d, c, rr, 180 + i * 18, 180 + 176, max(2, s * 0.05), NAVY)
    circle(d, c, s * 0.1, fill=RED)

def icon_space(d, x, y, s):
    # deep-space probe with dish, signal waves and star field
    ox, oy = x, y
    dot(d, (ox + s * 0.18, oy + s * 0.2), max(2, s * 0.018))
    dot(d, (ox + s * 0.3, oy + s * 0.12), max(2, s * 0.018))
    dot(d, (ox + s * 0.42, oy + s * 0.36), max(2, s * 0.018))
    line(d, (ox + s * 0.52, oy + s * 0.14), (ox + s * 0.7, oy + s * 0.14), max(2, s * 0.03), INK)
    pie(d, (ox + s * 0.7, oy + s * 0.14), s * 0.09, 0, 90, RED)
    line(d, (ox + s * 0.7, oy + s * 0.14), (ox + s * 0.7, oy + s * 0.88), s * 0.05, INK)
    line(d, (ox + s * 0.56, oy + s * 0.6), (ox + s * 0.84, oy + s * 0.6), max(2, s * 0.035), INK)
    for rr in (s * 0.1, s * 0.17, s * 0.24):
        arc_span(d, (ox + s * 0.7, oy + s * 0.6), rr, -45, 45, max(2, s * 0.022), TEAL)
    pie(d, (ox + s * 0.7, oy + s * 0.74), s * 0.05, 0, 360, GOLD)

def icon_americas(d, x, y, s):
    # handshake = restored cooperation, with a pulsing star
    ox, oy = x, y
    line(d, (ox + s * 0.74, oy + s * 0.58), (ox + s * 0.42, oy + s * 0.54),
         max(2, s * 0.09), RED)
    line(d, (ox + s * 0.26, oy + s * 0.58), (ox + s * 0.58, oy + s * 0.54),
         max(2, s * 0.09), NAVY)
    pie(d, (ox + s * 0.4, oy + s * 0.4), s * 0.09, 0, 360, INK)
    pie(d, (ox + s * 0.6, oy + s * 0.4), s * 0.09, 0, 360, INK)
    line(d, (ox + s * 0.4, oy + s * 0.4), (ox + s * 0.5, oy + s * 0.34), max(2, s * 0.03), INK)
    line(d, (ox + s * 0.6, oy + s * 0.4), (ox + s * 0.5, oy + s * 0.34), max(2, s * 0.03), INK)
    cx, cy = ox + s * 0.5, oy + s * 0.16
    pts = []
    for k in range(10):
        ang = -90 + k * 36
        rr = s * 0.09 if k % 2 == 0 else s * 0.04
        import math as _m
        pts.append((cx + rr * _m.cos(_m.radians(ang)), cy + rr * _m.sin(_m.radians(ang))))
    d.polygon(pts, fill=GOLD)

def chip(d, x, y, maxw, label, col):
    f = font(BOLD, 15)
    tw = text_w(d, label, f)
    cw = int(tw) + 24
    chh = 26
    rrect(d, (x, y, x + cw, y + chh), 13, fill=col)
    d.text((x + 12, y + 4), label, font=f, fill=WHITE)
    return (x, y + chh), (x + cw, y + chh)

def story_header(d, corner_x, corner_y, label, col, headline, sub, left, right):
    fchip = font(BOLD, 15)
    _, bry = chip(d, corner_x, corner_y, right - left - 2, label, col)
    bry = bry[1]
    hh = bry + 4
    fh = font(BOLD, 24)
    lines = wrap_text(d, headline, fh, right - left)
    for ln in lines[:2]:
        d.text((left, hh), ln, font=fh, fill=INK)
        hh += 33
    hs = font(REG, 14)
    slines = wrap_text(d, sub, hs, right - left)
    for ln in slines[:2]:
        d.text((left, hh), ln, font=hs, fill=INK)
        hh += 20
    return hh

def draw_north_star(d, x, y, r_outer):
    r_inner = r_outer * 0.4
    import math as _m
    pts = []
    for k in range(8):
        ang = -90 + k * 45
        rr = r_outer if k % 2 == 0 else r_inner
        pts.append((x + rr * _m.cos(_m.radians(ang)), y + rr * _m.sin(_m.radians(ang))))
    d.polygon(pts, fill=GOLD)

def draw_variant1(d):
    d.rectangle([0, 0, W, H], fill=PAPER)

    # ---------------- masthead (navy band) ----------------
    rect(d, (0, 0, W, 108), fill=NAVY)
    line(d, (0, 107, W, 107), 3, GOLD)
    f_mast = font(BOLD, 38)
    mast = "THE WORLD IN ONE IMAGE"
    y0 = 18
    tw = text_w(d, mast, f_mast)
    x0 = int((W - tw) / 2)
    d.text((x0, y0), mast, font=f_mast, fill=WHITE)
    y1 = y0 + 50
    f_date = font(BOLD, 30)
    date_s = "FRIDAY  20  NOVEMBER  2026"
    tw2 = text_w(d, date_s, f_date)
    d.text((int((W - tw2) / 2), y1), date_s, font=f_date, fill=GOLD)

    # ---------------- lead story (full width) ----------------
    lead_top = 108
    y = lead_top + 18
    chip(d, 18, y, 220, "LEAD  \u2022  DIPLOMACY", RED)
    y += 40
    fh = font(BOLD, 44)
    lines = wrap_text(d, "Trump, Xi and putin hold first three-way meeting in Shenzhen",
                      fh, W - 36)
    for ln in lines[:2]:
        d.text((18, y), ln, font=fh, fill=INK)
        y += 56
    fs = font(REG, 24)
    sllines = wrap_text(d,
        "At the APEC summit the three leaders released a joint \u201cpeace declaration\u201d "
        "on nuclear arms control and global security.",
        fs, W - 36)
    for ln in sllines[:2]:
        d.text((18, y), ln, font=fs, fill=INK)
        y += 34

    # ---------------- 2x2 grid (stories 2-5) ----------------
    x0 = 12
    grid_top = y + 8
    gap = 8
    panel_w = (W - 2 * x0 - gap) // 2
    panel_h = 156
    cells = {"one": (x0, grid_top), "two": (x0 + panel_w + gap, grid_top),
             "three": (x0, grid_top + panel_h + gap),
             "four": (x0 + panel_w + gap, grid_top + panel_h + gap)}
    panel_font = font(REG, 18)
    icon_s = 46
    for key, (px, py) in cells.items():
        rect(d, (px, py, px + panel_w, py + panel_h), outline=INK, width=1)
        if key == "one":
            label, col, headline, sub, icon = (
                "JUSTICE", NAVY, "ICJ rules Myanmar sought to destroy the Rohingya",
                "The court found the military likely intended to destroy a substantial "
                "part of the 2017 crackdown's minority.", icon_justice)
        elif key == "two":
            label, col, headline, sub, icon = (
                "WEATHER", TEAL, "Cyclone Akvan bears down on India's Odisha coast",
                "Landfall expected 20 Nov; schools closed and evacuations under way.",
                icon_weather)
        elif key == "three":
            label, col, headline, sub, icon = (
                "CULTURE", GOLD, "Van Gogh sells for a record $190.4 million",
                "Record auction price fell after a dispute over its Nazi-era history.",
                None)
        else:
            label, col, headline, sub, icon = (
                "SPACE", RED, "Voyager 1 hits one light-day from Earth",
                "First human-made object that far out; a radio signal now takes 24 hours.",
                icon_space)
        ix = px + 12
        iy = py + 26
        icon_box = (ix, iy, ix + icon_s, iy + icon_s)
        if key == "three":
            draw_north_star(d, ix + icon_s // 2, iy + icon_s // 2, icon_s // 2)
        else:
            icon(d, ix, iy, icon_s)
        try:
            rrect(d, icon_box, 8, outline=None)
        except Exception:
            pass
        rh = story_header(d, px + panel_w - 150, py + 16, label, col,
                          headline, sub, ix + icon_s + 12, px + panel_w - 12)

    # ---------------- bottom ticker strip ----------------
    tick_top = grid_top + 2 * panel_h + gap + 10
    tick_h = 58
    rect(d, (0, tick_top, W, tick_top + tick_h), fill=NAVY)
    line(d, (0, tick_top, W, tick_top), 2, GOLD)
    f_tick = font(BOLD, 15)
    fr = font(REG, 15)
    tx = 14
    ty = tick_top + 9
    d.text((tx, ty), "AMERICAS", font=f_tick, fill=GOLD)
    tx += int(text_w(d, "AMERICAS", f_tick)) + 12
    d.text((tx, ty), "U.S. and Venezuela sign deal to restore military cooperation",
           font=fr, fill=WHITE)
    tx += int(text_w(d, "U.S. and Venezuela sign deal to restore military cooperation", fr)) + 16
    d.text((tx, ty), "///", font=f_tick, fill=GOLD)
    tx += int(text_w(d, "///", f_tick)) + 12
    d.text((tx, ty), "Fiji declares national disaster over drought and water shortages",
           font=fr, fill=WHITE)
    tx += int(text_w(d, "Fiji declares national disaster over drought and water shortages", fr)) + 16
    d.text((tx, ty), "///", font=f_tick, fill=GOLD)
    tx += int(text_w(d, "///", f_tick)) + 12
    d.text((tx, ty), "UN: North Korea expanding uranium enrichment at Yongbyon",
           font=fr, fill=WHITE)
    ty2 = tick_top + 34
    tx = 14
    d.text((tx, ty2), "WHATS NEXT", font=f_tick, fill=GOLD)
    tx += int(text_w(d, "WHATS NEXT", f_tick)) + 12
    d.text((tx, ty2), "Anthropic valuation reportedly reaches $1.5 trillion",
           font=fr, fill=WHITE)
    tx += int(text_w(d, "Anthropic valuation reportedly reaches $1.5 trillion", fr)) + 16
    d.text((tx, ty2), "///", font=f_tick, fill=GOLD)
    tx += int(text_w(d, "///", f_tick)) + 12
    d.text((tx, ty2), "Musk to NYT: \u201cI'm not MAGA\u201d; funded ~$500m for 2026 midterms",
           font=fr, fill=WHITE)

    # ---------------- footer ----------------
    btm = tick_top + tick_h + 10
    f_foot = font(REG, 15)
    ftxt = "All stories first reported 20 November 2026"
    twf = text_w(d, ftxt, f_foot)
    d.text((int((W - twf) / 2), btm), ftxt, font=f_foot, fill=INK)
    line(d, (int((W - twf) / 2) - 10, btm + 8), (int((W + twf) / 2) + 10, btm + 8),
         1, INK)

def draw_variant2(d):
    d.rectangle([0, 0, W, H], fill=PAPER)

    # --- top date banner ---
    rect(d, (0, 0, W, 82), fill=NAVY)
    line(d, (0, 81, W, 81), 3, GOLD)
    f_title = font(BOLD, 28)
    title_s = "THE WORLD IN ONE IMAGE"
    twt = text_w(d, title_s, f_title)
    d.text((int((W - twt) / 2), 8), title_s, font=f_title, fill=WHITE)
    f_date = font(BOLD, 26)
    date_s = "FRIDAY  20  NOVEMBER  2026"
    twd = text_w(d, date_s, f_date)
    d.text((int((W - twd) / 2), 46), date_s, font=f_date, fill=GOLD)

    # --- 2 x 3 grid of six panels ---
    mt = 94
    cols = 2
    rows = 3
    gap = 14
    pad = 20
    pw = (W - 2 * pad - (cols - 1) * gap) // cols
    ph = (H - mt - pad - (rows - 1) * gap) // rows
    data = [
        ("DIPLOMACY", RED, "Trump, Xi and Putin hold first three-way meeting in Shenzhen",
         "At the APEC summit the leaders released a joint peace declaration on nuclear arms control and global security.", icon_lead),
        ("JUSTICE", NAVY, "ICJ rules Myanmar sought to destroy the Rohingya",
         "The court found the military likely intended to destroy a substantial part of the minority during the 2017 crackdown.", icon_justice),
        ("WEATHER", TEAL, "Cyclone Akvan bears down on India's Odisha coast",
         "Landfall expected 20 Nov; schools closed and evacuations under way.", icon_weather),
        ("CULTURE", GOLD, "Van Gogh sells for a record $190.4 million",
         "Record auction price fell after a dispute over its Nazi-era history.", None),
        ("SPACE", RED, "Voyager 1 hits one light-day from Earth",
         "First human-made object that far out; a radio signal now takes 24 hours.", icon_space),
        ("AMERICAS", NAVY, "U.S. and Venezuela sign deal to restore military cooperation",
         "Agreement less than a year after Maduro's ouster.", icon_americas),
    ]
    for i, (label, col, headline, sub, icon) in enumerate(data):
        r = i // cols
        c = i % cols
        x = pad + c * (pw + gap)
        y = mt + r * (ph + gap)
        rrect(d, (x, y, x + pw, y + ph), 12, fill=WHITE, outline=INK, width=2)
        # header chip
        chip(d, x + 14, y + 12, pw - 28, label, col)
        # icon at right of chip
        isz = 44
        ix = x + pw - 14 - isz
        iy = y + ph - 14 - isz
        if icon is None:
            draw_north_star(d, ix + isz // 2, iy + isz // 2, isz // 2)
        else:
            icon(d, ix, iy, isz)
        # headline text (up to 2 lines)
        ft = font(BOLD, 22)
        hlines = wrap_text(d, headline, ft, pw - 28)
        ty = y + 48
        for ln in hlines[:2]:
            d.text((x + 14, ty), ln, font=ft, fill=INK)
            ty += 28
        # summary (wrapped to two lines, never truncated)
        fs = font(REG, 15)
        wmax = pw - 28
        slines = wrap_text(d, sub, fs, wmax)
        for j, ln in enumerate(slines[:2]):
            d.text((x + 14, ty + 4 + j * 20), ln, font=fs, fill=INK)

def draw_variant3(d):
    d.rectangle([0, 0, W, H], fill=PAPER)

    # --- date line ---
    rect(d, (0, 0, W, 54), fill=NAVY)
    f_date = font(BOLD, 26)
    date_s = "FRIDAY  20  NOVEMBER  2026"
    twd = text_w(d, date_s, f_date)
    d.text((int((W - twd) / 2), 12), date_s, font=f_date, fill=GOLD)
    line(d, (0, 53, W, 53), 2, GOLD)

    # --- huge headline for story 1 ---
    chip(d, 20, 70, 300, "LEAD  \u2022  DIPLOMACY", RED)
    fh = font(BOLD, 46)
    hl = wrap_text(d, "Trump, Xi and Putin hold first three-way meeting in Shenzhen", fh, W - 40)
    ty = 104
    for ln in hl[:2]:
        d.text((20, ty), ln, font=fh, fill=INK)
        ty += 54
    fs = font(REG, 20)
    sl = wrap_text(d, "At the APEC summit the three leaders released a joint \u201cpeace declaration\u201d on nuclear arms control and global security.", fs, W - 40)
    ty += 2
    for ln in sl[:2]:
        d.text((20, ty), ln, font=fs, fill=INK)
        ty += 28

    # --- red rule ---
    ty += 6
    line(d, (20, ty, W - 20, ty), 4, RED)
    ty += 14

    # --- five brief rows (stories 2-6) ---
    briefs = [
        ("JUSTICE", NAVY, "ICJ rules Myanmar sought to destroy the Rohingya",
         "The court found the military likely intended to destroy a substantial part of the 2017 crackdown's minority."),
        ("WEATHER", TEAL, "Cyclone Akvan bears down on India's Odisha coast",
         "Landfall expected 20 Nov; schools closed and evacuations under way."),
        ("CULTURE", GOLD, "Van Gogh sells for a record $190.4 million",
         "Record auction price fell after a dispute over its Nazi-era history."),
        ("SPACE", RED, "Voyager 1 hits one light-day from Earth",
         "First human-made object that far out; a radio signal now takes 24 hours."),
        ("AMERICAS", NAVY, "U.S. and Venezuela sign deal to restore military cooperation",
         "Agreement less than a year after Maduro's ouster."),
    ]
    row_h = (H - ty - 96) // 5
    for i, (label, col, head, sub) in enumerate(briefs):
        ry = ty + i * row_h
        # panel background
        rrect(d, (20, ry, W - 20, ry + 70), 10, fill=WHITE, outline=INK, width=1)
        cyy = ry + 12
        chip(d, 32, cyy, 260, label, col)
        # bold headline
        fhh = font(BOLD, 22)
        chip_w = int(text_w(d, label, font(BOLD, 15))) + 24
        hx = 32 + chip_w + 16
        d.text((hx, cyy - 3), head, font=fhh, fill=INK)
        # one-liner summary
        fsb = font(REG, 15)
        d.text((hx, cyy + 26), sub, font=fsb, fill=INK)

    # --- bottom ticker strip (two items from story 7) ---
    strip_y = H - 86
    rect(d, (0, strip_y, W, H - 12), fill=NAVY)
    line(d, (0, strip_y, W, strip_y), 2, GOLD)
    f_tick = font(BOLD, 15)
    fr = font(REG, 15)
    d.text((16, strip_y + 8), "TICKER", font=f_tick, fill=GOLD)
    tx = 16 + int(text_w(d, "TICKER", f_tick)) + 14
    d.text((tx, strip_y + 8), "Fiji declares disaster over drought", font=fr, fill=WHITE)
    tx += int(text_w(d, "Fiji declares disaster over drought", fr)) + 14
    d.text((tx, strip_y + 8), "///", font=f_tick, fill=GOLD)
    tx += int(text_w(d, "///", f_tick)) + 14
    d.text((tx, strip_y + 8), "UN: North Korea expanding enrichment", font=fr, fill=WHITE)
    d.text((16, strip_y + 34), "Also that day: Anthropic valued at $1.5 trillion; Musk: \u201cI'm not MAGA.\u201d", font=fr, fill=WHITE)
    # footer (inside the navy strip, gold, fully within the canvas)
    f_foot = font(REG, 14)
    ftxt = "All stories first reported 20 November 2026"
    twf = text_w(d, ftxt, f_foot)
    d.text((int((W - twf) / 2), strip_y + 56), ftxt, font=f_foot, fill=GOLD)

def main():
    variant = sys.argv[1] if len(sys.argv) > 1 else "1"
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    fn = globals().get("draw_variant" + variant, None)
    if fn is None:
        raise SystemExit("unknown variant: " + variant)
    fn(d)
    img.save(sys.argv[2] if len(sys.argv) > 2 else ("out_" + variant + ".png"), "PNG")

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
