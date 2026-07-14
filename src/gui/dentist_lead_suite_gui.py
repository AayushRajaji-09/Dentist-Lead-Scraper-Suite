import os
import re
import sys
import threading
import time
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import pandas as pd
from playwright.sync_api import sync_playwright
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

try:
    from src.utils.run_logger import log_run
except ImportError:
    try:
        from run_logger import log_run
    except ImportError:
        def log_run(*args, **kwargs):
            pass

# =========================================================
# TOP COMMERCIAL AREAS FOR INDIAN CITIES (AUTO-DISCOVERY)
# =========================================================
TOP_INDIAN_AREAS = {
    "Ahmedabad": [
        "Satellite", "Navrangpura", "Vastrapur", "Maninagar", "Bopal",
        "Thaltej", "Gota", "Chandkheda", "Prahlad Nagar", "CG Road",
        "Sindhu Bhavan Road", "SG Highway"
    ],
    "Mumbai": [
        "Bandra West", "Andheri West", "Borivali West", "Dadar West", "Malad West",
        "Thane West", "Powai", "Juhu", "Colaba", "Lower Parel", "Goregaon West", "Chembur"
    ],
    "Surat": [
        "Adajan", "Vesu", "Ring Road", "Piplod", "Varachha",
        "City Light", "Ghod Dod Road", "Althan", "Katargam", "Pal"
    ],
    "Pune": [
        "Kothrud", "Baner", "Viman Nagar", "Wakad", "Hinjewadi",
        "Hadapsar", "Kalyani Nagar", "Aundh", "Shivaji Nagar", "Koregaon Park"
    ],
    "Bangalore": [
        "Koramangala", "Indiranagar", "Whitefield", "HSR Layout", "Jayanagar",
        "JP Nagar", "Electronic City", "Marathahalli", "Malleshwaram", "MG Road"
    ],
    "Delhi": [
        "Connaught Place", "South Extension", "Greater Kailash", "Rajouri Garden", "Rohini",
        "Saket", "Dwarka", "Vasant Kunj", "Karol Bagh", "Laxmi Nagar"
    ],
    "Hyderabad": [
        "Banjara Hills", "Jubilee Hills", "Gachibowli", "Madhapur", "Hitec City",
        "Kondapur", "Kukatpally", "Secunderabad", "Begumpet", "Manikonda"
    ],
    "Kolkata": [
        "Salt Lake", "Park Street", "Ballygunge", "Alipore", "New Town",
        "Bhawanipur", "Jadavpur", "Tollygunge", "Rajarhat", "Shyambazar"
    ],
    "Chennai": [
        "Anna Nagar", "T Nagar", "Adyar", "Velachery", "Mylapore",
        "Nungambakkam", "Besant Nagar", "OMR", "Porur", "Guindy"
    ],
    "Jaipur": [
        "Malviya Nagar", "Vaishali Nagar", "C Scheme", "Raja Park", "Mansarovar",
        "Bani Park", "Tonk Road", "Civil Lines"
    ]
}


def get_areas_for_city(city_name):
    """
    Returns top commercial areas for a known city, or generates dynamic search vectors.
    """
    clean_city = city_name.strip().title()
    if clean_city in TOP_INDIAN_AREAS:
        return TOP_INDIAN_AREAS[clean_city]
    # Fallback dynamic vectors for any custom city
    return [
        f"Central {clean_city}", f"North {clean_city}", f"South {clean_city}",
        f"East {clean_city}", f"West {clean_city}", f"Main Market {clean_city}",
        f"Ring Road {clean_city}", f"Civil Lines {clean_city}", f"MG Road {clean_city}",
        f"High Street {clean_city}"
    ]


def split_name_and_surname(full_text):
    if not full_text:
        return "", ""
    match = re.search(r"Dr\.?\s+([A-Za-z\u0900-\u097F]+)\s+([A-Za-z\u0900-\u097F]+)", full_text, re.IGNORECASE)
    if match:
        return match.group(1).capitalize(), match.group(2).capitalize()
    clean_words = re.sub(r"[^\w\s]", "", full_text).split()
    if len(clean_words) >= 2:
        return clean_words[0].capitalize(), clean_words[1].capitalize()
    elif len(clean_words) == 1:
        return clean_words[0].capitalize(), ""
    return full_text, ""


class ScraperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 Antigravity Dentist Lead Scraper Suite v2.0")
        self.root.geometry("780x640")
        self.root.minsize(650, 500)
        self.is_running = False

        # Apply modern ttk styling
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TLabel", font=("Segoe UI", 10))
        self.style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=6)
        self.style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground="#0f172a")

        self.setup_ui()

    def setup_ui(self):
        # Header Frame
        header_frame = ttk.Frame(self.root, padding="15 15 15 5")
        header_frame.pack(fill=tk.X)
        ttk.Label(header_frame, text="🦷 Dentist Lead Generation & Profiling Suite", style="Header.TLabel").pack(anchor=tk.W)
        ttk.Label(header_frame, text="Extract First/Last Names, Mobile Numbers, Ratings, Reviews, Website & Ad Status seamlessly.", foreground="#475569").pack(anchor=tk.W, pady=(3, 0))

        # Control Panel
        control_outer = ttk.LabelFrame(self.root, text=" ⚙️ Scraper Settings ", padding=15)
        control_outer.pack(fill=tk.X, padx=15, pady=10)
        
        control_frame = tk.Frame(control_outer)
        control_frame.pack(fill=tk.BOTH, expand=True)

        # City Input
        ttk.Label(control_frame, text="Target City Name:").grid(row=0, column=0, sticky=tk.W, pady=8)
        self.city_var = tk.StringVar(value="Mumbai")
        self.city_entry = ttk.Entry(control_frame, textvariable=self.city_var, width=36, font=("Segoe UI", 12))
        self.city_entry.grid(row=0, column=1, sticky=tk.W, padx=10, pady=8, ipady=3)

        # Areas Limit
        ttk.Label(control_frame, text="Areas to Scrape:").grid(row=0, column=2, sticky=tk.W, padx=(15, 5), pady=8)
        self.areas_var = tk.IntVar(value=6)
        self.areas_spin = ttk.Spinbox(control_frame, from_=1, to=20, textvariable=self.areas_var, width=10, font=("Segoe UI", 12))
        self.areas_spin.grid(row=0, column=3, sticky=tk.W, pady=8, ipady=3)

        # Scroll Depth
        ttk.Label(control_frame, text="Scroll Depth (Pages):").grid(row=1, column=0, sticky=tk.W, pady=8)
        self.scroll_var = tk.IntVar(value=10)
        self.scroll_spin = ttk.Spinbox(control_frame, from_=3, to=40, textvariable=self.scroll_var, width=10, font=("Segoe UI", 12))
        self.scroll_spin.grid(row=1, column=1, sticky=tk.W, padx=10, pady=8, ipady=3)

        # Checkboxes
        self.headless_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(control_frame, text="Run in Background (Headless Browser)", variable=self.headless_var).grid(row=1, column=2, columnspan=2, sticky=tk.W, padx=(15, 0), pady=5)

        # Action Buttons
        btn_frame = ttk.Frame(self.root, padding="15 5 15 10")
        btn_frame.pack(fill=tk.X)
        self.start_btn = ttk.Button(btn_frame, text="▶ Start Scraping & Profiling", command=self.start_thread)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.stop_btn = ttk.Button(btn_frame, text="⏹ Stop Scraper", command=self.stop_scraper, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=10)

        self.open_folder_btn = ttk.Button(btn_frame, text="📁 Open Output Folder", command=self.open_folder)
        self.open_folder_btn.pack(side=tk.RIGHT)

        # Log Terminal
        log_outer = ttk.LabelFrame(self.root, text=" 🖥️ Live Activity Log & Profiling Console ", padding=10)
        log_outer.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        log_frame = tk.Frame(log_outer)
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.console = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, font=("Consolas", 9), background="#0f172a", foreground="#38bdf8", state=tk.DISABLED)
        self.console.pack(fill=tk.BOTH, expand=True)

    def log(self, message):
        self.console.config(state=tk.NORMAL)
        timestamp = time.strftime("[%H:%M:%S] ")
        self.console.insert(tk.END, timestamp + message + "\n")
        self.console.see(tk.END)
        self.console.config(state=tk.DISABLED)

    def start_thread(self):
        if self.is_running:
            return
        self.is_running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.console.config(state=tk.NORMAL)
        self.console.delete("1.0", tk.END)
        self.console.config(state=tk.DISABLED)

        threading.Thread(target=self.run_scraper, daemon=True).start()

    def stop_scraper(self):
        self.is_running = False
        self.log("⚠️ Stopping scraper... Finishing current operation and saving checkpoint...")
        self.stop_btn.config(state=tk.DISABLED)

    def open_folder(self):
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        out_dir = os.path.join(root_dir, 'output')
        os.makedirs(out_dir, exist_ok=True)
        os.startfile(out_dir)

    def run_scraper(self):
        try:
            city = self.city_var.get().strip().title()
        except tk.TclError:
            city = "Mumbai"
        if not city:
            city = "Mumbai"
            
        try:
            areas_limit = int(self.areas_spin.get())
        except (ValueError, tk.TclError):
            areas_limit = 6
            
        try:
            scroll_depth = int(self.scroll_spin.get())
        except (ValueError, tk.TclError):
            scroll_depth = 10
            
        try:
            headless = self.headless_var.get()
        except tk.TclError:
            headless = False

        areas = get_areas_for_city(city)[:areas_limit]
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        out_dir = os.path.join(root_dir, 'output')
        os.makedirs(out_dir, exist_ok=True)
        output_file = os.path.join(out_dir, f"Dentists_{city}_Profiled_Directory.xlsx")

        self.log(f"🚀 Initializing Lead Scraper for City: '{city}' across {len(areas)} areas.")
        self.log(f"📋 Areas targeted: {', '.join(areas)}")

        results = []
        seen_urls = set()
        seen_phones = set()

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=headless)
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
                page = context.new_page()

                for area_idx, area in enumerate(areas, 1):
                    if not self.is_running:
                        break

                    search_query = f"Dentist in {area}, {city}"
                    self.log(f"\n📍 [{area_idx}/{len(areas)}] Searching Area: '{area}'...")
                    search_url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}"

                    try:
                        page.goto(search_url, timeout=30000)
                        time.sleep(3.5)
                    except Exception:
                        self.log(f"  ⚠️ Timeout loading area '{area}', skipping...")
                        continue

                    # Deep Scrolling
                    self.log(f"  📜 Scrolling {scroll_depth} times to discover clinic cards...")
                    for _ in range(scroll_depth):
                        if not self.is_running:
                            break
                        page.mouse.wheel(0, 3500)
                        time.sleep(1.1)

                    listings = page.locator('a[href*="/maps/place/"]').all()
                    self.log(f"  📋 Found {len(listings)} cards in {area}. Extracting full profiles...")

                    for idx, listing in enumerate(listings[:50]):
                        if not self.is_running:
                            break
                        try:
                            url = listing.get_attribute("href")
                            if not url:
                                continue
                            clean_url = url.split("?")[0]
                            if clean_url in seen_urls:
                                continue
                            seen_urls.add(clean_url)

                            # Check Sponsored Ads Badge on Card
                            card_text = listing.inner_text() or ""
                            is_sponsored = "Yes" if ("Sponsored" in card_text or "Ad" in card_text[:5]) else "No"

                            # 1. Clinic Name
                            raw_name = listing.get_attribute("aria-label") or ""
                            if not raw_name or raw_name.strip() == "Results":
                                name_elem = page.locator('h1[class*="fontHeadlineLarge"]').first
                                raw_name = name_elem.inner_text().strip() if name_elem.count() > 0 else ""

                            listing.click()
                            time.sleep(1.6)

                            # 2. Phone / Mobile
                            phone_elem = page.locator('button[data-item-id^="phone:"]').first
                            phone = ""
                            if phone_elem.count() > 0:
                                phone = phone_elem.inner_text().replace("Phone: ", "")
                                phone = re.sub(r"[^\d\+\-\s]", "", phone).replace("\n", " ").strip()

                            if phone and phone in seen_phones:
                                continue
                            if phone:
                                seen_phones.add(phone)

                            # 3. Address
                            address_elem = page.locator('button[data-item-id="address"]').first
                            address = ""
                            if address_elem.count() > 0:
                                address = address_elem.inner_text().replace("Address: ", "")
                                address = re.sub(r"[^\w\s\.,\-\/()]", "", address).replace("\n", " ").strip()

                            # 4. Rating & Reviews
                            rating_elem = page.locator('div.F7nice span[aria-hidden="true"]').first
                            rating = rating_elem.inner_text().strip() if rating_elem.count() > 0 else "N/A"

                            reviews_elem = page.locator('div.F7nice span[aria-label*="reviews"]').first
                            reviews = reviews_elem.inner_text().replace("(", "").replace(")", "").strip() if reviews_elem.count() > 0 else "0 reviews"

                            # 5. Website
                            web_elem = page.locator('a[data-item-id="authority"]').first
                            website = web_elem.get_attribute("href") if web_elem.count() > 0 else "No Website"

                            first_name, surname = split_name_and_surname(raw_name)

                            results.append({
                                "City": city,
                                "Area": area,
                                "First Name": first_name if first_name else raw_name,
                                "Surname": surname,
                                "Clinic Title": raw_name,
                                "Mobile Number": phone if phone else "No Phone Listed",
                                "Address": address,
                                "Rating": f"{rating} ★" if rating != "N/A" else "No Rating",
                                "Total Reviews": reviews,
                                "Website URL": website,
                                "Running Ads (Sponsored)?": is_sponsored,
                                "Google Location Link": clean_url
                            })

                            self.log(f"    ✅ [{len(results)}] {first_name} {surname} | 📱 {phone if phone else 'N/A'} | ⭐ {rating} | 📢 Ads: {is_sponsored}")

                        except Exception:
                            continue

                    # Live Checkpoint
                    if results:
                        pd.DataFrame(results).to_excel(output_file, index=False)
                        self.log(f"  💾 Checkpoint Saved: {len(results)} profiled leads -> '{output_file}'")

                browser.close()

        except Exception as e:
            self.log(f"\n❌ Error during execution: {e}")

        finally:
            if 'results' in locals() and results:
                self.log(f"\n🎉 SCRAPING COMPLETE! Total unique profiled leads saved: {len(results)}")
                self.log(f"📁 Output File: {os.path.abspath(output_file)}")
                # Log run telemetry
                log_run(city, len(areas), len(results), output_file, status="Success")
                # Showing message box safely
                self.root.after(0, lambda: messagebox.showinfo("Scraping Complete", f"Successfully extracted {len(results)} profiled dentist leads for {city}!\n\nSaved to: {output_file}"))
            elif 'results' in locals():
                self.log("\n⚠️ Scraper finished with 0 results recorded.")

            self.is_running = False
            self.root.after(0, lambda: self.start_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.stop_btn.config(state=tk.DISABLED))


def main():
    root = tk.Tk()
    app = ScraperApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
