#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║          KALI SMARTOPS MANAGER PRO — MIDNIGHT EDITION        ║
║          Full Python / Tkinter UI — All Features Included    ║
╚══════════════════════════════════════════════════════════════╝
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import threading
import os, stat, sys, math, time, json
from datetime import datetime
from pathlib import Path
import platform

# ═══════════════════════════════════════════════════════════════
#  PALETTE
# ═══════════════════════════════════════════════════════════════
BG         = "#000000"
BG1        = "#080808"
BG2        = "#0d0d0d"
BG3        = "#111111"
BG_CARD    = "#141414"
BG_HOVER   = "#1a1a1a"
BG_ACTIVE  = "#1e2840"
BORDER     = "#1a1a1a"
BORDER2    = "#222222"
DIM        = "#2a2a2a"
MUTED      = "#3a3a3a"
TEXT       = "#e8e8e8"
TEXT_DIM   = "#666666"
TEXT_SUB   = "#444444"
NEON       = "#00d4ff"
NEON_DIM   = "#001e26"
EMERALD    = "#00ff88"
EM_DIM     = "#001a0d"
WARN       = "#ffaa00"
DANGER     = "#ff3c3c"
PURPLE     = "#8855ff"

# Fonts
FT_TITLE  = ("Courier New", 13, "bold")
FT_HEADER = ("Courier New", 11, "bold")
FT_LABEL  = ("Courier New", 10)
FT_BOLD   = ("Courier New", 10, "bold")
FT_MONO   = ("Courier New", 10)
FT_MONO_S = ("Courier New", 9)
FT_SMALL  = ("Courier New", 9)
FT_TINY   = ("Courier New", 8)
FT_BIG    = ("Courier New", 18, "bold")
FT_HUGE   = ("Courier New", 24, "bold")

# ═══════════════════════════════════════════════════════════════
#  SHELL HELPERS
# ═══════════════════════════════════════════════════════════════
def shell(cmd, timeout=15):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip()
    except Exception:
        return ""

def shell_lines(cmd, timeout=15):
    out = shell(cmd, timeout)
    return [l for l in out.splitlines() if l.strip()]

def human_size(n):
    for unit in ["B","KB","MB","GB","TB"]:
        if n < 1024:
            return f"{n:.1f} {unit}" if unit != "B" else f"{n} B"
        n /= 1024
    return f"{n:.1f} PB"

def get_cpu_percent():
    try:
        line = shell("grep 'cpu ' /proc/stat")
        vals = list(map(int, line.split()[1:]))
        idle = vals[3]
        total = sum(vals)
        return total, idle
    except:
        return 0, 0

# ═══════════════════════════════════════════════════════════════
#  TOOLTIP
# ═══════════════════════════════════════════════════════════════
class Tooltip:
    def __init__(self, widget, text):
        self.widget, self.text, self.tip = widget, text, None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)
    def show(self, _):
        x = self.widget.winfo_rootx() + 24
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.geometry(f"+{x}+{y}")
        tk.Label(self.tip, text=self.text, bg=BG_CARD, fg=NEON,
                 font=FT_SMALL, padx=8, pady=4,
                 highlightbackground=BORDER2, highlightthickness=1).pack()
    def hide(self, _):
        if self.tip:
            self.tip.destroy(); self.tip = None

# ═══════════════════════════════════════════════════════════════
#  ARC METER (Canvas-based circular gauge)
# ═══════════════════════════════════════════════════════════════
class ArcMeter(tk.Canvas):
    def __init__(self, parent, label="", size=110, color=NEON, **kw):
        super().__init__(parent, width=size, height=size,
                         bg=BG1, bd=0, highlightthickness=0, **kw)
        self.size  = size
        self.color = color
        self.label = label
        self._val  = 0
        self._draw(0)

    def set(self, pct):
        self._val = max(0, min(100, pct))
        self._draw(self._val)

    def _draw(self, pct):
        self.delete("all")
        s = self.size
        pad = 10
        x0, y0, x1, y1 = pad, pad, s-pad, s-pad

        # Track
        self.create_arc(x0, y0, x1, y1, start=220, extent=-260,
                        outline=DIM, style="arc", width=8)

        # Fill
        extent = -int(260 * pct / 100)
        col = DANGER if pct > 85 else WARN if pct > 65 else self.color
        if extent != 0:
            self.create_arc(x0, y0, x1, y1, start=220, extent=extent,
                            outline=col, style="arc", width=8)

        # Neon dot at tip
        angle_deg = 220 - (260 * pct / 100)
        angle_rad = math.radians(angle_deg)
        cx, cy = s/2, s/2
        r = (s/2) - pad
        dx = cx + r * math.cos(angle_rad)
        dy = cy - r * math.sin(angle_rad)
        self.create_oval(dx-5, dy-5, dx+5, dy+5, fill=col, outline="")

        # Center text
        self.create_text(s/2, s/2 - 6, text=f"{int(pct)}%",
                         fill=col, font=FT_BOLD)
        self.create_text(s/2, s/2 + 10, text=self.label,
                         fill=TEXT_DIM, font=FT_TINY)

