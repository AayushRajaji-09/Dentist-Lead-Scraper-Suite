import os
import re
import time
import pandas as pd
from playwright.sync_api import sync_playwright

# ==========================================
# CONFIGURATION - TARGET CITY & AREAS
# ==========================================
CITY_NAME = "Ahmedabad"
AREAS = [
    "Satellite",
    "Navrangpura",
    "Vastrapur",
    "Maninagar",
    "Bopal",
    "Thaltej",
    "Gota",
    "Chandkheda",
    "Prahlad Nagar",
    "CG Road",
]
# ==========================================


def split_name_and_surname(full_text):
    """
    Cleans clinic/doctor titles and separates First Name and Surname cleanly.
    """
    if not full_text:
        return "", ""
    
    # Try matching explicit "Dr. Firstname Lastname" pattern
    match = re.search(
        r"Dr\.?\s+([A-Za-z\u0900-\u097F]+)\s+([A-Za-z\u0900-\u097F]+)",
        full_text,
        re.IGNORECASE,
    )
    if match:
        return match.group(1).capitalize(), match.group(2).capitalize()

    # Fallback splitting by space after removing special chars
    clean_words = re.sub(r"[^\w\s]", "", full_text).split()
    if len(clean_words) >= 2:
        return clean_words[0].capitalize(), clean_words[1].capitalize()
    elif len(clean_words) == 1:
        return clean_words[0].capitalize(), ""
    
    return full_text, ""


def scrape_complete_directory():
    results = []
    seen_urls = set()
    seen_phones = set()
    
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    out_dir = os.path.join(root_dir, 'output')
    os.makedirs(out_dir, exist_ok=True)
    output_filename = os.path.join(out_dir, f"Dentists_{CITY_NAME}_Complete_Directory.xlsx")
    print(f"\n🚀 Starting Multi-Area Deep Scraper across {len(AREAS)} areas of {CITY_NAME}!")
    print("---------------------------------------------------------")

    with sync_playwright() as p:
        # Launch browser (headless=False so you can watch Google Maps scroll visually)
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        for area_idx, area in enumerate(AREAS, 1):
            search_query = f"Dentist in {area}, {CITY_NAME}"
            print(f"\n📍 [{area_idx}/{len(AREAS)}] Searching Area: '{area}'...")
            
            search_url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}"
            try:
                page.goto(search_url, timeout=30000)
                time.sleep(4)
            except Exception as e:
                print(f"  ⚠️ Could not load area {area}, skipping...")
                continue

            # Scroll deep down the sidebar to load up to ~40-60 clinics per area
            print(f"  📜 Deep scrolling '{area}' listings...")
            for i in range(1, 16):
                page.mouse.wheel(0, 3500)
                time.sleep(1.2)

            # Find all clickable listing cards
            listings = page.locator('a[href*="/maps/place/"]').all()
            print(f"  📋 Found {len(listings)} listings in {area}. Extracting & deduplicating...")

            area_count = 0
            for idx, listing in enumerate(listings[:60]):  # Up to 60 clinics per area
                try:
                    url = listing.get_attribute("href")
                    if not url:
                        continue
                    clean_url = url.split("?")[0]
                    if clean_url in seen_urls:
                        continue
                    seen_urls.add(clean_url)

                    # 1. Extract Doctor/Clinic Name from card aria-label before clicking
                    raw_name = listing.get_attribute("aria-label") or ""
                    if not raw_name or raw_name.strip() == "Results":
                        name_elem = page.locator('h1[class*="fontHeadlineLarge"]').first
                        raw_name = name_elem.inner_text().strip() if name_elem.count() > 0 else ""

                    # Click on the card to view details
                    listing.click()
                    time.sleep(1.8)

                    # 2. Extract Phone/Mobile Number & clean map icons
                    phone_elem = page.locator('button[data-item-id^="phone:"]').first
                    phone = ""
                    if phone_elem.count() > 0:
                        phone = phone_elem.inner_text().replace("Phone: ", "")
                        phone = re.sub(r"[^\d\+\-\s]", "", phone).replace("\n", " ").strip()

                    # Deduplicate by exact phone number (if phone exists and already collected)
                    if phone and phone in seen_phones:
                        continue
                    if phone:
                        seen_phones.add(phone)

                    # 3. Extract Address & clean map icons
                    address_elem = page.locator('button[data-item-id="address"]').first
                    address = ""
                    if address_elem.count() > 0:
                        address = address_elem.inner_text().replace("Address: ", "")
                        address = re.sub(r"[^\w\s\.,\-\/()]", "", address).replace("\n", " ").strip()

                    # Split raw name into Name and Surname
                    first_name, surname = split_name_and_surname(raw_name)

                    results.append(
                        {
                            "Area": area,
                            "Name": first_name if first_name else raw_name,
                            "Surname": surname,
                            "Mobile Number": phone,
                            "Address": address,
                            "Google Location": clean_url,
                        }
                    )
                    
                    area_count += 1
                    print(f"    ✅ [{len(results)} total] {first_name} {surname} | 📱 {phone if phone else 'No Phone'}")

                except Exception as e:
                    continue

            # Live Checkpoint Save after each area completes!
            df = pd.DataFrame(results)
            df.to_excel(output_filename, index=False)
            print(f"  💾 Checkpoint saved: {len(results)} total unique clinics so far -> '{output_filename}'")

        browser.close()

    print("\n=========================================================")
    print(f"🎉 MASTER SCRAPING COMPLETE! Saved {len(results)} unique dentist records across {len(AREAS)} areas!")
    print(f"📁 File Location: {output_filename}")
    print("=========================================================\n")


if __name__ == "__main__":
    scrape_complete_directory()
