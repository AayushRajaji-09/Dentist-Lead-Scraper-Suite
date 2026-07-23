#!/usr/bin/env python3
"""
🚀 Antigravity Lead Scraper Suite v3.1 - Master Launcher
Multi-category Google Maps lead scraper.
  GUI  : python main.py
  CLI  : python main.py --cli
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
    else:
        print("🚀 Launching Antigravity Lead Scraper Suite v3.1 GUI...")
        from src.gui.dentist_lead_suite_gui import main as gui_main
        if callable(gui_main):
            gui_main()

if __name__ == "__main__":
    main()