# ═══════════════════════════════════════════════════════════════
#  SCROLLABLE FRAME
# ═══════════════════════════════════════════════════════════════
class ScrollFrame(tk.Frame):
    def __init__(self, parent, **kw):
        super().__init__(parent, bg=kw.get("bg", BG), **kw)
        canvas = tk.Canvas(self, bg=kw.get("bg", BG), bd=0, highlightthickness=0)
        vsb = tk.Scrollbar(self, orient="vertical", command=canvas.yview,
                           bg=BG1, troughcolor=BG, bd=0, width=6)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        self.inner = tk.Frame(canvas, bg=kw.get("bg", BG))
        win = canvas.create_window((0, 0), window=self.inner, anchor="nw")
        def on_cfg(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
        def on_canvas_cfg(e):
            canvas.itemconfigure(win, width=e.width)
        self.inner.bind("<Configure>", on_cfg)
        canvas.bind("<Configure>", on_canvas_cfg)
        for w in [canvas, self.inner]:
            w.bind("<MouseWheel>",
                   lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
            w.bind("<Button-4>", lambda e: canvas.yview_scroll(-3, "units"))
            w.bind("<Button-5>", lambda e: canvas.yview_scroll(3, "units"))
        self._canvas = canvas

# ═══════════════════════════════════════════════════════════════
#  STYLED TABLE (Treeview wrapper)
# ═══════════════════════════════════════════════════════════════
class DataTable(tk.Frame):
    def __init__(self, parent, columns, **kw):
        super().__init__(parent, bg=BG1, **kw)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Neon.Treeview",
            background=BG1, foreground=TEXT, fieldbackground=BG1,
            rowheight=26, font=FT_MONO_S, borderwidth=0)
        style.configure("Neon.Treeview.Heading",
            background=BG3, foreground=NEON, font=FT_BOLD,
            relief="flat", borderwidth=0)
        style.map("Neon.Treeview",
            background=[("selected", BG_ACTIVE)],
            foreground=[("selected", NEON)])

        self._tree = ttk.Treeview(self, columns=columns, show="headings",
                                   style="Neon.Treeview")
        for col in columns:
            self._tree.heading(col, text=col.upper())
            self._tree.column(col, anchor="w", width=120)

        vsb = ttk.Scrollbar(self, orient="vertical", command=self._tree.yview)
        hsb = ttk.Scrollbar(self, orient="horizontal", command=self._tree.xview)
        self._tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self._tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        # Alternating rows
        self._tree.tag_configure("odd",  background=BG2)
        self._tree.tag_configure("even", background=BG1)
        self._tree.tag_configure("warn", foreground=WARN)
        self._tree.tag_configure("danger", foreground=DANGER)
        self._tree.tag_configure("good", foreground=EMERALD)

    def clear(self):
        for item in self._tree.get_children():
            self._tree.delete(item)

    def insert(self, values, tag=""):
        idx = len(self._tree.get_children())
        row_tag = "odd" if idx % 2 else "even"
        tags = (row_tag, tag) if tag else (row_tag,)
        self._tree.insert("", "end", values=values, tags=tags)

    def col_width(self, col, width):
        self._tree.column(col, width=width)

# ═══════════════════════════════════════════════════════════════
#  NAV BUTTON
# ═══════════════════════════════════════════════════════════════
class NavBtn(tk.Frame):
    def __init__(self, parent, icon, label, on_click, badge="", **kw):
        super().__init__(parent, bg=BG1, cursor="hand2")
        self._active = False
        self._on_click = on_click

        self._indicator = tk.Frame(self, bg=BG1, width=3)
        self._indicator.pack(side="left", fill="y")

        inner = tk.Frame(self, bg=BG1)
        inner.pack(side="left", fill="x", expand=True, padx=(8,8), pady=5)

        self._ico = tk.Label(inner, text=icon, bg=BG1, fg=TEXT_DIM,
                              font=("Courier New", 13), width=2)
        self._ico.pack(side="left", padx=(0,6))

        self._lbl = tk.Label(inner, text=label, bg=BG1, fg=TEXT_DIM,
                              font=FT_LABEL, anchor="w")
        self._lbl.pack(side="left", fill="x", expand=True)

        if badge:
            bk = EMERALD if badge == "NEW" else DIM
            bc = "#000" if badge == "NEW" else TEXT_DIM
            tk.Label(inner, text=badge, bg=bk, fg=bc,
                     font=FT_TINY, padx=4, pady=1).pack(side="right")

        for w in [self, self._indicator, inner, self._ico, self._lbl]:
            w.bind("<Button-1>", self._click)
            w.bind("<Enter>", self._enter)
            w.bind("<Leave>", self._leave)

        if badge:
            Tooltip(self, label)

    def _click(self, _=None):
        self._on_click()

    def _enter(self, _):
        if not self._active:
            self._set(BG_HOVER, TEXT)

    def _leave(self, _):
        if not self._active:
            self._set(BG1, TEXT_DIM)

    def activate(self):
        self._active = True
        self._set(BG_ACTIVE, NEON)
        self._indicator.configure(bg=NEON)

    def deactivate(self):
        self._active = False
        self._set(BG1, TEXT_DIM)
        self._indicator.configure(bg=BG1)

    def _set(self, bg, fg):
        for w in [self, self._indicator]:
            w.configure(bg=bg)
        for w in self.winfo_children():
            w.configure(bg=bg)
            for ch in w.winfo_children():
                try: ch.configure(bg=bg, fg=fg)
                except: pass

# ═══════════════════════════════════════════════════════════════
#  TERMINAL OUTPUT WIDGET
# ═══════════════════════════════════════════════════════════════
class TermOutput(tk.Frame):
    def __init__(self, parent, **kw):
        super().__init__(parent, bg=BG, **kw)
        self._text = tk.Text(self, bg="#020406", fg=TEXT,
                              font=FT_MONO, bd=0, padx=14, pady=10,
                              insertbackground=NEON, selectbackground=NEON_DIM,
                              selectforeground=NEON, relief="flat", wrap="none",
                              state="disabled")
        vsb = tk.Scrollbar(self, command=self._text.yview,
                            bg=BG1, troughcolor=BG, bd=0, width=6)
        hsb = tk.Scrollbar(self, command=self._text.xview,
                            orient="horizontal", bg=BG1, troughcolor=BG, bd=0, width=6)
        self._text.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self._text.pack(fill="both", expand=True)

        # Tags
        self._text.tag_configure("neon",    foreground=NEON)
        self._text.tag_configure("emerald", foreground=EMERALD)
        self._text.tag_configure("warn",    foreground=WARN)
        self._text.tag_configure("danger",  foreground=DANGER)
        self._text.tag_configure("dim",     foreground=TEXT_DIM)
        self._text.tag_configure("purple",  foreground=PURPLE)
        self._text.tag_configure("text",    foreground=TEXT)
        self._text.tag_configure("section",
            foreground=NEON, font=("Courier New", 10, "bold"))

    def clear(self):
        self._text.configure(state="normal")
        self._text.delete("1.0", "end")
        self._text.configure(state="disabled")

    def append(self, text, tag="text"):
        self._text.configure(state="normal")
        self._text.insert("end", text + "\n", tag)
        self._text.configure(state="disabled")
        self._text.see("end")

    def append_raw(self, text):
        """Auto-colorize based on content."""
        low = text.lower()
        if any(k in low for k in ["✅","success","done","ok","good","normal"]):
            tag = "emerald"
        elif any(k in low for k in ["⚠","warning","warn","caution"]):
            tag = "warn"
        elif any(k in low for k in ["❌","error","fail","critical","danger","lost"]):
            tag = "danger"
        elif any(k in low for k in ["▶","►","●","═","╔","╚","║","──"]):
            tag = "neon"
        elif text.startswith("$"):
            tag = "dim"
        else:
            tag = "text"
        self.append(text, tag)

# ═══════════════════════════════════════════════════════════════
#  STATUS BAR
# ═══════════════════════════════════════════════════════════════
class StatusBar(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG1, height=26)
        self.pack_propagate(False)
        self._msg = tk.Label(self, text="● CONNECTED", bg=BG1,
                              fg=EMERALD, font=FT_SMALL, anchor="w")
        self._msg.pack(side="left", padx=12)
        self._right = tk.Label(self, text="", bg=BG1,
                                fg=TEXT_DIM, font=FT_SMALL, anchor="e")
        self._right.pack(side="right", padx=12)

    def set(self, msg, right="", color=EMERALD):
        self._msg.configure(text=msg, fg=color)
        self._right.configure(text=right)

# ═══════════════════════════════════════════════════════════════
#  STAT CARD (mini dashboard card)
# ═══════════════════════════════════════════════════════════════
class StatCard(tk.Frame):
    def __init__(self, parent, title, **kw):
        super().__init__(parent, bg=BG1, padx=14, pady=10,
                         highlightbackground=BORDER2, highlightthickness=1, **kw)
        tk.Label(self, text=title.upper(), bg=BG1, fg=TEXT_SUB,
                 font=FT_TINY).pack(anchor="w")
        self._val = tk.Label(self, text="—", bg=BG1, fg=TEXT,
                              font=FT_BIG)
        self._val.pack(anchor="w")

        # bar
        bar_bg = tk.Frame(self, bg=BORDER2, height=3)
        bar_bg.pack(fill="x", pady=(4,0))
        self._bar = tk.Frame(bar_bg, bg=NEON, height=3, width=0)
        self._bar.place(x=0, y=0, relheight=1)

    def update(self, text, pct, color=None):
        col = color or (DANGER if pct > 85 else WARN if pct > 65 else NEON)
        self._val.configure(text=text, fg=col)
        self._bar.configure(bg=col)
        # Animate width via after
        self.after(10, lambda: self._bar.place(relwidth=pct/100))

# ═══════════════════════════════════════════════════════════════
#  MINI BAR (horizontal labeled bar)
# ═══════════════════════════════════════════════════════════════
class MiniBar(tk.Frame):
    def __init__(self, parent, label, **kw):
        super().__init__(parent, bg=BG1, **kw)
        tk.Label(self, text=label, bg=BG1, fg=TEXT_DIM,
                 font=FT_TINY, width=12, anchor="w").pack(side="left")
        bg = tk.Frame(self, bg=DIM, height=6)
        bg.pack(side="left", fill="x", expand=True, padx=(4,8))
        self._fill = tk.Frame(bg, bg=NEON, height=6)
        self._fill.place(x=0, y=0, relheight=1, relwidth=0)
        self._pct = tk.Label(self, text="0%", bg=BG1, fg=TEXT_DIM,
                              font=FT_TINY, width=5, anchor="e")
        self._pct.pack(side="right")

    def set(self, pct, color=None):
        col = color or (DANGER if pct > 85 else WARN if pct > 65 else EMERALD)
        self._fill.configure(bg=col)
        self._fill.place(relwidth=pct/100)
        self._pct.configure(text=f"{int(pct)}%", fg=col)

# ═══════════════════════════════════════════════════════════════
#  MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════
class SmartOpsPro:
    def __init__(self, root):
        self.root = root
        root.title("Kali SmartOps Manager PRO — Midnight Edition")
        root.configure(bg=BG)
        root.minsize(1100, 700)
        self._center(1400, 860)

        self._active_nav = None
        self._nav_btns   = {}
        self._cpu_prev   = (0, 0)
        self._history    = []
        self._hist_idx   = -1

        self._build()
        self._start_metrics()

    def _center(self, w, h):
        self.root.update_idletasks()
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    # ── BUILD LAYOUT ──────────────────────────────────────────────

    def _build(self):
        # ── TITLEBAR ──────────────────────────────────────────────
        tb = tk.Frame(self.root, bg=BG1, height=40)
        tb.pack(fill="x"); tb.pack_propagate(False)

        dot = tk.Frame(tb, bg=EMERALD, width=8, height=8)
        dot.place(x=14, rely=0.5, anchor="w")

        tk.Label(tb, text="SMARTOPS PRO", bg=BG1, fg=NEON,
                 font=("Courier New", 11, "bold")).place(x=30, rely=0.5, anchor="w")

        tk.Label(tb, text="── KALI LINUX ADMINISTRATION SUITE ──",
                 bg=BG1, fg=TEXT_SUB,
                 font=("Courier New", 9)).place(relx=0.5, rely=0.5, anchor="center")

        self._clock_lbl = tk.Label(tb, text="00:00:00", bg=BG1, fg=TEXT_DIM,
                                    font=("Courier New", 10))
        self._clock_lbl.pack(side="right", padx=16)
        self._update_clock()

        # ── BODY ──────────────────────────────────────────────────
        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True)

        # SIDEBAR
        self._sidebar = tk.Frame(body, bg=BG1, width=220)
        self._sidebar.pack(side="left", fill="y")
        self._sidebar.pack_propagate(False)
        self._build_sidebar()

        # MAIN
        right = tk.Frame(body, bg=BG)
        right.pack(side="left", fill="both", expand=True)

        # Breadcrumb
        self._bc = tk.Frame(right, bg=BG1, height=32)
        self._bc.pack(fill="x"); self._bc.pack_propagate(False)
        tk.Label(self._bc, text="smartops", bg=BG1, fg=NEON,
                 font=FT_SMALL).place(x=16, rely=0.5, anchor="w")
        self._sep_lbl = tk.Label(self._bc, text=" › ", bg=BG1, fg=DIM, font=FT_SMALL)
        self._sep_lbl.place(x=76, rely=0.5, anchor="w")
        self._bc_lbl = tk.Label(self._bc, text="overview", bg=BG1, fg=TEXT,
                                 font=FT_SMALL)
        self._bc_lbl.place(x=100, rely=0.5, anchor="w")

        # Stats row
        self._stats_row = tk.Frame(right, bg=BG, height=80)
        self._stats_row.pack(fill="x"); self._stats_row.pack_propagate(False)
        self._build_stats_row()

        # Content area
        self._content = tk.Frame(right, bg=BG)
        self._content.pack(fill="both", expand=True)

        # Input bar
        inp = tk.Frame(right, bg=BG1, height=38)
        inp.pack(fill="x"); inp.pack_propagate(False)
        tk.Label(inp, text="❯", bg=BG1, fg=NEON,
                 font=("Courier New", 12, "bold")).pack(side="left", padx=(14,6))
        self._cmd = tk.Entry(inp, bg=BG1, fg=TEXT, font=FT_MONO,
                              insertbackground=NEON, relief="flat", bd=0)
        self._cmd.pack(side="left", fill="x", expand=True)
        self._cmd.bind("<Return>", self._handle_cmd)
        self._cmd.bind("<Up>", self._hist_up)
        self._cmd.bind("<Down>", self._hist_dn)
        tk.Label(inp, text="↵ run  ↑↓ history  Ctrl+L clear",
                 bg=BG1, fg=TEXT_SUB, font=FT_TINY).pack(side="right", padx=12)

        # Status bar
        self._status = StatusBar(self.root)
        self._status.pack(fill="x", side="bottom")

        # Footer
        ft = tk.Frame(self.root, bg=BG1, height=28)
        ft.pack(fill="x", side="bottom"); ft.pack_propagate(False)
        self._build_footer(ft)

        # Keyboard shortcuts
        self.root.bind("<Control-l>", lambda e: self._clear_content())
        self.root.bind("<Control-k>", lambda e: self._cmd.focus_set())
        self.root.bind("<Escape>", lambda e: None)

        # Show overview
        self._show_overview()

    # ── SIDEBAR ───────────────────────────────────────────────────

    def _build_sidebar(self):
        # Logo area
        logo = tk.Frame(self._sidebar, bg=BG1)
        logo.pack(fill="x", padx=14, pady=(14,6))
        tk.Label(logo, text="⚡", bg=BG1, fg=NEON,
                 font=("Courier New", 20)).pack(side="left")
        tk.Label(logo, text=" SmartOps", bg=BG1, fg=TEXT,
                 font=("Courier New", 11, "bold")).pack(side="left")

        self._sep()

        scroll = ScrollFrame(self._sidebar, bg=BG1)
        scroll.pack(fill="both", expand=True)
        f = scroll.inner

        sections = [
            ("SYSTEM", [
                ("◈", "Overview",        "overview",   ""),
                ("⬡", "System Info",     "sysinfo",    ""),
                ("⣿", "Process Monitor", "process",    ""),
                ("▶", "Realtime Monitor","realtime",   ""),
                ("⬛", "Hardware Info",   "hardware",   ""),
            ]),
            ("NETWORK", [
                ("◎", "Interfaces",      "network",    ""),
                ("⇅", "Bandwidth",       "bandwidth",  ""),
                ("⊕", "Port Scanner",    "ports",      ""),
            ]),
            ("SERVICES & DISK", [
                ("⚙", "Services",        "services",   ""),
                ("◉", "Disk Analysis",   "disk",       ""),
                ("✦", "Cleanup Tools",   "cleanup",    ""),
            ]),
            ("SECURITY", [
                ("⬡", "Security Check",  "security",   ""),
                ("↑", "Package Updates", "updates",    ""),
            ]),
            ("FILES", [
                ("▤", "File Manager",    "files",      ""),
                ("⌕", "File Search",     "search",     ""),
                ("⊞", "File Organizer",  "organizer",  "NEW"),
            ]),
            ("DRIVE TOOLS", [
                ("◈", "Bootable Creator","bootable",   ""),
                ("◌", "Storage Format",  "format",     ""),
            ]),
        ]

        for sec_label, items in sections:
            tk.Label(f, text=sec_label, bg=BG1, fg=TEXT_SUB,
                     font=("Courier New", 8, "bold")).pack(
                anchor="w", padx=18, pady=(10,2))
            for icon, label, tab_id, badge in items:
                btn = NavBtn(f, icon, label,
                             on_click=lambda t=tab_id: self._show_tab(t),
                             badge=badge)
                btn.pack(fill="x")
                self._nav_btns[tab_id] = btn
            # Divider
            tk.Frame(f, bg=BORDER, height=1).pack(fill="x", padx=14, pady=4)

    def _sep(self):
        tk.Frame(self._sidebar, bg=BORDER, height=1).pack(
            fill="x", padx=14, pady=6)

    # ── STATS ROW ─────────────────────────────────────────────────

    def _build_stats_row(self):
        self._sc_cpu  = StatCard(self._stats_row, "CPU Load")
        self._sc_mem  = StatCard(self._stats_row, "Memory")
        self._sc_disk = StatCard(self._stats_row, "Disk /")
        self._sc_proc = StatCard(self._stats_row, "Processes")
        for c in [self._sc_cpu, self._sc_mem, self._sc_disk, self._sc_proc]:
            c.pack(side="left", fill="both", expand=True, padx=1, pady=1)

    # ── FOOTER ────────────────────────────────────────────────────

    def _build_footer(self, parent):
        segs = [
            ("NORMAL", BG, NEON, True),
            ("F1 Help", BG1, TEXT_DIM, False),
            ("Ctrl+K Quick Run", BG1, TEXT_DIM, False),
            ("Ctrl+L Clear", BG1, TEXT_DIM, False),
            ("Esc Cancel", BG1, TEXT_DIM, False),
        ]
        for text, bg, fg, bold in segs:
            fnt = ("Courier New", 9, "bold") if bold else FT_TINY
            lbl = tk.Label(parent, text=text, bg=bg, fg=fg, font=fnt,
                            padx=10, pady=0)
            if bold:
                lbl.configure(relief="flat")
            lbl.pack(side="left", fill="y")
            tk.Frame(parent, bg=BORDER, width=1).pack(side="left", fill="y")
        tk.Label(parent, text="● CONNECTED", bg=BG1, fg=EMERALD,
                 font=FT_TINY).pack(side="right", padx=12)

    # ── CLOCK ─────────────────────────────────────────────────────

    def _update_clock(self):
        self._clock_lbl.configure(text=datetime.now().strftime("%H:%M:%S"))
        self.root.after(1000, self._update_clock)

    # ── METRICS LOOP ──────────────────────────────────────────────

    def _start_metrics(self):
        self._cpu_prev = get_cpu_percent()
        self.root.after(1500, self._poll_metrics)

    def _poll_metrics(self):
        try:
            # CPU
            cur = get_cpu_percent()
            pt, pi = self._cpu_prev
            ct, ci = cur
            diff_total = ct - pt; diff_idle = ci - pi
            cpu_pct = 0 if diff_total == 0 else round(100 * (1 - diff_idle/diff_total), 1)
            self._cpu_prev = cur
            self._sc_cpu.update(f"{cpu_pct}%", cpu_pct)

            # Memory
            mem = shell("cat /proc/meminfo | grep -E '^(MemTotal|MemAvailable)'")
            lines = {l.split(':')[0]: int(l.split(':')[1].strip().split()[0])
                     for l in mem.splitlines() if ':' in l}
            mt = lines.get("MemTotal", 1)
            ma = lines.get("MemAvailable", mt)
            mem_pct = round(100 * (1 - ma/mt), 1)
            mem_used_gb = round((mt - ma) / 1024 / 1024, 1)
            self._sc_mem.update(f"{mem_pct}%", mem_pct)

            # Disk
            disk = shell("df / | tail -1")
            parts = disk.split()
            disk_pct = int(parts[4].replace("%","")) if len(parts) >= 5 else 0
            self._sc_disk.update(f"{disk_pct}%", disk_pct)

            # Processes
            procs = shell("ps -e --no-headers | wc -l")
            self._sc_proc.update(procs.strip() or "—", 30, NEON)

            # Status
            self._status.set(f"  CPU {cpu_pct}%  RAM {mem_pct}%  Disk {disk_pct}%  |  {datetime.now().strftime('%H:%M:%S')}",
                              f"MEM {mem_used_gb}GB used", EMERALD)
        except Exception:
            pass
        self.root.after(4000, self._poll_metrics)

    # ── NAVIGATION ────────────────────────────────────────────────

    def _show_tab(self, tab_id):
        if self._active_nav and self._active_nav in self._nav_btns:
            self._nav_btns[self._active_nav].deactivate()
        self._active_nav = tab_id
        if tab_id in self._nav_btns:
            self._nav_btns[tab_id].activate()
        self._bc_lbl.configure(text=tab_id.replace("_"," "))
        self._clear_content()

        dispatch = {
            "overview":  self._show_overview,
            "sysinfo":   lambda: self._run_feature(1, "System Information"),
            "process":   lambda: self._run_feature(2, "Process Monitor"),
            "realtime":  self._show_realtime,
            "hardware":  lambda: self._run_feature(12, "Hardware Info"),
            "network":   lambda: self._run_feature(4, "Network Interfaces"),
            "bandwidth": lambda: self._run_feature(5, "Bandwidth Statistics"),
            "ports":     lambda: self._run_feature(6, "Port Scanner"),
            "services":  lambda: self._run_feature(7, "Service Manager"),
            "disk":      lambda: self._run_feature(8, "Disk Analysis"),
            "cleanup":   lambda: self._run_feature(9, "Cleanup Tools"),
            "security":  lambda: self._run_feature(10, "Security Check"),
            "updates":   lambda: self._run_feature(11, "Package Updates"),
            "files":     self._show_files,
            "search":    self._show_search,
            "organizer": self._show_organizer,
            "bootable":  self._show_bootable,
            "format":    self._show_format,
        }
        fn = dispatch.get(tab_id)
        if fn: fn()

    def _clear_content(self):
        for w in self._content.winfo_children():
            w.destroy()

    # ── OVERVIEW ──────────────────────────────────────────────────

    def _show_overview(self):
        self._show_tab("overview") if self._active_nav != "overview" else None
        if self._active_nav != "overview":
            return
        sf = ScrollFrame(self._content, bg=BG)
        sf.pack(fill="both", expand=True)
        f = sf.inner

        # ASCII art
        art = tk.Label(f,
            text=(
                "█▀▀ █▀▄▀█ ▄▀█ █▀█ ▀█▀ █▀█ █▀█ █▀\n"
                "▄▄█ █ ▀ █ █▀█ █▀▄  █  █▄█ █▀▀ ▄█"
            ),
            bg=BG, fg=NEON, font=("Courier New", 11, "bold"), justify="left")
        art.pack(anchor="w", padx=20, pady=(20, 4))

        tk.Label(f, text="Kali SmartOps Manager PRO  ·  Midnight Edition  ·  PowerShell Core",
                 bg=BG, fg=TEXT_DIM, font=FT_SMALL).pack(anchor="w", padx=20, pady=(0,16))

        # Meters row
        meters_f = tk.Frame(f, bg=BG)
        meters_f.pack(fill="x", padx=20, pady=(0,16))
        meter_data = [
            ("CPU",     NEON),
            ("Memory",  EMERALD),
            ("Disk /",  WARN),
            ("Swap",    PURPLE),
        ]
        self._meters = {}
        for label, color in meter_data:
            mf = tk.Frame(meters_f, bg=BG1,
                          highlightbackground=BORDER2, highlightthickness=1)
            mf.pack(side="left", expand=True, fill="both", padx=4)
            m = ArcMeter(mf, label=label, size=110, color=color, bg=BG1)
            m.pack(pady=12, padx=12)
            self._meters[label] = m
        self._update_meters()

        # System snapshot table
        tk.Label(f, text="SYSTEM SNAPSHOT", bg=BG, fg=NEON,
                 font=FT_HEADER).pack(anchor="w", padx=20, pady=(8,4))
        tbl = DataTable(f, ["Property", "Value"])
        tbl.pack(fill="x", padx=20, pady=(0,12))
        tbl.col_width("Property", 180); tbl.col_width("Value", 500)

        def load_snapshot():
            rows = []
            rows.append(("Hostname", shell("hostname") or "—"))
            rows.append(("OS", shell("lsb_release -d 2>/dev/null | cut -f2") or
                         shell("cat /etc/os-release | grep PRETTY_NAME | cut -d= -f2 | tr -d '\"'") or "—"))
            rows.append(("Kernel", shell("uname -r") or "—"))
            rows.append(("Uptime", shell("uptime -p") or shell("uptime") or "—"))
            rows.append(("CPU Model", shell("lscpu | grep 'Model name' | cut -d: -f2 | xargs") or "—"))
            rows.append(("CPU Cores", shell("nproc") or "—"))
            rows.append(("Arch", shell("uname -m") or "—"))
            mem = shell("free -h | grep '^Mem'")
            if mem:
                parts = mem.split()
                rows.append(("Memory Total", parts[1] if len(parts)>1 else "—"))
                rows.append(("Memory Used",  parts[2] if len(parts)>2 else "—"))
                rows.append(("Memory Free",  parts[3] if len(parts)>3 else "—"))
            rows.append(("Python", platform.python_version()))
            rows.append(("Platform", platform.system()))
            for row in rows:
                self.root.after(0, lambda r=row: tbl.insert(r))
        threading.Thread(target=load_snapshot, daemon=True).start()

        # Quick cards
        tk.Label(f, text="QUICK ACCESS", bg=BG, fg=NEON,
                 font=FT_HEADER).pack(anchor="w", padx=20, pady=(8,4))
        cards_f = tk.Frame(f, bg=BG)
        cards_f.pack(fill="x", padx=20, pady=(0,20))
        cards = [
            ("⬡", "System Info",     "sysinfo",   "OS · CPU · Memory · Uptime"),
            ("▶", "Realtime Monitor","realtime",  "CPU · RAM · Disk live metrics"),
            ("◎", "Network",         "network",   "Interfaces · Connections · Ports"),
            ("⬡", "Security",        "security",  "Suspicious procs · Login history"),
            ("⊞", "File Organizer",  "organizer", "Auto-sort files by type"),
            ("◉", "Disk Analysis",   "disk",      "Usage · Directories · File types"),
        ]
        for i, (ico, title, tab, desc) in enumerate(cards):
            col = i % 3
            row = i // 3
            card = tk.Frame(cards_f, bg=BG_CARD,
                            highlightbackground=BORDER2, highlightthickness=1,
                            cursor="hand2")
            card.grid(row=row, column=col, padx=4, pady=4, sticky="ew")
            cards_f.columnconfigure(col, weight=1)
            tk.Label(card, text=ico, bg=BG_CARD, fg=NEON,
                     font=("Courier New", 18)).pack(anchor="w", padx=12, pady=(10,2))
            tk.Label(card, text=title, bg=BG_CARD, fg=TEXT,
                     font=FT_BOLD).pack(anchor="w", padx=12)
            tk.Label(card, text=desc, bg=BG_CARD, fg=TEXT_DIM,
                     font=FT_SMALL).pack(anchor="w", padx=12, pady=(0,10))
            for w in [card] + list(card.winfo_children()):
                w.bind("<Button-1>", lambda e, t=tab: self._show_tab(t))
                w.bind("<Enter>", lambda e, c=card: c.configure(bg=BG_HOVER,
                    highlightbackground=NEON))
                w.bind("<Leave>", lambda e, c=card: c.configure(bg=BG_CARD,
                    highlightbackground=BORDER2))

    def _update_meters(self):
        if not hasattr(self, "_meters"):
            return
        def fetch():
            try:
                # CPU
                cur = get_cpu_percent()
                pt, pi = self._cpu_prev
                ct, ci = cur
                dT = ct - pt; dI = ci - pi
                cpu_p = 0 if dT == 0 else round(100*(1-dI/dT),1)
                self._cpu_prev = cur

                # Mem
                mem = shell("cat /proc/meminfo | grep -E '^(MemTotal|MemAvailable|SwapTotal|SwapFree)'")
                d = {l.split(':')[0]: int(l.split(':')[1].strip().split()[0])
                     for l in mem.splitlines() if ':' in l}
                mt = d.get("MemTotal",1); ma = d.get("MemAvailable",mt)
                mem_p = round(100*(1-ma/mt),1)
                st = d.get("SwapTotal",1); sf = d.get("SwapFree",st)
                swap_p = round(100*(1-sf/st),1) if st > 0 else 0

                # Disk
                disk = shell("df / | tail -1").split()
                disk_p = int(disk[4].replace("%","")) if len(disk)>=5 else 0

                self.root.after(0, lambda: [
                    self._meters.get("CPU") and self._meters["CPU"].set(cpu_p),
                    self._meters.get("Memory") and self._meters["Memory"].set(mem_p),
                    self._meters.get("Disk /") and self._meters["Disk /"].set(disk_p),
                    self._meters.get("Swap") and self._meters["Swap"].set(swap_p),
                ])
            except: pass
        threading.Thread(target=fetch, daemon=True).start()
        self.root.after(5000, self._update_meters)

    # ── REALTIME ──────────────────────────────────────────────────

    def _show_realtime(self):
        f = self._content
        tk.Label(f, text="REAL-TIME MONITOR", bg=BG, fg=NEON,
                 font=FT_HEADER).pack(anchor="w", padx=16, pady=(12,8))

        # Meters row
        meters_row = tk.Frame(f, bg=BG)
        meters_row.pack(fill="x", padx=16, pady=(0,12))
        self._rt_meters = {}
        for label, color in [("CPU", NEON), ("Memory", EMERALD), ("Disk /", WARN), ("Swap", PURPLE)]:
            mf = tk.Frame(meters_row, bg=BG1,
                          highlightbackground=BORDER2, highlightthickness=1)
            mf.pack(side="left", expand=True, fill="both", padx=4)
            m = ArcMeter(mf, label=label, size=120, color=color, bg=BG1)
            m.pack(pady=14, padx=14)
            self._rt_meters[label] = m

        # Bars
        bars_f = tk.Frame(f, bg=BG1,
                          highlightbackground=BORDER2, highlightthickness=1)
        bars_f.pack(fill="x", padx=16, pady=(0,12))
        tk.Label(bars_f, text="RESOURCE USAGE", bg=BG1, fg=NEON,
                 font=FT_BOLD).pack(anchor="w", padx=12, pady=(8,4))
        self._rt_bars = {}
        for label in ["CPU", "Memory", "Disk /", "Swap", "Network RX", "Network TX"]:
            bar = MiniBar(bars_f, label)
            bar.pack(fill="x", padx=12, pady=3)
            self._rt_bars[label] = bar
        tk.Frame(bars_f, bg=BG1, height=8).pack()

        # Info table
        tbl_f = tk.Frame(f, bg=BG)
        tbl_f.pack(fill="both", expand=True, padx=16, pady=(0,12))
        self._rt_table = DataTable(tbl_f, ["Metric", "Value", "Status"])
        self._rt_table.pack(fill="both", expand=True)
        self._rt_table.col_width("Metric", 160)
        self._rt_table.col_width("Value",  200)
        self._rt_table.col_width("Status", 120)

        self._rt_running = True
        self._rt_update()

    def _rt_update(self):
        if not hasattr(self, "_rt_running") or not self._rt_running:
            return
        # Check widgets still exist
        try:
            self._rt_meters["CPU"].winfo_exists()
        except:
            return

        def fetch():
            try:
                cur = get_cpu_percent()
                pt, pi = self._cpu_prev; ct, ci = cur
                dT = ct-pt; dI = ci-pi
                cpu_p = 0 if dT==0 else round(100*(1-dI/dT),1)
                self._cpu_prev = cur

                mem = shell("cat /proc/meminfo | grep -E '^(MemTotal|MemAvailable|SwapTotal|SwapFree|Buffers|Cached)'")
                d = {}
                for line in mem.splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        parts = v.strip().split()
                        if parts: d[k.strip()] = int(parts[0])
                mt = d.get("MemTotal",1); ma = d.get("MemAvailable",mt)
                mem_p = round(100*(1-ma/mt),1)
                st = d.get("SwapTotal",1); sf = d.get("SwapFree",st)
                swap_p = round(100*(1-sf/st),1) if st > 0 else 0

                disk = shell("df / | tail -1").split()
                disk_p = int(disk[4].replace("%","")) if len(disk)>=5 else 0
                disk_used = disk[2] if len(disk)>2 else "?"
                disk_avail = disk[3] if len(disk)>3 else "?"

                load = shell("cat /proc/loadavg").split()[:3]
                load_str = "  ".join(load) if load else "—"

                procs = shell("ps -e --no-headers | wc -l").strip()
                threads = shell("ps -eLf --no-headers | wc -l").strip()

                net_rx = shell("cat /proc/net/dev | awk 'NR>2{sum+=$2} END{printf \"%.1f\", sum/1024/1024}'")
                net_tx = shell("cat /proc/net/dev | awk 'NR>2{sum+=$10} END{printf \"%.1f\", sum/1024/1024}'")

                cpu_status = "CRITICAL" if cpu_p>85 else "HIGH" if cpu_p>65 else "NORMAL"
                mem_status = "CRITICAL" if mem_p>90 else "HIGH" if mem_p>75 else "NORMAL"
                disk_status = "CRITICAL" if disk_p>90 else "WARNING" if disk_p>80 else "GOOD"

                rows = [
                    ("CPU Usage",        f"{cpu_p}%",                    cpu_status),
                    ("Memory Usage",     f"{mem_p}% ({human_size((mt-ma)*1024)})", mem_status),
                    ("Memory Free",      human_size(ma*1024),             ""),
                    ("Swap Usage",       f"{swap_p}%",                   ""),
                    ("Disk Usage (/)",   f"{disk_p}% (used: {disk_used}K)", disk_status),
                    ("Disk Free (/)",    f"{disk_avail}K",                ""),
                    ("Load Average",     load_str,                        ""),
                    ("Running Processes",procs,                           ""),
                    ("Threads",          threads,                         ""),
                    ("Net RX Total",     f"{net_rx} MB",                  ""),
                    ("Net TX Total",     f"{net_tx} MB",                  ""),
                ]

                def update():
                    try:
                        for key, m in self._rt_meters.items():
                            m.winfo_exists()
                        self._rt_meters["CPU"].set(cpu_p)
                        self._rt_meters["Memory"].set(mem_p)
                        self._rt_meters["Disk /"].set(disk_p)
                        self._rt_meters["Swap"].set(swap_p)
                        for label, val in [("CPU",cpu_p),("Memory",mem_p),
                                           ("Disk /",disk_p),("Swap",swap_p)]:
                            self._rt_bars[label].set(val)
                        try:
                            rx_f = float(net_rx or "0")
                            tx_f = float(net_tx or "0")
                            max_net = max(rx_f, tx_f, 1)
                            self._rt_bars["Network RX"].set(min(rx_f/max_net*100,100), NEON)
                            self._rt_bars["Network TX"].set(min(tx_f/max_net*100,100), PURPLE)
                        except: pass
                        self._rt_table.clear()
                        for row in rows:
                            tag = "danger" if "CRITICAL" in row[2] else \
                                  "warn" if "HIGH" in row[2] or "WARNING" in row[2] else \
                                  "good" if "NORMAL" in row[2] or "GOOD" in row[2] else ""
                            self._rt_table.insert(row, tag)
                    except: pass
                self.root.after(0, update)
            except: pass
        threading.Thread(target=fetch, daemon=True).start()
        self.root.after(3000, self._rt_update)

    # ── GENERIC FEATURE RUNNER ────────────────────────────────────

    def _run_feature(self, feature_num, title, params=""):
        f = self._content
        # Header
        hdr = tk.Frame(f, bg=BG1)
        hdr.pack(fill="x")
        tk.Label(hdr, text=title.upper(), bg=BG1, fg=NEON,
                 font=FT_HEADER).pack(side="left", padx=16, pady=10)
        run_btn = tk.Button(hdr, text="▶  Run Again", bg=NEON, fg="#000",
                            font=FT_BOLD, relief="flat", padx=14, pady=4,
                            cursor="hand2")
        run_btn.pack(side="right", padx=16, pady=8)

        # Output
        out = TermOutput(f)
        out.pack(fill="both", expand=True)
        run_btn.configure(command=lambda: self._exec_feature(feature_num, params, out))
        self._exec_feature(feature_num, params, out)

    def _exec_feature(self, feature_num, params, out_widget):
        out_widget.clear()
        cmd = f"pwsh smartops.ps1 -Feature {feature_num}{params}"
        out_widget.append(f"$ {cmd}", "dim")
        out_widget.append("", "dim")
        self._status.set(f"  Running Feature {feature_num}…", color=WARN)

        def run():
            try:
                result = subprocess.run(
                    ["pwsh", "-File", "smartops.ps1", "-Feature", str(feature_num)]
                    + self._parse_params(params),
                    capture_output=True, text=True, timeout=60
                )
                lines = (result.stdout + ("\n" + result.stderr if result.stderr else "")).splitlines()
                def update():
                    for line in lines:
                        out_widget.append_raw(line)
                    self._status.set("  Done.", color=EMERALD)
                self.root.after(0, update)
            except FileNotFoundError:
                def show_mock():
                    out_widget.append("⚠ pwsh not found — showing simulated output", "warn")
                    out_widget.append("", "dim")
                    self._mock_output(feature_num, out_widget)
                    self._status.set("  Simulated output (pwsh not available)", color=WARN)
                self.root.after(0, show_mock)
            except Exception as e:
                self.root.after(0, lambda: [
                    out_widget.append(f"❌ Error: {e}", "danger"),
                    self._status.set("  Error.", color=DANGER)
                ])
        threading.Thread(target=run, daemon=True).start()

    def _parse_params(self, params_str):
        import shlex
        try:
            return shlex.split(params_str)
        except:
            return []

    def _mock_output(self, feature_num, out_widget):
        """Simulated output when pwsh is unavailable — uses live /proc data."""
        def append(t, tag="text"): out_widget.append(t, tag)

        if feature_num == 1:
            append("══════════════ SYSTEM INFORMATION ══════════════", "section")
            append(f"▶ OS:     {shell('lsb_release -d 2>/dev/null | cut -f2') or platform.system()}", "neon")
            append(f"   {shell('uname -a') or platform.version()}")
            append(f"▶ Uptime: {shell('uptime -p') or 'N/A'}", "neon")
            append(f"▶ CPU:    {shell('lscpu | grep Model | cut -d: -f2 | xargs') or platform.processor()}", "neon")
            append(f"   Cores: {shell('nproc') or '?'}")
            mem_raw = shell("free -h | grep '^Mem'").split()
            if mem_raw:
                append(f"▶ Memory: Total={mem_raw[1]}  Used={mem_raw[2]}  Free={mem_raw[3]}", "neon")
            disk = shell("df -h / | tail -1")
            append(f"▶ Disk:   {disk}", "neon")
            append(f"▶ Users:  {shell('who')}", "neon")

        elif feature_num == 2:
            append("══════════════ TOP PROCESSES ══════════════", "section")
            append(f"{'PID':<8} {'PROCESS':<25} {'CPU%':<8} {'MEM%':<8}", "neon")
            append("─"*55, "dim")
            procs = shell_lines("ps -eo pid,comm,%cpu,%mem --sort=-%cpu | head -16")[1:]
            for p in procs:
                append(f"  {p}")

        elif feature_num == 3:
            append("══════════════ REAL-TIME METRICS ══════════════", "section")
            cpu_raw = shell("top -bn1 | grep 'Cpu(s)'")
            append(f"▶ CPU: {cpu_raw}", "neon")
            mem_raw = shell("free -h | grep '^Mem'").split()
            if mem_raw:
                append(f"▶ MEM: Total={mem_raw[1]}  Used={mem_raw[2]}  Free={mem_raw[3]}", "neon")
            append(f"▶ Load: {shell('uptime')}", "neon")

        elif feature_num == 4:
            append("══════════════ NETWORK INTERFACES ══════════════", "section")
            for line in shell_lines("ip -br addr show"):
                tag = "emerald" if "UP" in line else "dim"
                pre = "✅" if "UP" in line else "❌"
                append(f"  {pre} {line}", tag)
            append("▶ Connections:", "neon")
            for line in shell_lines("ss -tuln | head -20"):
                append(f"  {line}")

        elif feature_num == 5:
            append("══════════════ BANDWIDTH STATS ══════════════", "section")
            ifaces = shell_lines("ip -br link | grep -v LOOPBACK | awk '{print $1}'")
            for iface in ifaces:
                rx = shell(f"cat /sys/class/net/{iface}/statistics/rx_bytes 2>/dev/null")
                tx = shell(f"cat /sys/class/net/{iface}/statistics/tx_bytes 2>/dev/null")
                if rx and tx:
                    append(f"▶ {iface}", "neon")
                    append(f"  📥 RX: {human_size(int(rx))}")
                    append(f"  📤 TX: {human_size(int(tx))}")

        elif feature_num == 6:
            append("══════════════ OPEN PORTS ══════════════", "section")
            for line in shell_lines("ss -tuln | grep LISTEN"):
                append(f"  🔌 {line}", "emerald")

        elif feature_num == 7:
            append("══════════════ SERVICE MANAGER ══════════════", "section")
            append("▶ Running Services:", "neon")
            for line in shell_lines("systemctl list-units --type=service --state=running 2>/dev/null | head -20"):
                append(f"  ✅ {line}", "emerald")
            append("▶ Failed Services:", "neon")
            failed = shell_lines("systemctl --failed 2>/dev/null | grep '^●' | head -10")
            if failed:
                for line in failed:
                    append(f"  ❌ {line}", "danger")
            else:
                append("  ✅ No failed services", "emerald")

        elif feature_num == 8:
            append("══════════════ DISK ANALYSIS ══════════════", "section")
            for line in shell_lines("df -h | grep '^/dev'"):
                append(f"  {line}")
            append("▶ Top directories:", "neon")
            for line in shell_lines("du -sh /* 2>/dev/null | sort -rh | head -12"):
                append(f"  📁 {line}")

        elif feature_num == 9:
            append("══════════════ CLEANUP TOOLS ══════════════", "section")
            cache = shell("du -sh /var/cache/apt/archives 2>/dev/null | awk '{print $1}'") or "N/A"
            append(f"▶ APT Cache: {cache}", "neon")
            old_logs = shell("find /var/log -name '*.log' -mtime +30 2>/dev/null | wc -l")
            append(f"▶ Old Logs (>30d): {old_logs}", "warn" if int(old_logs or 0) > 5 else "neon")
            tmp = shell("du -sh /tmp 2>/dev/null | awk '{print $1}'") or "N/A"
            append(f"▶ /tmp size: {tmp}", "neon")

        elif feature_num == 10:
            append("══════════════ SECURITY CHECK ══════════════", "section")
            append("▶ Last Logins:", "neon")
            for line in shell_lines("last -n 10 2>/dev/null"):
                append(f"  {line}")
            append("▶ High CPU Processes:", "neon")
            for line in shell_lines("ps -eo pid,comm,%cpu --sort=-%cpu | head -6")[1:]:
                append(f"  {line}")

        elif feature_num == 11:
            append("══════════════ PACKAGE UPDATES ══════════════", "section")
            append("▶ Checking updates…", "neon")
            updates = shell_lines("apt list --upgradable 2>/dev/null | grep -v Listing | head -20")
            if updates:
                for u in updates:
                    append(f"  📦 {u}")
                append(f"  Total upgradable: {len(updates)}", "emerald")
            else:
                append("  ✅ System is up to date!", "emerald")

        elif feature_num == 12:
            append("══════════════ HARDWARE INFO ══════════════", "section")
            for line in shell_lines("lscpu | grep -E '^(Model name|Architecture|CPU|Thread|Core|Socket|Virt)'"):
                append(f"  {line}")
            append("▶ Memory:", "neon")
            for line in shell_lines("free -h | head -2"):
                append(f"  {line}")
            append("▶ Block Devices:", "neon")
            for line in shell_lines("lsblk | grep -v loop | head -15"):
                append(f"  💾 {line}")
            append("▶ GPU:", "neon")
            for line in shell_lines("lspci | grep -i vga"):
                append(f"  🖥️  {line}")

        elif feature_num == 22:
            append("══════════════ STORAGE DEVICES ══════════════", "section")
            for line in shell_lines("lsblk -o NAME,SIZE,TYPE,MOUNTPOINT,FSTYPE | grep -v loop"):
                append(f"  💾 {line}")

    # ── FILE MANAGER ──────────────────────────────────────────────

    def _show_files(self):
        f = self._content
        cwd = [Path.home()]
        hist = [Path.home()]
        hist_pos = [0]
        selected = set()

        # Toolbar
        tb = tk.Frame(f, bg=BG1)
        tb.pack(fill="x")

        nav_f = tk.Frame(tb, bg=BG1)
        nav_f.pack(side="left", padx=6, pady=6)
        path_var = tk.StringVar(value=str(Path.home()))

        def load(path):
            path = Path(path)
            if not path.is_dir():
                messagebox.showerror("Error", f"Not a directory: {path}")
                return
            cwd[0] = path
            path_var.set(str(path))
            update_bread()
            refresh()

        def go_back():
            if hist_pos[0] > 0:
                hist_pos[0] -= 1
                load(hist[hist_pos[0]])
        def go_fwd():
            if hist_pos[0] < len(hist)-1:
                hist_pos[0] += 1
                load(hist[hist_pos[0]])
        def go_up():
            p = cwd[0].parent
            if p != cwd[0]:
                hist.append(p); hist_pos[0] = len(hist)-1
                load(p)
        def go_home():
            load(Path.home())

        for icon, tip, cmd in [("←","Back",go_back),("→","Fwd",go_fwd),
                                ("⌂","Home",go_home),("↑","Up",go_up),
                                ("⟳","Refresh",lambda: load(cwd[0]))]:
            b = tk.Button(nav_f, text=icon, bg=BG1, fg=NEON, font=FT_LABEL,
                           relief="flat", cursor="hand2", command=cmd, padx=8)
            b.pack(side="left", padx=2)
            Tooltip(b, tip)

        # Path entry
        pf = tk.Frame(tb, bg=BG_CARD, highlightbackground=BORDER2, highlightthickness=1)
        pf.pack(side="left", fill="x", expand=True, padx=8, pady=8)
        pe = tk.Entry(pf, textvariable=path_var, bg=BG_CARD, fg=TEXT,
                      font=FT_MONO, insertbackground=NEON, relief="flat", bd=4)
        pe.pack(fill="x")
        pe.bind("<Return>", lambda _: load(path_var.get()))

        # Search
        sf = tk.Frame(tb, bg=BG_CARD, highlightbackground=BORDER2, highlightthickness=1)
        sf.pack(side="right", padx=8, pady=8)
        tk.Label(sf, text="⌕", bg=BG_CARD, fg=TEXT_DIM,
                 font=("Courier New", 11)).pack(side="left", padx=(6,2))
        search_var = tk.StringVar()
        sk = tk.Entry(sf, textvariable=search_var, bg=BG_CARD, fg=TEXT,
                      font=FT_MONO, insertbackground=NEON, relief="flat", bd=4, width=16)
        sk.pack(side="left")

        # Breadcrumb
        bread_f = tk.Frame(f, bg=BG1)
        bread_f.pack(fill="x")

        def update_bread():
            for w in bread_f.winfo_children():
                w.destroy()
            parts = list(cwd[0].parts)
            for i, part in enumerate(parts):
                p = Path(*parts[:i+1])
                col = NEON if i == len(parts)-1 else TEXT_DIM
                lbl = tk.Label(bread_f, text=part or "/", bg=BG1, fg=col,
                                font=FT_SMALL, cursor="hand2")
                lbl.pack(side="left")
                lbl.bind("<Button-1>", lambda e, p_=p: load(p_))
                if i < len(parts)-1:
                    tk.Label(bread_f, text=" › ", bg=BG1, fg=DIM,
                             font=FT_SMALL).pack(side="left")

        # Action bar
        ab = tk.Frame(f, bg=BG1)
        ab.pack(fill="x")
        for label, icon, cmd_fn, color in [
            ("New Folder", "📁", lambda: new_folder(), NEON),
            ("Copy",       "⎘",  lambda: copy_sel(),   EMERALD),
            ("Move",       "✂",  lambda: move_sel(),   WARN),
            ("Delete",     "🗑", lambda: del_sel(),    DANGER),
            ("Select All", "☑",  lambda: sel_all(),    MUTED),
        ]:
            tk.Button(ab, text=f"{icon} {label}", bg=BG1, fg=color,
                      font=FT_SMALL, relief="flat", cursor="hand2",
                      command=cmd_fn, padx=10, pady=5).pack(side="left", padx=2, pady=4)

        # Table
        tbl = DataTable(f, ["Type","Name","Size","Modified","Permissions"])
        tbl.pack(fill="both", expand=True, padx=4, pady=(0,4))
        tbl.col_width("Type", 60)
        tbl.col_width("Name", 300)
        tbl.col_width("Size", 100)
        tbl.col_width("Modified", 150)
        tbl.col_width("Permissions", 120)

        # Double-click to navigate
        def on_double(e):
            sel = tbl._tree.selection()
            if not sel: return
            vals = tbl._tree.item(sel[0])["values"]
            if vals[0] == "📁 DIR":
                p = cwd[0] / vals[1]
                hist.append(p); hist_pos[0] = len(hist)-1
                load(p)
            else:
                try:
                    subprocess.Popen(["xdg-open", str(cwd[0]/vals[1])],
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except: pass
        tbl._tree.bind("<Double-1>", on_double)

        def refresh():
            tbl.clear()
            selected.clear()
            try:
                items = []
                for entry in os.scandir(cwd[0]):
                    try:
                        st = entry.stat(follow_symlinks=False)
                        items.append({
                            "name": entry.name,
                            "isdir": entry.is_dir(follow_symlinks=False),
                            "size": st.st_size,
                            "mtime": st.st_mtime,
                            "mode": st.st_mode,
                        })
                    except:
                        items.append({"name": entry.name, "isdir": entry.is_dir(),
                                      "size": 0, "mtime": 0, "mode": 0})
                items.sort(key=lambda x: (0 if x["isdir"] else 1, x["name"].lower()))

                q = search_var.get().lower()
                if q:
                    items = [i for i in items if q in i["name"].lower()]

                for item in items:
                    typ = "📁 DIR" if item["isdir"] else "📄 FILE"
                    sz  = "—" if item["isdir"] else human_size(item["size"])
                    mt  = datetime.fromtimestamp(item["mtime"]).strftime("%Y-%m-%d %H:%M") if item["mtime"] else "—"
                    pm  = stat.filemode(item["mode"]) if item["mode"] else "—"
                    tbl.insert((typ, item["name"], sz, mt, pm))
                self._status.set(f"  {len(items)} items in {cwd[0].name or str(cwd[0])}")
            except PermissionError:
                self._status.set("  ⚠ Permission denied", color=WARN)

        search_var.trace("w", lambda *_: refresh())

        def sel_all():
            for item in tbl._tree.get_children():
                vals = tbl._tree.item(item)["values"]
                selected.add(cwd[0] / vals[1])
            tbl._tree.selection_set(tbl._tree.get_children())

        def new_folder():
            d = tk.Toplevel(f)
            d.configure(bg=BG_CARD); d.title("New Folder"); d.geometry("340x130")
            d.resizable(False, False)
            tk.Label(d, text="Folder name:", bg=BG_CARD, fg=TEXT, font=FT_BOLD).pack(padx=20, pady=(20,6), anchor="w")
            var = tk.StringVar()
            e = tk.Entry(d, textvariable=var, bg=BG, fg=TEXT, font=FT_MONO,
                         insertbackground=NEON, relief="flat", bd=8)
            e.pack(fill="x", padx=20); e.focus()
            def create():
                name = var.get().strip()
                if name:
                    try: (cwd[0]/name).mkdir(parents=False, exist_ok=False)
                    except Exception as ex: messagebox.showerror("Error", str(ex))
                d.destroy(); refresh()
            tk.Button(d, text="Create", command=create, bg=NEON, fg="#000",
                      font=FT_BOLD, relief="flat", pady=6).pack(fill="x", padx=20, pady=12)
            e.bind("<Return>", lambda _: create())

        def _get_sel_paths():
            sel = tbl._tree.selection()
            return [cwd[0] / tbl._tree.item(s)["values"][1] for s in sel] if sel else []

        def copy_sel():
            paths = _get_sel_paths()
            if not paths: messagebox.showinfo("Copy","Select items first"); return
            dest = filedialog.askdirectory(title="Copy To", initialdir=str(cwd[0]))
            if dest:
                for src in paths:
                    subprocess.run(f"cp -r '{src}' '{dest}'", shell=True)
                refresh()

        def move_sel():
            paths = _get_sel_paths()
            if not paths: messagebox.showinfo("Move","Select items first"); return
            dest = filedialog.askdirectory(title="Move To", initialdir=str(cwd[0]))
            if dest:
                for src in paths:
                    subprocess.run(f"mv -n '{src}' '{dest}'", shell=True)
                refresh()

        def del_sel():
            paths = _get_sel_paths()
            if not paths: messagebox.showinfo("Delete","Select items first"); return
            if messagebox.askyesno("Delete", f"Delete {len(paths)} item(s)? Cannot be undone."):
                for p in paths:
                    subprocess.run(f"rm -rf '{p}'", shell=True)
                refresh()

        update_bread()
        refresh()

    # ── FILE SEARCH ───────────────────────────────────────────────

    def _show_search(self):
        f = self._content
        tk.Label(f, text="FILE SEARCH", bg=BG, fg=NEON,
                 font=FT_HEADER).pack(anchor="w", padx=16, pady=(12,8))

        ctrl = tk.Frame(f, bg=BG1, highlightbackground=BORDER2, highlightthickness=1)
        ctrl.pack(fill="x", padx=16, pady=(0,8))

        pat_var = tk.StringVar()
        dir_var = tk.StringVar(value=str(Path.home()))

        for label, var, browse in [("Pattern", pat_var, None), ("Directory", dir_var, True)]:
            row = tk.Frame(ctrl, bg=BG1)
            row.pack(fill="x", padx=12, pady=6)
            tk.Label(row, text=label, bg=BG1, fg=TEXT_DIM,
                     font=FT_SMALL, width=10, anchor="w").pack(side="left")
            tk.Entry(row, textvariable=var, bg=BG_CARD, fg=TEXT,
                     font=FT_MONO, insertbackground=NEON,
                     relief="flat", bd=6).pack(side="left", fill="x", expand=True, padx=(8,0))
            if browse:
                tk.Button(row, text="Browse", bg=BG_CARD, fg=NEON,
                          font=FT_SMALL, relief="flat",
                          command=lambda: dir_var.set(
                              filedialog.askdirectory(initialdir=dir_var.get()) or dir_var.get()
                          )).pack(side="right", padx=4)

        # Results table
        tbl = DataTable(f, ["Path","Size","Modified"])
        tbl.pack(fill="both", expand=True, padx=16, pady=(0,12))
        tbl.col_width("Path", 500)
        tbl.col_width("Size", 100)
        tbl.col_width("Modified", 150)

        out = TermOutput(f)
        out.pack(fill="x", padx=16, pady=(0,8))
        out.configure(height=4)

        def run():
            pat = pat_var.get().strip()
            d   = dir_var.get().strip() or "."
            if not pat: messagebox.showinfo("Search","Enter a pattern"); return
            tbl.clear(); out.clear()
            out.append(f"$ find '{d}' -name '*{pat}*'", "dim")
            self._status.set("  Searching…", color=WARN)
            def search():
                try:
                    results = []
                    for root_d, dirs, files in os.walk(d):
                        dirs[:] = [dd for dd in dirs if not dd.startswith('.')]
                        for fname in files:
                            if pat.lower() in fname.lower():
                                fp = Path(root_d) / fname
                                try:
                                    st = fp.stat()
                                    results.append((str(fp), human_size(st.st_size),
                                                    datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M")))
                                except:
                                    results.append((str(fp),"—","—"))
                        if len(results) >= 200: break
                    def update():
                        for r in results[:200]:
                            tbl.insert(r)
                        out.append(f"📊 Found {len(results)} matches", "emerald")
                        self._status.set(f"  Found {len(results)} matches", color=EMERALD)
                    self.root.after(0, update)
                except Exception as e:
                    self.root.after(0, lambda: out.append(f"❌ {e}", "danger"))
            threading.Thread(target=search, daemon=True).start()

        btn_row = tk.Frame(ctrl, bg=BG1)
        btn_row.pack(fill="x", padx=12, pady=8)
        tk.Button(btn_row, text="▶  Search", command=run, bg=NEON, fg="#000",
                  font=FT_BOLD, relief="flat", padx=14, pady=5).pack(side="right")

    # ── FILE ORGANIZER ────────────────────────────────────────────

    def _show_organizer(self):
        f = self._content
        tk.Label(f, text="AUTOMATED FILE ORGANIZER", bg=BG, fg=NEON,
                 font=FT_HEADER).pack(anchor="w", padx=16, pady=(12,4))
        tk.Label(f, text="Sorts files by type → Images / Documents / Videos / Music / Archives",
                 bg=BG, fg=TEXT_DIM, font=FT_SMALL).pack(anchor="w", padx=16, pady=(0,8))

        ctrl = tk.Frame(f, bg=BG1, highlightbackground=BORDER2, highlightthickness=1)
        ctrl.pack(fill="x", padx=16, pady=(0,8))

        row = tk.Frame(ctrl, bg=BG1)
        row.pack(fill="x", padx=12, pady=12)
        tk.Label(row, text="Directory", bg=BG1, fg=TEXT_DIM,
                 font=FT_SMALL, width=10, anchor="w").pack(side="left")
        dir_var = tk.StringVar(value=str(Path.home() / "Downloads"))
        tk.Entry(row, textvariable=dir_var, bg=BG_CARD, fg=TEXT,
                 font=FT_MONO, insertbackground=NEON,
                 relief="flat", bd=6).pack(side="left", fill="x", expand=True, padx=(8,0))
        tk.Button(row, text="Browse", bg=BG_CARD, fg=NEON, font=FT_SMALL, relief="flat",
                  command=lambda: dir_var.set(
                      filedialog.askdirectory(initialdir=dir_var.get()) or dir_var.get()
                  )).pack(side="right", padx=4)

        dry_var = tk.BooleanVar(value=True)
        dr = tk.Frame(ctrl, bg=BG1)
        dr.pack(fill="x", padx=12, pady=(0,8))
        tk.Checkbutton(dr, text="Dry Run (preview only — no files moved)",
                       variable=dry_var, bg=BG1, fg=WARN,
                       selectcolor=BG, activebackground=BG1, font=FT_SMALL).pack(side="left")

        out = TermOutput(f)
        out.pack(fill="both", expand=True, padx=16, pady=(0,4))

        # Results summary
        summary_f = tk.Frame(f, bg=BG1)
        summary_f.pack(fill="x", padx=16, pady=(0,12))
        self._org_summary = {}
        for folder, icon, color in [("Images","🖼️",CYAN),("Documents","📄",NEON),
                                     ("Videos","🎬",PURPLE),("Music","🎵",EMERALD),
                                     ("Archives","📦",WARN),("Skipped","⏭",TEXT_DIM)]:
            sf2 = tk.Frame(summary_f, bg=BG1,
                           highlightbackground=BORDER2, highlightthickness=1)
            sf2.pack(side="left", expand=True, fill="both", padx=3)
            tk.Label(sf2, text=icon, bg=BG1, fg=color,
                     font=("Courier New", 16)).pack(pady=(8,2))
            tk.Label(sf2, text=folder, bg=BG1, fg=TEXT_DIM, font=FT_TINY).pack()
            cnt_lbl = tk.Label(sf2, text="0", bg=BG1, fg=color, font=FT_BIG)
            cnt_lbl.pack(pady=(0,8))
            self._org_summary[folder] = cnt_lbl

        def run():
            d = dir_var.get().strip()
            if not d or not Path(d).is_dir():
                messagebox.showerror("Error","Not a valid directory"); return
            out.clear()
            dry = dry_var.get()
            if dry:
                out.append("▶ DRY RUN — no files will be moved", "warn")
            out.append(f"▶ Organizing: {d}", "neon")
            out.append("", "dim")

            def organize():
                CATEGORIES = {
                    "Images":    ["jpg","jpeg","png","gif","svg","webp","bmp","ico","tiff"],
                    "Documents": ["pdf","doc","docx","txt","ppt","pptx","xls","xlsx","odt","rtf","md","csv"],
                    "Videos":    ["mp4","mkv","mov","avi","webm","flv","wmv"],
                    "Music":     ["mp3","wav","flac","aac","ogg","m4a","wma"],
                    "Archives":  ["zip","rar","tar","gz","7z","bz2","xz","tar.gz"],
                }
                ext_map = {}
                for cat, exts in CATEGORIES.items():
                    for e in exts:
                        ext_map[e] = cat

                counts = {k: 0 for k in list(CATEGORIES.keys()) + ["Skipped"]}
                base = Path(d)

                if not dry:
                    for cat in CATEGORIES:
                        (base/cat).mkdir(exist_ok=True)

                for item in base.iterdir():
                    if item.is_dir(): continue
                    ext = item.suffix.lstrip(".").lower()
                    if not ext:
                        self.root.after(0, lambda n=item.name: out.append(
                            f"[SKIP]     '{n}' — no extension", "dim"))
                        counts["Skipped"] += 1
                        continue
                    cat = ext_map.get(ext)
                    if not cat:
                        self.root.after(0, lambda n=item.name, x=ext: out.append(
                            f"[SKIP]     '{n}' — unknown type (.{x})", "dim"))
                        counts["Skipped"] += 1
                        continue
                    tag_map = {"Images":"neon","Documents":"neon","Videos":"purple",
                               "Music":"emerald","Archives":"warn"}
                    self.root.after(0, lambda n=item.name, c=cat, tg=tag_map.get(cat,"text"): out.append(
                        f"[{c.upper():<10}] Moving '{n}' → {c}/", tg))
                    counts[cat] += 1
                    if not dry:
                        try:
                            item.rename(base/cat/item.name)
                        except Exception as e:
                            self.root.after(0, lambda err=e: out.append(f"  ❌ {err}", "danger"))

                def finish():
                    out.append("", "dim")
                    out.append("══════════════ SUMMARY ══════════════", "section")
                    for k, v in counts.items():
                        out.append(f"  {k:<12}: {v} file(s)", "emerald" if v > 0 else "dim")
                    out.append("", "dim")
                    out.append("✅ DONE!" if not dry else "✅ Dry run complete — review above", "emerald")
                    for k, lbl in self._org_summary.items():
                        lbl.configure(text=str(counts.get(k, 0)))
                    self._status.set("  Organization complete", color=EMERALD)
                self.root.after(100, finish)

            threading.Thread(target=organize, daemon=True).start()
            self._status.set("  Organizing…", color=WARN)

        btn_row = tk.Frame(ctrl, bg=BG1)
        btn_row.pack(fill="x", padx=12, pady=(0,12))
        tk.Button(btn_row, text="▶  Organize Now", command=run, bg=EMERALD, fg="#000",
                  font=FT_BOLD, relief="flat", padx=14, pady=5).pack(side="right")

    # ── STORAGE / BOOTABLE / FORMAT ───────────────────────────────

    def _show_bootable(self):
        f = self._content
        tk.Label(f, text="BOOTABLE DRIVE CREATOR", bg=BG, fg=DANGER,
                 font=FT_HEADER).pack(anchor="w", padx=16, pady=(12,4))
        tk.Label(f, text="⚠  WARNING: This will DESTROY ALL DATA on the target device!",
                 bg=BG, fg=WARN, font=FT_BOLD).pack(anchor="w", padx=16, pady=(0,10))

        ctrl = tk.Frame(f, bg=BG1, highlightbackground=BORDER2, highlightthickness=1)
        ctrl.pack(fill="x", padx=16, pady=(0,8))

        dev_var = tk.StringVar(value="/dev/sdb")
        iso_var = tk.StringVar()

        for label, var, browse in [("Target Device", dev_var, None), ("ISO File", iso_var, True)]:
            row = tk.Frame(ctrl, bg=BG1)
            row.pack(fill="x", padx=12, pady=6)
            tk.Label(row, text=label, bg=BG1, fg=TEXT_DIM,
                     font=FT_SMALL, width=14, anchor="w").pack(side="left")
            tk.Entry(row, textvariable=var, bg=BG_CARD, fg=TEXT,
                     font=FT_MONO, insertbackground=NEON,
                     relief="flat", bd=6).pack(side="left", fill="x", expand=True, padx=(8,0))
            if browse:
                tk.Button(row, text="Browse", bg=BG_CARD, fg=NEON, font=FT_SMALL, relief="flat",
                          command=lambda: iso_var.set(
                              filedialog.askopenfilename(
                                  filetypes=[("ISO Files","*.iso"),("All","*.*")]) or iso_var.get()
                          )).pack(side="right", padx=4)

        out = TermOutput(f)
        out.pack(fill="both", expand=True, padx=16, pady=(0,12))

        def run():
            dev = dev_var.get().strip(); iso = iso_var.get().strip()
            if not dev or not iso:
                messagebox.showwarning("Missing","Set both device and ISO"); return
            if not messagebox.askyesno("CONFIRM DANGER",
                f"Write:\n  {iso}\nto:\n  {dev}\n\nALL DATA ON {dev} WILL BE DESTROYED!"):
                return
            out.clear()
            out.append(f"⚠️  WARNING: Destroying all data on {dev}!", "danger")
            out.append(f"📀 ISO: {iso}", "neon")
            out.append(f"💽 Target: {dev}", "neon")

            cmd = f"pwsh smartops.ps1 -Feature 21 -Device '{dev}' -IsoPath '{iso}'"
            def run_cmd():
                try:
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=600)
                    lines = (result.stdout + result.stderr).splitlines()
                    self.root.after(0, lambda: [out.append_raw(l) for l in lines])
                except FileNotFoundError:
                    self.root.after(0, lambda: out.append(
                        "pwsh not found. Would run:\n  sudo dd if=\"{iso}\" of=\"{dev}\" bs=4M status=progress", "warn"))
                except Exception as e:
                    self.root.after(0, lambda: out.append(f"❌ {e}", "danger"))
            threading.Thread(target=run_cmd, daemon=True).start()

        btn_row = tk.Frame(ctrl, bg=BG1)
        btn_row.pack(fill="x", padx=12, pady=(0,12))
        tk.Button(btn_row, text="🚀  Create Bootable USB", command=run, bg=DANGER, fg="white",
                  font=FT_BOLD, relief="flat", padx=14, pady=7).pack(side="right")
        tk.Button(btn_row, text="List Devices", bg=BG_CARD, fg=NEON, font=FT_SMALL, relief="flat",
                  command=lambda: self._exec_feature(22, "", out)).pack(side="right", padx=(0,8))

    def _show_format(self):
        f = self._content
        tk.Label(f, text="STORAGE FORMAT", bg=BG, fg=DANGER,
                 font=FT_HEADER).pack(anchor="w", padx=16, pady=(12,4))
        tk.Label(f, text="⚠  WARNING: This will ERASE all data on the selected device!",
                 bg=BG, fg=WARN, font=FT_BOLD).pack(anchor="w", padx=16, pady=(0,10))

        ctrl = tk.Frame(f, bg=BG1, highlightbackground=BORDER2, highlightthickness=1)
        ctrl.pack(fill="x", padx=16, pady=(0,8))

        dev_var = tk.StringVar(value="/dev/sdb1")
        fs_var  = tk.StringVar(value="ext4")
        lbl_var = tk.StringVar()

        row1 = tk.Frame(ctrl, bg=BG1)
        row1.pack(fill="x", padx=12, pady=6)
        tk.Label(row1, text="Device", bg=BG1, fg=TEXT_DIM,
                 font=FT_SMALL, width=14, anchor="w").pack(side="left")
        tk.Entry(row1, textvariable=dev_var, bg=BG_CARD, fg=TEXT,
                 font=FT_MONO, insertbackground=NEON,
                 relief="flat", bd=6).pack(side="left", fill="x", expand=True, padx=8)

        row2 = tk.Frame(ctrl, bg=BG1)
        row2.pack(fill="x", padx=12, pady=6)
        tk.Label(row2, text="Filesystem", bg=BG1, fg=TEXT_DIM,
                 font=FT_SMALL, width=14, anchor="w").pack(side="left")
        style = ttk.Style(); style.configure("Dark.TCombobox",
            fieldbackground=BG_CARD, background=BG_CARD, foreground=TEXT)
        cb = ttk.Combobox(row2, textvariable=fs_var, values=["ext4","ntfs","fat32","exfat"],
                           state="readonly", width=14)
        cb.pack(side="left", padx=8)

        row3 = tk.Frame(ctrl, bg=BG1)
        row3.pack(fill="x", padx=12, pady=6)
        tk.Label(row3, text="Label (opt.)", bg=BG1, fg=TEXT_DIM,
                 font=FT_SMALL, width=14, anchor="w").pack(side="left")
        tk.Entry(row3, textvariable=lbl_var, bg=BG_CARD, fg=TEXT,
                 font=FT_MONO, insertbackground=NEON,
                 relief="flat", bd=6).pack(side="left", fill="x", expand=True, padx=8)

        out = TermOutput(f)
        out.pack(fill="both", expand=True, padx=16, pady=(0,12))

        def run():
            dev = dev_var.get().strip(); fs = fs_var.get(); lbl = lbl_var.get().strip()
            if not dev:
                messagebox.showwarning("Missing","Set device path"); return
            if not messagebox.askyesno("CONFIRM",
                f"Format {dev} as {fs}?\nALL DATA WILL BE ERASED!"):
                return
            out.clear()
            out.append(f"⚠️  Formatting {dev} as {fs}…", "warn")
            args = f" -Device '{dev}' -Filesystem '{fs}'"
            if lbl: args += f" -Label '{lbl}'"
            cmd = f"pwsh smartops.ps1 -Feature 23{args}"
            def run_cmd():
                try:
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
                    lines = (result.stdout+result.stderr).splitlines()
                    self.root.after(0, lambda: [out.append_raw(l) for l in lines])
                except FileNotFoundError:
                    native_cmd = f"sudo umount {dev} 2>/dev/null; sudo mkfs.{fs} {'-F ' if fs in ('ext4','ntfs') else ''}{'-L '+lbl+' ' if lbl else ''}{dev}"
                    self.root.after(0, lambda: out.append(
                        f"pwsh not found.\nNative equivalent:\n  {native_cmd}", "warn"))
                except Exception as e:
                    self.root.after(0, lambda: out.append(f"❌ {e}", "danger"))
            threading.Thread(target=run_cmd, daemon=True).start()

        btn_row = tk.Frame(ctrl, bg=BG1)
        btn_row.pack(fill="x", padx=12, pady=(0,12))
        tk.Button(btn_row, text="⚡  Format Device", command=run, bg=DANGER, fg="white",
                  font=FT_BOLD, relief="flat", padx=14, pady=7).pack(side="right")
        tk.Button(btn_row, text="List Devices", bg=BG_CARD, fg=NEON, font=FT_SMALL, relief="flat",
                  command=lambda: self._exec_feature(22, "", out)).pack(side="right", padx=(0,8))

    # ── CMD INPUT ─────────────────────────────────────────────────

    def _handle_cmd(self, _):
        val = self._cmd.get().strip()
        if not val: return
        self._history.insert(0, val)
        self._hist_idx = -1
        self._cmd.delete(0, "end")

        try: num = int(val)
        except: num = None

        if num and 1 <= num <= 17:
            self._show_tab({
                1:"sysinfo",2:"process",3:"realtime",4:"network",5:"bandwidth",
                6:"ports",7:"services",8:"disk",9:"cleanup",10:"security",
                11:"updates",12:"hardware",13:"files",16:"search",17:"organizer"
            }.get(num,"sysinfo"))
        elif val == "help":
            self._show_tab("overview")
        elif val in ("clear","cls"):
            self._clear_content()
        else:
            self._clear_content()
            out = TermOutput(self._content)
            out.pack(fill="both", expand=True)
            out.append(f"$ {val}", "dim")
            def run():
                result = subprocess.run(val, shell=True, capture_output=True, text=True, timeout=30)
                lines = (result.stdout + result.stderr).splitlines()
                self.root.after(0, lambda: [out.append_raw(l) for l in (lines or ["(no output)"])])
            threading.Thread(target=run, daemon=True).start()

    def _hist_up(self, _):
        if self._history:
            self._hist_idx = min(self._hist_idx+1, len(self._history)-1)
            self._cmd.delete(0,"end")
            self._cmd.insert(0, self._history[self._hist_idx])

    def _hist_dn(self, _):
        self._hist_idx = max(self._hist_idx-1, -1)
        self._cmd.delete(0,"end")
        if self._hist_idx >= 0:
            self._cmd.insert(0, self._history[self._hist_idx])


# ═══════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════
def main():
    root = tk.Tk()
    try:
        style = ttk.Style(root)
        style.theme_use("clam")
        style.configure("TScrollbar", background=BG1, troughcolor=BG,
                         bordercolor=BG, arrowcolor=TEXT_DIM, relief="flat")
        style.configure("TCombobox", fieldbackground=BG_CARD,
                         background=BG_CARD, foreground=TEXT,
                         selectbackground=BG_ACTIVE, selectforeground=NEON,
                         arrowcolor=NEON)
        style.map("TCombobox",
                  fieldbackground=[("readonly", BG_CARD)],
                  selectbackground=[("readonly", BG_ACTIVE)])
    except Exception:
        pass

    app = SmartOpsPro(root)
    root.mainloop()


if __name__ == "__main__":
    main()