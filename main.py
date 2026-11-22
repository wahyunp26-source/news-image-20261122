#!/usr/bin/env python3
"""Sunday 22 November 2026 - the world in one image.

A pure-stdlib program that draws a one-page newspaper front page summing up
Sunday 22 November 2026: masthead, eight illustrated panels for the day's
biggest stories and a 24-item briefs index, then writes /output/entry.png.

No network, no randomness, no time: two runs write identical bytes.
"""
import os
import struct
import sys
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- palette ---
PAPER = (247, 241, 227)
INK = (26, 26, 26)
INK_SOFT = (74, 74, 74)
RED = (178, 34, 34)
BLUE = (31, 76, 141)
SKY = (135, 196, 235)
SKY_DUSK = (58, 74, 120)
SEA = (28, 96, 140)
SEA_DARK = (16, 64, 96)
SAND = (232, 205, 150)
GREEN = (46, 125, 50)
LEAF = (76, 175, 80)
GOLD = (212, 160, 32)
ORANGE = (230, 120, 30)
FLAME = (245, 180, 40)
SMOKE = (120, 120, 118)
GREY = (150, 150, 148)
DARKGREY = (90, 90, 88)
WHITE = (255, 255, 255)
CREAM = (250, 246, 236)
TEAL = (0, 128, 128)
BROWN = (120, 72, 20)
MOUNTAIN = (96, 110, 140)
MOUNTAIN2 = (70, 84, 112)

