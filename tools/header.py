"""GitHub profile header for Christian Gennari.

A year of GitHub contributions, week by week, lands on a lever as the contribution graph
and lifts the world. Then the Archimedes line is typed out as a code comment.
Transparent APNG, so it sits on any GitHub theme. Run: python3 header.py [light|dark] [--frames a,b,c]
"""
import json, math, sys
from PIL import Image, ImageDraw, ImageFont

W, H, SS = 880, 356, 3
MS = 40
LM = 64                    # left margin, shared by the name, the ground and the comment
GH = {  # GitHub's own colours
  'light': dict(fg=(31,35,40), muted=(89,99,110), line=(209,217,224), cmt=(89,99,110), kw=(207,34,46), fn=(130,80,223),
                cells=[(235,237,240),(155,233,168),(64,196,99),(48,161,78),(33,110,57)]),
  'dark':  dict(fg=(230,237,243), muted=(145,152,161), line=(61,68,77), cmt=(145,152,161), kw=(255,123,114), fn=(210,168,255),
                cells=[(33,40,48),(14,68,41),(0,109,50),(38,166,65),(57,211,83)]),
}
cal = json.load(open('/tmp/ghgif/contrib.json'))['data']['user']['contributionsCollection']['contributionCalendar']
weeks = [[d['contributionCount'] for d in w['contributionDays']] for w in cal['weeks']]
weeks = weeks[-53:]
def lvl(c): return 0 if c == 0 else 1 if c < 6 else 2 if c < 16 else 3 if c < 33 else 4
week_w = [sum(w) for w in weeks]

F_NAME = ImageFont.truetype('/tmp/ghgif/Literata-36.ttf', 30 * SS)
F_MONO = ImageFont.truetype('/home/dev/.local/share/fonts/JetBrainsMono-Regular.ttf', 13 * SS)
F_MONO_S = ImageFont.truetype('/home/dev/.local/share/fonts/JetBrainsMono-Regular.ttf', 12 * SS)

GROUND = 246
PIV = (318, GROUND - 22)
LEFT, RIGHT = 120, 470
CELL, GAP = 6, 2
A0 = -math.asin((GROUND - PIV[1]) / LEFT)
A1 = math.asin((GROUND - PIV[1] - 2) / RIGHT)
N = len(weeks)
DROP_EVERY, FALL = 2, 13
LAST = (N - 1) * DROP_EVERY + FALL
TYPE_START = LAST + 18
LINE1 = '// Give me a place to stand and a working API,'
LINE2 = '// and I shall move the world. (Archimedes)'
CODE = [('await', 'kw'), (' world.', 'fg'), ('MoveAsync', 'fn'), ('(lever);', 'fg')]
LINE3 = ''.join(t for t, _ in CODE)
TYPE_LEN = len(LINE1) + len(LINE2) + len(LINE3)
TYPE_END = TYPE_START + math.ceil(TYPE_LEN / 2.2)
HOLD_END = TYPE_END + 90
TOTAL = HOLD_END + 24

def P(d, n, a):
    c, s = math.cos(a), math.sin(a)
    return (PIV[0] + d * c + n * s, PIV[1] + d * s - n * c)
def ease(t): t = max(0, min(1, t)); return t * t * (3 - 2 * t)

def angles():
    tot = sum(week_w); out = []; a = A0
    for f in range(TOTAL):
        if f >= HOLD_END:
            target = A1 + (A0 - A1) * ease((f - HOLD_END) / 24); a = target
        else:
            w = sum(week_w[i] for i in range(N) if f >= i * DROP_EVERY + FALL)
            k = ease(max(0, (w / tot - .3) / .7))
            a += (A0 + (A1 - A0) * k - a) * .14
        out.append(a)
    return out

