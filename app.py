"""
SolarYield India — Streamlit Web App v4.0
Sections: NASA API · Coordinates · Tilt/Azimuth · Load · Inverter · Battery · Loan · PDF
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import math, datetime, requests
from io import BytesIO

st.set_page_config(page_title="SolarYield India", page_icon="☀️", layout="wide",
                   initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Syne:wght@700;800&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}
.main-hdr{background:linear-gradient(135deg,#0D2137,#163350 60%,#1B4A8A);
  padding:1.5rem 2.5rem;border-radius:12px;margin-bottom:1rem;
  border-bottom:3px solid #C9922A;}
.main-hdr h1{font-family:'Syne',sans-serif;color:#F0B429;font-size:1.9rem;margin:0;}
.main-hdr .sub{color:#94A3B8;font-size:0.8rem;margin-top:.3rem;}
.api-badge{background:rgba(201,146,42,.18);border:1px solid #C9922A;color:#F0B429;
  padding:2px 10px;border-radius:20px;font-size:.7rem;font-weight:600;margin-left:8px;}
.kpi-card{background:linear-gradient(135deg,#0D2137,#163350);
  border:1px solid rgba(201,146,42,.3);border-top:3px solid #C9922A;
  border-radius:10px;padding:1rem;text-align:center;margin-bottom:.5rem;}
.kpi-val{font-size:1.45rem;font-weight:700;color:#F0B429;font-family:'Syne',sans-serif;}
.kpi-unit{font-size:.65rem;color:#94A3B8;text-transform:uppercase;letter-spacing:1px;}
.kpi-label{font-size:.7rem;color:#CBD5E1;margin-top:.15rem;}
.kpi-green{border-top-color:#1A6B3C;}.kpi-green .kpi-val{color:#22C55E;}
.kpi-blue{border-top-color:#1A5276;}.kpi-blue .kpi-val{color:#60A5FA;}
.kpi-violet{border-top-color:#6D28D9;}.kpi-violet .kpi-val{color:#A78BFA;}
.sec-hdr{background:linear-gradient(90deg,#0D2137,#163350);color:#F0B429;
  padding:.5rem 1rem;border-radius:6px;border-left:4px solid #C9922A;
  font-weight:700;font-size:.78rem;text-transform:uppercase;letter-spacing:1px;
  margin:.9rem 0 .6rem 0;}
.nasa-box{background:linear-gradient(135deg,#0a1628,#0f2744);
  border:1px solid #C9922A;border-radius:10px;padding:1rem 1.2rem;margin:.4rem 0;}
.nasa-box h4{color:#F0B429;margin:0 0 .4rem 0;font-size:.88rem;}
.nasa-url{font-family:monospace;font-size:.68rem;color:#60A5FA;word-break:break-all;
  background:rgba(0,0,0,.3);padding:.35rem .6rem;border-radius:4px;display:block;margin-top:.35rem;}
.inv-box{background:linear-gradient(135deg,#EEF2FF,#E0E7FF);
  border:2px solid #6366F1;border-radius:10px;padding:1rem;text-align:center;}
.bat-box{background:linear-gradient(135deg,#F0FDF4,#DCFCE7);
  border:2px solid #16A34A;border-radius:10px;padding:1rem;text-align:center;}
.insight-box{background:#F8FAFC;border-left:4px solid #C9922A;
  border-radius:0 8px 8px 0;padding:.65rem 1rem;margin:.35rem 0;}
.insight-title{font-weight:700;color:#0D2137;font-size:.76rem;text-transform:uppercase;}
.insight-body{color:#334155;font-size:.78rem;margin-top:.2rem;}
.disc-box{background:#F8F9FA;border:1px solid #E2E8F0;border-left:4px solid #C9922A;
  border-radius:4px;padding:.65rem 1rem;font-size:.68rem;color:#64748B;margin-top:1rem;}
div[data-testid="stMetric"]{background:linear-gradient(135deg,#0D2137,#163350);
  border:1px solid rgba(201,146,42,.3);border-radius:8px;padding:.7rem;}
div[data-testid="stMetric"] label{color:#94A3B8!important;}
div[data-testid="stMetric"] div[data-testid="stMetricValue"]{color:#F0B429!important;font-weight:700;}
.stTabs [data-baseweb="tab-highlight"]{background-color:#C9922A;}
</style>
""", unsafe_allow_html=True)

# ── DATA ──────────────────────────────────────────────────────
CITIES = {
    "Bengaluru (Karnataka)":   {"lat":12.97,"lon":77.59,"ghi":5.3,"tariff":6.50,"fit":3.82,"state":"Karnataka"},
    "Mumbai (Maharashtra)":    {"lat":19.07,"lon":72.88,"ghi":5.0,"tariff":5.50,"fit":2.90,"state":"Maharashtra"},
    "Delhi (NCT)":             {"lat":28.61,"lon":77.21,"ghi":5.4,"tariff":6.00,"fit":3.00,"state":"Delhi"},
    "Chennai (Tamil Nadu)":    {"lat":13.08,"lon":80.27,"ghi":5.6,"tariff":4.50,"fit":3.20,"state":"Tamil Nadu"},
    "Hyderabad (Telangana)":   {"lat":17.38,"lon":78.49,"ghi":5.5,"tariff":4.20,"fit":3.50,"state":"Telangana"},
    "Ahmedabad (Gujarat)":     {"lat":23.02,"lon":72.57,"ghi":5.8,"tariff":4.00,"fit":2.25,"state":"Gujarat"},
    "Pune (Maharashtra)":      {"lat":18.52,"lon":73.86,"ghi":5.2,"tariff":5.50,"fit":2.90,"state":"Maharashtra"},
    "Jaipur (Rajasthan)":      {"lat":26.91,"lon":75.79,"ghi":6.0,"tariff":5.55,"fit":3.26,"state":"Rajasthan"},
    "Lucknow (UP)":            {"lat":26.85,"lon":80.95,"ghi":4.9,"tariff":5.50,"fit":2.90,"state":"Uttar Pradesh"},
    "Kolkata (West Bengal)":   {"lat":22.57,"lon":88.37,"ghi":4.5,"tariff":7.00,"fit":2.50,"state":"West Bengal"},
    "Bhopal (MP)":             {"lat":23.26,"lon":77.41,"ghi":5.5,"tariff":4.53,"fit":3.14,"state":"Madhya Pradesh"},
    "Chandigarh (Punjab)":     {"lat":30.73,"lon":76.78,"ghi":4.8,"tariff":4.39,"fit":2.65,"state":"Punjab"},
    "Kochi (Kerala)":          {"lat": 9.93,"lon":76.27,"ghi":4.6,"tariff":3.45,"fit":3.15,"state":"Kerala"},
    "Custom Location":         {"lat":20.59,"lon":78.96,"ghi":5.0,"tariff":5.00,"fit":3.00,"state":"India"},
}
BANKS = {
    "SBI — Surya Ghar (≤3 kW)":  7.00,
    "SBI — Surya Ghar (3–10 kW)": 9.15,
    "SBI — Home Loan Customer":   9.15,
    "Punjab National Bank":        9.50,
    "Bank of Baroda":             10.00,
    "IDBI Bank":                  10.50,
    "Union Bank of India":        10.25,
    "ICICI Bank":                 11.00,
    "HDFC Bank":                  11.50,
    "Custom Rate":                 9.15,
}
APPLIANCES = [
    ("LED Lights (10 nos)",     0.10,  8),
    ("Ceiling Fans (4 nos)",    0.30, 10),
    ("Refrigerator (250 L)",    0.25, 24),
    ("TV / Set-top Box",        0.15,  6),
    ("Washing Machine",         0.50,  1),
    ("Water Pump (0.5 HP)",     0.37,  2),
    ("Air Conditioner (1.5 T)", 1.50,  6),
    ("Laptop / Computer",       0.10,  6),
    ("Geyser / Water Heater",   2.00,  1),
    ("Microwave Oven",          1.00,  0.5),
]
BAT_DEFAULTS = {"Lithium-Ion (LFP)":{"eff":95,"dod":90},"Lithium-Ion (NMC)":{"eff":92,"dod":85},
                "Lead Acid":{"eff":80,"dod":50},"Flow Battery":{"eff":75,"dod":80}}

# ── HELPERS ───────────────────────────────────────────────────
def fetch_nasa(lat, lon):
    url = (f"https://power.larc.nasa.gov/api/temporal/climatology/point"
           f"?parameters=ALLSKY_SFC_SW_DWN&community=RE"
           f"&longitude={lon:.4f}&latitude={lat:.4f}&format=JSON")
    try:
        d = requests.get(url, timeout=15).json()
        m = d["properties"]["parameter"]["ALLSKY_SFC_SW_DWN"]
        ann = m.get("ANN")
        monthly = {k:v for k,v in m.items() if k not in ("ANN","CLR_ANN")}
        return {"ghi":round(ann,2) if ann else None,"monthly":monthly,"url":url,"ok":True}
    except Exception as e:
        return {"ghi":None,"monthly":{},"url":url,"ok":False,"err":str(e)}

def tilt_f(lat, tilt, az):
    opt = abs(lat)*0.76+3.1
    tf  = 1 - (abs(tilt-opt)/90)*0.15
    af  = 1 - (abs(az-180)/180)*0.25
    return round(max(0.5, min(1.10, tf*af)), 3)

def inr(v, short=True):
    if v is None: return "N/A"
    neg=v<0; av=abs(int(round(v)))
    if short and av>=10_000_000: return f"{'−' if neg else ''}Rs.{av/10_000_000:.2f} Cr"
    if short and av>=100_000:    return f"{'−' if neg else ''}Rs.{av/100_000:.2f} L"
    s=str(av)
    if len(s)>3: s=s[:-3]+","+s[-3:]
    if len(s)>7: s=s[:-7]+","+s[-7:]
    return f"{'−' if neg else ''}Rs.{s}"

def kpi(val, unit, label, cls=""):
    return f'<div class="kpi-card {cls}"><div class="kpi-val">{val}</div><div class="kpi-unit">{unit}</div><div class="kpi-label">{label}</div></div>'

def sh(txt): st.markdown(f'<div class="sec-hdr">{txt}</div>', unsafe_allow_html=True)

