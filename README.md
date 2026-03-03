# ☀️ SolarYield India — Advanced PV Energy Dashboard

A fully client-side, single-file solar PV yield and financial calculator built for India. No server needed — runs entirely in the browser.

**🌐 Live Demo:** [https://YOUR-USERNAME.github.io/solar-yield-india](https://YOUR-USERNAME.github.io/solar-yield-india)

---

## ✨ Features

### ⚡ PV Yield Engine
- Solar capacity (kWp), panel efficiency, system losses
- Tilt angles for all 4 orientations (N / S / E / W) with correction factors
- Inverter size & efficiency with clipping detection
- Battery storage flow modelling

### 📍 Location & Irradiance
- **25 Indian cities** pre-loaded with monthly GHI data
- **NASA POWER live API** — real 2019–2023 irradiance for any lat/lon
- Manual coordinate entry for any location in India

### ₹ State-wise Electricity Tariffs
Auto-fills **import tariff** and **solar export FiT (net metering rate)** for every city:

| State | Import (₹/kWh) | Export FiT (₹/kWh) | Source |
|---|---|---|---|
| Delhi | 6.50 | 3.50 | DERC 2024-25 |
| Maharashtra | 9.00 | 2.90 | MSEDCL 2024-25 |
| Karnataka | 6.50 | 3.82 | BESCOM 2024-25 |
| Tamil Nadu | 5.00 | 3.10 | TANGEDCO 2024-25 |
| Gujarat | 5.50 | 2.25 | GUVNL 2024-25 |
| Rajasthan | 6.50 | 3.26 | JVVNL 2024-25 |
| Telangana | 6.00 | 2.80 | TSSPDCL 2024-25 |
| Kerala | 5.50 | 3.15 | KSEB 2023-24 |
| West Bengal | 7.50 | 2.09 | WBSEDCL 2024-25 |
| ...and more | | | |

### 🏦 Bank Loan Financing
9 Indian banks with real 2024-25 solar loan rates:
- **SBI Surya Ghar** — 7.0% (≤3kW) / 9.15% (3–10kW)
- Punjab National Bank — 9.5%
- Bank of Baroda — 10.0%
- IDBI Surya Shakti — 10.5%
- Union Bank, ICICI, HDFC + Custom rate

Full amortization schedule, Loan vs Cash comparison, annual net benefit chart.

### 📊 5-Tab Dashboard
| Tab | Contents |
|---|---|
| **Overview** | KPIs, energy flow diagram, monthly yield chart, gauges, losses table |
| **Hourly Profile** | 24-hour solar + load + battery + export canvas chart, hour-by-hour table |
| **Financial ROI** | 25-year cashflow with tariff escalation, IRR, LCOE, payback, year-by-year table |
| **Loan Analysis** | EMI, amortization, loan vs cash comparison, net benefit bar chart |
| **CO₂ Impact** | Annual/25yr CO₂ avoided, tree/homes/petrol equivalents |

### 📄 PDF Export
Dark-themed professional report with all KPIs, financial summary, energy flow, monthly chart.

---

## 🚀 Deployment

### GitHub Pages (Recommended)
```bash
git clone https://github.com/YOUR-USERNAME/solar-yield-india.git
cd solar-yield-india
# Push to main branch, then enable Pages in repo Settings → Pages → Deploy from branch: main
```

### Netlify (Drag & Drop)
1. Go to [netlify.com](https://netlify.com)
2. Drag the `index.html` file onto the deploy zone
3. Get instant URL like `https://solar-yield-india.netlify.app`

### Vercel
```bash
npm i -g vercel
vercel --yes
```

### Self-hosted / Local
```bash
# Just open index.html in any browser — no server needed!
open index.html
```

---

## 📁 Project Structure

```
solar-yield-india/
├── index.html          # Complete app (single file, ~92KB)
├── README.md           # This file
├── LICENSE             # MIT License
├── .gitignore
└── .github/
    └── workflows/
        └── deploy.yml  # Auto-deploy to GitHub Pages on push
```

---

## 🔧 Tech Stack

| Component | Technology |
|---|---|
| Frontend | Vanilla HTML5 / CSS3 / JavaScript |
| Charts | HTML5 Canvas (custom) |
| PDF Export | [jsPDF](https://github.com/parallax/jsPDF) (CDN) |
| Fonts | Google Fonts (Syne + JetBrains Mono) |
| Irradiance API | [NASA POWER](https://power.larc.nasa.gov/) |
| Deployment | GitHub Pages / Netlify / Vercel |

**Zero build step. Zero dependencies to install. Zero backend.**

---

## 🌦 NASA POWER API

The app uses the free [NASA POWER API](https://power.larc.nasa.gov/) to fetch real monthly solar irradiance:
```
GET https://power.larc.nasa.gov/api/temporal/monthly/point
  ?parameters=ALLSKY_SFC_SW_DWN
  &community=RE
  &longitude={lon}&latitude={lat}
  &format=JSON&start=2019&end=2023
```
No API key required.

---

## 📜 Data Sources

- **Irradiance**: NASA POWER / Built-in monthly GHI averages
- **Electricity Tariffs**: State DISCOM tariff orders FY2024-25 (DERC, MSEDCL, BESCOM, TANGEDCO, GUVNL, etc.)
- **Solar Export FiT**: State net-metering regulations & APPC rates 2024
- **Loan Rates**: SBI Surya Ghar scheme, bank websites FY2024-25
- **CO₂ Factor**: CEA Grid Emission Factor 2023-24 (0.716 kg CO₂/kWh)

---

## ⚠️ Disclaimer

This tool provides estimates for planning purposes. Actual yield and savings depend on local shading, soiling, equipment degradation, utility tariff revisions, and installation quality. Consult a certified solar installer for detailed system design and a financial advisor for investment decisions.

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

## 🤝 Contributing

PRs welcome! Areas for improvement:
- More cities / states
- Real-time tariff API integration
- Bifacial panel modelling
- String sizing calculator
- Export to Excel