def frame(f, th, angs):
    s = SS
    im = Image.new('RGBA', (W * s, H * s), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    ang = angs[f]
    out = ease((f - HOLD_END) / 24) if f >= HOLD_END else 0      # fade for the loop
    def c(rgb, a=1.0): return rgb + (int(255 * a * (1 - out) if a < 9 else 255),)
    # name and role
    d.text((LM * s, 48 * s), 'Christian Gennari', font=F_NAME, fill=th['fg'] + (255,), anchor='ls')
    d.text((LM * s, 72 * s), '.NET developer', font=F_MONO_S, fill=th['muted'] + (255,), anchor='ls')
    # ground, fulcrum, plank
    d.line([(LM * s, GROUND * s), ((W - LM) * s, GROUND * s)], fill=th['line'] + (255,), width=s)
    d.polygon([(PIV[0] * s, PIV[1] * s), ((PIV[0] - 18) * s, GROUND * s), ((PIV[0] + 18) * s, GROUND * s)], fill=th['muted'] + (255,))
    pts = [P(-LEFT, 0, ang), P(RIGHT, 0, ang), P(RIGHT, 3, ang), P(-LEFT, 3, ang)]
    d.polygon([(x * s, y * s) for x, y in pts], fill=th['fg'] + (255,))
    # the world
    r = 20; cx, cy = P(-LEFT + 28, 3 + r, ang)
    for box, wd in (((cx - r, cy - r, cx + r, cy + r), 1.5), ((cx - r * .42, cy - r, cx + r * .42, cy + r), 1)):
        d.ellipse([v * s for v in box], outline=th['fg'] + (255,), width=int(wd * s))
    d.line([((cx - r) * s, cy * s), ((cx + r) * s, cy * s)], fill=th['fg'] + (255,), width=s)
    # the contribution graph, one week at a time; newest week lands nearest the fulcrum
    col_w = CELL + GAP
    for i, days in enumerate(weeks):
        t0 = i * DROP_EVERY
        if f < t0: continue
        dist = RIGHT - 8 - (i + 1) * col_w + GAP
        falling = f < t0 + FALL
        tf = (f - t0) / FALL
        for k, cnt in enumerate(days):
            col = th['cells'][lvl(cnt)] + (int(255 * (1 - out)),)
            n0 = 3 + 1 + (6 - k) * col_w                    # Sunday at the top, like GitHub
            if falling:
                bx, by = P(dist, n0, ang)
                lift = (1 - tf * tf) * 46
                col = col[:3] + (int(col[3] * ease(tf * 1.6)),)
                q = [(bx, by - lift), (bx + CELL, by - lift), (bx + CELL, by - lift - CELL), (bx, by - lift - CELL)]
            else:
                q = [P(dist, n0, ang), P(dist + CELL, n0, ang), P(dist + CELL, n0 + CELL, ang), P(dist, n0 + CELL, ang)]
            d.polygon([(x * s, y * s) for x, y in q], fill=col)
    # the comment types itself out once the world is up
    if f >= TYPE_START:
        n = int((f - TYPE_START) * 2.2)
        l1, l2 = LINE1[:n], LINE2[:max(0, n - len(LINE1))]
        n3 = max(0, n - len(LINE1) - len(LINE2))
        a = 1 - out
        x0 = LM * s
        d.text((x0, 290 * s), l1, font=F_MONO, fill=th['cmt'] + (int(255 * a),), anchor='ls')
        d.text((x0, 312 * s), l2, font=F_MONO, fill=th['cmt'] + (int(255 * a),), anchor='ls')
        xx, left = x0, n3
        for tok, role in CODE:
            part = tok[:max(0, left)]; left -= len(tok)
            if part: d.text((xx, 334 * s), part, font=F_MONO, fill=th[role] + (int(255 * a),), anchor='ls')
            xx += d.textlength(tok, font=F_MONO)
        typing = TYPE_START <= f < TYPE_END + 30 and (f // 8) % 2 == 0
        if typing:
            if n3 > 0: txt, yy = LINE3[:n3], 334
            elif n > len(LINE1): txt, yy = l2, 312
            else: txt, yy = l1, 290
            cx2 = x0 + d.textlength(txt, font=F_MONO); cy2 = yy * s
            d.rectangle([cx2 + 2 * s, cy2 - 12 * s, cx2 + 9 * s, cy2 + 2 * s], fill=th['muted'] + (int(200 * a),))
    return im.convert('RGBa').resize((W, H), Image.LANCZOS).convert('RGBA')

def main():
    themes = [a for a in sys.argv[1:] if a in GH] or list(GH)
    pick = next((a.split('=')[1] for a in sys.argv if a.startswith('--frames=')), None)
    for t in themes:
        th = GH[t]; angs = angles()
        if pick:
            for f in map(int, pick.split(',')):
                frame(f, th, angs).save(f'/tmp/ghgif/v2/f-{t}-{f}.png')
            continue
        frames = [frame(f, th, angs) for f in range(TOTAL)]
        frames[0].save(f'/tmp/ghgif/v2/header-{t}.webp', save_all=True, append_images=frames[1:], duration=MS, loop=0, quality=82, alpha_quality=90, method=6, minimize_size=True)
        print(t, TOTAL, 'frames')
    print('TOTAL', TOTAL, 'LAST', LAST, 'TYPE_END', TYPE_END)
main()
