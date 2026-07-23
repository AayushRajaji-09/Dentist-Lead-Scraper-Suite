# 🚀 Antigravity Lead Scraper Suite v3.0 — Official User Manual

Welcome to the **Matrix Edition** of the Antigravity Lead Scraper Suite! This tool automatically discovers businesses across **30 major Indian cities × 20 commercial areas each**, extracts deep Google Maps profiles, and exports them to Excel — all through a stunning dark terminal UI.

---

## ⚡ Section 1: Quick Start (Non-Technical Users)

### Step 1 — Setup (one time only)
Open PowerShell inside the project folder and run:
```powershell
pip install -r requirements.txt
playwright install chromium
```

### Step 2 — Launch
```powershell
python main.py
```
A full-screen dark terminal window titled **◈ ANTIGRAVITY LEAD SCRAPER SUITE v3.0 | MATRIX EDITION** will open, complete with falling green characters and a boot sequence.

### Step 3 — Choose Category
In the **⚙ SCRAPER SETTINGS** panel, select your target business type from the **CATEGORY** dropdown:

| Emoji | Category | What it scrapes |
|---|---|---|
| 🦷 | **Dentists** | Dental clinics & practitioners |
| 🏠 | **Real Estate Agents** | Property brokers & offices |
| ✂️ | **Salons** | Hair salons, beauty parlours & spas |
| 📊 | **CA / Accountants** | Chartered accountants & tax firms |

### Step 4 — Pick Your City & Areas
1. Click **`[ 📍 SELECT CITY & AREAS ]`** — a terminal-style dialog opens.
2. Choose a city from the dropdown (30 cities available).
3. The dialog auto-loads **20 curated commercial areas** — all pre-checked.
4. Uncheck any areas you want to skip.
5. **Add a custom area**: type any neighbourhood in the text box and press `+ ADD` or `Enter`.
6. Click **`[ ✅ CONFIRM GRID ]`**.

### Step 5 — Start Scraping
1. Set **Scroll Depth** (default `10` = loads ~30–45 listings per area).
2. Optionally tick **> HEADLESS EXECUTION** to run the browser invisibly (faster).
3. Click **`[ ▶ INITIATE SCRAPE ]`**.
4. Watch the **LIVE NEURAL FEED** console print every lead in real-time.
5. After completion, click **`[ 📁 OUTPUT DIR ]`** to open your Excel file.

---

## 💻 Section 2: Developer & Technical Guide

### Environment Setup
```powershell
# Create & activate virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install packages
pip install -r requirements.txt

# Install Playwright Chromium engine
playwright install chromium
```

### Launch Modes
```powershell
# Interactive Matrix GUI (recommended)
python main.py

# Headless CLI scraper (Dentists only, Ahmedabad default)
python main.py --cli
```

### Adding a New Category
Edit [`src/scraper/categories.py`](../src/scraper/categories.py) and add a new entry:
```python
"🏋️ Gyms": {
    "search_template": "Gym in {area}, {city}",
    "output_prefix":   "Gyms",
    "name_mode":       "business",   # doctor / person / business
    "emoji":           "🏋️",
    "description":     "Fitness centres & gyms",
},
```
It will automatically appear in the GUI dropdown — no other changes needed.

### `name_mode` Values
| Value | Behaviour | Best for |
|---|---|---|
| `doctor` | Extracts after `Dr.` / `CA` prefix; falls back to first+surname | Dentists, CA |
| `person` | Straight first+surname split | Real Estate |
| `business` | Keeps full raw name intact — no splitting | Salons, Gyms |

### Git Telemetry (`run_logger.py`)
After each successful scrape, the suite logs:
- **`output/run_history.json`** — structured JSON (timestamp, city, areas, leads, file, status)
- **`output/run_log.csv`** — tabular metrics for analysis
- Auto git commit: `Auto Log Run: Scraped [X] leads in [City] ([Timestamp])`

---

## 📊 Section 3: Excel Output Schema (13 Columns)

| Column | Description | Example | Use Case |
|---|---|---|---|
| **City** | Target city | `Mumbai` | Geographic filtering |
| **Area** | Commercial neighbourhood | `Bandra West` | Hyper-local ad targeting |
| **Category** | Scrape category | `🦷 Dentists` | Multi-category file tagging |
| **First Name** | Parsed first name | `Rajesh` | Personalised salutation (`Hi Dr. Rajesh,`) |
| **Surname** | Parsed surname | `Patel` | Formal correspondence |
| **Business Name** | Full Google Maps title | `Apex Dental Studio` | Entity verification |
| **Mobile Number** | Cleaned direct phone | `098984 59197` | WhatsApp / telecalling |
| **Address** | Cleaned street address | `102, CG Road, Ahmedabad` | Physical visits / direct mail |
| **Rating** | Star rating | `4.8 ★` | Filter low-rep clinics for ORM pitches |
| **Total Reviews** | Review count | `215` | High count = established budget |
| **Website URL** | Official website (if any) | `https://apexdental.in` or `No Website` | `No Website` = prime web/SEO prospect |
| **Running Ads?** | Google Sponsored badge | `Yes` / `No` | `Yes` = proven ad budget for agency pitch |
| **Google Maps Link** | Direct Maps URL | `https://google.com/maps/place/...` | One-click audit / verification |

---

## 🎨 Section 4: Matrix UI Reference

### Console Log Colours
| Colour | Tag | Used for |
|---|---|---|
| `#00FF41` Matrix green | `success` | Normal extracted leads |
| `#AAFFAA` Bright green | `bright` | Headers / mission complete |
| `#FFB000` Amber | `warning` | Timeouts / abort signals |
| `#FF3333` Red | `error` | Execution errors |
| `#00FFCC` Cyan | `save` | Checkpoint saves |
| `#004400` Dim green | `dim` | Timestamps / dividers |

### Status Bar
```
[ SYS: SCANNING ]  [ LEADS: 42 ]  [ AREA: Bandra West ]  [ 19:32:14 ]
```
All fields update live during scraping.

---

## ❓ Section 5: Troubleshooting & FAQ

**Q: The GUI opens but the rain animation is not visible?**  
A: Resize the window slightly — the canvas `<Configure>` event will trigger and start the animation.

**Q: The Combobox dropdown text looks white/wrong?**  
A: This is a known Windows ttk limitation. The selected value inside the box will appear in the correct Matrix green.

**Q: How do I scrape a city not in the 30-city list?**  
A: In the City & Area picker dialog, pick any city, then manually add your own areas using the **✏ ADD CUSTOM AREA** box. You can add as many as needed.

**Q: Scraper returns 0 results?**  
A: Google Maps occasionally rate-limits bot traffic. Try: increasing `time.sleep()` delays in the scraper, switching to Headless=False to watch the browser, or re-running after a few minutes.

**Q: Can I scrape multiple cities in one run?**  
A: Not in the current GUI — run one city at a time. Output files are named per category+city (e.g., `Salons_Mumbai_Leads.xlsx`) so they won't overwrite each other.

---

*Antigravity Lead Scraper Suite v3.0 — Matrix Edition*  
*Built by Antigravity Agent · Google Maps Neural Engine · Playwright + Tkinter*
