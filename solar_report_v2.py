"""
SolarYield India — Premium Corporate Report v2
Indian Corporate Standards: MNRE / SBI / NTPC Annual Report Style
Fixes: TTF fonts for Rs. symbol, 5 exact pages, professional layout
"""

import math, datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

W, H = A4  # 595.27 x 841.89 pt

# ── REGISTER TTF FONTS (supports Rs. and all Indian chars) ─────
pdfmetrics.registerFont(TTFont('Sans',     '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('Sans-B',   '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
pdfmetrics.registerFont(TTFont('Sans-I',   '/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf'))
pdfmetrics.registerFont(TTFont('Sans-BI',  '/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf'))

# ── COLOUR PALETTE  (Indian corporate: deep navy + saffron gold) ─
C_NAVY     = colors.HexColor('#0D2137')   # Primary navy
C_NAVY2    = colors.HexColor('#163350')   # Header bg
C_GOLD     = colors.HexColor('#B8860B')   # Saffron gold
C_GOLD2    = colors.HexColor('#DAA520')   # Bright gold
C_GOLD_BG  = colors.HexColor('#FBF3DC')   # Gold tint
C_GREEN    = colors.HexColor('#1A6B3C')   # Profit green
C_GREEN_BG = colors.HexColor('#EAF6EE')
C_RED      = colors.HexColor('#8B1A1A')   # Loss red
C_RED_BG   = colors.HexColor('#FDEAEA')
C_SLATE    = colors.HexColor('#2C3E50')
C_MUTED    = colors.HexColor('#6B7280')
C_BORDER   = colors.HexColor('#BDC3C7')
C_ROW_ALT  = colors.HexColor('#F4F6F8')
C_WHITE    = colors.HexColor('#FFFFFF')
C_LIGHT    = colors.HexColor('#F8F9FA')

RS = 'Rs.'   # Rupee prefix — safe for all PDF viewers

# ── SIMULATION INPUTS ──────────────────────────────────────────
INP = {
    "client":          "M/s Sunrise Infra Pvt. Ltd.",
    "project_ref":     "SYI/2025-26/KA/0042",
    "city":            "Bengaluru",
    "state":           "Karnataka",
    "capacity_kw":     10.0,
    "cost_per_kw":     45000,
    "subsidy":         94500,
    "panel_eff":       20.5,
    "pr":              0.80,
    "degradation":     0.005,
    "life":            25,
    "ghi":             5.3,
    "import_tariff":   6.50,
    "export_fit":      3.82,
    "tariff_esc":      0.03,
    "self_cons":       0.75,
    "om_yr1":          5000,
    "om_esc":          0.04,
    "inv_replace":     40000,
    "bank":            "State Bank of India — Surya Ghar Scheme",
    "interest":        9.15,
    "tenure_yr":       7,
    "down_pct":        20,
    "discount":        8.0,
}

# ── FORMATTING ─────────────────────────────────────────────────
def fmt(v, lakh=True):
    """Format as Indian numbering with Rs. prefix"""
    if v is None: return "N/A"
    neg = v < 0
    av  = abs(int(round(v)))
    if lakh and av >= 10_00_000:
        return f"{'(-) ' if neg else ''}{RS}{av/10_00_000:.2f} Cr"
    if lakh and av >= 1_00_000:
        return f"{'(-) ' if neg else ''}{RS}{av/1_00_000:.2f} L"
    s = str(av)
    if len(s) > 3: s = s[:-3] + "," + s[-3:]
    if len(s) > 7: s = s[:-7] + "," + s[-7:]
    return f"{'(-) ' if neg else ''}{RS}{s}"

def fmt_full(v):
    if v is None: return "N/A"
    neg = v < 0
    av  = abs(int(round(v)))
    s   = str(av)
    if len(s) > 3: s = s[:-3] + "," + s[-3:]
    if len(s) > 7: s = s[:-7] + "," + s[-7:]
    if len(s) > 11: s = s[:-11] + "," + s[-11:]
    return f"{'-' if neg else ''}{RS}{s}"

# ── SIMULATION ─────────────────────────────────────────────────
def simulate():
    cap  = INP["capacity_kw"]
    cost = cap * INP["cost_per_kw"]
    sub  = INP["subsidy"]
    nc   = cost - sub
    y1   = cap * INP["ghi"] * 365 * INP["pr"]
    disc = INP["discount"] / 100

    cf, cum, npv = [], -nc, -nc
    for y in range(1, INP["life"]+1):
        deg    = (1 - INP["degradation"])**(y-1)
        yld    = y1 * deg
        tar    = INP["import_tariff"] * (1+INP["tariff_esc"])**(y-1)
        exp    = INP["export_fit"]    * (1+INP["tariff_esc"])**(y-1)
        saved  = yld * INP["self_cons"] * tar
        exprev = yld * (1-INP["self_cons"]) * exp
        om     = INP["om_yr1"] * (1+INP["om_esc"])**(y-1)
        extra  = INP["inv_replace"] if y == 12 else 0
        net    = saved + exprev - om - extra
        cum   += net
        npv   += net / (1+disc)**y
        cf.append(dict(y=y, yld=round(yld), tar=round(tar,2),
            saved=round(saved), exprev=round(exprev),
            om=round(om), extra=extra, net=round(net), cum=round(cum)))

    payback = next((r["y"] for r in cf if r["cum"]>=0), None)

    # IRR
    flows = [-nc] + [r["net"] for r in cf]
    r = 0.10
    for _ in range(300):
        f  = sum(v/(1+r)**i for i,v in enumerate(flows))
        df = sum(-i*v/(1+r)**(i+1) for i,v in enumerate(flows))
        if abs(df)<1e-12: break
        r -= f/df
        if r<=-1: r=-0.999
    irr = r if -1<r<10 else None

    om_total  = sum(r["om"]+r["extra"] for r in cf)
    yld_total = sum(r["yld"] for r in cf)
    lcoe      = (nc + om_total) / yld_total

    res = dict(
        cost=round(cost), nc=round(nc),
        y1=round(y1), cf=cf,
        payback=payback,
        irr=round(irr*100,2) if irr else None,
        npv=round(npv), lcoe=round(lcoe,2),
        profit25=round(cf[-1]["cum"]),
        gross25=round(cf[-1]["cum"]+nc),
    )

    # Loan
    dp   = round(nc * INP["down_pct"]/100)
    lamt = nc - dp
    rm   = INP["interest"]/100/12
    nm   = INP["tenure_yr"]*12
    emi  = lamt*rm*(1+rm)**nm/((1+rm)**nm-1)
    ann  = emi*12

    amort, bal, tint = [], lamt, 0
    for m in range(1, nm+1):
        i = bal*rm; p = emi-i; bal=max(0,bal-p); tint+=i
        amort.append(dict(m=m, emi=round(emi), p=round(p), i=round(i), bal=round(bal)))

    lcf, lcum, lnpv = [], -dp, -dp
    for r in cf:
        ec   = ann if r["y"]<=INP["tenure_yr"] else 0
        net  = r["net"]-ec
        lcum += net
        lnpv += net/(1+disc)**r["y"]
        lcf.append(dict(y=r["y"], solar=r["net"], emi=round(ec), net=round(net), cum=round(lcum)))

    l_payback = next((r["y"] for r in lcf if r["cum"]>=0), None)
    flows2 = [-dp] + [r["net"] for r in lcf]
    r2 = 0.15
    for _ in range(300):
        f  = sum(v/(1+r2)**i for i,v in enumerate(flows2))
        df = sum(-i*v/(1+r2)**(i+1) for i,v in enumerate(flows2))
        if abs(df)<1e-12: break
        r2 -= f/df
        if r2<=-1: r2=-0.999
    l_irr = r2 if -1<r2<10 else None

    res["loan"] = dict(
        dp=dp, lamt=round(lamt), emi=round(emi), nm=nm,
        ann=round(ann), tint=round(tint),
        tpaid=round(emi*nm+dp),
        amort=amort, lcf=lcf,
        payback=l_payback,
        irr=round(l_irr*100,1) if l_irr else None,
        npv=round(lnpv),
        profit25=round(lcf[-1]["cum"]),
    )
    return res

# ── DRAWING PRIMITIVES ─────────────────────────────────────────
def F(c, name, size): c.setFont(name, size)
def FC(c, col): c.setFillColor(col)
def SC(c, col): c.setStrokeColor(col)
def LW(c, w): c.setLineWidth(w)

def txt(c, t, x, y, font='Sans', size=9, color=C_SLATE, align='left'):
    c.setFont(font, size)
    c.setFillColor(color)
    t = str(t)
    if   align=='center': c.drawCentredString(x, y, t)
    elif align=='right':  c.drawRightString(x, y, t)
    else:                 c.drawString(x, y, t)

def box(c, x, y, w, h, fill=None, stroke=None, lw=0.5, r=0):
    if fill:   c.setFillColor(fill)
    if stroke: c.setStrokeColor(stroke); c.setLineWidth(lw)
    if r:      c.roundRect(x, y, w, h, r, fill=bool(fill), stroke=bool(stroke))
    else:      c.rect(x, y, w, h, fill=bool(fill), stroke=bool(stroke))

def hline(c, x1, x2, y, col=C_BORDER, lw=0.4):
    c.setStrokeColor(col); c.setLineWidth(lw)
    c.line(x1, y, x2, y)

def vline(c, x, y1, y2, col=C_BORDER, lw=0.4):
    c.setStrokeColor(col); c.setLineWidth(lw)
    c.line(x, y1, x, y2)

# ── HEADER / FOOTER ────────────────────────────────────────────
def chrome(c, pg, total, title):
    # Top bar
    box(c, 0, H-18*mm, W, 18*mm, fill=C_NAVY2)
    # Gold rule below header
    box(c, 0, H-18*mm, W, 1.2, fill=C_GOLD)
    # Left — logo block
    box(c, 0, H-18*mm, 38*mm, 18*mm, fill=C_NAVY)
    txt(c, "SolarYield", 3*mm, H-9*mm,  'Sans-B', 10, C_GOLD)
    txt(c, "INDIA  Pvt. Ltd.", 3*mm, H-14*mm, 'Sans', 7, colors.HexColor('#94A3B8'))
    # Vertical gold divider
    vline(c, 38*mm, H-18*mm, H, C_GOLD, 1.5)
    # Centre — page title
    txt(c, title.upper(), W/2, H-10*mm, 'Sans-B', 9, C_GOLD2, 'center')
    txt(c, "Solar PV Investment Feasibility Report", W/2, H-15*mm, 'Sans', 6.5,
        colors.HexColor('#94A3B8'), 'center')
    # Right — ref & date
    now = datetime.datetime.now().strftime("%d %b %Y")
    txt(c, f"Ref: {INP['project_ref']}", W-3*mm, H-9*mm, 'Sans', 7,
        colors.HexColor('#94A3B8'), 'right')
    txt(c, f"Dated: {now}", W-3*mm, H-14*mm, 'Sans', 7,
        colors.HexColor('#CBD5E1'), 'right')

    # Footer bar
    box(c, 0, 0, W, 11*mm, fill=C_NAVY)
    box(c, 0, 11*mm, W, 0.8, fill=C_GOLD)
    txt(c, INP["client"], 5*mm, 4*mm, 'Sans', 6.5, colors.HexColor('#94A3B8'))
    txt(c, "STRICTLY CONFIDENTIAL — For Authorised Recipient Only",
        W/2, 4*mm, 'Sans-I', 6.5, colors.HexColor('#64748B'), 'center')
    txt(c, f"Page {pg} of {total}", W-5*mm, 4*mm, 'Sans-B', 7, C_GOLD2, 'right')

# ── SECTION TITLE ──────────────────────────────────────────────
def sec(c, x, y, w, title, sub=None):
    """Returns y after the section bar"""
    box(c, x, y-7*mm, w, 7*mm, fill=C_NAVY)
    # Gold left accent
    box(c, x, y-7*mm, 3, 7*mm, fill=C_GOLD)
    txt(c, title, x+6*mm, y-4.5*mm, 'Sans-B', 8.5, C_WHITE)
    if sub:
        txt(c, sub, x+w-3*mm, y-4.5*mm, 'Sans', 7, C_GOLD2, 'right')
    return y - 9*mm

# ── KPI CARD ──────────────────────────────────────────────────
def kpi(c, x, y, w, h, val, label, sub, vc=C_GOLD):
    # Card background with subtle border
    box(c, x, y, w, h, fill=C_WHITE, stroke=C_BORDER, lw=0.5)
    # Top colour stripe
    box(c, x, y+h-2, w, 2, fill=vc)
    # Bottom navy strip
    box(c, x, y, w, 7*mm, fill=C_NAVY)
    # Value
    txt(c, val,   x+w/2, y+h*0.45, 'Sans-B', 12, vc, 'center')
    txt(c, label, x+w/2, y+h*0.25, 'Sans',   6.5, C_MUTED, 'center')
    txt(c, sub,   x+w/2, y+3,      'Sans-B', 6,   C_GOLD2, 'center')

# ── HORIZONTAL BAR CHART ──────────────────────────────────────
def bar_chart(c, x, y, w, h, data, labels, bar_col, show_zero=False):
    if not data: return
    max_v = max(abs(v) for v in data) or 1
    min_v = min(data)
    n     = len(data)
    bw    = w/n*0.65
    gap   = w/n*0.35
    ph    = h*0.82
    base  = y + h*0.1

    # BG
    box(c, x, y, w, h, fill=C_LIGHT, stroke=C_BORDER, lw=0.3)
    # Grid
    for i in range(1,5):
        gy = base + i*ph/4
        hline(c, x, x+w, gy, C_BORDER, 0.25)

    zero_y = base + ((-min_v)/(max_v-min_v+0.001))*ph if min_v<0 else base
    if min_v<0 or show_zero:
        hline(c, x, x+w, zero_y, C_SLATE, 0.8)

    rng = max_v - min(min_v,0) or 1
    for i,(v,col) in enumerate(zip(data,bar_col)):
        bx  = x + i*(bw+gap) + gap/2
        bh  = abs(v)/max_v*ph*0.88
        by  = zero_y if v>=0 else zero_y-bh
        c.setFillColor(col)
        c.rect(bx, by, bw, bh, fill=1, stroke=0)
        if i%5==0 or i==n-1:
            txt(c, str(labels[i]), bx+bw/2, y+1.5, 'Sans', 4.5, C_MUTED, 'center')

# ── LINE CHART ────────────────────────────────────────────────
def line_chart(c, x, y, w, h, series, labels, cols, leg_labels):
    all_v = [v for s in series for v in s]
    if not all_v: return
    max_v, min_v = max(all_v), min(all_v)
    rng = max_v-min_v or 1
    n   = len(labels)
    ph  = h*0.82
    base= y + h*0.1
    pw  = w

    box(c, x, y, w, h, fill=C_LIGHT, stroke=C_BORDER, lw=0.3)
    for i in range(1,5):
        gy = base+i*ph/4
        hline(c, x, x+w, gy, C_BORDER, 0.25)
        gv = min_v + i*rng/4
        lbl = f"{gv/100000:.1f}L" if abs(gv)>=100000 else f"{int(gv/1000)}k"
        txt(c, lbl, x-1, gy, 'Sans', 4.5, C_MUTED, 'right')

    if min_v<0:
        zy = base+((-min_v)/rng)*ph
        hline(c, x, x+w, zy, C_SLATE, 0.8)

    for series_data, col, lw in zip(series, cols, [1.8, 1.3]):
        pts = [(x+i*pw/(n-1), base+((v-min_v)/rng)*ph)
               for i,v in enumerate(series_data)]
        c.setStrokeColor(col); c.setLineWidth(lw)
        p = c.beginPath(); p.moveTo(*pts[0])
        for pt in pts[1:]: p.lineTo(*pt)
        c.drawPath(p, stroke=1, fill=0)

    # X labels
    for i in range(0,n,5):
        px = x+i*pw/(n-1)
        txt(c, f"Yr{labels[i]}", px, y+1.5, 'Sans', 4.5, C_MUTED, 'center')
    txt(c, f"Yr{labels[-1]}", x+(n-1)*pw/(n-1), y+1.5, 'Sans', 4.5, C_MUTED, 'center')

    # Legend
    lx = x+w-60*mm; ly = y+h-5*mm
    for i,(lbl,col) in enumerate(zip(leg_labels, cols)):
        c.setFillColor(col)
        c.rect(lx+i*32*mm, ly, 12, 3.5, fill=1, stroke=0)
        txt(c, lbl, lx+i*32*mm+14, ly, 'Sans', 6, C_SLATE)

# ═══════════════════════════════════════════════════════════════
#  PAGE 1 — COVER PAGE
# ═══════════════════════════════════════════════════════════════
def page1_cover(c, R):
    # Full-page navy top band
    box(c, 0, H*0.52, W, H*0.48, fill=C_NAVY2)

    # Decorative geometric pattern — concentric arcs top-right
    import math as m
    c.setStrokeColor(colors.HexColor('#1E3F5A')); c.setLineWidth(0.6)
    for r in [35, 60, 85, 110, 135]:
        c.arc(W-5*mm-r, H-5*mm-r, W-5*mm+r, H-5*mm+r, 180, 90)
    # Gold accent arc
    c.setStrokeColor(C_GOLD); c.setLineWidth(2)
    c.arc(W-90*mm, H-90*mm, W+90*mm, H+90*mm, 183, 84)

    # ── COMPANY LOGO BLOCK ──
    # Sun circle
    cx, cy = 22*mm, H-30*mm
    c.setFillColor(C_GOLD)
    c.circle(cx, cy, 12*mm, fill=1, stroke=0)
    c.setFillColor(C_NAVY2)
    c.circle(cx, cy, 8.5*mm, fill=1, stroke=0)
    c.setFillColor(C_GOLD)
    c.circle(cx, cy, 5*mm, fill=1, stroke=0)
    # Sun rays
    c.setStrokeColor(C_GOLD2); c.setLineWidth(1.3)
    for ang in range(0, 360, 30):
        rad = math.radians(ang)
        c.line(cx+13.5*mm*math.cos(rad), cy+13.5*mm*math.sin(rad),
               cx+17*mm*math.cos(rad),   cy+17*mm*math.sin(rad))

    txt(c, "SOLARYIELD INDIA", 38*mm, H-23*mm, 'Sans-B', 16, C_GOLD2)
    txt(c, "PRIVATE LIMITED", 38*mm, H-29*mm, 'Sans', 8.5, colors.HexColor('#94A3B8'))

    # Gold horizontal rule
    box(c, 15*mm, H-36*mm, W-30*mm, 1.5, fill=C_GOLD)

    # ── REPORT TITLE ──
    txt(c, "SOLAR PHOTOVOLTAIC", 15*mm, H-48*mm, 'Sans-B', 24, C_WHITE)
    txt(c, "INVESTMENT FEASIBILITY REPORT", 15*mm, H-60*mm, 'Sans-B', 20, C_WHITE)
    box(c, 15*mm, H-62*mm, W-30*mm, 0.6, fill=colors.HexColor('#2E5F8A'))
    txt(c, "With Detailed Bank Loan Financing Analysis | As per MNRE Guidelines",
        15*mm, H-69*mm, 'Sans-I', 9, colors.HexColor('#8BA7C0'))

    # ── DIAGONAL SEPARATOR ──
    c.setFillColor(C_GOLD)
    p = c.beginPath()
    p.moveTo(0, H*0.52); p.lineTo(W, H*0.52)
    p.lineTo(W, H*0.52-8); p.lineTo(0, H*0.52+8)
    p.close()
    c.drawPath(p, fill=1, stroke=0)

    # ── WHITE LOWER HALF ──
    box(c, 0, 0, W, H*0.52, fill=C_WHITE)

    # ── PROJECT DETAILS BOX (left) ──
    bx, by = 15*mm, H*0.52-10*mm-82*mm
    bw, bh = 115*mm, 82*mm
    box(c, bx, by, bw, bh, fill=C_WHITE, stroke=C_BORDER, lw=0.6)
    # Header
    box(c, bx, by+bh-9*mm, bw, 9*mm, fill=C_NAVY)
    txt(c, "PROJECT DETAILS", bx+bw/2, by+bh-6*mm, 'Sans-B', 8, C_GOLD2, 'center')

    details = [
        ("Client / Applicant",    INP["client"]),
        ("Project Location",      f'{INP["city"]}, {INP["state"]}'),
        ("System Capacity",       f'{INP["capacity_kw"]} kWp On-Grid Solar PV'),
        ("Gross Project Cost",    fmt_full(R["cost"])),
        ("PM Surya Ghar Subsidy", fmt_full(INP["subsidy"])),
        ("Net Investment",        fmt_full(R["nc"])),
        ("Report Reference",      INP["project_ref"]),
        ("Prepared By",           "SolarYield India Pvt. Ltd."),
        ("Report Date",           datetime.datetime.now().strftime("%d %B %Y")),
    ]
    dy = by + bh - 16*mm
    for label, val in details:
        txt(c, label+":", bx+4*mm, dy, 'Sans', 7, C_MUTED)
        txt(c, val,       bx+bw-3*mm, dy, 'Sans-B', 7, C_NAVY, 'right')
        dy -= 7*mm
        hline(c, bx+3*mm, bx+bw-3*mm, dy+4.5*mm, C_ROW_ALT, 0.4)

    # ── KEY METRICS PANEL (right) ──
    L = R["loan"]
    metrics = [
        (fmt(R["nc"]),           "Net Investment",     "After Subsidy",          C_NAVY2),
        (f'{R["payback"]} Yrs',  "Payback Period",     "Cash Purchase",          C_GREEN),
        (f'{L["payback"]} Yrs',  "Payback Period",     "Loan Financing",         C_GOLD),
        (f'{R["irr"]}%',         "IRR — 25 Years",     "Cash Scenario",          C_NAVY2),
    ]
    kw, kh = 62*mm, 18*mm
    rx = 140*mm; ry = by + bh - 9*mm - 4*(kh+2*mm) + 2*mm
    for i,(v,l,s,col) in enumerate(metrics):
        kpi(c, rx, ry+i*(kh+2*mm), kw, kh, v, l, s, col)

    # ── BOTTOM OFFICIAL FOOTER ──
    box(c, 0, 0, W, 16*mm, fill=C_NAVY)
    box(c, 0, 16*mm, W, 1.2, fill=C_GOLD)
    txt(c, f'Report No.: {INP["project_ref"]}',
        15*mm, 10*mm, 'Sans-B', 7.5, C_GOLD2)
    txt(c, f'System: {INP["capacity_kw"]} kWp | Location: {INP["city"]}, {INP["state"]} | Date: {datetime.datetime.now().strftime("%d %b %Y")}',
        W/2, 10*mm, 'Sans', 7, colors.HexColor('#94A3B8'), 'center')
    txt(c, "CONFIDENTIAL",
        W-15*mm, 10*mm, 'Sans-B', 7.5, C_GOLD, 'right')
    txt(c, "This document contains proprietary financial analysis. Unauthorised reproduction is prohibited.",
        W/2, 4*mm, 'Sans-I', 6, colors.HexColor('#4B6278'), 'center')

    c.showPage()

# ═══════════════════════════════════════════════════════════════
#  PAGE 2 — EXECUTIVE SUMMARY
# ═══════════════════════════════════════════════════════════════
def page2_exec(c, R, TP):
    chrome(c, 2, TP, "Executive Summary")
    L  = R["loan"]
    y  = H - 22*mm
    M  = 12*mm   # left margin
    CW = W - 24*mm  # content width

    # ── KPI GRID ROW 1 ──
    y = sec(c, M, y, CW, "KEY PERFORMANCE INDICATORS — CASH PURCHASE SCENARIO")
    kw = (CW-3*mm)/4; kh = 21*mm
    kpis_r1 = [
        (fmt(R["nc"]),             "Net Project Cost",    "After PM Subsidy",       C_NAVY2),
        (f'{R["y1"]:,} kWh',       "Annual Generation",  "Year 1 Estimate",         C_GREEN),
        (f'{R["payback"]} Years',  "Simple Payback",     "Cash Purchase",            colors.HexColor('#1A5276')),
        (f'{R["irr"]}%',           "IRR — 25 Years",     "Internal Rate of Return",  C_GOLD),
    ]
    for i,(v,l,s,col) in enumerate(kpis_r1):
        kpi(c, M+i*(kw+1*mm), y-kh, kw, kh, v, l, s, col)
    y -= kh+3*mm

    kpis_r2 = [
        (f'{RS}{R["lcoe"]:.2f}/kWh',  "LCOE",              "Levelised Cost of Energy",  C_GOLD),
        (fmt(R["npv"]),               "Net Present Value", f'@ {INP["discount"]}% Disc. Rate', C_GREEN),
        (fmt(R["profit25"]),          "Net Profit — 25yr", "Cash Scenario",               colors.HexColor('#1A5276')),
        (f'{INP["ghi"]} kWh/m\u00b2',"Daily Irradiance",  "NASA POWER Data",             C_NAVY2),
    ]
    for i,(v,l,s,col) in enumerate(kpis_r2):
        kpi(c, M+i*(kw+1*mm), y-kh, kw, kh, v, l, s, col)
    y -= kh+4*mm

    # ── KPI GRID ROW — LOAN ──
    y = sec(c, M, y, CW, "KEY PERFORMANCE INDICATORS — BANK LOAN SCENARIO",
            f'{INP["bank"].split(" — ")[0]} @ {INP["interest"]}%')
    kpis_loan = [
        (fmt_full(L["dp"]),           "Down Payment",      f'{INP["down_pct"]}% Upfront',  C_NAVY2),
        (fmt_full(L["emi"]),          "Monthly EMI",       "Rs./Month",                     C_GOLD),
        (f'{L["payback"]} Years',     "Loan Payback",      "With Financing",                C_GREEN),
        (f'{L["irr"]}%' if L["irr"] else "N/A",
                                      "Loan IRR — 25yr",   "With Financing",                colors.HexColor('#1A5276')),
    ]
    for i,(v,l,s,col) in enumerate(kpis_loan):
        kpi(c, M+i*(kw+1*mm), y-kh, kw, kh, v, l, s, col)
    y -= kh+4*mm

    # ── SYSTEM PARAMETERS TABLE ──
    y = sec(c, M, y, CW, "SYSTEM & PROJECT PARAMETERS")

    params = [
        [("System Capacity",    f'{INP["capacity_kw"]} kWp'),
         ("Installation City",  f'{INP["city"]}, {INP["state"]}')],
        [("Installation Cost",  f'{RS}{INP["cost_per_kw"]:,}/kW'),
         ("Gross Project Cost", fmt_full(R["cost"]))],
        [("PM Surya Ghar Sub.", fmt_full(INP["subsidy"])),
         ("Net Project Cost",   fmt_full(R["nc"]))],
        [("Panel Efficiency",   f'{INP["panel_eff"]}%'),
         ("Performance Ratio",  f'{INP["pr"]:.0%}')],
        [("Import Tariff",      f'{RS}{INP["import_tariff"]:.2f}/kWh'),
         ("Export FiT (NM)",    f'{RS}{INP["export_fit"]:.2f}/kWh')],
        [("Self Consumption",   f'{INP["self_cons"]:.0%}'),
         ("Tariff Escalation",  f'{INP["tariff_esc"]:.0%} per annum')],
        [("Annual O&M (Yr 1)", fmt_full(INP["om_yr1"])),
         ("O&M Escalation",     f'{INP["om_esc"]:.0%} per annum')],
        [("Panel Degradation",  f'{INP["degradation"]:.1%}/yr'),
         ("Inverter Replacement", f'{fmt_full(INP["inv_replace"])} at Year 12')],
        [("System Design Life", f'{INP["life"]} Years'),
         ("Discount Rate (NPV)", f'{INP["discount"]}% per annum')],
        [("Daily GHI (NASA)",   f'{INP["ghi"]} kWh/m\u00b2/day'),
         ("Year 1 Yield",       f'{R["y1"]:,} kWh')],
    ]

    col_w = CW/4; rh = 6.5*mm
    for ri, row in enumerate(params):
        bg = C_ROW_ALT if ri%2==0 else C_WHITE
        box(c, M, y-rh, CW, rh, fill=bg)
        for ci,(lbl,val) in enumerate(row):
            bx = M + ci*2*col_w
            txt(c, lbl, bx+2*mm, y-rh+2*mm, 'Sans-B', 7, C_SLATE)
            txt(c, val, bx+col_w+2*mm, y-rh+2*mm, 'Sans', 7.5, C_NAVY)
            if ci==0: vline(c, bx+col_w, y-rh, y, C_BORDER, 0.4)
        vline(c, M+2*col_w, y-rh, y, C_BORDER, 0.8)
        hline(c, M, M+CW, y-rh, C_BORDER, 0.3)
        y -= rh

    box(c, M, y, CW, len(params)*rh, fill=None, stroke=C_BORDER, lw=0.6)

    # ── PROJECT OVERVIEW TEXT ──
    y -= 5*mm
    y = sec(c, M, y, CW, "PROJECT OVERVIEW NARRATIVE")
    narrative = (
        f"This report presents a comprehensive financial feasibility study for a "
        f"{INP['capacity_kw']} kWp on-grid solar photovoltaic system at {INP['city']}, "
        f"{INP['state']}. Based on NASA POWER satellite irradiance data ({INP['ghi']} kWh/m\u00b2/day), "
        f"the system is estimated to generate {R['y1']:,} kWh in Year 1 with a Performance Ratio of "
        f"{INP['pr']:.0%}. After the PM Surya Ghar Muft Bijli Yojana subsidy of "
        f"{fmt_full(INP['subsidy'])}, net project investment is {fmt_full(R['nc'])}. "
        f"The project achieves payback in {R['payback']} years under cash purchase with an IRR of "
        f"{R['irr']}% and 25-year net profit of {fmt_full(R['profit25'])}. Under SBI loan financing "
        f"(Monthly EMI: {fmt_full(L['emi'])}), payback is achieved in {L['payback']} years."
    )
    words = narrative.split()
    line_buf, lines = "", []
    for w in words:
        if len(line_buf)+len(w)+1 <= 110: line_buf += (" " if line_buf else "")+w
        else: lines.append(line_buf); line_buf = w
    if line_buf: lines.append(line_buf)
    for ln in lines:
        txt(c, ln, M, y, 'Sans', 7.5, C_SLATE)
        y -= 5*mm

    c.showPage()

# ═══════════════════════════════════════════════════════════════
#  PAGE 3 — SOLAR YIELD & O&M TABLE
# ═══════════════════════════════════════════════════════════════
def page3_yield(c, R, TP):
    chrome(c, 3, TP, "Solar Yield & O&M Analysis")
    cf = R["cf"]
    M  = 12*mm; CW = W-24*mm
    y  = H-22*mm

    # ── GENERATION CHART ──
    y = sec(c, M, y, CW, "25-YEAR ANNUAL SOLAR GENERATION FORECAST",
            f'Degradation: {INP["degradation"]:.1%}/yr | PR: {INP["pr"]:.0%}')
    yields  = [f["yld"] for f in cf]
    yrs     = [f["y"] for f in cf]
    ycols   = [C_GOLD if i%2==0 else colors.HexColor('#C8A040') for i in range(25)]
    bar_chart(c, M, y-48*mm, CW, 46*mm, yields, yrs, ycols)
    y -= 52*mm

    # Stats strip
    box(c, M, y-9*mm, CW, 9*mm, fill=C_NAVY)
    stats = [
        (f'{cf[0]["yld"]:,} kWh', "Year 1 Generation"),
        (f'{cf[-1]["yld"]:,} kWh',"Year 25 Generation"),
        (f'{sum(f["yld"] for f in cf):,} kWh', "25-Year Cumulative"),
        (f'{RS}{R["lcoe"]:.2f}/kWh', "Levelised Cost of Energy"),
    ]
    sw = CW/4
    for i,(v,l) in enumerate(stats):
        sx = M+i*sw
        txt(c, v, sx+sw/2, y-4*mm, 'Sans-B', 8, C_GOLD2, 'center')
        txt(c, l, sx+sw/2, y-7.5*mm, 'Sans', 5.5, colors.HexColor('#94A3B8'), 'center')
        if i<3: vline(c, sx+sw, y-9*mm, y, C_GOLD, 0.4)
    y -= 12*mm

    # ── YIELD TABLE ──
    y = sec(c, M, y, CW, "YEAR-WISE ENERGY GENERATION & FINANCIAL PERFORMANCE")

    cols  = ["Yr", "Yield\n(kWh)", "Tariff\n(Rs./kWh)", "Bill Saved", "Export\nRevenue",
             "O & M Cost", "Net Income\n(Annual)", "Cumulative\nNet (Rs.)"]
    cws   = [8, 20, 20, 22, 22, 22, 24, 28]  # mm — total = 166mm
    rh    = 5.8*mm

    # Header
    box(c, M, y-rh, CW, rh, fill=C_NAVY)
    xc = M
    for ci,(col,cw) in enumerate(zip(cols,cws)):
        # Multi-line header
        lines = col.split('\n')
        if len(lines)==2:
            txt(c, lines[0], xc+cw*mm/2, y-rh*0.37, 'Sans-B', 6, C_GOLD2, 'center')
            txt(c, lines[1], xc+cw*mm/2, y-rh*0.73, 'Sans-B', 6, C_GOLD2, 'center')
        else:
            txt(c, col, xc+cw*mm/2, y-rh*0.55, 'Sans-B', 6, C_GOLD2, 'center')
        if ci<len(cols)-1: vline(c, xc+cw*mm, y-rh, y, colors.HexColor('#1E3F5A'), 0.5)
        xc += cw*mm
    y -= rh

    for fi,f in enumerate(cf):
        is_inv  = f["y"]==12
        is_pb   = f["y"]==R["payback"]
        if is_inv: bg = colors.HexColor('#FEF9C3')
        elif is_pb: bg = colors.HexColor('#D1FAE5')
        else: bg = C_ROW_ALT if fi%2==0 else C_WHITE
        box(c, M, y-rh, CW, rh, fill=bg)

        om_str  = fmt_full(f["om"])
        if f["extra"]: om_str += f' + {fmt_full(f["extra"])}'
        vals = [
            (str(f["y"]),          'center'),
            (f'{f["yld"]:,}',      'right'),
            (f'{RS}{f["tar"]:.2f}','right'),
            (fmt_full(f["saved"]), 'right'),
            (fmt_full(f["exprev"]),'right'),
            (om_str,               'right'),
            (fmt_full(f["net"]),   'right'),
            (fmt_full(f["cum"]),   'right'),
        ]
        cum_col = C_GREEN if f["cum"]>=0 else C_RED
        xc = M
        for ci,((val,align),cw) in enumerate(zip(vals,cws)):
            fc = C_NAVY if ci==0 else (cum_col if ci==7 else C_SLATE)
            fn = 'Sans-B' if ci in (0,7) else 'Sans'
            px = xc+cw*mm/2 if align=='center' else xc+cw*mm-1.5*mm
            txt(c, val, px, y-rh+1.8*mm, fn, 5.8 if ci==5 else 6.5, fc, align)
            if ci<len(vals)-1: vline(c, xc+cw*mm, y-rh, y, C_BORDER, 0.25)
            xc += cw*mm

        hline(c, M, M+CW, y-rh, C_BORDER, 0.25)
        y -= rh

    box(c, M, y, CW, len(cf)*rh+rh, fill=None, stroke=C_BORDER, lw=0.6)
    y -= 4*mm
    txt(c, f"Note: Yellow row = Inverter replacement year (Year 12) with additional cost of {fmt_full(INP['inv_replace'])}.  "
        f"Green row = Cash purchase payback achieved in Year {R['payback']}.",
        M, y, 'Sans-I', 6.5, C_MUTED)

    c.showPage()

# ═══════════════════════════════════════════════════════════════
#  PAGE 4 — BANK LOAN ANALYSIS
# ═══════════════════════════════════════════════════════════════
def page4_loan(c, R, TP):
    chrome(c, 4, TP, "Bank Loan Financing Analysis")
    L  = R["loan"]
    M  = 12*mm; CW = W-24*mm
    y  = H-22*mm

    # ── LOAN TERMS KPIs ──
    y = sec(c, M, y, CW, "LOAN TERMS & STRUCTURE",
            f'{INP["bank"]} | {INP["interest"]}% p.a. Fixed')
    kw = (CW-4*mm)/5; kh = 19*mm
    L1 = [
        (fmt_full(L["dp"]),       "Down Payment",     f'{INP["down_pct"]}% of Cost',  C_NAVY2),
        (fmt_full(L["lamt"]),     "Loan Principal",   "Amount Financed",               C_GOLD),
        (fmt_full(L["emi"]),      "Monthly EMI",      "Rs./Month",                     C_GREEN),
        (f'{INP["interest"]}%',   "Interest Rate",    "Per Annum (Fixed)",             colors.HexColor('#1A5276')),
        (f'{INP["tenure_yr"]} Yr',"Loan Tenure",      "Repayment Period",              C_NAVY2),
    ]
    for i,(v,l,s,col) in enumerate(L1):
        kpi(c, M+i*(kw+1*mm), y-kh, kw, kh, v, l, s, col)
    y -= kh+3*mm

    L2 = [
        (fmt(L["tint"]),          "Total Interest",    "Over Full Tenure",             C_RED),
        (fmt(L["tpaid"]),         "Total Outflow",     "Down + All EMIs",              C_SLATE),
        (f'{L["payback"]} Yrs',   "Loan Payback",      "With Financing",               C_GREEN),
        (f'{L["irr"]}%' if L["irr"] else "N/A",
                                  "Loan Scenario IRR", "25-Year Return",               C_GOLD),
        (fmt(L["profit25"]),      "Net Profit — 25yr", "Loan Scenario",                colors.HexColor('#1A5276')),
    ]
    for i,(v,l,s,col) in enumerate(L2):
        kpi(c, M+i*(kw+1*mm), y-kh, kw, kh, v, l, s, col)
    y -= kh+5*mm

    # ── CUMULATIVE CASHFLOW CHART ──
    y = sec(c, M, y, CW, "CUMULATIVE NET CASHFLOW — CASH PURCHASE vs. LOAN FINANCING (Rs.)",
            "25-Year Projection")
    years    = [f["y"] for f in R["cf"]]
    cash_cum = [f["cum"] for f in R["cf"]]
    loan_cum = [f["cum"] for f in L["lcf"]]
    line_chart(c, M, y-57*mm, CW, 55*mm,
               [cash_cum, loan_cum], years,
               [C_GREEN, C_GOLD], ["Cash Purchase", "Loan Financing"])
    y -= 62*mm

    # ── COMPARATIVE TABLE ──
    y = sec(c, M, y, CW, "CASH PURCHASE vs. LOAN FINANCING — DETAILED COMPARISON")

    comp = [
        ("Metric",                     "Cash Purchase",           "Loan Financing"),
        ("Upfront Investment Required", fmt_full(R["nc"]),         fmt_full(L["dp"])),
        ("Loan Amount",                 "Not Applicable",          fmt_full(L["lamt"])),
        ("Monthly EMI Obligation",      "Not Applicable",          fmt_full(L["emi"])),
        ("Interest Rate",               "Not Applicable",          f'{INP["interest"]}% p.a. (Fixed)'),
        ("Loan Tenure",                 "Not Applicable",          f'{INP["tenure_yr"]} Years'),
        ("Total Interest Outgo",        "Not Applicable",          fmt_full(L["tint"])),
        ("Total Project Outflow",       fmt_full(R["nc"]),         fmt_full(L["tpaid"])),
        ("Simple Payback Period",       f'{R["payback"]} Years',   f'{L["payback"]} Years'),
        ("25-Year Gross Savings",       fmt_full(R["gross25"]),    "—"),
        ("25-Year Net Profit",          fmt_full(R["profit25"]),   fmt_full(L["profit25"])),
        ("Internal Rate of Return",     f'{R["irr"]}%',            f'{L["irr"]}%' if L["irr"] else "N/A"),
        (f'NPV @ {INP["discount"]}%',   fmt_full(R["npv"]),        fmt_full(L["npv"])),
    ]

    c1, c2, c3 = 62*mm, 54*mm, 54*mm
    rh = 6.5*mm
    for ri, row in enumerate(comp):
        is_hdr = ri==0
        bg = C_NAVY if is_hdr else (C_ROW_ALT if ri%2==0 else C_WHITE)
        box(c, M, y-rh, CW, rh, fill=bg)
        # Col 1
        fn = 'Sans-B'; fc_l = C_GOLD2 if is_hdr else C_SLATE
        txt(c, row[0], M+3*mm, y-rh+2.2*mm, fn, 7.5 if is_hdr else 7, fc_l)
        vline(c, M+c1, y-rh, y, C_BORDER, 0.5)
        # Col 2
        fc2 = C_WHITE if is_hdr else C_GREEN
        txt(c, row[1], M+c1+3*mm, y-rh+2.2*mm, fn if is_hdr else 'Sans',
            7.5 if is_hdr else 7, fc2 if not is_hdr else C_GOLD2)
        vline(c, M+c1+c2, y-rh, y, C_BORDER, 0.5)
        # Col 3
        fc3 = C_WHITE if is_hdr else C_GOLD
        txt(c, row[2], M+c1+c2+3*mm, y-rh+2.2*mm, fn if is_hdr else 'Sans',
            7.5 if is_hdr else 7, fc3 if not is_hdr else C_GOLD2)
        hline(c, M, M+CW, y-rh, C_BORDER, 0.3)
        y -= rh

    box(c, M, y, CW, len(comp)*rh, fill=None, stroke=C_BORDER, lw=0.6)
    c.showPage()

# ═══════════════════════════════════════════════════════════════
#  PAGE 5 — AMORTIZATION SCHEDULE & RECOMMENDATIONS
# ═══════════════════════════════════════════════════════════════
def page5_amort(c, R, TP):
    chrome(c, 5, TP, "Amortization Schedule & Recommendations")
    L  = R["loan"]
    M  = 12*mm; CW = W-24*mm
    y  = H-22*mm

    # ── NET BENEFIT BAR CHART ──
    y = sec(c, M, y, CW, "ANNUAL NET BENEFIT — SOLAR SAVINGS MINUS LOAN EMI (Rs.)",
            "Positive = Surplus  |  Negative = Top-up Required")
    net_ben = [f["net"] for f in L["lcf"]]
    yrs     = [f["y"] for f in L["lcf"]]
    nbcols  = [C_GREEN if v>=0 else C_RED for v in net_ben]
    bar_chart(c, M, y-43*mm, CW, 41*mm, net_ben, yrs, nbcols, show_zero=True)
    y -= 48*mm

    # ── AMORTIZATION TABLE ──
    y = sec(c, M, y, CW, f"LOAN AMORTIZATION SCHEDULE — ANNUAL SUMMARY",
            f'{INP["bank"]} @ {INP["interest"]}% | Tenure: {INP["tenure_yr"]} Years')

    cols = ["Loan\nYear", "Annual\nEMI", "Principal\nRepaid",
            "Interest\nPaid", "Closing\nBalance", "Solar Net\nIncome", "Net\nBenefit"]
    cws  = [14, 24, 24, 24, 28, 28, 24]  # mm = 166
    rh   = 6.5*mm

    # Header
    box(c, M, y-rh, CW, rh, fill=C_NAVY)
    xc = M
    for ci,(col,cw) in enumerate(zip(cols,cws)):
        lines = col.split('\n')
        if len(lines)==2:
            txt(c, lines[0], xc+cw*mm/2, y-rh*0.35, 'Sans-B', 6.5, C_GOLD2, 'center')
            txt(c, lines[1], xc+cw*mm/2, y-rh*0.72, 'Sans-B', 6.5, C_GOLD2, 'center')
        else:
            txt(c, col, xc+cw*mm/2, y-rh*0.55, 'Sans-B', 6.5, C_GOLD2, 'center')
        if ci<len(cols)-1: vline(c, xc+cw*mm, y-rh, y, colors.HexColor('#1E3F5A'), 0.5)
        xc += cw*mm
    y -= rh

    t_emi = t_prin = t_int = t_sol = t_nb = 0
    for yr in range(1, INP["tenure_yr"]+1):
        sl    = L["amort"][(yr-1)*12 : yr*12]
        y_emi = sum(m["emi"] for m in sl)
        y_pri = sum(m["p"]   for m in sl)
        y_int = sum(m["i"]   for m in sl)
        y_bal = sl[-1]["bal"]
        lc    = L["lcf"][yr-1]
        nb    = lc["net"]
        t_emi+=y_emi; t_prin+=y_pri; t_int+=y_int; t_sol+=lc["solar"]; t_nb+=nb

        bg = C_ROW_ALT if yr%2==0 else C_WHITE
        box(c, M, y-rh, CW, rh, fill=bg)

        vals = [
            (str(yr),           'center'),
            (fmt_full(y_emi),   'right'),
            (fmt_full(y_pri),   'right'),
            (fmt_full(y_int),   'right'),
            (fmt_full(y_bal),   'right'),
            (fmt_full(lc["solar"]), 'right'),
            (fmt_full(nb),      'right'),
        ]
        xc = M
        for ci,((val,align),cw) in enumerate(zip(vals,cws)):
            fc = C_NAVY if ci==0 else (C_GREEN if (ci==6 and nb>=0) else (C_RED if (ci==6 and nb<0) else C_SLATE))
            fn = 'Sans-B' if ci==0 else 'Sans'
            px = xc+cw*mm/2 if align=='center' else xc+cw*mm-1.5*mm
            txt(c, val, px, y-rh+2*mm, fn, 7, fc, align)
            if ci<len(vals)-1: vline(c, xc+cw*mm, y-rh, y, C_BORDER, 0.3)
            xc += cw*mm
        hline(c, M, M+CW, y-rh, C_BORDER, 0.3)
        y -= rh

    # Totals row
    box(c, M, y-rh, CW, rh, fill=C_NAVY2)
    totals = [
        ("TOTAL",          'center'),
        (fmt_full(t_emi),  'right'),
        (fmt_full(t_prin), 'right'),
        (fmt_full(t_int),  'right'),
        ("—",              'center'),
        (fmt_full(t_sol),  'right'),
        (fmt_full(t_nb),   'right'),
    ]
    xc = M
    for ci,((val,align),cw) in enumerate(zip(totals,cws)):
        fc = C_GOLD2 if ci==0 else C_WHITE
        px = xc+cw*mm/2 if align=='center' else xc+cw*mm-1.5*mm
        txt(c, val, px, y-rh+2*mm, 'Sans-B', 7, fc, align)
        if ci<len(vals)-1: vline(c, xc+cw*mm, y-rh, y, colors.HexColor('#1E3F5A'), 0.4)
        xc += cw*mm
    y -= rh
    box(c, M, y, CW, (INP["tenure_yr"]+2)*rh, fill=None, stroke=C_BORDER, lw=0.6)
    y -= 5*mm

    # ── RECOMMENDATIONS ──
    y = sec(c, M, y, CW, "KEY FINANCIAL INSIGHTS & RECOMMENDATIONS")

    diff     = R["profit25"] - L["profit25"]
    emi_cov  = R["cf"][0]["net"] / 12
    diff_pb  = (L["payback"] or 25) - (R["payback"] or 25)

    insights = [
        (C_GREEN,  "PAYBACK PERIOD ANALYSIS",
         f"Cash purchase achieves payback in {R['payback']} years. Loan financing achieves payback in "
         f"{L['payback']} years — {abs(diff_pb)} years {'sooner' if diff_pb<0 else 'later'} due to lower "
         f"upfront outlay of {fmt_full(L['dp'])} vs. {fmt_full(R['nc'])}."),
        (C_GOLD,   "PROFITABILITY COMPARISON",
         f"Cash IRR of {R['irr']}% vs. Loan IRR of {L['irr']}%. The higher loan IRR reflects leverage on "
         f"smaller upfront capital. 25-year cash profit is {fmt_full(R['profit25'])} vs. "
         f"{fmt_full(L['profit25'])} under loan — a difference of {fmt_full(abs(int(diff)))}."),
        (colors.HexColor('#1A5276'), "EMI SERVICEABILITY",
         f"Monthly solar income in Year 1 is approximately {fmt_full(int(emi_cov))}, which "
         f"{'comfortably covers' if emi_cov >= L['emi'] else 'partially covers'} the monthly EMI "
         f"of {fmt_full(L['emi'])}. "
         f"{'No top-up required from Year 1.' if emi_cov >= L['emi'] else 'Marginal top-up required in early years.'}"),
        (C_RED,    "INTEREST COST OPTIMISATION",
         f"Total interest payable over {INP['tenure_yr']} years is {fmt_full(L['tint'])}. Part-prepayment "
         f"after Year 3 (if surplus available) can reduce total interest outgo significantly. "
         f"From Year {INP['tenure_yr']+1}, entire solar income becomes net surplus."),
        (C_NAVY2,  "RECOMMENDATION",
         f"If capital is available, cash purchase maximises 25-year returns by {fmt_full(abs(int(diff)))}. "
         f"For capital-constrained investors, SBI Surya Ghar scheme at {INP['interest']}% p.a. remains "
         f"the most cost-effective financing option with full EMI coverage from solar savings."),
    ]

    for col, title, body in insights:
        if y < 38*mm: break
        box(c, M, y-5.5*mm, 3, 5.5*mm, fill=col)
        txt(c, title, M+5*mm, y-1.2*mm, 'Sans-B', 7.5, col)
        y -= 6.5*mm
        words = body.split()
        line_buf, lines = "", []
        for w in words:
            if len(line_buf)+len(w)+1 <= 113: line_buf += (" " if line_buf else "")+w
            else: lines.append(line_buf); line_buf = w
        if line_buf: lines.append(line_buf)
        for ln in lines:
            if y < 35*mm: break
            txt(c, ln, M+5*mm, y, 'Sans', 7.2, C_SLATE)
            y -= 4.8*mm
        y -= 2*mm

    # Disclaimer box
    if y > 28*mm:
        bh = min(y-15*mm, 18*mm)
        box(c, M, 14*mm, CW, bh, fill=C_LIGHT, stroke=C_BORDER, lw=0.5)
        box(c, M, 14*mm, 3, bh, fill=C_GOLD)
        disc = ("DISCLAIMER: This report is prepared for indicative purposes only. "
                "Actual solar yield depends on local weather, shading, soiling, orientation and system losses. "
                "Tariffs, bank rates and subsidies are subject to revision without notice. "
                "Consult a CEIG-certified solar installer and your bank before final commitment. "
                "Subsidy subject to MNRE/DISCOM approval.")
        words = disc.split(); lbuf, dlines = "", []
        for w in words:
            if len(lbuf)+len(w)+1<=110: lbuf+=(" " if lbuf else "")+w
            else: dlines.append(lbuf); lbuf=w
        if lbuf: dlines.append(lbuf)
        dy = 14*mm+bh-5*mm
        txt(c, "DISCLAIMER", M+5*mm, dy, 'Sans-B', 7, C_GOLD)
        dy -= 5*mm
        for ln in dlines:
            if dy < 15*mm: break
            txt(c, ln, M+5*mm, dy, 'Sans-I', 6.5, C_MUTED)
            dy -= 4.5*mm

    c.showPage()

# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════
def build(filename="solar_report_v2.pdf"):
    print("Running simulation...")
    R = simulate()
    L = R["loan"]
    print(f"  Net Cost:     {fmt_full(R['nc'])}")
    print(f"  Year 1 Yield: {R['y1']:,} kWh")
    print(f"  Cash Payback: {R['payback']} years  |  IRR: {R['irr']}%")
    print(f"  Monthly EMI:  {fmt_full(L['emi'])}  |  Loan Payback: {L['payback']} years")

    TP = 5
    c = canvas.Canvas(filename, pagesize=A4)
    c.setTitle("SolarYield India — Solar PV Investment Feasibility Report")
    c.setAuthor("SolarYield India Pvt. Ltd.")
    c.setSubject(f"Solar PV Financial Analysis | {INP['client']} | {INP['city']}")

    print("Building 5-page premium report...")
    page1_cover(c, R)
    page2_exec(c, R, TP)
    page3_yield(c, R, TP)
    page4_loan(c, R, TP)
    page5_amort(c, R, TP)

    c.save()
    print(f"Done! Saved: {filename}")

if __name__ == "__main__":
    build("solar_report_v2.pdf")
