import csv
import json
import os
import subprocess
from datetime import datetime

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUTPUT_DIR = os.path.join(ROOT_DIR, 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

LOG_JSON = os.path.join(OUTPUT_DIR, "run_history.json")
LOG_CSV = os.path.join(OUTPUT_DIR, "run_log.csv")


def log_run(city_name, areas_count, leads_count, output_filename, status="Success"):
    """
    Logs scraping run metrics to JSON & CSV files and auto-commits the log to Git.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = {
        "timestamp": timestamp,
        "city": city_name,
        "areas_scraped": areas_count,
        "leads_found": leads_count,
        "output_file": output_filename,
        "status": status,
    }

    # 1. Update JSON log
    history = []
    if os.path.exists(LOG_JSON):
        try:
            with open(LOG_JSON, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            history = []
    
    history.append(entry)
    with open(LOG_JSON, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4)

    # 2. Update CSV log
    file_exists = os.path.exists(LOG_CSV)
    with open(LOG_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "city", "areas_scraped", "leads_found", "output_file", "status"])
        if not file_exists:
            writer.writeheader()
        writer.writerow(entry)

    print(f"\n📊 Run metrics recorded to '{LOG_JSON}' & '{LOG_CSV}'.")

    # 3. Auto-commit to Git
    try:
        subprocess.run(["git", "add", LOG_JSON, LOG_CSV], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        commit_msg = f"Auto Log Run: Scraped {leads_count} leads across {areas_count} areas in {city_name} ({timestamp})"
        res = subprocess.run(["git", "commit", "-m", commit_msg], check=False, capture_output=True, text=True)
        if res.returncode == 0:
            print(f"🔒 Git Auto-Commit Successful: '{commit_msg}'")
        else:
            # Maybe no changes or identity not set
            pass
    except Exception as e:
        print(f"⚠️ Git logging note: {e}")


if __name__ == "__main__":
    # Quick self-test
    log_run("Ahmedabad (Test)", 10, 250, "Dentists_Ahmedabad_Complete_Directory.xlsx")
