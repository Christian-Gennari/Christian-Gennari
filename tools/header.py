"""GitHub header for Christian Gennari: a year of work, week by week, tips a lever and lifts the world."""
import json, math, sys
from PIL import Image, ImageDraw, ImageFont

W, H, SS = 800, 400, 3
MS = 40
THEMES = {
  'light': dict(bg=(238,240,236), ink=(43,48,45), soft=(95,103,98), bar=[(201,217,207),(143,179,160),(93,138,118),(59,102,86)], world=(59,102,86)),
  'dark':  dict(bg=(29,27,24), ink=(231,224,211), soft=(150,142,127), bar=[(74,66,53),(122,106,76),(169,140,94),(212,178,124)], world=(212,178,124)),
}
cal = json.load(open('/tmp/ghgif/contrib.json'))['data']['user']['contributionsCollection']['contributionCalendar']
weeks = [sum(d['contributionCount'] for d in w['contributionDays']) for w in cal['weeks']]
mx = max(weeks)
def lvl(v):
    q = v / mx
    return 0 if q < .15 else 1 if q < .35 else 2 if q < .6 else 3
heights = [0 if v == 0 else 6 + 58 * math.sqrt(v / mx) for v in weeks]

F_NAME = ImageFont.truetype('/tmp/ghgif/Literata-36.ttf', 34 * SS)
F_QUOTE = ImageFont.truetype('/tmp/ghgif/Literata-Italic-24.ttf', 21 * SS)
F_SMALL = ImageFont.truetype('/tmp/ghgif/Literata-12.ttf', 14 * SS)

GROUND = 262                      # y of the ground line
PIV = (232, GROUND - 30)          # fulcrum tip
LEFT, RIGHT = 120, 470            # plank lengths from the pivot (short arm left, long arm right)
BAR_W, GAP = 7, 0.6
A0 = -math.asin((GROUND - PIV[1]) / LEFT)        # start: the short end rests on the ground
A1 = math.asin((GROUND - PIV[1] - 2) / RIGHT)    # end: the long end rests on the ground
DROP_EVERY, FALL = 2, 14
N = len(weeks)
LAST_LAND = (N - 1) * DROP_EVERY + FALL
SETTLE, HOLD, BACK = 26, 95, 22
TOTAL = LAST_LAND + SETTLE + HOLD + BACK

def P(d, n, ang):
    """point at distance d along the plank (right positive) and n along its upward normal"""
    c, s = math.cos(ang), math.sin(ang)
    return (PIV[0] + d * c + n * s, PIV[1] + d * s - n * c)

def ease(t): return t * t * (3 - 2 * t)

def angle_at(f):
    if f >= LAST_LAND + SETTLE + HOLD:                       # drift back to the start for a seamless loop
        t = (f - (LAST_LAND + SETTLE + HOLD)) / BACK
        return A1 + (A0 - A1) * ease(min(1, t))
    landed = sum(1 for i in range(N) if f >= i * DROP_EVERY + FALL and heights[i] > 0)
    w = sum(heights[i] for i in range(N) if f >= i * DROP_EVERY + FALL)
    frac = w / sum(heights)
    # the lever waits until enough weight has gathered, then moves; smoothed with a short lag
    k = max(0.0, (frac - .35) / .65)
    return A0 + (A1 - A0) * ease(min(1, k))

def smooth_angles():
    raw = [angle_at(f) for f in range(TOTAL)]
    out, a = [], raw[0]
    for f, r in enumerate(raw):
        a += (r - a) * (0.12 if f < LAST_LAND + SETTLE + HOLD else 1)
        out.append(a)
    return out

