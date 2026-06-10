"""Render the LearnLanka C4 Context diagram to PNG (matches the .drawio layout)."""
import math
from PIL import Image, ImageDraw, ImageFont

S = 2  # supersample factor for crisp text/lines
W, H = 1460 * S, 1020 * S

# Colours (C4 palette)
PERSON   = (8, 66, 123)      # dark blue
PERSON_S = (7, 59, 111)
SYSTEM   = (17, 104, 189)    # blue
SYSTEM_S = (11, 72, 132)
EXT      = (140, 140, 140)   # grey
EXT_S    = (108, 108, 108)
WHITE    = (255, 255, 255)
INK      = (40, 40, 40)
LINE     = (90, 90, 90)

img = Image.new("RGB", (W, H), WHITE)
d = ImageDraw.Draw(img)

def font(size, bold=False):
    paths = [r"C:\Windows\Fonts\arialbd.ttf"] if bold else [r"C:\Windows\Fonts\arial.ttf"]
    for p in paths:
        try:
            return ImageFont.truetype(p, size * S)
        except OSError:
            pass
    return ImageFont.load_default()

F_TITLE = font(22, True)
F_HEAD  = font(13, True)
F_BODY  = font(11)
F_LBL   = font(10)
F_LEG   = font(11)

def wrap(text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def centered_block(cx, cy, head, headf, body, bodyf, max_w, color):
    """Draw a heading + wrapped body centered around (cx, cy)."""
    hlines = wrap(head, headf, max_w)
    blines = wrap(body, bodyf, max_w) if body else []
    lh_h = (headf.getbbox("Ay")[3] - headf.getbbox("Ay")[1]) + 6 * S
    lh_b = (bodyf.getbbox("Ay")[3] - bodyf.getbbox("Ay")[1]) + 4 * S
    total = len(hlines) * lh_h + (8 * S if blines else 0) + len(blines) * lh_b
    y = cy - total / 2
    for ln in hlines:
        d.text((cx, y), ln, font=headf, fill=color, anchor="ma")
        y += lh_h
    if blines:
        y += 8 * S
    for ln in blines:
        d.text((cx, y), ln, font=bodyf, fill=color, anchor="ma")
        y += lh_b

def box(x0, y0, x1, y1, fill, stroke, head, body, headf=F_HEAD, bodyf=F_BODY):
    r = 14 * S
    d.rounded_rectangle([x0, y0, x1, y1], radius=r, fill=fill, outline=stroke, width=2 * S)
    centered_block((x0 + x1) / 2, (y0 + y1) / 2, head, headf, body, bodyf,
                   (x1 - x0) - 24 * S, WHITE)
    return (x0, y0, x1, y1)

def actor(cx, top, head, body, fill=PERSON, stroke=PERSON_S):
    """Stick figure with label below. Returns connection point (right side)."""
    r = 14 * S
    head_cy = top + r
    d.ellipse([cx - r, head_cy - r, cx + r, head_cy + r], fill=fill, outline=stroke, width=2 * S)
    body_top = head_cy + r
    body_bot = body_top + 36 * S
    d.line([cx, body_top, cx, body_bot], fill=fill, width=4 * S)            # torso
    d.line([cx - 22 * S, body_top + 12 * S, cx + 22 * S, body_top + 12 * S], fill=fill, width=4 * S)  # arms
    d.line([cx, body_bot, cx - 18 * S, body_bot + 26 * S], fill=fill, width=4 * S)  # leg
    d.line([cx, body_bot, cx + 18 * S, body_bot + 26 * S], fill=fill, width=4 * S)  # leg
    label_top = body_bot + 26 * S + 8 * S
    centered_block(cx, label_top + 42 * S, head, F_HEAD, body, F_LBL, 200 * S, PERSON)
    return (cx + 28 * S, head_cy + 18 * S)  # right-ish connection point

def arrow(p0, p1, label):
    d.line([p0, p1], fill=LINE, width=2 * S)
    # arrowhead
    ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    L = 14 * S
    for da in (math.radians(22), -math.radians(22)):
        d.line([p1, (p1[0] - L * math.cos(ang - da), p1[1] - L * math.sin(ang - da))],
               fill=LINE, width=2 * S)
    # label with white background at midpoint
    mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
    lines = wrap(label, F_LBL, 230 * S)
    lh = (F_LBL.getbbox("Ay")[3] - F_LBL.getbbox("Ay")[1]) + 3 * S
    tw = max(d.textlength(ln, font=F_LBL) for ln in lines)
    th = len(lines) * lh
    pad = 5 * S
    d.rectangle([mx - tw / 2 - pad, my - th / 2 - pad, mx + tw / 2 + pad, my + th / 2 + pad],
                fill=WHITE, outline=(220, 220, 220), width=1 * S)
    yy = my - th / 2
    for ln in lines:
        d.text((mx, yy), ln, font=F_LBL, fill=INK, anchor="ma")
        yy += lh

# ---- Title ----
d.text((W / 2, 26 * S), "LearnLanka — C4 System Context Diagram (Level 1)",
       font=F_TITLE, fill=INK, anchor="ma")

# ---- Actors (left column) ----
a_student = actor(150 * S, 120 * S, "Student [Person]", "O/L & A/L student finding & booking tutors")
a_tutor   = actor(150 * S, 360 * S, "Tutor [Person]", "Publishes slots, teaches, gets paid")
a_admin   = actor(150 * S, 600 * S, "Operations Admin [Person]", "Vets tutors, runs payouts, PDPA & disputes")

# ---- System in scope (centre) ----
plat = box(540 * S, 380 * S, 880 * S, 560 * S, SYSTEM, SYSTEM_S,
           "LearnLanka Platform  [IN SCOPE]",
           "Tutor search & booking, payment orchestration, commission & payouts, ratings, PDPA consent/deletion")

# ---- External systems (right column) ----
e_pay  = box(1090 * S, 90 * S,  1400 * S, 200 * S, EXT, EXT_S, "PayHere [External]", "PCI-DSS card & eZ Cash payment gateway")
e_vid  = box(1090 * S, 260 * S, 1400 * S, 370 * S, EXT, EXT_S, "Daily.co / 100ms [External]", "Third-party video calling")
e_sms  = box(1090 * S, 430 * S, 1400 * S, 540 * S, EXT, EXT_S, "SMS Gateway [External]", "OTP & booking notifications")
e_bank = box(1090 * S, 600 * S, 1400 * S, 710 * S, EXT, EXT_S, "Sampath Vishwa [External]", "Bank for weekly tutor payouts")

# ---- Relationships: actors -> platform ----
arrow(a_student, (540 * S, 420 * S), "Searches & books, rates tutor  [HTTPS]")
arrow(a_tutor,   (540 * S, 470 * S), "Publishes slots, accepts/declines  [HTTPS]")
arrow(a_admin,   (540 * S, 520 * S), "Vets tutors, runs payouts, PDPA  [HTTPS]")

# ---- Relationships: platform -> external ----
arrow((880 * S, 415 * S), (1090 * S, 145 * S), "Charges card / eZ Cash  [HTTPS API]")
arrow((880 * S, 455 * S), (1090 * S, 315 * S), "Creates & joins video room  [HTTPS/SDK]")
arrow((880 * S, 495 * S), (1090 * S, 485 * S), "Sends OTP & notifications  [HTTPS/SMPP]")
arrow((880 * S, 535 * S), (1090 * S, 655 * S), "Sends weekly payout file  [SFTP]")

# ---- Legend ----
lx0, ly0, lx1, ly1 = 540 * S, 760 * S, 880 * S, 980 * S
d.rounded_rectangle([lx0, ly0, lx1, ly1], radius=8 * S, fill=WHITE, outline=(150, 150, 150), width=2 * S)
d.text((lx0 + 16 * S, ly0 + 12 * S), "Legend", font=F_HEAD, fill=INK)
ly = ly0 + 50 * S
# person sample
d.ellipse([lx0 + 22 * S, ly, lx0 + 42 * S, ly + 20 * S], fill=PERSON, outline=PERSON_S, width=2 * S)
d.text((lx0 + 60 * S, ly), "Person (actor / role)", font=F_LEG, fill=INK)
ly += 44 * S
d.rounded_rectangle([lx0 + 20 * S, ly, lx0 + 48 * S, ly + 22 * S], radius=5 * S, fill=SYSTEM, outline=SYSTEM_S, width=2 * S)
d.text((lx0 + 60 * S, ly + 2 * S), "System in scope (LearnLanka)", font=F_LEG, fill=INK)
ly += 44 * S
d.rounded_rectangle([lx0 + 20 * S, ly, lx0 + 48 * S, ly + 22 * S], radius=5 * S, fill=EXT, outline=EXT_S, width=2 * S)
d.text((lx0 + 60 * S, ly + 2 * S), "External system (third-party)", font=F_LEG, fill=INK)
ly += 44 * S
d.line([lx0 + 20 * S, ly + 10 * S, lx0 + 48 * S, ly + 10 * S], fill=LINE, width=2 * S)
d.polygon([(lx0 + 48 * S, ly + 10 * S), (lx0 + 40 * S, ly + 5 * S), (lx0 + 40 * S, ly + 15 * S)], fill=LINE)
d.text((lx0 + 60 * S, ly + 2 * S), "Relationship — verb + [protocol]", font=F_LEG, fill=INK)

# ---- Downscale for anti-aliasing & save ----
out = img.resize((W // S, H // S), Image.LANCZOS)
out.save("buddhika-day1-context-diagram.png", "PNG")
print("Saved buddhika-day1-context-diagram.png", out.size)
