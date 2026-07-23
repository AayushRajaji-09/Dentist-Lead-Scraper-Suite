"""
🚀 Antigravity Lead Scraper Suite v3.0 — MATRIX EDITION
Deep-green terminal aesthetic:
  ▸ Falling Katakana rain animation on header canvas
  ▸ Typewriter boot sequence on startup
  ▸ Color-coded live console (success / warn / error / save / dim)
  ▸ Matrix-styled City & Area picker dialog
  ▸ Custom hover-reactive buttons, dark Spinbox/Checkbutton
  ▸ Live status bar (SYS | LEADS | AREA | CLOCK)
"""
import os
import re
import sys
import random
import threading
import time
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

try:
    import pandas as pd
except ImportError:
    pd = None
import requests
from playwright.sync_api import sync_playwright

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


def save_leads_to_file(results: list, output_file: str):
    if not results:
        return
    try:
        import openpyxl
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Leads"
        headers = list(results[0].keys())
        ws.append(headers)
        for r in results:
            ws.append([str(r.get(h, "")) for h in headers])
        wb.save(output_file)
        return
    except ImportError:
        pass
    if pd is not None:
        try:
            pd.DataFrame(results).to_excel(output_file, index=False)
            return
        except Exception:
            pass
    import csv
    csv_file = output_file.replace(".xlsx", ".csv") if output_file.endswith(".xlsx") else output_file + ".csv"
    with open(csv_file, "w", newline="", encoding="utf-8-sig") as f:
        headers = list(results[0].keys())
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(results)

