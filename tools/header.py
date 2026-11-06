"""GitHub profile header for Christian Gennari, v3.

A year of GitHub contributions falls day by day onto a lever as the contribution graph,
tips it with a spring, and lifts a slowly spinning world. Then the Archimedes line is typed
as a code comment, followed by one line of C#. Transparent animated WebP for any GitHub theme.
Run: python3 header.py [light|dark] [--frames=a,b,c]
"""
import json, math, random, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, SS = 880, 356, 3
MS = 33
LM = 64
GH = {
  'light': dict(fg=(31,35,40), muted=(89,99,110), cmt=(89,99,110), kw=(207,34,46), fn=(130,80,223),
                cells=[(235,237,240),(155,233,168),(64,196,99),(48,161,78),(33,110,57)],
                shadow=(31,35,40), shadow_a=.16, globe_fill=(246,248,250), globe_line=(89,99,110), globe_shade=(31,35,40)),
  'dark':  dict(fg=(230,237,243), muted=(145,152,161), cmt=(145,152,161), kw=(255,123,114), fn=(210,168,255),
                cells=[(45,51,59),(14,68,41),(0,109,50),(38,166,65),(57,211,83)],
                shadow=(0,0,0), shadow_a=.45, globe_fill=(45,51,59), globe_line=(145,152,161), globe_shade=(0,0,0)),
}
cal = json.load(open('/tmp/ghgif/contrib.json'))['data']['user']['contributionsCollection']['contributionCalendar']
weeks = [[d['contributionCount'] for d in w['contributionDays']] for w in cal['weeks']][-53:]
def lvl(c): return 0 if c == 0 else 1 if c < 6 else 2 if c < 16 else 3 if c < 33 else 4
week_w = [sum(w) for w in weeks]

F_NAME = ImageFont.truetype('/tmp/ghgif/Literata-36.ttf', 30 * SS)
F_MONO = ImageFont.truetype('/home/dev/.local/share/fonts/JetBrainsMono-Regular.ttf', 13 * SS)
F_MONO_S = ImageFont.truetype('/home/dev/.local/share/fonts/JetBrainsMono-Regular.ttf', 12 * SS)

GROUND = 246
PIV = (318, GROUND - 22)
LEFT, RIGHT = 120, 470
THICK = 5
CELL, GAP = 6, 2
A0 = -math.asin((GROUND - PIV[1]) / LEFT)
A1 = math.asin((GROUND - PIV[1] - THICK + 1) / RIGHT)
N = len(weeks)
G = 0.62                          # gravity, px per frame squared
rnd = random.Random(11)
cells = []
for i, days in enumerate(weeks):
    for k, cnt in enumerate(days):
        t0 = i * 2.6 + rnd.uniform(0, 9)               # weeks arrive in order, days rain in loosely
        h = rnd.uniform(70, 150)                       # drop height above the landing spot
        cells.append(dict(i=i, k=k, cnt=cnt, t0=t0, h=h, spin=rnd.uniform(-9, 9), drift=rnd.uniform(-10, 10)))

def fall(c, t):
    """height above the landing spot, rotation and squash at time t after the drop starts; None when resting"""
    n, v, rot, w, tt, bounces = c['h'], 0.0, rnd_rot(c), c['spin'], 0, 0
    squash = 1.0
    while tt < t:
        v += G; n -= v; rot += w; tt += 1
        if n <= 0:
            n = 0
            if bounces < 2 and v > 2.2:
                v = -v * (.28 if bounces == 0 else .18); w *= -.35; bounces += 1
                squash = .74
            else:
                return dict(n=0, rot=0, squash=1, landed_at=tt) if tt < t else dict(n=0, rot=rot * .3, squash=squash, landed_at=tt)
        squash += (1 - squash) * .45
    return dict(n=n, rot=rot, squash=squash, landed_at=None)

def rnd_rot(c): return c['spin'] * 2.2

def land_time(c):
    n, v, tt, bounces = c['h'], 0.0, 0, 0
    while True:
        v += G; n -= v; tt += 1
        if n <= 0:
            if bounces < 2 and v > 2.2: v = -v * (.28 if bounces == 0 else .18); bounces += 1; n = 0
            else: return c['t0'] + tt
