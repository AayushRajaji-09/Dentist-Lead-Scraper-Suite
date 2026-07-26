#!/usr/bin/env python3
"""
🚀 Antigravity Lead Scraper Suite v3.1 - Master Launcher
Multi-category Google Maps lead scraper and B2B email outreach campaign engine.
  GUI         : python main.py
  CLI Scraper : python main.py --cli
  Campaign    : python main.py --campaign
"""
import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def main():
    if "--cli" in sys.argv or "--scraper" in sys.argv:
        print("🖥️  Launching Headless CLI Scraper Engine (v3.1)...")
        from src.scraper.free_dentist_scraper import main as scraper_main
        if callable(scraper_main):
            scraper_main()
    elif "--campaign" in sys.argv or "--emailer" in sys.argv or "--email" in sys.argv:
        print("✉️  Launching Antigravity Matrix Pro Outreach Campaign Engine (v2.0)...")
        from src.gui.email_sender_gui import main as emailer_main
        if callable(emailer_main):
            emailer_main()
    else:
        print("🚀 Launching Antigravity Lead Scraper Suite v3.1 GUI...")
        from src.gui.dentist_lead_suite_gui import main as gui_main
        if callable(gui_main):
            gui_main()

if __name__ == "__main__":
    main()
