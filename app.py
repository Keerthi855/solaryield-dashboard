"""
SolarYield India — Streamlit Web App
Solar PV Yield & Financial Simulator with Bank Loan Analysis
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import math, datetime, base64
from io import BytesIO

# ── PAGE CONFIG ────────────────────────────────────────────────
st.set_page_config(
    page_title="SolarYield India — Solar PV Calculator",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CUSTOM CSS ─────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Syne:wght@700;800&display=swap');

    :root {
        --navy:   #0D2137;
        --navy2:  #163350;
        --gold:   #C9922A;
        --gold2:  #F0B429;
        --green:  #1A6B3C;
        --red:    #8B1A1A;
    }

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .main-header {
        background: linear-gradient(135deg, #0D2137 0%, #163350 50%, #1B3A6B 100%);
        padding: 2rem 2.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        border-bottom: 3px solid #C9922A;
        position: relative;
        overflow: hidden;
    }
    .main-header::before {
        content: '';
        position: absolute;
        top: -50px; right: -50px;
        width: 200px; height: 200px;
        border-radius: 50%;
        border: 2px solid rgba(201,146,42,0.2);
    }
    .main-header h1 {
        font-family: 'Syne', sans-serif;
        color: #F0B429;
        font-size: 2.2rem;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .main-header p { color: #94A3B8; margin: 0.3rem 0 0 0; font-size: 0.9rem; }

    .kpi-card {
        background: linear-gradient(135deg, #0D2137, #163350);
        border: 1px solid rgba(201,146,42,0.3);
        border-top: 3px solid #C9922A;
        border-radius: 10px;
        padding: 1.2rem;
        text-align: center;
        margin-bottom: 0.8rem;
    }
    .kpi-val  { font-size: 1.6rem; font-weight: 700; color: #F0B429; font-family: 'Syne', sans-serif; }
    .kpi-unit { font-size: 0.7rem; color: #94A3B8; text-transform: uppercase; letter-spacing: 1px; }
    .kpi-label{ font-size: 0.75rem; color: #CBD5E1; margin-top: 0.2rem; font-weight: 500; }

    .kpi-green  { border-top-color: #1A6B3C; }
    .kpi-green .kpi-val { color: #22C55E; }
    .kpi-blue   { border-top-color: #1A5276; }
    .kpi-blue .kpi-val  { color: #60A5FA; }
    .kpi-violet { border-top-color: #6D28D9; }
    .kpi-violet .kpi-val{ color: #A78BFA; }

    .section-header {
        background: linear-gradient(90deg, #0D2137, #163350);
        color: #F0B429;
        padding: 0.6rem 1rem;
        border-radius: 6px;
        border-left: 4px solid #C9922A;
        font-weight: 700;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 1.2rem 0 0.8rem 0;
    }

    .insight-box {
        background: #F8FAFC;
        border-left: 4px solid #C9922A;
        border-radius: 0 8px 8px 0;
        padding: 0.8rem 1rem;
        margin: 0.5rem 0;
    }
    .insight-title { font-weight: 700; color: #0D2137; font-size: 0.8rem; text-transform: uppercase; }
    .insight-body  { color: #334155; font-size: 0.82rem; margin-top: 0.3rem; }

    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #0D2137, #163350);
        border: 1px solid rgba(201,146,42,0.3);
        border-radius: 8px;
        padding: 0.8rem;
    }
    div[data-testid="stMetric"] label { color: #94A3B8 !important; }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] { color: #F0B429 !important; font-weight: 700; }

    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        font-size: 0.85rem;
    }
    .stTabs [data-baseweb="tab-highlight"] { background-color: #C9922A; }

    .disclaimer {
        background: #F8F9FA;
        border: 1px solid #E2E8F0;
        border-left: 4px solid #C9922A;
        border-radius: 4px;
        padding: 0.8rem 1rem;
        font-size: 0.72rem;
        color: #64748B;
        margin-top: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ── CITY DATABASE ──────────────────────────────────────────────
CITIES = {
    "Bengaluru (Karnataka)":    {"ghi": 5.3, "tariff": 6.50, "fit": 3.82, "state": "Karnataka"},
    "Mumbai (Maharashtra)":     {"ghi": 5.0, "tariff": 5.50, "fit": 2.90, "state": "Maharashtra"},
    "Delhi (NCT)":              {"ghi": 5.4, "tariff": 6.00, "fit": 3.00, "state": "Delhi"},
    "Chennai (Tamil Nadu)":     {"ghi": 5.6, "tariff": 4.50, "fit": 3.20, "state": "Tamil Nadu"},
    "Hyderabad (Telangana)":    {"ghi": 5.5, "tariff": 4.20, "fit": 3.50, "state": "Telangana"},
    "Ahmedabad (Gujarat)":      {"ghi": 5.8, "tariff": 4.00, "fit": 2.25, "state": "Gujarat"},
    "Pune (Maharashtra)":       {"ghi": 5.2, "tariff": 5.50, "fit": 2.90, "state": "Maharashtra"},
    "Jaipur (Rajasthan)":       {"ghi": 6.0, "tariff": 5.55, "fit": 3.26, "state": "Rajasthan"},
    "Lucknow (Uttar Pradesh)":  {"ghi": 4.9, "tariff": 5.50, "fit": 2.90, "state": "Uttar Pradesh"},
    "Kolkata (West Bengal)":    {"ghi": 4.5, "tariff": 7.00, "fit": 2.50, "state": "West Bengal"},
    "Bhopal (Madhya Pradesh)":  {"ghi": 5.5, "tariff": 4.53, "fit": 3.14, "state": "Madhya Pradesh"},
    "Chandigarh (Punjab)":      {"ghi": 4.8, "tariff": 4.39, "fit": 2.65, "state": "Punjab"},
    "Kochi (Kerala)":           {"ghi": 4.6, "tariff": 3.45, "fit": 3.15, "state": "Kerala"},
    "Custom Location":          {"ghi": 5.0, "tariff": 5.00, "fit": 3.00, "state": "Custom"},
}

BANKS = {
    "SBI — Surya Ghar (≤3 kW)":   7.00,
    "SBI — Surya Ghar (3–10 kW)":  9.15,
    "SBI — Home Loan Customer":     9.15,
    "SBI — General (Non-HL)":      10.15,
    "Punjab National Bank":         9.50,
    "Bank of Baroda":              10.00,
    "IDBI Bank":                   10.50,
    "Union Bank of India":         10.25,
    "ICICI Bank":                  11.00,
    "HDFC Bank":                   11.50,
    "Custom Rate":                  9.15,
}

# ── SIMULATION ─────────────────────────────────────────────────
def simulate(cap, cost_kw, subsidy, ghi, pr, deg, imp_t, exp_t,
             t_esc, sc, om0, om_esc, inv_rep, life, disc,
             loan_on, down_pct, rate, tenure):

    cost = cap * cost_kw
    nc   = cost - subsidy
    y1   = cap * ghi * 365 * pr

    cf, cum, npv = [], -nc, -nc
    for y in range(1, life+1):
        yld    = y1 * (1-deg)**(y-1)
        tar    = imp_t * (1+t_esc)**(y-1)
        exp    = exp_t * (1+t_esc)**(y-1)
        saved  = yld * sc * tar
        exprev = yld * (1-sc) * exp
        om     = om0 * (1+om_esc)**(y-1)
        extra  = inv_rep if y == 12 else 0
        net    = saved + exprev - om - extra
        cum   += net
        npv   += net / (1+disc/100)**y
        cf.append(dict(Year=y, Yield=round(yld), Tariff=round(tar,2),
            BillSaved=round(saved), ExportRev=round(exprev),
            OM=round(om), Extra=extra, NetIncome=round(net), Cumulative=round(cum)))

    payback = next((r["Year"] for r in cf if r["Cumulative"]>=0), None)

    # IRR
    flows = [-nc] + [r["NetIncome"] for r in cf]
    r_irr = 0.10
    for _ in range(300):
        f  = sum(v/(1+r_irr)**i for i,v in enumerate(flows))
        df = sum(-i*v/(1+r_irr)**(i+1) for i,v in enumerate(flows))
        if abs(df)<1e-12: break
        r_irr -= f/df
        if r_irr<=-1: r_irr=-0.999
    irr = round(r_irr*100, 2) if -1<r_irr<10 else None

    total_om  = sum(r["OM"]+r["Extra"] for r in cf)
    total_yld = sum(r["Yield"] for r in cf)
    lcoe      = round((nc+total_om)/total_yld, 2) if total_yld else 0

    res = dict(cost=round(cost), nc=round(nc), y1=round(y1),
               cf=cf, payback=payback, irr=irr, npv=round(npv),
               lcoe=lcoe, profit25=round(cf[-1]["Cumulative"]),
               gross25=round(cf[-1]["Cumulative"]+nc))

    if loan_on:
        dp   = round(nc * down_pct/100)
        lamt = nc - dp
        rm   = rate/100/12
        nm   = tenure*12
        emi  = lamt*rm*(1+rm)**nm/((1+rm)**nm-1) if rm>0 else lamt/nm
        ann  = emi*12

        amort, bal, tint = [], lamt, 0
        for m in range(1, nm+1):
            i = bal*rm; p = emi-i; bal=max(0,bal-p); tint+=i
            amort.append(dict(Month=m, EMI=round(emi), Principal=round(p),
                              Interest=round(i), Balance=round(bal)))

        lcf, lcum, lnpv = [], -dp, -dp
        for r in cf:
            ec   = ann if r["Year"]<=tenure else 0
            net  = r["NetIncome"]-ec
            lcum += net
            lnpv += net/(1+disc/100)**r["Year"]
            lcf.append(dict(Year=r["Year"], SolarIncome=r["NetIncome"],
                            EMI=round(ec), NetBenefit=round(net), Cumulative=round(lcum)))

        l_pb = next((r["Year"] for r in lcf if r["Cumulative"]>=0), None)
        flows2 = [-dp] + [r["NetBenefit"] for r in lcf]
        r2 = 0.15
        for _ in range(300):
            f  = sum(v/(1+r2)**i for i,v in enumerate(flows2))
            df2 = sum(-i*v/(1+r2)**(i+1) for i,v in enumerate(flows2))
            if abs(df2)<1e-12: break
            r2 -= f/df2
            if r2<=-1: r2=-0.999
        l_irr = round(r2*100,1) if -1<r2<10 else None

        res["loan"] = dict(
            dp=dp, lamt=round(lamt), emi=round(emi), nm=nm,
            ann=round(ann), tint=round(tint), tpaid=round(emi*nm+dp),
            amort=amort, lcf=lcf, payback=l_pb,
            irr=l_irr, npv=round(lnpv),
            profit25=round(lcf[-1]["Cumulative"])
        )
    return res

# ── FORMAT HELPERS ─────────────────────────────────────────────
def inr(v, short=True):
    if v is None: return "N/A"
    neg = v < 0
    av  = abs(int(round(v)))
    if short and av >= 10_000_000: return f"{'−' if neg else ''}Rs.{av/10_000_000:.2f} Cr"
    if short and av >= 100_000:    return f"{'−' if neg else ''}Rs.{av/100_000:.2f} L"
    s = str(av)
    if len(s)>3: s=s[:-3]+","+s[-3:]
    if len(s)>7: s=s[:-7]+","+s[-7:]
    return f"{'−' if neg else ''}Rs.{s}"

def kpi_html(val, unit, label, color=""):
    return f"""<div class="kpi-card {color}">
        <div class="kpi-val">{val}</div>
        <div class="kpi-unit">{unit}</div>
        <div class="kpi-label">{label}</div>
    </div>"""

# ── PDF REPORT GENERATOR ───────────────────────────────────────
def generate_pdf(R, inp_params):
    from reportlab.pdfgen import canvas as rl_canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    import os

    # Register fonts
    font_paths = [
        ('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',        'Sans'),
        ('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',   'Sans-B'),
        ('/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf','Sans-I'),
    ]
    for path, name in font_paths:
        if os.path.exists(path):
            try: pdfmetrics.registerFont(TTFont(name, path))
            except: pass

    W, H   = A4
    NAVY   = colors.HexColor('#0D2137')
    NAVY2  = colors.HexColor('#163350')
    GOLD   = colors.HexColor('#C9922A')
    GOLD2  = colors.HexColor('#F0B429')
    GREEN  = colors.HexColor('#1A6B3C')
    RED    = colors.HexColor('#8B1A1A')
    SLATE  = colors.HexColor('#334155')
    MUTED  = colors.HexColor('#6B7280')
    BORDER = colors.HexColor('#BDC3C7')
    LIGHT  = colors.HexColor('#F4F6F8')
    WHITE  = colors.white
    RS     = 'Rs.'

    def f(v, short=True):
        if v is None: return "N/A"
        neg = v < 0; av = abs(int(round(v)))
        if short and av >= 10_000_000: return f"{'(-) ' if neg else ''}{RS}{av/10_000_000:.2f} Cr"
        if short and av >= 100_000:    return f"{'(-) ' if neg else ''}{RS}{av/100_000:.2f} L"
        s = str(av)
        if len(s)>3: s=s[:-3]+","+s[-3:]
        if len(s)>7: s=s[:-7]+","+s[-7:]
        return f"{'(-) ' if neg else ''}{RS}{s}"

    def ff(v):
        if v is None: return "N/A"
        neg = v < 0; av = abs(int(round(v)))
        s = str(av)
        if len(s)>3: s=s[:-3]+","+s[-3:]
        if len(s)>7: s=s[:-7]+","+s[-7:]
        return f"{'-' if neg else ''}{RS}{s}"

    def t(c, txt, x, y, font='Sans', size=9, color=SLATE, align='left'):
        c.setFont(font, size); c.setFillColor(color)
        if   align=='center': c.drawCentredString(x, y, str(txt))
        elif align=='right':  c.drawRightString(x, y, str(txt))
        else:                 c.drawString(x, y, str(txt))

    def box(c, x, y, w, h, fill=None, stroke=None, lw=0.5):
        if fill:   c.setFillColor(fill)
        if stroke: c.setStrokeColor(stroke); c.setLineWidth(lw)
        c.rect(x, y, w, h, fill=bool(fill), stroke=bool(stroke))

    def hl(c, x1, x2, y, col=BORDER, lw=0.4):
        c.setStrokeColor(col); c.setLineWidth(lw); c.line(x1, y, x2, y)

    def vl(c, x, y1, y2, col=BORDER, lw=0.4):
        c.setStrokeColor(col); c.setLineWidth(lw); c.line(x, y1, x, y2)

    def chrome(c, pg, total, title):
        box(c, 0, H-18*mm, W, 18*mm, fill=NAVY2)
        box(c, 0, H-18*mm, W, 1.2, fill=GOLD)
        box(c, 0, H-18*mm, 38*mm, 18*mm, fill=NAVY)
        t(c, "SolarYield", 3*mm, H-9*mm,  'Sans-B', 10, GOLD2)
        t(c, "INDIA  Pvt. Ltd.", 3*mm, H-14*mm, 'Sans', 7, colors.HexColor('#94A3B8'))
        vl(c, 38*mm, H-18*mm, H, GOLD, 1.5)
        t(c, title.upper(), W/2, H-10*mm, 'Sans-B', 9, GOLD2, 'center')
        t(c, "Solar PV Investment Feasibility Report", W/2, H-15*mm, 'Sans', 6.5, colors.HexColor('#94A3B8'), 'center')
        now = datetime.datetime.now().strftime("%d %b %Y")
        t(c, f"Ref: {inp_params.get('ref','SYI/2025-26')}", W-3*mm, H-9*mm, 'Sans', 7, colors.HexColor('#94A3B8'), 'right')
        t(c, f"Dated: {now}", W-3*mm, H-14*mm, 'Sans', 7, colors.HexColor('#CBD5E1'), 'right')
        box(c, 0, 0, W, 11*mm, fill=NAVY)
        box(c, 0, 11*mm, W, 0.8, fill=GOLD)
        t(c, inp_params.get('client', 'Client'), 5*mm, 4*mm, 'Sans', 6.5, colors.HexColor('#94A3B8'))
        t(c, "STRICTLY CONFIDENTIAL", W/2, 4*mm, 'Sans-I', 6.5, colors.HexColor('#64748B'), 'center')
        t(c, f"Page {pg} of 5", W-5*mm, 4*mm, 'Sans-B', 7, GOLD2, 'right')

    def sec(c, x, y, w, title):
        box(c, x, y-7*mm, w, 7*mm, fill=NAVY)
        box(c, x, y-7*mm, 3, 7*mm, fill=GOLD)
        t(c, title, x+6*mm, y-4.5*mm, 'Sans-B', 8.5, WHITE)
        return y - 9*mm

    def kcard(c, x, y, w, h, val, label, sub, vc=GOLD):
        box(c, x, y, w, h, fill=WHITE, stroke=BORDER, lw=0.5)
        box(c, x, y+h-2, w, 2, fill=vc)
        box(c, x, y, w, 7*mm, fill=NAVY)
        t(c, str(val),  x+w/2, y+h*0.45, 'Sans-B', 11, vc, 'center')
        t(c, str(label),x+w/2, y+h*0.26, 'Sans',  6.5, MUTED, 'center')
        t(c, str(sub),  x+w/2, y+3,      'Sans-B', 6,  GOLD2, 'center')

    buf = BytesIO()
    c   = rl_canvas.Canvas(buf, pagesize=A4)
    c.setTitle("SolarYield India — Solar PV Investment Feasibility Report")
    L   = R.get("loan")
    M   = 12*mm; CW = W-24*mm

    # ── PAGE 1: COVER ──
    box(c, 0, H*0.52, W, H*0.48, fill=NAVY2)
    import math as _m
    c.setStrokeColor(colors.HexColor('#1E3F5A')); c.setLineWidth(0.6)
    for r in [35,60,85,110]: c.arc(W-5*mm-r,H-5*mm-r,W-5*mm+r,H-5*mm+r,180,90)
    c.setStrokeColor(GOLD); c.setLineWidth(2)
    c.arc(W-90*mm,H-90*mm,W+90*mm,H+90*mm,183,84)
    cx,cy = 22*mm, H-30*mm
    c.setFillColor(GOLD); c.circle(cx,cy,12*mm,fill=1,stroke=0)
    c.setFillColor(NAVY2); c.circle(cx,cy,8.5*mm,fill=1,stroke=0)
    c.setFillColor(GOLD); c.circle(cx,cy,5*mm,fill=1,stroke=0)
    c.setStrokeColor(GOLD2); c.setLineWidth(1.3)
    for ang in range(0,360,30):
        rad=_m.radians(ang)
        c.line(cx+13.5*mm*_m.cos(rad),cy+13.5*mm*_m.sin(rad),cx+17*mm*_m.cos(rad),cy+17*mm*_m.sin(rad))
    t(c,"SOLARYIELD INDIA",38*mm,H-23*mm,'Sans-B',16,GOLD2)
    t(c,"PRIVATE LIMITED",38*mm,H-29*mm,'Sans',8.5,colors.HexColor('#94A3B8'))
    box(c,15*mm,H-36*mm,W-30*mm,1.5,fill=GOLD)
    t(c,"SOLAR PHOTOVOLTAIC",15*mm,H-48*mm,'Sans-B',22,WHITE)
    t(c,"INVESTMENT FEASIBILITY REPORT",15*mm,H-60*mm,'Sans-B',20,WHITE)
    t(c,"With Detailed Bank Loan Financing Analysis | As per MNRE Guidelines",15*mm,H-69*mm,'Sans-I',9,colors.HexColor('#8BA7C0'))
    c.setFillColor(GOLD)
    p2=c.beginPath(); p2.moveTo(0,H*0.52); p2.lineTo(W,H*0.52)
    p2.lineTo(W,H*0.52-8); p2.lineTo(0,H*0.52+8); p2.close(); c.drawPath(p2,fill=1,stroke=0)
    box(c,0,0,W,H*0.52,fill=WHITE)
    bx,by=15*mm,H*0.52-10*mm-82*mm; bw,bh=115*mm,82*mm
    box(c,bx,by,bw,bh,fill=WHITE,stroke=BORDER,lw=0.6)
    box(c,bx,by+bh-9*mm,bw,9*mm,fill=NAVY)
    t(c,"PROJECT DETAILS",bx+bw/2,by+bh-6*mm,'Sans-B',8,GOLD2,'center')
    details=[
        ("Client / Applicant",   inp_params.get("client","—")),
        ("Project Location",     f'{inp_params.get("city","—")}, {inp_params.get("state","—")}'),
        ("System Capacity",      f'{inp_params.get("cap",0)} kWp On-Grid Solar PV'),
        ("Gross Project Cost",   ff(R["cost"])),
        ("PM Surya Ghar Subsidy",ff(inp_params.get("subsidy",0))),
        ("Net Investment",       ff(R["nc"])),
        ("Report Reference",     inp_params.get("ref","SYI/2025-26")),
        ("Prepared By",          "SolarYield India Pvt. Ltd."),
        ("Report Date",          datetime.datetime.now().strftime("%d %B %Y")),
    ]
    dy=by+bh-16*mm
    for label,val in details:
        t(c,label+":",bx+4*mm,dy,'Sans',7,MUTED)
        t(c,val,bx+bw-3*mm,dy,'Sans-B',7,NAVY,'right')
        dy-=7*mm; hl(c,bx+3*mm,bx+bw-3*mm,dy+4.5*mm,LIGHT,0.4)
    if L:
        metrics=[(f(R["nc"]),"Net Investment","After Subsidy",NAVY2),
                 (f'{R["payback"]} Yrs',"Cash Payback","Simple",GREEN),
                 (f'{L["payback"]} Yrs',"Loan Payback","With Financing",GOLD),
                 (f'{R["irr"]}%',"IRR 25 Years","Cash Scenario",NAVY2)]
    else:
        metrics=[(f(R["nc"]),"Net Investment","After Subsidy",NAVY2),
                 (f'{R["payback"]} Yrs',"Payback Period","Cash Purchase",GREEN),
                 (f'{R["irr"]}%',"IRR 25 Years","Cash Scenario",GOLD),
                 (f'{R["lcoe"]:.2f}','LCOE Rs./kWh','Levelised Cost',NAVY2)]
    kw,kh=62*mm,18*mm; rx=140*mm; ry=by+bh-9*mm-4*(kh+2*mm)+2*mm
    for i,(v,l,s,col) in enumerate(metrics): kcard(c,rx,ry+i*(kh+2*mm),kw,kh,v,l,s,col)
    box(c,0,0,W,16*mm,fill=NAVY); box(c,0,16*mm,W,1.2,fill=GOLD)
    t(c,f'Report No.: {inp_params.get("ref","SYI/2025-26")}',15*mm,10*mm,'Sans-B',7.5,GOLD2)
    t(c,"CONFIDENTIAL",W-15*mm,10*mm,'Sans-B',7.5,GOLD,'right')
    t(c,"This document contains proprietary financial analysis. Unauthorised reproduction is prohibited.",W/2,4*mm,'Sans-I',6,colors.HexColor('#4B6278'),'center')
    c.showPage()

    # ── PAGE 2: EXECUTIVE SUMMARY ──
    chrome(c,2,5,"Executive Summary")
    y=H-22*mm
    y=sec(c,M,y,CW,"KEY PERFORMANCE INDICATORS")
    kw=(CW-3*mm)/4; kh=20*mm
    kpis=[(f(R["nc"]),"Net Investment","After PM Subsidy",NAVY2),
          (f'{R["y1"]:,} kWh',"Year 1 Yield","Annual Generation",GREEN),
          (f'{R["payback"]} Years',"Payback Period","Cash Purchase",colors.HexColor('#1A5276')),
          (f'{R["irr"]}%',"IRR 25 Years","Internal Rate of Return",GOLD)]
    for i,(v,l,s,col) in enumerate(kpis): kcard(c,M+i*(kw+1*mm),y-kh,kw,kh,v,l,s,col)
    y-=kh+3*mm
    kpis2=[(f'Rs.{R["lcoe"]:.2f}/kWh',"LCOE","Levelised Cost",GOLD),
           (f(R["npv"]),"Net Present Value",f'@ {inp_params.get("disc",8)}% Disc.',GREEN),
           (f(R["profit25"]),"Net Profit 25yr","Cash Scenario",colors.HexColor('#1A5276')),
           (f'{inp_params.get("ghi",5.3)} kWh/m\u00b2',"Daily GHI","NASA Data",NAVY2)]
    for i,(v,l,s,col) in enumerate(kpis2): kcard(c,M+i*(kw+1*mm),y-kh,kw,kh,v,l,s,col)
    y-=kh+4*mm
    if L:
        y=sec(c,M,y,CW,"LOAN SCENARIO — KEY METRICS")
        lkpis=[(ff(L["dp"]),"Down Payment",f'{inp_params.get("down_pct",20)}% Upfront',NAVY2),
               (ff(L["emi"]),"Monthly EMI","Rs./Month",GOLD),
               (f'{L["payback"]} Years',"Loan Payback","With Financing",GREEN),
               (f'{L["irr"]}%' if L["irr"] else "N/A","Loan IRR","25 Year Return",colors.HexColor('#1A5276'))]
        for i,(v,l,s,col) in enumerate(lkpis): kcard(c,M+i*(kw+1*mm),y-kh,kw,kh,v,l,s,col)
        y-=kh+4*mm
    y=sec(c,M,y,CW,"SYSTEM & PROJECT PARAMETERS")
    params=[
        [("System Capacity",f'{inp_params.get("cap",10)} kWp'),("City / State",f'{inp_params.get("city","")}, {inp_params.get("state","")}')],
        [("Install Cost",f'Rs.{inp_params.get("cost_kw",45000):,}/kW'),("Gross Project Cost",ff(R["cost"]))],
        [("PM Subsidy",ff(inp_params.get("subsidy",0))),("Net Project Cost",ff(R["nc"]))],
        [("Import Tariff",f'Rs.{inp_params.get("imp_t",6.5):.2f}/kWh'),("Export FiT",f'Rs.{inp_params.get("exp_t",3.82):.2f}/kWh')],
        [("Self Consumption",f'{inp_params.get("sc",0.75):.0%}'),("Performance Ratio",f'{inp_params.get("pr",0.8):.0%}')],
        [("Annual O&M Yr1",ff(inp_params.get("om0",5000))),("O&M Escalation",f'{inp_params.get("om_esc",0.04):.0%}/yr')],
        [("Panel Degradation",f'{inp_params.get("deg",0.005):.1%}/yr'),("Inverter Replace.",f'{ff(inp_params.get("inv_rep",40000))} @Yr12')],
        [("System Life","25 Years"),("Discount Rate",f'{inp_params.get("disc",8)}%')],
    ]
    col_w=CW/4; rh=6.5*mm
    for ri,row in enumerate(params):
        bg=LIGHT if ri%2==0 else WHITE
        box(c,M,y-rh,CW,rh,fill=bg)
        for ci,(lbl,val) in enumerate(row):
            bx=M+ci*2*col_w
            t(c,lbl,bx+2*mm,y-rh+2*mm,'Sans-B',7,SLATE)
            t(c,val,bx+col_w+2*mm,y-rh+2*mm,'Sans',7.5,NAVY)
            if ci==0: vl(c,bx+col_w,y-rh,y,BORDER,0.4)
        vl(c,M+2*col_w,y-rh,y,BORDER,0.8); hl(c,M,M+CW,y-rh,BORDER,0.3); y-=rh
    box(c,M,y,CW,len(params)*rh,fill=None,stroke=BORDER,lw=0.6)
    c.showPage()

    # ── PAGE 3: YIELD TABLE ──
    chrome(c,3,5,"Solar Yield & O&M Analysis")
    cf=R["cf"]; y=H-22*mm
    y=sec(c,M,y,CW,"25-YEAR ANNUAL ENERGY & FINANCIAL PERFORMANCE TABLE")
    cols=["Yr","Yield (kWh)","Tariff Rs/kWh","Bill Saved","Export Rev.","O & M","Net Income","Cumulative"]
    cws=[9,22,22,23,22,22,24,26]
    rh=5.8*mm
    box(c,M,y-rh,CW,rh,fill=NAVY)
    xc=M
    for ci,(col,cw) in enumerate(zip(cols,cws)):
        t(c,col,xc+cw*mm/2,y-rh*0.55,'Sans-B',6.5,GOLD2,'center')
        if ci<len(cols)-1: vl(c,xc+cw*mm,y-rh,y,colors.HexColor('#1E3F5A'),0.5)
        xc+=cw*mm
    y-=rh
    for fi,row in enumerate(cf):
        is_inv=row["Year"]==12; is_pb=row["Year"]==R.get("payback")
        if is_inv: bg=colors.HexColor('#FEF9C3')
        elif is_pb: bg=colors.HexColor('#D1FAE5')
        else: bg=LIGHT if fi%2==0 else WHITE
        box(c,M,y-rh,CW,rh,fill=bg)
        om_s=ff(row["OM"])+(f'+{ff(row["Extra"])}' if row["Extra"] else "")
        vals=[(str(row["Year"]),'center'),(f'{row["Yield"]:,}','right'),
              (f'Rs.{row["Tariff"]:.2f}','right'),(ff(row["BillSaved"]),'right'),
              (ff(row["ExportRev"]),'right'),(om_s,'right'),
              (ff(row["NetIncome"]),'right'),(ff(row["Cumulative"]),'right')]
        xc=M
        for ci,((val,align),cw) in enumerate(zip(vals,cws)):
            fc=NAVY if ci==0 else (GREEN if ci==7 and row["Cumulative"]>=0 else (RED if ci==7 else SLATE))
            fn='Sans-B' if ci in(0,7) else 'Sans'
            px=xc+cw*mm/2 if align=='center' else xc+cw*mm-1.5*mm
            t(c,val,px,y-rh+1.8*mm,fn,6,fc,align)
            if ci<len(vals)-1: vl(c,xc+cw*mm,y-rh,y,BORDER,0.25)
            xc+=cw*mm
        hl(c,M,M+CW,y-rh,BORDER,0.25); y-=rh
    box(c,M,y,CW,len(cf)*rh+rh,fill=None,stroke=BORDER,lw=0.6)
    y-=4*mm
    t(c,f"Note: Yellow=Inverter replacement (Yr12). Green=Cash payback Yr{R.get('payback','?')}. Cumulative is net of all costs from Year 0.",M,y,'Sans-I',6,MUTED)
    c.showPage()

    # ── PAGE 4: LOAN ANALYSIS ──
    chrome(c,4,5,"Bank Loan Financing Analysis")
    y=H-22*mm
    if L:
        y=sec(c,M,y,CW,f"LOAN DETAILS — {inp_params.get('bank','SBI')} @ {inp_params.get('rate',9.15)}% p.a.")
        kw=(CW-4*mm)/5; kh=19*mm
        l1=[(ff(L["dp"]),"Down Payment",f'{inp_params.get("down_pct",20)}% of Cost',NAVY2),
            (ff(L["lamt"]),"Loan Principal","Amount Financed",GOLD),
            (ff(L["emi"]),"Monthly EMI","Rs./Month",GREEN),
            (f'{inp_params.get("rate",9.15)}%',"Interest Rate","Per Annum",colors.HexColor('#1A5276')),
            (f'{inp_params.get("tenure",7)} Yr',"Loan Tenure","Repayment",NAVY2)]
        for i,(v,l,s,col) in enumerate(l1): kcard(c,M+i*(kw+1*mm),y-kh,kw,kh,v,l,s,col)
        y-=kh+3*mm
        l2=[(f(L["tint"]),"Total Interest","Over Tenure",RED),
            (f(L["tpaid"]),"Total Outflow","Down + EMIs",SLATE),
            (f'{L["payback"]} Yrs',"Loan Payback","With Financing",GREEN),
            (f'{L["irr"]}%' if L["irr"] else "N/A","Loan IRR","25 Year",GOLD),
            (f(L["profit25"]),"Net Profit 25yr","Loan Scenario",colors.HexColor('#1A5276'))]
        for i,(v,l,s,col) in enumerate(l2): kcard(c,M+i*(kw+1*mm),y-kh,kw,kh,v,l,s,col)
        y-=kh+5*mm
        y=sec(c,M,y,CW,"CASH vs. LOAN — COMPARATIVE SUMMARY")
        comp=[("Parameter","Cash Purchase","Loan Financing"),
              ("Upfront Investment",ff(R["nc"]),ff(L["dp"])),
              ("Loan Amount","—",ff(L["lamt"])),("Monthly EMI","—",ff(L["emi"])),
              ("Interest Rate","—",f'{inp_params.get("rate",9.15)}% p.a.'),
              ("Total Interest","—",ff(L["tint"])),("Total Outflow",ff(R["nc"]),ff(L["tpaid"])),
              ("Payback Period",f'{R["payback"]} Years',f'{L["payback"]} Years'),
              ("25yr Net Profit",ff(R["profit25"]),ff(L["profit25"])),
              ("IRR 25 Years",f'{R["irr"]}%',f'{L["irr"]}%' if L["irr"] else "N/A"),
              (f'NPV @ {inp_params.get("disc",8)}%',ff(R["npv"]),ff(L["npv"]))]
        c1w,c2w,c3w=62*mm,54*mm,54*mm; rh=6.5*mm
        for ri,row in enumerate(comp):
            is_hdr=ri==0; bg=NAVY if is_hdr else (LIGHT if ri%2==0 else WHITE)
            box(c,M,y-rh,CW,rh,fill=bg)
            t(c,row[0],M+3*mm,y-rh+2.2*mm,'Sans-B',7.5 if is_hdr else 7,GOLD2 if is_hdr else SLATE)
            vl(c,M+c1w,y-rh,y,BORDER,0.5)
            t(c,row[1],M+c1w+3*mm,y-rh+2.2*mm,'Sans-B' if is_hdr else 'Sans',7.5 if is_hdr else 7,GOLD2 if is_hdr else GREEN)
            vl(c,M+c1w+c2w,y-rh,y,BORDER,0.5)
            t(c,row[2],M+c1w+c2w+3*mm,y-rh+2.2*mm,'Sans-B' if is_hdr else 'Sans',7.5 if is_hdr else 7,GOLD2 if is_hdr else GOLD)
            hl(c,M,M+CW,y-rh,BORDER,0.3); y-=rh
        box(c,M,y,CW,len(comp)*rh,fill=None,stroke=BORDER,lw=0.6)
    else:
        t(c,"Loan financing not enabled for this report.",M,y-20*mm,'Sans',10,MUTED)
    c.showPage()

    # ── PAGE 5: AMORTIZATION & RECOMMENDATIONS ──
    chrome(c,5,5,"Amortization Schedule & Recommendations")
    y=H-22*mm
    if L:
        y=sec(c,M,y,CW,f"LOAN AMORTIZATION — {inp_params.get('bank','SBI')} @ {inp_params.get('rate',9.15)}% | {inp_params.get('tenure',7)} Years")
        cols=["Loan\nYear","Annual\nEMI","Principal\nRepaid","Interest\nPaid","Closing\nBalance","Solar Net\nIncome","Net\nBenefit"]
        cws=[14,24,24,24,28,28,24]; rh=6.5*mm
        box(c,M,y-rh,CW,rh,fill=NAVY)
        xc=M
        for ci,(col,cw) in enumerate(zip(cols,cws)):
            lines2=col.split('\n')
            if len(lines2)==2:
                t(c,lines2[0],xc+cw*mm/2,y-rh*0.35,'Sans-B',6.5,GOLD2,'center')
                t(c,lines2[1],xc+cw*mm/2,y-rh*0.72,'Sans-B',6.5,GOLD2,'center')
            else: t(c,col,xc+cw*mm/2,y-rh*0.55,'Sans-B',6.5,GOLD2,'center')
            if ci<len(cols)-1: vl(c,xc+cw*mm,y-rh,y,colors.HexColor('#1E3F5A'),0.5)
            xc+=cw*mm
        y-=rh
        tenure=inp_params.get("tenure",7)
        t_emi2=t_pri2=t_int2=t_sol2=t_nb2=0
        for yr in range(1,tenure+1):
            sl=L["amort"][(yr-1)*12:yr*12]
            y_emi=sum(m["EMI"] for m in sl); y_pri=sum(m["Principal"] for m in sl)
            y_int=sum(m["Interest"] for m in sl); y_bal=sl[-1]["Balance"]
            lc=L["lcf"][yr-1]; nb=lc["NetBenefit"]
            t_emi2+=y_emi; t_pri2+=y_pri; t_int2+=y_int; t_sol2+=lc["SolarIncome"]; t_nb2+=nb
            bg=LIGHT if yr%2==0 else WHITE; box(c,M,y-rh,CW,rh,fill=bg)
            vals2=[(str(yr),'center'),(ff(y_emi),'right'),(ff(y_pri),'right'),
                   (ff(y_int),'right'),(ff(y_bal),'right'),(ff(lc["SolarIncome"]),'right'),(ff(nb),'right')]
            xc=M
            for ci,((val,align),cw) in enumerate(zip(vals2,cws)):
                fc=NAVY if ci==0 else (GREEN if ci==6 and nb>=0 else (RED if ci==6 else SLATE))
                fn='Sans-B' if ci==0 else 'Sans'
                px=xc+cw*mm/2 if align=='center' else xc+cw*mm-1.5*mm
                t(c,val,px,y-rh+2*mm,fn,7,fc,align)
                if ci<len(vals2)-1: vl(c,xc+cw*mm,y-rh,y,BORDER,0.3)
                xc+=cw*mm
            hl(c,M,M+CW,y-rh,BORDER,0.3); y-=rh
        box(c,M,y-rh,CW,rh,fill=NAVY2)
        tots=[("TOTAL",'center'),(ff(t_emi2),'right'),(ff(t_pri2),'right'),(ff(t_int2),'right'),
              ("—",'center'),(ff(t_sol2),'right'),(ff(t_nb2),'right')]
        xc=M
        for ci,((val,align),cw) in enumerate(zip(tots,cws)):
            fc=GOLD2 if ci==0 else WHITE; px=xc+cw*mm/2 if align=='center' else xc+cw*mm-1.5*mm
            t(c,val,px,y-rh+2*mm,'Sans-B',7,fc,align)
            if ci<len(tots)-1: vl(c,xc+cw*mm,y-rh,y,colors.HexColor('#1E3F5A'),0.4); xc+=cw*mm
        y-=rh; box(c,M,y,CW,(tenure+2)*rh,fill=None,stroke=BORDER,lw=0.6); y-=6*mm

        y=sec(c,M,y,CW,"KEY FINANCIAL INSIGHTS & RECOMMENDATIONS")
        emi_cov=R["cf"][0]["NetIncome"]/12; diff=R["profit25"]-L["profit25"]
        insights2=[
            (GREEN,"PAYBACK PERIOD",f"Cash: {R['payback']} yrs. Loan: {L['payback']} yrs. Lower upfront {ff(L['dp'])} vs {ff(R['nc'])}."),
            (GOLD,"PROFITABILITY",f"Cash IRR {R['irr']}% vs Loan IRR {L['irr']}%. 25yr profit diff: {f(abs(int(diff)))} in favour of {'cash' if diff>0 else 'loan'}."),
            (colors.HexColor('#1A5276'),"EMI SERVICEABILITY",f"Monthly solar income Yr1 ~{ff(int(emi_cov))} vs EMI {ff(L['emi'])}. {'Fully covered from Day 1.' if emi_cov>=L['emi'] else 'Partial top-up needed early years.'}"),
            (RED,"INTEREST OPTIMISATION",f"Total interest {f(L['tint'])} over {tenure} yrs. Prepayment after Yr3 recommended to reduce outgo."),
            (NAVY2,"RECOMMENDATION",f"SBI Surya Ghar @ {inp_params.get('rate',9.15)}% is most cost-effective. From Yr{tenure+1} all solar income is net surplus."),
        ]
        for col2,title2,body2 in insights2:
            if y<40*mm: break
            box(c,M,y-5.5*mm,3,5.5*mm,fill=col2)
            t(c,title2,M+5*mm,y-1.2*mm,'Sans-B',7.5,col2); y-=6.5*mm
            words2=body2.split(); lbuf2,ls2=[],""
            for w2 in words2:
                if len(lbuf2)+len(w2)+1<=112: lbuf2+=(" " if lbuf2 else "")+w2
                else: ls2.append(lbuf2); lbuf2=w2
            if lbuf2: ls2.append(lbuf2)
            for ln2 in ls2:
                if y<36*mm: break
                t(c,ln2,M+5*mm,y,'Sans',7.2,SLATE); y-=4.8*mm
            y-=2*mm

    # Disclaimer
    if y>26*mm:
        bh2=min(y-15*mm,14*mm); box(c,M,14*mm,CW,bh2,fill=LIGHT,stroke=BORDER,lw=0.5)
        box(c,M,14*mm,3,bh2,fill=GOLD)
        disc2="DISCLAIMER: For indicative purposes only. Actual yield depends on local conditions. Tariffs and subsidies subject to revision. Consult CEIG-certified installer and bank before final commitment."
        words3=disc2.split(); lbuf3,ls3=[],""
        for w3 in words3:
            if len(lbuf3)+len(w3)+1<=108: lbuf3+=(" " if lbuf3 else "")+w3
            else: ls3.append(lbuf3); lbuf3=w3
        if lbuf3: ls3.append(lbuf3)
        dy2=14*mm+bh2-5*mm; t(c,"DISCLAIMER",M+5*mm,dy2,'Sans-B',7,GOLD); dy2-=5*mm
        for ln3 in ls3:
            if dy2<15*mm: break
            t(c,ln3,M+5*mm,dy2,'Sans-I',6.5,MUTED); dy2-=4.5*mm

    c.save()
    buf.seek(0)
    return buf.read()


# ── MAIN APP ───────────────────────────────────────────────────
def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>☀ SolarYield India</h1>
        <p>Solar PV Investment Feasibility Simulator · Bank Loan Analysis · PM Surya Ghar</p>
    </div>
    """, unsafe_allow_html=True)

    # ── SIDEBAR ──────────────────────────────────────────────
    with st.sidebar:
        st.markdown("### 📍 Location")
        city_sel = st.selectbox("City / State", list(CITIES.keys()), index=0)
        city     = CITIES[city_sel]

        if city_sel == "Custom Location":
            ghi     = st.number_input("Daily GHI (kWh/m²/day)", 3.0, 8.0, 5.0, 0.1)
            imp_t   = st.number_input("Import Tariff (Rs./kWh)", 2.0, 15.0, 5.0, 0.1)
            exp_t   = st.number_input("Export FiT (Rs./kWh)",   1.0, 8.0,  3.0, 0.1)
        else:
            ghi   = city["ghi"]
            imp_t = city["tariff"]
            exp_t = city["fit"]
            st.info(f"🌞 GHI: {ghi} kWh/m²/day\n\n💡 Import: Rs.{imp_t}/kWh\n\n⚡ Export FiT: Rs.{exp_t}/kWh")

        st.markdown("### ⚙️ System")
        cap      = st.number_input("System Capacity (kWp)", 0.5, 500.0, 10.0, 0.5)
        cost_kw  = st.number_input("Install Cost (Rs./kWp)", 30000, 80000, 45000, 1000)
        subsidy  = st.number_input("PM Surya Ghar Subsidy (Rs.)", 0, 500000, 94500, 500)
        pr       = st.slider("Performance Ratio (%)", 60, 95, 80) / 100
        deg      = st.slider("Panel Degradation (%/yr)", 0.1, 1.0, 0.5) / 100

        st.markdown("### 💰 Financial")
        t_esc    = st.slider("Tariff Escalation (%/yr)", 0, 8, 3) / 100
        sc       = st.slider("Self Consumption (%)", 50, 100, 75) / 100
        om0      = st.number_input("Annual O&M — Year 1 (Rs.)", 1000, 50000, 5000, 500)
        om_esc   = st.slider("O&M Escalation (%/yr)", 0, 8, 4) / 100
        inv_rep  = st.number_input("Inverter Replacement (Rs.)", 0, 100000, 40000, 5000)
        disc     = st.slider("Discount Rate for NPV (%)", 4, 15, 8)

        st.markdown("### 🏦 Bank Loan")
        loan_on  = st.toggle("Enable Loan Financing", value=True)
        if loan_on:
            bank_sel = st.selectbox("Bank / Scheme", list(BANKS.keys()), index=1)
            rate     = st.number_input("Interest Rate (% p.a.)", 5.0, 20.0,
                                       BANKS[bank_sel], 0.05)
            tenure   = st.slider("Loan Tenure (Years)", 1, 15, 7)
            down_pct = st.slider("Down Payment (%)", 5, 80, 20)

            # Live EMI preview
            nc_preview = cap*cost_kw - subsidy
            dp_prev    = round(nc_preview * down_pct/100)
            lamt_prev  = nc_preview - dp_prev
            rm         = rate/100/12
            nm         = tenure*12
            emi_prev   = lamt_prev*rm*(1+rm)**nm/((1+rm)**nm-1) if rm>0 else lamt_prev/nm
            st.success(f"**EMI Preview**\n\nDown: {inr(dp_prev)}\nLoan: {inr(lamt_prev)}\n**EMI: {inr(emi_prev)}/month**")
        else:
            rate=9.15; tenure=7; down_pct=20

        calc_btn = st.button("⚡ Calculate Yield & ROI", type="primary", use_container_width=True)

    # ── CALCULATE ────────────────────────────────────────────
    if calc_btn or "results" not in st.session_state:
        with st.spinner("Running simulation..."):
            R = simulate(cap, cost_kw, subsidy, ghi, pr, deg,
                        imp_t, exp_t, t_esc, sc, om0, om_esc,
                        inv_rep, 25, disc, loan_on,
                        down_pct, rate, tenure)
            st.session_state["results"] = R
            st.session_state["loan_on"] = loan_on

    R = st.session_state["results"]
    L = R.get("loan")

    # ── TABS ─────────────────────────────────────────────────
    tabs = st.tabs(["📊 Overview", "📈 Cashflow Table", "🏦 Loan Analysis", "📉 Charts", "📋 Amortization", "📄 Download Report"])

    # ══ TAB 1 — OVERVIEW ══════════════════════════════════════
    with tabs[0]:
        st.markdown('<div class="section-header">CASH PURCHASE — KEY PERFORMANCE INDICATORS</div>', unsafe_allow_html=True)
        c1,c2,c3,c4 = st.columns(4)
        with c1: st.markdown(kpi_html(inr(R["nc"]), "Net Investment", "After PM Subsidy"), unsafe_allow_html=True)
        with c2: st.markdown(kpi_html(f'{R["y1"]:,} kWh', "Year 1 Yield", "Annual Generation", "kpi-green"), unsafe_allow_html=True)
        with c3: st.markdown(kpi_html(f'{R["payback"]} Years', "Payback Period", "Cash Purchase", "kpi-blue"), unsafe_allow_html=True)
        with c4: st.markdown(kpi_html(f'{R["irr"]}%', "IRR — 25 Years", "Internal Rate of Return", "kpi-violet"), unsafe_allow_html=True)

        c5,c6,c7,c8 = st.columns(4)
        with c5: st.markdown(kpi_html(f'Rs.{R["lcoe"]:.2f}/kWh', "LCOE", "Levelised Cost of Energy"), unsafe_allow_html=True)
        with c6: st.markdown(kpi_html(inr(R["npv"]), "Net Present Value", f'@ {disc}% Discount Rate', "kpi-green"), unsafe_allow_html=True)
        with c7: st.markdown(kpi_html(inr(R["profit25"]), "Net Profit — 25yr", "Cash Scenario", "kpi-violet"), unsafe_allow_html=True)
        with c8: st.markdown(kpi_html(f'{ghi} kWh/m²', "Daily GHI", "NASA Irradiance Data", "kpi-blue"), unsafe_allow_html=True)

        if L:
            st.markdown('<div class="section-header">BANK LOAN SCENARIO — KEY METRICS</div>', unsafe_allow_html=True)
            l1,l2,l3,l4 = st.columns(4)
            with l1: st.markdown(kpi_html(inr(L["dp"]), "Down Payment", f'{down_pct}% Upfront'), unsafe_allow_html=True)
            with l2: st.markdown(kpi_html(inr(L["emi"]), "Monthly EMI", "Rs./Month", "kpi-green"), unsafe_allow_html=True)
            with l3: st.markdown(kpi_html(f'{L["payback"]} Years', "Loan Payback", "With Financing", "kpi-blue"), unsafe_allow_html=True)
            with l4: st.markdown(kpi_html(f'{L["irr"]}%' if L["irr"] else "N/A", "Loan IRR", "25-Year Return", "kpi-violet"), unsafe_allow_html=True)

        st.markdown('<div class="section-header">SYSTEM PARAMETERS</div>', unsafe_allow_html=True)
        params_df = pd.DataFrame([
            ["System Capacity",    f"{cap} kWp",              "City / State",       city_sel.split("(")[0].strip()],
            ["Install Cost",       f"Rs.{cost_kw:,}/kW",       "Gross Project Cost",  inr(R["cost"])],
            ["PM Surya Ghar Sub.", inr(subsidy),               "Net Investment",      inr(R["nc"])],
            ["Import Tariff",      f"Rs.{imp_t:.2f}/kWh",      "Export FiT (NM)",     f"Rs.{exp_t:.2f}/kWh"],
            ["Performance Ratio",  f"{pr:.0%}",                "Panel Degradation",   f"{deg:.1%}/yr"],
            ["Self Consumption",   f"{sc:.0%}",                "Tariff Escalation",   f"{t_esc:.0%}/yr"],
            ["Annual O&M (Yr 1)", inr(om0, False),            "O&M Escalation",       f"{om_esc:.0%}/yr"],
            ["Inverter Replace.",  inr(inv_rep, False)+" @Yr12","System Life",         "25 Years"],
        ], columns=["Parameter", "Value", "Parameter ", "Value "])
        st.dataframe(params_df, use_container_width=True, hide_index=True)

    # ══ TAB 2 — CASHFLOW TABLE ════════════════════════════════
    with tabs[1]:
        st.markdown('<div class="section-header">25-YEAR ENERGY & FINANCIAL PERFORMANCE</div>', unsafe_allow_html=True)

        df = pd.DataFrame(R["cf"])
        df["O&M + Extra"] = df.apply(
            lambda r: f'{inr(r["OM"],False)}' + (f' + {inr(r["Extra"],False)}' if r["Extra"] else ''), axis=1)
        df["Bill Saved"]   = df["BillSaved"].apply(lambda v: inr(v, False))
        df["Export Rev."]  = df["ExportRev"].apply(lambda v: inr(v, False))
        df["Net Income"]   = df["NetIncome"].apply(lambda v: inr(v, False))
        df["Cumulative"]   = df["Cumulative"].apply(lambda v: inr(v, False))
        df["Tariff Rs/kWh"]= df["Tariff"].apply(lambda v: f"Rs.{v:.2f}")

        display_df = df[["Year","Yield","Tariff Rs/kWh","Bill Saved","Export Rev.","O&M + Extra","Net Income","Cumulative"]].copy()
        display_df.columns = ["Year","Yield (kWh)","Tariff","Bill Saved","Export Rev.","O&M Cost","Net Income","Cumulative"]

        def highlight_rows(row):
            styles = [''] * len(row)
            if row["Year"] == 12:
                styles = ['background-color: #FEF3C7'] * len(row)
            elif R["payback"] and row["Year"] == R["payback"]:
                styles = ['background-color: #D1FAE5'] * len(row)
            return styles

        st.dataframe(
            display_df.style.apply(highlight_rows, axis=1),
            use_container_width=True, hide_index=True, height=600
        )
        st.caption("🟡 Yellow = Inverter replacement year (Year 12)   🟢 Green = Cash payback achieved")

        # Download button
        csv = display_df.to_csv(index=False)
        st.download_button("⬇ Download Table as CSV", csv,
                          "solaryield_cashflow.csv", "text/csv")

    # ══ TAB 3 — LOAN ANALYSIS ════════════════════════════════
    with tabs[2]:
        if not L:
            st.info("Enable Bank Loan Financing in the sidebar to see loan analysis.")
        else:
            st.markdown('<div class="section-header">LOAN vs CASH — COMPARISON</div>', unsafe_allow_html=True)
            comp = pd.DataFrame([
                ["Upfront Investment",   inr(R["nc"]),          inr(L["dp"])],
                ["Loan Amount",          "—",                   inr(L["lamt"])],
                ["Monthly EMI",          "—",                   inr(L["emi"])],
                ["Interest Rate",        "—",                   f'{rate}% p.a.'],
                ["Loan Tenure",          "—",                   f'{tenure} Years'],
                ["Total Interest Outgo", "—",                   inr(L["tint"])],
                ["Total Outflow",        inr(R["nc"]),          inr(L["tpaid"])],
                ["Payback Period",       f'{R["payback"]} Yrs', f'{L["payback"]} Yrs'],
                ["25-yr Gross Savings",  inr(R["gross25"]),     "—"],
                ["25-yr Net Profit",     inr(R["profit25"]),    inr(L["profit25"])],
                ["IRR (25 Years)",       f'{R["irr"]}%',        f'{L["irr"]}%' if L["irr"] else "N/A"],
                [f'NPV @ {disc}%',       inr(R["npv"]),         inr(L["npv"])],
            ], columns=["Metric", "Cash Purchase", "Loan Financing"])
            st.dataframe(comp, use_container_width=True, hide_index=True)

            # Loan cashflow table
            st.markdown('<div class="section-header">LOAN CASHFLOW — YEAR BY YEAR</div>', unsafe_allow_html=True)
            lcf_df = pd.DataFrame(L["lcf"])
            lcf_df["Solar Income"] = lcf_df["SolarIncome"].apply(lambda v: inr(v, False))
            lcf_df["Annual EMI"]   = lcf_df["EMI"].apply(lambda v: inr(v, False))
            lcf_df["Net Benefit"]  = lcf_df["NetBenefit"].apply(lambda v: inr(v, False))
            lcf_df["Cumulative"]   = lcf_df["Cumulative"].apply(lambda v: inr(v, False))
            st.dataframe(lcf_df[["Year","Solar Income","Annual EMI","Net Benefit","Cumulative"]],
                        use_container_width=True, hide_index=True, height=400)

            # Insights
            st.markdown('<div class="section-header">KEY INSIGHTS</div>', unsafe_allow_html=True)
            emi_cov = R["cf"][0]["NetIncome"] / 12
            diff    = R["profit25"] - L["profit25"]

            insights = [
                ("📊 Payback Comparison",
                 f"Cash purchase breaks even in {R['payback']} years. "
                 f"Loan scenario breaks even in {L['payback']} years — "
                 f"lower upfront (Rs.{L['dp']:,}) vs full investment (Rs.{R['nc']:,})."),
                ("💹 Profitability",
                 f"Cash IRR: {R['irr']}% vs Loan IRR: {L['irr']}%. "
                 f"25-year profit difference: {inr(abs(int(diff)))} in favour of "
                 f"{'cash purchase' if diff>0 else 'loan financing'}."),
                ("🏦 EMI Coverage",
                 f"Monthly solar savings in Year 1 ≈ {inr(int(emi_cov))}. "
                 f"Monthly EMI = {inr(L['emi'])}. "
                 f"{'✅ EMI fully covered by solar from Day 1.' if emi_cov>=L['emi'] else '⚠️ Partial top-up required in early years.'}"),
                ("💡 Recommendation",
                 f"SBI Surya Ghar @ {rate}% is most cost-effective. "
                 f"Total interest: {inr(L['tint'])}. Consider prepayment after Year 3 to save on interest. "
                 f"From Year {tenure+1}, full solar income is net surplus."),
            ]
            for title, body in insights:
                st.markdown(f"""<div class="insight-box">
                    <div class="insight-title">{title}</div>
                    <div class="insight-body">{body}</div>
                </div>""", unsafe_allow_html=True)

    # ══ TAB 4 — CHARTS ═══════════════════════════════════════
    with tabs[3]:
        col1, col2 = st.columns(2)

        with col1:
            # Yield bar chart
            fig1 = go.Figure()
            years  = [r["Year"] for r in R["cf"]]
            yields = [r["Yield"] for r in R["cf"]]
            fig1.add_trace(go.Bar(
                x=years, y=yields,
                marker_color=[f'rgb({180+i*2},{130},{30})' for i in range(25)],
                name="Annual Yield"
            ))
            fig1.update_layout(
                title="25-Year Solar Generation Forecast (kWh)",
                xaxis_title="Year", yaxis_title="kWh",
                plot_bgcolor="#F8FAFC", paper_bgcolor="#F8FAFC",
                font=dict(family="Inter"),
                title_font=dict(size=13, color="#0D2137"),
                height=320
            )
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            # Cumulative cashflow
            cum_vals  = [r["Cumulative"] for r in R["cf"]]
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=years, y=cum_vals,
                fill='tozeroy',
                fillcolor='rgba(26,107,60,0.15)',
                line=dict(color="#1A6B3C", width=2.5),
                name="Cash Purchase"
            ))
            if L:
                loan_cum = [r["Cumulative"] for r in L["lcf"]]
                fig2.add_trace(go.Scatter(
                    x=years, y=loan_cum,
                    line=dict(color="#C9922A", width=2.5, dash="dash"),
                    name="Loan Financing"
                ))
            fig2.add_hline(y=0, line_color="#334155", line_width=1)
            fig2.update_layout(
                title="Cumulative Net Cashflow (Rs.)",
                xaxis_title="Year", yaxis_title="Rs.",
                plot_bgcolor="#F8FAFC", paper_bgcolor="#F8FAFC",
                font=dict(family="Inter"),
                title_font=dict(size=13, color="#0D2137"),
                legend=dict(bgcolor="rgba(0,0,0,0)"),
                height=320
            )
            st.plotly_chart(fig2, use_container_width=True)

        col3, col4 = st.columns(2)
        with col3:
            # Annual net income
            net_inc = [r["NetIncome"] for r in R["cf"]]
            colors_ni = ["#1A6B3C" if v>=0 else "#8B1A1A" for v in net_inc]
            fig3 = go.Figure(go.Bar(x=years, y=net_inc, marker_color=colors_ni))
            fig3.update_layout(
                title="Annual Net Income — Cash (Rs.)",
                xaxis_title="Year", yaxis_title="Rs.",
                plot_bgcolor="#F8FAFC", paper_bgcolor="#F8FAFC",
                font=dict(family="Inter"),
                title_font=dict(size=13, color="#0D2137"),
                height=300
            )
            st.plotly_chart(fig3, use_container_width=True)

        with col4:
            if L:
                nb = [r["NetBenefit"] for r in L["lcf"]]
                nb_cols = ["#1A6B3C" if v>=0 else "#8B1A1A" for v in nb]
                fig4 = go.Figure(go.Bar(x=years, y=nb, marker_color=nb_cols))
                fig4.update_layout(
                    title="Annual Net Benefit — Loan (Rs.)",
                    xaxis_title="Year", yaxis_title="Rs.",
                    plot_bgcolor="#F8FAFC", paper_bgcolor="#F8FAFC",
                    font=dict(family="Inter"),
                    title_font=dict(size=13, color="#0D2137"),
                    height=300
                )
                st.plotly_chart(fig4, use_container_width=True)
            else:
                # O&M escalation pie
                om_vals = [r["OM"] for r in R["cf"]]
                fig4 = go.Figure(go.Scatter(x=years, y=om_vals,
                    line=dict(color="#C9922A", width=2), fill='tozeroy',
                    fillcolor='rgba(201,146,42,0.15)'))
                fig4.update_layout(title="O&M Cost Escalation (Rs.)",
                    plot_bgcolor="#F8FAFC", paper_bgcolor="#F8FAFC",
                    height=300)
                st.plotly_chart(fig4, use_container_width=True)

    # ══ TAB 5 — AMORTIZATION ═════════════════════════════════
    with tabs[4]:
        if not L:
            st.info("Enable Bank Loan Financing in the sidebar to see amortization schedule.")
        else:
            st.markdown('<div class="section-header">ANNUAL AMORTIZATION SUMMARY</div>', unsafe_allow_html=True)

            am_rows = []
            for yr in range(1, tenure+1):
                sl    = L["amort"][(yr-1)*12 : yr*12]
                y_emi = sum(m["EMI"]      for m in sl)
                y_pri = sum(m["Principal"] for m in sl)
                y_int = sum(m["Interest"]  for m in sl)
                y_bal = sl[-1]["Balance"]
                lc    = L["lcf"][yr-1]
                am_rows.append({
                    "Loan Year":        yr,
                    "Annual EMI":       inr(y_emi, False),
                    "Principal Repaid": inr(y_pri, False),
                    "Interest Paid":    inr(y_int, False),
                    "Closing Balance":  inr(y_bal, False),
                    "Solar Net Income": inr(lc["SolarIncome"], False),
                    "Net Benefit":      inr(lc["NetBenefit"], False),
                })

            am_df = pd.DataFrame(am_rows)
            st.dataframe(am_df, use_container_width=True, hide_index=True)

            # Summary row
            col1, col2, col3 = st.columns(3)
            with col1: st.metric("Total EMI Paid",     inr(sum(sum(m["EMI"] for m in L["amort"][:tenure*12])  for _ in [1])))
            with col2: st.metric("Total Interest Paid", inr(L["tint"]))
            with col3: st.metric("Total Outflow",       inr(L["tpaid"]))

            # Monthly amortization chart
            st.markdown('<div class="section-header">MONTHLY PRINCIPAL vs INTEREST SPLIT</div>', unsafe_allow_html=True)
            months   = [m["Month"] for m in L["amort"]]
            prin_m   = [m["Principal"] for m in L["amort"]]
            int_m    = [m["Interest"]  for m in L["amort"]]
            bal_m    = [m["Balance"]   for m in L["amort"]]

            fig5 = make_subplots(specs=[[{"secondary_y": True}]])
            fig5.add_trace(go.Bar(x=months, y=prin_m, name="Principal", marker_color="#1A6B3C"), secondary_y=False)
            fig5.add_trace(go.Bar(x=months, y=int_m,  name="Interest",  marker_color="#8B1A1A"), secondary_y=False)
            fig5.add_trace(go.Scatter(x=months, y=bal_m, name="Balance",
                line=dict(color="#C9922A", width=2)), secondary_y=True)
            fig5.update_layout(
                barmode="stack",
                xaxis_title="Month",
                plot_bgcolor="#F8FAFC", paper_bgcolor="#F8FAFC",
                font=dict(family="Inter"),
                legend=dict(bgcolor="rgba(0,0,0,0)"),
                height=350
            )
            st.plotly_chart(fig5, use_container_width=True)

    # ══ TAB 6 — DOWNLOAD REPORT ══════════════════════════════
    with tabs[5]:
        st.markdown('<div class="section-header">GENERATE PREMIUM PDF FEASIBILITY REPORT</div>', unsafe_allow_html=True)

        col_l, col_r = st.columns([1, 1])
        with col_l:
            st.markdown("#### 📋 Report Details")
            client_name = st.text_input("Client / Applicant Name", value="M/s Sunrise Infra Pvt. Ltd.")
            report_ref  = st.text_input("Report Reference No.", value="SYI/2025-26/KA/0042")
            bank_name   = st.text_input("Bank / Scheme Name", value="State Bank of India — Surya Ghar Scheme" if loan_on else "N/A")

        with col_r:
            st.markdown("#### 📄 Report Contents")
            st.markdown("""
            The generated PDF includes:
            - ✅ **Page 1** — Corporate Cover Page with project details & KPI cards
            - ✅ **Page 2** — Executive Summary with all parameters
            - ✅ **Page 3** — 25-Year Cashflow Table (colour-coded)
            - ✅ **Page 4** — Bank Loan Analysis & Comparison
            - ✅ **Page 5** — Amortization Schedule & Recommendations
            """)
            st.info(f"Report based on: **{cap} kWp** system at **{city_sel.split('(')[0].strip()}**\n\nNet Investment: **{inr(R['nc'])}** | IRR: **{R['irr']}%** | Payback: **{R['payback']} Years**")

        st.markdown("---")

        gen_col, _ = st.columns([1, 2])
        with gen_col:
            gen_btn = st.button("📄 Generate PDF Report", type="primary", use_container_width=True)

        if gen_btn:
            with st.spinner("Generating 5-page premium PDF report..."):
                inp_params = dict(
                    client   = client_name,
                    ref      = report_ref,
                    bank     = bank_name,
                    city     = city_sel.split("(")[0].strip(),
                    state    = city.get("state", "India"),
                    cap      = cap,
                    cost_kw  = cost_kw,
                    subsidy  = subsidy,
                    ghi      = ghi,
                    pr       = pr,
                    deg      = deg,
                    imp_t    = imp_t,
                    exp_t    = exp_t,
                    t_esc    = t_esc,
                    sc       = sc,
                    om0      = om0,
                    om_esc   = om_esc,
                    inv_rep  = inv_rep,
                    disc     = disc,
                    down_pct = down_pct if loan_on else 20,
                    rate     = rate     if loan_on else 9.15,
                    tenure   = tenure   if loan_on else 7,
                )
                try:
                    pdf_bytes = generate_pdf(R, inp_params)
                    ref_slug  = report_ref.replace("/", "-")
                    st.success("✅ PDF generated successfully! Click below to download.")
                    st.download_button(
                        label     = "⬇ Download PDF Report",
                        data      = pdf_bytes,
                        file_name = f"SolarYield_{inp_params['city']}_{ref_slug}.pdf",
                        mime      = "application/pdf",
                        use_container_width = True,
                    )
                except Exception as e:
                    st.error(f"Error generating PDF: {e}")
                    st.exception(e)

    # ── DISCLAIMER ───────────────────────────────────────────
    st.markdown("""<div class="disclaimer">
        <b>DISCLAIMER:</b> This tool is for indicative and planning purposes only.
        Actual solar yield depends on local weather conditions, shading, soiling, panel orientation and system losses.
        Electricity tariffs, bank interest rates and government subsidies are subject to revision without notice.
        Consult a CEIG-certified solar installer and your bank before final commitment.
        PM Surya Ghar subsidy subject to MNRE/DISCOM approval and scheme availability.
        SolarYield India Pvt. Ltd. · Version 3.0
    </div>""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