def insight(title, body):
    st.markdown(f'<div class="insight-box"><div class="insight-title">{title}</div><div class="insight-body">{body}</div></div>', unsafe_allow_html=True)

# ── SIMULATION ─────────────────────────────────────────────────
def simulate(cap, cost_kw, sub, ghi, pr, deg, imp_t, exp_t,
             t_esc, sc, om0, om_esc, inv_rep, disc,
             loan_on, dp_pct, rate, tenure,
             tf_val=1.0, bat_cap=0, bat_eff=0.9, bat_dod=0.8):
    cost=cap*cost_kw; nc=cost-sub; y1=cap*ghi*tf_val*365*pr
    cf,cum,npv=[],- nc,-nc
    for y in range(1,26):
        yld   = y1*(1-deg)**(y-1)
        tar   = imp_t*(1+t_esc)**(y-1)
        exp   = exp_t*(1+t_esc)**(y-1)
        dgen  = yld/365
        bboost= min(bat_cap*bat_dod*bat_eff, dgen*(1-sc)) if bat_cap>0 else 0
        esc   = min(0.99, sc+(bboost/dgen if dgen>0 else 0))
        saved = yld*esc*tar; exprev=yld*(1-esc)*exp
        om    = om0*(1+om_esc)**(y-1)
        extra = inv_rep if y==12 else 0
        net   = saved+exprev-om-extra
        cum  += net; npv+=net/(1+disc/100)**y
        cf.append(dict(Year=y,Yield=round(yld),Tariff=round(tar,2),
            BillSaved=round(saved),ExportRev=round(exprev),
            OM=round(om),Extra=extra,NetIncome=round(net),
            Cumulative=round(cum),EffSC=round(esc*100,1)))
    pb=next((r["Year"] for r in cf if r["Cumulative"]>=0),None)
    flows=[-nc]+[r["NetIncome"] for r in cf]
    ri=0.10
    for _ in range(300):
        f=sum(v/(1+ri)**i for i,v in enumerate(flows))
        df=sum(-i*v/(1+ri)**(i+1) for i,v in enumerate(flows))
        if abs(df)<1e-12: break
        ri-=f/df
        if ri<=-1: ri=-0.999
    irr=round(ri*100,2) if -1<ri<10 else None
    tom=sum(r["OM"]+r["Extra"] for r in cf)
    ty=sum(r["Yield"] for r in cf)
    lcoe=round((nc+tom)/ty,2) if ty else 0
    res=dict(cost=round(cost),nc=round(nc),y1=round(y1),cf=cf,
             payback=pb,irr=irr,npv=round(npv),lcoe=lcoe,
             profit25=round(cf[-1]["Cumulative"]),gross25=round(cf[-1]["Cumulative"]+nc))
    if loan_on:
        dp=round(nc*dp_pct/100); la=nc-dp; rm=rate/100/12; nm=tenure*12
        emi=la*rm*(1+rm)**nm/((1+rm)**nm-1) if rm>0 else la/nm
        am,bal,ti=[],la,0
        for m in range(1,nm+1):
            ii=bal*rm; pp=emi-ii; bal=max(0,bal-pp); ti+=ii
            am.append(dict(Month=m,EMI=round(emi),Principal=round(pp),Interest=round(ii),Balance=round(bal)))
        lcf,lcum,lnpv=[],-dp,-dp
        for r in cf:
            ec=emi*12 if r["Year"]<=tenure else 0
            net=r["NetIncome"]-ec; lcum+=net; lnpv+=net/(1+disc/100)**r["Year"]
            lcf.append(dict(Year=r["Year"],SolarIncome=r["NetIncome"],
                            EMI=round(ec),NetBenefit=round(net),Cumulative=round(lcum)))
        lpb=next((r["Year"] for r in lcf if r["Cumulative"]>=0),None)
        f2=[-dp]+[r["NetBenefit"] for r in lcf]; r2=0.15
        for _ in range(300):
            f=sum(v/(1+r2)**i for i,v in enumerate(f2))
            df=sum(-i*v/(1+r2)**(i+1) for i,v in enumerate(f2))
            if abs(df)<1e-12: break
            r2-=f/df
            if r2<=-1: r2=-0.999
        li=round(r2*100,1) if -1<r2<10 else None
        res["loan"]=dict(dp=dp,lamt=round(la),emi=round(emi),nm=nm,
            ann=round(emi*12),tint=round(ti),tpaid=round(emi*nm+dp),
            amort=am,lcf=lcf,payback=lpb,irr=li,
            npv=round(lnpv),profit25=round(lcf[-1]["Cumulative"]))
    return res