for c in cells: c['tl'] = land_time(c)
FALL = 0
LAST = max(c['tl'] for c in cells)
TYPE_START = int(LAST) + 34
LINE1 = '// Give me a place to stand and a working API,'
LINE2 = '// and I shall move the world. (Archimedes)'
CODE = [('await', 'kw'), (' world.', 'fg'), ('MoveAsync', 'fn'), ('(lever);', 'fg')]
LINE3 = ''.join(t for t, _ in CODE)
TYPE_LEN = len(LINE1) + len(LINE2) + len(LINE3)
TYPE_END = TYPE_START + math.ceil(TYPE_LEN / 2.2)
HOLD_END = TYPE_END + 90
OUTRO = 26
TOTAL = HOLD_END + OUTRO

def P(d, n, a):
    c, s = math.cos(a), math.sin(a)
    return (PIV[0] + d * c + n * s, PIV[1] + d * s - n * c)
def ease(t): t = max(0, min(1, t)); return t * t * (3 - 2 * t)
def easeout(t): t = max(0, min(1, t)); return 1 - (1 - t) ** 3

def angles():
    """Lever physics: torque from the landed squares against the world, ground contact at both ends."""
    col_w = CELL + GAP
    total = sum((1 + c['cnt'] * .9) * (RIGHT - 10 - (c['i'] + 1) * col_w) for c in cells)
    world_torque = total * .84                                  # the world is heavy: it takes most of a year to move it
    a, v, out = A0, 0.0, []
    landed_prev = 0
    for f in range(TOTAL):
        if f >= HOLD_END:
            a = A1 + (A0 - A1) * ease((f - HOLD_END) / OUTRO); out.append(a); continue
        torque = -world_torque
        landed = 0
        for c in cells:
            if f >= c['tl']:
                dist = RIGHT - 10 - (c['i'] + 1) * col_w
                torque += (1 + c['cnt'] * .9) * dist * 1.0
                landed += 1
        kick = (landed - landed_prev) * 0.0009                 # each landing nudges the lever
        landed_prev = landed
        acc = torque / total * .011 - v * .06
        v += acc + kick
        a += v
        if a <= A0: a = A0; v = -v * .22 if v < 0 else v       # short end rests on the ground
        if a >= A1: a = A1; v = -v * .3 if v > 0 else v        # long end lands with a small bounce
        out.append(a)
    return out

def rrect(cx, cy, w, h, ang, r, sx=1, sy=1):
    """rounded rectangle polygon centred at (cx, cy), rotated by ang (radians), scaled by sx, sy"""
    w, h = w * sx, h * sy; r = min(r, w / 2, h / 2); pts = []
    for qx, qy, a0 in ((w/2 - r, -h/2 + r, -90), (w/2 - r, h/2 - r, 0), (-w/2 + r, h/2 - r, 90), (-w/2 + r, -h/2 + r, 180)):
        for j in range(5):
            t = math.radians(a0 + j * 22.5)
            pts.append((qx + r * math.cos(t), qy + r * math.sin(t)))
    c, s = math.cos(ang), math.sin(ang)
    return [(cx + x * c - y * s, cy + x * s + y * c) for x, y in pts]

_SHADE = {}
def shade_tile(th, r, s):
    key = (th['globe_shade'], r, s)
    if key not in _SHADE:
        n = 2 * r * s; t = Image.new('RGBA', (n, n), th['globe_shade'] + (0,)); px = t.load()
        for yy in range(n):
            for xx in range(n):
                dx, dy = (xx - n / 2) / (n / 2), (yy - n / 2) / (n / 2)
                if dx * dx + dy * dy > 1: continue
                lx, ly = dx + .45, dy + .45                       # distance from the light, top left
                a = max(0, min(1, (math.hypot(lx, ly) - .55) / 1.1))
                px[xx, yy] = th['globe_shade'] + (int(255 * .38 * a * a),)
        _SHADE[key] = t
    return _SHADE[key]

