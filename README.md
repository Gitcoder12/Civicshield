# CivicShield 🛡️

**Food Safety, Made Public.**

A citizen-powered food safety transparency platform for Hyderabad — combining FSSAI license verification, anonymous citizen reports, official inspector audits, and dish safety ratings in one working demo.

> M.Tech Project · Computer Science & Engineering · Amity University Hyderabad · Mar 2026
> **D Satvik (15) · C Ajay (32)** · Guide: Dr Ratnanjali Tiwari

---

## Live Demo

Open `index.html` directly in any browser. No server, no setup, no installation required.

---

## What It Does

| Feature | Description |
|---|---|
| **FSSAI Verification** | 14-digit license number and validity status per venue |
| **Area Safety Heatmap** | 15 Hyderabad areas color-coded by average safety score |
| **Citizen Reports** | Anonymous 11-item hygiene checklist with adulteration alerts |
| **Inspector Audits** | Official FSSAI inspector reports with public attribution |
| **Dish Ratings** | Best dishes, healthy options, popular picks per venue |
| **Chain Branches** | All branches ranked — best branch auto-highlighted |
| **Owner Contacts** | Public contact info per establishment |
| **Healthy Filter** | One-click filter for venues with healthy menu options |

---

## Dataset

- **114 venues** across **15 Hyderabad areas**
- Areas: Banjara Hills, Jubilee Hills, Hitech City, Gachibowli, Kukatpally, Ameerpet, Secunderabad, Begumpet, Charminar, Abids, LB Nagar, Dilsukhnagar, Uppal, Kondapur, Himayatnagar
- **65 FSSAI verified** · **8 expired** · **19 unregistered**
- **8 named FSSAI inspectors** with designations and audit verdicts
- **14 restaurant chains** with branch comparison
- **400+ dishes** catalogued with best/healthy/popular tags

---

## Project Structure

```
CivicShield/
├── index.html          # Complete self-contained demo (no build step)
├── backend_app.py      # Flask REST API (for production deployment)
├── hotels.json         # Venue dataset
└── README.md
```

---

## Running the Demo

**Browser (instant — no setup):**
```bash
# Just open index.html in Chrome, Firefox, or Edge
```

**Flask backend (production):**
```bash
pip install flask flask-cors
python backend_app.py
# API at http://localhost:5000
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5 · CSS3 · Vanilla JavaScript |
| Fonts | Montserrat (body) · Syne (headings) |
| Backend | Python · Flask · Flask-CORS |
| Database | JSON (demo) → PostgreSQL (production) |
| Data Source | FSSAI FOSCOS API · Manual curation |

---

## ICEDIP Model

| Phase | Action | Outcome |
|---|---|---|
| **I — Identify** | Mapped India's food safety reporting gap | 87,000+ annual complaints, <2% resolved publicly |
| **C — Collect** | FSSAI FOSCOS API, Hyderabad venue data | 114 venues, 400+ dishes, 8 inspectors |
| **E — Evaluate** | Assessed Zomato, Swiggy, FSSAI portal | No platform merges citizen + inspector + FSSAI |
| **D — Design** | Flask + PostgreSQL, dual reporting UI | Orange-red civic palette, FSSAI blocks per venue |
| **I — Implement** | Full working browser demo | Heatmap, chain tracking, dish ratings, reports |
| **P — Promote** | M.Tech poster, AUH Mar 2026 | GitHub open source, India-wide roadmap |

---

## Scaling Roadmap

```
Phase 1 (Now)      → Hyderabad demo, 114 venues, static HTML      ✓ Done
Phase 2 (3-6 mo)   → Flask + PostgreSQL, city selector, live API
Phase 3 (6-18 mo)  → India-wide, crowd-sourced, mobile app
Phase 4 (18+ mo)   → Global, FDA/FSA APIs, AI violation detection
```

---

## FSSAI License Status

| Status | Meaning |
|---|---|
| 🟢 Active | Valid license, number displayed publicly |
| 🟡 Expired | License exists, renewal overdue |
| 🔴 Unregistered | Operating without mandatory FSSAI registration |

Live verification via **FSSAI FOSCOS Open API**: `foscos.fssai.gov.in`

---

## Report System

| Reporter | Identity | Checklist |
|---|---|---|
| Citizen | **Anonymous** | 11-item hygiene checklist |
| FSSAI Inspector | **Public** (name + ID + designation) | 12-item audit + official verdict |

---

## License

MIT — open source, free to use and extend.

---

**D Satvik** · [github.com/gitcoder12](https://github.com/gitcoder12) · M.Tech CSE, Amity University Hyderabad