# ── PDF GENERATOR ─────────────────────────────────────────────
def gen_pdf(R, P):
    from reportlab.pdfgen import canvas as C
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors as RC
    from reportlab.lib.units import mm
    from reportlab.pdfbase import pdfmetrics as PM
    from reportlab.pdfbase.ttfonts import TTFont
    import os, math as M
    for path,name in [('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf','Sans'),
                      ('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf','Sans-B'),
                      ('/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf','Sans-I')]:
        if os.path.exists(path):
            try: PM.registerFont(TTFont(name,path))
            except: pass
    W,H=A4; NV=RC.HexColor('#0D2137'); NV2=RC.HexColor('#163350')
    GD=RC.HexColor('#C9922A'); GD2=RC.HexColor('#F0B429'); GN=RC.HexColor('#1A6B3C')
    RD=RC.HexColor('#8B1A1A'); SL=RC.HexColor('#334155'); MU=RC.HexColor('#6B7280')
    BD=RC.HexColor('#BDC3C7'); LT=RC.HexColor('#F4F6F8')
    RS='Rs.'
    def fm(v,sh=True):
        if v is None: return "N/A"
        ng=v<0; av=abs(int(round(v)))
        if sh and av>=10_000_000: return f"{'(-) ' if ng else ''}{RS}{av/10_000_000:.2f} Cr"
        if sh and av>=100_000:    return f"{'(-) ' if ng else ''}{RS}{av/100_000:.2f} L"
        s=str(av)
        if len(s)>3: s=s[:-3]+","+s[-3:]
        if len(s)>7: s=s[:-7]+","+s[-7:]
        return f"{'(-) ' if ng else ''}{RS}{s}"
    def ff(v):
        if v is None: return "N/A"
        ng=v<0; av=abs(int(round(v))); s=str(av)
        if len(s)>3: s=s[:-3]+","+s[-3:]
        if len(s)>7: s=s[:-7]+","+s[-7:]
        return f"{'-' if ng else ''}{RS}{s}"
    def tx(c,t,x,y,fn='Sans',sz=9,cl=SL,al='left'):
        c.setFont(fn,sz); c.setFillColor(cl); t=str(t)
        if al=='center': c.drawCentredString(x,y,t)
        elif al=='right': c.drawRightString(x,y,t)
        else: c.drawString(x,y,t)
    def bx(c,x,y,w,h,fi=None,st2=None,lw=0.5):
        if fi: c.setFillColor(fi)
        if st2: c.setStrokeColor(st2); c.setLineWidth(lw)
        c.rect(x,y,w,h,fill=bool(fi),stroke=bool(st2))
    def hl(c,x1,x2,y,cl=BD,lw=0.4): c.setStrokeColor(cl); c.setLineWidth(lw); c.line(x1,y,x2,y)
    def vl(c,x,y1,y2,cl=BD,lw=0.4): c.setStrokeColor(cl); c.setLineWidth(lw); c.line(x,y1,x,y2)
    def chrome(c,pg,title):
        bx(c,0,H-18*mm,W,18*mm,fi=NV2); bx(c,0,H-18*mm,W,1.2,fi=GD)
        bx(c,0,H-18*mm,38*mm,18*mm,fi=NV)
        tx(c,"SolarYield",3*mm,H-9*mm,'Sans-B',10,GD2)
        tx(c,"INDIA  Pvt. Ltd.",3*mm,H-14*mm,'Sans',7,RC.HexColor('#94A3B8'))
        vl(c,38*mm,H-18*mm,H,GD,1.5)
        tx(c,title.upper(),W/2,H-10*mm,'Sans-B',9,GD2,'center')
        tx(c,"Solar PV Investment Feasibility Report",W/2,H-15*mm,'Sans',6.5,RC.HexColor('#94A3B8'),'center')
        tx(c,f"Ref: {P.get('ref','SYI/2025-26')}",W-3*mm,H-9*mm,'Sans',7,RC.HexColor('#94A3B8'),'right')
        tx(c,f"Dated: {datetime.datetime.now().strftime('%d %b %Y')}",W-3*mm,H-14*mm,'Sans',7,RC.HexColor('#CBD5E1'),'right')
        bx(c,0,0,W,11*mm,fi=NV); bx(c,0,11*mm,W,0.8,fi=GD)
        tx(c,P.get('client','—'),5*mm,4*mm,'Sans',6.5,RC.HexColor('#94A3B8'))
        tx(c,"STRICTLY CONFIDENTIAL",W/2,4*mm,'Sans-I',6.5,RC.HexColor('#64748B'),'center')
        tx(c,f"Page {pg} of 5",W-5*mm,4*mm,'Sans-B',7,GD2,'right')
    def sec(c,x,y,w,title):
        bx(c,x,y-7*mm,w,7*mm,fi=NV); bx(c,x,y-7*mm,3,7*mm,fi=GD)
        tx(c,title,x+6*mm,y-4.5*mm,'Sans-B',8.5,RC.white); return y-9*mm
    def kcard(c,x,y,w,h,val,lbl,sub,vc=GD):
        bx(c,x,y,w,h,fi=RC.white,st2=BD,lw=0.5); bx(c,x,y+h-2,w,2,fi=vc)
        bx(c,x,y,w,7*mm,fi=NV)
        tx(c,str(val),x+w/2,y+h*.45,'Sans-B',11,vc,'center')
        tx(c,str(lbl),x+w/2,y+h*.26,'Sans',6.5,MU,'center')
        tx(c,str(sub),x+w/2,y+3,'Sans-B',6,GD2,'center')
    buf=BytesIO(); c=C.Canvas(buf,pagesize=A4)
    c.setTitle("SolarYield India — Solar PV Investment Feasibility Report")
    L=R.get("loan"); ML=12*mm; CW=W-24*mm
    # PG1 COVER
    bx(c,0,H*.52,W,H*.48,fi=NV2)
    c.setStrokeColor(RC.HexColor('#1E3F5A')); c.setLineWidth(0.6)
    for r2 in [35,60,85,110]: c.arc(W-5*mm-r2,H-5*mm-r2,W-5*mm+r2,H-5*mm+r2,180,90)
    c.setStrokeColor(GD); c.setLineWidth(2); c.arc(W-90*mm,H-90*mm,W+90*mm,H+90*mm,183,84)
    cx2,cy2=22*mm,H-30*mm
    c.setFillColor(GD); c.circle(cx2,cy2,12*mm,fill=1,stroke=0)
    c.setFillColor(NV2); c.circle(cx2,cy2,8.5*mm,fill=1,stroke=0)
    c.setFillColor(GD); c.circle(cx2,cy2,5*mm,fill=1,stroke=0)
    c.setStrokeColor(GD2); c.setLineWidth(1.3)
    for ang in range(0,360,30):
        r=M.radians(ang)
        c.line(cx2+13.5*mm*M.cos(r),cy2+13.5*mm*M.sin(r),cx2+17*mm*M.cos(r),cy2+17*mm*M.sin(r))
    tx(c,"SOLARYIELD INDIA",38*mm,H-23*mm,'Sans-B',16,GD2)
    tx(c,"PRIVATE LIMITED",38*mm,H-29*mm,'Sans',8.5,RC.HexColor('#94A3B8'))
    bx(c,15*mm,H-36*mm,W-30*mm,1.5,fi=GD)
    tx(c,"SOLAR PHOTOVOLTAIC",15*mm,H-48*mm,'Sans-B',22,RC.white)
    tx(c,"INVESTMENT FEASIBILITY REPORT",15*mm,H-60*mm,'Sans-B',18,RC.white)
    tx(c,f"Tilt: {P.get('tilt',15)}\u00b0 | Az: {P.get('az',180)}\u00b0 | Lat: {P.get('lat',0):.2f}N Lon: {P.get('lon',0):.2f}E | NASA GHI: {P.get('ghi',5.0)} kWh/m\u00b2/day",
        15*mm,H-68*mm,'Sans-I',8,RC.HexColor('#8BA7C0'))
    c.setFillColor(GD)
    p=c.beginPath(); p.moveTo(0,H*.52); p.lineTo(W,H*.52)
    p.lineTo(W,H*.52-8); p.lineTo(0,H*.52+8); p.close(); c.drawPath(p,fill=1,stroke=0)
    bx(c,0,0,W,H*.52,fi=RC.white)
    bw2,bh2=115*mm,88*mm; bx2,by2=15*mm,H*.52-10*mm-bh2
    bx(c,bx2,by2,bw2,bh2,fi=RC.white,st2=BD,lw=0.6)
    bx(c,bx2,by2+bh2-9*mm,bw2,9*mm,fi=NV)
    tx(c,"PROJECT DETAILS",bx2+bw2/2,by2+bh2-6*mm,'Sans-B',8,GD2,'center')
    dtls=[("Client",P.get("client","—")),("Location",f'{P.get("city","—")}, {P.get("state","—")}'),
          ("Coordinates",f'{P.get("lat",0):.3f}°N, {P.get("lon",0):.3f}°E'),
          ("System",f'{P.get("cap",0)} kWp On-Grid Solar PV'),
          ("Inverter",f'{P.get("inv_cap",0):.1f} kVA | Ratio: {P.get("inv_ratio",1.15):.2f}'),
          ("Battery",f'{P.get("bat_cap",0)} kWh' if P.get("bat_cap",0)>0 else "Not Included"),
          ("Tilt / Azimuth",f'{P.get("tilt",15)}\u00b0 / {P.get("az",180)}\u00b0'),
          ("NASA GHI",f'{P.get("ghi",5.0)} kWh/m\u00b2/day'),
          ("Net Investment",ff(R["nc"])),("Ref",P.get("ref","SYI/2025-26")),
          ("Date",datetime.datetime.now().strftime("%d %B %Y"))]
    dy=by2+bh2-16*mm
    for lbl,val in dtls:
        tx(c,lbl+":",bx2+4*mm,dy,'Sans',6.5,MU)
        tx(c,val,bx2+bw2-3*mm,dy,'Sans-B',6.5,NV,'right')
        dy-=6.8*mm; hl(c,bx2+3*mm,bx2+bw2-3*mm,dy+4*mm,LT,0.4)
    if L:
        mts=[(fm(R["nc"]),"Net Investment","After Subsidy",NV2),
             (f'{R["payback"]} Yrs',"Cash Payback","Simple",GN),
             (f'{L["payback"]} Yrs',"Loan Payback","Financing",GD),
             (f'{R["irr"]}%',"IRR 25yr","Cash",NV2)]
    else:
        mts=[(fm(R["nc"]),"Net Investment","After Subsidy",NV2),
             (f'{R["payback"]} Yrs',"Payback","Cash",GN),
             (f'{R["irr"]}%',"IRR 25yr","Cash",GD),
             (f'Rs.{R["lcoe"]:.2f}',"LCOE","Rs/kWh",NV2)]
    kw3,kh3=62*mm,18*mm; rx3=140*mm; ry3=by2+bh2-9*mm-4*(kh3+2*mm)+2*mm
    for i,(v,l,s,cl) in enumerate(mts): kcard(c,rx3,ry3+i*(kh3+2*mm),kw3,kh3,v,l,s,cl)
    bx(c,0,0,W,16*mm,fi=NV); bx(c,0,16*mm,W,1.2,fi=GD)
    tx(c,f'Report: {P.get("ref","SYI")}',15*mm,10*mm,'Sans-B',7.5,GD2)
    tx(c,"CONFIDENTIAL",W-15*mm,10*mm,'Sans-B',7.5,GD,'right')
    tx(c,"Proprietary — Unauthorised reproduction prohibited.",W/2,4*mm,'Sans-I',6,RC.HexColor('#4B6278'),'center')
    c.showPage()
    # PG2 EXEC SUMMARY
    chrome(c,2,"Executive Summary"); y=H-22*mm
    y=sec(c,ML,y,CW,"KEY PERFORMANCE INDICATORS — CASH PURCHASE")
    kw4=(CW-3*mm)/4; kh4=19*mm
    for i,(v,l,s,cl) in enumerate([
        (fm(R["nc"]),"Net Investment","After PM Subsidy",NV2),
        (f'{R["y1"]:,} kWh',"Year 1 Yield","Annual Gen.",GN),
        (f'{R["payback"]} Years',"Payback","Cash Purchase",RC.HexColor('#1A5276')),
        (f'{R["irr"]}%',"IRR 25 Years","Int. Rate of Return",GD)]):
        kcard(c,ML+i*(kw4+1*mm),y-kh4,kw4,kh4,v,l,s,cl)
    y-=kh4+3*mm
    for i,(v,l,s,cl) in enumerate([
        (f'Rs.{R["lcoe"]:.2f}/kWh',"LCOE","Levelised Cost",GD),
        (fm(R["npv"]),"NPV",f'@ {P.get("disc",8)}% Disc.',GN),
        (fm(R["profit25"]),"Net Profit 25yr","Cash",RC.HexColor('#1A5276')),
        (f'{P.get("ghi",5.0)} kWh/m\u00b2',"Daily GHI","NASA POWER",NV2)]):
        kcard(c,ML+i*(kw4+1*mm),y-kh4,kw4,kh4,v,l,s,cl)
    y-=kh4+4*mm
    if L:
        y=sec(c,ML,y,CW,"LOAN SCENARIO KPIs")
        for i,(v,l,s,cl) in enumerate([
            (ff(L["dp"]),"Down Payment",f'{P.get("dp_pct",20)}% Upfront',NV2),
            (ff(L["emi"]),"Monthly EMI","Rs./Month",GD),
            (f'{L["payback"]} Years',"Loan Payback","With Financing",GN),
            (f'{L["irr"]}%' if L["irr"] else "N/A","Loan IRR","25yr",RC.HexColor('#1A5276'))]):
            kcard(c,ML+i*(kw4+1*mm),y-kh4,kw4,kh4,v,l,s,cl)
        y-=kh4+4*mm
    y=sec(c,ML,y,CW,"TECHNICAL & PROJECT PARAMETERS")
    params=[
        [("Capacity",f'{P.get("cap",0)} kWp'),("City",f'{P.get("city","")}, {P.get("state","")}')],
        [("Lat / Lon",f'{P.get("lat",0):.3f}°N {P.get("lon",0):.3f}°E'),("NASA GHI",f'{P.get("ghi",5.0)} kWh/m\u00b2/day')],
        [("Tilt",f'{P.get("tilt",15)}\u00b0'),("Azimuth",f'{P.get("az",180)}\u00b0 (180=South)')],
        [("Inverter",f'{P.get("inv_cap",0):.1f} kVA'),("DC/AC Ratio",f'{P.get("inv_ratio",1.15):.2f}')],
        [("Battery",f'{P.get("bat_cap",0)} kWh'),("Daily Load",f'{P.get("daily_load",0):.1f} kWh/day')],
        [("Import Tariff",f'Rs.{P.get("imp_t",6.5):.2f}/kWh'),("Export FiT",f'Rs.{P.get("exp_t",3.82):.2f}/kWh')],
        [("Self Consumption",f'{P.get("sc",0.75):.0%}'),("Performance Ratio",f'{P.get("pr",0.8):.0%}')],
        [("O&M Year 1",ff(P.get("om0",5000))),("System Life","25 Years")],
    ]
    cw5=CW/4; rh5=6.5*mm
    for ri,row in enumerate(params):
        bg=LT if ri%2==0 else RC.white; bx(c,ML,y-rh5,CW,rh5,fi=bg)
        for ci,(lb,vl2) in enumerate(row):
            bx3=ML+ci*2*cw5
            tx(c,lb,bx3+2*mm,y-rh5+2*mm,'Sans-B',7,SL)
            tx(c,vl2,bx3+cw5+2*mm,y-rh5+2*mm,'Sans',7,NV)
            if ci==0: vl(c,bx3+cw5,y-rh5,y,BD,0.4)
        vl(c,ML+2*cw5,y-rh5,y,BD,0.8); hl(c,ML,ML+CW,y-rh5,BD,0.3); y-=rh5
    bx(c,ML,y,CW,len(params)*rh5,fi=None,st2=BD,lw=0.6); c.showPage()
    # PG3 YIELD TABLE
    chrome(c,3,"Solar Yield & O&M Analysis"); cf=R["cf"]; y=H-22*mm
    y=sec(c,ML,y,CW,"25-YEAR ANNUAL ENERGY & FINANCIAL PERFORMANCE")
    cols6=["Yr","Yield kWh","Tariff Rs","Bill Saved","Export Rev","O & M","Net Income","Cumulative"]
    cws6=[9,22,20,23,22,22,24,26]; rh6=5.8*mm
    bx(c,ML,y-rh6,CW,rh6,fi=NV)
    xc6=ML
    for ci,(col,cw6) in enumerate(zip(cols6,cws6)):
        tx(c,col,xc6+cw6*mm/2,y-rh6*.55,'Sans-B',6.5,GD2,'center')
        if ci<len(cols6)-1: vl(c,xc6+cw6*mm,y-rh6,y,RC.HexColor('#1E3F5A'),0.5)
        xc6+=cw6*mm
    y-=rh6
    for fi2,row in enumerate(cf):
        ii=row["Year"]==12; ip=R.get("payback") and row["Year"]==R["payback"]
        bg6=RC.HexColor('#FEF9C3') if ii else (RC.HexColor('#D1FAE5') if ip else (LT if fi2%2==0 else RC.white))
        bx(c,ML,y-rh6,CW,rh6,fi=bg6)
        oms=ff(row["OM"])+(f'+{ff(row["Extra"])}' if row["Extra"] else "")
        vs=[(str(row["Year"]),'c'),(f'{row["Yield"]:,}','r'),
            (f'Rs.{row["Tariff"]:.2f}','r'),(ff(row["BillSaved"]),'r'),
            (ff(row["ExportRev"]),'r'),(oms,'r'),(ff(row["NetIncome"]),'r'),(ff(row["Cumulative"]),'r')]
        xc6=ML
        for ci2,((vv,al),cw6) in enumerate(zip(vs,cws6)):
            fc6=NV if ci2==0 else (GN if ci2==7 and row["Cumulative"]>=0 else (RD if ci2==7 else SL))
            fn6='Sans-B' if ci2 in(0,7) else 'Sans'
            px6=xc6+cw6*mm/2 if al=='c' else xc6+cw6*mm-1.5*mm
            tx(c,vv,px6,y-rh6+1.8*mm,fn6,6,fc6,'center' if al=='c' else 'right')
            if ci2<len(vs)-1: vl(c,xc6+cw6*mm,y-rh6,y,BD,0.25)
            xc6+=cw6*mm
        hl(c,ML,ML+CW,y-rh6,BD,0.25); y-=rh6
    bx(c,ML,y,CW,len(cf)*rh6+rh6,fi=None,st2=BD,lw=0.6); c.showPage()
    # PG4 LOAN
    chrome(c,4,"Bank Loan Financing Analysis"); y=H-22*mm
    if L:
        y=sec(c,ML,y,CW,f"LOAN DETAILS — {P.get('bank','SBI')} @ {P.get('rate',9.15)}% p.a.")
        kw7=(CW-4*mm)/5; kh7=19*mm
        for i,(v,l,s,cl) in enumerate([
            (ff(L["dp"]),"Down Payment",f'{P.get("dp_pct",20)}% of Cost',NV2),
            (ff(L["lamt"]),"Loan Principal","Amount Financed",GD),
            (ff(L["emi"]),"Monthly EMI","Rs./Month",GN),
            (f'{P.get("rate",9.15)}%',"Interest Rate","Per Annum",RC.HexColor('#1A5276')),
            (f'{P.get("tenure",7)} Yr',"Loan Tenure","Repayment",NV2)]):
            kcard(c,ML+i*(kw7+1*mm),y-kh7,kw7,kh7,v,l,s,cl)
        y-=kh7+3*mm
        for i,(v,l,s,cl) in enumerate([
            (fm(L["tint"]),"Total Interest","Over Tenure",RD),
            (fm(L["tpaid"]),"Total Outflow","Down+EMIs",SL),
            (f'{L["payback"]} Yrs',"Loan Payback","With Financing",GN),
            (f'{L["irr"]}%' if L["irr"] else "N/A","Loan IRR","25 Year",GD),
            (fm(L["profit25"]),"Net Profit 25yr","Loan",RC.HexColor('#1A5276'))]):
            kcard(c,ML+i*(kw7+1*mm),y-kh7,kw7,kh7,v,l,s,cl)
        y-=kh7+5*mm
        y=sec(c,ML,y,CW,"CASH vs. LOAN — COMPARISON")
        comp=[("Parameter","Cash Purchase","Loan Financing"),
              ("Upfront Investment",ff(R["nc"]),ff(L["dp"])),
              ("Loan Amount","—",ff(L["lamt"])),("Monthly EMI","—",ff(L["emi"])),
              ("Total Interest","—",fm(L["tint"])),("Total Outflow",ff(R["nc"]),fm(L["tpaid"])),
              ("Payback",f'{R["payback"]} Years',f'{L["payback"]} Years'),
              ("25yr Net Profit",fm(R["profit25"]),fm(L["profit25"])),
              ("IRR 25yr",f'{R["irr"]}%',f'{L["irr"]}%' if L["irr"] else "N/A"),
              (f'NPV @ {P.get("disc",8)}%',fm(R["npv"]),fm(L["npv"]))]
        c1w,c2w=62*mm,54*mm; rh8=6.5*mm
        for ri2,row in enumerate(comp):
            hdr=ri2==0; bg8=NV if hdr else (LT if ri2%2==0 else RC.white)
            bx(c,ML,y-rh8,CW,rh8,fi=bg8)
            tx(c,row[0],ML+3*mm,y-rh8+2.2*mm,'Sans-B',7.5 if hdr else 7,GD2 if hdr else SL)
            vl(c,ML+c1w,y-rh8,y,BD,0.5)
            tx(c,row[1],ML+c1w+3*mm,y-rh8+2.2*mm,'Sans-B' if hdr else 'Sans',7.5 if hdr else 7,GD2 if hdr else GN)
            vl(c,ML+c1w+c2w,y-rh8,y,BD,0.5)
            tx(c,row[2],ML+c1w+c2w+3*mm,y-rh8+2.2*mm,'Sans-B' if hdr else 'Sans',7.5 if hdr else 7,GD2 if hdr else GD)
            hl(c,ML,ML+CW,y-rh8,BD,0.3); y-=rh8
        bx(c,ML,y,CW,len(comp)*rh8,fi=None,st2=BD,lw=0.6)
    c.showPage()
    # PG5 AMORTIZATION
    chrome(c,5,"Amortization & Recommendations"); y=H-22*mm
    if L:
        tenure9=P.get("tenure",7)
        y=sec(c,ML,y,CW,f"LOAN AMORTIZATION — {P.get('bank','SBI')} @ {P.get('rate',9.15)}% | {tenure9} Years")
        cols9=["Loan\nYear","Annual\nEMI","Principal\nRepaid","Interest\nPaid","Closing\nBalance","Solar Net\nIncome","Net\nBenefit"]
        cws9=[14,24,24,24,28,28,24]; rh9=6.5*mm
        bx(c,ML,y-rh9,CW,rh9,fi=NV)
        xc9=ML
        for ci,(col,cw9) in enumerate(zip(cols9,cws9)):
            ls9=col.split('\n')
            if len(ls9)==2:
                tx(c,ls9[0],xc9+cw9*mm/2,y-rh9*.35,'Sans-B',6.5,GD2,'center')
                tx(c,ls9[1],xc9+cw9*mm/2,y-rh9*.72,'Sans-B',6.5,GD2,'center')
            else: tx(c,col,xc9+cw9*mm/2,y-rh9*.55,'Sans-B',6.5,GD2,'center')
            if ci<len(cols9)-1: vl(c,xc9+cw9*mm,y-rh9,y,RC.HexColor('#1E3F5A'),0.5)
            xc9+=cw9*mm
        y-=rh9; te2=tp2=ti2=ts2=tn2=0
        for yr2 in range(1,tenure9+1):
            sl2=L["amort"][(yr2-1)*12:yr2*12]
            ye2=sum(m["EMI"] for m in sl2); yp2=sum(m["Principal"] for m in sl2)
            yi2=sum(m["Interest"] for m in sl2); yb2=sl2[-1]["Balance"]
            lc3=L["lcf"][yr2-1]; nb3=lc3["NetBenefit"]
            te2+=ye2;tp2+=yp2;ti2+=yi2;ts2+=lc3["SolarIncome"];tn2+=nb3
            bg9=LT if yr2%2==0 else RC.white; bx(c,ML,y-rh9,CW,rh9,fi=bg9)
            vs9=[(str(yr2),'c'),(ff(ye2),'r'),(ff(yp2),'r'),
                 (ff(yi2),'r'),(ff(yb2),'r'),(ff(lc3["SolarIncome"]),'r'),(ff(nb3),'r')]
            xc9=ML
            for ci2,((vv2,al2),cw9) in enumerate(zip(vs9,cws9)):
                fc9=NV if ci2==0 else (GN if ci2==6 and nb3>=0 else (RD if ci2==6 else SL))
                px9=xc9+cw9*mm/2 if al2=='c' else xc9+cw9*mm-1.5*mm
                tx(c,vv2,px9,y-rh9+2*mm,'Sans-B' if ci2==0 else 'Sans',7,fc9,'center' if al2=='c' else 'right')
                if ci2<len(vs9)-1: vl(c,xc9+cw9*mm,y-rh9,y,BD,0.3)
                xc9+=cw9*mm
            hl(c,ML,ML+CW,y-rh9,BD,0.3); y-=rh9
        bx(c,ML,y-rh9,CW,rh9,fi=NV2)
        tots9=[("TOTAL",'c'),(ff(te2),'r'),(ff(tp2),'r'),(ff(ti2),'r'),("—",'c'),(ff(ts2),'r'),(ff(tn2),'r')]
        xc9=ML
        for ci2,((vv2,al2),cw9) in enumerate(zip(tots9,cws9)):
            px9=xc9+cw9*mm/2 if al2=='c' else xc9+cw9*mm-1.5*mm
            tx(c,vv2,px9,y-rh9+2*mm,'Sans-B',7,GD2 if ci2==0 else RC.white,'center' if al2=='c' else 'right')
            if ci2<len(tots9)-1: vl(c,xc9+cw9*mm,y-rh9,y,RC.HexColor('#1E3F5A'),0.4); xc9+=cw9*mm
        y-=rh9; bx(c,ML,y,CW,(tenure9+2)*rh9,fi=None,st2=BD,lw=0.6); y-=5*mm
        y=sec(c,ML,y,CW,"KEY FINANCIAL INSIGHTS & RECOMMENDATIONS")
        emc=R["cf"][0]["NetIncome"]/12; diff=R["profit25"]-L["profit25"]
        for cl10,ttl10,body10 in [
            (GN,"PAYBACK",f"Cash: {R['payback']} yrs | Loan: {L['payback']} yrs. Upfront {ff(L['dp'])} vs {ff(R['nc'])}."),
            (GD,"PROFITABILITY",f"Cash IRR {R['irr']}% vs Loan {L['irr']}%. 25yr diff: {fm(abs(int(diff)))} favour {'cash' if diff>0 else 'loan'}."),
            (RC.HexColor('#1A5276'),"EMI",f"Monthly solar ~{ff(int(emc))} vs EMI {ff(L['emi'])}. {'Fully covered Day 1.' if emc>=L['emi'] else 'Top-up needed early years.'}"),
            (RD,"INTEREST",f"Total interest {fm(L['tint'])} over {tenure9} yrs. Prepayment after Yr3 recommended."),
            (NV2,"RECOMMENDATION",f"SBI Surya Ghar @ {P.get('rate',9.15)}% most cost-effective. From Yr{tenure9+1} all solar = net surplus."),
        ]:
            if y<40*mm: break
            bx(c,ML,y-5.5*mm,3,5.5*mm,fi=cl10); tx(c,ttl10,ML+5*mm,y-1.2*mm,'Sans-B',7.5,cl10); y-=6.5*mm
            ws10=body10.split(); lb10,ls10="",[]
            for w10 in ws10:
                if len(lb10)+len(w10)+1<=112: lb10+=(" " if lb10 else "")+w10
                else: ls10.append(lb10); lb10=w10
            if lb10: ls10.append(lb10)
            for ln10 in ls10:
                if y<36*mm: break
                tx(c,ln10,ML+5*mm,y,'Sans',7.2,SL); y-=4.8*mm
            y-=2*mm
    if y>26*mm:
        bh10=min(y-15*mm,14*mm); bx(c,ML,14*mm,CW,bh10,fi=LT,st2=BD,lw=0.5)
        bx(c,ML,14*mm,3,bh10,fi=GD)
        dsc="DISCLAIMER: For indicative purposes only. Consult CEIG-certified installer and bank before final commitment."
        ws10=dsc.split(); lb10,ls10="",[]
        for w10 in ws10:
            if len(lb10)+len(w10)+1<=108: lb10+=(" " if lb10 else "")+w10
            else: ls10.append(lb10); lb10=w10
        if lb10: ls10.append(lb10)
        dy10=14*mm+bh10-5*mm; tx(c,"DISCLAIMER",ML+5*mm,dy10,'Sans-B',7,GD); dy10-=5*mm
        for ln10 in ls10:
            if dy10<15*mm: break
            tx(c,ln10,ML+5*mm,dy10,'Sans-I',6.5,MU); dy10-=4.5*mm
    c.save(); buf.seek(0); return buf.read()

