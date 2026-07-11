# 🚀 Antigravity Dentist Lead Scraper Suite v2.0

An automated, customizable B2B lead generation and profiling suite across 10+ major Indian cities (`Ahmedabad`, `Mumbai`, `Surat`, `Pune`, `Bangalore`, `Delhi`, `Hyderabad`, `Kolkata`, `Chennai`, `Jaipur`). Equipped with an interactive GUI (`tkinter`), deep Google Maps extraction (`Ratings`, `Reviews`, `Ad Status`, `Website` checks), auto-discovery vectors, and automated Git telemetry.

---

## 📁 Repository Organization & Functionality

```
Dentist-Lead-Scraper-Suite/
  ├── main.py                          ← Master entry point launcher (CLI or GUI)
  ├── src/
  │    ├── gui/
  │    │    └── dentist_lead_suite_gui.py     ← Tkinter Interactive Dashboard
  │    ├── scraper/
  │    │    └── free_dentist_scraper.py       ← Headless Playwright Scraper Engine
  │    └── utils/
  │         └── run_logger.py                 ← Git Telemetry & Metrics Logger
  ├── docs/
  │    └── HOW_TO_USE.md                      ← Complete User Manual & Agency Strategy
  ├── output/                          ← Directory for exported .xlsx and log files
  ├── requirements.txt
  └── README.md
```

### Module Breakdown
- **`src/gui/dentist_lead_suite_gui.py`**: Interactive graphical interface featuring real-time log box, progress bars, scroll-depth tuning, and one-click output directory navigation.
- **`src/scraper/free_dentist_scraper.py`**: Standalone multi-area headless Playwright scraper targeting Google Maps directly. Parses doctor `First Name` & `Surname` (`split_name_and_surname`), checks `Running Ads (Sponsored)?` badges, and identifies `No Website` prospects.
- **`src/utils/run_logger.py`**: Automated telemetry tracking (`output/run_history.json`, `output/run_log.csv`) recording metrics and timestamps.
- **`docs/HOW_TO_USE.md`**: Comprehensive user manual, Excel column definitions, and ad agency outreach guides.

---

## 🟢 Quickstart

1. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   playwright install chromium
   ```
2. Launch the Interactive GUI Suite:
   ```powershell
   python main.py
   ```
   Or run the CLI Scraper:
   ```powershell
   python main.py --cli
   ```

*(For detailed column definitions, strategic agency pitching tips, and troubleshooting, read **[`docs/HOW_TO_USE.md`](docs/HOW_TO_USE.md)**.)*
