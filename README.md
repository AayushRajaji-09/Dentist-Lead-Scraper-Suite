# 🚀 Antigravity Lead Scraper Suite v3.0 — Matrix Edition

A multi-category, automated B2B lead generation and profiling suite covering **30 major Indian cities × 20 commercial areas each**. Features a stunning **Matrix-aesthetic GUI** with falling Katakana rain, real-time color-coded console, and an interactive City & Area picker dialog.

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
  │    │    ├── categories.py             ← [NEW v3.0] Category config (4 categories)
  │    │    └── free_dentist_scraper.py   ← Headless CLI scraper engine
  │    └── utils/
  │         └── run_logger.py             ← Git telemetry & metrics logger
  ├── docs/
  │    └── HOW_TO_USE.md                  ← Full user manual
  ├── output/                             ← Exported .xlsx lead files go here
  ├── requirements.txt
  └── README.md
```

---

## 🟢 Quickstart

```powershell
# 1. Install dependencies
pip install -r requirements.txt
playwright install chromium

# 2. Launch the Matrix GUI
python main.py

# 3. Or run the headless CLI scraper
python main.py --cli
```

---

## ✨ v3.0 — What's New

| Feature | Details |
|---|---|
| 🏙️ **30 Cities × 20 Areas** | Expanded from 10 cities to full 30-city India coverage |
| 📍 **City & Area Picker Dialog** | Click to open — dropdown + checkboxes + custom area entry |
| 🗂️ **4 Scraping Categories** | Dentists, Real Estate Agents, Salons, CA/Accountants |
| 🌧️ **Matrix Rain UI** | Falling Katakana animation on the header canvas |
| 🎨 **Full Dark Theme** | Black `#000000` bg, Matrix green `#00FF41` throughout |
| 🖥️ **Color-coded Console** | 6 log tags: success / bright / warning / error / save / dim |
| 📊 **Live Status Bar** | SYS · LEADS · AREA · CLOCK — all live updated |
| ✏️ **Custom Area Entry** | Add any area not in the preset list from the picker dialog |
| 📡 **Discord Team Telemetry** | Optional `config.json` integration to send rich embed run summaries to Discord |

---

*(For detailed column definitions, setup guide, and outreach strategy, read **[`docs/HOW_TO_USE.md`](docs/HOW_TO_USE.md)**.)*
