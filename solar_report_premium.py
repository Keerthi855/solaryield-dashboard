"""
SolarYield India — Premium Corporate Report Generator
Indian Corporate Standards: Navy + Gold palette, geometric design
"""

import math, datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

W, H = A4   # 210 x 297 mm → 595.27 x 841.89 pt

# ── BRAND PALETTE ──────────────────────────────────────────────
NAVY      = colors.HexColor('#0A1628')   # Deep navy (primary)
NAVY2     = colors.HexColor('#112240')   # Section bg
NAVY3     = colors.HexColor('#1B3A6B')   # Lighter navy
GOLD      = colors.HexColor('#C9922A')   # Saffron gold (accent)
GOLD2     = colors.HexColor('#F0B429')   # Bright gold
GOLD_LT   = colors.HexColor('#FDF3DC')   # Gold tint bg
GREEN     = colors.HexColor('#1A7A4A')   # Prosperity green
GREEN_LT  = colors.HexColor('#E8F5EE')
RED_IND   = colors.HexColor('#B91C1C')
RED_LT    = colors.HexColor('#FEE2E2')
SLATE     = colors.HexColor('#334155')
MUTED     = colors.HexColor('#64748B')
BORDER    = colors.HexColor('#CBD5E1')
LIGHT     = colors.HexColor('#F8FAFC')
WHITE     = colors.HexColor('#FFFFFF')
RULE      = colors.HexColor('#E2E8F0')

# ── SIMULATION INPUTS ───────────────────────────────────────────
INPUTS = {
    "city":               "Bengaluru",
    "state":              "Karnataka",
    "client_name":        "M/s Sunrise Infra Pvt. Ltd.",
    "project_ref":        "SYI/2025-26/KA/0042",
    "prepared_by":        "SolarYield India Pvt. Ltd.",
    "capacity_kw":        10.0,
    "install_cost_per_kw":45000,
    "subsidy":            94500,
    "panel_eff":          20.5,
    "pr":                 0.80,
    "degradation":        0.005,
    "system_life":        25,
    "ghi_kwh_m2_day":     5.3,
    "import_tariff":      6.50,
    "export_fit":         3.82,
    "tariff_escalation":  0.03,
    "self_consumption":   0.75,
    "annual_om":          5000,
    "om_escalation":      0.04,
    "inverter_replacement":40000,
    "loan_enabled":       True,
    "bank_name":          "SBI Surya Ghar Scheme",
    "interest_rate":      9.15,
    "loan_tenure_yr":     7,
    "down_payment_pct":   20,
    "moratorium_months":  0,
    "discount_rate":      8.0,
}

# ── HELPERS ─────────────────────────────────────────────────────
def inr(v, cr=False):
    """Format as Indian Rupee"""
    if v is None: return "N/A"
    v = int(round(abs(v)))
    neg = int(round(v)) != int(round(abs(v)))  # can't detect easily, pass raw
    s = str(v)
    if len(s) > 3:
        s = s[:-3] + "," + s[-3:]
    if len(s) > 7:
        s = s[:-7] + "," + s[-7:]
    if len(s) > 11:
        s = s[:-11] + "," + s[-11:]
    result = "\u20b9" + s
    if cr and v >= 10000000:
        cr_val = v / 10000000
        result = f"\u20b9{cr_val:.2f} Cr"
    elif v >= 100000:
        lac_val = v / 100000
        result = f"\u20b9{lac_val:.2f} L"
    return result

def inr_full(v):
    if v is None: return "N/A"
    neg = v < 0
    v = int(round(abs(v)))
    s = str(v)
    if len(s) > 3:   s = s[:-3] + "," + s[-3:]
    if len(s) > 7:   s = s[:-7] + "," + s[-7:]
    if len(s) > 11:  s = s[:-11] + "," + s[-11:]
    return ("\u20b9-" if neg else "\u20b9") + s

def calcEMI(p, annual_r, n):
    if annual_r == 0: return p / n
    r = annual_r / 100 / 12
    return p * r * (1+r)**n / ((1+r)**n - 1)

def calcIRR(cost, flows):
    all_flows = [-cost] + flows
    r = 0.10
    for _ in range(200):
        npv  = sum(f/(1+r)**i for i,f in enumerate(all_flows))
        dnpv = sum(-i*f/(1+r)**(i+1) for i,f in enumerate(all_flows))
        if abs(dnpv) < 1e-10: break
        r -= npv/dnpv
        if r <= -1: r = -0.999
    return r if -1 < r < 10 else None

# ── SIMULATION ENGINE ────────────────────────────────────────────
def simulate(inp):
    cap   = inp["capacity_kw"]
    cost  = cap * inp["install_cost_per_kw"]
    sub   = inp["subsidy"]
    nc    = cost - sub
    life  = inp["system_life"]
    ghi   = inp["ghi_kwh_m2_day"]
    pr    = inp["pr"]
    deg   = inp["degradation"]
    esc   = inp["tariff_escalation"]
    om0   = inp["annual_om"]
    om_e  = inp["om_escalation"]
    sc    = inp["self_consumption"]
    disc  = inp["discount_rate"] / 100
    imp_t = inp["import_tariff"]
    exp_t = inp["export_fit"]
    inv_r = inp["inverter_replacement"]

    y1_yield = cap * ghi * 365 * pr
    cashflow, cum, npv_c = [], -nc, -nc

    for y in range(1, life+1):
        df     = (1-deg)**(y-1)
        yld    = y1_yield * df
        tariff = imp_t * (1+esc)**(y-1)
        expfit = exp_t * (1+esc)**(y-1)
        saved  = yld * sc * tariff
        exprev = yld * (1-sc) * expfit
        om     = om0 * (1+om_e)**(y-1)
        extra  = inv_r if y == 12 else 0
        gross  = saved + exprev
        net    = gross - om - extra
        cum   += net
        npv_c += net / (1+disc)**y
        cashflow.append(dict(year=y, yield_kwh=round(yld), tariff=round(tariff,2),
            saved=round(saved), exprev=round(exprev), gross=round(gross),
            om=round(om), extra=extra, net=round(net), cum=round(cum)))

    payback = next((cf["year"] for cf in cashflow if cf["cum"]>=0), None)
    irr     = calcIRR(nc, [cf["net"] for cf in cashflow])
    total_om = sum(cf["om"]+cf["extra"] for cf in cashflow)
    total_yield = sum(cf["yield_kwh"] for cf in cashflow)
    lcoe    = (nc + total_om) / total_yield if total_yield else 0

    res = dict(inp=inp, cost=round(cost), nc=round(nc),
               y1=round(y1_yield), cf=cashflow,
               payback=payback, irr=round(irr*100,2) if irr else None,
               npv=round(npv_c), lcoe=round(lcoe,2),
               gross_25=round(cashflow[-1]["cum"]+nc),
               profit_25=round(cashflow[-1]["cum"]))

    if inp["loan_enabled"]:
        dp_pct = inp["down_payment_pct"]/100
        down   = round(nc * dp_pct)
        lamt   = nc - down
        n_m    = inp["loan_tenure_yr"] * 12
        emi    = calcEMI(lamt, inp["interest_rate"], n_m)
        ann_emi= emi * 12

        # Amortization
        amort, bal, tot_int = [], lamt, 0
        r_m = inp["interest_rate"]/100/12
        for m in range(1, n_m+1):
            interest  = bal * r_m
            principal = emi - interest
            bal       = max(0, bal - principal)
            tot_int  += interest
            amort.append(dict(m=m, emi=round(emi), prin=round(principal),
                              int=round(interest), bal=round(bal)))

        # Annual loan cashflow
        lcf, lcum, lnpv = [], -down, -down
        for cf in cashflow:
            y      = cf["year"]
            emi_yr = ann_emi if y <= inp["loan_tenure_yr"] else 0
            net    = cf["net"] - emi_yr
            lcum  += net
            lnpv  += net/(1+disc)**y
            lcf.append(dict(year=y, net_income=cf["net"],
                            emi=round(emi_yr), net=round(net), cum=round(lcum)))

        l_payback = next((lc["year"] for lc in lcf if lc["cum"]>=0), None)
        l_irr     = calcIRR(down, [lc["net"] for lc in lcf])
        res["loan"] = dict(
            down=down, lamt=round(lamt), emi=round(emi), n_m=n_m,
            tot_int=round(tot_int), tot_paid=round(emi*n_m+down),
            amort=amort, lcf=lcf, payback=l_payback,
            irr=round(l_irr*100,2) if l_irr else None,
            npv=round(lnpv), profit_25=round(lcf[-1]["cum"]),
            ann_emi=round(ann_emi)
        )
    return res

