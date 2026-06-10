"""Render GreenChit C4 Container (L2) and Component (L3) diagrams to PNG."""
import math
from PIL import Image, ImageDraw, ImageFont

S = 2
PERSON, PERSON_S = (8, 66, 123), (7, 59, 111)
CONTAINER, CONTAINER_S = (23, 130, 195), (15, 90, 140)
COMPONENT, COMPONENT_S = (66, 152, 210), (35, 110, 165)
STORE, STORE_S = (45, 125, 90), (30, 95, 65)
EXT, EXT_S = (140, 140, 140), (108, 108, 108)
WHITE, INK = (255, 255, 255), (40, 40, 40)
SYNC = (70, 70, 70)
ASYNC = (208, 110, 20)

def font(size, bold=False):
    p = r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf"
    try:
        return ImageFont.truetype(p, size * S)
    except OSError:
        return ImageFont.load_default()

F_TITLE, F_HEAD, F_TECH, F_BODY, F_LBL, F_LEG = font(21, True), font(12, True), font(9, True), font(9), font(8), font(10)

class C:
    def __init__(self, w, h):
        self.img = Image.new("RGB", (w * S, h * S), WHITE)
        self.d = ImageDraw.Draw(self.img)
    def wrap(self, text, fnt, max_w):
        words, lines, cur = text.split(), [], ""
        for w in words:
            t = (cur + " " + w).strip()
            if self.d.textlength(t, font=fnt) <= max_w: cur = t
            else:
                if cur: lines.append(cur)
                cur = w
        if cur: lines.append(cur)
        return lines
    def block(self, cx, cy, spec, max_w):
        rendered = []
        for text, fnt, color in spec:
            for ln in self.wrap(text, fnt, max_w):
                lh = (fnt.getbbox("Ay")[3] - fnt.getbbox("Ay")[1]) + 5 * S
                rendered.append((ln, fnt, color, lh))
        total = sum(lh for *_, lh in rendered); y = cy - total / 2
        for ln, fnt, color, lh in rendered:
            self.d.text((cx, y), ln, font=fnt, fill=color, anchor="ma"); y += lh
    def box(self, x0, y0, x1, y1, fill, stroke, name, tech, resp, hf=None):
        self.d.rounded_rectangle([x0*S, y0*S, x1*S, y1*S], radius=10*S, fill=fill, outline=stroke, width=2*S)
        spec = [(name, hf or F_HEAD, WHITE)]
        if tech: spec.append((f"[{tech}]", F_TECH, (230, 240, 248)))
        if resp: spec.append((resp, F_BODY, WHITE))
        self.block((x0+x1)/2*S, (y0+y1)/2*S, spec, (x1-x0-16)*S)
        return (x0, y0, x1, y1)
    def actor(self, cx, top, name, resp):
        r = 13
        hcy = top + r
        self.d.ellipse([(cx-r)*S, (hcy-r)*S, (cx+r)*S, (hcy+r)*S], fill=PERSON, outline=PERSON_S, width=2*S)
        bt = hcy + r; bb = bt + 30
        self.d.line([cx*S, bt*S, cx*S, bb*S], fill=PERSON, width=4*S)
        self.d.line([(cx-18)*S, (bt+10)*S, (cx+18)*S, (bt+10)*S], fill=PERSON, width=4*S)
        self.d.line([cx*S, bb*S, (cx-15)*S, (bb+22)*S], fill=PERSON, width=4*S)
        self.d.line([cx*S, bb*S, (cx+15)*S, (bb+22)*S], fill=PERSON, width=4*S)
        self.block(cx*S, (bb+22+26)*S, [(name, F_HEAD, PERSON), (resp, F_LBL, PERSON)], 180*S)
    def dashed(self, p0, p1, color, width, dash=12, gap=8):
        x0, y0 = p0[0]*S, p0[1]*S; x1, y1 = p1[0]*S, p1[1]*S
        dist = math.hypot(x1-x0, y1-y0)
        if dist == 0: return
        ux, uy = (x1-x0)/dist, (y1-y0)/dist; n = 0.0
        while n < dist:
            seg = min(dash*S, dist-n)
            self.d.line([(x0+ux*n, y0+uy*n), (x0+ux*(n+seg), y0+uy*(n+seg))], fill=color, width=width)
            n += (dash+gap)*S
    def arrow(self, p0, p1, label, async_=False):
        color = ASYNC if async_ else SYNC; w = 2*S
        P0 = (p0[0]*S, p0[1]*S); P1 = (p1[0]*S, p1[1]*S)
        if async_: self.dashed(p0, p1, color, w)
        else: self.d.line([P0, P1], fill=color, width=w)
        ang = math.atan2(P1[1]-P0[1], P1[0]-P0[0]); L = 13*S
        for da in (math.radians(24), -math.radians(24)):
            self.d.line([P1, (P1[0]-L*math.cos(ang-da), P1[1]-L*math.sin(ang-da))], fill=color, width=w)
        mx, my = (P0[0]+P1[0])/2, (P0[1]+P1[1])/2
        lines = self.wrap(label, F_LBL, 200*S)
        lh = (F_LBL.getbbox("Ay")[3]-F_LBL.getbbox("Ay")[1])+3*S
        tw = max(self.d.textlength(ln, font=F_LBL) for ln in lines); th = len(lines)*lh; pad = 4*S
        self.d.rectangle([mx-tw/2-pad, my-th/2-pad, mx+tw/2+pad, my+th/2+pad], fill=WHITE, outline=(225,225,225), width=1*S)
        yy = my-th/2
        for ln in lines:
            self.d.text((mx, yy), ln, font=F_LBL, fill=(ASYNC if async_ else INK), anchor="ma"); yy += lh
    def title(self, w, text):
        self.d.text((w/2*S, 22*S), text, font=F_TITLE, fill=INK, anchor="ma")
    def legend(self, x0, y0, items):
        rows = len(items)
        self.d.rounded_rectangle([x0*S, y0*S, (x0+300)*S, (y0+30+rows*26)*S], radius=8*S, fill=WHITE, outline=(150,150,150), width=2*S)
        self.d.text(((x0+12)*S, (y0+8)*S), "Legend", font=F_HEAD, fill=INK)
        yy = y0 + 34
        for kind, fill, stroke, label in items:
            if kind == "box":
                self.d.rounded_rectangle([(x0+14)*S, yy*S, (x0+40)*S, (yy+18)*S], radius=4*S, fill=fill, outline=stroke, width=2*S)
            elif kind == "sync":
                self.d.line([(x0+14)*S, (yy+9)*S, (x0+40)*S, (yy+9)*S], fill=SYNC, width=3*S)
            elif kind == "async":
                self.dashed((x0+14, yy+9), (x0+40, yy+9), ASYNC, 3*S, dash=7, gap=5)
            self.d.text(((x0+50)*S, (yy+1)*S), label, font=F_LEG, fill=INK); yy += 26
    def save(self, path):
        out = self.img.resize((self.img.width//S, self.img.height//S), Image.LANCZOS)
        out.save(path, "PNG"); print("Saved", path, out.size)


# ============================ CONTAINER DIAGRAM ============================
def render_container():
    W, H = 1520, 1060
    c = C(W, H)
    c.title(W, "GreenChit — C4 Container Diagram (Level 2)")

    # Actors
    c.actor(90, 70, "Staff", "Submits claims")
    c.actor(90, 250, "Line Manager", "Approves / rejects")
    c.actor(90, 430, "Finance", "Exports approved claims")
    c.actor(90, 610, "Audit", "Reviews audit log")

    web   = c.box(250, 250, 450, 380, CONTAINER, CONTAINER_S, "Web App", "SPA (React)", "Staff/manager/finance UI")
    entra = c.box(560, 95, 780, 185, EXT, EXT_S, "Identity", "Microsoft Entra ID", "SSO / issues JWT")
    api   = c.box(580, 300, 860, 440, CONTAINER, CONTAINER_S, "Claims API", "ASP.NET Core / App Service", "Claims, receipts, audit, export")
    sp    = c.box(1110, 120, 1330, 215, EXT, EXT_S, "SharePoint", "M365", "Watched CSV drop folder")
    pay   = c.box(1110, 250, 1330, 345, EXT, EXT_S, "Payroll Automation", "Power Automate", "Reads CSV, pays claims")
    bus   = c.box(930, 300, 1100, 390, CONTAINER, CONTAINER_S, "Message Bus", "Azure Service Bus", "claim.* events")
    work  = c.box(930, 470, 1100, 575, CONTAINER, CONTAINER_S, "Notifier", "Worker / Functions", "Sends notifications")
    teams = c.box(1160, 445, 1380, 535, EXT, EXT_S, "Teams", "Adaptive Card webhook", "Manager notification")
    email = c.box(1160, 565, 1380, 655, EXT, EXT_S, "Email", "Azure Comms Services", "Email fallback")
    sql   = c.box(470, 560, 690, 680, STORE, STORE_S, "Database", "Azure SQL", "Claims + audit (system of record)")
    blob  = c.box(230, 560, 430, 680, STORE, STORE_S, "Receipt Store", "Azure Blob Storage", "Receipt images (SAS)")
    av    = c.box(230, 710, 430, 825, EXT, EXT_S, "Malware Scan", "Defender for Storage", "Scans uploaded receipts")

    # Actor -> Web App
    c.arrow((125, 110), (250, 290), "Submits claims [HTTPS]")
    c.arrow((125, 290), (250, 320), "Approves/rejects [HTTPS]")
    c.arrow((125, 470), (250, 350), "Exports claims [HTTPS]")
    c.arrow((125, 650), (250, 375), "Reviews audit [HTTPS]")
    # Web App
    c.arrow((400, 250), (640, 185), "SSO sign-in [OIDC]")
    c.arrow((450, 315), (580, 345), "REST calls w/ JWT [HTTPS/JSON]")
    c.arrow((345, 380), (345, 560), "Uploads receipts via SAS [HTTPS]")
    # API -> identity / stores
    c.arrow((720, 300), (700, 185), "Validates JWT [HTTPS]")
    c.arrow((640, 440), (560, 560), "Reads/writes claims+audit [TDS]")
    c.arrow((580, 420), (430, 575), "Issues SAS / reads receipts [HTTPS]")
    c.arrow((330, 680), (330, 710), "Scans on upload [managed]")
    # API -> export
    c.arrow((770, 300), (1110, 175), "Writes CSV export [Graph/HTTPS]")
    c.arrow((1220, 215), (1220, 250), "Watched folder; reads CSV [internal]")
    # Async
    c.arrow((860, 360), (930, 360), "Publishes claim.* [AMQP]", async_=True)
    c.arrow((1015, 470), (1015, 390), "Consumes events [AMQP]", async_=True)
    # Worker -> Teams/Email
    c.arrow((1100, 505), (1160, 490), "Posts Adaptive Card [HTTPS]")
    c.arrow((1100, 545), (1160, 595), "Email fallback [HTTPS]")

    c.legend(560, 770, [
        ("box", PERSON, PERSON_S, "Person (role)"),
        ("box", CONTAINER, CONTAINER_S, "Container we build/run"),
        ("box", STORE, STORE_S, "Managed data store"),
        ("box", EXT, EXT_S, "External / managed service"),
        ("sync", None, None, "Synchronous call (request/response)"),
        ("async", None, None, "Asynchronous message (queue)"),
    ])
    c.save("buddhika-day4-greenchit-design/diagrams/container-diagram.png")


# ============================ COMPONENT DIAGRAM ============================
def render_component():
    W, H = 1380, 940
    c = C(W, H)
    c.title(W, "GreenChit — C4 Component Diagram: Claims API (Level 3)")

    # Boundary of the Claims API container
    bx0, by0, bx1, by1 = 360, 90, 1010, 760
    c.d.rounded_rectangle([bx0*S, by0*S, bx1*S, by1*S], radius=14*S, outline=CONTAINER_S, width=3*S)
    c.d.text(((bx0+18)*S, (by0+10)*S), "Claims API  [Container: ASP.NET Core]", font=F_HEAD, fill=CONTAINER_S)

    # Components inside
    ctrl  = c.box(560, 140, 810, 215, COMPONENT, COMPONENT_S, "API Controllers", "Minimal API / MVC", "HTTP endpoints, model binding", hf=F_HEAD)
    auth  = c.box(390, 270, 600, 350, COMPONENT, COMPONENT_S, "Auth & Access", "Middleware", "JWT validation, role checks (RBAC)", hf=F_HEAD)
    claims= c.box(650, 270, 870, 350, COMPONENT, COMPONENT_S, "Claims Service", "Domain", "Claim state machine", hf=F_HEAD)
    rec   = c.box(390, 400, 600, 480, COMPONENT, COMPONENT_S, "Receipts", "Service", "Issues SAS, validates size/count", hf=F_HEAD)
    notif = c.box(650, 400, 870, 480, COMPONENT, COMPONENT_S, "Notifications", "Service", "Publishes claim.* events", hf=F_HEAD)
    audit = c.box(390, 530, 600, 610, COMPONENT, COMPONENT_S, "Audit", "Service", "Tamper-evident transition log", hf=F_HEAD)
    export= c.box(650, 530, 870, 610, COMPONENT, COMPONENT_S, "Export", "Service", "Builds CSV, writes to SharePoint", hf=F_HEAD)
    repo  = c.box(520, 655, 850, 725, COMPONENT, COMPONENT_S, "Persistence", "EF Core repositories", "Transactional data access", hf=F_HEAD)

    # External (outside boundary)
    web   = c.box(80, 140, 300, 230, CONTAINER, CONTAINER_S, "Web App", "React SPA", "Calls the API")
    entra = c.box(80, 280, 300, 360, EXT, EXT_S, "Entra ID", "M365", "JWKS / tokens")
    sql   = c.box(1060, 250, 1300, 340, STORE, STORE_S, "Azure SQL", "Database", "Claims + audit")
    blob  = c.box(1060, 390, 1300, 480, STORE, STORE_S, "Blob Storage", "Receipts", "SAS upload")
    bus   = c.box(1060, 530, 1300, 620, CONTAINER, CONTAINER_S, "Service Bus", "Queue", "claim.* events")
    spc   = c.box(1060, 660, 1300, 750, EXT, EXT_S, "SharePoint", "M365", "CSV drop folder")

    # Arrows
    c.arrow((300, 178), (560, 178), "REST w/ JWT [HTTPS]")
    c.arrow((600, 195), (600, 270), "Authenticates [in-proc]")
    c.arrow((490, 280), (300, 320), "Validates JWT (JWKS) [HTTPS]")
    c.arrow((760, 215), (760, 270), "Submit/approve/reject [in-proc]")
    c.arrow((760, 350), (530, 400), "Attach receipts [in-proc]")
    c.arrow((760, 350), (760, 400), "Raise event [in-proc]")
    c.arrow((650, 310), (560, 530), "Record transition [in-proc]")
    c.arrow((810, 195), (810, 530), "Finance export [in-proc]")
    c.arrow((600, 480), (1060, 430), "Stores receipts via SAS [HTTPS]")
    c.arrow((870, 440), (1060, 565), "Publishes events [AMQP]", async_=True)
    c.arrow((870, 570), (1060, 690), "Writes CSV [Graph/HTTPS]")
    # components -> persistence -> SQL
    c.arrow((690, 350), (690, 655), "Load/save [in-proc]")
    c.arrow((520, 575), (640, 655), "Append audit [in-proc]")
    c.arrow((850, 690), (1060, 300), "Reads/writes [TDS]")

    c.legend(80, 470, [
        ("box", COMPONENT, COMPONENT_S, "Component (inside API)"),
        ("box", CONTAINER, CONTAINER_S, "Container"),
        ("box", STORE, STORE_S, "Data store"),
        ("box", EXT, EXT_S, "External service"),
        ("sync", None, None, "Synchronous / in-process call"),
        ("async", None, None, "Asynchronous message"),
    ])
    c.save("buddhika-day4-greenchit-design/diagrams/component-diagram.png")


render_container()
render_component()
