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
    tabs = st.tabs(["📊 Overview", "📈 Cashflow Table", "🏦 Loan Analysis", "📉 Charts", "📋 Amortization"])

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
