"""
campaign_storage.py — JSON persistence for Antigravity Lead Campaign Suite v2.0
Stores saved templates, signatures, SMTP settings, and campaign configuration.
"""
import os
import json
import time

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
CONFIG_DIR = os.path.join(PROJECT_ROOT, "config")
DATA_FILE = os.path.join(CONFIG_DIR, "campaign_data.json")

DEFAULT_TEMPLATES = {
    "Dental Intro": {
        "subject": "Increasing patient acquisition at {Business Name}",
        "body": "Hello {First Name},\n\nI noticed {Business Name} is listed in {City} with a solid Google rating of {Rating}.\n\nWe specialize in automated patient acquisition and AI-driven appointment reminders specifically for dental practices. Many clinics in {City} are seeing a 30% boost in recurring check-ups using our automated recall system.\n\nWould you be open to a quick 5-minute chat this week to see how it works for {Business Name}?\n\nBest regards,"
    },
    "AI Receptionist": {
        "subject": "24/7 AI Receptionist for {Business Name} — Never miss a patient call",
        "body": "Hi Dr. {Surname},\n\nWhen patients call {Business Name} after hours or during busy clinic times, unanswered calls often turn into lost appointments.\n\nOur voice AI receptionist integrates directly with dental booking systems to answer calls 24/7, answer common clinic questions, and book appointments instantly.\n\nAre you available for a brief 10-minute demo on Tuesday to test the AI voice live?\n\nWarm regards,"
    },
    "Clinic Follow-up": {
        "subject": "Following up: Dental automation for {Business Name}",
        "body": "Hello {First Name},\n\nI wanted to quickly follow up on my previous note regarding patient acquisition and workflow automation for {Business Name} in {City}.\n\nWe know running a busy clinic takes all your focus. If you'd like to see a quick 3-minute video walkthrough of how we save dental front desks 15 hours a week, just reply 'VIDEO' to this email.\n\nBest regards,"
    },
    "Pricing": {
        "subject": "Transparent pricing & ROI for {Business Name}",
        "body": "Hi {First Name},\n\nWe believe in 100% transparent pricing for dental practices. Our complete automated lead nurturing suite starts at just $199/month with zero setup fees and no long-term lock-in contracts.\n\nFor {Business Name}, our system typically pays for itself with just 1 or 2 new high-value dental implant or Invisalign patients per month.\n\nWould you like me to send over our complete feature & pricing brochure?\n\nBest,"
    },
    "Reminder": {
        "subject": "Quick reminder regarding {Business Name}'s online growth",
        "body": "Hello Dr. {Surname},\n\nJust a friendly check-in! As dental clinics in {City} continue expanding their digital presence, automated patient reviews and lead follow-ups have become essential.\n\nLet me know if you have 5 minutes this Thursday to discuss strategies tailored to {Business Name}.\n\nRegards,"
    },
    "Demo Invitation": {
        "subject": "Live 10-Minute VIP Demo Invitation for {Business Name}",
        "body": "Hi {First Name},\n\nYou are invited to a 1-on-1 personalized demo of the Antigravity Lead Growth Engine tailored specifically for {Business Name}.\n\nDuring this 10-minute session, we will show you:\n1. How to automatically nurture your Google Maps leads.\n2. How to convert missed calls into booked appointments.\n3. How to generate 5-star Google reviews on autopilot.\n\nSimply reply with your preferred day and time this week to lock in your session.\n\nSincerely,"
    }
}

DEFAULT_SIGNATURES = {
    "Founder / Default": "Nitin Kumar\nFounder & CEO | Antigravity AI Suite\n🌐 Website: https://antigravity.dev\n📱 Phone: +91 98765 43210\n🔗 LinkedIn: https://linkedin.com/in/nitinkumar"
}

DEFAULT_SMTP = {
    "host": "smtp.gmail.com",
    "port": 587,
    "user": "",
    "password": "",
    "ssl_mode": False,
    "max_per_hour": 100,
    "delay_min": 3,
    "delay_max": 8
}

class CampaignStorage:
    @staticmethod
    def ensure_storage():
        os.makedirs(CONFIG_DIR, exist_ok=True)
        if not os.path.exists(DATA_FILE):
            data = {
                "templates": DEFAULT_TEMPLATES,
                "signatures": DEFAULT_SIGNATURES,
                "smtp": DEFAULT_SMTP,
                "last_campaign": {}
            }
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            return data
        
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Ensure all keys exist
            if "templates" not in data or not data["templates"]:
                data["templates"] = DEFAULT_TEMPLATES
            if "signatures" not in data or not data["signatures"]:
                data["signatures"] = DEFAULT_SIGNATURES
            if "smtp" not in data:
                data["smtp"] = DEFAULT_SMTP
            else:
                for k, v in DEFAULT_SMTP.items():
                    if k not in data["smtp"]:
                        data["smtp"][k] = v
            if "last_campaign" not in data:
                data["last_campaign"] = {}
            return data
        except Exception:
            # Fallback if corrupted
            return {
                "templates": DEFAULT_TEMPLATES,
                "signatures": DEFAULT_SIGNATURES,
                "smtp": DEFAULT_SMTP,
                "last_campaign": {}
            }

    @classmethod
    def load(cls):
        return cls.ensure_storage()

    @classmethod
    def save(cls, data):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    @classmethod
    def get_templates(cls):
        return cls.load().get("templates", {})

    @classmethod
    def save_template(cls, name, subject, body):
        data = cls.load()
        data["templates"][name] = {"subject": subject, "body": body}
        cls.save(data)

    @classmethod
    def delete_template(cls, name):
        data = cls.load()
        if name in data.get("templates", {}):
            del data["templates"][name]
            cls.save(data)

    @classmethod
    def get_signatures(cls):
        return cls.load().get("signatures", {})

    @classmethod
    def save_signature(cls, name, text):
        data = cls.load()
        data["signatures"][name] = text
        cls.save(data)

    @classmethod
    def delete_signature(cls, name):
        data = cls.load()
        if name in data.get("signatures", {}):
            del data["signatures"][name]
            cls.save(data)

    @classmethod
    def get_smtp_config(cls):
        return cls.load().get("smtp", DEFAULT_SMTP)

    @classmethod
    def save_smtp_config(cls, smtp_dict):
        data = cls.load()
        data["smtp"].update(smtp_dict)
        cls.save(data)

    @classmethod
    def save_last_campaign(cls, campaign_info):
        data = cls.load()
        data["last_campaign"] = campaign_info
        cls.save(data)

    @classmethod
    def get_last_campaign(cls):
        return cls.load().get("last_campaign", {})