def extract_emails_from_website(url):
    """Fetches the homepage and extracts an email using regex."""
    if not url or url == "No Website":
        return "No Email Found"
    try:
        response = requests.get(url, timeout=4, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        if response.status_code == 200:
            emails = set(re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", response.text))
            filtered = [e for e in emails if not e.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.wixpress.com', 'sentry.io')) and not e.lower().startswith(('sentry@', 'wix@'))]
            if filtered:
                return filtered[0]
    except Exception:
        pass
    return "No Email Found"

# ── Logging fallback ──────────────────────────────────────────────────────────
try:
    from src.utils.run_logger import log_run
except ImportError:
    try:
        from run_logger import log_run
    except ImportError:
        def log_run(*args, **kwargs):
            pass

# ── Category config fallback ──────────────────────────────────────────────────
try:
    from src.scraper.categories import CATEGORIES, CATEGORY_NAMES
except ImportError:
    try:
        from categories import CATEGORIES, CATEGORY_NAMES
    except ImportError:
        CATEGORIES = {
            "🦷 Dentists":          {"search_template": "Dentist in {area}, {city}",             "output_prefix": "Dentists",      "name_mode": "doctor",   "emoji": "🦷"},
            "🏠 Real Estate Agents": {"search_template": "Real Estate Agent in {area}, {city}",   "output_prefix": "RealEstate",    "name_mode": "person",   "emoji": "🏠"},
            "✂️ Salons":             {"search_template": "Salon in {area}, {city}",                "output_prefix": "Salons",        "name_mode": "business", "emoji": "✂️"},
            "📊 CA / Accountants":   {"search_template": "Chartered Accountant in {area}, {city}", "output_prefix": "CA_Accountants","name_mode": "doctor",   "emoji": "📊"},
        }
        CATEGORY_NAMES = list(CATEGORIES.keys())


# =============================================================================
# MATRIX COLOUR PALETTE & FONTS
# =============================================================================
BG         = "#000000"
FG         = "#00FF41"   # standard Matrix green
FG_BRIGHT  = "#AAFFAA"   # highlight / selected
FG_DIM     = "#004400"   # muted text / borders
FG_HEAD    = "#FFFFFF"   # rain head
AMBER      = "#FFB000"   # warnings / custom areas
RED_CLR    = "#FF3333"   # errors
CYAN_CLR   = "#00FFCC"   # checkpoint / save
BORDER     = "#002200"   # frame borders
SEL_CLR    = "#001100"   # selected / active bg

MONO      = ("Courier New", 10)
MONO_B    = ("Courier New", 10, "bold")
MONO_SM   = ("Courier New", 8)
MONO_LG   = ("Courier New", 13, "bold")
MONO_XL   = ("Courier New", 20, "bold")

MATRIX_CHARS = (
    "ﾁｦｱｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ"
    "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%<>?="
)


# =============================================================================
# TOP COMMERCIAL AREAS — 30 INDIAN CITIES × 20 AREAS EACH
# =============================================================================
TOP_INDIAN_AREAS = {
    "Ahmedabad": [
        "Satellite", "Navrangpura", "Vastrapur", "Maninagar", "Bopal",
        "Thaltej", "Gota", "Chandkheda", "Prahlad Nagar", "CG Road",
        "Sindhu Bhavan Road", "SG Highway", "Naranpura", "Paldi",
        "Vejalpur", "Ambawadi", "Memnagar", "Vastral", "Iscon", "Bodakdev",
    ],
    "Bengaluru": [
        "Koramangala", "Indiranagar", "Whitefield", "HSR Layout", "Jayanagar",
        "JP Nagar", "Electronic City", "Marathahalli", "Malleshwaram", "MG Road",
        "Bannerghatta Road", "BTM Layout", "Rajajinagar", "Vijayanagar",
        "Hebbal", "Yelahanka", "Sarjapur Road", "Bellandur", "RT Nagar", "Banashankari",
    ],
    "Bhopal": [
        "MP Nagar", "Arera Colony", "Shahpura", "Kolar Road", "BHEL",
        "Govindpura", "TT Nagar", "Piplani", "Ayodhya Bypass", "Habibganj",
        "New Market", "Bittan Market", "Hoshangabad Road", "Misrod",
        "Khajuri Kalan", "Berasia Road", "Katara Hills", "Peer Gate", "Lalghati", "Indrapuri",
    ],
    "Bhubaneswar": [
        "Saheed Nagar", "Patia", "Jaydev Vihar", "Bomikhal", "Master Canteen",
        "Tamando", "Chandrasekharpur", "Nayapalli", "Unit 4", "Rasulgarh",
        "Mancheswar", "Vani Vihar", "Acharya Vihar", "Khandagiri",
        "Airport Road", "IRC Village", "Palasuni", "Aiginia", "Laxmi Sagar", "Old Town",
    ],
    "Chandigarh": [
        "Sector 17", "Sector 22", "Sector 35", "Sector 43", "Sector 9",
        "Sector 11", "Sector 37", "Sector 15", "IT Park Chandigarh", "Industrial Area Phase 1",
        "Panchkula", "Mohali", "Sector 20", "Sector 26",
        "Sector 32", "Sector 40", "Sector 45", "Manimajra", "Ramdarbar", "Sector 34",
    ],
    "Chennai": [
        "Anna Nagar", "T Nagar", "Adyar", "Velachery", "Mylapore",
        "Nungambakkam", "Besant Nagar", "OMR", "Porur", "Guindy",
        "Tambaram", "Chromepet", "Perambur", "Egmore",
        "Kodambakkam", "Thiruvanmiyur", "Sholinganallur", "Pallikaranai", "Ambattur", "Avadi",
    ],
    "Coimbatore": [
        "RS Puram", "Gandhipuram", "Race Course Road", "Peelamedu", "Saibaba Colony",
        "Ramanathapuram", "Singanallur", "Ukkadam", "Tidel Park Road", "Mettupalayam Road",
        "Avinashi Road", "Trichy Road", "Sulur", "Hope College",
        "Vadavalli", "Nanjundapuram", "Saravanampatty", "Kuniyamuthur", "Thudiyalur", "Cheran Ma Nagar",
    ],
    "Delhi": [
        "Connaught Place", "South Extension", "Greater Kailash", "Rajouri Garden", "Rohini",
        "Saket", "Dwarka", "Vasant Kunj", "Karol Bagh", "Laxmi Nagar",
        "Pitampura", "Janakpuri", "Preet Vihar", "Malviya Nagar",
        "Green Park", "Hauz Khas", "Safdarjung", "Mayur Vihar", "Uttam Nagar", "Punjabi Bagh",
    ],
    "Faridabad": [
        "Sector 21", "Sector 12", "NIT Faridabad", "Old Faridabad", "Neelam Chowk",
        "Sector 28", "Sector 37", "NHPC Colony", "Ballabgarh", "Sector 15",
        "Sector 16", "Sector 14", "Ashoka Enclave", "Badhkal",
        "Pali Village", "Sector 46", "Sector 78", "Sector 82", "Aravalli Hills", "Sector 86",
    ],
    "Ghaziabad": [
        "Indirapuram", "Vaishali", "Raj Nagar Extension", "Kaushambi", "Crossings Republik",
        "Niti Khand", "Vasundhara", "Shalimar Garden", "Lal Kuan", "Govindpuram",
        "Modinagar", "Murad Nagar", "Sahibabad", "Pratap Vihar",
        "RDC Ghaziabad", "Surya Nagar", "Patel Nagar", "Kavinagar", "Shastri Nagar", "Vijaynagar",
    ],
    "Gurugram": [
        "DLF Phase 1", "Sohna Road", "Golf Course Road", "MG Road Gurugram", "Sector 14",
        "Sector 29", "Sector 56", "Sector 46", "Palam Vihar", "Udyog Vihar",
        "Cyber City", "South City", "Sector 49", "New Colony Gurugram",
        "Civil Lines Gurugram", "Bhondsi", "Manesar", "Wazirabad", "Sector 67", "Sector 83",
    ],
    "Hyderabad": [
        "Banjara Hills", "Jubilee Hills", "Gachibowli", "Madhapur", "Hitec City",
        "Kondapur", "Kukatpally", "Secunderabad", "Begumpet", "Manikonda",
        "Miyapur", "LB Nagar", "Dilsukhnagar", "Ameerpet",
        "SR Nagar", "Uppal", "Tarnaka", "AS Rao Nagar", "Sainikpuri", "Mehdipatnam",
    ],
    "Indore": [
        "Vijay Nagar", "Palasia", "MG Road Indore", "AB Road", "Bhawarkua",
        "LIG Colony", "South Tukoganj", "Annapurna Road", "Treasure Island", "Scheme 54",
        "Malharganj", "Rajwada", "Navlakha", "Banganga",
        "Aerodrome Road", "MR 10", "Bhawar Kuan", "Tilak Nagar", "Manik Bagh", "Chandan Nagar",
    ],
    "Jaipur": [
        "Malviya Nagar", "Vaishali Nagar", "C Scheme", "Raja Park", "Mansarovar",
        "Bani Park", "Tonk Road", "Civil Lines Jaipur", "Jagatpura", "Gopalpura",
        "Sitapura", "Sanganer", "Sindhi Camp", "Station Road Jaipur",
        "Nirman Nagar", "Durgapura", "Patrakar Colony", "Shyam Nagar", "Vidyadhar Nagar", "Agrasen Nagar",
    ],
    "Jodhpur": [
        "Sardarpura", "Paota", "Shastri Nagar Jodhpur", "Ratanada", "Sojati Gate",
        "Chopasni Road", "Raika Bagh", "Airport Road Jodhpur", "Pal Road", "Mandore Road",
        "Circuit House Road", "Siwanchi Gate", "Brahmpuri", "Basni",
        "New Pali Road", "Kamla Nehru Nagar", "Umed Colony", "Bhati Circle", "Residency Road", "Nai Sarak",
    ],
    "Kochi": [
        "MG Road Kochi", "Kakkanad", "Edapally", "Palarivattom", "Vyttila",
        "Marine Drive", "Fort Kochi", "Kaloor", "Thrippunithura", "Thevara",
        "Aluva", "Panampilly Nagar", "Kadavanthra", "Girinagar",
        "Elamkulam", "Vytilla Hub", "Seaport Airport Road", "HMT Colony", "Ernakulam North", "Cheranalloor",
    ],
    "Kolkata": [
        "Salt Lake", "Park Street", "Ballygunge", "Alipore", "New Town",
        "Bhawanipur", "Jadavpur", "Tollygunge", "Rajarhat", "Shyambazar",
        "Dum Dum", "Behala", "Kasba", "Gariahat",
        "Ultadanga", "Lake Town", "Baguiati", "Barasat", "Esplanade", "Sealdah",
    ],
    "Lucknow": [
        "Hazratganj", "Gomti Nagar", "Aliganj", "Indiranagar Lucknow", "Vibhuti Khand",
        "Mahanagar", "Alambagh", "Rajajipuram", "Sushant Golf City", "Kanpur Road",
        "Jankipuram", "Chinhat", "Mundera", "Faizabad Road",
        "Lekhraj Market", "LDA Colony", "Eldeco", "Sultanpur Road", "Trans Gomti", "Sarvodaya Nagar",
    ],
    "Ludhiana": [
        "Model Town", "Sarabha Nagar", "Pakhowal Road", "Mall Road Ludhiana", "BRS Nagar",
        "Ferozepur Road", "Dugri", "Humbran Road", "Gurdev Nagar", "Rajguru Nagar",
        "Civil Lines Ludhiana", "Chander Nagar", "Sherpur", "Shimlapuri",
        "Bhai Randhir Singh Nagar", "Akalsar Road", "Jagraon Bridge", "Giaspura", "Focal Point", "Transport Nagar",
    ],
    "Mangalore": [
        "Hampankatta", "Attavar", "Bejai", "Kadri", "KS Rao Road",
        "Balmatta", "Lalbagh Mangalore", "Kankanady", "Urwa", "Mangaladevi",
        "Bajpe", "Kuloor", "Bikarnakatte", "Ullal",
        "Surathkal", "Derebail", "Valachil", "Malemar", "Pandeshwar", "Kodailbail",
    ],
    "Mumbai": [
        "Bandra West", "Andheri West", "Borivali West", "Dadar West", "Malad West",
        "Thane West", "Powai", "Juhu", "Colaba", "Lower Parel",
        "Goregaon West", "Chembur", "Kandivali", "Vile Parle",
        "Santacruz", "Mulund", "Ghatkopar", "Kurla", "Vikhroli", "Navi Mumbai",
    ],
    "Mysuru": [
        "Saraswathipuram", "Vijayanagar Mysuru", "Kuvempunagar", "VV Mohalla", "Jayalakshmipuram",
        "Hebbal Mysuru", "Gokulam", "Lakshmipuram", "Chamundipuram", "Siddiqua Colony",
        "Devaraja", "Yadavagiri", "Bogadi", "JP Nagar Mysuru",
        "Ashokapuram", "Ring Road Mysuru", "Brindavan Extension", "Ramakrishnanagar", "Udaygiri", "Kesare",
    ],
    "Nagpur": [
        "Dharampeth", "Sadar", "Civil Lines Nagpur", "Sitabuldi", "Ramdaspeth",
        "Bajaj Nagar", "Pratap Nagar", "Sakkardara", "Laxmi Nagar Nagpur", "Manish Nagar",
        "Ambazari", "Khamla", "Hingna Road", "Besa",
        "Wardhaman Nagar", "Itwari", "Cotton Market", "Trimurti Nagar", "Nandanvan", "Shankar Nagar",
    ],
    "Noida": [
        "Sector 18", "Sector 62", "Sector 50", "Sector 44", "Sector 137",
        "Sector 76", "Sector 120", "Greater Noida West", "Sector 100", "Sector 93",
        "Sector 110", "Sector 128", "Sector 12", "Sector 15",
        "Sector 25", "Sector 27", "Sector 34", "Sector 51", "Golf Course Noida", "Expressway Noida",
    ],
    "Patna": [
        "Boring Road", "Frazer Road", "Exhibition Road", "Bailey Road", "Kankarbagh",
        "Rajendra Nagar", "Ashok Raj Path", "Dak Bungalow Road", "Patliputra Colony", "Gandhi Maidan",
        "Kurji", "Phulwari Sharif", "Mithapur", "Danapur",
        "Saguna More", "New Bypass Road", "Bankipore", "Kadamkuan", "Rajabazar", "Jakkanpur",
    ],
    "Pune": [
        "Kothrud", "Baner", "Viman Nagar", "Wakad", "Hinjewadi",
        "Hadapsar", "Kalyani Nagar", "Aundh", "Shivaji Nagar", "Koregaon Park",
        "Kharadi", "NIBM Road", "Wanowrie", "Pimple Saudagar",
        "Bavdhan", "Magarpatta", "Fatima Nagar", "PCMC", "Undri", "Kondhwa",
    ],
    "Raipur": [
        "VIP Road Raipur", "Shankar Nagar Raipur", "Devendra Nagar", "Pandri", "Telibandha",
        "Tatibandh", "Byron Bazaar", "Fafadih", "Samta Colony", "GE Road",
        "Mahaveer Nagar", "Avanti Vihar", "Kota Raipur", "Mowa",
        "Amanaka", "Pachpedi Nagar", "Old Bhilai Road", "Tikrapara", "Sant Nagar", "Sunder Nagar",
    ],
    "Rajkot": [
        "Kalawad Road", "Yagnik Road", "Gondal Road", "Tagore Road", "Race Course Road Rajkot",
        "Bhaktinagar", "Mavdi", "150 Feet Ring Road", "University Road", "Raiya Road",
        "Amin Marg", "Kotecha Chowk", "Nirmala Road", "Karanpara",
        "Sattadhar", "Punjabipara", "Jamnagar Road", "Morbi Road", "Paddhari", "Kothariya",
    ],
    "Surat": [
        "Adajan", "Vesu", "Ring Road Surat", "Piplod", "Varachha",
        "City Light", "Ghod Dod Road", "Althan", "Katargam", "Pal",
        "Udhna", "Rander", "Dumas Road", "Kapodra",
        "Athwa", "Majura Gate", "Nanpura", "Chowk Bazar", "Sarthana", "Palanpur Patia",
    ],
    "Vadodara": [
        "Alkapuri", "Racecourse Vadodara", "Fatehgunj", "Manjalpur", "Karelibaug",
        "Akota", "Gotri", "Waghodia Road", "Old Padra Road", "Tarsali",
        "Makarpura", "Sama", "Vasna Road", "GIDC Vadodara",
        "Subhanpura", "Productivity Road", "Harni Road", "Ellora Park", "Nizampura", "Panigate",
    ],
}

CITY_NAMES_SORTED = sorted(TOP_INDIAN_AREAS.keys())


# =============================================================================
# NAME PARSER — CATEGORY-AWARE
# =============================================================================
def parse_lead_name(raw_name: str, name_mode: str):
    if not raw_name:
        return "", ""
    if name_mode == "business":
        return raw_name.strip(), ""
    if name_mode == "doctor":
        m = re.search(r"Dr\.?\s+([A-Za-z\u0900-\u097F]+)\s+([A-Za-z\u0900-\u097F]+)", raw_name, re.IGNORECASE)
        if m:
            return m.group(1).capitalize(), m.group(2).capitalize()
        m = re.search(r"\bCA\.?\s+([A-Za-z\u0900-\u097F]+)\s+([A-Za-z\u0900-\u097F]+)", raw_name, re.IGNORECASE)
        if m:
            return m.group(1).capitalize(), m.group(2).capitalize()
    clean = re.sub(r"[^\w\s]", "", raw_name).split()
    if len(clean) >= 2:
        return clean[0].capitalize(), clean[1].capitalize()
    if len(clean) == 1:
        return clean[0].capitalize(), ""
    return raw_name, ""


# =============================================================================
# MATRIX BUTTON FACTORY
# =============================================================================
def mk_btn(parent, text: str, command, state=tk.NORMAL, width=None) -> tk.Button:
    btn = tk.Button(
        parent, text=text, command=command,
        bg="#001800" if state == tk.NORMAL else "#000800",
        fg=FG if state == tk.NORMAL else FG_DIM,
        activebackground=FG, activeforeground="#000000",
        font=("Courier New", 10, "bold"), relief=tk.SOLID, bd=1,
        highlightbackground="#004400", highlightcolor=FG,
        highlightthickness=1, cursor="hand2",
        padx=12, pady=6, state=state,
    )
    if width:
        btn.config(width=width)
    def _enter(e):
        if str(btn["state"]) != "disabled":
            btn.config(bg=FG, fg="#000000", highlightbackground=FG)
    def _leave(e):
        if str(btn["state"]) != "disabled":
            btn.config(bg="#001800", fg=FG, highlightbackground="#004400")
    btn.bind("<Enter>", _enter)
    btn.bind("<Leave>", _leave)
    return btn


def mk_option_menu(parent, var: tk.StringVar, options: list, command=None, width=None) -> tk.OptionMenu:
    opt = tk.OptionMenu(parent, var, *options, command=command)
    opt.config(
        bg="#001800", fg=FG, activebackground=FG, activeforeground="#000000",
        font=("Courier New", 10, "bold"), relief=tk.SOLID, bd=1,
        highlightbackground="#004400", highlightcolor=FG,
        highlightthickness=1, cursor="hand2", padx=8, pady=4,
    )
    if width:
        opt.config(width=width)
    opt["menu"].config(
        bg="#001800", fg=FG, activebackground=FG, activeforeground="#000000",
        font=("Courier New", 10, "bold"), bd=1, relief=tk.SOLID,
    )
    def _enter(e):
        if str(opt["state"]) != "disabled":
            opt.config(bg=FG, fg="#000000", highlightbackground=FG)
    def _leave(e):
        if str(opt["state"]) != "disabled":
            opt.config(bg="#001800", fg=FG, highlightbackground="#004400")
    opt.bind("<Enter>", _enter)
    opt.bind("<Leave>", _leave)
    return opt


# =============================================================================
# MATRIX RAIN ANIMATION
# =============================================================================
class MatrixRain:
    """
    Falling katakana/alphanumeric rain on a tk.Canvas.
    Uses pre-created text items (no per-frame create/delete overhead).
    """
    CHAR_W = 13
    CHAR_H = 13
    FONT   = ("Courier New", 9, "bold")

    def __init__(self, canvas: tk.Canvas, width: int, height: int, top_tags=("banner",)):
        self.canvas    = canvas
        self.width     = width
        self.height    = height
        self.top_tags  = top_tags
        self.running   = True
        self.cols      = max(1, width  // self.CHAR_W)
        self.rows      = max(1, height // self.CHAR_H)

        # Pre-create all text items (tagged "rain")
        self._items: list[list[int]] = []
        for c in range(self.cols):
            row_items = []
            for r in range(self.rows):
                iid = canvas.create_text(
                    c * self.CHAR_W + self.CHAR_W // 2,
                    r * self.CHAR_H + self.CHAR_H // 2,
                    text=" ", fill=BG,
                    font=self.FONT, tags="rain",
                )
                row_items.append(iid)
            self._items.append(row_items)

        # Per-column state
        self._cols: list[dict] = []
        for _ in range(self.cols):
            self._cols.append({
                "head" : random.uniform(-self.rows, 0),
                "speed": random.uniform(0.35, 1.1),
                "trail": random.randint(6, 16),
            })

        self._animate()

    # ── Animation loop ────────────────────────────────────────────────────────
    def _animate(self):
        if not self.running:
            return

        ic = self.canvas.itemconfig
        CHARS = MATRIX_CHARS

        for c_idx, (col_items, state) in enumerate(zip(self._items, self._cols)):
            head  = state["head"]
            trail = state["trail"]

            for r in range(self.rows):
                dist = int(head) - r   # 0 = head, >0 = behind

                if dist < 0 or dist >= trail:
                    ic(col_items[r], text=" ", fill=BG)
                elif dist == 0:
                    ic(col_items[r], text=random.choice(CHARS), fill=FG_HEAD)
                elif dist == 1:
                    ic(col_items[r], text=random.choice(CHARS), fill=FG_BRIGHT)
                else:
                    fade  = (trail - dist) / trail
                    g_val = int(max(30, min(220, 220 * fade)))
                    ic(col_items[r], text=random.choice(CHARS), fill="#00%02x00" % g_val)

            state["head"] += state["speed"]
            if state["head"] - trail > self.rows:
                state["head"]  = random.uniform(-self.rows // 2, 0)
                state["speed"] = random.uniform(0.35, 1.1)
                state["trail"] = random.randint(6, 16)

        # Keep banner overlay on top
        for tag in self.top_tags:
            try:
                self.canvas.tag_raise(tag)
            except Exception:
                pass

        if self.running:
            self.canvas.after(90, self._animate)

    def stop(self):
        self.running = False


# =============================================================================
# CITY & AREA PICKER DIALOG — MATRIX EDITION
# =============================================================================
class CityAreaPickerDialog(tk.Toplevel):
    """
    Full-black terminal-style city/area picker.
    After dialog closes, check .confirmed; read .result_city and .result_areas.
    """

    def __init__(self, parent, current_city: str, current_areas: list):
        super().__init__(parent)
        self.title("> CITY & AREA SELECTION MATRIX")
        self.geometry("540x640")
        self.configure(bg=BG)
        self.resizable(True, True)
        self.minsize(460, 500)
        self.transient(parent)
        self.grab_set()

        self.confirmed    = False
        self.result_city  = current_city
        self.result_areas = list(current_areas)
        self.area_vars: dict[str, tk.BooleanVar] = {}

        self._build()
        self.wait_window()

    # ── Build ─────────────────────────────────────────────────────────────────
    def _build(self):
        # Header bar
        hdr = tk.Frame(self, bg=BORDER, pady=10)
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text=" ◈  CITY & AREA SELECTION MATRIX",
                 bg=BORDER, fg=FG_BRIGHT, font=MONO_LG).pack(side=tk.LEFT, padx=12)

        tk.Frame(self, bg=FG_DIM, height=1).pack(fill=tk.X)

        # City selector
        city_frm = tk.Frame(self, bg=BG, padx=14, pady=10)
        city_frm.pack(fill=tk.X)
        tk.Label(city_frm, text="> SELECT TARGET CITY :", bg=BG, fg=FG_DIM, font=MONO_SM).pack(anchor=tk.W)

        style = ttk.Style()
        style.configure("Dlg.TCombobox",
            fieldbackground=BG, background=BG, foreground=FG,
            selectbackground=SEL_CLR, selectforeground=FG_BRIGHT,
            arrowcolor=FG, bordercolor=BORDER, insertcolor=FG,
        )
        style.map("Dlg.TCombobox",
            fieldbackground=[("readonly", BG)],
            foreground=[("readonly", FG)],
        )

        self.city_var = tk.StringVar(value=self.result_city if self.result_city in CITY_NAMES_SORTED else CITY_NAMES_SORTED[0])
        mk_option_menu(
            city_frm, self.city_var, CITY_NAMES_SORTED,
            command=lambda val: self._load(val), width=32
        ).pack(anchor=tk.W, pady=(4, 0))

        tk.Frame(self, bg=FG_DIM, height=1).pack(fill=tk.X, pady=4)

        # Area header row
        ah = tk.Frame(self, bg=BG, padx=14, pady=4)
        ah.pack(fill=tk.X)
        tk.Label(ah, text="> AREAS TO INCLUDE :", bg=BG, fg=FG, font=MONO_B).pack(side=tk.LEFT)
        self.count_lbl = tk.Label(ah, text="", bg=BG, fg=AMBER, font=MONO_B)
        self.count_lbl.pack(side=tk.LEFT, padx=10)
        mk_btn(ah, "[☐ NONE]", self._none, width=10).pack(side=tk.RIGHT, padx=4)
        mk_btn(ah, "[☑ ALL]",  self._all,  width=10).pack(side=tk.RIGHT, padx=4)

        # Scrollable checkboxes
        cx_outer = tk.Frame(self, bg=BORDER, bd=1, relief=tk.SOLID)
        cx_outer.pack(fill=tk.BOTH, expand=True, padx=10, pady=4)
        self._canvas = tk.Canvas(cx_outer, bg=BG, highlightthickness=0)
        vbar = tk.Scrollbar(cx_outer, orient=tk.VERTICAL, command=self._canvas.yview,
                            bg=BG, troughcolor=BG, activebackground=FG_DIM, width=10, bd=0, relief=tk.FLAT)
        self._canvas.configure(yscrollcommand=vbar.set)
        vbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._cb_frame = tk.Frame(self._canvas, bg=BG)
        self._cw = self._canvas.create_window((0, 0), window=self._cb_frame, anchor="nw")
        self._cb_frame.bind("<Configure>", lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all")))
        self._canvas.bind("<Configure>", lambda e: self._canvas.itemconfig(self._cw, width=e.width))
        self._canvas.bind_all("<MouseWheel>", self._scroll)

        # Custom area entry
        tk.Frame(self, bg=BORDER, height=1).pack(fill=tk.X, padx=10, pady=4)
        cust = tk.Frame(self, bg=BG, padx=14, pady=6)
        cust.pack(fill=tk.X)
        tk.Label(cust, text="> ADD CUSTOM AREA :", bg=BG, fg=FG, font=MONO_B).pack(anchor=tk.W)
        row = tk.Frame(cust, bg=BG)
        row.pack(fill=tk.X, pady=4)
        self.custom_e = tk.Entry(row, font=("Courier New", 11, "bold"), width=28,
                                 bg="#001800", fg=FG, insertbackground=FG,
                                 relief=tk.SOLID, bd=1,
                                 highlightbackground=BORDER, highlightcolor=FG, highlightthickness=1)
        self.custom_e.pack(side=tk.LEFT, padx=(0, 8))
        self.custom_e.bind("<Return>", lambda e: self._add_custom())
        mk_btn(row, "[+ ADD]", self._add_custom).pack(side=tk.LEFT)

        # Footer
        tk.Frame(self, bg=BORDER, height=1).pack(fill=tk.X, padx=10)
        foot = tk.Frame(self, bg=BG, padx=14, pady=10)
        foot.pack(fill=tk.X)
        mk_btn(foot, "[ ✕  ABORT ]",        self.destroy).pack(side=tk.LEFT)
        mk_btn(foot, "[ ✅  CONFIRM GRID ]", self._confirm).pack(side=tk.RIGHT)

        self._load(self.result_city)

    def _scroll(self, event):
        self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _load(self, city: str):
        for w in self._cb_frame.winfo_children():
            w.destroy()
        self.area_vars.clear()
        for i, area in enumerate(TOP_INDIAN_AREAS.get(city, [])):
            var = tk.BooleanVar(value=True)
            self.area_vars[area] = var
            tk.Checkbutton(
                self._cb_frame, text=f"  ▸ {area}", variable=var,
                bg=BG, fg=FG, activebackground=BG, activeforeground=FG_BRIGHT,
                selectcolor="#003800", font=("Courier New", 10, "bold"), anchor=tk.W, bd=0,
                cursor="hand2", command=self._upd_count,
            ).grid(row=i // 2, column=i % 2, sticky=tk.W, padx=10, pady=3)
        self._upd_count()
        self._canvas.update_idletasks()
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _upd_count(self):
        sel = sum(1 for v in self.area_vars.values() if v.get())
        self.count_lbl.config(text=f"[{sel} / {len(self.area_vars)} ACTIVE]")

    def _all(self):
        for v in self.area_vars.values():
            v.set(True)
        self._upd_count()

    def _none(self):
        for v in self.area_vars.values():
            v.set(False)
        self._upd_count()

    def _add_custom(self):
        raw = self.custom_e.get().strip().title()
        if not raw:
            return
        if raw in self.area_vars:
            messagebox.showinfo("> DUPLICATE", f"'{raw}' already in the grid.", parent=self)
            return
        var = tk.BooleanVar(value=True)
        self.area_vars[raw] = var
        idx = len(self.area_vars) - 1
        tk.Checkbutton(
            self._cb_frame, text=f"  ✏ {raw} [CUSTOM]", variable=var,
            bg=BG, fg=AMBER, activebackground=BG, activeforeground=FG_BRIGHT,
            selectcolor="#003800", font=("Courier New", 10, "bold"), anchor=tk.W, bd=0,
            cursor="hand2", command=self._upd_count,
        ).grid(row=idx // 2, column=idx % 2, sticky=tk.W, padx=10, pady=3)
        self.custom_e.delete(0, tk.END)
        self._upd_count()
        self._canvas.update_idletasks()
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))
        self._canvas.yview_moveto(1.0)

    def _confirm(self):
        sel = [a for a, v in self.area_vars.items() if v.get()]
        if not sel:
            messagebox.showwarning("> ERROR", "Select at least one area.", parent=self)
            return
        self.result_city  = self.city_var.get()
        self.result_areas = sel
        self.confirmed    = True
        self.destroy()


# =============================================================================
# MAIN APPLICATION — MATRIX EDITION
# =============================================================================
class ScraperApp:

    def __init__(self, root: tk.Tk):
        self.root     = root
        self.root.title("◈  ANTIGRAVITY LEAD SCRAPER SUITE  v3.0  |  MATRIX EDITION")
        self.root.geometry("980x760")
        self.root.minsize(820, 620)
        self.root.configure(bg=BG)

        self.is_running     = False
        self.city_name      = "Mumbai"
        self.selected_areas = list(TOP_INDIAN_AREAS["Mumbai"])
        self.rain: MatrixRain | None = None
        self._banner_drawn  = False

        self._apply_ttk_styles()
        self._build_ui()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.after(500,  self._boot_sequence)
        self.root.after(1000, self._tick_clock)

    # ── TTK styles ────────────────────────────────────────────────────────────
    def _apply_ttk_styles(self):
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("Matrix.TCombobox",
            fieldbackground="#001800", background="#002800", foreground=FG,
            selectbackground="#003800", selectforeground="#AAFFAA",
            arrowcolor=FG, bordercolor=FG, lightcolor=FG, darkcolor=FG,
            font=("Courier New", 10, "bold"),
        )
        s.map("Matrix.TCombobox",
            fieldbackground=[("readonly", "#001800")],
            foreground=[("readonly", FG)],
            background=[("active", "#003800")],
        )
        s.configure("Dlg.TCombobox",
            fieldbackground="#001800", background="#002800", foreground=FG,
            selectbackground="#003800", selectforeground="#AAFFAA",
            arrowcolor=FG, bordercolor=FG,
            font=("Courier New", 10, "bold"),
        )
        s.map("Dlg.TCombobox",
            fieldbackground=[("readonly", "#001800")],
            foreground=[("readonly", FG)],
        )
        self.root.option_add("*TCombobox*Listbox.background", "#001800")
        self.root.option_add("*TCombobox*Listbox.foreground", "#00FF41")
        self.root.option_add("*TCombobox*Listbox.selectBackground", "#00FF41")
        self.root.option_add("*TCombobox*Listbox.selectForeground", "#000000")
        self.root.option_add("*TCombobox*Listbox.font", "Courier New 10 bold")

    # ── Layout ────────────────────────────────────────────────────────────────
    def _build_ui(self):
        self._build_rain_header()
        self._build_settings()
        self._build_action_bar()
        self._build_console()
        self._build_status_bar()

    # ── 1. Rain header ────────────────────────────────────────────────────────
    def _build_rain_header(self):
        self.rain_canvas = tk.Canvas(
            self.root, height=128, bg=BG,
            highlightthickness=1, highlightbackground=BORDER,
        )
        self.rain_canvas.pack(fill=tk.X, padx=8, pady=(8, 0))
        self.rain_canvas.bind("<Configure>", self._on_canvas_cfg)

    def _on_canvas_cfg(self, event):
        if not self._banner_drawn:
            self._banner_drawn = True
            self._start_rain(event.width, event.height)
            self._draw_banner(event.width)
        else:
            # Window resize — rebuild
            if self.rain:
                self.rain.stop()
            self.rain_canvas.delete("all")
            self._banner_drawn = False
            self.root.after(80, lambda: self._on_canvas_cfg(
                type("E", (), {"width": self.rain_canvas.winfo_width(),
                               "height": self.rain_canvas.winfo_height()})()
            ))

    def _start_rain(self, w: int, h: int):
        self.rain = MatrixRain(self.rain_canvas, w, h, top_tags=("banner",))

    def _draw_banner(self, w: int):
        cx = w // 2
        # Dark backdrop so banner is readable over rain
        self.rain_canvas.create_rectangle(
            cx - 380, 12, cx + 380, 116,
            fill="#000000", outline=FG_DIM, width=1, tags="banner",
        )
        # Top accent line
        self.rain_canvas.create_line(cx - 360, 24, cx + 360, 24, fill=FG_DIM, tags="banner")

        self.rain_canvas.create_text(
            cx, 52,
            text="◈  A N T I G R A V I T Y  ◈",
            fill=FG_BRIGHT, font=("Courier New", 22, "bold"), tags="banner",
        )
        self.rain_canvas.create_text(
            cx, 78,
            text="LEAD  SCRAPER  SUITE   v3.0   |   GOOGLE  MAPS  NEURAL  ENGINE",
            fill=FG_DIM, font=("Courier New", 9, "bold"), tags="banner",
        )
        # Bottom accent line
        self.rain_canvas.create_line(cx - 360, 104, cx + 360, 104, fill=FG_DIM, tags="banner")

    # ── 2. Settings panel ─────────────────────────────────────────────────────
    def _build_settings(self):
        frm = tk.LabelFrame(
            self.root, text="  ⚙  SCRAPER SETTINGS  ",
            bg=BG, fg=FG_BRIGHT, font=MONO_B,
            bd=1, relief=tk.SOLID, labelanchor="nw",
        )
        frm.pack(fill=tk.X, padx=8, pady=6)

        # Row 0 — Category | Depth
        tk.Label(frm, text="> CATEGORY :", bg=BG, fg=FG, font=MONO_B).grid(
            row=0, column=0, sticky=tk.W, padx=(14, 6), pady=8)

        self.category_var = tk.StringVar(value=CATEGORY_NAMES[0])
        mk_option_menu(
            frm, self.category_var, CATEGORY_NAMES, width=28
        ).grid(row=0, column=1, sticky=tk.W, padx=6, pady=8)

        tk.Label(frm, text="> DEPTH :", bg=BG, fg=FG, font=MONO_B).grid(
            row=0, column=2, sticky=tk.W, padx=(24, 6), pady=8)
        self.scroll_var = tk.IntVar(value=10)
        tk.Spinbox(
            frm, from_=3, to=50, textvariable=self.scroll_var, width=7,
            bg="#001800", fg=FG, insertbackground=FG, relief=tk.SOLID, bd=1,
            buttonbackground=BORDER, font=("Courier New", 11, "bold"),
            highlightbackground=BORDER, highlightthickness=1,
        ).grid(row=0, column=3, sticky=tk.W, padx=6, pady=8)

        # Row 1 — City display | button
        tk.Label(frm, text="> CITY/AREAS :", bg=BG, fg=FG, font=MONO_B).grid(
            row=1, column=0, sticky=tk.W, padx=(14, 6), pady=8)

        self.city_display_var = tk.StringVar()
        self._refresh_city_lbl()
        tk.Label(frm, textvariable=self.city_display_var,
                 bg=BG, fg=FG_BRIGHT, font=MONO_B).grid(
            row=1, column=1, sticky=tk.W, padx=6, pady=8)

        mk_btn(frm, "[ 📍  SELECT CITY & AREAS ]", self.open_city_dialog).grid(
            row=1, column=2, columnspan=2, sticky=tk.W, padx=(24, 0), pady=8)

        # Row 2 — Headless
        self.headless_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            frm,
            text="  > HEADLESS EXECUTION  (background browser — faster, no visible window)",
            variable=self.headless_var,
            bg=BG, fg=FG, activebackground=BG, activeforeground=FG_BRIGHT,
            selectcolor="#003800", font=("Courier New", 10, "bold"), anchor=tk.W, bd=0, cursor="hand2",
        ).grid(row=2, column=0, columnspan=4, sticky=tk.W, padx=14, pady=(2, 10))

    # ── 3. Action buttons ─────────────────────────────────────────────────────
    def _build_action_bar(self):
        frm = tk.Frame(self.root, bg=BG)
        frm.pack(fill=tk.X, padx=8, pady=4)

        self.start_btn = mk_btn(frm, "[ ▶  INITIATE SCRAPE ]", self.start_thread)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.stop_btn = mk_btn(frm, "[ ⏹  ABORT MISSION ]", self.stop_scraper, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=4)

        mk_btn(frm, "[ 📁  OUTPUT DIR ]", self.open_folder).pack(side=tk.RIGHT)

    # ── 4. Console ────────────────────────────────────────────────────────────
    def _build_console(self):
        tk.Label(self.root, text="  ◈  LIVE NEURAL FEED  ◈",
                 bg=BG, fg=FG_BRIGHT, font=("Courier New", 10, "bold")).pack(anchor=tk.W, padx=10, pady=(4, 2))

        outer = tk.Frame(self.root, bg=BORDER, bd=1, relief=tk.SOLID)
        outer.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 4))

        self.console = scrolledtext.ScrolledText(
            outer, wrap=tk.WORD, font=("Courier New", 10),
            bg=BG, fg=FG, insertbackground=FG,
            state=tk.DISABLED, relief=tk.FLAT, bd=0,
        )
        self.console.pack(fill=tk.BOTH, expand=True)
        self.console.vbar.config(
            bg=BG, troughcolor=BG, activebackground=FG_DIM,
            width=10, bd=0, relief=tk.FLAT,
        )

        # Color tags
        self.console.tag_configure("success", foreground=FG)
        self.console.tag_configure("bright",  foreground=FG_BRIGHT)
        self.console.tag_configure("warning", foreground=AMBER)
        self.console.tag_configure("error",   foreground=RED_CLR)
        self.console.tag_configure("save",    foreground=CYAN_CLR)
        self.console.tag_configure("dim",     foreground="#008822")
        self.console.tag_configure("ts",      foreground="#008822")

    # ── 5. Status bar ─────────────────────────────────────────────────────────
    def _build_status_bar(self):
        bar = tk.Frame(self.root, bg="#001800", pady=5)
        bar.pack(fill=tk.X, side=tk.BOTTOM)

        tk.Label(bar, text=" ◈ ", bg="#001800", fg=FG, font=MONO_B).pack(side=tk.LEFT)

        self.lbl_sys = tk.Label(bar, text="SYS: ONLINE", bg="#001800", fg=FG_BRIGHT, font=MONO_B)
        self.lbl_sys.pack(side=tk.LEFT, padx=6)
        self._sep(bar)

        self.lbl_leads = tk.Label(bar, text="LEADS: 0", bg="#001800", fg=AMBER, font=MONO_B)
        self.lbl_leads.pack(side=tk.LEFT, padx=6)
        self._sep(bar)

        self.lbl_area = tk.Label(bar, text="AREA: ---", bg="#001800", fg=FG, font=MONO_B)
        self.lbl_area.pack(side=tk.LEFT, padx=6)

        # Right side
        self.lbl_clock = tk.Label(bar, text="", bg="#001800", fg=FG_BRIGHT, font=MONO_B)
        self.lbl_clock.pack(side=tk.RIGHT, padx=8)
        self._sep(bar, side=tk.RIGHT)
        tk.Label(bar, text="ANTIGRAVITY ENGINE v3.0 ", bg="#001800", fg=FG, font=MONO_B).pack(side=tk.RIGHT)

    def _sep(self, parent, side=tk.LEFT):
        tk.Label(parent, text="|", bg="#001800", fg="#005511", font=MONO_B).pack(side=side, padx=3)

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _refresh_city_lbl(self):
        n = len(self.selected_areas)
        self.city_display_var.set(f"{self.city_name}   [{n} AREAS ACTIVE]")

    def _tick_clock(self):
        self.lbl_clock.config(text=time.strftime("%H:%M:%S"))
        self.root.after(1000, self._tick_clock)

    def _set_status(self, sys_txt=None, leads=None, area=None):
        if sys_txt is not None:
            self.lbl_sys.config(text=f"SYS: {sys_txt}")
        if leads is not None:
            self.lbl_leads.config(text=f"LEADS: {leads}")
        if area is not None:
            self.lbl_area.config(text=f"AREA: {str(area)[:22]}")

    # ── Logging ───────────────────────────────────────────────────────────────
    def log(self, message: str, tag: str = "success"):
        """Thread-safe. Schedules insert on main thread."""
        self.root.after(0, lambda m=message, t=tag: self._insert_log(m, t))

    def _insert_log(self, message: str, tag: str):
        self.console.config(state=tk.NORMAL)
        ts = time.strftime("[%H:%M:%S] ")
        self.console.insert(tk.END, ts, "ts")
        self.console.insert(tk.END, message + "\n", tag)
        self.console.see(tk.END)
        self.console.config(state=tk.DISABLED)

    # ── Boot sequence ─────────────────────────────────────────────────────────
    def _boot_sequence(self):
        # Check if discord webhook is configured
        discord_status = "[ OPTIONAL : ADD WEBHOOK IN config.json ]"
        try:
            from src.utils.run_logger import get_discord_webhook_url
            if get_discord_webhook_url():
                discord_status = "[ ACTIVE : DISCORD TEAM SYNC ENABLED ]"
        except Exception:
            pass

        lines = [
            ("══════════════════════════════════════════════════════════", "dim"),
            ("  ◈  ANTIGRAVITY NEURAL LEAD ENGINE  —  MATRIX EDITION  ◈", "bright"),
            ("══════════════════════════════════════════════════════════", "dim"),
            ("> SCRAPER CORE ............. [ INITIALIZING ]", "success"),
            ("> CITY DATABASE ............ [ 30 CITIES / 600 AREAS LOADED ]", "success"),
            ("> CATEGORY MODULES ......... [ DENTISTS | REAL ESTATE | SALONS | CA ]", "success"),
            ("> PLAYWRIGHT BROWSER ....... [ ENGINE READY ]", "success"),
            (f"> TEAM TELEMETRY ........... {discord_status}", "save" if "ACTIVE" in discord_status else "dim"),
            ("> GOOGLE MAPS GRID ......... [ CONNECTED ]", "success"),
            ("──────────────────────────────────────────────────────────", "dim"),
            (">  SYSTEM  ONLINE.   AWAITING  OPERATOR  INPUT.", "bright"),
            ("", "success"),
        ]
        for i, (text, tag) in enumerate(lines):
            self.root.after(i * 160, lambda t=text, tg=tag: self.log(t, tg))

    # ── Button handlers ───────────────────────────────────────────────────────
    def open_city_dialog(self):
        dlg = CityAreaPickerDialog(self.root, self.city_name, self.selected_areas)
        if dlg.confirmed:
            self.city_name      = dlg.result_city
            self.selected_areas = dlg.result_areas
            self._refresh_city_lbl()
            self.log(f"> GRID UPDATED → {self.city_name}  |  {len(self.selected_areas)} AREAS ACTIVE", "bright")

    def start_thread(self):
        if self.is_running:
            return
        if not self.selected_areas:
            messagebox.showwarning("> ERROR", "No areas selected.\nUse  [ 📍 SELECT CITY & AREAS ]  first.")
            return
        self.is_running = True
        self.start_btn.config(state=tk.DISABLED, fg=FG_DIM)
        self.stop_btn.config(state=tk.NORMAL, fg=FG, bg=BG)
        self.console.config(state=tk.NORMAL)
        self.console.delete("1.0", tk.END)
        self.console.config(state=tk.DISABLED)
        self._set_status("SCANNING", 0, "INITIALIZING")
        threading.Thread(target=self._run_scraper, daemon=True).start()

    def stop_scraper(self):
        self.is_running = False
        self.log("> ABORT SIGNAL SENT — finishing current card and saving checkpoint...", "warning")
        self.stop_btn.config(state=tk.DISABLED, fg=FG_DIM)
        self._set_status("ABORTING")

    def open_folder(self):
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        out_dir  = os.path.join(root_dir, 'output')
        os.makedirs(out_dir, exist_ok=True)
        os.startfile(out_dir)

    def _on_close(self):
        if self.rain:
            self.rain.stop()
        self.root.destroy()

    # ── Core scraper ──────────────────────────────────────────────────────────
    def _run_scraper(self):
        city         = self.city_name
        areas        = list(self.selected_areas)
        scroll_depth = self.scroll_var.get()
        headless     = self.headless_var.get()
        cat_key      = self.category_var.get()
        cat_cfg      = CATEGORIES[cat_key]
        name_mode    = cat_cfg["name_mode"]
        search_tpl   = cat_cfg["search_template"]
        out_prefix   = cat_cfg["output_prefix"]
        cat_emoji    = cat_cfg.get("emoji", "◈")

        root_dir    = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        out_dir     = os.path.join(root_dir, 'output')
        os.makedirs(out_dir, exist_ok=True)
        output_file = os.path.join(out_dir, f"{out_prefix}_{city}_Leads.xlsx")

        self.log("══════════════════════════════════════════════════════════", "dim")
        self.log(f"> MISSION BRIEF", "bright")
        self.log(f"  {cat_emoji}  CATEGORY : {cat_key}", "success")
        self.log(f"  🏙️  CITY     : {city}", "success")
        self.log(f"  📍  AREAS    : {len(areas)}  |  DEPTH : {scroll_depth}", "success")
        self.log(f"  📁  OUTPUT   : {output_file}", "dim")
        self.log(f"  🗂️  TARGETS  : {', '.join(areas[:5])}{'...' if len(areas) > 5 else ''}", "dim")
        self.log("──────────────────────────────────────────────────────────", "dim")

        results:      list  = []
        seen_urls:    set   = set()
        seen_phones:  set   = set()

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=headless)
                context = browser.new_context(user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ))
                page = context.new_page()

                for ai, area in enumerate(areas, 1):
                    if not self.is_running:
                        self.log("> ABORT — halting area loop.", "warning")
                        break

                    query = search_tpl.format(area=area, city=city)
                    self.root.after(0, lambda a=area, n=len(results): self._set_status("SCANNING", n, a))
                    self.log(f"> [{ai:>2}/{len(areas)}]  {query}", "dim")

                    url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}"
                    try:
                        page.goto(url, timeout=30000)
                        time.sleep(3.5)
                    except Exception:
                        self.log(f"  ⚠  TIMEOUT → '{area}' — SKIPPING", "warning")
                        continue

                    self.log(f"  > SCROLLING {scroll_depth}× ...", "dim")
                    for _ in range(scroll_depth):
                        if not self.is_running:
                            break
                        page.mouse.wheel(0, 3500)
                        time.sleep(1.1)

                    listings = page.locator('a[href*="/maps/place/"]').all()
                    self.log(f"  > {len(listings)} CARDS DETECTED — EXTRACTING PROFILES ...", "dim")

                    for listing in listings[:50]:
                        if not self.is_running:
                            break
                        try:
                            href = listing.get_attribute("href")
                            if not href:
                                continue
                            clean_url = href.split("?")[0]
                            if clean_url in seen_urls:
                                continue
                            seen_urls.add(clean_url)

                            card_txt     = listing.inner_text() or ""
                            is_sponsored = "Yes" if ("Sponsored" in card_txt or card_txt[:5].strip() == "Ad") else "No"

                            raw_name = listing.get_attribute("aria-label") or ""
                            if not raw_name or raw_name.strip() == "Results":
                                ne = page.locator('h1[class*="fontHeadlineLarge"]').first
                                raw_name = ne.inner_text().strip() if ne.count() > 0 else ""

                            listing.click()
                            time.sleep(1.6)

                            pe    = page.locator('button[data-item-id^="phone:"]').first
                            phone = ""
                            if pe.count() > 0:
                                phone = re.sub(r"[^\d\+\-\s]", "", pe.inner_text().replace("Phone: ", "")).replace("\n", " ").strip()
                            if phone and phone in seen_phones:
                                continue
                            if phone:
                                seen_phones.add(phone)

                            ae      = page.locator('button[data-item-id="address"]').first
                            address = ""
                            if ae.count() > 0:
                                address = re.sub(r"[^\w\s\.,\-\/()]", "", ae.inner_text().replace("Address: ", "")).replace("\n", " ").strip()

                            re_el  = page.locator('div.F7nice span[aria-hidden="true"]').first
                            rating = re_el.inner_text().strip() if re_el.count() > 0 else "N/A"

                            rv_el   = page.locator('div.F7nice span[aria-label*="reviews"]').first
                            reviews = rv_el.inner_text().replace("(","").replace(")","").strip() if rv_el.count() > 0 else "0"

                            we_el   = page.locator('a[data-item-id="authority"]').first
                            website = we_el.get_attribute("href") if we_el.count() > 0 else "No Website"
                            email_address = extract_emails_from_website(website)

                            first_name, surname = parse_lead_name(raw_name, name_mode)

                            results.append({
                                "City": city, "Area": area, "Category": cat_key,
                                "First Name": first_name if first_name else raw_name,
                                "Surname": surname, "Business Name": raw_name,
                                "Mobile Number": phone if phone else "No Phone Listed",
                                "Address": address,
                                "Rating": f"{rating} ★" if rating != "N/A" else "No Rating",
                                "Total Reviews": reviews,
                                "Website URL": website if website else "No Website",
                                "Email Address": email_address,
                                "Running Ads?": is_sponsored,
                                "Google Maps Link": clean_url,
                            })

                            fn_disp = (first_name or raw_name)[:14]
                            sn_disp = surname[:10]
                            ph_disp = (phone or "N/A")[:13]
                            em_disp = email_address[:18]
                            self.log(
                                f"  ✅  [{len(results):>4}]  {fn_disp:<14} {sn_disp:<10}  "
                                f"📱 {ph_disp:<13}  📧 {em_disp:<18}  ⭐ {rating}  📢 {is_sponsored}",
                                "success"
                            )
                            self.root.after(0, lambda n=len(results): self._set_status(leads=n))

                        except Exception:
                            continue

                    if results:
                        save_leads_to_file(results, output_file)
                        self.log(f"  💾  CHECKPOINT → {len(results)} LEADS SAVED TO DISK", "save")

                browser.close()

        except Exception as exc:
            self.log(f"> ❌  EXECUTION ERROR: {exc}", "error")

        self.root.after(0, lambda: self._scrape_done(results, output_file, city, cat_key, len(areas)))

    def _scrape_done(self, results, output_file, city, cat_key, n_areas):
        self.is_running = False
        self.start_btn.config(state=tk.NORMAL, fg=FG)
        self.stop_btn.config(state=tk.DISABLED, fg=FG_DIM)

        if results:
            self.log("══════════════════════════════════════════════════════════", "dim")
            self.log(f">  MISSION  COMPLETE", "bright")
            self.log(f"   {len(results)} UNIQUE LEADS EXTRACTED & SAVED", "bright")
            self.log(f"   FILE → {output_file}", "save")
            self.log("══════════════════════════════════════════════════════════", "dim")
            self._set_status("COMPLETE", len(results), "DONE")
            log_run(city, n_areas, len(results), output_file, status="Success")
        else:
            self.log("> MISSION ENDED — 0 RESULTS RECORDED", "warning")
            self._set_status("IDLE", 0, "---")

        messagebox.showinfo(
            "◈ MISSION COMPLETE",
            f"Category : {cat_key}\n"
            f"City     : {city}\n"
            f"Areas    : {n_areas}\n"
            f"Leads    : {len(results)}\n\n"
            f"Saved →\n{output_file}"
        )


# =============================================================================
# ENTRY POINT
# =============================================================================
def main():
    root = tk.Tk()
    ScraperApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
