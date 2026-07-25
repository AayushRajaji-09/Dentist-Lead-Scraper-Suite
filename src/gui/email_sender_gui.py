"""
email_sender_gui.py — Matrix Edition Lead Campaign Suite v2.0 GUI
A cyberpunk-styled, 4-tab professional email outreach application integrated into the Antigravity Suite.
"""
import os
import sys
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

try:
    from src.emailer.campaign_storage import CampaignStorage, DEFAULT_TEMPLATES, DEFAULT_SIGNATURES
    from src.emailer.campaign_engine import process_lead_list, score_template, render_template, SMTEngine
except ImportError:
    from campaign_storage import CampaignStorage, DEFAULT_TEMPLATES, DEFAULT_SIGNATURES
    from campaign_engine import process_lead_list, score_template, render_template, SMTEngine

# ── MATRIX PALETTE & FONTS ──────────────────────────────────────────────────
BG         = "#000000"
FG         = "#00FF41"   # Matrix Green
FG_BRIGHT  = "#AAFFAA"   # Highlight / Selected
FG_DIM     = "#004400"   # Muted / Borders
FG_WARN    = "#FFB000"   # Amber Warning
FG_ERR     = "#FF3333"   # Red Error
FG_CYAN    = "#00FFCC"   # Save / Checkpoint
BORDER     = "#002200"   # Frame Borders
SEL_CLR    = "#001800"   # Active Tab / Selected BG

MONO       = ("Courier New", 10)
MONO_B     = ("Courier New", 10, "bold")
MONO_SM    = ("Courier New", 8)
MONO_LG    = ("Courier New", 12, "bold")
MONO_XL    = ("Courier New", 16, "bold")

def mk_btn(parent, text: str, command, state=tk.NORMAL, width=None) -> tk.Button:
    btn = tk.Button(
        parent, text=text, command=command,
        bg=SEL_CLR if state == tk.NORMAL else "#000800",
        fg=FG if state == tk.NORMAL else FG_DIM,
        activebackground=FG, activeforeground=BG,
        font=MONO_B, relief=tk.SOLID, bd=1,
        highlightbackground=FG_DIM, highlightcolor=FG,
        highlightthickness=1, cursor="hand2",
        padx=10, pady=5, state=state
    )
    if width:
        btn.config(width=width)
    def _enter(e):
        if str(btn["state"]) != "disabled":
            btn.config(bg=FG, fg=BG, highlightbackground=FG)
    def _leave(e):
        if str(btn["state"]) != "disabled":
            btn.config(bg=SEL_CLR, fg=FG, highlightbackground=FG_DIM)
    btn.bind("<Enter>", _enter)
    btn.bind("<Leave>", _leave)
    return btn

