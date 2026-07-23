"""
categories.py — Central category configuration for Antigravity Lead Scraper Suite v3.0

Add new categories here; they will automatically appear in the GUI dropdown.
name_mode values:
  'doctor'   → tries Dr./CA prefix extraction, falls back to first+surname split
  'person'   → straight first+surname split (no prefix matching)
  'business' → keeps full raw name intact (no splitting)
"""

CATEGORIES = {
    "🦷 Dentists": {
        "search_template": "Dentist in {area}, {city}",
        "output_prefix": "Dentists",
        "name_mode": "doctor",
        "emoji": "🦷",
        "description": "Dental clinics & practitioners",
    },
    "🏠 Real Estate Agents": {
        "search_template": "Real Estate Agent in {area}, {city}",
        "output_prefix": "RealEstate",
        "name_mode": "person",
        "emoji": "🏠",
        "description": "Property brokers & real estate offices",
    },
    "✂️ Salons": {
        "search_template": "Salon in {area}, {city}",
        "output_prefix": "Salons",
        "name_mode": "business",
        "emoji": "✂️",
        "description": "Hair salons, beauty parlours & spas",
    },
    "📊 CA / Accountants": {
        "search_template": "Chartered Accountant in {area}, {city}",
        "output_prefix": "CA_Accountants",
        "name_mode": "doctor",
        "emoji": "📊",
        "description": "CAs, tax consultants & accounting firms",
    },
}

# Ordered list of display names for GUI dropdowns
CATEGORY_NAMES = list(CATEGORIES.keys())
