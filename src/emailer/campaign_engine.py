"""
campaign_engine.py — Core Engine for Antigravity Lead Campaign Suite v2.0
Handles email validation, deduplication, personalization scoring, HTML/Hybrid MIME construction,
SMTP connection testing, anti-spam rate limiting, and campaign reporting.
"""
import os
import re
import time
import random
import smtplib
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import pandas as pd

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
GENERIC_DOMAINS_IGNORE = {"example.com", "test.com", "sample.com", "noemail.com", "na.com"}

def validate_email(email_str: str) -> bool:
    """
    Validates email syntax using regex and checks against placeholder domains.
    """
    if not email_str or not isinstance(email_str, str):
        return False
    email_str = email_str.strip()
    if not EMAIL_REGEX.match(email_str):
        return False
    domain = email_str.split("@")[-1].lower()
    if domain in GENERIC_DOMAINS_IGNORE:
        return False
    return True

def process_lead_list(df: pd.DataFrame, email_col: str, remove_duplicates: bool = True) -> tuple[pd.DataFrame, dict]:
    """
    Filters DataFrame for valid emails and optionally removes duplicates.
    Returns (cleaned_df, stats_dict).
    """
    total_loaded = len(df)
    if email_col not in df.columns:
        return pd.DataFrame(), {
            "loaded": total_loaded,
            "valid": 0,
            "invalid": total_loaded,
            "duplicate": 0
        }

    valid_mask = df[email_col].apply(lambda x: validate_email(str(x) if pd.notnull(x) else ""))
    invalid_count = int((~valid_mask).sum())
    
    valid_df = df[valid_mask].copy()
    valid_df["__clean_email__"] = valid_df[email_col].astype(str).str.strip().str.lower()
    
    duplicate_count = 0
    if remove_duplicates and not valid_df.empty:
        initial_valid = len(valid_df)
        valid_df = valid_df.drop_duplicates(subset=["__clean_email__"], keep="first")
        duplicate_count = initial_valid - len(valid_df)
    
    if "__clean_email__" in valid_df.columns:
        valid_df = valid_df.drop(columns=["__clean_email__"])

    stats = {
        "loaded": total_loaded,
        "valid": len(valid_df),
        "invalid": invalid_count,
        "duplicate": duplicate_count
    }
    return valid_df, stats

def score_template(subject: str, body: str) -> tuple[str, list[str]]:
    """
    Analyzes subject and body for dynamic variables and returns Personalisation Score + Suggestions.
    """
    combined = (subject or "") + " " + (body or "")
    placeholders = set(re.findall(r"\{([^{}]+)\}", combined))
    
    suggestions = []
    score = "Low"
    
    has_biz = "Business Name" in placeholders or "Company" in placeholders or "Clinic Name" in placeholders
    has_city = "City" in placeholders or "Area" in placeholders
    has_name = "First Name" in placeholders or "Surname" in placeholders or "Name" in placeholders
    has_rating = "Rating" in placeholders or "Total Reviews" in placeholders

    if not has_biz:
        suggestions.append("✓ Include {Business Name} to make the email feel tailored.")
    if not has_city:
        suggestions.append("✓ Reference {City} or {Area} to build local relevance.")
    if not has_name:
        suggestions.append("✓ Address the recipient by {First Name} or Dr. {Surname}.")
    if not has_rating:
        suggestions.append("✓ Mention their Google {Rating}⭐ for immediate social proof.")

    var_count = len(placeholders)
    if var_count >= 3 and (has_biz or has_name) and (has_city or has_rating):
        score = "High"
        if not suggestions:
            suggestions.append("🌟 Excellent! Template is highly personalized and optimized for conversions.")
    elif var_count >= 1:
        score = "Medium"
    else:
        score = "Low"
        suggestions.insert(0, "⚠ No dynamic placeholders detected! Email will appear as a generic bulk broadcast.")

    return score, suggestions

def render_template(text: str, row_data: dict) -> str:
    """
    Substitutes {Column Name} placeholders with actual values from row_data.
    """
    if not text:
        return ""
    
    def replace_match(match):
        key = match.group(1).strip()
        val = row_data.get(key, "")
        if pd.isnull(val) or val == "" or str(val).strip() == "N/A":
            # Try fallback aliases
            lower_key = key.lower()
            if "name" in lower_key and "first" in lower_key:
                val = row_data.get("Name", row_data.get("Business Name", "there"))
            elif "business" in lower_key or "clinic" in lower_key:
                val = row_data.get("Business Name", row_data.get("Company", "your clinic"))
            elif "city" in lower_key:
                val = row_data.get("City", "your area")
            elif "rating" in lower_key:
                val = row_data.get("Rating", "4.8 ★")
            else:
                val = ""
        return str(val).strip() if val != "" else f"[{key}]"

    return re.sub(r"\{([^{}]+)\}", replace_match, text)