# ── CANVAS DRAWING PRIMITIVES ────────────────────────────────────
def set_font(c, name="Helvetica", size=10, color=None):
    c.setFont(name, size)
    if color: c.setFillColor(color)

def draw_rect(c, x, y, w, h, fill=None, stroke=None, lw=0.5, radius=0):
    if fill:   c.setFillColor(fill)
    if stroke: c.setStrokeColor(stroke); c.setLineWidth(lw)
    if radius:
        c.roundRect(x, y, w, h, radius, fill=bool(fill), stroke=bool(stroke))
    else:
        c.rect(x, y, w, h, fill=bool(fill), stroke=bool(stroke))

def text(c, txt, x, y, font="Helvetica", size=9, color=SLATE, align="left"):
    c.setFont(font, size)
    c.setFillColor(color)
    if align == "center": c.drawCentredString(x, y, str(txt))
    elif align == "right": c.drawRightString(x, y, str(txt))
    else: c.drawString(x, y, str(txt))

def hline(c, x1, y, x2, color=RULE, lw=0.5):
    c.setStrokeColor(color)
    c.setLineWidth(lw)
    c.line(x1, y, x2, y)

def vline(c, x, y1, y2, color=RULE, lw=0.5):
    c.setStrokeColor(color)
    c.setLineWidth(lw)
    c.line(x, y1, x, y2)

# ── HEADER / FOOTER (all inner pages) ───────────────────────────
def page_chrome(c, page_num, total_pages, title, inp):
    # Top bar — navy strip
    draw_rect(c, 0, H-22*mm, W, 22*mm, fill=NAVY)
    # Gold accent line
    draw_rect(c, 0, H-22*mm, W, 1.5, fill=GOLD)
    # Logo area — sun icon (drawn)
    cx, cy = 15*mm, H-11*mm
    c.setFillColor(GOLD)
    c.circle(cx, cy, 5*mm, fill=1, stroke=0)
    # Sun rays
    c.setStrokeColor(GOLD2)
    c.setLineWidth(1.2)
    import math as _m
    for ang in range(0, 360, 45):
        rad = _m.radians(ang)
        c.line(cx+5.8*mm*_m.cos(rad), cy+5.8*mm*_m.sin(rad),
               cx+7.5*mm*_m.cos(rad), cy+7.5*mm*_m.sin(rad))
    # Company name
    text(c, "SOLARYIELD INDIA", 24*mm, H-9*mm,  "Helvetica-Bold", 11, WHITE)
    text(c, "Solar PV Financial Analysis Platform", 24*mm, H-14*mm, "Helvetica", 7, colors.HexColor('#94A3B8'))
    # Page title (centered)
    text(c, title.upper(), W/2, H-10*mm, "Helvetica-Bold", 10, GOLD, "center")
    # Right — ref & date
    now = datetime.datetime.now().strftime("%d %b %Y")
    text(c, f"Ref: {inp['project_ref']}", W-15*mm, H-9*mm, "Helvetica", 7, colors.HexColor('#94A3B8'), "right")
    text(c, f"Date: {now}", W-15*mm, H-14*mm, "Helvetica", 7, colors.HexColor('#94A3B8'), "right")

    # Footer
    draw_rect(c, 0, 0, W, 13*mm, fill=NAVY)
    draw_rect(c, 0, 13*mm, W, 0.8, fill=GOLD)
    text(c, inp["prepared_by"], 15*mm, 5*mm, "Helvetica", 7, colors.HexColor('#94A3B8'))
    text(c, "CONFIDENTIAL — For Authorized Use Only", W/2, 5*mm, "Helvetica-Oblique", 7,
         colors.HexColor('#64748B'), "center")
    text(c, f"Page {page_num} of {total_pages}", W-15*mm, 5*mm, "Helvetica-Bold", 7, GOLD, "right")

# ── SECTION TITLE BAR ────────────────────────────────────────────
def section_bar(c, x, y, w, title, icon="", color=NAVY3):
    draw_rect(c, x, y-6*mm, w, 7*mm, fill=color)
    draw_rect(c, x, y-6*mm, 2.5, 7*mm, fill=GOLD)
    text(c, f"{icon}  {title}" if icon else title, x+5*mm, y-3.5*mm,
         "Helvetica-Bold", 9, WHITE)
    return y - 8*mm

# ── KPI CARD ────────────────────────────────────────────────────
def kpi_card(c, x, y, w, h, value, unit, label, val_color=GOLD, bg=NAVY2):
    draw_rect(c, x, y, w, h, fill=bg, radius=2)
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.5)
    c.roundRect(x, y, w, h, 2, fill=0, stroke=1)
    # Gold top accent
    draw_rect(c, x, y+h-1.5, w, 1.5, fill=val_color)
    # Value
    text(c, str(value), x+w/2, y+h*0.45, "Helvetica-Bold", 13, val_color, "center")
    # Unit
    text(c, str(unit), x+w/2, y+h*0.28, "Helvetica", 6.5, colors.HexColor('#94A3B8'), "center")
    # Label
    text(c, str(label), x+w/2, y+7, "Helvetica-Bold", 6, colors.HexColor('#CBD5E1'), "center")