class EmailSenderApp:
    def __init__(self, root=None):
        self.own_root = False
        if root is None:
            self.root = tk.Tk()
            self.own_root = True
        else:
            self.root = tk.Toplevel(root)
        
        self.root.title("✉️ ANTIGRAVITY MATRIX OUTREACH ENGINE v2.0")
        self.root.geometry("1100x780")
        self.root.configure(bg=BG)
        self.root.minsize(950, 680)

        # State Variables
        self.storage_data = CampaignStorage.load()
        self.raw_df = pd.DataFrame()
        self.valid_df = pd.DataFrame()
        self.stats = {"loaded": 0, "valid": 0, "invalid": 0, "duplicate": 0}
        self.current_preview_idx = 0
        self.attachments = []
        self.last_focus_widget = None

        # Campaign control flags
        self.is_running = False
        self.stop_event = threading.Event()
        self.pause_event = threading.Event()
        self.campaign_thread = None

        # Build UI
        self._apply_ttk_styles()
        self._build_header_dashboard()
        self._build_tab_navigation()
        self._build_tab_containers()

        # Build individual tab views
        self._build_tab1_loader()
        self._build_tab2_editor()
        self._build_tab3_smtp()
        self._build_tab4_campaign()

        # Switch to Tab 1 initially
        self.switch_tab(0)
        self._update_status_dashboard()

        if self.own_root:
            self.root.protocol("WM_DELETE_WINDOW", self._on_close)
            self.root.after(300, lambda: self.log("🚀 MATRIX OUTREACH ENGINE v2.0 INITIALIZED AND READY.", "bright"))

    def _on_close(self):
        if self.is_running:
            if messagebox.askyesno("Confirm Exit", "An email campaign is currently actively running! Abort mission and exit?"):
                self.stop_event.set()
                self.root.destroy()
        else:
            self.root.destroy()

    def _apply_ttk_styles(self):
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("Matrix.TCombobox",
            fieldbackground=BG, background=BG, foreground=FG,
            selectbackground=SEL_CLR, selectforeground=FG_BRIGHT,
            arrowcolor=FG, bordercolor=BORDER, insertcolor=FG
        )
        s.map("Matrix.TCombobox",
            fieldbackground=[("readonly", BG)],
            foreground=[("readonly", FG)],
            background=[("active", BORDER)]
        )

    # ── TOP STATUS DASHBOARD ──────────────────────────────────────────────────
    def _build_header_dashboard(self):
        hdr = tk.Frame(self.root, bg=BG, bd=1, relief=tk.SOLID, highlightbackground=BORDER, highlightthickness=1)
        hdr.pack(fill=tk.X, padx=10, pady=(10, 5))

        title_frm = tk.Frame(hdr, bg=BG)
        title_frm.pack(fill=tk.X, padx=12, pady=(8, 4))
        tk.Label(title_frm, text="  ◈  ANTIGRAVITY PRO OUTREACH CAMPAIGN ENGINE  ◈",
                 bg=BG, fg=FG_BRIGHT, font=MONO_XL).pack(side=tk.LEFT)
        self.status_pill = tk.Label(title_frm, text="[ SYSTEM IDLE ]", bg=SEL_CLR, fg=FG_BRIGHT, font=MONO_B, padx=8, pady=2)
        self.status_pill.pack(side=tk.RIGHT)

        # Dashboard grid
        grid_frm = tk.Frame(hdr, bg=SEL_CLR, pady=6, padx=12)
        grid_frm.pack(fill=tk.X, padx=10, pady=(0, 8))

        self.lbl_stat_loaded = tk.Label(grid_frm, text="LOADED LEADS: 0", bg=SEL_CLR, fg=FG, font=MONO_B)
        self.lbl_stat_loaded.grid(row=0, column=0, padx=15, sticky=tk.W)

        self.lbl_stat_ready = tk.Label(grid_frm, text="READY (VALID): 0", bg=SEL_CLR, fg=FG_CYAN, font=MONO_B)
        self.lbl_stat_ready.grid(row=0, column=1, padx=15, sticky=tk.W)

        self.lbl_stat_smtp = tk.Label(grid_frm, text="SMTP: NOT VERIFIED", bg=SEL_CLR, fg=FG_WARN, font=MONO_B)
        self.lbl_stat_smtp.grid(row=0, column=2, padx=15, sticky=tk.W)

        self.lbl_stat_score = tk.Label(grid_frm, text="TEMPLATE SCORE: LOW", bg=SEL_CLR, fg=FG_ERR, font=MONO_B)
        self.lbl_stat_score.grid(row=0, column=3, padx=15, sticky=tk.W)

    def _update_status_dashboard(self):
        self.lbl_stat_loaded.config(text=f"LOADED LEADS: {self.stats.get('loaded', 0)}")
        self.lbl_stat_ready.config(text=f"READY (VALID): {self.stats.get('valid', 0)}")

    # ── TAB NAVIGATION BAR ────────────────────────────────────────────────────
    def _build_tab_navigation(self):
        nav = tk.Frame(self.root, bg=BG)
        nav.pack(fill=tk.X, padx=10, pady=5)

        self.tab_buttons = []
        tab_names = [
            "[ 📁 1. LEAD LOADER & VALIDATION ]",
            "[ ✉️ 2. TEMPLATES, CHIPS & PREVIEW ]",
            "[ ⚙️ 3. SMTP & ANTI-SPAM SETTINGS ]",
            "[ 🚀 4. LIVE CAMPAIGN & ANALYTICS ]"
        ]
        for idx, name in enumerate(tab_names):
            btn = tk.Button(
                nav, text=name, font=MONO_B, relief=tk.FLAT, bd=0,
                bg=BG, fg=FG_DIM, activebackground=SEL_CLR, activeforeground=FG_BRIGHT,
                cursor="hand2", padx=12, pady=8,
                command=lambda i=idx: self.switch_tab(i)
            )
            btn.pack(side=tk.LEFT, padx=2)
            self.tab_buttons.append(btn)

    def switch_tab(self, tab_idx: int):
        for idx, btn in enumerate(self.tab_buttons):
            if idx == tab_idx:
                btn.config(bg=SEL_CLR, fg=FG_BRIGHT, relief=tk.SOLID, bd=1, highlightbackground=FG, highlightthickness=1)
                self.tab_frames[idx].pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
            else:
                btn.config(bg=BG, fg=FG_DIM, relief=tk.FLAT, bd=0, highlightthickness=0)
                self.tab_frames[idx].pack_forget()

    def _build_tab_containers(self):
        self.content_area = tk.Frame(self.root, bg=BG)
        self.content_area.pack(fill=tk.BOTH, expand=True)
        self.tab_frames = [
            tk.Frame(self.content_area, bg=BG),
            tk.Frame(self.content_area, bg=BG),
            tk.Frame(self.content_area, bg=BG),
            tk.Frame(self.content_area, bg=BG)
        ]

    # ── TAB 1: LEAD LOADER & VALIDATION ───────────────────────────────────────
    def _build_tab1_loader(self):
        frm = self.tab_frames[0]
        
        box_top = tk.LabelFrame(frm, text=" 📂 IMPORT SCRAPER LEADS OR SPREADSHEET ", bg=BG, fg=FG_BRIGHT, font=MONO_LG, bd=1, relief=tk.SOLID, padx=15, pady=15)
        box_top.pack(fill=tk.X, pady=(5, 15))

        top_row = tk.Frame(box_top, bg=BG)
        top_row.pack(fill=tk.X, pady=5)

        mk_btn(top_row, "[ 📂 SELECT EXCEL / CSV FILE ]", self.open_lead_file).pack(side=tk.LEFT, padx=(0, 15))
        self.lbl_filepath = tk.Label(top_row, text="No file selected...", bg=BG, fg=FG_DIM, font=MONO)
        self.lbl_filepath.pack(side=tk.LEFT, fill=tk.X, expand=True, anchor=tk.W)

        # Selector Row
        sel_row = tk.Frame(box_top, bg=BG)
        sel_row.pack(fill=tk.X, pady=10)

        tk.Label(sel_row, text="Target Email Column :", bg=BG, fg=FG, font=MONO_B).pack(side=tk.LEFT, padx=(0, 10))
        self.email_col_var = tk.StringVar()
        self.email_col_dropdown = ttk.Combobox(sel_row, textvariable=self.email_col_var, state="readonly", width=25, style="Matrix.TCombobox")
        self.email_col_dropdown.pack(side=tk.LEFT, padx=(0, 25))
        self.email_col_dropdown.bind("<<ComboboxSelected>>", lambda e: self.run_validation())

        self.remove_dups_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            sel_row, text="☑ Remove Duplicate Emails (Auto-Deduplicate)", variable=self.remove_dups_var,
            bg=BG, fg=FG, activebackground=BG, activeforeground=FG_BRIGHT,
            selectcolor=SEL_CLR, font=MONO_B, cursor="hand2", command=self.run_validation
        ).pack(side=tk.LEFT)

        # Statistics Panel
        box_stats = tk.LabelFrame(frm, text=" 📊 VALIDATION & DEDUPLICATION REPORT ", bg=BG, fg=FG_BRIGHT, font=MONO_LG, bd=1, relief=tk.SOLID, padx=15, pady=15)
        box_stats.pack(fill=tk.X, pady=(0, 15))

        stat_grid = tk.Frame(box_stats, bg=BG)
        stat_grid.pack(fill=tk.X)

        self.stat_lbl_tot = tk.Label(stat_grid, text="Loaded Rows: 0", bg=BG, fg=FG, font=MONO_LG, width=20, anchor=tk.W)
        self.stat_lbl_tot.grid(row=0, column=0, pady=5)

        self.stat_lbl_val = tk.Label(stat_grid, text="Valid Emails: 0", bg=BG, fg=FG_CYAN, font=MONO_LG, width=20, anchor=tk.W)
        self.stat_lbl_val.grid(row=0, column=1, pady=5)

        self.stat_lbl_inv = tk.Label(stat_grid, text="Invalid Syntax: 0", bg=BG, fg=FG_ERR, font=MONO_LG, width=20, anchor=tk.W)
        self.stat_lbl_inv.grid(row=1, column=0, pady=5)

        self.stat_lbl_dup = tk.Label(stat_grid, text="Duplicates Removed: 0", bg=BG, fg=FG_WARN, font=MONO_LG, width=20, anchor=tk.W)
        self.stat_lbl_dup.grid(row=1, column=1, pady=5)

        # Valid Leads Preview Table
        box_prev = tk.LabelFrame(frm, text=" 👀 VALID LEADS PREVIEW (TOP 15 RECORDS) ", bg=BG, fg=FG_BRIGHT, font=MONO_LG, bd=1, relief=tk.SOLID, padx=10, pady=10)
        box_prev.pack(fill=tk.BOTH, expand=True)

        self.leads_listbox = tk.Listbox(box_prev, bg=SEL_CLR, fg=FG, font=MONO_SM, bd=0, relief=tk.FLAT, selectbackground=FG_DIM)
        self.leads_listbox.pack(fill=tk.BOTH, expand=True)

    def open_lead_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Lead Spreadsheet",
            filetypes=[("Excel & CSV Files", "*.xlsx *.xls *.csv"), ("All Files", "*.*")]
        )
        if not file_path:
            return
        
        self.lbl_filepath.config(text=file_path, fg=FG_BRIGHT)
        try:
            if file_path.endswith(".csv"):
                self.raw_df = pd.read_csv(file_path)
            else:
                self.raw_df = pd.read_excel(file_path)
            
            cols = list(self.raw_df.columns)
            self.email_col_dropdown["values"] = cols
            
            # Auto-detect email column
            detected = ""
            for c in cols:
                cl = c.lower()
                if "email" in cl or "e-mail" in cl or "mail" in cl:
                    detected = c
                    break
            if not detected and cols:
                detected = cols[0]
            
            self.email_col_var.set(detected)
            self.run_validation()
            self.log(f"📁 Successfully loaded {len(self.raw_df)} rows from: {os.path.basename(file_path)}", "save")
        except Exception as e:
            messagebox.showerror("Error Loading File", f"Could not read spreadsheet:\n{e}")

    def run_validation(self):
        if self.raw_df.empty:
            return
        col = self.email_col_var.get()
        rem_dup = self.remove_dups_var.get()
        
        self.valid_df, self.stats = process_lead_list(self.raw_df, col, rem_dup)
        self._update_status_dashboard()

        # Update stats UI
        self.stat_lbl_tot.config(text=f"Loaded Rows: {self.stats['loaded']}")
        self.stat_lbl_val.config(text=f"Valid Emails: {self.stats['valid']}")
        self.stat_lbl_inv.config(text=f"Invalid Syntax: {self.stats['invalid']}")
        self.stat_lbl_dup.config(text=f"Duplicates Removed: {self.stats['duplicate']}")

        # Populate Preview Listbox
        self.leads_listbox.delete(0, tk.END)
        for idx, row in self.valid_df.head(15).iterrows():
            em = str(row.get(col, "")).strip()
            bn = str(row.get("Business Name", row.get("Name", "No Name"))).strip()
            ct = str(row.get("City", row.get("Area", ""))).strip()
            self.leads_listbox.insert(tk.END, f"  [{len(self.leads_listbox)+1:02d}] ✉️ {em:<28} | 🏥 {bn:<25} | 📍 {ct}")

    # ── TAB 2: TEMPLATES, CHIPS & PREVIEW ─────────────────────────────────────
    def _build_tab2_editor(self):
        frm = self.tab_frames[1]

        # Top Bar: Presets and Signatures
        top_row = tk.Frame(frm, bg=BG)
        top_row.pack(fill=tk.X, pady=(5, 10))

        tk.Label(top_row, text="Preset Template :", bg=BG, fg=FG, font=MONO_B).pack(side=tk.LEFT, padx=(0, 8))
        self.preset_var = tk.StringVar(value="Dental Intro")
        preset_box = ttk.Combobox(top_row, textvariable=self.preset_var, values=list(DEFAULT_TEMPLATES.keys()), state="readonly", width=18, style="Matrix.TCombobox")
        preset_box.pack(side=tk.LEFT, padx=(0, 10))
        mk_btn(top_row, "[ LOAD ]", self.load_preset_template).pack(side=tk.LEFT, padx=(0, 20))

        tk.Label(top_row, text="Signature :", bg=BG, fg=FG, font=MONO_B).pack(side=tk.LEFT, padx=(0, 8))
        self.sig_var = tk.StringVar(value="Founder / Default")
        sig_box = ttk.Combobox(top_row, textvariable=self.sig_var, values=list(DEFAULT_SIGNATURES.keys()), state="readonly", width=18, style="Matrix.TCombobox")
        sig_box.pack(side=tk.LEFT, padx=(0, 10))
        mk_btn(top_row, "[ INSERT AT CURSOR ]", self.insert_signature).pack(side=tk.LEFT)

        # Personalisation Score Banner
        self.lbl_score_banner = tk.Label(frm, text="🌟 TEMPLATE SCORE: HIGH PERSONALISATION — Excellent conversion optimization!", bg=SEL_CLR, fg=FG_CYAN, font=MONO_B, pady=6, bd=1, relief=tk.SOLID)
        self.lbl_score_banner.pack(fill=tk.X, pady=(0, 10))

        # Clickable Placeholder Chips Row
        chip_frm = tk.LabelFrame(frm, text=" ⚡ CLICKABLE PLACEHOLDER CHIPS (INSERTS AT CURSOR) ", bg=BG, fg=FG_BRIGHT, font=MONO_SM, padx=10, pady=6)
        chip_frm.pack(fill=tk.X, pady=(0, 10))

        chips = ["{First Name}", "{Surname}", "{Business Name}", "{City}", "{Rating}", "{Phone}", "{Website URL}"]
        for c in chips:
            btn = tk.Button(
                chip_frm, text=f"+ {c}", bg="#002200", fg=FG_BRIGHT, font=MONO_SM, relief=tk.SOLID, bd=1,
                cursor="hand2", padx=6, pady=2, command=lambda tag=c: self.insert_placeholder_chip(tag)
            )
            btn.pack(side=tk.LEFT, padx=4, pady=2)

        # Editor Area Split: Left Input, Right Preview
        split_frm = tk.Frame(frm, bg=BG)
        split_frm.pack(fill=tk.BOTH, expand=True)

        left_edit = tk.LabelFrame(split_frm, text=" ✍️ TEMPLATE COMPOSER ", bg=BG, fg=FG_BRIGHT, font=MONO_LG, padx=10, pady=10)
        left_edit.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # Format option & Subject
        subj_row = tk.Frame(left_edit, bg=BG)
        subj_row.pack(fill=tk.X, pady=(0, 8))
        tk.Label(subj_row, text="Subject:", bg=BG, fg=FG, font=MONO_B).pack(side=tk.LEFT, padx=(0, 8))
        self.entry_subject = tk.Entry(subj_row, bg=SEL_CLR, fg=FG_BRIGHT, font=MONO_B, insertbackground=FG, bd=1, relief=tk.SOLID)
        self.entry_subject.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry_subject.bind("<KeyRelease>", lambda e: self.update_score_and_preview())
        self.entry_subject.bind("<FocusIn>", lambda e: setattr(self, 'last_focus_widget', self.entry_subject))

        # Format Radiobuttons & Attachments
        fmt_row = tk.Frame(left_edit, bg=BG)
        fmt_row.pack(fill=tk.X, pady=(0, 8))
        self.format_var = tk.BooleanVar(value=False) # False=Plain, True=HTML
        tk.Radiobutton(fmt_row, text="Plain Text", variable=self.format_var, value=False, bg=BG, fg=FG, selectcolor=SEL_CLR, font=MONO_SM, command=self.update_score_and_preview).pack(side=tk.LEFT, padx=(0, 10))
        tk.Radiobutton(fmt_row, text="HTML / Hybrid", variable=self.format_var, value=True, bg=BG, fg=FG, selectcolor=SEL_CLR, font=MONO_SM, command=self.update_score_and_preview).pack(side=tk.LEFT, padx=(0, 15))
        
        mk_btn(fmt_row, "[ 📎 ATTACH FILE ]", self.add_attachment).pack(side=tk.RIGHT)
        self.lbl_att = tk.Label(fmt_row, text="No attachments", bg=BG, fg=FG_DIM, font=MONO_SM)
        self.lbl_att.pack(side=tk.RIGHT, padx=10)

        # Body Text area
        self.text_body = scrolledtext.ScrolledText(left_edit, wrap=tk.WORD, font=MONO, bg=SEL_CLR, fg=FG, insertbackground=FG, bd=1, relief=tk.SOLID)
        self.text_body.pack(fill=tk.BOTH, expand=True)
        self.text_body.bind("<KeyRelease>", lambda e: self.update_score_and_preview())
        self.text_body.bind("<FocusIn>", lambda e: setattr(self, 'last_focus_widget', self.text_body))

        # Right Side Preview
        right_prev = tk.LabelFrame(split_frm, text=" 👀 LIVE LEAD PREVIEW ", bg=BG, fg=FG_BRIGHT, font=MONO_LG, padx=10, pady=10)
        right_prev.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        nav_prev = tk.Frame(right_prev, bg=BG)
        nav_prev.pack(fill=tk.X, pady=(0, 8))
        mk_btn(nav_prev, "[ ◀ PREV ]", self.prev_preview_lead, width=8).pack(side=tk.LEFT, padx=(0, 5))
        mk_btn(nav_prev, "[ NEXT ▶ ]", self.next_preview_lead, width=8).pack(side=tk.LEFT)
        self.lbl_prev_count = tk.Label(nav_prev, text="Lead #0 / 0", bg=BG, fg=FG_CYAN, font=MONO_B)
        self.lbl_prev_count.pack(side=tk.RIGHT)

        self.text_preview = scrolledtext.ScrolledText(right_prev, wrap=tk.WORD, font=MONO, bg="#000800", fg=FG_BRIGHT, state=tk.DISABLED, bd=1, relief=tk.SOLID)
        self.text_preview.pack(fill=tk.BOTH, expand=True)

        # Load default preset
        self.load_preset_template()

    def load_preset_template(self):
        name = self.preset_var.get()
        tpl = DEFAULT_TEMPLATES.get(name, {})
        if tpl:
            self.entry_subject.delete(0, tk.END)
            self.entry_subject.insert(0, tpl.get("subject", ""))
            self.text_body.delete("1.0", tk.END)
            self.text_body.insert("1.0", tpl.get("body", ""))
            self.update_score_and_preview()

    def insert_signature(self):
        name = self.sig_var.get()
        sig = DEFAULT_SIGNATURES.get(name, "")
        if sig:
            self.text_body.insert(tk.INSERT, "\n\n" + sig)
            self.update_score_and_preview()

    def insert_placeholder_chip(self, tag: str):
        target = getattr(self, 'last_focus_widget', self.text_body)
        if target == self.entry_subject:
            idx = self.entry_subject.index(tk.INSERT)
            self.entry_subject.insert(idx, tag)
        else:
            self.text_body.insert(tk.INSERT, tag)
        self.update_score_and_preview()

    def add_attachment(self):
        file_path = filedialog.askopenfilename(title="Select Attachment (PDF, DOCX, etc.)")
        if file_path and os.path.isfile(file_path):
            self.attachments.append(file_path)
            names = [os.path.basename(p) for p in self.attachments]
            self.lbl_att.config(text=f"{len(names)} file(s): " + ", ".join(names), fg=FG_BRIGHT)

    def update_score_and_preview(self):
        subj = self.entry_subject.get()
        body = self.text_body.get("1.0", tk.END)
        
        score, suggestions = score_template(subj, body)
        self.lbl_stat_score.config(
            text=f"TEMPLATE SCORE: {score.upper()}",
            fg=FG_BRIGHT if score == "High" else (FG_WARN if score == "Medium" else FG_ERR)
        )

        if score == "High":
            self.lbl_score_banner.config(text="🌟 TEMPLATE SCORE: HIGH — Excellent conversion optimization!", fg=FG_CYAN)
        elif score == "Medium":
            self.lbl_score_banner.config(text=f"⚡ TEMPLATE SCORE: MEDIUM — Tip: {suggestions[0] if suggestions else ''}", fg=FG_WARN)
        else:
            self.lbl_score_banner.config(text=f"⚠ TEMPLATE SCORE: LOW — Tip: {suggestions[0] if suggestions else 'Add dynamic placeholders!'}", fg=FG_ERR)

        # Render Live Preview
        self.text_preview.config(state=tk.NORMAL)
        self.text_preview.delete("1.0", tk.END)

        if not self.valid_df.empty:
            total = len(self.valid_df)
            if self.current_preview_idx >= total:
                self.current_preview_idx = 0
            row = self.valid_df.iloc[self.current_preview_idx].to_dict()
            self.lbl_prev_count.config(text=f"Lead #{self.current_preview_idx+1} / {total}")
            
            rend_subj = render_template(subj, row)
            rend_body = render_template(body, row)

            preview_txt = f"TO       : {row.get(self.email_col_var.get(), 'test@example.com')}\n"
            preview_txt += f"SUBJECT  : {rend_subj}\n"
            preview_txt += "───────────────────────────────────────────────────────────\n\n"
            preview_txt += rend_body
            if self.attachments:
                preview_txt += f"\n\n[📎 Attached: {', '.join([os.path.basename(p) for p in self.attachments])}]"
            self.text_preview.insert("1.0", preview_txt)
        else:
            self.lbl_prev_count.config(text="Lead #0 / 0")
            self.text_preview.insert("1.0", "[No valid leads loaded in Tab 1 yet. Showing raw template:]\n\nSUBJECT: " + subj + "\n\n" + body)
        
        self.text_preview.config(state=tk.DISABLED)

    def prev_preview_lead(self):
        if not self.valid_df.empty:
            self.current_preview_idx = (self.current_preview_idx - 1) % len(self.valid_df)
            self.update_score_and_preview()

    def next_preview_lead(self):
        if not self.valid_df.empty:
            self.current_preview_idx = (self.current_preview_idx + 1) % len(self.valid_df)
            self.update_score_and_preview()

    # ── TAB 3: SMTP & ANTI-SPAM SETTINGS ──────────────────────────────────────
    def _build_tab3_smtp(self):
        frm = self.tab_frames[2]

        box_smtp = tk.LabelFrame(frm, text=" 🔌 SMTP CREDENTIALS & SERVER CONFIGURATION ", bg=BG, fg=FG_BRIGHT, font=MONO_LG, padx=20, pady=20)
        box_smtp.pack(fill=tk.X, pady=(10, 20))

        grid = tk.Frame(box_smtp, bg=BG)
        grid.pack(fill=tk.X)

        tk.Label(grid, text="SMTP Host :", bg=BG, fg=FG, font=MONO_B).grid(row=0, column=0, sticky=tk.W, pady=8)
        self.smtp_host_var = tk.StringVar(value="smtp.gmail.com")
        tk.Entry(grid, textvariable=self.smtp_host_var, bg=SEL_CLR, fg=FG_BRIGHT, font=MONO, width=30, insertbackground=FG, bd=1, relief=tk.SOLID).grid(row=0, column=1, padx=15, pady=8)

        tk.Label(grid, text="Port :", bg=BG, fg=FG, font=MONO_B).grid(row=0, column=2, sticky=tk.W, pady=8)
        self.smtp_port_var = tk.StringVar(value="587")
        tk.Entry(grid, textvariable=self.smtp_port_var, bg=SEL_CLR, fg=FG_BRIGHT, font=MONO, width=10, insertbackground=FG, bd=1, relief=tk.SOLID).grid(row=0, column=3, padx=15, pady=8)

        tk.Label(grid, text="Sender Email :", bg=BG, fg=FG, font=MONO_B).grid(row=1, column=0, sticky=tk.W, pady=8)
        self.smtp_user_var = tk.StringVar()
        tk.Entry(grid, textvariable=self.smtp_user_var, bg=SEL_CLR, fg=FG_BRIGHT, font=MONO, width=30, insertbackground=FG, bd=1, relief=tk.SOLID).grid(row=1, column=1, padx=15, pady=8)

        tk.Label(grid, text="App Password :", bg=BG, fg=FG, font=MONO_B).grid(row=1, column=2, sticky=tk.W, pady=8)
        self.smtp_pass_var = tk.StringVar()
        tk.Entry(grid, textvariable=self.smtp_pass_var, show="•", bg=SEL_CLR, fg=FG_BRIGHT, font=MONO, width=25, insertbackground=FG, bd=1, relief=tk.SOLID).grid(row=1, column=3, padx=15, pady=8)

        self.smtp_ssl_var = tk.BooleanVar(value=False)
        tk.Checkbutton(grid, text="Use Direct SSL/TLS (Port 465)", variable=self.smtp_ssl_var, bg=BG, fg=FG, selectcolor=SEL_CLR, font=MONO_B, cursor="hand2").grid(row=2, column=1, sticky=tk.W, pady=10)

        mk_btn(box_smtp, "[ 🔌 TEST SMTP CONNECTION ]", self.test_smtp).pack(anchor=tk.W, pady=(15, 5))

        # Helper note
        lbl_note = tk.Label(box_smtp, text="💡 NOTE FOR GMAIL / YAHOO: You MUST use a 16-character App Password generated from your Account Security settings.\nRegular login passwords will be blocked by Google/Yahoo.", bg=BG, fg=FG_WARN, font=MONO_SM, justify=tk.LEFT)
        lbl_note.pack(anchor=tk.W, pady=5)

        # Anti-Spam Rate Limiting Box
        box_spam = tk.LabelFrame(frm, text=" 🛡️ ANTI-SPAM RATE LIMITING & THROTTLING PROTECTION ", bg=BG, fg=FG_BRIGHT, font=MONO_LG, padx=20, pady=20)
        box_spam.pack(fill=tk.X)

        s_grid = tk.Frame(box_spam, bg=BG)
        s_grid.pack(fill=tk.X)

        tk.Label(s_grid, text="Max Emails per Hour :", bg=BG, fg=FG, font=MONO_B).grid(row=0, column=0, sticky=tk.W, pady=10)
        self.spam_max_var = tk.StringVar(value="100")
        ttk.Combobox(s_grid, textvariable=self.spam_max_var, values=["50", "100", "200", "500", "Unlimited"], state="readonly", width=15, style="Matrix.TCombobox").grid(row=0, column=1, padx=15, sticky=tk.W)

        tk.Label(s_grid, text="Random Delay Range (Seconds) :", bg=BG, fg=FG, font=MONO_B).grid(row=1, column=0, sticky=tk.W, pady=10)
        
        delay_frm = tk.Frame(s_grid, bg=BG)
        delay_frm.grid(row=1, column=1, padx=15, sticky=tk.W)
        
        tk.Label(delay_frm, text="Min:", bg=BG, fg=FG_DIM, font=MONO).pack(side=tk.LEFT, padx=(0, 5))
        self.delay_min_var = tk.StringVar(value="3.0")
        tk.Spinbox(delay_frm, from_=1.0, to=60.0, increment=0.5, textvariable=self.delay_min_var, width=6, bg=SEL_CLR, fg=FG_BRIGHT, font=MONO, bd=1, relief=tk.SOLID).pack(side=tk.LEFT, padx=(0, 15))

        tk.Label(delay_frm, text="Max:", bg=BG, fg=FG_DIM, font=MONO).pack(side=tk.LEFT, padx=(0, 5))
        self.delay_max_var = tk.StringVar(value="8.0")
        tk.Spinbox(delay_frm, from_=2.0, to=120.0, increment=0.5, textvariable=self.delay_max_var, width=6, bg=SEL_CLR, fg=FG_BRIGHT, font=MONO, bd=1, relief=tk.SOLID).pack(side=tk.LEFT)

    def test_smtp(self):
        host = self.smtp_host_var.get().strip()
        port = self.smtp_port_var.get().strip()
        user = self.smtp_user_var.get().strip()
        pwd = self.smtp_pass_var.get().strip()
        ssl = self.smtp_ssl_var.get()

        if not host or not user or not pwd:
            messagebox.showwarning("Missing Credentials", "Please enter SMTP Host, Sender Email, and App Password.")
            return

        self.log(f"🔌 Testing SMTP login for {user} on {host}:{port}...", "dim")
        
        def _test_thread():
            success, msg = SMTEngine.test_connection(host, port, user, pwd, ssl)
            self.root.after(0, lambda: self._on_test_result(success, msg))
        
        threading.Thread(target=_test_thread, daemon=True).start()

    def _on_test_result(self, success, msg):
        if success:
            self.lbl_stat_smtp.config(text="SMTP: CONNECTED ✅", fg=FG_CYAN)
            self.log(msg, "success")
            messagebox.showinfo("SMTP Verification Success", msg)
        else:
            self.lbl_stat_smtp.config(text="SMTP: FAILED ❌", fg=FG_ERR)
            self.log(msg, "error")
            messagebox.showerror("SMTP Verification Failed", msg)

    # ── TAB 4: LIVE CAMPAIGN & ANALYTICS ──────────────────────────────────────
    def _build_tab4_campaign(self):
        frm = self.tab_frames[3]

        box_ctrl = tk.LabelFrame(frm, text=" 🚀 MISSION CONTROL & EXECUTION MODES ", bg=BG, fg=FG_BRIGHT, font=MONO_LG, padx=15, pady=12)
        box_ctrl.pack(fill=tk.X, pady=(5, 10))

        # Mode row
        mode_row = tk.Frame(box_ctrl, bg=BG)
        mode_row.pack(fill=tk.X, pady=5)
        tk.Label(mode_row, text="Execution Mode:", bg=BG, fg=FG, font=MONO_B).pack(side=tk.LEFT, padx=(0, 15))
        
        self.mode_var = tk.StringVar(value="production")
        tk.Radiobutton(mode_row, text="Test Mode (First 3 Leads Only)", variable=self.mode_var, value="test", bg=BG, fg=FG_CYAN, selectcolor=SEL_CLR, font=MONO_B).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(mode_row, text="Production Mode (Send to Entire List)", variable=self.mode_var, value="production", bg=BG, fg=FG_BRIGHT, selectcolor=SEL_CLR, font=MONO_B).pack(side=tk.LEFT, padx=10)
        
        res_frm = tk.Frame(mode_row, bg=BG)
        res_frm.pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(res_frm, text="Resume Mode from Lead #", variable=self.mode_var, value="resume", bg=BG, fg=FG_WARN, selectcolor=SEL_CLR, font=MONO_B).pack(side=tk.LEFT)
        self.resume_idx_var = tk.StringVar(value="1")
        tk.Spinbox(res_frm, from_=1, to=10000, textvariable=self.resume_idx_var, width=6, bg=SEL_CLR, fg=FG_BRIGHT, font=MONO, bd=1, relief=tk.SOLID).pack(side=tk.LEFT, padx=5)

        # Action buttons row
        act_row = tk.Frame(box_ctrl, bg=BG)
        act_row.pack(fill=tk.X, pady=(10, 5))

        self.btn_start = mk_btn(act_row, "[ ▶  INITIATE CAMPAIGN ]", self.start_campaign)
        self.btn_start.pack(side=tk.LEFT, padx=(0, 10))

        self.btn_pause = mk_btn(act_row, "[ ⏸  PAUSE ]", self.toggle_pause, state=tk.DISABLED)
        self.btn_pause.pack(side=tk.LEFT, padx=5)

        self.btn_stop = mk_btn(act_row, "[ ⏹  ABORT MISSION ]", self.stop_campaign, state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT, padx=5)

        # Live Progress & Telemetry Box
        box_prog = tk.LabelFrame(frm, text=" 📈 LIVE TELEMETRY & PROGRESS TRACKER ", bg=BG, fg=FG_BRIGHT, font=MONO_LG, padx=15, pady=10)
        box_prog.pack(fill=tk.X, pady=(0, 10))

        self.lbl_prog_bar = tk.Label(box_prog, text="[--------------------------------------------------] 0.0%", bg=BG, fg=FG_BRIGHT, font=MONO_B)
        self.lbl_prog_bar.pack(anchor=tk.W, pady=(5, 8))

        t_grid = tk.Frame(box_prog, bg=BG)
        t_grid.pack(fill=tk.X)
        self.lbl_tel_sent = tk.Label(t_grid, text="Sent: 0 / 0", bg=BG, fg=FG_CYAN, font=MONO_B, width=22, anchor=tk.W)
        self.lbl_tel_sent.grid(row=0, column=0, pady=2)
        
        self.lbl_tel_fail = tk.Label(t_grid, text="Failed / Bounced: 0", bg=BG, fg=FG_ERR, font=MONO_B, width=22, anchor=tk.W)
        self.lbl_tel_fail.grid(row=0, column=1, pady=2)

        self.lbl_tel_time = tk.Label(t_grid, text="Elapsed: 0s | Avg: 0s", bg=BG, fg=FG, font=MONO_B, width=30, anchor=tk.W)
        self.lbl_tel_time.grid(row=1, column=0, pady=2)

        self.lbl_tel_eta = tk.Label(t_grid, text="ETA Remaining: ---", bg=BG, fg=FG_WARN, font=MONO_B, width=30, anchor=tk.W)
        self.lbl_tel_eta.grid(row=1, column=1, pady=2)

        # Console Feed
        box_cons = tk.LabelFrame(frm, text=" 🖥️ LIVE NEURAL CAMPAIGN CONSOLE ", bg=BG, fg=FG_BRIGHT, font=MONO_LG, padx=10, pady=10)
        box_cons.pack(fill=tk.BOTH, expand=True)

        self.console = scrolledtext.ScrolledText(box_cons, wrap=tk.WORD, font=MONO, bg="#000800", fg=FG, insertbackground=FG, state=tk.DISABLED, bd=1, relief=tk.SOLID)
        self.console.pack(fill=tk.BOTH, expand=True)
        
        self.console.tag_config("bright",  foreground=FG_BRIGHT, font=MONO_B)
        self.console.tag_config("dim",     foreground=FG_DIM)
        self.console.tag_config("warning", foreground=FG_WARN, font=MONO_B)
        self.console.tag_config("error",   foreground=FG_ERR,  font=MONO_B)
        self.console.tag_config("save",    foreground=FG_CYAN, font=MONO_B)
        self.console.tag_config("success", foreground=FG,      font=MONO_B)

    def log(self, text: str, tag: str = "success"):
        self.console.config(state=tk.NORMAL)
        ts = time.strftime("%H:%M:%S")
        self.console.insert(tk.END, f"[{ts}] {text}\n", tag)
        self.console.see(tk.END)
        self.console.config(state=tk.DISABLED)

    def start_campaign(self):
        if self.valid_df.empty:
            messagebox.showwarning("No Leads Ready", "Please load a valid spreadsheet in Tab 1 first.")
            self.switch_tab(0)
            return

        host = self.smtp_host_var.get().strip()
        user = self.smtp_user_var.get().strip()
        pwd = self.smtp_pass_var.get().strip()
        if not host or not user or not pwd:
            messagebox.showwarning("Missing SMTP Settings", "Please configure your SMTP Server and credentials in Tab 3.")
            self.switch_tab(2)
            return

        mode = self.mode_var.get()
        res_idx = 0
        if mode == "resume":
            try:
                res_idx = max(0, int(self.resume_idx_var.get()) - 1)
            except ValueError:
                res_idx = 0

        self.is_running = True
        self.stop_event.clear()
        self.pause_event.clear()
        
        self.btn_start.config(state=tk.DISABLED)
        self.btn_pause.config(state=tk.NORMAL, text="[ ⏸  PAUSE ]")
        self.btn_stop.config(state=tk.NORMAL)
        self.status_pill.config(text="[ CAMPAIGN ACTIVE ]", bg="#003800", fg=FG_BRIGHT)

        smtp_config = {
            "host": host, "port": self.smtp_port_var.get().strip(),
            "user": user, "password": pwd, "ssl_mode": self.smtp_ssl_var.get(),
            "max_per_hour": 999999 if self.spam_max_var.get() == "Unlimited" else int(self.spam_max_var.get()),
            "delay_min": float(self.delay_min_var.get()),
            "delay_max": float(self.delay_max_var.get())
        }

        def _progress_cb(current, total, sent, failed, elapsed, eta):
            self.root.after(0, lambda: self._update_telemetry_ui(current, total, sent, failed, elapsed, eta))

        def _log_cb(msg, tag="success"):
            self.root.after(0, lambda: self.log(msg, tag))

        def _run_thread():
            report_file = SMTEngine.execute_campaign(
                leads_df=self.valid_df,
                email_col=self.email_col_var.get(),
                subject_tpl=self.entry_subject.get(),
                body_tpl=self.text_body.get("1.0", tk.END),
                signature="", # signature is already inserted in text_body if user clicked insert
                smtp_config=smtp_config,
                mode=mode,
                resume_from_idx=res_idx,
                is_html=self.format_var.get(),
                attachments=self.attachments,
                progress_callback=_progress_cb,
                log_callback=_log_cb,
                stop_event=self.stop_event,
                pause_event=self.pause_event
            )
            self.root.after(0, lambda: self._on_campaign_end(report_file))

        self.campaign_thread = threading.Thread(target=_run_thread, daemon=True)
        self.campaign_thread.start()

    def _update_telemetry_ui(self, current, total, sent, failed, elapsed, eta):
        pct = (current / total) * 100 if total > 0 else 0
        bar_len = 50
        filled = int((pct / 100) * bar_len)
        bar_str = "[" + "█" * filled + "-" * (bar_len - filled) + f"] {pct:.1f}%"
        self.lbl_prog_bar.config(text=bar_str)

        self.lbl_tel_sent.config(text=f"Sent: {sent} / {total}")
        self.lbl_tel_fail.config(text=f"Failed / Bounced: {failed}")
        
        m_el, s_el = divmod(int(elapsed), 60)
        avg = elapsed / current if current > 0 else 0
        self.lbl_tel_time.config(text=f"Elapsed: {m_el}m {s_el}s | Avg: {avg:.1f}s/email")

        m_eta, s_eta = divmod(eta, 60)
        self.lbl_tel_eta.config(text=f"ETA Remaining: {m_eta}m {s_eta}s")

    def toggle_pause(self):
        if not self.is_running:
            return
        if self.pause_event.is_set():
            self.pause_event.clear()
            self.btn_pause.config(text="[ ⏸  PAUSE ]", bg=SEL_CLR)
            self.status_pill.config(text="[ CAMPAIGN ACTIVE ]", bg="#003800")
            self.log("▶ Mission resumed.", "bright")
        else:
            self.pause_event.set()
            self.btn_pause.config(text="[ ▶  RESUME ]", bg="#333300", fg="#FFFF00")
            self.status_pill.config(text="[ PAUSED ]", bg="#333300", fg="#FFFF00")
            self.log("⏸ Mission paused by user. Waiting to resume...", "warning")

    def stop_campaign(self):
        if self.is_running and messagebox.askyesno("Confirm Abort", "Abort active email campaign?"):
            self.stop_event.set()
            self.pause_event.clear()
            self.log("⏹ ABORT SIGNAL SENT. Terminating active sending loop...", "error")

    def _on_campaign_end(self, report_file):
        self.is_running = False
        self.btn_start.config(state=tk.NORMAL)
        self.btn_pause.config(state=tk.DISABLED, text="[ ⏸  PAUSE ]", bg=SEL_CLR)
        self.btn_stop.config(state=tk.DISABLED)
        self.status_pill.config(text="[ SYSTEM IDLE ]", bg=SEL_CLR, fg=FG_BRIGHT)
        
        if report_file and os.path.exists(report_file):
            self.log(f"🎉 MISSION COMPLETE! Campaign Telemetry saved to:\n{report_file}", "save")
            messagebox.showinfo("Campaign Complete", f"Email Campaign Completed!\n\nDelivery Telemetry Report Saved:\n{report_file}")
        else:
            self.log("🏁 Campaign stopped or finished without generating report.", "dim")

def main():
    app = EmailSenderApp()
    if app.own_root:
        app.root.mainloop()

if __name__ == "__main__":
    main()
