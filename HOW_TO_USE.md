# 🚀 Antigravity Dentist Lead Scraper Suite v2.0 - Official User Manual

Welcome to the **Dentist Lead Generation & Profiling Suite**! This tool automatically discovers top commercial neighborhoods across Indian cities (`Ahmedabad`, `Mumbai`, `Surat`, `Pune`, `Bangalore`, `Delhi`, `Hyderabad`, `Kolkata`, `Chennai`, `Jaipur` + custom vectors), extracts deep business profiles (`First/Last Names`, `Direct Phone/Mobile`, `Address`, `Rating`, `Total Reviews`, `Website`, `Ad Status`), and records telemetry into your Git history.

---

## 🟢 Section 1: Quick Start Guide (For Non-Tech Users)

If you have never touched code before, don't worry! You can run the entire suite using a clean, easy-to-use graphical interface (`GUI Dialog Box`).

### Step 1: Open the Suite
1. Open your terminal or PowerShell inside the project folder (`C:\Users\aayus\Desktop\opencodebase`).
2. Copy and paste this single line, then press **Enter**:
   ```powershell
   .venv\Scripts\python.exe dentist_lead_suite_gui.py
   ```
3. A sleek popup window titled **"🚀 Antigravity Dentist Lead Scraper Suite v2.0"** will appear on your screen!

### Step 2: Configure & Launch
1. **Target City Name:** Enter your desired city (e.g., `Mumbai`, `Surat`, `Ahmedabad`, `Pune`, or `Delhi`).
2. **Areas to Scrape:** Choose how many neighborhoods you want to crawl (e.g., `6` for a fast run, or `10-15` for a deep city-wide audit).
3. **Scroll Depth (Pages):** Set how far down each neighborhood map the bot should scroll (default `10` loads ~30-45 cards per area).
4. Click the blue **`▶ Start Scraping & Profiling`** button!

### Step 3: Watch & Open Your Excel Directory
1. As the tool runs, you can watch the live console inside the dialog box print out every lead found.
2. The browser window will navigate area-by-area automatically.
3. Once completed, a confirmation popup will appear. Click **`📁 Open Output Folder`** to directly view your newly created Excel file (`Dentists_Mumbai_Profiled_Directory.xlsx` or `Dentists_Ahmedabad_Profiled_Directory.xlsx`).

---

## 💻 Section 2: Developer & Technical Guide

### 1. Environment Setup
If cloning this repository onto a fresh machine or server:
```powershell
# 1. Create & activate virtual environment (Windows)
python -m venv .venv
.venv\Scripts\activate

# 2. Install required Python packages
pip install -r requirements.txt

# 3. Install Playwright browser engines
playwright install chromium
```

### 2. Command-Line Execution
While the GUI is recommended for interactive use, you can run the standalone background script directly from the CLI:
```powershell
.venv\Scripts\python.exe free_dentist_scraper.py
```

### 3. Automatic Git Telemetry & Run Logging (`run_logger.py`)
Every time a scraping job finishes (via GUI or CLI), the suite invokes `run_logger.py`:
- **`run_history.json`**: Appends structured JSON metadata (`timestamp`, `city`, `areas_scraped`, `leads_found`, `output_file`, `status`).
- **`run_log.csv`**: Appends tabular metrics for easy spreadsheet analysis.
- **Auto-Commit**: The script automatically executes `git add run_history.json run_log.csv` and creates a commit with the summary:
  `Auto Log Run: Scraped [X] leads across [Y] areas in [City] ([Timestamp])`

---

## 📊 Section 3: Data Profiling Schema (Excel Column Definitions)

Your generated `.xlsx` master directory contains 11 enriched columns designed for high-conversion B2B outreach and ad agency targeting:

| Column Name | Description | Example Output | Strategic Outreach Use Case |
| :--- | :--- | :--- | :--- |
| **City** | Target metropolitan city | `Mumbai` | Geographic filtering |
| **Area** | Specific commercial neighborhood | `Bandra West` | Hyper-local ad targeting / route planning |
| **First Name** | Parsed doctor/owner first name | `Rajesh` | Personalized cold email/WhatsApp salutation (`Hi Dr. Rajesh,`) |
| **Surname** | Parsed doctor/owner last name | `Patel` | Formal correspondence |
| **Clinic Title** | Full Google Maps business title | `Apex Dental Studio & Implant Centre` | Business entity verification |
| **Mobile Number** | Cleaned direct contact number | `098984 59197` | Direct WhatsApp messaging or telecalling (`+91` format ready) |
| **Address** | Cleaned street address without icons | `102, C.G. Road, Navrangpura, Ahmedabad...` | Direct mailers / physical sales rep visits |
| **Rating** | Verified Google Maps star rating | `4.8 ★` | Reputation auditing (filter clinics `< 4.0 ★` for ORM pitches) |
| **Total Reviews** | Review volume count | `215 reviews` | Authority filtering (high review count = established budget) |
| **Website URL** | Official clinic URL (if attached) | `https://www.apexdental.in` or `No Website` | **High-Value Lead Flag:** Clinics with `No Website` are prime prospects for web development & SEO services! |
| **Running Ads (Sponsored)?** | Detects active Google Maps sponsored ad badge | `Yes` or `No` | **Ad Agency Pitch:** Clinics marked `Yes` actively spend on ads (proven marketing budget)! |
| **Google Location Link** | Cleaned direct map URL | `https://www.google.com/maps/place/...` | One-click verification / manual audit |

---

## ❓ Section 4: Troubleshooting & FAQ

- **Q: Why does the terminal say `can't open file`?**  
  A: Ensure your terminal directory is `C:\Users\aayus\Desktop\opencodebase` (use `cd C:\Users\aayus\Desktop\opencodebase`).
- **Q: How do I scrape a custom city not listed in the dropdown?**  
  A: Simply type any city name (e.g., `Indore`, `Lucknow`, `Nagpur`) in the GUI's `Target City Name` field. The engine will dynamically generate 10 commercial search vectors (`Central Indore`, `North Indore`, `Main Market Indore`, etc.) automatically!
