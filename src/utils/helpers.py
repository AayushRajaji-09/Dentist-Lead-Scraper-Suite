"""
⚡ Antigravity Lead Scraper Suite v3.1 — Shared Utility Helpers
Contains common file saving, email scraping, and name parsing functions
used by both GUI and CLI scraper modules.
"""
import re
import requests


def extract_emails_from_website(url: str, timeout: float = 4.0) -> str:
    """Fetches the target homepage via HTTP and extracts email addresses via regex."""
    if not url or url in ("No Website", "N/A"):
        return "No Email Found"
    try:
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        resp = requests.get(
            url,
            timeout=timeout,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )
        if resp.status_code == 200:
            emails = set(re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", resp.text))
            filtered = [
                e for e in emails
                if not e.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.wixpress.com', 'sentry.io'))
                and not e.lower().startswith(('sentry@', 'wix@'))
            ]
            if filtered:
                return filtered[0]
    except Exception:
        pass
    return "No Email Found"


def parse_lead_name(full_text: str, mode: str = "doctor") -> tuple[str, str]:
    """
    Cleans clinic/doctor titles and separates First Name and Surname cleanly.
    """
    if not full_text:
        return "", ""

    if mode == "doctor":
        match = re.search(
            r"Dr\.?\s+([A-Za-z\u0900-\u097F]+)\s+([A-Za-z\u0900-\u097F]+)",
            full_text,
            re.IGNORECASE,
        )
        if match:
            return match.group(1).capitalize(), match.group(2).capitalize()

    clean_words = re.sub(r"[^\w\s]", "", full_text).split()
    if len(clean_words) >= 2:
        return clean_words[0].capitalize(), clean_words[1].capitalize()
    elif len(clean_words) == 1:
        return clean_words[0].capitalize(), ""

    return full_text, ""


def save_leads_to_file(results: list, output_file: str):
    """
    Saves scraping results list to an Excel (.xlsx) file.
    Falls back to CSV format if Excel engine is unavailable.
    """
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
    except Exception:
        pass

    try:
        import pandas as pd
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