# ------------------------------------------------------------- 5x7 font -----
# Each glyph: 7 rows of 5 cells, '#' = ink.
FONT = {
    'A': (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".####", "#....", "#....", "#....", "#....", "#...#", ".###."),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".####"),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    '0': (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "..##.", ".#...", "#....", "#####"),
    '3': ("#####", "...#.", "..#..", "...#.", "....#", "#...#", ".###."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': ("..##.", ".#...", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "...#.", ".##.."),
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    '.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ',': (".....", ".....", ".....", ".....", ".##..", "..#..", ".#..."),
    ':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ';': (".....", ".##..", ".##..", ".....", ".##..", "..#..", ".#..."),
    '-': (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "....#", "..##.", "..#..", ".....", "..#.."),
    '/': ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    '(': ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ')': (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    '&': (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    '+': (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    '%': ("##..#", "##.#.", "....#", "...#.", "..#..", ".#..#", "#.##."),
    '$': ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    '=': (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
    '*': (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
}


def text_w(s, scale):
    """Pixel width of string s at the given scale."""
    return len(s) * (6 * scale) - scale if s else 0


# ---------------------------------------------------------------- canvas ----
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill(bg)

    def fill(self, c):
        r, g, b = c
        self.px[:] = bytes((r, g, b)) * (self.w * self.h)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(c)

    def rect(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(c) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def border(self, x, y, w, h, c, t=2):
        self.rect(x, y, w, t, c)
        self.rect(x, y + h - t, w, t, c)
        self.rect(x, y, t, h, c)
        self.rect(x + w - t, y, t, h, c)

    def line(self, x0, y0, x1, y1, c):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def line_w(self, x0, y0, x1, y1, c, w=2):
        self.line(x0, y0, x1, y1, c)
        if w > 1:
            self.line(x0 + 1, y0, x1 + 1, y1, c)
            self.line(x0, y0 + 1, x1, y1 + 1, c)

    def circle(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            dy = yy - cy
            dx = int((r * r - dy * dy) ** 0.5) if r * r - dy * dy >= 0 else 0
            self.rect(cx - dx, yy, dx * 2 + 1, 1, c)

    def ellipse(self, cx, cy, rx, ry, c):
        for yy in range(cy - ry, cy + ry + 1):
            dy = (yy - cy) / float(ry) if ry else 0
            if abs(dy) > 1:
                continue
            dx = int(rx * (1 - dy * dy) ** 0.5)
            self.rect(cx - dx, yy, dx * 2 + 1, 1, c)

    def poly(self, pts, c):
        """Scanline fill of a simple polygon."""
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        for yy in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= yy < y1) or (y1 <= yy < y0):
                    t = (yy - y0) / float(y1 - y0)
                    xs.append(x0 + t * (x1 - x0))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                self.rect(int(xs[k]), yy, int(xs[k + 1]) - int(xs[k]) + 1, 1, c)

    def vgrad(self, x, y, w, h, top, bot):
        for yy in range(h):
            t = yy / float(max(1, h - 1))
            c = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
            self.rect(x, y + yy, w, 1, c)

    def text(self, x, y, s, scale, c):
        cx = x
        for ch in s:
            g = FONT.get(ch, FONT[' '])
            for row in range(7):
                bits = g[row]
                for col in range(5):
                    if bits[col] == '#':
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, c)
            cx += 6 * scale
        return cx

    def text_c(self, cx, y, s, scale, c):
        self.text(cx - text_w(s, scale) // 2, y, s, scale, c)

    def wrap(self, s, maxw, scale):
        """Word-wrap s to lines fitting maxw pixels at scale."""
        cw = 6 * scale
        per = max(1, maxw // cw)
        words = s.split(' ')
        lines = []
        cur = ''
        for wd in words:
            trial = (cur + ' ' + wd).strip()
            if len(trial) <= per:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines


def png_bytes(cv):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        out = struct.pack('>I', len(data)) + tag + data
        out += struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)
        return out

    ihdr = struct.pack('>IIBBBBB', cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr)
            + chunk(b'IDAT', comp) + chunk(b'IEND', b''))

# ------------------------------------------------------------ scene bits ----
def sun(cv, x, y, r, c=GOLD):
    cv.circle(x, y, r, c)
    for k in range(8):
        ang = k * 0.785398
        import math
        dx = int(math.cos(ang) * (r + 8))
        dy = int(math.sin(ang) * (r + 8))
        cv.line_w(x + int(math.cos(ang) * r), y + int(math.sin(ang) * r),
                  x + dx, y + dy, c, 2)


def cloud(cv, x, y, s, c=WHITE):
    cv.ellipse(x, y, 26 * s // 10, 10 * s // 10, c)
    cv.ellipse(x - 18 * s // 10, y + 4 * s // 10, 16 * s // 10, 8 * s // 10, c)
    cv.ellipse(x + 18 * s // 10, y + 4 * s // 10, 16 * s // 10, 8 * s // 10, c)


def smoke(cv, x, y, c=SMOKE):
    cv.circle(x, y, 9, c)
    cv.circle(x - 10, y + 6, 7, c)
    cv.circle(x + 10, y + 5, 8, c)
    cv.circle(x - 4, y - 10, 7, c)
    cv.circle(x + 6, y - 9, 6, c)


def flame(cv, x, y, s=10):
    # layered teardrop flame, base at (x, y)
    cv.poly([(x - s, y), (x - s // 2, y - 2 * s), (x, y - 3 * s),
             (x + s // 2, y - 2 * s), (x + s, y)], ORANGE)
    cv.poly([(x - s // 2, y), (x - s // 4, y - s), (x, y - 2 * s),
             (x + s // 4, y - s), (x + s // 2, y)], FLAME)
    cv.poly([(x - s // 4, y), (x, y - s), (x + s // 4, y)], (255, 240, 160))


def wave_row(cv, x, y, w, c, amp=4, step=14):
    import math
    for xx in range(x, x + w, 2):
        yy = y + int(amp * math.sin((xx - x) * 0.22))
        cv.rect(xx, yy, 2, 3, c)


def figure(cv, x, y, shirt, skin=(222, 184, 150), h=22):
    # simple standing person, feet at (x, y)
    cv.circle(x, y - h + 4, 4, skin)
    cv.rect(x - 4, y - h + 9, 8, h - 12, shirt)
    cv.line_w(x - 3, y - 3, x - 5, y, INK, 2)
    cv.line_w(x + 3, y - 3, x + 5, y, INK, 2)


def flag_pole(cv, x, y, h, c1, c2=None):
    cv.line_w(x, y, x, y - h, INK, 2)
    cv.rect(x + 1, y - h, 30, 18, c1)
    if c2 is not None:
        cv.rect(x + 1, y - h + 9, 30, 9, c2)


def building(cv, x, y, w, h, c, win=WHITE):
    cv.rect(x, y - h, w, h, c)
    for wy in range(y - h + 8, y - 6, 14):
        for wx in range(x + 6, x + w - 8, 12):
            cv.rect(wx, wy, 6, 8, win)


def crack(cv, x, y, segs, c=INK):
    px, py = x, y
    for dx, dy in segs:
        cv.line_w(px, py, px + dx, py + dy, c, 2)
        px, py = px + dx, py + dy


# ---------------------------------------------------------------- scenes ----
def scene_cop31(cv, x, y, w, h):
    """Antalya climate summit: hall, flags, sun, leaf, delegates."""
    cv.vgrad(x, y, w, h, (168, 214, 240), (240, 238, 214))
    sun(cv, x + w - 52, y + 30, 18)
    cloud(cv, x + 70, y + 26, 8)
    cloud(cv, x + w - 150, y + 62, 6)
    # distant hills
    cv.poly([(x, y + h), (x, y + h - 34), (x + w // 3, y + h - 58),
             (x + 2 * w // 3, y + h - 30), (x + w, y + h - 44),
             (x + w, y + h)], MOUNTAIN)
    # conference hall
    hx, hy, hw, hh = x + 60, y + h - 8, w - 120, 62
    cv.rect(hx, hy - hh, hw, hh, (232, 222, 196))
    cv.poly([(hx - 8, hy - hh), (hx + hw // 2, hy - hh - 22),
             (hx + hw + 8, hy - hh)], (150, 60, 50))
    for i in range(6):
        cv.rect(hx + 12 + i * ((hw - 24) // 6), hy - hh + 12, 16, 26, SKY)
    # flags on the hall
    flag_pole(cv, hx + 26, hy - hh - 20, 26, RED)
    cv.circle(hx + 43, hy - hh - 11, 4, WHITE)
    flag_pole(cv, hx + hw - 56, hy - hh - 20, 26, LEAF)
    cv.circle(hx + hw - 40, hy - hh - 11, 4, WHITE)
    # delegates row
    for i, sh in enumerate((BLUE, RED, GREEN, TEAL, GOLD, (120, 60, 140))):
        figure(cv, hx + 22 + i * ((hw - 44) // 5), hy - 2, sh, h=18)
    # big green leaf badge
    cv.circle(x + w - 46, y + h - 30, 16, LEAF)
    cv.line(x + w - 58, y + h - 18, x + w - 34, y + h - 42, (20, 90, 30))
    cv.line(x + w - 52, y + h - 30, x + w - 40, y + h - 30, (20, 90, 30))


def scene_bahrain(cv, x, y, w, h):
    """Night over Bahrain: missile trails, radar dome, industrial fire."""
    cv.vgrad(x, y, w, h, (16, 22, 52), (64, 44, 84))
    # stars
    for sx, sy in ((18, 12), (52, 30), (96, 10), (150, 22), (210, 14),
                   (260, 34), (300, 12), (350, 26), (410, 10), (120, 44)):
        cv.rect(x + sx % (w - 10), y + sy, 2, 2, WHITE)
    # moon
    cv.circle(x + w - 60, y + 26, 14, (240, 238, 210))
    cv.circle(x + w - 66, y + 22, 12, (16, 22, 52))
    # missile trails arcing down
    for k, (sx, ex) in enumerate(((40, 150), (180, 300), (320, 430))):
        import math
        for t in range(0, 21):
            u = t / 20.0
            px = x + sx + int((ex - sx) * u)
            py = y + 8 + int(58 * math.sin(u * 1.5708))
            cv.rect(px, py, 3, 3, (255, 200, 90) if k != 1 else (255, 120, 60))
        cv.circle(x + ex, y + 8 + 58, 5, (255, 220, 120))
    # sea
    cv.rect(x, y + h - 34, w, 34, SEA_DARK)
    wave_row(cv, x, y + h - 26, w, (90, 160, 200), 3)
    wave_row(cv, x, y + h - 14, w, (60, 130, 180), 3)
    # radar dome + base on the shore
    bx, by = x + 46, y + h - 34
    cv.rect(bx, by - 26, 74, 26, (96, 96, 92))
    cv.circle(bx + 37, by - 26, 22, (200, 200, 196))
    cv.line(bx + 37, by - 48, bx + 52, by - 62, WHITE)
    cv.circle(bx + 52, by - 62, 3, FLAME)
    # industrial plant, on fire
    px = x + w - 150
    cv.rect(px, by - 40, 26, 40, (120, 110, 100))
    cv.rect(px + 34, by - 30, 20, 30, (120, 110, 100))
    cv.rect(px + 62, by - 52, 14, 52, (140, 60, 50))
    cv.rect(px + 84, by - 44, 14, 44, (140, 60, 50))
    flame(cv, px + 13, by - 40, 12)
    flame(cv, px + 44, by - 30, 9)
    smoke(cv, px + 69, by - 66)
    smoke(cv, px + 91, by - 58)
    # small boat
    cv.poly([(x + w // 2 - 20, by + 8), (x + w // 2 + 20, by + 8),
             (x + w // 2 + 12, by + 18), (x + w // 2 - 12, by + 18)], WHITE)
    cv.rect(x + w // 2 - 4, by - 4, 8, 12, RED)


def scene_peru(cv, x, y, w, h):
    """Andes quake: cracked ground, tilted houses, rescuers, dust."""
    cv.vgrad(x, y, w, h, (150, 200, 235), (238, 224, 196))
    sun(cv, x + w - 46, y + 26, 15)
    cloud(cv, x + 60, y + 22, 7)
    # Andes ridge
    cv.poly([(x, y + h - 70), (x + w // 4, y + h - 108),
             (x + w // 2, y + h - 76), (x + 3 * w // 4, y + h - 112),
             (x + w, y + h - 78), (x + w, y + h - 70), (x, y + h - 70)],
            MOUNTAIN2)
    cv.poly([(x + w // 4 - 16, y + h - 108), (x + w // 4, y + h - 96),
             (x + w // 4 + 16, y + h - 108)], WHITE)
    # ground
    cv.rect(x, y + h - 70, w, 70, (196, 164, 120))
    # cracked road
    crack(cv, x + 20, y + h - 70,
          [(30, 12), (-14, 14), (26, 12), (-10, 14), (20, 12)])
    crack(cv, x + w - 60, y + h - 70,
          [(-24, 10), (12, 12), (-20, 12), (10, 12)])
    # tilted houses
    cv.poly([(x + 30, y + h - 70), (x + 30, y + h - 104),
             (x + 66, y + h - 116), (x + 66, y + h - 70)], (190, 90, 60))
    cv.poly([(x + 26, y + h - 104), (x + 48, y + h - 120),
             (x + 70, y + h - 104)], (140, 50, 40))
    cv.rect(x + 88, y + h - 96, 44, 26, (220, 200, 150))
    cv.poly([(x + 84, y + h - 96), (x + 110, y + h - 112),
             (x + 136, y + h - 96)], (160, 60, 40))
    cv.line_w(x + 96, y + h - 96, x + 108, y + h - 108, INK, 2)
    # rubble
    cv.poly([(x + w - 120, y + h - 70), (x + w - 96, y + h - 88),
             (x + w - 66, y + h - 70)], GREY)
    cv.poly([(x + w - 96, y + h - 70), (x + w - 80, y + h - 84),
             (x + w - 58, y + h - 70)], DARKGREY)
    # rescuers with helmets
    figure(cv, x + w - 150, y + h - 6, ORANGE, h=22)
    cv.circle(x + w - 150, y + h - 22, 5, GOLD)
    figure(cv, x + w - 126, y + h - 6, BLUE, h=22)
    cv.circle(x + w - 126, y + h - 22, 5, WHITE)
    smoke(cv, x + w - 90, y + h - 96, (200, 190, 170))


def scene_sparta(cv, x, y, w, h):
    """Sparta II burning in the Gulf of Finland."""
    cv.vgrad(x, y, w, h, (120, 170, 210), (210, 224, 232))
    cloud(cv, x + 60, y + 20, 7)
    cloud(cv, x + w - 90, y + 34, 6)
    # sea
    cv.rect(x, y + h - 46, w, 46, SEA)
    wave_row(cv, x, y + h - 38, w, (120, 190, 230), 4)
    wave_row(cv, x, y + h - 24, w, (90, 160, 210), 4)
    wave_row(cv, x, y + h - 10, w, (60, 130, 190), 4)
    # cargo ship, listing
    sx, sy = x + 56, y + h - 46
    cv.poly([(sx, sy), (sx + 200, sy - 6), (sx + 216, sy + 16),
             (sx + 16, sy + 20)], (40, 40, 40))
    cv.rect(sx + 24, sy - 22, 60, 22, (150, 50, 40))
    cv.rect(sx + 96, sy - 30, 46, 30, (200, 200, 196))
    cv.rect(sx + 152, sy - 18, 30, 18, (150, 50, 40))
    for wx in range(sx + 100, sx + 138, 10):
        cv.rect(wx, sy - 26, 6, 8, SKY)
    # funnel smoke + flames
    smoke(cv, sx + 60, sy - 40)
    flame(cv, sx + 120, sy - 30, 13)
    flame(cv, sx + 166, sy - 18, 10)
    # lifeboat with crew
    cv.poly([(sx + 210, sy + 10), (sx + 252, sy + 10), (sx + 244, sy + 22),
             (sx + 218, sy + 22)], ORANGE)
    figure(cv, sx + 224, sy + 10, RED, h=12)
    figure(cv, sx + 240, sy + 10, BLUE, h=12)
    # coast guard boat
    gx = x + w - 96
    cv.poly([(gx, sy + 6), (gx + 70, sy + 6), (gx + 60, sy + 18),
             (gx + 10, sy + 18)], WHITE)
    cv.rect(gx + 14, sy - 8, 26, 14, RED)
    cv.rect(gx + 44, sy - 4, 4, 10, INK)
    # helicopter
    hx, hy = x + w - 60, y + 30
    cv.ellipse(hx, hy, 13, 6, (60, 60, 66))
    cv.rect(hx - 26, hy - 3, 26, 2, INK)
    cv.rect(hx + 12, hy - 3, 20, 2, INK)
    cv.line(hx + 13, hy + 5, hx + 22, hy + 5, INK)
    cv.circle(hx + 4, hy - 2, 2, SKY)

def scene_kryvyi(cv, x, y, w, h):
    """Night barrage over a Ukrainian city: drones, bursts, skyline."""
    cv.vgrad(x, y, w, h, (12, 16, 40), (70, 40, 70))
    for sx, sy in ((16, 10), (60, 26), (110, 12), (170, 30), (230, 12),
                   (280, 24), (40, 44), (200, 46)):
        cv.rect(x + sx % (w - 8), y + sy, 2, 2, WHITE)
    # drone silhouettes
    for dx, dy in ((50, 34), (150, 20), (250, 40)):
        cv.rect(x + dx - 8, y + dy, 16, 3, (220, 220, 220))
        cv.rect(x + dx - 2, y + dy - 3, 4, 9, (220, 220, 220))
        cv.circle(x + dx - 10, y + dy + 1, 2, RED)
        cv.circle(x + dx + 10, y + dy + 1, 2, RED)
    # explosion bursts: jagged starbursts, not round suns
    for bx, by, r in ((x + 96, y + 62, 14), (x + 216, y + 52, 11),
                      (x + 292, y + 70, 9)):
        import math
        outer = []
        for k in range(12):
            a = k * 0.5236
            rr = r + 7 if k % 2 == 0 else r - 2
            outer.append((bx + int(math.cos(a) * rr),
                          by + int(math.sin(a) * rr)))
        cv.poly(outer, ORANGE)
        inner = []
        for k in range(10):
            a = k * 0.6283
            rr = r // 2 + 3 if k % 2 == 0 else r // 2 - 2
            inner.append((bx + int(math.cos(a) * rr),
                          by + int(math.sin(a) * rr)))
        cv.poly(inner, FLAME)
        cv.circle(bx, by, 3, (255, 240, 160))
        smoke(cv, bx + r + 6, by - r - 4, (110, 100, 100))
    # skyline, one building damaged
    base = y + h
    building(cv, x + 8, base, 44, 52, (30, 30, 44), (255, 210, 90))
    building(cv, x + 60, base, 38, 70, (36, 36, 52), (255, 210, 90))
    cv.poly([(x + 104, base - 70), (x + 118, base - 88), (x + 132, base - 70)],
            (36, 36, 52))
    cv.rect(x + 104, base - 70, 28, 70, (36, 36, 52))
    smoke(cv, x + 118, base - 96)
    building(cv, x + 140, base, 46, 44, (30, 30, 44), (255, 210, 90))
    building(cv, x + 194, base, 40, 62, (36, 36, 52), (255, 210, 90))
    building(cv, x + 242, base, 48, 40, (30, 30, 44), (255, 210, 90))
    cv.rect(x + 294, base - 12, 18, 12, (60, 60, 76))
    # ground glow
    cv.rect(x, base - 4, w, 4, ORANGE)


def scene_sinaloa(cv, x, y, w, h):
    """Desert road in Sinaloa: convoy, burning truck, mountains."""
    cv.vgrad(x, y, w, h, (240, 190, 120), (250, 230, 180))
    sun(cv, x + w - 44, y + 24, 16, (245, 200, 60))
    # mountains
    cv.poly([(x, y + h - 64), (x + w // 3, y + h - 100),
             (x + 2 * w // 3, y + h - 72), (x + w, y + h - 96),
             (x + w, y + h - 64), (x, y + h - 64)], (150, 100, 60))
    # cactus
    cv.rect(x + 18, y + h - 96, 8, 32, GREEN)
    cv.rect(x + 8, y + h - 88, 10, 6, GREEN)
    cv.rect(x + 8, y + h - 82, 6, 10, GREEN)
    cv.rect(x + 26, y + h - 80, 10, 6, GREEN)
    cv.rect(x + 30, y + h - 74, 6, 12, GREEN)
    # road
    cv.rect(x, y + h - 44, w, 44, (80, 78, 74))
    for dx in range(0, w, 36):
        cv.rect(x + dx, y + h - 24, 18, 3, (240, 220, 80))
    # police pickup
    px, py = x + 30, y + h - 44
    cv.rect(px, py - 16, 64, 16, (20, 60, 120))
    cv.rect(px + 40, py - 28, 30, 12, (20, 60, 120))
    cv.rect(px + 46, py - 26, 10, 8, SKY)
    cv.circle(px + 14, py, 7, INK)
    cv.circle(px + 52, py, 7, INK)
    cv.circle(px + 70, py - 30, 3, RED)
    # burning truck ahead
    tx = x + w - 110
    cv.rect(tx, py - 18, 74, 18, (140, 40, 30))
    cv.rect(tx + 54, py - 30, 22, 12, (140, 40, 30))
    cv.circle(tx + 16, py, 7, INK)
    cv.circle(tx + 58, py, 7, INK)
    flame(cv, tx + 30, py - 18, 12)
    flame(cv, tx + 60, py - 30, 9)
    smoke(cv, tx + 36, py - 52)
    # badge star
    cv.circle(x + w - 30, y + 26, 13, GOLD)
    cv.text(x + w - 35, y + 19, "*", 1, INK)


def scene_delhi(cv, x, y, w, h):
    """New Delhi welcome: India Gate, flags of Nepal and India, handshake."""
    cv.vgrad(x, y, w, h, (150, 200, 240), (250, 228, 190))
    sun(cv, x + 44, y + 24, 14)
    cloud(cv, x + w - 110, y + 22, 6)
    cloud(cv, x + 120, y + 40, 5)
    # India Gate
    gx = x + w // 2 - 34
    gy = y + h - 8
    cv.rect(gx, gy - 64, 68, 64, (196, 150, 110))
    cv.poly([(gx - 10, gy - 64), (gx + 34, gy - 82), (gx + 78, gy - 64)],
            (170, 120, 80))
    cv.rect(gx + 24, gy - 48, 20, 48, SKY)
    cv.poly([(gx + 24, gy - 48), (gx + 34, gy - 60), (gx + 44, gy - 48)],
            SKY)
    cv.rect(gx - 6, gy - 8, 80, 8, (150, 100, 60))
    # lawn
    cv.rect(x, gy, w, 8, GREEN)
    # Nepal flag (double pennant) + India flag
    cv.line_w(x + 34, gy, x + 34, gy - 52, INK, 2)
    cv.poly([(x + 35, gy - 52), (x + 35, gy - 26), (x + 62, gy - 38)], RED)
    cv.poly([(x + 35, gy - 38), (x + 35, gy - 26), (x + 56, gy - 32)], RED)
    cv.circle(x + 42, gy - 44, 2, WHITE)
    cv.line_w(x + w - 34, gy, x + w - 34, gy - 52, INK, 2)
    cv.rect(x + w - 33, gy - 52, 30, 9, (255, 153, 51))
    cv.rect(x + w - 33, gy - 43, 30, 9, WHITE)
    cv.rect(x + w - 33, gy - 34, 30, 9, (19, 136, 8))
    cv.circle(x + w - 18, gy - 38, 4, BLUE)
    # two figures shaking hands
    figure(cv, x + w // 2 - 62, gy, (60, 60, 60), h=24)
    figure(cv, x + w // 2 + 62, gy, (120, 40, 40), h=24)
    cv.line_w(x + w // 2 - 58, gy - 16, x + w // 2 - 46, gy - 14, (222, 184, 150), 2)
    cv.line_w(x + w // 2 + 58, gy - 16, x + w // 2 + 46, gy - 14, (222, 184, 150), 2)
    # plane
    cv.ellipse(x + w - 70, y + 44, 18, 6, WHITE)
    cv.poly([(x + w - 88, y + 44), (x + w - 70, y + 36),
             (x + w - 52, y + 44)], WHITE)


def scene_basra(cv, x, y, w, h):
    """Hartha power plant fire in Basra: towers, flames, fire truck."""
    cv.vgrad(x, y, w, h, (200, 170, 140), (240, 210, 170))
    sun(cv, x + w - 40, y + 22, 13, (240, 150, 60))
    # cooling towers
    for tx in (x + 30, x + 92):
        cv.poly([(tx, y + h - 8), (tx + 10, y + h - 78), (tx + 44, y + h - 78),
                 (tx + 54, y + h - 8)], (170, 160, 150))
        cv.ellipse(tx + 27, y + h - 78, 17, 5, (140, 130, 120))
    # plant block
    cv.rect(x + 170, y + h - 52, 70, 44, (120, 110, 100))
    cv.rect(x + 170, y + h - 66, 20, 14, (120, 110, 100))
    cv.rect(x + 210, y + h - 60, 16, 8, (120, 110, 100))
    # flames on the block and tower
    flame(cv, x + 186, y + h - 52, 13)
    flame(cv, x + 224, y + h - 52, 10)
    flame(cv, x + 57, y + h - 78, 11)
    smoke(cv, x + 57, y + h - 104)
    smoke(cv, x + 205, y + h - 92)
    # fire truck
    fx = x + w - 96
    fy = y + h - 8
    cv.rect(fx, fy - 18, 66, 18, RED)
    cv.rect(fx + 44, fy - 30, 24, 12, RED)
    cv.rect(fx + 50, fy - 28, 10, 8, SKY)
    cv.circle(fx + 14, fy, 7, INK)
    cv.circle(fx + 52, fy, 7, INK)
    cv.line_w(fx + 8, fy - 18, fx - 6, fy - 44, WHITE, 2)
    # ground
    cv.rect(x, y + h - 8, w, 8, (150, 120, 80))


# --------------------------------------------------------------- layout -----
def kicker(cv, x, y, s):
    cv.text(x, y, s, 1, RED)


def panel(cv, x, y, w, h, tag, head, cap, scene):
    cv.border(x, y, w, h, INK, 2)
    cv.rect(x + 2, y + 2, w - 4, 18, (232, 222, 196))
    kicker(cv, x + 8, y + 6, tag)
    iy = y + 22
    ih = h - 22 - 62
    scene(cv, x + 2, iy, w - 4, ih)
    hy = iy + ih + 6
    for i, ln in enumerate(cv.wrap(head, w - 16, 2)):
        cv.text(x + 8, hy + i * 16, ln, 2, INK)
    cy = hy + 16 * max(1, len(cv.wrap(head, w - 16, 2)))
    for i, ln in enumerate(cv.wrap(cap, w - 16, 1)):
        cv.text(x + 8, cy + 4 + i * 9, ln, 1, INK_SOFT)


BRIEFS = [
    ("NIGERIA", "24 BODIES FOUND AFTER BOAT CAPSIZE"),
    ("EUROPE", "EU AND INDONESIA SIGN TRADE AND INVESTMENT DEALS"),
    ("EUROPE", "UK AND EU AGREE POST-BREXIT RESET ON FOOD AND CARBON"),
    ("EUROPE", "GEN Z PROTESTS IN 25 COUNTRIES OVER PRICES AND ARMS"),
    ("MARKETS", "US STOCKS SLIDE AS AI SELL-OFF DEEPENS"),
    ("GULF", "HOUTHI MISSILE AT RIYADH INTERCEPTED BY SAUDI DEFENCES"),
    ("GULF", "TANKER HIT BY MINE IN THE STRAIT OF HORMUZ"),
    ("GAZA", "FOUR PALESTINIANS KILLED IN ISRAELI STRIKES"),
    ("EUROPE", "DENMARK EXPELS RUSSIAN DEFENCE ATTACHE OVER PLOT"),
    ("HEALTH", "TRIAL PILL DARAXONRASIB SHOWS HOPE ON PANCREATIC CANCER"),
    ("US", "GUPTA JAILED ABOUT 20 YEARS IN PANNUN MURDER PLOT"),
    ("ASIA", "INDIA AND JAPAN HOLD 2+2 TALKS ON SECURITY"),
    ("ASIA", "QUAD LEADERS MEET IN MANILA; RUBIO HAILS TALKS"),
    ("AMERICAS", "MOSQUITO STUDY CUTS DENGUE IN BRAZILIAN CHILDREN"),
    ("EUROPE", "THREE FRENCH POLICE JAILED OVER 2020 ZECLER ASSAULT"),
    ("ISRAEL", "NETANYAHU INVITES EISENKOT FOR COALITION TALKS"),
    ("US", "TRUMP CALLS PUTIN A FRIEND AFTER SHENZHEN SUMMIT WITH XI"),
    ("UKRAINE", "ZELENSKYY JOINS COALITION OF THE WILLING IN BERLIN"),
    ("ASIA", "FIRST SCO CIVILISATIONAL FORUM OPENS IN NEW DELHI"),
    ("US", "SENATE REJECTS LIMITING PRESIDENTIAL WAR POWERS"),
    ("EUROPE", "FINLAND PROBES SUSPECTED RUSSIAN HELICOPTER INCURSION"),
    ("EUROPE", "ESTONIA ALERTS ON DRONE RISKS; NATO JETS SCRAMBLED"),
    ("EUROPE", "GERMANY PLEDGES 30M EUROS FOR INDUSTRIAL RAMSTEIN"),
    ("CLIMATE", "EU: NO DEAL BETTER THAN A WEAK ONE AT COP31, SAYS HOEKSTRA"),
]

def draw_page():
    cv = Canvas(W, H, PAPER)
    # masthead
    cv.rect(0, 0, W, 4, INK)
    cv.text_c(W // 2, 16, "THE SUNDAY GLOBE", 4, INK)
    cv.rect(16, 62, W - 32, 2, INK)
    cv.text(16, 72, "SUNDAY 22 NOVEMBER 2026", 2, INK)
    cv.text(W - 16 - text_w("32 STORIES - 6 REGIONS", 2), 72,
            "32 STORIES - 6 REGIONS", 2, RED)
    cv.text_c(W // 2, 72, "THE WORLD IN ONE DAY", 1, INK_SOFT)
    cv.rect(16, 92, W - 32, 2, INK)

    # hero row: the two biggest stories
    panel(cv, 16, 100, 488, 232, "CLIMATE - ANTALYA, TURKIYE",
          "COP31: NEW DRAFT AT DAWN, STILL NO DEAL",
          "TALKS RUN PAST DEADLINE AS FOSSIL FUELS STAY OUT OF THE TEXT",
          scene_cop31)
    panel(cv, 520, 100, 488, 232, "CONFLICT - MANAMA, BAHRAIN",
          "IRAN HITS US BASES IN BAHRAIN",
          "TEHRAN SAYS IT STRUCK TWO US SITES; BAHRAIN REPORTS AN INDUSTRIAL FIRE",
          scene_bahrain)

    # second row: disaster and war
    panel(cv, 16, 340, 320, 216, "DISASTER - CENTRAL PERU",
          "QUAKE SHAKES PERU, M6.7",
          "152 HOMES LEFT UNINHABITABLE IN THE ANDES",
          scene_peru)
    panel(cv, 352, 340, 320, 216, "BALTIC SEA - GULF OF FINLAND",
          "DRONE HIT SETS SHIP ABLAZE",
          "SPARTA II BURNS AT SEA; CREW OF 16 ESCAPES",
          scene_sparta)
    panel(cv, 688, 340, 320, 216, "WAR - KRYVYI RIH, UKRAINE",
          "MISSILE HITS ZELENSKYY'S HOME CITY",
          "TWO KILLED, 60 WOUNDED IN 400-DRONE BARRAGE",
          scene_kryvyi)

    # third row: crime, diplomacy, disaster
    panel(cv, 16, 564, 320, 188, "MEXICO - SINALOA",
          "KINGPIN SEIZED IN SINALOA",
          "EL CHAPO ISIDRO CAUGHT; VIOLENCE KILLS 11",
          scene_sinaloa)
    panel(cv, 352, 564, 320, 188, "DIPLOMACY - NEW DELHI",
          "NEPAL PM LANDS IN NEW DELHI",
          "BALENDRA SHAH BEGINS FIRST STATE VISIT TO INDIA",
          scene_delhi)
    panel(cv, 688, 564, 320, 188, "DISASTER - BASRA, IRAQ",
          "FIRE AT BASRA POWER PLANT",
          "FOUR DEAD, 35 HURT AT THE HARTHA STATION",
          scene_basra)

    # briefs index
    by = 760
    cv.rect(16, by, W - 32, 2, INK)
    cv.text(16, by + 8, "AROUND THE WORLD IN BRIEF", 2, INK)
    cv.text(W - 16 - text_w("24 MORE STORIES", 1), by + 11,
            "24 MORE STORIES", 1, RED)
    cv.rect(16, by + 28, W - 32, 1, INK_SOFT)
    col_w = 320
    for idx, (tag, txt) in enumerate(BRIEFS):
        col = idx // 8
        row = idx % 8
        bx = 16 + col * (col_w + 16)
        yy = by + 38 + row * 22
        cv.text(bx, yy, tag, 1, RED)
        lines = cv.wrap(txt, col_w - text_w(tag + "  ", 1), 1)
        lx = bx + text_w(tag + "  ", 1)
        for j, ln in enumerate(lines[:2]):
            cv.text(lx, yy + j * 9, ln, 1, INK)

    # footer
    cv.rect(16, 988, W - 32, 2, INK)
    cv.text_c(W // 2, 996, "ALL STORIES FROM SUNDAY 22 NOVEMBER 2026", 1, INK_SOFT)
    cv.rect(0, H - 4, W, 4, INK)
    return cv


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    data = png_bytes(draw_page())
    with open(os.path.join(outdir, "entry.png"), "wb") as f:
        f.write(data)
    return 0


if __name__ == "__main__":
    sys.exit(main())