# ── BAR CHART ───────────────────────────────────────────────────
def draw_bar_chart(c, x, y, w, h, data, labels, bar_colors,
                   show_zero=False, y_label=""):
    if not data: return
    max_v = max(abs(v) for v in data) or 1
    min_v = min(data)
    n = len(data)

    # Background
    draw_rect(c, x, y, w, h, fill=colors.HexColor('#F8FAFC'))
    c.setStrokeColor(RULE)
    c.setLineWidth(0.3)
    c.rect(x, y, w, h, fill=0, stroke=1)

    # Grid lines (horizontal)
    for i in range(1, 5):
        gy = y + i * h / 4
        c.setStrokeColor(RULE)
        c.setLineWidth(0.25)
        c.line(x, gy, x+w, gy)

    bar_w   = w / n * 0.65
    gap     = w / n * 0.35
    plot_h  = h * 0.85
    base_y  = y + h * 0.08

    rng = max_v - min(min_v, 0) or 1
    zero_y = base_y + ((-min_v) / (max_v - min_v + 0.001)) * plot_h if min_v < 0 else base_y

    # Zero line
    if show_zero or min_v < 0:
        c.setStrokeColor(SLATE)
        c.setLineWidth(0.6)
        c.line(x, zero_y, x+w, zero_y)

    for i, (val, col) in enumerate(zip(data, bar_colors)):
        bx  = x + i * (bar_w + gap) + gap/2
        bh  = abs(val) / max_v * plot_h * 0.9
        by  = zero_y if val >= 0 else zero_y - bh
        c.setFillColor(col)
        c.rect(bx, by, bar_w, bh, fill=1, stroke=0)
        # Label every 5 years
        if i % 5 == 0 or i == n-1:
            c.setFont("Helvetica", 5)
            c.setFillColor(MUTED)
            c.drawCentredString(bx + bar_w/2, y+2, str(labels[i]))

# ── LINE CHART ──────────────────────────────────────────────────
def draw_line_chart(c, x, y, w, h, series_list, labels, line_colors, line_labels=None):
    if not series_list or not series_list[0]: return
    all_v = [v for s in series_list for v in s]
    max_v, min_v = max(all_v), min(all_v)
    rng = max_v - min_v or 1
    n   = len(labels)

    draw_rect(c, x, y, w, h, fill=colors.HexColor('#F8FAFC'))
    c.setStrokeColor(RULE)
    c.setLineWidth(0.3)
    c.rect(x, y, w, h, fill=0, stroke=1)

    for i in range(1, 5):
        gy = y + i * h / 4
        c.setStrokeColor(RULE); c.setLineWidth(0.25)
        c.line(x, gy, x+w, gy)

    # Y axis labels
    for i in range(5):
        gv  = min_v + i * rng / 4
        gy  = y + i * h / 4
        lbl = f"{gv/100000:.1f}L" if abs(gv) >= 100000 else f"{int(gv/1000)}k" if abs(gv) >= 1000 else str(int(gv))
        c.setFont("Helvetica", 4.5); c.setFillColor(MUTED)
        c.drawRightString(x-1*mm, gy-2, lbl)

    zero_y = y + ((-min_v)/rng)*h if min_v < 0 else y
    if min_v < 0:
        c.setStrokeColor(SLATE); c.setLineWidth(0.8)
        c.line(x, zero_y, x+w, zero_y)

    plot_w = w
    plot_h = h
    for series, col, lw in zip(series_list, line_colors, [1.5, 1.2, 1.0]):
        pts = []
        for i, v in enumerate(series):
            px = x + i * plot_w / (n-1)
            py = y + ((v - min_v)/rng)*plot_h
            pts.append((px, py))
        c.setStrokeColor(col); c.setLineWidth(lw)
        p = c.beginPath()
        p.moveTo(*pts[0])
        for pt in pts[1:]: p.lineTo(*pt)
        c.drawPath(p, stroke=1, fill=0)

    # X labels
    c.setFont("Helvetica", 5); c.setFillColor(MUTED)
    for i in range(0, n, 5):
        px = x + i * plot_w / (n-1)
        c.drawCentredString(px, y-4*mm, f"Yr {labels[i]}")
    c.drawCentredString(x + (n-1)*plot_w/(n-1), y-4*mm, f"Yr {labels[-1]}")

    # Legend
    if line_labels:
        lx = x + w - 55*mm
        ly = y + h - 5*mm
        for i, (lbl, col) in enumerate(zip(line_labels, line_colors)):
            c.setFillColor(col)
            c.rect(lx + i*28*mm, ly, 10, 4, fill=1, stroke=0)
            c.setFont("Helvetica", 6); c.setFillColor(SLATE)
            c.drawString(lx + i*28*mm + 12, ly, lbl)

