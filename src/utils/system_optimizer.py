"""
⚡ Antigravity Lead Scraper Suite v3.1 — System Auto-Optimizer
Detects host OS, CPU cores, and screen resolution on startup.
Sets performance profile, font system, and injects boot diagnostics
into the Matrix console.
"""
import os
import sys


def auto_optimize_system(screen_width: int = 1920) -> dict:
    """
    Probes the host machine and returns an optimized configuration dict.
    Called once at application startup before the GUI is fully rendered.
    """
    cpus = os.cpu_count() or 4
    platform = sys.platform

    # ── 1. OS Detection & Font Selection ─────────────────────────────────────
    if platform == "darwin":  # macOS
        os_name = "macOS"
        font_ui    = "SF Pro Display"
        font_mono  = "Monaco"
        user_agent = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    elif platform == "win32":  # Windows
        os_name = "Windows"
        font_ui    = "Segoe UI"
        font_mono  = "Consolas"
        user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    else:  # Linux / Other
        os_name = "Linux"
        font_ui    = "DejaVu Sans"
        font_mono  = "Monospace"
        user_agent = (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )

    # ── 2. CPU-Based Performance Profile ─────────────────────────────────────
    if cpus <= 2:
        profile_name  = "ECO"
        scroll_depth  = 5
        http_timeout  = 3
    elif cpus <= 8:
        profile_name  = "BALANCED"
        scroll_depth  = 10
        http_timeout  = 4
    else:
        profile_name  = "TURBO"
        scroll_depth  = 15
        http_timeout  = 6

    # ── 3. Screen-Responsive Window Sizing ───────────────────────────────────
    if screen_width >= 1920:
        window_size = "1000x720"
    elif screen_width >= 1366:
        window_size = "880x640"
    else:
        window_size = "780x580"

    return {
        "os_name":      os_name,
        "platform":     platform,
        "cpus":         cpus,
        "profile_name": profile_name,
        "scroll_depth": scroll_depth,
        "http_timeout": http_timeout,
        "user_agent":   user_agent,
        "fonts": {
            "ui":   font_ui,
            "mono": font_mono,
        },
        "window_size": window_size,
    }