def globe(d, cx, cy, r, spin, th, s, im=None):
    """an orthographic sphere with a 23 degree tilt, spinning around its axis"""
    tilt = math.radians(23)
    def proj(lat, lon):
        x = math.cos(lat) * math.sin(lon); y = math.sin(lat); z = math.cos(lat) * math.cos(lon)
        y2 = y * math.cos(tilt) - z * math.sin(tilt); z2 = y * math.sin(tilt) + z * math.cos(tilt)
        return cx + r * x, cy - r * y2, z2
    d.ellipse([(cx - r) * s, (cy - r) * s, (cx + r) * s, (cy + r) * s], fill=th['globe_fill'] + (255,))
    lines = []
    for lon_deg in range(0, 180, 30):
        lon = math.radians(lon_deg) + spin
        for side in (0, math.pi):
            lines.append([proj(math.radians(la), lon + side) for la in range(-90, 91, 6)])
    for lat_deg in (-60, -30, 0, 30, 60):
        lines.append([proj(math.radians(lat_deg), math.radians(lo)) for lo in range(0, 361, 6)])
    for ln in lines:
        seg = []
        for x, y, z in ln + [(None, None, -1)]:
            if z is not None and z > 0: seg.append((x * s, y * s))
            else:
                if len(seg) > 1: d.line(seg, fill=th['globe_line'] + (150,), width=max(1, int(.8 * s)), joint='curve')
                seg = []
    if im is not None: im.alpha_composite(shade_tile(th, r, s), (int((cx - r) * s), int((cy - r) * s)))
    d.ellipse([(cx - r) * s, (cy - r) * s, (cx + r) * s, (cy + r) * s], outline=th['fg'] + (255,), width=int(1.4 * s))

def shadow_layer(f, ang, th, gy):
    """soft contact shadows at 1x, blurred, then scaled up"""
    sh = Image.new('L', (W, H), 0); d = ImageDraw.Draw(sh)
    a = int(255 * th['shadow_a'])
    d.ellipse([PIV[0] - 26, GROUND - 3, PIV[0] + 26, GROUND + 3], fill=a)                 # under the fulcrum
    ex, ey = P(RIGHT, 0, ang); gap = max(0, GROUND - ey)
    k = max(0, 1 - gap / 70)
    d.ellipse([ex - 70, GROUND - 2, ex + 4, GROUND + 3], fill=int(a * .7 * k))           # where the long end meets the ground
    gx, gy2 = P(-LEFT + 30, THICK + 21, ang); lift = max(0, GROUND - (gy2 + 21))
    k2 = max(0, 1 - lift / 18)
    d.ellipse([gx - 22 * (1 + (1 - k2) * .4), GROUND - 2, gx + 22 * (1 + (1 - k2) * .4), GROUND + 3], fill=int(a * .8 * k2))
    sh = sh.filter(ImageFilter.GaussianBlur(4)).resize((W * SS, H * SS), Image.BILINEAR)
    lay = Image.new('RGBA', (W * SS, H * SS), th['shadow'] + (0,)); lay.putalpha(sh)
    return lay

