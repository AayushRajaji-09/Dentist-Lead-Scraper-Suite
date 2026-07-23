# 🚀 Antigravity Lead Scraper Suite v3.1 — Matrix Edition

A multi-category, automated B2B lead generation and profiling suite covering **30 major Indian cities × 20 commercial areas each**. Features a stunning **Matrix-aesthetic GUI** with falling Katakana rain, real-time color-coded console, OS-adaptive system optimization, and persistent per-city deduplication.

Supports 4 business categories: **Dentists · Real Estate Agents · Salons · CA / Accountants**

---

## 📁 Repository Structure

```
Dentist-Lead-Scraper-Suite/
  ├── main.py                              ← Master launcher (GUI or CLI)
  ├── src/
  │    ├── gui/
  │    │    └── dentist_lead_suite_gui.py  ← Matrix UI (Tkinter) — main interface
  │    ├── scraper/
  │    │    ├── categories.py             ← Category config (4 categories)
  │    │    └── free_dentist_scraper.py   ← Headless CLI scraper engine
  │    └── utils/
  │         ├── helpers.py                ← [NEW v3.1] Shared utilities (Excel save, email regex, name parser)
  │         ├── system_optimizer.py       ← [NEW v3.1] OS/CPU auto-tuning & profile engine
  │         └── run_logger.py             ← Git telemetry, metrics logger & dedup registry
  ├── docs/
  │    └── HOW_TO_USE.md                  ← Full user manual
  ├── output/                             ← Exported .xlsx lead files & dedup registries go here
  ├── requirements.txt
  └── README.md
```

---

## 🟢 Quickstart

```powershell
# 1. Install dependencies
pip install -r requirements.txt
playwright install chromium

# 2. Launch the Matrix GUI (v3.1)
python main.py

# 3. Or run the headless CLI scraper
python main.py --cli
```

---

## ✨ v3.1 — What's New

| Feature | Details |
|---|---|
| 🧠 **System Auto-Optimizer** | Probes host OS (Windows/macOS/Linux), CPU cores & screen size; auto-activates TURBO/BALANCED/ECO mode |
| 🔁 **Smart Deduplication** | Persistent MD5 lead fingerprinting per city (`seen_leads_<City>.json`) — prevents duplicate leads across separate runs |
| 🎛️ **Force Re-Scrape Option** | Toggle checkbox in GUI settings panel to clear deduplication registry for clean re-scraping |
| 🏙️ **30 Cities × 20 Areas** | Expanded 30-city India coverage (600 commercial hubs pre-configured) |
| 📍 **City & Area Picker** | Dropdown + multi-select checkboxes + custom area add button |
| 🗂️ **4 Business Categories** | Dentists, Real Estate Agents, Salons, CA / Accountants |
| 🌧️ **Matrix Rain UI** | Animated falling Katakana header banner |
| 🎨 **Full Dark Theme** | Black `#000000` background with high-contrast Matrix green `#00FF41` |
| 📡 **Discord Team Telemetry** | Optional Discord webhook integration for live mission completion alerts |

---

*(For detailed column definitions, setup guide, and outreach strategy, read **[`docs/HOW_TO_USE.md`](docs/HOW_TO_USE.md)**.)*