# ══ MAIN ══════════════════════════════════════════════════════
def main():
    st.markdown("""<div class="main-hdr">
        <h1>☀ SolarYield India <span class="api-badge">NASA POWER API</span></h1>
        <p class="sub">Solar PV Simulator · Tilt/Azimuth · Load Profile · Inverter Sizing · Battery BESS · Bank Loan · Live Irradiance · PDF Report</p>
    </div>""", unsafe_allow_html=True)

    with st.sidebar:
        # ── 1. LOCATION & COORDINATES ──
        st.markdown("### 📍 Location & Coordinates")
        city_sel=st.selectbox("Select City",list(CITIES.keys()))
        city=CITIES[city_sel]
        if city_sel=="Custom Location":
            lat=st.number_input("Latitude (°N)",-35.0,38.0,20.59,0.01)
            lon=st.number_input("Longitude (°E)",68.0,98.0,78.96,0.01)
        else:
            lat=city["lat"]; lon=city["lon"]
            st.info(f"📌 **{lat:.3f}° N, {lon:.3f}° E**")

        # ── 2. NASA API ──
        st.markdown("### 🛰 NASA POWER — Live Irradiance")
        nasa_url=(f"https://power.larc.nasa.gov/api/temporal/climatology/point"
                  f"?parameters=ALLSKY_SFC_SW_DWN&community=RE"
                  f"&longitude={lon:.3f}&latitude={lat:.3f}&format=JSON")
        st.markdown(f'<span class="nasa-url">{nasa_url[:85]}…</span>',unsafe_allow_html=True)
        if st.button("🛰 Fetch NASA GHI Data",use_container_width=True):
            with st.spinner("Calling NASA POWER API..."):
                nr=fetch_nasa(lat,lon); st.session_state["nasa_res"]=nr
        nr=st.session_state.get("nasa_res",{})
        if nr.get("ok") and nr.get("ghi"):
            st.success(f"✅ NASA GHI: **{nr['ghi']} kWh/m²/day**")
            ghi=st.number_input("Use GHI (kWh/m²/day)",2.0,9.0,float(nr["ghi"]),0.01)
        else:
            if nr.get("err"): st.warning(f"API error: {nr['err']}")
            default_ghi=float(city.get("ghi",5.0))
            ghi=st.number_input("Daily GHI (kWh/m²/day)",2.0,9.0,default_ghi,0.01)

        # ── 3. TILT & AZIMUTH ──
        st.markdown("### 📐 Tilt & Azimuth")
        opt_tilt=round(abs(lat)*0.76+3.1,1)
        opt_tilt_int=int(round(opt_tilt))
        tilt=st.slider(f"Panel Tilt (°)  [Optimal ≈ {opt_tilt}°]",0,60,opt_tilt_int)
        azimuth=st.slider("Azimuth (° from North)  [180°=South]",90,270,180)
        tf_val=tilt_f(lat,tilt,azimuth)
        az_lbl={90:"East",135:"SE",180:"South",225:"SW",270:"West"}.get(azimuth,f"{azimuth}°")
        c_ta,c_tb=st.columns(2); c_ta.metric("POA Factor",f"{tf_val:.3f}"); c_tb.metric("Facing",az_lbl)
        if abs(tilt-opt_tilt)>10: st.warning(f"⚠️ Optimal {opt_tilt}° — ~{(1-tf_val)*100:.0f}% loss")
        else: st.success(f"✅ Good tilt | Factor: {tf_val:.3f}")

        # ── 4. SYSTEM ──
        st.markdown("### ⚙️ System Parameters")
        cap     =st.number_input("System Capacity (kWp)",0.5,500.0,10.0,0.5)
        cost_kw =st.number_input("Install Cost (Rs./kWp)",30000,80000,45000,1000)
        subsidy =st.number_input("PM Surya Ghar Subsidy (Rs.)",0,500000,94500,500)
        pr      =st.slider("Performance Ratio (%)",60,95,80)/100
        deg     =st.slider("Panel Degradation (%/yr)",0.1,1.0,0.5)/100

        # ── 5. INVERTER ──
        st.markdown("### 🔌 Inverter Sizing")
        inv_ratio=st.slider("DC/AC Sizing Ratio",1.00,1.40,1.15,0.01)
        inv_cap  =round(cap/inv_ratio,2)
        inv_type =st.selectbox("Inverter Type",["String Inverter","Central Inverter","Micro Inverter","Hybrid Inverter"])
        inv_eff  =st.slider("Inverter Efficiency (%)",94,99,97)/100
        num_inv  =math.ceil(cap/inv_cap) if inv_cap>0 else 1
        c_ia,c_ib=st.columns(2); c_ia.metric("Inverter Size",f"{inv_cap:.1f} kVA"); c_ib.metric("Units",str(num_inv))
        if 1.05<=inv_ratio<=1.30: st.success(f"✅ {inv_type} — {inv_cap:.1f} kVA × {num_inv}")
        elif inv_ratio<1.05: st.warning("⚠️ Ratio < 1.05: May underperform")
        else: st.warning("⚠️ Ratio > 1.30: Clipping on peak hours")

        # ── 6. LOAD ──
        st.markdown("### 🏠 Daily Load Profile")
        daily_load=st.number_input("Total Daily Load (kWh/day)",1.0,500.0,20.0,0.5)
        if st.toggle("Configure Appliance-wise Load"):
            total_app=0
            for aname,akw,ahr in APPLIANCES:
                hrs=st.slider(f"{aname}",0.0,24.0,float(ahr),0.5,key=f"ap_{aname}")
                total_app+=akw*hrs
            st.info(f"Total: **{total_app:.1f} kWh/day**"); daily_load=total_app
        sc_auto=min(0.98,daily_load/max(0.1,cap*ghi*tf_val*pr))
        sc=st.slider("Self Consumption (%)",30,98,int(min(98,max(30,sc_auto*100))))/100
        imp_t =st.number_input("Import Tariff (Rs./kWh)",2.0,15.0,float(city.get("tariff",6.5)),0.05)
        exp_t =st.number_input("Export FiT (Rs./kWh)",0.5,8.0,float(city.get("fit",3.82)),0.05)
        t_esc =st.slider("Tariff Escalation (%/yr)",0,8,3)/100

        # ── 7. BATTERY ──
        st.markdown("### 🔋 Battery Storage (BESS)")
        bat_on=st.toggle("Include Battery Storage")
        bat_cap=bat_eff=bat_dod=0; bat_type="Lithium-Ion (LFP)"
        if bat_on:
            bat_cap =st.number_input("Battery Capacity (kWh)",1.0,500.0,10.0,1.0)
            bat_type=st.selectbox("Battery Chemistry",list(BAT_DEFAULTS.keys()))
            bat_eff =st.slider("Round-Trip Efficiency (%)",70,98,BAT_DEFAULTS[bat_type]["eff"])/100
            bat_dod =st.slider("Depth of Discharge (%)",50,100,BAT_DEFAULTS[bat_type]["dod"])/100
            usb=round(bat_cap*bat_dod*bat_eff,2)
            bkh=round(usb/(daily_load/24),1) if daily_load>0 else 0
            c1b,c2b,c3b=st.columns(3)
            c1b.metric("Usable",f"{usb:.1f} kWh"); c2b.metric("Backup",f"{bkh:.1f} h"); c3b.metric("RTE",f"{bat_eff*100:.0f}%")
        else: bat_cap=0; bat_eff=0.9; bat_dod=0.8

        # ── 8. O&M ──
        st.markdown("### 💰 O&M & Financial")
        om0    =st.number_input("Annual O&M Yr 1 (Rs.)",500,100000,5000,500)
        om_esc =st.slider("O&M Escalation (%/yr)",0,8,4)/100
        inv_rep=st.number_input("Inverter Replacement (Rs.)",0,200000,40000,5000)
        disc   =st.slider("Discount Rate NPV (%)",4,15,8)

        # ── 9. LOAN ──
        st.markdown("### 🏦 Bank Loan Financing")
        loan_on=st.toggle("Enable Loan Financing",value=True)
        rate=9.15; tenure=7; dp_pct=20; bank_sel="SBI — Surya Ghar (3–10 kW)"
        if loan_on:
            bank_sel=st.selectbox("Bank / Scheme",list(BANKS.keys()),index=1)
            rate    =st.number_input("Interest Rate (% p.a.)",5.0,20.0,BANKS[bank_sel],0.05)
            tenure  =st.slider("Loan Tenure (Years)",1,15,7)
            dp_pct  =st.slider("Down Payment (%)",5,80,20)
            nc_p=cap*cost_kw-subsidy; dp_p=round(nc_p*dp_pct/100)
            rm_p=rate/100/12; nm_p=tenure*12
            emi_p=((nc_p-dp_p)*rm_p*(1+rm_p)**nm_p/((1+rm_p)**nm_p-1)) if rm_p>0 else (nc_p-dp_p)/nm_p
            st.success(f"**Down:** {inr(dp_p)}\n\n**Loan:** {inr(nc_p-dp_p)}\n\n**EMI: {inr(emi_p)}/month**")

        if st.button("⚡ Run Simulation",type="primary",use_container_width=True):
            with st.spinner("Simulating 25-year cashflow..."):
                R=simulate(cap,cost_kw,subsidy,ghi,pr,deg,imp_t,exp_t,t_esc,sc,
                           om0,om_esc,inv_rep,disc,loan_on,dp_pct,rate,tenure,
                           tf_val,bat_cap,bat_eff,bat_dod)
                st.session_state["results"]=R
                st.session_state["P"]=dict(
                    cap=cap,cost_kw=cost_kw,subsidy=subsidy,ghi=ghi,pr=pr,deg=deg,
                    imp_t=imp_t,exp_t=exp_t,t_esc=t_esc,sc=sc,om0=om0,om_esc=om_esc,
                    inv_rep=inv_rep,disc=disc,lat=lat,lon=lon,tilt=tilt,az=azimuth,
                    tf=tf_val,inv_cap=inv_cap,inv_ratio=inv_ratio,inv_type=inv_type,
                    bat_cap=bat_cap,bat_eff=bat_eff,bat_dod=bat_dod,bat_type=bat_type,
                    daily_load=daily_load,city=city_sel.split("(")[0].strip(),
                    state=city.get("state","India"),dp_pct=dp_pct,rate=rate,tenure=tenure,
                    bank=bank_sel)

    if "results" not in st.session_state:
        st.info("👈 Configure parameters in the sidebar and click **Run Simulation**")
        return

    R=st.session_state["results"]; L=R.get("loan"); P=st.session_state.get("P",{})
    nr=st.session_state.get("nasa_res",{})

    tabs=st.tabs(["📊 Overview","🛰 NASA API","📐 Tilt & Yield","🔌 Inverter & Load",
                  "🔋 Battery","📈 Cashflow","🏦 Loan","📉 Charts","📋 Amortization","📄 PDF Report"])

    # TAB 1 — OVERVIEW
    with tabs[0]:
        sh("CASH PURCHASE — KEY PERFORMANCE INDICATORS")
        c1,c2,c3,c4=st.columns(4)
        with c1: st.markdown(kpi(inr(R["nc"]),"Net Investment","After PM Subsidy"),unsafe_allow_html=True)
        with c2: st.markdown(kpi(f'{R["y1"]:,} kWh',"Year 1 Yield","Annual Generation","kpi-green"),unsafe_allow_html=True)
        with c3: st.markdown(kpi(f'{R["payback"]} Years',"Payback Period","Cash Purchase","kpi-blue"),unsafe_allow_html=True)
        with c4: st.markdown(kpi(f'{R["irr"]}%',"IRR — 25 Years","Internal Rate of Return","kpi-violet"),unsafe_allow_html=True)
        c5,c6,c7,c8=st.columns(4)
        with c5: st.markdown(kpi(f'Rs.{R["lcoe"]:.2f}/kWh',"LCOE","Levelised Cost of Energy"),unsafe_allow_html=True)
        with c6: st.markdown(kpi(inr(R["npv"]),"Net Present Value",f'@ {P.get("disc",8)}% Disc.',"kpi-green"),unsafe_allow_html=True)
        with c7: st.markdown(kpi(inr(R["profit25"]),"Net Profit 25yr","Cash Scenario","kpi-violet"),unsafe_allow_html=True)
        with c8: st.markdown(kpi(f'{P.get("ghi",ghi)} kWh/m²',"Daily GHI","NASA POWER","kpi-blue"),unsafe_allow_html=True)
        if L:
            sh("LOAN SCENARIO — KEY METRICS")
            l1,l2,l3,l4=st.columns(4)
            with l1: st.markdown(kpi(inr(L["dp"]),"Down Payment",f'{P.get("dp_pct",20)}% Upfront'),unsafe_allow_html=True)
            with l2: st.markdown(kpi(inr(L["emi"]),"Monthly EMI","Rs./Month","kpi-green"),unsafe_allow_html=True)
            with l3: st.markdown(kpi(f'{L["payback"]} Years',"Loan Payback","With Financing","kpi-blue"),unsafe_allow_html=True)
            with l4: st.markdown(kpi(f'{L["irr"]}%' if L["irr"] else "N/A","Loan IRR","25 Year","kpi-violet"),unsafe_allow_html=True)

    # TAB 2 — NASA
    with tabs[1]:
        sh("NASA POWER API — LIVE IRRADIANCE DATA")
        c_n1,c_n2=st.columns([2,1])
        with c_n1:
            st.markdown(f"""<div class="nasa-box">
                <h4>🛰 API Endpoint</h4>
                <span class="nasa-url">{P.get("lat",lat):.4f}°N, {P.get("lon",lon):.4f}°E — ALLSKY_SFC_SW_DWN | Community: RE | Format: JSON</span>
                <span class="nasa-url">https://power.larc.nasa.gov/api/temporal/climatology/point?parameters=ALLSKY_SFC_SW_DWN&community=RE&longitude={P.get("lon",lon):.4f}&latitude={P.get("lat",lat):.4f}&format=JSON</span>
            </div>""",unsafe_allow_html=True)
        with c_n2:
            st.metric("Latitude",f'{P.get("lat",lat):.4f}° N')
            st.metric("Longitude",f'{P.get("lon",lon):.4f}° E')
            st.metric("GHI Used",f'{P.get("ghi",ghi)} kWh/m²/day')
        if nr.get("ok") and nr.get("monthly"):
            sh("MONTHLY GHI — NASA POWER 30-YEAR CLIMATOLOGY")
            months=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
            mv=[nr["monthly"].get(str(i+1).zfill(2),0) for i in range(12)]
            fig_n=go.Figure(go.Bar(x=months,y=mv,
                marker_color=[f'rgba({180+int(v*5)},{130},{30},.85)' for v in mv],
                text=[f'{v:.2f}' for v in mv],textposition='outside'))
            fig_n.add_hline(y=nr["ghi"],line_dash="dash",line_color="#C9922A",
                annotation_text=f'Annual Avg: {nr["ghi"]} kWh/m²/day')
            fig_n.update_layout(title=f"Monthly GHI at ({P.get('lat',lat):.3f}°N, {P.get('lon',lon):.3f}°E)",
                yaxis_title="kWh/m²/day",plot_bgcolor="#F8FAFC",paper_bgcolor="#F8FAFC",height=380)
            st.plotly_chart(fig_n,use_container_width=True)
        else:
            st.info("👈 Click **Fetch NASA GHI Data** in sidebar to load live irradiance data")

    # TAB 3 — TILT
    with tabs[2]:
        sh("PANEL TILT & AZIMUTH OPTIMISATION")
        c_t1,c_t2=st.columns(2)
        with c_t1:
            tilts=[i*5 for i in range(13)]
            tfs2=[tilt_f(P.get("lat",lat),t,P.get("az",azimuth)) for t in tilts]
            fig_t=go.Figure()
            fig_t.add_trace(go.Scatter(x=tilts,y=[tf2*100 for tf2 in tfs2],
                name="POA Factor",line=dict(color="#C9922A",width=2.5)))
            fig_t.add_vline(x=P.get("tilt",tilt),line_dash="dash",line_color="#1A6B3C",
                annotation_text=f"Selected: {P.get('tilt',tilt)}°")
            fig_t.add_vline(x=round(abs(P.get("lat",lat))*0.76+3.1,1),line_dash="dot",
                line_color="#60A5FA",annotation_text="Optimal")
            fig_t.update_layout(title="Tilt Angle vs POA Factor",
                xaxis_title="Tilt (°)",yaxis_title="POA Factor (%)",
                plot_bgcolor="#F8FAFC",paper_bgcolor="#F8FAFC",height=350)
            st.plotly_chart(fig_t,use_container_width=True)
        with c_t2:
            azs=list(range(90,271,10))
            az_tfs=[tilt_f(P.get("lat",lat),P.get("tilt",tilt),a) for a in azs]
            fig_az=go.Figure(go.Scatter(x=azs,y=[a*100 for a in az_tfs],
                fill='tozeroy',fillcolor='rgba(201,146,42,.15)',
                line=dict(color="#C9922A",width=2.5)))
            fig_az.add_vline(x=P.get("az",azimuth),line_dash="dash",line_color="#1A6B3C",
                annotation_text=f"{P.get('az',azimuth)}°")
            fig_az.update_layout(title="Azimuth Direction vs Yield Factor",
                xaxis_title="Azimuth (° from North)",yaxis_title="Yield Factor (%)",
                plot_bgcolor="#F8FAFC",paper_bgcolor="#F8FAFC",height=350)
            st.plotly_chart(fig_az,use_container_width=True)
        c1t,c2t,c3t,c4t,c5t=st.columns(5)
        c1t.metric("Latitude",f'{P.get("lat",lat):.2f}°N')
        c2t.metric("Optimal Tilt",f'{round(abs(P.get("lat",lat))*0.76+3.1,1)}°')
        c3t.metric("Selected Tilt",f'{P.get("tilt",tilt)}°')
        c4t.metric("Azimuth",f'{P.get("az",azimuth)}°')
        c5t.metric("POA Factor",f'{P.get("tf",tf_val):.3f}')

    # TAB 4 — INVERTER & LOAD
    with tabs[3]:
        sh("INVERTER SIZING ANALYSIS")
        ci1,ci2,ci3,ci4=st.columns(4)
        ci1.metric("PV Array (DC)",f"{P.get('cap',cap)} kWp")
        ci2.metric("Inverter (AC)",f"{P.get('inv_cap',inv_cap):.1f} kVA")
        ci3.metric("DC/AC Ratio",f"{P.get('inv_ratio',inv_ratio):.2f}")
        ci4.metric("Inverter Eff.",f"{P.get('inv_eff',inv_eff)*100 if 'inv_eff' in P else 97:.0f}%")
        c_i1,c_i2=st.columns([1,2])
        with c_i1:
            ni=math.ceil(P.get("cap",cap)/P.get("inv_cap",inv_cap)) if P.get("inv_cap",inv_cap)>0 else 1
            st.markdown(f"""<div class="inv-box">
                <h3 style="color:#6366F1;margin:0">{P.get("inv_type",inv_type)}</h3>
                <p style="font-size:2rem;font-weight:800;color:#4F46E5;margin:.5rem 0">{P.get("inv_cap",inv_cap):.1f} kVA</p>
                <p style="color:#6B7280">× {ni} unit(s) | Ratio: {P.get("inv_ratio",inv_ratio):.2f}</p>
            </div>""",unsafe_allow_html=True)
        with c_i2:
            ratio=P.get("inv_ratio",inv_ratio)
            clip="Low ✅" if ratio<=1.20 else ("Medium ⚠️" if ratio<=1.30 else "High ❌")
            st.dataframe(pd.DataFrame({"Parameter":["PV Array","Inverter AC","DC/AC Ratio","No. of Units","Clipping Risk"],
                "Value":[f"{P.get('cap',cap)} kWp",f"{P.get('inv_cap',inv_cap):.1f} kVA",
                         f"{ratio:.2f}",str(ni),clip]}),use_container_width=True,hide_index=True)
        sh("DAILY LOAD PROFILE")
        c_l1,c_l2=st.columns([1,2])
        with c_l1:
            dl=P.get("daily_load",daily_load); dg=R["y1"]/365
            st.metric("Daily Load",f"{dl:.1f} kWh/day")
            st.metric("Daily Generation",f"{dg:.1f} kWh/day")
            st.metric("Self Consumption",f"{P.get('sc',sc)*100:.0f}%")
            st.metric("Daily Export",f"{max(0,dg*(1-P.get('sc',sc))):.1f} kWh")
        with c_l2:
            hrs=list(range(24))
            lc=[dl/24*(0.5 if h in range(1,6) else 1.8 if h in range(7,10) else 1.2 if h in range(10,17) else 1.6 if h in range(17,22) else 0.8) for h in hrs]
            ln=sum(lc); lc=[v/ln*dl for v in lc]
            gc=[0 if h<6 or h>18 else R["y1"]/365*math.sin(math.pi*(h-6)/12) for h in hrs]
            fig_ld=go.Figure()
            fig_ld.add_trace(go.Scatter(x=hrs,y=lc,name="Load",fill='tozeroy',
                fillcolor='rgba(239,68,68,.15)',line=dict(color="#EF4444",width=2)))
            fig_ld.add_trace(go.Scatter(x=hrs,y=gc,name="Solar Gen",fill='tozeroy',
                fillcolor='rgba(201,146,42,.15)',line=dict(color="#C9922A",width=2)))
            fig_ld.update_layout(title="Daily Load vs Solar Generation (Indicative)",
                xaxis_title="Hour",yaxis_title="kWh",height=340,
                xaxis=dict(tickmode='array',tickvals=list(range(0,24,3)),
                           ticktext=[f"{h:02d}:00" for h in range(0,24,3)]),
                plot_bgcolor="#F8FAFC",paper_bgcolor="#F8FAFC",
                legend=dict(bgcolor="rgba(0,0,0,0)"))
            st.plotly_chart(fig_ld,use_container_width=True)

    # TAB 5 — BATTERY
    with tabs[4]:
        sh("BATTERY STORAGE (BESS) ANALYSIS")
        if not P.get("bat_cap",0) or P.get("bat_cap",0)<=0:
            st.info("🔋 Enable **Battery Storage** in the sidebar to see BESS analysis.")
            for txt in ["✅ Increase self-consumption from ~75% to 90%+",
                        "✅ Backup power during grid outages",
                        "✅ Shift excess solar to evening peak hours",
                        "✅ EV charging optimisation"]:
                st.markdown(f"**{txt}**")
        else:
            bc=P.get("bat_cap",0); be=P.get("bat_eff",0.9); bd=P.get("bat_dod",0.8)
            dl2=P.get("daily_load",daily_load); dg2=R["y1"]/365
            usb2=bc*bd*be; bkh2=round(usb2/(dl2/24),1) if dl2>0 else 0
            exc2=max(0,dg2*(1-P.get("sc",sc)))
            cyc=min(365,round(exc2/usb2*365,0)) if usb2>0 else 0
            c_b1,c_b2,c_b3,c_b4=st.columns(4)
            c_b1.metric("Battery",f"{bc} kWh"); c_b2.metric("Usable",f"{usb2:.1f} kWh")
            c_b3.metric("Backup",f"{bkh2:.1f} hrs"); c_b4.metric("Cycles/yr",f"{cyc:.0f}")
            c_bx1,c_bx2=st.columns([1,2])
            with c_bx1:
                st.markdown(f"""<div class="bat-box">
                    <h3 style="color:#16A34A;margin:0">{P.get("bat_type","Lithium-Ion (LFP)")}</h3>
                    <p style="font-size:2.5rem;font-weight:800;color:#15803D;margin:.5rem 0">{bc} kWh</p>
                    <p style="color:#166534">RTE: {be*100:.0f}% | DoD: {bd*100:.0f}%</p>
                    <p style="color:#166534">Usable: {usb2:.1f} kWh/cycle</p>
                </div>""",unsafe_allow_html=True)
            with c_bx2:
                hrs2=list(range(25)); soc=[50.0]
                for h in range(24):
                    gh=0 if h<6 or h>18 else dg2*math.sin(math.pi*(h-6)/12)
                    lh=dl2/24*(0.5 if h in range(1,6) else 1.8 if h in range(7,10) else 1.2 if h in range(10,17) else 1.6 if h in range(17,22) else 0.8)
                    ns=max(100*(1-bd),min(100,soc[-1]+(gh-lh)*be/bc*100 if bc>0 else soc[-1]))
                    soc.append(ns)
                fig_b=go.Figure()
                fig_b.add_trace(go.Scatter(x=hrs2,y=soc,name="Battery SoC",fill='tozeroy',
                    fillcolor='rgba(22,163,74,.15)',line=dict(color="#16A34A",width=2.5)))
                fig_b.add_hline(y=(1-bd)*100,line_dash="dash",line_color="#EF4444",annotation_text="Min SoC (DoD)")
                fig_b.add_hline(y=100,line_dash="dot",line_color="#C9922A",annotation_text="Full Charge")
                fig_b.update_layout(title="Battery State of Charge — 24 Hours (Indicative)",
                    xaxis_title="Hour",yaxis_title="SoC (%)",yaxis=dict(range=[0,110]),
                    xaxis=dict(tickmode='array',tickvals=list(range(0,25,3)),
                               ticktext=[f"{h:02d}:00" for h in range(0,25,3)]),
                    plot_bgcolor="#F8FAFC",paper_bgcolor="#F8FAFC",height=370)
                st.plotly_chart(fig_b,use_container_width=True)

    # TAB 6 — CASHFLOW
    with tabs[5]:
        sh("25-YEAR ENERGY & FINANCIAL PERFORMANCE TABLE")
        df=pd.DataFrame(R["cf"])
        df["O&M"]=df.apply(lambda r:inr(r["OM"],False)+(f' + {inr(r["Extra"],False)}' if r["Extra"] else ''),axis=1)
        df["Bill Saved"]=df["BillSaved"].apply(lambda v:inr(v,False))
        df["Export"]=df["ExportRev"].apply(lambda v:inr(v,False))
        df["Net"]=df["NetIncome"].apply(lambda v:inr(v,False))
        df["Cumul."]=df["Cumulative"].apply(lambda v:inr(v,False))
        df["Tariff"]=df["Tariff"].apply(lambda v:f"Rs.{v:.2f}")
        disp=df[["Year","Yield","Tariff","Bill Saved","Export","O&M","Net","Cumul.","EffSC"]].copy()
        disp.columns=["Year","Yield kWh","Tariff","Bill Saved","Export Rev","O&M","Net Income","Cumulative","SC %"]
        def hr(row):
            if row["Year"]==12: return ['background-color:#FEF3C7']*len(row)
            if R.get("payback") and row["Year"]==R["payback"]: return ['background-color:#D1FAE5']*len(row)
            return ['']*len(row)
        st.dataframe(disp.style.apply(hr,axis=1),use_container_width=True,hide_index=True,height=580)
        st.caption("🟡 Yr 12=Inverter replacement  🟢 Cash payback  SC%=Effective Self-Consumption with Battery")
        st.download_button("⬇ Download CSV",disp.to_csv(index=False),"solaryield_cashflow.csv","text/csv")

    # TAB 7 — LOAN
    with tabs[6]:
        if not L: st.info("Enable Bank Loan in the sidebar.")
        else:
            sh("LOAN vs CASH — DETAILED COMPARISON")
            cdf=pd.DataFrame([
                ["Upfront Investment",inr(R["nc"]),inr(L["dp"])],
                ["Loan Amount","—",inr(L["lamt"])],["Monthly EMI","—",inr(L["emi"])],
                ["Interest Rate","—",f'{P.get("rate",rate)}% p.a.'],
                ["Loan Tenure","—",f'{P.get("tenure",tenure)} Years'],
                ["Total Interest","—",inr(L["tint"])],["Total Outflow",inr(R["nc"]),inr(L["tpaid"])],
                ["Payback Period",f'{R["payback"]} Yrs',f'{L["payback"]} Yrs'],
                ["25yr Net Profit",inr(R["profit25"]),inr(L["profit25"])],
                ["IRR 25yr",f'{R["irr"]}%',f'{L["irr"]}%' if L["irr"] else "N/A"],
                [f'NPV @ {P.get("disc",8)}%',inr(R["npv"]),inr(L["npv"])],
            ],columns=["Metric","Cash Purchase","Loan Financing"])
            st.dataframe(cdf,use_container_width=True,hide_index=True)
            emc=R["cf"][0]["NetIncome"]/12; diff=R["profit25"]-L["profit25"]
            insight("📊 Payback",f"Cash: {R['payback']} yrs. Loan: {L['payback']} yrs. Upfront {inr(L['dp'])} vs {inr(R['nc'])}.")
            insight("💹 IRR",f"Cash IRR {R['irr']}% vs Loan IRR {L['irr']}%. 25yr diff: {inr(abs(int(diff)))}.")
            insight("🏦 EMI",f"Monthly solar ~{inr(int(emc))} vs EMI {inr(L['emi'])}. {'✅ Covered Day 1.' if emc>=L['emi'] else '⚠️ Top-up needed.'}")

    # TAB 8 — CHARTS
    with tabs[7]:
        yrs=[r["Year"] for r in R["cf"]]
        c1c,c2c=st.columns(2)
        with c1c:
            fig1=go.Figure(go.Bar(x=yrs,y=[r["Yield"] for r in R["cf"]],
                marker_color=[f'rgba({180+i*2},{130},{30},.85)' for i in range(25)]))
            fig1.update_layout(title="25-Year Solar Generation (kWh)",height=320,
                plot_bgcolor="#F8FAFC",paper_bgcolor="#F8FAFC")
            st.plotly_chart(fig1,use_container_width=True)
        with c2c:
            fig2=go.Figure()
            fig2.add_trace(go.Scatter(x=yrs,y=[r["Cumulative"] for r in R["cf"]],name="Cash",
                fill='tozeroy',fillcolor='rgba(26,107,60,.15)',line=dict(color="#1A6B3C",width=2.5)))
            if L: fig2.add_trace(go.Scatter(x=yrs,y=[r["Cumulative"] for r in L["lcf"]],
                name="Loan",line=dict(color="#C9922A",width=2.5,dash="dash")))
            fig2.add_hline(y=0,line_color="#334155",line_width=1)
            fig2.update_layout(title="Cumulative Cashflow (Rs.)",height=320,
                plot_bgcolor="#F8FAFC",paper_bgcolor="#F8FAFC",legend=dict(bgcolor="rgba(0,0,0,0)"))
            st.plotly_chart(fig2,use_container_width=True)
        c3c,c4c=st.columns(2)
        with c3c:
            ni=[r["NetIncome"] for r in R["cf"]]
            fig3=go.Figure(go.Bar(x=yrs,y=ni,marker_color=["#1A6B3C" if v>=0 else "#8B1A1A" for v in ni]))
            fig3.update_layout(title="Annual Net Income (Rs.)",height=300,
                plot_bgcolor="#F8FAFC",paper_bgcolor="#F8FAFC")
            st.plotly_chart(fig3,use_container_width=True)
        with c4c:
            if L:
                nb=[r["NetBenefit"] for r in L["lcf"]]
                fig4=go.Figure(go.Bar(x=yrs,y=nb,marker_color=["#1A6B3C" if v>=0 else "#8B1A1A" for v in nb]))
                fig4.update_layout(title="Net Benefit — Loan Scenario (Rs.)",height=300,
                    plot_bgcolor="#F8FAFC",paper_bgcolor="#F8FAFC")
                st.plotly_chart(fig4,use_container_width=True)

    # TAB 9 — AMORTIZATION
    with tabs[8]:
        if not L: st.info("Enable Bank Loan in the sidebar.")
        else:
            sh("ANNUAL AMORTIZATION SUMMARY")
            tenure_v=P.get("tenure",tenure); amr=[]
            for yr in range(1,tenure_v+1):
                sl=L["amort"][(yr-1)*12:yr*12]
                amr.append({"Loan Year":yr,"Annual EMI":inr(sum(m["EMI"] for m in sl),False),
                    "Principal":inr(sum(m["Principal"] for m in sl),False),
                    "Interest":inr(sum(m["Interest"] for m in sl),False),
                    "Closing Bal":inr(sl[-1]["Balance"],False),
                    "Solar Income":inr(L["lcf"][yr-1]["SolarIncome"],False),
                    "Net Benefit":inr(L["lcf"][yr-1]["NetBenefit"],False)})
            st.dataframe(pd.DataFrame(amr),use_container_width=True,hide_index=True)
            c_a1,c_a2,c_a3=st.columns(3)
            c_a1.metric("Total EMI Paid",inr(L["tpaid"]-L["dp"])); c_a2.metric("Total Interest",inr(L["tint"])); c_a3.metric("Total Outflow",inr(L["tpaid"]))
            fig5=make_subplots(specs=[[{"secondary_y":True}]])
            mns=[m["Month"] for m in L["amort"]]
            fig5.add_trace(go.Bar(x=mns,y=[m["Principal"] for m in L["amort"]],name="Principal",marker_color="#1A6B3C"),secondary_y=False)
            fig5.add_trace(go.Bar(x=mns,y=[m["Interest"] for m in L["amort"]],name="Interest",marker_color="#8B1A1A"),secondary_y=False)
            fig5.add_trace(go.Scatter(x=mns,y=[m["Balance"] for m in L["amort"]],name="Balance",line=dict(color="#C9922A",width=2)),secondary_y=True)
            fig5.update_layout(barmode="stack",xaxis_title="Month",
                plot_bgcolor="#F8FAFC",paper_bgcolor="#F8FAFC",
                legend=dict(bgcolor="rgba(0,0,0,0)"),height=350)
            st.plotly_chart(fig5,use_container_width=True)

    # TAB 10 — PDF REPORT
    with tabs[9]:
        sh("GENERATE PREMIUM 5-PAGE PDF FEASIBILITY REPORT")
        c_r1,c_r2=st.columns([1,1])
        with c_r1:
            st.markdown("#### 📋 Report Details")
            client_name=st.text_input("Client / Applicant Name","M/s Sunrise Infra Pvt. Ltd.")
            report_ref =st.text_input("Report Reference No.","SYI/2025-26/KA/0042")
            bank_name  =st.text_input("Bank / Scheme",P.get("bank","SBI Surya Ghar") if P.get("bank") else "N/A")
        with c_r2:
            st.markdown("#### 📄 Report Contains")
            st.markdown("""
- ✅ **Page 1** — Cover: Coordinates, Tilt, Inverter, Battery
- ✅ **Page 2** — Executive Summary + Technical Parameters
- ✅ **Page 3** — 25-Year Cashflow Table (colour-coded)
- ✅ **Page 4** — Bank Loan Analysis & Cash vs Loan
- ✅ **Page 5** — Amortization + Recommendations + Disclaimer
""")
            st.info(f"**{P.get('cap',cap)} kWp | {P.get('city','')} | Tilt {P.get('tilt',tilt)}° | GHI {P.get('ghi',ghi)} | IRR {R['irr']}%**")
        st.markdown("---")
        if st.button("📄 Generate & Download PDF Report",type="primary",use_container_width=True):
            with st.spinner("Generating 5-page Indian corporate PDF..."):
                inp={**P,"client":client_name,"ref":report_ref,"bank":bank_name,
                     "dp_pct":P.get("dp_pct",dp_pct),"rate":P.get("rate",rate),
                     "tenure":P.get("tenure",tenure)}
                try:
                    pdf=gen_pdf(R,inp); ref2=report_ref.replace("/","-")
                    st.success("✅ PDF generated!")
                    st.download_button("⬇ Download PDF Report",data=pdf,
                        file_name=f"SolarYield_{P.get('city','')}_{ref2}.pdf",
                        mime="application/pdf",use_container_width=True)
                except Exception as e:
                    st.error(f"PDF error: {e}"); st.exception(e)

    st.markdown("""<div class="disc-box">
        <b>DISCLAIMER:</b> For indicative purposes only. Actual yield depends on site conditions.
        Tariffs, bank rates and subsidies subject to revision. Consult CEIG-certified installer and bank before commitment.
        PM Surya Ghar subject to MNRE/DISCOM approval. SolarYield India Pvt. Ltd. · v4.0 · Powered by NASA POWER API
    </div>""",unsafe_allow_html=True)

if __name__=="__main__":
    main()
