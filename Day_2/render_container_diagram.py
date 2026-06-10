"""Render the BookSwap C4 Container diagram (Level 2) to PNG."""
import math
from PIL import Image, ImageDraw, ImageFont

S = 2
W, H = 1640 * S, 1080 * S

PERSON, PERSON_S = (8, 66, 123), (7, 59, 111)
CONTAINER, CONTAINER_S = (23, 130, 195), (15, 90, 140)     # our containers (blue)
STORE, STORE_S = (45, 125, 90), (30, 95, 65)               # data stores (green)
EXT, EXT_S = (140, 140, 140), (108, 108, 108)              # external (grey)
WHITE, INK = (255, 255, 255), (40, 40, 40)
SYNC = (70, 70, 70)        # solid sync arrows
ASYNC = (208, 110, 20)     # dashed async arrows (orange)

img = Image.new("RGB", (W, H), WHITE)
d = ImageDraw.Draw(img)

def font(size, bold=False):
    p = r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf"
    try:
        return ImageFont.truetype(p, size * S)
    except OSError:
        return ImageFont.load_default()

F_TITLE, F_HEAD, F_TECH, F_BODY, F_LBL, F_LEG = font(22, True), font(13, True), font(10, True), font(10), font(9), font(11)

def wrap(text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def block(cx, cy, lines_spec, max_w):
    """lines_spec: list of (text, font, color). Centered block around (cx,cy)."""
    rendered = []
    for text, fnt, color in lines_spec:
        for ln in wrap(text, fnt, max_w):
            lh = (fnt.getbbox("Ay")[3] - fnt.getbbox("Ay")[1]) + 5 * S
            rendered.append((ln, fnt, color, lh))
    total = sum(lh for *_ , lh in rendered)
    y = cy - total / 2
    for ln, fnt, color, lh in rendered:
        d.text((cx, y), ln, font=fnt, fill=color, anchor="ma")
        y += lh

def box(x0, y0, x1, y1, fill, stroke, name, tech, resp):
    d.rounded_rectangle([x0, y0, x1, y1], radius=12 * S, fill=fill, outline=stroke, width=2 * S)
    block((x0 + x1) / 2, (y0 + y1) / 2, [
        (name, F_HEAD, WHITE),
        (f"[{tech}]", F_TECH, (225, 235, 245)),
        (resp, F_BODY, WHITE),
    ], (x1 - x0) - 20 * S)
    return (x0, y0, x1, y1)

def center(b): return ((b[0] + b[2]) / 2, (b[1] + b[3]) / 2)

def actor(cx, top, name, resp):
    r = 14 * S
    hcy = top + r
    d.ellipse([cx - r, hcy - r, cx + r, hcy + r], fill=PERSON, outline=PERSON_S, width=2 * S)
    bt = hcy + r; bb = bt + 34 * S
    d.line([cx, bt, cx, bb], fill=PERSON, width=4 * S)
    d.line([cx - 20 * S, bt + 11 * S, cx + 20 * S, bt + 11 * S], fill=PERSON, width=4 * S)
    d.line([cx, bb, cx - 16 * S, bb + 24 * S], fill=PERSON, width=4 * S)
    d.line([cx, bb, cx + 16 * S, bb + 24 * S], fill=PERSON, width=4 * S)
    block(cx, bb + 24 * S + 30 * S, [(name, F_HEAD, PERSON), (resp, F_LBL, PERSON)], 200 * S)
    return (cx, hcy)

def dashed(p0, p1, color, width, dash=14 * S, gap=9 * S):
    x0, y0 = p0; x1, y1 = p1
    dist = math.hypot(x1 - x0, y1 - y0)
    if dist == 0: return
    ux, uy = (x1 - x0) / dist, (y1 - y0) / dist
    n = 0.0
    while n < dist:
        seg = min(dash, dist - n)
        d.line([(x0 + ux * n, y0 + uy * n), (x0 + ux * (n + seg), y0 + uy * (n + seg))], fill=color, width=width)
        n += dash + gap

def arrow(p0, p1, label, async_=False):
    color = ASYNC if async_ else SYNC
    w = 3 * S
    if async_:
        dashed(p0, p1, color, w)
    else:
        d.line([p0, p1], fill=color, width=w)
    ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0]); L = 15 * S
    for da in (math.radians(24), -math.radians(24)):
        d.line([p1, (p1[0] - L * math.cos(ang - da), p1[1] - L * math.sin(ang - da))], fill=color, width=w)
    mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
    lines = wrap(label, F_LBL, 220 * S)
    lh = (F_LBL.getbbox("Ay")[3] - F_LBL.getbbox("Ay")[1]) + 3 * S
    tw = max(d.textlength(ln, font=F_LBL) for ln in lines); th = len(lines) * lh; pad = 5 * S
    d.rectangle([mx - tw / 2 - pad, my - th / 2 - pad, mx + tw / 2 + pad, my + th / 2 + pad],
                fill=WHITE, outline=(225, 225, 225), width=1 * S)
    yy = my - th / 2
    for ln in lines:
        d.text((mx, yy), ln, font=F_LBL, fill=(ASYNC if async_ else INK), anchor="ma"); yy += lh

# ---- Title ----
d.text((W / 2, 24 * S), "BookSwap — C4 Container Diagram (Level 2)", font=F_TITLE, fill=INK, anchor="ma")