def frame(f, th, angs, sub):
    s = SS
    ang = angs[f]
    out = ease((f - HOLD_END) / OUTRO) if f >= HOLD_END else 0
    im = Image.new('RGBA', (W * s, H * s), (0, 0, 0, 0))
    im.alpha_composite(shadow_layer(f, ang, th, GROUND))
    d = ImageDraw.Draw(im)
    d.text((LM * s, 48 * s), 'Christian Gennari', font=F_NAME, fill=th['fg'] + (255,), anchor='ls')
    d.text((LM * s, 72 * s), sub, font=F_MONO_S, fill=th['muted'] + (255,), anchor='ls')
    # fulcrum: a softened triangle
    tip, bl, br = (PIV[0], PIV[1] + 1), (PIV[0] - 17, GROUND), (PIV[0] + 17, GROUND)
    d.polygon([(x * s, y * s) for x, y in (tip, br, bl)], fill=th['muted'] + (255,))
    d.ellipse([(PIV[0] - 3) * s, (PIV[1] - 1) * s, (PIV[0] + 3) * s, (PIV[1] + 5) * s], fill=th['muted'] + (255,))
    # plank with rounded ends
    mid = P((RIGHT - LEFT) / 2, THICK / 2, ang)
    d.polygon([(x * s, y * s) for x, y in rrect(mid[0], mid[1], LEFT + RIGHT, THICK, ang, THICK / 2)], fill=th['fg'] + (255,))
    # the world, resting on the short end and spinning slowly
    r = 21; gx, gy = P(-LEFT + 30, THICK + r, ang)
    globe(d, gx, gy, r, f * 0.035, th, s, im)
    # the contribution graph, a day at a time; newest week nearest the fulcrum, Sunday on top as on GitHub
    col_w = CELL + GAP
    for c in cells:
        t = f - c['t0']
        if t < 0: continue
        dist = RIGHT - 10 - (c['i'] + 1) * col_w + GAP + CELL / 2
        n0 = THICK + 1 + (6 - c['k']) * col_w + CELL / 2
        st = fall(c, t)
        x, y = P(dist + c['drift'] * min(1, st['n'] / c['h']), n0 + st['n'], ang)
        col = th['cells'][lvl(c['cnt'])]
        alpha = (1 - out) * min(1, t / 5)
        sq = st['squash']
        poly = rrect(x, y, CELL, CELL, ang + math.radians(st['rot']), 1.4, 1 / max(.7, sq) ** .5, sq)
        d.polygon([(px * s, py * s) for px, py in poly], fill=col + (int(255 * alpha),))
    # the comment types itself, then one line of C#
    if f >= TYPE_START:
        n = int((f - TYPE_START) * 2.2)
        l1, l2 = LINE1[:n], LINE2[:max(0, n - len(LINE1))]
        n3 = max(0, n - len(LINE1) - len(LINE2))
        a = 1 - out; x0 = LM * s
        d.text((x0, 290 * s), l1, font=F_MONO, fill=th['cmt'] + (int(255 * a),), anchor='ls')
        d.text((x0, 312 * s), l2, font=F_MONO, fill=th['cmt'] + (int(255 * a),), anchor='ls')
        xx, left = x0, n3
        for tok, role in CODE:
            part = tok[:max(0, left)]; left -= len(tok)
            if part: d.text((xx, 334 * s), part, font=F_MONO, fill=th[role] + (int(255 * a),), anchor='ls')
            xx += d.textlength(tok, font=F_MONO)
        if (f // 8) % 2 == 0 and f < HOLD_END:
            if n3 > 0: txt, yy = LINE3[:n3], 334
            elif n > len(LINE1): txt, yy = l2, 312
            else: txt, yy = l1, 290
            cx2 = x0 + d.textlength(txt, font=F_MONO); cy2 = yy * s
            d.rectangle([cx2 + 2 * s, cy2 - 12 * s, cx2 + 9 * s, cy2 + 2 * s], fill=th['muted'] + (int(200 * a),))
    return im.convert('RGBa').resize((W, H), Image.LANCZOS).convert('RGBA')

def main():
    sub = 'Software developer'
    themes = [a for a in sys.argv[1:] if a in GH] or list(GH)
    pick = next((a.split('=')[1] for a in sys.argv if a.startswith('--frames=')), None)
    for t in themes:
        th = GH[t]; angs = angles()
        if pick:
            for f in map(int, pick.split(',')): frame(f, th, angs, sub).save(f'/tmp/ghgif/v4/f-{t}-{f}.png')
            continue
        frames = [frame(f, th, angs, sub) for f in range(TOTAL)]
        frames[0].save(f'/tmp/ghgif/v4/header-{t}.webp', save_all=True, append_images=frames[1:], duration=MS, loop=0,
                       quality=84, alpha_quality=92, method=6, minimize_size=True)
        print(t, TOTAL, 'frames')
    print('TOTAL', TOTAL, 'LAST', int(LAST), 'TYPE_START', TYPE_START, 'HOLD_END', HOLD_END)
main()
