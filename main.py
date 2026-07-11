#!/usr/bin/env python3
"""
🚀 Antigravity Dentist Lead Scraper Suite v2.0 - Master Launcher
Executes either the interactive GUI suite or the standalone CLI scraper.
"""
import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def main():
    if "--cli" in sys.argv or "--scraper" in sys.argv:
        print("Launching Headless CLI Dentist Scraper Engine...")
        from src.scraper.free_dentist_scraper import main as scraper_main
        if callable(scraper_main):
            scraper_main()
    else:
        print("Launching Interactive GUI Suite...")
        from src.gui.dentist_lead_suite_gui import main as gui_main
        if callable(gui_main):
            gui_main()

if __name__ == "__main__":
    main()