# ═══════════════════════════════════════════════════════════════
# PAGE 1 — PREMIUM COVER
# ═══════════════════════════════════════════════════════════════
def page_cover(c, res):
    inp = res["inp"]
    loan = res.get("loan")

    # Full navy background top half
    draw_rect(c, 0, H*0.45, W, H*0.55, fill=NAVY)

    # Geometric decorative circles (top right)
    import math as _m
    c.setStrokeColor(colors.HexColor('#1B3A6B'))
    c.setLineWidth(0.5)
    for r in [40, 70, 100, 130]:
        c.circle(W - 10*mm, H - 10*mm, r, fill=0, stroke=1)
    # Gold arc
    c.setStrokeColor(GOLD); c.setLineWidth(2)
    c.arc(W-150, H-150, W+30, H+30, 180, 90)

    # Diagonal gold stripe (decorative)
    c.setFillColor(colors.HexColor('#C9922A22'))
    p = c.beginPath()
    p.moveTo(0, H*0.55)
    p.lineTo(W*0.6, H*0.55)
    p.lineTo(W*0.5, H*0.45)
    p.lineTo(0, H*0.45)
    p.close()
    c.drawPath(p, fill=1, stroke=0)

    # Sun logo (large, decorative)
    sux, suy = 25*mm, H - 55*mm
    c.setFillColor(GOLD)
    c.circle(sux, suy, 14*mm, fill=1, stroke=0)
    c.setFillColor(NAVY)
    c.circle(sux, suy, 10*mm, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.circle(sux, suy, 6*mm, fill=1, stroke=0)
    # Rays
    c.setStrokeColor(GOLD2); c.setLineWidth(1.5)
    for ang in range(0, 360, 30):
        rad = _m.radians(ang)
        c.line(sux+15*mm*_m.cos(rad), suy+15*mm*_m.sin(rad),
               sux+19*mm*_m.cos(rad), suy+19*mm*_m.sin(rad))

    # Company brand
    text(c, "SOLARYIELD INDIA", 45*mm, H-42*mm, "Helvetica-Bold", 18, GOLD2)
    text(c, "PRIVATE LIMITED", 45*mm, H-49*mm, "Helvetica", 9, colors.HexColor('#94A3B8'))

    # Gold rule
    draw_rect(c, 15*mm, H-55*mm, W-30*mm, 1.5, fill=GOLD)

    # Report title
    text(c, "SOLAR PHOTOVOLTAIC", 15*mm, H-67*mm, "Helvetica-Bold", 22, WHITE)
    text(c, "INVESTMENT FEASIBILITY REPORT", 15*mm, H-78*mm, "Helvetica-Bold", 22, WHITE)
    text(c, "With Bank Loan Financing Analysis", 15*mm, H-88*mm, "Helvetica-Oblique", 12,
         colors.HexColor('#94A3B8'))

    # Lower half — white background
    draw_rect(c, 0, 0, W, H*0.45, fill=WHITE)

    # Gold separator
    draw_rect(c, 0, H*0.45, W, 2, fill=GOLD)

    # Project details box (left)
    bx, by, bw, bh = 15*mm, H*0.45 - 80*mm, 110*mm, 75*mm
    draw_rect(c, bx, by, bw, bh, fill=LIGHT, radius=3)
    c.setStrokeColor(BORDER); c.setLineWidth(0.5)
    c.roundRect(bx, by, bw, bh, 3, fill=0, stroke=1)
    draw_rect(c, bx, by+bh-8*mm, bw, 8*mm, fill=NAVY2, radius=3)
    text(c, "PROJECT DETAILS", bx+bw/2, by+bh-5*mm, "Helvetica-Bold", 8, WHITE, "center")

    details = [
        ("Client / Applicant", inp["client_name"]),
        ("Project Location",   f'{inp["city"]}, {inp["state"]}'),
        ("System Capacity",    f'{inp["capacity_kw"]} kWp On-Grid Solar PV'),
        ("Total Project Cost", inr_full(res["cost"])),
        ("PM Surya Ghar Subsidy", inr_full(inp["subsidy"])),
        ("Net Investment",     inr_full(res["nc"])),
        ("Report Reference",   inp["project_ref"]),
        ("Prepared By",        inp["prepared_by"]),
    ]
    dy = by + bh - 14*mm
    for label, val in details:
        text(c, label, bx+4*mm, dy, "Helvetica", 7, MUTED)
        text(c, val,   bx+bw-4*mm, dy, "Helvetica-Bold", 7.5, NAVY, "right")
        dy -= 7*mm
        hline(c, bx+4*mm, dy+5*mm, bx+bw-4*mm, RULE, 0.3)

    # Key metrics panel (right)
    rx, ry, rw = 135*mm, H*0.45 - 80*mm, 60*mm
    metrics = [
        (f'{res["payback"]} Yrs', "Payback Period",  GREEN, "Cash Purchase"),
        (f'{res["irr"]}%',       "IRR (25 Year)",    GOLD, "Internal Rate"),
        (inr(res["nc"]),         "Net Investment",   NAVY3, "After Subsidy"),
        (f'{res["y1"]:,}',      "kWh / Year",        colors.HexColor('#1B3A6B'), "Year 1 Yield"),
    ] if not loan else [
        (f'{res["payback"]} Yrs',       "Cash Payback",     GREEN, "Simple"),
        (f'{loan["payback"] or ">25"} Yrs', "Loan Payback", GOLD, "With Loan"),
        (f'{res["irr"]}%',              "Cash IRR",         NAVY3, "25 Year"),
        (inr(loan["emi"]),              "Monthly EMI",      colors.HexColor('#8B5CF6'), "Bank Loan"),
    ]
    kh = 17*mm
    for i, (val, unit, col, sublabel) in enumerate(metrics):
        ky = ry + (3-i) * (kh + 2*mm)
        kpi_card(c, rx, ky, rw, kh, val, unit, sublabel, col, NAVY2)

    # Bottom footer strip
    draw_rect(c, 0, 0, W, 18*mm, fill=NAVY)
    draw_rect(c, 0, 18*mm, W, 1, fill=GOLD)
    now = datetime.datetime.now().strftime("%d %B %Y")
    text(c, f"Report Date: {now}", 15*mm, 7*mm, "Helvetica", 7.5, colors.HexColor('#94A3B8'))
    text(c, "CONFIDENTIAL — For Authorized Recipient Only", W/2, 7*mm,
         "Helvetica-Oblique", 7, colors.HexColor('#64748B'), "center")
    text(c, inp["prepared_by"], W-15*mm, 7*mm, "Helvetica-Bold", 7.5, GOLD, "right")

    c.showPage()

# ═══════════════════════════════════════════════════════════════
# PAGE 2 — EXECUTIVE SUMMARY + SYSTEM PARAMETERS
# ═══════════════════════════════════════════════════════════════
def page_executive(c, res, total_pages):
    inp = res["inp"]
    page_chrome(c, 2, total_pages, "Executive Summary", inp)

    y = H - 28*mm

    # ── KPI ROW 1 (4 cards)
    y = section_bar(c, 15*mm, y, W-30*mm, "KEY PERFORMANCE INDICATORS", "▶", NAVY3)
    y -= 3*mm
    kw, kh, kgap = 40*mm, 22*mm, 2.5*mm
    kpis1 = [
        (inr(res["nc"]),             "Total Net Investment", "After PM Surya Ghar", GOLD),
        (f'{res["y1"]:,} kWh',       "Annual Generation",   "Year 1 Estimate",     GREEN),
        (f'{res["payback"]} Years',   "Payback Period",      "Cash Purchase",       colors.HexColor('#3B82F6')),
        (f'{res["irr"]}%',           "IRR (25 Years)",      "Internal Rate of Ret.",GOLD2),
    ]
    for i,(v,u,l,col) in enumerate(kpis1):
        kpi_card(c, 15*mm + i*(kw+kgap), y-kh, kw, kh, v, u, l, col)
    y -= kh + 4*mm

    kpis2 = [
        (f'Rs.{res["lcoe"]:.2f}/kWh',  "LCOE",             "Levelised Cost Energy", GOLD),
        (inr(res["npv"]),              "Net Present Value",  f'@ {inp["discount_rate"]}% Discount', GREEN),
        (inr(res["profit_25"]),        "Net Profit (25yr)", "Cash Scenario",          colors.HexColor('#8B5CF6')),
        (f'{inp["ghi_kwh_m2_day"]}',   "kWh/m²/day",       "NASA GHI Irradiance",    GOLD2),
    ]
    for i,(v,u,l,col) in enumerate(kpis2):
        kpi_card(c, 15*mm + i*(kw+kgap), y-kh, kw, kh, v, u, l, col)
    y -= kh + 6*mm

    # ── SYSTEM PARAMETERS TABLE
    y = section_bar(c, 15*mm, y, W-30*mm, "SYSTEM & FINANCIAL PARAMETERS", "◆", NAVY3)
    y -= 3*mm

    params = [
        # LEFT column pairs                     RIGHT column pairs
        [("System Capacity",    f'{inp["capacity_kw"]} kWp'),    ("Installation City",   f'{inp["city"]}, {inp["state"]}')],
        [("Install Cost",       f'Rs.{inp["install_cost_per_kw"]:,}/kW'), ("Total Install Cost",  inr_full(res["cost"]))],
        [("PM Surya Ghar Sub.", inr_full(inp["subsidy"])),       ("Net Project Cost",    inr_full(res["nc"]))],
        [("Panel Efficiency",   f'{inp["panel_eff"]}%'),         ("Performance Ratio",   f'{inp["pr"]:.0%}')],
        [("Import Tariff",      f'Rs.{inp["import_tariff"]:.2f}/kWh'), ("Export FiT (NM)",    f'Rs.{inp["export_fit"]:.2f}/kWh')],
        [("Self Consumption",   f'{inp["self_consumption"]:.0%}'),("Tariff Escalation",  f'{inp["tariff_escalation"]:.0%} p.a.')],
        [("Annual O&M (Yr.1)", inr_full(inp["annual_om"])),     ("O&M Escalation",      f'{inp["om_escalation"]:.0%} p.a.')],
        [("Panel Degradation",  f'{inp["degradation"]:.1%} p.a.'), ("Inverter Replacement", f'{inr_full(inp["inverter_replacement"])} @ Yr 12')],
        [("System Life",        f'{inp["system_life"]} Years'),  ("Discount Rate (NPV)", f'{inp["discount_rate"]}%')],
        [("Daily GHI (NASA)",   f'{inp["ghi_kwh_m2_day"]} kWh/m²/day'), ("Annual Yield (Yr.1)", f'{res["y1"]:,} kWh')],
    ]

    col_w = (W-30*mm) / 4
    row_h = 6.5*mm
    for ri, row in enumerate(params):
        bg = LIGHT if ri % 2 == 0 else WHITE
        draw_rect(c, 15*mm, y - row_h, W-30*mm, row_h, fill=bg)
        for ci, (label, val) in enumerate(row):
            base_x = 15*mm + ci * 2 * col_w
            # Label cell
            draw_rect(c, base_x, y-row_h, col_w, row_h, fill=None)
            text(c, label, base_x+2*mm, y-row_h+2*mm, "Helvetica-Bold", 7, SLATE)
            # Value cell
            draw_rect(c, base_x+col_w, y-row_h, col_w, row_h, fill=None)
            text(c, val, base_x+col_w+2*mm, y-row_h+2*mm, "Helvetica", 7.5, NAVY)
        hline(c, 15*mm, y-row_h, W-15*mm, BORDER, 0.3)
        y -= row_h

    # Border around table
    table_top = y + len(params)*row_h
    c.setStrokeColor(BORDER); c.setLineWidth(0.5)
    c.rect(15*mm, y, W-30*mm, len(params)*row_h, fill=0, stroke=1)
    # Vertical dividers
    for cx in [15*mm+col_w, 15*mm+col_w*2, 15*mm+col_w*3]:
        c.line(cx, y, cx, y+len(params)*row_h)

    y -= 6*mm

    # ── BRIEF NARRATIVE
    y = section_bar(c, 15*mm, y, W-30*mm, "PROJECT OVERVIEW", "◈", NAVY3)
    y -= 4*mm
    narrative = (
        f"This report presents a comprehensive financial feasibility analysis for a "
        f"{inp['capacity_kw']} kWp on-grid solar photovoltaic system at {inp['city']}, "
        f"{inp['state']}. Based on NASA POWER irradiance data ({inp['ghi_kwh_m2_day']} kWh/m\u00b2/day), "
        f"the system is estimated to generate {res['y1']:,} kWh in Year 1 with a Performance Ratio of "
        f"{inp['pr']:.0%}. After the PM Surya Ghar Muft Bijli Yojana subsidy of "
        f"{inr_full(inp['subsidy'])}, net project investment stands at {inr_full(res['nc'])}. "
        f"The project achieves payback in {res['payback']} years (cash) with an IRR of {res['irr']}% "
        f"and 25-year net profit of {inr_full(res['profit_25'])}."
    )
    # Word-wrapped text block
    words = narrative.split()
    lines, line = [], ""
    char_limit = 110
    for w in words:
        if len(line) + len(w) + 1 <= char_limit:
            line += (" " if line else "") + w
        else:
            lines.append(line); line = w
    if line: lines.append(line)
    for ln in lines:
        text(c, ln, 15*mm, y, "Helvetica", 7.5, SLATE)
        y -= 5*mm

    c.showPage()

# ═══════════════════════════════════════════════════════════════
# PAGE 3 — SOLAR YIELD & O&M ANALYSIS
# ═══════════════════════════════════════════════════════════════
def page_yield(c, res, total_pages):
    inp  = res["inp"]
    cf   = res["cf"]
    page_chrome(c, 3, total_pages, "Solar Yield & O&M Analysis", inp)

    y = H - 28*mm

    # ── YIELD CHART
    y = section_bar(c, 15*mm, y, W-30*mm, "25-YEAR ANNUAL SOLAR GENERATION FORECAST (kWh)", "☀", NAVY3)
    y -= 3*mm

    years  = [f["year"] for f in cf]
    yields = [f["yield_kwh"] for f in cf]
    yc     = [GOLD if i%2==0 else GOLD2 for i in range(25)]
    draw_bar_chart(c, 15*mm, y-52*mm, W-30*mm, 50*mm, yields, years, yc)
    y -= 56*mm

    # Yield stats strip
    draw_rect(c, 15*mm, y-9*mm, W-30*mm, 9*mm, fill=NAVY2)
    stats = [
        (f'{cf[0]["yield_kwh"]:,} kWh', "Year 1 Generation"),
        (f'{cf[-1]["yield_kwh"]:,} kWh', "Year 25 Generation"),
        (f'{sum(f["yield_kwh"] for f in cf):,} kWh', "25-Year Total Yield"),
        (f'Rs.{res["lcoe"]:.2f}/kWh', "Levelised Cost of Energy"),
    ]
    sw = (W-30*mm) / 4
    for i, (v, l) in enumerate(stats):
        sx = 15*mm + i*sw
        text(c, v, sx+sw/2, y-4*mm, "Helvetica-Bold", 8, GOLD, "center")
        text(c, l, sx+sw/2, y-7.5*mm, "Helvetica", 5.5, colors.HexColor('#94A3B8'), "center")
        if i < 3:
                c.setStrokeColor(GOLD); c.setLineWidth(0.3)
                c.line(sx+sw, y-9*mm, sx+sw, y)
    y -= 12*mm

    # ── CASHFLOW TABLE
    y = section_bar(c, 15*mm, y, W-30*mm, "ANNUAL ENERGY & FINANCIAL PERFORMANCE TABLE", "◆", NAVY3)
    y -= 3*mm

    # Table header
    cols  = ["Yr", "Yield (kWh)", "Tariff Rs/kWh", "Bill Saved", "Export Rev.",
             "O & M Cost", "Net Income", "Cumulative"]
    cws   = [9, 22, 22, 23, 23, 22, 23, 26]  # mm
    ch    = 6*mm

    # Header row
    draw_rect(c, 15*mm, y-ch, W-30*mm, ch, fill=NAVY)
    xc = 15*mm
    for ci, (col, cw) in enumerate(zip(cols, cws)):
        text(c, col, xc+cw*mm/2, y-ch+2*mm, "Helvetica-Bold", 6.5, WHITE, "center")
        if ci < len(cols)-1: vline(c, xc+cw*mm, y-ch, y, colors.HexColor("#1B3A6B"), 0.5)
        xc += cw*mm
    y -= ch

    rh = 5.5*mm
    for fi, f in enumerate(cf):
        bg = colors.HexColor('#FEF3C7') if f["year"] == 12 else (LIGHT if fi%2==0 else WHITE)
        if res.get("payback") and f["year"] == res["payback"]: bg = colors.HexColor('#DCFCE7')
        draw_rect(c, 15*mm, y-rh, W-30*mm, rh, fill=bg)

        vals = [f["year"], f'{f["yield_kwh"]:,}', f'Rs.{f["tariff"]:.2f}',
                inr_full(f["saved"]), inr_full(f["exprev"]),
                inr_full(f["om"]) + (" + " + inr_full(f["extra"]) if f["extra"] else ""),
                inr_full(f["net"]), inr_full(f["cum"])]

        xc = 15*mm
        for ci, (val, cw) in enumerate(zip(vals, cws)):
            col = GREEN if ci == 7 and f["cum"] >= 0 else (RED_IND if ci == 7 and f["cum"] < 0 else NAVY)
            align = "center" if ci == 0 else "right"
            bx = xc if align != "right" else xc+cw*mm-2*mm
            if align == "right":
                text(c, str(val), xc+cw*mm-2*mm, y-rh+1.5*mm, "Helvetica", 6, col, "right")
            else:
                text(c, str(val), xc+cw*mm/2, y-rh+1.5*mm, "Helvetica-Bold", 6.5, NAVY, "center")
            if ci < len(vals)-1: vline(c, xc+cw*mm, y-rh, y, BORDER, 0.2)
            xc += cw*mm

        hline(c, 15*mm, y-rh, W-15*mm, BORDER, 0.2)
        y -= rh

    c.setStrokeColor(BORDER); c.setLineWidth(0.5)
    c.rect(15*mm, y, W-30*mm, len(cf)*rh+ch, fill=0, stroke=1)

    y -= 4*mm
    text(c, "* Yellow = Inverter replacement year (Year 12).   Green row = Cash payback achieved.",
         15*mm, y, "Helvetica-Oblique", 6.5, MUTED)

    c.showPage()

# ═══════════════════════════════════════════════════════════════
# PAGE 4 — BANK LOAN ANALYSIS
# ═══════════════════════════════════════════════════════════════
def page_loan(c, res, total_pages):
    inp  = res["inp"]
    loan = res.get("loan")
    page_chrome(c, 4, total_pages, "Bank Loan Financing Analysis", inp)

    y = H - 28*mm

    if not loan:
        text(c, "Loan financing not enabled.", 15*mm, y-20*mm, "Helvetica", 10, MUTED)
        c.showPage(); return

    # ── LOAN KPIs Row 1
    y = section_bar(c, 15*mm, y, W-30*mm, f"LOAN DETAILS — {inp['bank_name']}", "🏦", NAVY3)
    y -= 3*mm

    kw, kh, kgap = 33*mm, 20*mm, 2*mm
    lkpis1 = [
        (inr_full(loan["down"]),       "Down Payment",      f'{inp["down_payment_pct"]}% Upfront', GOLD),
        (inr_full(loan["lamt"]),       "Loan Principal",    "Amount Financed",    GOLD2),
        (inr_full(loan["emi"]),        "Monthly EMI",       "Rs./Month",          GREEN),
        (f'{inp["interest_rate"]}%',   "Interest Rate",     "Per Annum (Fixed)",  colors.HexColor('#3B82F6')),
        (f'{inp["loan_tenure_yr"]} Yrs',"Loan Tenure",      "Repayment Period",   colors.HexColor('#8B5CF6')),
    ]
    for i,(v,u,l,col) in enumerate(lkpis1):
        kpi_card(c, 15*mm + i*(kw+kgap), y-kh, kw, kh, v, u, l, col)
    y -= kh + 3*mm

    lkpis2 = [
        (inr_full(loan["tot_int"]),    "Total Interest",    "Outgo Over Tenure",  RED_IND),
        (inr_full(loan["tot_paid"]),   "Total Outflow",     "Down + All EMIs",    SLATE),
        (f'{loan["payback"] or ">25"} Yrs',"Loan Payback",  "With Financing",     GREEN),
        (f'{loan["irr"] or "N/A"}%',   "Loan Scenario IRR","25 Year Return",      GOLD),
        (inr_full(loan["profit_25"]),  "Net Profit 25yr",   "Loan Scenario",      colors.HexColor('#8B5CF6')),
    ]
    for i,(v,u,l,col) in enumerate(lkpis2):
        kpi_card(c, 15*mm + i*(kw+kgap), y-kh, kw, kh, v, u, l, col)
    y -= kh + 5*mm

    # ── DUAL LINE CHART
    y = section_bar(c, 15*mm, y, W-30*mm, "CUMULATIVE NET CASHFLOW: CASH vs. LOAN SCENARIO (Rs.)", "◈", NAVY3)
    y -= 4*mm
    years    = [f["year"] for f in res["cf"]]
    cash_cum = [f["cum"] for f in res["cf"]]
    loan_cum = [lc["cum"] for lc in loan["lcf"]]
    draw_line_chart(c, 15*mm, y-58*mm, W-30*mm, 55*mm,
                    [cash_cum, loan_cum], years,
                    [GREEN, GOLD], ["Cash Purchase", "Loan Financing"])
    y -= 63*mm

    # ── COMPARISON TABLE (side by side)
    y = section_bar(c, 15*mm, y, W-30*mm, "CASH PURCHASE vs. LOAN FINANCING — COMPARATIVE SUMMARY", "◆", NAVY3)
    y -= 3*mm

    comp_rows = [
        ("Parameter",               "Cash Purchase",              "Loan Financing"),
        ("Upfront Investment",       inr_full(res["nc"]),          inr_full(loan["down"])),
        ("Loan Amount",              "—",                          inr_full(loan["lamt"])),
        ("Monthly EMI",              "—",                          inr_full(loan["emi"])),
        ("Interest Rate",            "—",                          f'{inp["interest_rate"]}% p.a.'),
        ("Total Interest Outgo",     "—",                          inr_full(loan["tot_int"])),
        ("Total 25yr Outflow",       inr_full(res["nc"]),          inr_full(loan["tot_paid"])),
        ("Payback Period",           f'{res["payback"]} Years',    f'{loan["payback"] or ">25"} Years'),
        ("25-Year Gross Savings",    inr_full(res["gross_25"]),    "—"),
        ("25-Year Net Profit",       inr_full(res["profit_25"]),   inr_full(loan["profit_25"])),
        ("IRR (25 Year)",            f'{res["irr"]}%',             f'{loan["irr"] or "N/A"}%'),
        (f'NPV @ {inp["discount_rate"]}%', inr_full(res["npv"]),  inr_full(loan["npv"])),
    ]

    cw1, cw2, cw3 = 65*mm, 55*mm, 55*mm
    rh = 6.5*mm
    for ri, row in enumerate(comp_rows):
        is_hdr = ri == 0
        bg     = NAVY if is_hdr else (LIGHT if ri % 2 == 0 else WHITE)
        draw_rect(c, 15*mm, y-rh, W-30*mm, rh, fill=bg)
        for ci, (val, cw) in enumerate(zip(row, [cw1, cw2, cw3])):
            xbase = 15*mm + sum([cw1,cw2,cw3][:ci])
            fc    = WHITE if is_hdr else (NAVY if ci == 0 else (GREEN if ci==1 else GOLD))
            fn    = "Helvetica-Bold" if (is_hdr or ci == 0) else "Helvetica"
            text(c, val, xbase+3*mm, y-rh+2*mm, fn, 7.5 if is_hdr else 7, fc)
            if ci < 2: vline(c, xbase+cw, y-rh, y, BORDER, 0.4)
        hline(c, 15*mm, y-rh, W-15*mm, BORDER, 0.3)
        y -= rh

    c.setStrokeColor(BORDER); c.setLineWidth(0.5)
    c.rect(15*mm, y, W-30*mm, len(comp_rows)*rh, fill=0, stroke=1)

    c.showPage()

# ═══════════════════════════════════════════════════════════════
# PAGE 5 — AMORTIZATION + RECOMMENDATIONS
# ═══════════════════════════════════════════════════════════════
def page_amort(c, res, total_pages):
    inp  = res["inp"]
    loan = res.get("loan")
    page_chrome(c, 5, total_pages, "Amortization Schedule & Recommendations", inp)

    y = H - 28*mm

    if not loan:
        text(c, "Loan financing not enabled.", 15*mm, y-20*mm, "Helvetica", 10, MUTED)
        c.showPage(); return

    # ── ANNUAL NET BENEFIT BAR
    y = section_bar(c, 15*mm, y, W-30*mm, "ANNUAL NET BENEFIT — SOLAR SAVINGS MINUS EMI (Rs.)", "◈", NAVY3)
    y -= 3*mm
    years     = [lc["year"] for lc in loan["lcf"]]
    net_ben   = [lc["net"] for lc in loan["lcf"]]
    nb_colors = [GREEN if v >= 0 else RED_IND for v in net_ben]
    draw_bar_chart(c, 15*mm, y-45*mm, W-30*mm, 43*mm, net_ben, years, nb_colors, show_zero=True)
    y -= 50*mm

    # ── AMORTIZATION TABLE (annual)
    y = section_bar(c, 15*mm, y, W-30*mm,
        f"LOAN AMORTIZATION SCHEDULE — {inp['bank_name']} @ {inp['interest_rate']}% for {inp['loan_tenure_yr']} Years", "◆", NAVY3)
    y -= 3*mm

    am_cols = ["Loan Year", "Annual EMI", "Principal Paid", "Interest Paid", "Closing Balance", "Solar Net Income", "Net Benefit"]
    am_cws  = [18, 25, 25, 25, 28, 28, 27]  # mm
    rh = 6.5*mm

    # Header
    draw_rect(c, 15*mm, y-rh, W-30*mm, rh, fill=NAVY)
    xc = 15*mm
    for ci, (col, cw) in enumerate(zip(am_cols, am_cws)):
        text(c, col, xc+cw*mm/2, y-rh+2*mm, "Helvetica-Bold", 6.5, WHITE, "center")
        if ci < len(am_cols)-1: vline(c, xc+cw*mm, y-rh, y, colors.HexColor("#1B3A6B"), 0.5)
        xc += cw*mm
    y -= rh

    for yr in range(1, inp["loan_tenure_yr"]+1):
        slice_ = loan["amort"][(yr-1)*12 : yr*12]
        yr_emi  = sum(m["emi"]  for m in slice_)
        yr_prin = sum(m["prin"] for m in slice_)
        yr_int  = sum(m["int"]  for m in slice_)
        yr_bal  = slice_[-1]["bal"]
        lc      = loan["lcf"][yr-1]
        nb      = lc["net"]
        bg      = LIGHT if yr % 2 == 0 else WHITE

        draw_rect(c, 15*mm, y-rh, W-30*mm, rh, fill=bg)
        vals = [str(yr), inr_full(yr_emi), inr_full(yr_prin),
                inr_full(yr_int), inr_full(yr_bal),
                inr_full(lc["net_income"]), inr_full(nb)]
        xc = 15*mm
        for ci, (val, cw) in enumerate(zip(vals, am_cws)):
            fc = NAVY if ci == 0 else (GREEN if ci == 6 and nb >= 0 else (RED_IND if ci == 6 else SLATE))
            fn = "Helvetica-Bold" if ci == 0 else "Helvetica"
            align = "center" if ci == 0 else "right"
            if align == "right":
                text(c, val, xc+cw*mm-2*mm, y-rh+1.5*mm, fn, 7, fc, "right")
            else:
                text(c, val, xc+cw*mm/2, y-rh+1.5*mm, fn, 7, fc, "center")
            if ci < len(vals)-1: vline(c, xc+cw*mm, y-rh, y, BORDER, 0.25)
            xc += cw*mm
        hline(c, 15*mm, y-rh, W-15*mm, BORDER, 0.25)
        y -= rh

    # Totals row
    draw_rect(c, 15*mm, y-rh, W-30*mm, rh, fill=NAVY2)
    tot_emi  = sum(m["emi"]  for m in loan["amort"])
    tot_prin = sum(m["prin"] for m in loan["amort"])
    tot_int  = loan["tot_int"]
    totals = ["TOTAL", inr_full(tot_emi), inr_full(tot_prin),
              inr_full(tot_int), "—",
              inr_full(sum(lc["net_income"] for lc in loan["lcf"][:inp["loan_tenure_yr"]])),
              inr_full(sum(lc["net"] for lc in loan["lcf"][:inp["loan_tenure_yr"]]))]
    xc = 15*mm
    for ci, (val, cw) in enumerate(zip(totals, am_cws)):
        fc = GOLD if ci == 0 else WHITE
        text(c, val, xc + (cw*mm/2 if ci==0 else cw*mm-2*mm),
             y-rh+2*mm, "Helvetica-Bold", 7, fc,
             "center" if ci==0 else "right")
        if ci < len(totals)-1: vline(c, xc+cw*mm, y-rh, y, colors.HexColor("#1B3A6B"), 0.4)
        xc += cw*mm
    y -= rh

    c.setStrokeColor(BORDER); c.setLineWidth(0.5)
    c.rect(15*mm, y, W-30*mm, (inp["loan_tenure_yr"]+2)*rh, fill=0, stroke=1)
    y -= 6*mm

    # ── RECOMMENDATIONS
    y = section_bar(c, 15*mm, y, W-30*mm, "KEY INSIGHTS & RECOMMENDATIONS", "★", NAVY3)
    y -= 4*mm

    loan_adv  = res["profit_25"] - loan["profit_25"]
    emi_cover = res["cf"][0]["gross"] / 12

    insights = [
        (GREEN,   "Payback Period",
         f"Cash purchase achieves payback in {res['payback']} years, loan scenario in "
         f"{loan['payback'] or '>25'} years — a difference of "
         f"{(loan['payback'] or 25) - (res['payback'] or 0)} years."),
        (GOLD,    "Profitability",
         f"Cash IRR: {res['irr']}% | Loan IRR: {loan['irr'] or 'N/A'}%. "
         f"25-year profit advantage of cash over loan: {inr_full(abs(int(loan_adv)))}."
         if loan_adv > 0 else
         f"Loan leverages smaller upfront capital with competitive IRR of {loan['irr']}%."),
        (colors.HexColor('#3B82F6'), "EMI Serviceability",
         f"Estimated monthly solar savings in Year 1: {inr_full(int(emi_cover))}/month vs. "
         f"EMI of {inr_full(loan['emi'])}/month. "
         f"{'EMI fully covered by solar savings from Day 1.' if emi_cover >= loan['emi'] else 'Partial top-up required during initial loan period.'}"),
        (colors.HexColor('#8B5CF6'), "Interest Cost",
         f"Total interest outgo over {inp['loan_tenure_yr']} years: {inr_full(loan['tot_int'])}. "
         f"Consider part-prepayment after Year 3 if surplus funds available to reduce total interest."),
        (GOLD2,   "Recommendation",
         f"{'If capital availability permits, cash purchase maximises 25-year returns. ' if loan_adv > 0 else ''}"
         f"SBI Surya Ghar scheme at {inp['interest_rate']}% is the most attractive financing option. "
         f"Post-loan period from Year {inp['loan_tenure_yr']+1} onwards, net benefit is entirely clean surplus."),
    ]

    for col, title, body in insights:
        # Bullet color block
        draw_rect(c, 15*mm, y-5*mm, 3, 5*mm, fill=col)
        text(c, title.upper(), 20*mm, y-1*mm, "Helvetica-Bold", 7.5, col)
        y -= 6*mm
        # Wrap body
        words, lines, line = body.split(), [], ""
        for w in words:
            if len(line)+len(w)+1 <= 112: line += (" " if line else "") + w
            else: lines.append(line); line = w
        if line: lines.append(line)
        for ln in lines:
            text(c, ln, 20*mm, y, "Helvetica", 7, SLATE)
            y -= 5*mm
        y -= 2*mm

    # Disclaimer box
    y -= 2*mm
    box_h = 14*mm
    draw_rect(c, 15*mm, y-box_h, W-30*mm, box_h, fill=LIGHT, radius=2)
    c.setStrokeColor(BORDER); c.setLineWidth(0.5)
    c.roundRect(15*mm, y-box_h, W-30*mm, box_h, 2, fill=0, stroke=1)
    draw_rect(c, 15*mm, y-box_h, 2.5, box_h, fill=GOLD)
    disc_text = (
        "DISCLAIMER: This report is prepared for indicative and planning purposes only. "
        "Actual solar yield depends on local weather, shading, soiling, orientation and system losses. "
        "Electricity tariffs, bank interest rates and government subsidies are subject to revision. "
        "Consult a CEIG-certified installer and your bank for final project quotations. "
        "Subsidy subject to MNRE/DISCOM approval and scheme availability."
    )
    words, lines, line = disc_text.split(), [], ""
    for w in words:
        if len(line)+len(w)+1 <= 108: line += (" " if line else "") + w
        else: lines.append(line); line = w
    if line: lines.append(line)
    dy = y - 3*mm
    for ln in lines:
        text(c, ln, 20*mm, dy, "Helvetica-Oblique", 6.5, MUTED)
        dy -= 4.5*mm

    c.showPage()

# ═══════════════════════════════════════════════════════════════
# MAIN BUILDER
# ═══════════════════════════════════════════════════════════════
def build(filename="solar_report_premium.pdf"):
    print("Running simulation...")
    res = simulate(INPUTS)

    print(f"  Net Cost:    {inr_full(res['nc'])}")
    print(f"  Year 1 Gen:  {res['y1']:,} kWh")
    print(f"  Payback:     {res['payback']} years")
    print(f"  IRR:         {res['irr']}%")
    if res.get("loan"):
        print(f"  EMI:         {inr_full(res['loan']['emi'])}/month")
        print(f"  Loan Payback:{res['loan']['payback']} years")

    TOTAL_PAGES = 5
    c = canvas.Canvas(filename, pagesize=A4)
    c.setTitle("SolarYield India — Solar PV Investment Feasibility Report")
    c.setAuthor(INPUTS["prepared_by"])
    c.setSubject("Solar PV Financial Analysis with Bank Loan")

    print("Building PDF...")
    page_cover(c, res)
    page_executive(c, res, TOTAL_PAGES)
    page_yield(c, res, TOTAL_PAGES)
    page_loan(c, res, TOTAL_PAGES)
    page_amort(c, res, TOTAL_PAGES)

    c.save()
    print(f"Saved: {filename}")
    return filename

if __name__ == "__main__":
    build("solar_report_premium.pdf")