def render(theme):
    th = THEMES[theme]
    angs = smooth_angles()
    frames = []
    s = SS
    for f in range(TOTAL):
        im = Image.new('RGB', (W * s, H * s), th['bg']); d = ImageDraw.Draw(im)
        ang = angs[f]
        back = f >= LAST_LAND + SETTLE + HOLD
        fade_bars = 1 - ease(min(1, (f - (LAST_LAND + SETTLE + HOLD)) / BACK)) if back else 1
        # name
        d.text((W * s // 2, 52 * s), 'Christian Gennari', font=F_NAME, fill=th['ink'], anchor='ms')
        # ground and fulcrum
        d.line([(60 * s, GROUND * s), (W * s - 60 * s, GROUND * s)], fill=th['soft'], width=max(1, s // 2))
        d.polygon([(PIV[0] * s, PIV[1] * s), ((PIV[0] - 21) * s, GROUND * s), ((PIV[0] + 21) * s, GROUND * s)], fill=th['ink'])
        # plank
        a, b = P(-LEFT, 0, ang), P(RIGHT, 0, ang); a2, b2 = P(-LEFT, 4, ang), P(RIGHT, 4, ang)
        d.polygon([(x * s, y * s) for x, y in (a, b, b2, a2)], fill=th['ink'])
        # the world on the short end
        r = 23
        cx, cy = P(-LEFT + 30, 4 + r, ang)
        d.ellipse([(cx - r) * s, (cy - r) * s, (cx + r) * s, (cy + r) * s], outline=th['world'], width=int(1.6 * s))
        d.ellipse([(cx - r * .42) * s, (cy - r) * s, (cx + r * .42) * s, (cy + r) * s], outline=th['world'], width=max(1, s))
        d.line([((cx - r) * s, cy * s), ((cx + r) * s, cy * s)], fill=th['world'], width=max(1, s))
        # the year, week by week, on the long end (latest week nearest the fulcrum)
        for i, h in enumerate(heights):
            if h <= 0: continue
            t0 = i * DROP_EVERY
            if f < t0: continue
            dist = RIGHT - 6 - (i + 1) * (BAR_W + GAP) + BAR_W
            col = th['bar'][lvl(weeks[i])]
            if fade_bars < 1: col = tuple(int(c * fade_bars + bgc * (1 - fade_bars)) for c, bgc in zip(col, th['bg']))
            if f < t0 + FALL:
                bx, by = P(dist, 4, ang)
                tf = (f - t0) / FALL
                yoff = -(1 - tf * tf) * (by + 20)
                pts = [(bx, by + yoff), (bx + BAR_W, by + yoff), (bx + BAR_W, by + yoff - h), (bx, by + yoff - h)]
            else:
                pts = [P(dist, 4, ang), P(dist + BAR_W, 4, ang), P(dist + BAR_W, 4 + h, ang), P(dist, 4 + h, ang)]
            d.polygon([(x * s, y * s) for x, y in pts], fill=col)
        # the quote arrives once the world is up
        qa = ease(max(0, min(1, (f - (LAST_LAND + 4)) / 22))) * (1 - ease(min(1, (f - (LAST_LAND + SETTLE + HOLD)) / 12)) if back else 1)
        if qa > 0:
            mix = lambda c: tuple(int(cc * qa + bg * (1 - qa)) for cc, bg in zip(c, th['bg']))
            d.text((W * s // 2, 322 * s), '“Give me a place to stand and a working API,', font=F_QUOTE, fill=mix(th['ink']), anchor='ms')
            d.text((W * s // 2, 350 * s), 'and I shall move the world.”', font=F_QUOTE, fill=mix(th['ink']), anchor='ms')
            d.text((W * s // 2, 380 * s), 'Archimedes', font=F_SMALL, fill=mix(th['soft']), anchor='ms')
        frames.append(im.resize((W, H), Image.LANCZOS).convert('P', palette=Image.ADAPTIVE, colors=48))
    dur = [MS] * TOTAL
    out = f'/tmp/ghgif/lever-{theme}.gif'
    frames[0].save(out, save_all=True, append_images=frames[1:], duration=dur, loop=0, optimize=True)
    print(out, TOTAL, 'frames')

for t in sys.argv[1:] or THEMES: render(t)