# ---- Actor ----
a_member = actor(110 * S, 330 * S, "Member [Person]", "Building neighbour")

# ---- Containers ----
mobile = box(250 * S, 300 * S, 470 * S, 400 * S, CONTAINER, CONTAINER_S, "Mobile App", "React Native", "Member-facing UI")
entra  = box(250 * S, 100 * S, 470 * S, 195 * S, EXT, EXT_S, "Entra External ID", "Microsoft Entra", "Authn / issues JWT")
api    = box(640 * S, 300 * S, 900 * S, 420 * S, CONTAINER, CONTAINER_S, "API Service", "Node.js Express / App Service", "REST API, auth, orchestration")
sql    = box(540 * S, 600 * S, 740 * S, 710 * S, STORE, STORE_S, "Database", "Azure SQL", "System of record")
redis  = box(770 * S, 600 * S, 970 * S, 710 * S, STORE, STORE_S, "Cache", "Azure Cache for Redis", "Hot read paths")
blob   = box(1000 * S, 600 * S, 1210 * S, 710 * S, STORE, STORE_S, "Object Store", "Azure Blob Storage", "Book photos")
bus    = box(1020 * S, 290 * S, 1250 * S, 390 * S, CONTAINER, CONTAINER_S, "Message Queue", "Azure Service Bus", "Notifications, digest jobs")
worker = box(1020 * S, 460 * S, 1250 * S, 560 * S, CONTAINER, CONTAINER_S, "Worker", "Node.js / Functions", "Drains queue, sends email")
email  = box(1340 * S, 460 * S, 1560 * S, 560 * S, EXT, EXT_S, "Email", "Azure Comms Services", "Outbound digest/email")

# ---- SYNC relationships (solid) ----
arrow(a_member, (250 * S, 350 * S), "Uses  [HTTPS]")
arrow((360 * S, 300 * S), (360 * S, 195 * S), "Signs in, gets JWT  [HTTPS/OIDC]")
arrow((470 * S, 345 * S), (640 * S, 345 * S), "API calls w/ Bearer JWT  [HTTPS/JSON]")
arrow((640 * S, 320 * S), (470 * S, 150 * S), "Validates JWT (JWKS)  [HTTPS]")
arrow((720 * S, 420 * S), (660 * S, 600 * S), "Reads/writes  [TDS/SQL]")
arrow((830 * S, 420 * S), (860 * S, 600 * S), "Caches hot reads  [RESP]")
arrow((900 * S, 400 * S), (1080 * S, 600 * S), "Stores/serves photos  [HTTPS]")
arrow((1250 * S, 510 * S), (1340 * S, 510 * S), "Sends email  [HTTPS]")
arrow((1100 * S, 560 * S), (720 * S, 660 * S), "Writes notifications  [TDS]")

# ---- ASYNC relationships (dashed, orange) ----
arrow((900 * S, 340 * S), (1020 * S, 340 * S), "Enqueues jobs  [AMQP]", async_=True)
arrow((1135 * S, 460 * S), (1135 * S, 390 * S), "Consumes messages  [AMQP]", async_=True)

# ---- Legend ----
lx0, ly0, lx1, ly1 = 250 * S, 780 * S, 720 * S, 1010 * S
d.rounded_rectangle([lx0, ly0, lx1, ly1], radius=8 * S, fill=WHITE, outline=(150, 150, 150), width=2 * S)
d.text((lx0 + 16 * S, ly0 + 12 * S), "Legend", font=F_HEAD, fill=INK)
ly = ly0 + 50 * S
def swatch(fill, stroke, label):
    global ly
    d.rounded_rectangle([lx0 + 20 * S, ly, lx0 + 50 * S, ly + 22 * S], radius=5 * S, fill=fill, outline=stroke, width=2 * S)
    d.text((lx0 + 62 * S, ly + 2 * S), label, font=F_LEG, fill=INK); ly += 40 * S
swatch(CONTAINER, CONTAINER_S, "Container we build / run")
swatch(STORE, STORE_S, "Managed data store")
swatch(EXT, EXT_S, "External / managed service")
# sync line
d.line([lx0 + 20 * S, ly + 10 * S, lx0 + 50 * S, ly + 10 * S], fill=SYNC, width=3 * S)
d.polygon([(lx0 + 50 * S, ly + 10 * S), (lx0 + 42 * S, ly + 5 * S), (lx0 + 42 * S, ly + 15 * S)], fill=SYNC)
d.text((lx0 + 62 * S, ly + 2 * S), "Synchronous call (request/response)", font=F_LEG, fill=INK); ly += 36 * S
# async line
dashed((lx0 + 20 * S, ly + 10 * S), (lx0 + 50 * S, ly + 10 * S), ASYNC, 3 * S, dash=8 * S, gap=5 * S)
d.polygon([(lx0 + 50 * S, ly + 10 * S), (lx0 + 42 * S, ly + 5 * S), (lx0 + 42 * S, ly + 15 * S)], fill=ASYNC)
d.text((lx0 + 62 * S, ly + 2 * S), "Asynchronous message (queue)", font=F_LEG, fill=ASYNC)

out = img.resize((W // S, H // S), Image.LANCZOS)
out.save("buddhika-day2-container-diagram.png", "PNG")
print("Saved buddhika-day2-container-diagram.png", out.size)
