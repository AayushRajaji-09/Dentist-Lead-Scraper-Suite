"""
⚡ Antigravity Lead Scraper Suite v3.1 — Headless CLI Scraper Engine
Independent CLI scraper supporting multi-area Google Maps search,
email extraction, system auto-optimization, and persistent deduplication.
"""
import os
import re
import sys
import time
from playwright.sync_api import sync_playwright

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

try:
    from src.utils.helpers import (
        save_leads_to_file, extract_emails_from_website, parse_lead_name
    )
    from src.utils.system_optimizer import auto_optimize_system
    from src.utils.run_logger import (
        load_seen_fingerprints, save_seen_fingerprints, make_lead_fingerprint
    )
except ImportError:
    from helpers import save_leads_to_file, extract_emails_from_website, parse_lead_name
    from system_optimizer import auto_optimize_system
    from run_logger import load_seen_fingerprints, save_seen_fingerprints, make_lead_fingerprint

# ==========================================
# CONFIGURATION - TARGET CITY & AREAS
# ==========================================
CITY_NAME = "Ahmedabad"
AREAS = [
    "Satellite", "Navrangpura", "Vastrapur", "Maninagar", "Bopal",
    "Thaltej", "Gota", "Chandkheda", "Prahlad Nagar", "CG Road",
]
# ==========================================


def scrape_complete_directory():
    sys_cfg = auto_optimize_system()
    results = []
    seen_urls = set()
    seen_phones = set()
    seen_fingerprints = load_seen_fingerprints(CITY_NAME)

    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    out_dir = os.path.join(root_dir, 'output')
    os.makedirs(out_dir, exist_ok=True)
    output_filename = os.path.join(out_dir, f"Dentists_{CITY_NAME}_Complete_Directory.xlsx")

    print(f"\n🚀 Starting Antigravity Lead Scraper Suite v3.1 CLI Engine!")
    print(f"💻 System Profile: {sys_cfg['os_name']} | {sys_cfg['cpus']}-Core CPU | {sys_cfg['profile_name']} Mode")
    print(f"📍 Target: {len(AREAS)} areas in {CITY_NAME}")
    print(f"🔁 Dedup Registry: {len(seen_fingerprints)} previously seen leads loaded")
    print("---------------------------------------------------------")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(user_agent=sys_cfg["user_agent"])
        page = context.new_page()

        for area_idx, area in enumerate(AREAS, 1):
            search_query = f"Dentist in {area}, {CITY_NAME}"
            print(f"\n📍 [{area_idx}/{len(AREAS)}] Searching Area: '{area}'...")

            search_url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}"
            try:
                page.goto(search_url, timeout=30000)
                time.sleep(4)
            except Exception:
                print(f"  ⚠️ Could not load area {area}, skipping...")
                continue

            print(f"  📜 Scrolling '{area}' listings (depth={sys_cfg['scroll_depth']})...")
            for _ in range(sys_cfg['scroll_depth']):
                page.mouse.wheel(0, 3500)
                time.sleep(1.1)

            listings = page.locator('a[href*="/maps/place/"]').all()
            print(f"  📋 Found {len(listings)} listings in {area}. Extracting profiles...")

            for listing in listings[:60]:
                try:
                    url = listing.get_attribute("href")
                    if not url:
                        continue
                    clean_url = url.split("?")[0]
                    if clean_url in seen_urls:
                        continue
                    seen_urls.add(clean_url)

                    raw_name = listing.get_attribute("aria-label") or ""
                    if not raw_name or raw_name.strip() == "Results":
                        name_elem = page.locator('h1[class*="fontHeadlineLarge"]').first
                        raw_name = name_elem.inner_text().strip() if name_elem.count() > 0 else ""

                    listing.click()
                    time.sleep(1.6)

                    phone_elem = page.locator('button[data-item-id^="phone:"]').first
                    phone = ""
                    if phone_elem.count() > 0:
                        phone = phone_elem.inner_text().replace("Phone: ", "")
                        phone = re.sub(r"[^\d\+\-\s]", "", phone).replace("\n", " ").strip()

                    if phone and phone in seen_phones:
                        continue
                    if phone:
                        seen_phones.add(phone)

                    address_elem = page.locator('button[data-item-id="address"]').first
                    address = ""
                    if address_elem.count() > 0:
                        address = address_elem.inner_text().replace("Address: ", "")
                        address = re.sub(r"[^\w\s\.,\-\/()]", "", address).replace("\n", " ").strip()

                    web_elem = page.locator('a[data-item-id="authority"]').first
                    website = web_elem.get_attribute("href") if web_elem.count() > 0 else "No Website"
                    email_address = extract_emails_from_website(website, timeout=sys_cfg["http_timeout"])

                    first_name, surname = parse_lead_name(raw_name, mode="doctor")

                    fp = make_lead_fingerprint(phone, raw_name, clean_url)
                    if fp in seen_fingerprints:
                        print(f"    ⏩ Skip known: {(raw_name or 'Unknown')[:28]}")
                        continue
                    seen_fingerprints.add(fp)

                    results.append({
                        "Area": area,
                        "Name": first_name if first_name else raw_name,
                        "Surname": surname,
                        "Mobile Number": phone if phone else "No Phone Listed",
                        "Address": address,
                        "Website URL": website,
                        "Email Address": email_address,
                        "Google Location": clean_url,
                    })

                    print(f"    ✅ [{len(results)} total] {first_name} {surname} | 📱 {phone if phone else 'No Phone'} | 📧 {email_address}")

                except Exception:
                    continue

            save_leads_to_file(results, output_filename)
            save_seen_fingerprints(CITY_NAME, seen_fingerprints)
            print(f"  💾 Checkpoint saved: {len(results)} total unique clinics so far -> '{output_filename}'")

        browser.close()

    print("\n=========================================================")
    print(f"🎉 MASTER SCRAPING COMPLETE! Saved {len(results)} unique dentist records across {len(AREAS)} areas!")
    print(f"📁 File Location: {output_filename}")
    print("=========================================================\n")


def main():
    scrape_complete_directory()


if __name__ == "__main__":
    main()