def build_mime_message(sender_email: str, recipient_email: str, subject: str, body_text: str, is_html: bool = False, attachments: list = None) -> MIMEMultipart:
    """
    Constructs a complete MIME message supporting Plain Text, HTML, and Attachments.
    """
    msg = MIMEMultipart("alternative" if (is_html and not attachments) else "mixed")
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg["Subject"] = subject

    if is_html:
        # If user wrote basic text, wrap in clean professional HTML structure
        if "<html" not in body_text.lower() and "<body" not in body_text.lower():
            html_content = f"""
            <html>
              <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333333; max-width: 650px; margin: 0 auto; padding: 20px;">
                <div style="background-color: #ffffff; padding: 25px; border-radius: 8px; border: 1px solid #e0e0e0;">
                  {body_text.replace(chr(10), '<br>')}
                </div>
              </body>
            </html>
            """
        else:
            html_content = body_text
        
        # Attach plain text version as fallback
        plain_fallback = re.sub(r"<[^>]+>", "", body_text)
        msg.attach(MIMEText(plain_fallback, "plain", "utf-8"))
        msg.attach(MIMEText(html_content, "html", "utf-8"))
    else:
        msg.attach(MIMEText(body_text, "plain", "utf-8"))

    # Add attachments if provided
    if attachments:
        for file_path in attachments:
            if not file_path or not os.path.isfile(file_path):
                continue
            try:
                filename = os.path.basename(file_path)
                with open(file_path, "rb") as attachment_file:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment_file.read())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", f'attachment; filename="{filename}"')
                msg.attach(part)
            except Exception as e:
                print(f"[WARN] Could not attach file {file_path}: {e}")

    return msg

