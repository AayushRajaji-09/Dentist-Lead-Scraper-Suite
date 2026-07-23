import csv
import json
import os
import socket
import getpass
import subprocess
import urllib.request
from datetime import datetime

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUTPUT_DIR = os.path.join(ROOT_DIR, 'output')
CONFIG_FILE = os.path.join(ROOT_DIR, 'config.json')
os.makedirs(OUTPUT_DIR, exist_ok=True)

LOG_JSON = os.path.join(OUTPUT_DIR, "run_history.json")
LOG_CSV = os.path.join(OUTPUT_DIR, "run_log.csv")


def get_discord_webhook_url():
    """Checks env var or config.json for DISCORD_WEBHOOK_URL."""
    url = os.environ.get("DISCORD_WEBHOOK_URL")
    if url:
        return url.strip()
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("DISCORD_WEBHOOK_URL", "").strip()
        except Exception:
            pass
    return ""


def send_discord_webhook(city_name, areas_count, leads_count, output_filename, status):
    """Sends a rich embedded notification card to Discord when a scrape finishes."""
    webhook_url = get_discord_webhook_url()
    if not webhook_url or not webhook_url.startswith("http"):
        return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    machine_info = f"{socket.gethostname()} ({getpass.getuser()})"

    embed = {
        "title": "🟢 Antigravity Scrape Mission Complete",
        "color": 65281,  # Matrix Green (#00FF41)
        "fields": [
            {"name": "🏙️ Target City", "value": str(city_name), "inline": True},
            {"name": "📍 Areas Scraped", "value": f"{areas_count} areas", "inline": True},
            {"name": "🎯 Leads Extracted", "value": f"**{leads_count}** leads", "inline": True},
            {"name": "📁 Output File", "value": f"`{os.path.basename(output_filename)}`", "inline": False},
            {"name": "💻 Operator Machine", "value": f"`{machine_info}`", "inline": True},
            {"name": "⏱️ Timestamp", "value": timestamp, "inline": True},
        ],
        "footer": {
            "text": "Antigravity Team Telemetry · Matrix Edition"
        }
    }

    payload = {
        "username": "Antigravity Lead Engine",
        "avatar_url": "https://cdn-icons-png.flaticon.com/512/2815/2815428.png",
        "embeds": [embed]
    }

    try:
        req = urllib.request.Request(
            webhook_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "User-Agent": "Antigravity-Engine/3.0"}
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            if resp.status in (200, 204):
                print("📡 Discord Team Notification Sent Successfully!")
    except Exception as e:
        print(f"⚠️ Discord webhook note: {e}")


def log_run(city_name, areas_count, leads_count, output_filename, status="Success"):
    """
    Logs scraping run metrics to JSON & CSV files, sends Discord alert, and auto-commits to Git.
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

    # 3. Send Discord Webhook Notification
    send_discord_webhook(city_name, areas_count, leads_count, output_filename, status)

    # 4. Auto-commit to Git
    try:
        subprocess.run(["git", "add", LOG_JSON, LOG_CSV], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        commit_msg = f"Auto Log Run: Scraped {leads_count} leads across {areas_count} areas in {city_name} ({timestamp})"
        res = subprocess.run(["git", "commit", "-m", commit_msg], check=False, capture_output=True, text=True)
        if res.returncode == 0:
            print(f"🔒 Git Auto-Commit Successful: '{commit_msg}'")
        else:
            pass
    except Exception as e:
        print(f"⚠️ Git logging note: {e}")


if __name__ == "__main__":
    # Quick self-test
    log_run("Ahmedabad (Test)", 10, 250, "Dentists_Ahmedabad_Complete_Directory.xlsx")