class SMTEngine:
    @staticmethod
    def test_connection(host: str, port: int, user: str, password: str, ssl_mode: bool = False) -> tuple[bool, str]:
        """
        Tests login credentials against the specified SMTP server.
        """
        try:
            port = int(port)
            if ssl_mode or port == 465:
                server = smtplib.SMTP_SSL(host, port, timeout=15)
            else:
                server = smtplib.SMTP(host, port, timeout=15)
                server.ehlo()
                if port == 587 or "gmail" in host.lower() or "outlook" in host.lower():
                    server.starttls()
                    server.ehlo()
            
            if user and password:
                server.login(user, password)
            server.quit()
            return True, f"✅ SMTP Connection Successful! Verified login for {user} on {host}:{port}."
        except smtplib.SMTPAuthenticationError:
            return False, "❌ Authentication Error: Invalid Password or User. For Gmail/Yahoo, make sure you use an App Password (not your regular account password)."
        except smtplib.SMTPConnectError:
            return False, f"❌ Connection Refused: Could not connect to {host} on port {port}. Check host and port."
        except Exception as e:
            return False, f"❌ SMTP Error: {str(e)}"

    @staticmethod
    def execute_campaign(
        leads_df: pd.DataFrame,
        email_col: str,
        subject_tpl: str,
        body_tpl: str,
        signature: str,
        smtp_config: dict,
        mode: str = "production",
        resume_from_idx: int = 0,
        is_html: bool = False,
        attachments: list = None,
        progress_callback = None,
        log_callback = None,
        stop_event = None,
        pause_event = None
    ) -> str:
        """
        Executes the campaign sending loop with rate limiting, anti-spam delay, and telemetry reporting.
        Returns path to the generated Campaign Report Excel file.
        """
        host = smtp_config.get("host", "smtp.gmail.com")
        port = int(smtp_config.get("port", 587))
        user = smtp_config.get("user", "")
        password = smtp_config.get("password", "")
        ssl_mode = smtp_config.get("ssl_mode", False)
        max_per_hour = int(smtp_config.get("max_per_hour", 100))
        delay_min = float(smtp_config.get("delay_min", 3.0))
        delay_max = float(smtp_config.get("delay_max", 8.0))

        if mode == "test":
            target_df = leads_df.iloc[:3].copy()
            if log_callback:
                log_callback(f"[MODE] 🧪 Running in TEST MODE — Restricted to first 3 leads.", "bright")
        elif mode == "resume":
            target_df = leads_df.iloc[resume_from_idx:].copy()
            if log_callback:
                log_callback(f"[MODE] ⏩ Running in RESUME MODE — Starting from lead #{resume_from_idx + 1}.", "bright")
        else:
            target_df = leads_df.copy()
            if log_callback:
                log_callback(f"[MODE] 🚀 Running in PRODUCTION MODE — Targeting all {len(target_df)} leads.", "bright")

        total_to_send = len(target_df)
        if total_to_send == 0:
            if log_callback:
                log_callback("[WARN] No leads available to send after filtering/slicing.", "warning")
            return ""

        # Connect to SMTP Server
        if log_callback:
            log_callback(f"[SMTP] Establishing connection to {host}:{port}...", "dim")
        try:
            if ssl_mode or port == 465:
                server = smtplib.SMTP_SSL(host, port, timeout=20)
            else:
                server = smtplib.SMTP(host, port, timeout=20)
                server.ehlo()
                if port == 587 or "gmail" in host.lower() or "outlook" in host.lower():
                    server.starttls()
                    server.ehlo()
            if user and password:
                server.login(user, password)
            if log_callback:
                log_callback(f"[SMTP] ✅ Connected and authenticated as {user}", "success")
        except Exception as e:
            if log_callback:
                log_callback(f"[ERROR] Fatal SMTP connection failure: {e}", "error")
            return ""

        # Sending Loop
        sent_timestamps = []
        results_log = []
        start_time = time.time()
        sent_count = 0
        failed_count = 0

        try:
            for idx, (row_idx, row) in enumerate(target_df.iterrows()):
                if stop_event and stop_event.is_set():
                    if log_callback:
                        log_callback("[ABORT] ⏹ Mission aborted by user.", "warning")
                    break

                # Handle Pausing
                while pause_event and pause_event.is_set():
                    if stop_event and stop_event.is_set():
                        break
                    time.sleep(0.5)
                if stop_event and stop_event.is_set():
                    break

                # Throttling / Rate Limiting Check (Max per hour)
                now = time.time()
                sent_timestamps = [t for t in sent_timestamps if now - t < 3600]
                if max_per_hour > 0 and len(sent_timestamps) >= max_per_hour:
                    oldest = sent_timestamps[0]
                    wait_seconds = int(3600 - (now - oldest) + 5)
                    if log_callback:
                        log_callback(f"[THROTTLE] ⏳ Hourly limit ({max_per_hour}/hr) reached! Pausing for {wait_seconds}s to protect domain reputation...", "warning")
                    while wait_seconds > 0:
                        if stop_event and stop_event.is_set():
                            break
                        time.sleep(min(1, wait_seconds))
                        wait_seconds -= 1
                    if stop_event and stop_event.is_set():
                        break
                    sent_timestamps = [t for t in sent_timestamps if time.time() - t < 3600]

                recipient = str(row.get(email_col, "")).strip()
                biz_name = str(row.get("Business Name", row.get("Name", recipient))).strip()
                row_dict = row.to_dict()

                # Render dynamic template
                full_body_tpl = body_tpl
                if signature and signature.strip():
                    full_body_tpl += "\n\n" + signature.strip()
                
                rendered_subject = render_template(subject_tpl, row_dict)
                rendered_body = render_template(full_body_tpl, row_dict)

                msg = build_mime_message(user, recipient, rendered_subject, rendered_body, is_html, attachments)

                # Execute Send
                status = "Success"
                error_msg = ""
                try:
                    server.sendmail(user, recipient, msg.as_string())
                    sent_timestamps.append(time.time())
                    sent_count += 1
                    if log_callback:
                        log_callback(f"[SEND] ✅ [{idx+1}/{total_to_send}] Sent -> {recipient} ({biz_name})", "success")
                except smtplib.SMTPRecipientsRefused as e:
                    status = "Bounced"
                    error_msg = str(e)
                    failed_count += 1
                    if log_callback:
                        log_callback(f"[BOUNCE] ⚠️ [{idx+1}/{total_to_send}] Recipient Refused -> {recipient}", "warning")
                except Exception as e:
                    status = "Failed"
                    error_msg = str(e)
                    failed_count += 1
                    if log_callback:
                        log_callback(f"[FAIL] ❌ [{idx+1}/{total_to_send}] Error sending to {recipient}: {error_msg}", "error")

                # Log record
                results_log.append({
                    "Row Index": row_idx,
                    "Target Email": recipient,
                    "Business Name": biz_name,
                    "Sent Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Delivery Status": status,
                    "Error Details": error_msg,
                    "Subject Used": rendered_subject
                })

                # Progress & Telemetry update
                if progress_callback:
                    elapsed = time.time() - start_time
                    avg_time = elapsed / (idx + 1)
                    rem_items = total_to_send - (idx + 1)
                    eta_sec = int(rem_items * avg_time) if rem_items > 0 else 0
                    progress_callback(idx + 1, total_to_send, sent_count, failed_count, elapsed, eta_sec)

                # Anti-spam randomized delay (skip after last item)
                if idx < total_to_send - 1 and not (stop_event and stop_event.is_set()):
                    delay = random.uniform(delay_min, delay_max)
                    time.sleep(delay)

        finally:
            try:
                server.quit()
            except Exception:
                pass
            if log_callback:
                log_callback("[SMTP] Connection closed safely.", "dim")

        # Generate Campaign Report
        out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'output'))
        os.makedirs(out_dir, exist_ok=True)
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(out_dir, f"Campaign_Report_{timestamp_str}.xlsx")
        
        if results_log:
            try:
                df_report = pd.DataFrame(results_log)
                df_report.to_excel(report_path, index=False)
                if log_callback:
                    log_callback(f"[REPORT] 📁 Campaign Telemetry Saved -> {report_path}", "save")
            except Exception as e:
                if log_callback:
                    log_callback(f"[WARN] Failed to write Excel report: {e}", "warning")
                report_path = ""
        else:
            report_path = ""

        return report_path
