#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║        KALI SMARTOPS MANAGER PRO — OBSIDIAN EDITION          ║
║        Rewritten · Enhanced UI · All Bugs Fixed              ║
╚══════════════════════════════════════════════════════════════╝
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess, threading, os, stat, sys, math, time, json, shlex
from datetime import datetime
from pathlib import Path
import platform

# ═══════════════════════════════════════════════════════════════
#  PALETTE — Obsidian Dark
# ═══════════════════════════════════════════════════════════════
BG          = "#050508"
BG1         = "#0a0a0f"
BG2         = "#0e0e15"
BG3         = "#12121a"
BG_CARD     = "#14141e"
BG_HOVER    = "#1a1a28"
BG_ACTIVE   = "#151f3a"
BORDER      = "#1c1c2e"
BORDER2     = "#252538"
BORDER_NEON = "#00bfff30"
DIM         = "#2a2a40"
MUTED       = "#3a3a55"
TEXT        = "#e2e2f0"
TEXT_DIM    = "#6060a0"
TEXT_SUB    = "#38384a"
NEON        = "#00c8ff"
NEON2       = "#0090d0"
NEON_DIM    = "#00182a"
NEON_GLOW   = "#00c8ff20"
EMERALD     = "#00ffaa"
EM_DIM      = "#001a10"
EMERALD2    = "#00cc88"
WARN        = "#ffcc00"
WARN_DIM    = "#1a1400"
DANGER      = "#ff4455"
DANGER_DIM  = "#1a0008"
PURPLE      = "#9966ff"
PURPLE2     = "#7744dd"
PINK        = "#ff44aa"
CYAN        = "#00e5ff"
GOLD        = "#ffaa00"

# ── FONTS ────────────────────────────────────────────────────
FT_TITLE   = ("JetBrains Mono", 13, "bold")
FT_HEADER  = ("JetBrains Mono", 11, "bold")
FT_LABEL   = ("JetBrains Mono", 10)
FT_BOLD    = ("JetBrains Mono", 10, "bold")
FT_MONO    = ("JetBrains Mono", 10)
FT_MONO_S  = ("JetBrains Mono", 9)
FT_SMALL   = ("JetBrains Mono", 9)
FT_TINY    = ("JetBrains Mono", 8)
FT_BIG     = ("JetBrains Mono", 18, "bold")
FT_HUGE    = ("JetBrains Mono", 24, "bold")

# Fallback font chain
def _resolve_fonts():
    import tkinter.font as tkfont
    try:
        root_tmp = tk.Tk(); root_tmp.withdraw()
        families = tkfont.families(root_tmp)
        root_tmp.destroy()
        for preferred in ["JetBrains Mono", "Fira Code", "Cascadia Code", "Consolas", "Courier New"]:
            if preferred in families:
                return preferred
    except:
        pass
    return "Courier New"

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
    return [l for l in shell(cmd, timeout).splitlines() if l.strip()]

def human_size(n):
    try:
        n = float(n)
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if n < 1024:
                return f"{n:.1f} {unit}"
            n /= 1024
        return f"{n:.1f} PB"
    except:
        return "—"

def get_cpu_stat():
    try:
        line = shell("grep 'cpu ' /proc/stat")
        vals = list(map(int, line.split()[1:]))
        return sum(vals), vals[3]
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
        x = self.widget.winfo_rootx() + 28
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 6
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.geometry(f"+{x}+{y}")
        outer = tk.Frame(self.tip, bg=NEON, padx=1, pady=1)
        outer.pack()
        tk.Label(outer, text=self.text, bg=BG_CARD, fg=TEXT,
                 font=FT_SMALL, padx=10, pady=5).pack()

    def hide(self, _):
        if self.tip:
            self.tip.destroy()
            self.tip = None

# ═══════════════════════════════════════════════════════════════
#  ARC METER
# ═══════════════════════════════════════════════════════════════
class ArcMeter(tk.Canvas):
    def __init__(self, parent, label="", size=120, color=NEON, **kw):
        kw.pop("bg", None)
        super().__init__(parent, width=size, height=size + 20,
                         bg=BG_CARD, bd=0, highlightthickness=0, **kw)
        self.size = size
        self.color = color
        self.label = label
        self._val = 0
        self._target = 0
        self._draw(0)

    def set(self, pct):
        self._target = max(0.0, min(100.0, float(pct)))
        self._animate()

    def _animate(self):
        diff = self._target - self._val
        if abs(diff) < 0.5:
            self._val = self._target
            self._draw(self._val)
            return
        self._val += diff * 0.18
        self._draw(self._val)
        self.after(16, self._animate)

    def _draw(self, pct):
        self.delete("all")
        s = self.size
        pad = 14
        cx, cy = s / 2, s / 2 + 4
        r = s / 2 - pad

        # Outer glow ring
        glow_col = DANGER if pct > 85 else WARN if pct > 65 else self.color
        for g in range(3, 0, -1):
            alpha_pad = pad - g * 2
            self.create_arc(alpha_pad, alpha_pad + 4, s - alpha_pad, s - alpha_pad + 4,
                            start=225, extent=-270, outline=glow_col,
                            style="arc", width=1)

        # Track
        self.create_arc(pad, pad + 4, s - pad, s - pad + 4,
                        start=225, extent=-270,
                        outline=DIM, style="arc", width=10)

        # Segment ticks
        for i in range(0, 101, 10):
            angle = math.radians(225 - (270 * i / 100))
            r_out = r + 2
            r_in  = r - 4
            x1 = cx + r_out * math.cos(angle)
            y1 = cy - r_out * math.sin(angle)
            x2 = cx + r_in  * math.cos(angle)
            y2 = cy - r_in  * math.sin(angle)
            tick_col = glow_col if i <= pct else TEXT_SUB
            self.create_line(x1, y1, x2, y2, fill=tick_col, width=1)

        # Fill arc
        if pct > 0:
            extent = -int(270 * pct / 100)
            self.create_arc(pad, pad + 4, s - pad, s - pad + 4,
                            start=225, extent=extent,
                            outline=glow_col, style="arc", width=8)

        # Tip dot
        angle = math.radians(225 - (270 * pct / 100))
        dx = cx + r * math.cos(angle)
        dy = cy - r * math.sin(angle)
        self.create_oval(dx - 6, dy - 6, dx + 6, dy + 6,
                         fill=glow_col, outline=BG_CARD, width=2)

        # Inner circle background
        inner_r = r - 14
        self.create_oval(cx - inner_r, cy - inner_r,
                         cx + inner_r, cy + inner_r,
                         fill=BG3, outline=BORDER2, width=1)

        # Value text
        self.create_text(cx, cy - 7,
                         text=f"{int(pct)}",
                         fill=glow_col, font=("JetBrains Mono", 14, "bold"))
        self.create_text(cx, cy + 10,
                         text="%",
                         fill=TEXT_DIM, font=("JetBrains Mono", 8))

        # Label below
        self.create_text(s / 2, s + 10,
                         text=self.label.upper(),
                         fill=TEXT_DIM, font=("JetBrains Mono", 7, "bold"))

# ═══════════════════════════════════════════════════════════════
#  SCROLL FRAME (BUG FIXED)
# ═══════════════════════════════════════════════════════════════
class ScrollFrame(tk.Frame):
    def __init__(self, parent, **kw):
        bg = kw.pop("bg", BG)  # ← FIX: pop before unpacking
        super().__init__(parent, bg=bg, **kw)
        canvas = tk.Canvas(self, bg=bg, bd=0, highlightthickness=0)
        vsb = tk.Scrollbar(self, orient="vertical", command=canvas.yview,
                           bg=BG2, troughcolor=BG, bd=0, width=5,
                           activebackground=NEON)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        self.inner = tk.Frame(canvas, bg=bg)
        win = canvas.create_window((0, 0), window=self.inner, anchor="nw")

        def on_cfg(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
        def on_canvas_cfg(e):
            canvas.itemconfigure(win, width=e.width)

        self.inner.bind("<Configure>", on_cfg)
        canvas.bind("<Configure>", on_canvas_cfg)

        def _scroll(e):
            canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
        for w in [canvas, self.inner]:
            w.bind("<MouseWheel>", _scroll)
            w.bind("<Button-4>", lambda e: canvas.yview_scroll(-3, "units"))
            w.bind("<Button-5>", lambda e: canvas.yview_scroll(3, "units"))
        self._canvas = canvas

# ═══════════════════════════════════════════════════════════════
#  DATA TABLE
# ═══════════════════════════════════════════════════════════════
class DataTable(tk.Frame):
    def __init__(self, parent, columns, **kw):
        super().__init__(parent, bg=BG1, **kw)
        style = ttk.Style()
        style.theme_use("clam")
        uid = f"T{id(self)}"
        style.configure(f"{uid}.Treeview",
            background=BG1, foreground=TEXT, fieldbackground=BG1,
            rowheight=28, font=FT_MONO_S, borderwidth=0)
        style.configure(f"{uid}.Treeview.Heading",
            background=BG3, foreground=NEON, font=FT_BOLD,
            relief="flat", borderwidth=0, padding=(8, 6))
        style.map(f"{uid}.Treeview",
            background=[("selected", BG_ACTIVE)],
            foreground=[("selected", NEON)])
        style.layout(f"{uid}.Treeview", [
            ("Treeview.treearea", {"sticky": "nswe"})
        ])

        self._tree = ttk.Treeview(self, columns=columns, show="headings",
                                   style=f"{uid}.Treeview")
        for col in columns:
            self._tree.heading(col, text=col.upper())
            self._tree.column(col, anchor="w", width=120, minwidth=60)

        vsb = ttk.Scrollbar(self, orient="vertical", command=self._tree.yview)
        hsb = ttk.Scrollbar(self, orient="horizontal", command=self._tree.xview)
        self._tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self._tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self._tree.tag_configure("odd",    background=BG2)
        self._tree.tag_configure("even",   background=BG1)
        self._tree.tag_configure("warn",   foreground=WARN)
        self._tree.tag_configure("danger", foreground=DANGER)
        self._tree.tag_configure("good",   foreground=EMERALD)
        self._tree.tag_configure("neon",   foreground=NEON)
        self._tree.tag_configure("purple", foreground=PURPLE)

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
#  NAV BUTTON — enhanced
# ═══════════════════════════════════════════════════════════════
class NavBtn(tk.Frame):
    def __init__(self, parent, icon, label, on_click, badge="", shortcut=""):
        super().__init__(parent, bg=BG1, cursor="hand2")
        self._active = False
        self._on_click = on_click

        self._glow = tk.Frame(self, bg=BG1, width=3)
        self._glow.pack(side="left", fill="y")

        inner = tk.Frame(self, bg=BG1)
        inner.pack(side="left", fill="x", expand=True, padx=(10, 8), pady=6)

        self._ico = tk.Label(inner, text=icon, bg=BG1, fg=TEXT_DIM,
                              font=("JetBrains Mono", 12), width=2)
        self._ico.pack(side="left", padx=(0, 8))

        self._lbl = tk.Label(inner, text=label, bg=BG1, fg=TEXT_DIM,
                              font=FT_SMALL, anchor="w")
        self._lbl.pack(side="left", fill="x", expand=True)

        if shortcut:
            tk.Label(inner, text=shortcut, bg=BG1, fg=TEXT_SUB,
                     font=FT_TINY).pack(side="right")

        if badge:
            bk = EMERALD if badge == "NEW" else PURPLE if badge == "PRO" else DIM
            bc = BG if badge in ("NEW", "PRO") else TEXT_DIM
            tk.Label(inner, text=badge, bg=bk, fg=bc,
                     font=FT_TINY, padx=5, pady=1).pack(side="right", padx=4)

        for w in self._all_widgets():
            w.bind("<Button-1>", lambda e: self._on_click())
            w.bind("<Enter>",    self._enter)
            w.bind("<Leave>",    self._leave)

    def _all_widgets(self):
        def collect(w):
            yield w
            for c in w.winfo_children():
                yield from collect(c)
        return list(collect(self))

    def _enter(self, _=None):
        if not self._active:
            for w in self._all_widgets():
                try: w.configure(bg=BG_HOVER)
                except: pass
            self._ico.configure(fg=TEXT)
            self._lbl.configure(fg=TEXT)

    def _leave(self, _=None):
        if not self._active:
            for w in self._all_widgets():
                try: w.configure(bg=BG1)
                except: pass
            self._ico.configure(fg=TEXT_DIM)
            self._lbl.configure(fg=TEXT_DIM)

    def activate(self):
        self._active = True
        for w in self._all_widgets():
            try: w.configure(bg=BG_ACTIVE)
            except: pass
        self._glow.configure(bg=NEON)
        self._ico.configure(fg=NEON, bg=BG_ACTIVE)
        self._lbl.configure(fg=TEXT, bg=BG_ACTIVE, font=FT_BOLD)

    def deactivate(self):
        self._active = False
        for w in self._all_widgets():
            try: w.configure(bg=BG1)
            except: pass
        self._glow.configure(bg=BG1)
        self._ico.configure(fg=TEXT_DIM, bg=BG1)
        self._lbl.configure(fg=TEXT_DIM, bg=BG1, font=FT_SMALL)

# ═══════════════════════════════════════════════════════════════
#  TERMINAL OUTPUT
# ═══════════════════════════════════════════════════════════════
class TermOutput(tk.Frame):
    def __init__(self, parent, **kw):
        super().__init__(parent, bg=BG, **kw)
        # Header bar
        hbar = tk.Frame(self, bg=BG3, height=28)
        hbar.pack(fill="x")
        hbar.pack_propagate(False)
        for dot, col in [("●", DANGER), ("●", WARN), ("●", EMERALD)]:
            tk.Label(hbar, text=dot, bg=BG3, fg=col,
                     font=("JetBrains Mono", 10)).pack(side="left", padx=(6, 2))
        tk.Label(hbar, text="TERMINAL OUTPUT", bg=BG3, fg=TEXT_DIM,
                 font=FT_TINY).pack(side="left", padx=12)
        tk.Button(hbar, text="⟳ Clear", bg=BG3, fg=TEXT_DIM,
                  font=FT_TINY, relief="flat", cursor="hand2",
                  command=self.clear, padx=8).pack(side="right", padx=4)

        self._text = tk.Text(self, bg="#020408", fg=TEXT,
                              font=FT_MONO, bd=0, padx=16, pady=12,
                              insertbackground=NEON, selectbackground=NEON_DIM,
                              selectforeground=NEON, relief="flat", wrap="none",
                              state="disabled", spacing1=2, spacing3=2)
        vsb = tk.Scrollbar(self, command=self._text.yview,
                            bg=BG1, troughcolor=BG, bd=0, width=5)
        hsb = tk.Scrollbar(self, command=self._text.xview,
                            orient="horizontal", bg=BG1, troughcolor=BG, bd=0, width=5)
        self._text.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self._text.pack(fill="both", expand=True)

        tags = {
            "neon":    {"foreground": NEON},
            "emerald": {"foreground": EMERALD},
            "warn":    {"foreground": WARN},
            "danger":  {"foreground": DANGER},
            "dim":     {"foreground": TEXT_DIM},
            "purple":  {"foreground": PURPLE},
            "pink":    {"foreground": PINK},
            "text":    {"foreground": TEXT},
            "section": {"foreground": NEON, "font": FT_BOLD},
            "cmd":     {"foreground": TEXT_DIM, "font": FT_MONO_S},
        }
        for name, cfg in tags.items():
            self._text.tag_configure(name, **cfg)

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
        low = text.lower()
        if any(k in low for k in ["✅", "success", "done", "ok ","good", "normal", "active"]):
            tag = "emerald"
        elif any(k in low for k in ["⚠", "warning", "warn", "caution"]):
            tag = "warn"
        elif any(k in low for k in ["❌", "error", "fail", "critical", "danger", "denied"]):
            tag = "danger"
        elif text.startswith("$") or text.startswith("  $"):
            tag = "cmd"
        elif any(k in text for k in ["═", "╔", "╚", "║", "──", "▶", "►", "●"]):
            tag = "section"
        else:
            tag = "text"
        self.append(text, tag)

# ═══════════════════════════════════════════════════════════════
#  STAT CARD
# ═══════════════════════════════════════════════════════════════
class StatCard(tk.Frame):
    def __init__(self, parent, title, icon="", color=NEON, **kw):
        super().__init__(parent, bg=BG_CARD, padx=16, pady=12,
                         highlightbackground=BORDER, highlightthickness=1, **kw)
        self._color = color
        # Icon + title row
        top = tk.Frame(self, bg=BG_CARD)
        top.pack(fill="x")
        if icon:
            tk.Label(top, text=icon, bg=BG_CARD, fg=color,
                     font=("JetBrains Mono", 14)).pack(side="left")
        tk.Label(top, text=title.upper(), bg=BG_CARD, fg=TEXT_DIM,
                 font=FT_TINY).pack(side="left", padx=(6, 0))

        self._val = tk.Label(self, text="—", bg=BG_CARD, fg=color,
                              font=("JetBrains Mono", 22, "bold"))
        self._val.pack(anchor="w", pady=(4, 2))

        self._sub = tk.Label(self, text="", bg=BG_CARD, fg=TEXT_DIM, font=FT_TINY)
        self._sub.pack(anchor="w")

        # Progress bar
        bar_bg = tk.Frame(self, bg=BORDER, height=2)
        bar_bg.pack(fill="x", pady=(8, 0))
        self._bar = tk.Frame(bar_bg, bg=color, height=2, width=0)
        self._bar.place(x=0, y=0, relheight=1)

    def update(self, text, pct, sub="", color=None):
        col = color or (DANGER if pct > 85 else WARN if pct > 65 else self._color)
        self._val.configure(text=text, fg=col)
        self._sub.configure(text=sub)
        self._bar.configure(bg=col)
        self.after(20, lambda: self._bar.place(relwidth=min(pct, 100) / 100))
        # Subtle border highlight
        border_col = col if pct > 75 else BORDER
        self.configure(highlightbackground=border_col)

# ═══════════════════════════════════════════════════════════════
#  MINI BAR
# ═══════════════════════════════════════════════════════════════
class MiniBar(tk.Frame):
    def __init__(self, parent, label, **kw):
        super().__init__(parent, bg=BG1, **kw)
        tk.Label(self, text=label, bg=BG1, fg=TEXT_DIM,
                 font=FT_TINY, width=14, anchor="w").pack(side="left")
        bar_bg = tk.Frame(self, bg=DIM, height=8)
        bar_bg.pack(side="left", fill="x", expand=True, padx=(6, 10))
        self._fill = tk.Frame(bar_bg, bg=NEON, height=8)
        self._fill.place(x=0, y=0, relheight=1, relwidth=0)
        self._pct_lbl = tk.Label(self, text="  0%", bg=BG1, fg=TEXT_DIM,
                                  font=FT_TINY, width=6, anchor="e")
        self._pct_lbl.pack(side="right")

    def set(self, pct, color=None):
        col = color or (DANGER if pct > 85 else WARN if pct > 65 else EMERALD)
        self._fill.configure(bg=col)
        self._fill.place(relwidth=min(pct, 100) / 100)
        self._pct_lbl.configure(text=f"{int(pct):3}%", fg=col)

# ═══════════════════════════════════════════════════════════════
#  SECTION LABEL
# ═══════════════════════════════════════════════════════════════
def make_section(parent, text, bg=BG):
    f = tk.Frame(parent, bg=bg)
    f.pack(fill="x", padx=16, pady=(14, 4))
    tk.Label(f, text=text, bg=bg, fg=NEON,
             font=FT_HEADER).pack(side="left")
    tk.Frame(f, bg=BORDER2, height=1).pack(
        side="left", fill="x", expand=True, padx=(10, 0), pady=8)
    return f

# ═══════════════════════════════════════════════════════════════
#  MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════
class SmartOpsPro:
    def __init__(self, root):
        self.root = root
        root.title("Kali SmartOps Manager PRO — Obsidian Edition")
        root.configure(bg=BG)
        root.minsize(1100, 720)
        self._center(1440, 900)

        self._active_nav = None
        self._nav_btns   = {}
        self._cpu_prev   = (0, 0)
        self._history    = []
        self._hist_idx   = -1
        self._rt_running = False

        # Resolve font
        self._font = _resolve_fonts()
        self._patch_fonts()
        self._build()
        self._start_metrics()

    def _patch_fonts(self):
        f = self._font
        global FT_TITLE, FT_HEADER, FT_LABEL, FT_BOLD, FT_MONO, FT_MONO_S
        global FT_SMALL, FT_TINY, FT_BIG, FT_HUGE
        FT_TITLE   = (f, 13, "bold")
        FT_HEADER  = (f, 11, "bold")
        FT_LABEL   = (f, 10)
        FT_BOLD    = (f, 10, "bold")
        FT_MONO    = (f, 10)
        FT_MONO_S  = (f, 9)
        FT_SMALL   = (f, 9)
        FT_TINY    = (f, 8)
        FT_BIG     = (f, 18, "bold")
        FT_HUGE    = (f, 24, "bold")

    def _center(self, w, h):
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")

    # ── BUILD ─────────────────────────────────────────────────

    def _build(self):
        self._build_titlebar()
        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True)
        self._build_sidebar(body)
        right = tk.Frame(body, bg=BG)
        right.pack(side="left", fill="both", expand=True)
        self._build_breadcrumb(right)
        self._build_stats(right)
        self._content = tk.Frame(right, bg=BG)
        self._content.pack(fill="both", expand=True)
        self._build_input(right)
        self._build_statusbar()
        self._bind_keys()
        self._show_tab("overview")

    # ── TITLE BAR ─────────────────────────────────────────────

    def _build_titlebar(self):
        tb = tk.Frame(self.root, bg=BG1, height=44)
        tb.pack(fill="x")
        tb.pack_propagate(False)

        # Left: logo
        left = tk.Frame(tb, bg=BG1)
        left.pack(side="left", padx=14, fill="y")
        tk.Label(left, text="⬡", bg=BG1, fg=NEON,
                 font=(self._font, 16, "bold")).pack(side="left", pady=8)
        tk.Label(left, text=" SMARTOPS PRO", bg=BG1, fg=TEXT,
                 font=(self._font, 11, "bold")).pack(side="left")

        # Center: subtitle
        tk.Label(tb, text="KALI LINUX ADMINISTRATION SUITE  ·  OBSIDIAN EDITION",
                 bg=BG1, fg=TEXT_SUB,
                 font=(self._font, 8)).place(relx=0.5, rely=0.5, anchor="center")

        # Right: clock + indicators
        right = tk.Frame(tb, bg=BG1)
        right.pack(side="right", padx=16, fill="y")
        self._net_dot = tk.Label(right, text="◉ LIVE", bg=BG1, fg=EMERALD,
                                  font=(self._font, 8, "bold"))
        self._net_dot.pack(side="right", padx=(10, 0))
        tk.Frame(right, bg=BORDER, width=1).pack(side="right", fill="y", pady=8)
        self._clock_lbl = tk.Label(right, text="00:00:00", bg=BG1, fg=NEON,
                                    font=(self._font, 11, "bold"))
        self._clock_lbl.pack(side="right", padx=(10, 0))
        self._date_lbl = tk.Label(right, text="", bg=BG1, fg=TEXT_DIM,
                                   font=(self._font, 8))
        self._date_lbl.pack(side="right", padx=4)
        self._update_clock()

        # Separator line with gradient effect
        sep = tk.Frame(self.root, bg=NEON, height=1)
        sep.pack(fill="x")

    def _update_clock(self):
        now = datetime.now()
        self._clock_lbl.configure(text=now.strftime("%H:%M:%S"))
        self._date_lbl.configure(text=now.strftime("%a %d %b"))
        self.root.after(1000, self._update_clock)

    # ── SIDEBAR ───────────────────────────────────────────────

    def _build_sidebar(self, parent):
        self._sidebar = tk.Frame(parent, bg=BG1, width=230)
        self._sidebar.pack(side="left", fill="y")
        self._sidebar.pack_propagate(False)

        # Top border
        tk.Frame(self._sidebar, bg=BORDER, height=1).pack(fill="x")

        scroll = ScrollFrame(self._sidebar, bg=BG1)
        scroll.pack(fill="both", expand=True)
        f = scroll.inner

        sections = [
            ("SYSTEM", [
                ("◈", "Overview",         "overview",  "", ""),
                ("⬡", "System Info",      "sysinfo",   "", ""),
                ("⣿", "Processes",        "process",   "", ""),
                ("▶", "Realtime Monitor", "realtime",  "", ""),
                ("⬛", "Hardware",         "hardware",  "", ""),
            ]),
            ("NETWORK", [
                ("◎", "Interfaces",       "network",   "", ""),
                ("⇅", "Bandwidth",        "bandwidth", "", ""),
                ("⊕", "Port Scanner",     "ports",     "", ""),
            ]),
            ("STORAGE", [
                ("⚙", "Services",         "services",  "", ""),
                ("◉", "Disk Analysis",    "disk",      "", ""),
                ("✦", "Cleanup",          "cleanup",   "", ""),
            ]),
            ("SECURITY", [
                ("⬡", "Security Audit",   "security",  "", ""),
                ("↑", "Package Updates",  "updates",   "", ""),
            ]),
            ("FILES", [
                ("▤", "File Manager",     "files",     "", ""),
                ("⌕", "File Search",      "search",    "", ""),
                ("⊞", "File Organizer",   "organizer", "NEW", ""),
            ]),
            ("TOOLS", [
                ("◈", "Bootable Creator", "bootable",  "", ""),
                ("◌", "Format Drive",     "format",    "", ""),
            ]),
        ]

        for sec_label, items in sections:
            # Section header
            sh = tk.Frame(f, bg=BG1)
            sh.pack(fill="x", padx=14, pady=(12, 3))
            tk.Label(sh, text=sec_label, bg=BG1, fg=TEXT_SUB,
                     font=(self._font, 7, "bold")).pack(side="left")
            tk.Frame(sh, bg=BORDER, height=1).pack(
                side="left", fill="x", expand=True, padx=(6, 0), pady=4)

            for icon, label, tab_id, badge, sc in items:
                btn = NavBtn(f, icon, label,
                             on_click=lambda t=tab_id: self._show_tab(t),
                             badge=badge, shortcut=sc)
                btn.pack(fill="x")
                self._nav_btns[tab_id] = btn

        # Bottom section: sys info quick
        tk.Frame(self._sidebar, bg=BORDER, height=1).pack(fill="x", padx=0, side="bottom")
        self._sidebar_footer()

    def _sidebar_footer(self):
        ft = tk.Frame(self._sidebar, bg=BG1)
        ft.pack(side="bottom", fill="x", padx=14, pady=10)
        hostname = shell("hostname") or platform.node() or "kali"
        user = shell("whoami") or "root"
        tk.Label(ft, text=f"  {user}@{hostname}", bg=BG1, fg=TEXT_DIM,
                 font=(self._font, 8)).pack(anchor="w")
        tk.Label(ft, text=f"  {platform.system()} {platform.machine()}",
                 bg=BG1, fg=TEXT_SUB, font=(self._font, 7)).pack(anchor="w")

    # ── BREADCRUMB ────────────────────────────────────────────

    def _build_breadcrumb(self, parent):
        self._bc_frame = tk.Frame(parent, bg=BG2, height=34)
        self._bc_frame.pack(fill="x")
        self._bc_frame.pack_propagate(False)
        tk.Frame(self._bc_frame, bg=BORDER, height=1).place(x=0, rely=1.0, relwidth=1.0)
        tk.Label(self._bc_frame, text="smartops", bg=BG2, fg=NEON,
                 font=FT_TINY).place(x=14, rely=0.5, anchor="w")
        tk.Label(self._bc_frame, text=" ›", bg=BG2, fg=DIM,
                 font=FT_TINY).place(x=72, rely=0.5, anchor="w")
        self._bc_lbl = tk.Label(self._bc_frame, text="overview", bg=BG2,
                                  fg=TEXT, font=FT_TINY)
        self._bc_lbl.place(x=90, rely=0.5, anchor="w")

    # ── STATS ROW ─────────────────────────────────────────────

    def _build_stats(self, parent):
        row = tk.Frame(parent, bg=BG, height=90)
        row.pack(fill="x")
        row.pack_propagate(False)
        self._sc_cpu  = StatCard(row, "CPU Load",   icon="◉", color=NEON)
        self._sc_mem  = StatCard(row, "Memory",      icon="▣", color=EMERALD)
        self._sc_disk = StatCard(row, "Disk /",      icon="◌", color=WARN)
        self._sc_proc = StatCard(row, "Processes",   icon="⬡", color=PURPLE)
        for c in [self._sc_cpu, self._sc_mem, self._sc_disk, self._sc_proc]:
            c.pack(side="left", fill="both", expand=True, padx=1, pady=1)
        tk.Frame(parent, bg=BORDER, height=1).pack(fill="x")

    # ── INPUT BAR ─────────────────────────────────────────────

    def _build_input(self, parent):
        tk.Frame(parent, bg=BORDER, height=1).pack(fill="x")
        inp = tk.Frame(parent, bg=BG2, height=40)
        inp.pack(fill="x")
        inp.pack_propagate(False)

        tk.Label(inp, text="❯", bg=BG2, fg=NEON,
                 font=(self._font, 13, "bold")).pack(side="left", padx=(14, 6))
        self._cmd = tk.Entry(inp, bg=BG2, fg=TEXT, font=FT_MONO,
                              insertbackground=NEON, relief="flat", bd=0)
        self._cmd.pack(side="left", fill="x", expand=True)
        self._cmd.bind("<Return>", self._handle_cmd)
        self._cmd.bind("<Up>",     self._hist_up)
        self._cmd.bind("<Down>",   self._hist_dn)

        hints = tk.Label(inp, text="↵ run  ↑↓ history  Ctrl+L clear  Ctrl+K focus",
                          bg=BG2, fg=TEXT_SUB, font=FT_TINY)
        hints.pack(side="right", padx=14)

    # ── STATUS BAR ────────────────────────────────────────────

    def _build_statusbar(self):
        self._status_bar = tk.Frame(self.root, bg=BG2, height=24)
        self._status_bar.pack(fill="x", side="bottom")
        self._status_bar.pack_propagate(False)
        tk.Frame(self._status_bar, bg=BORDER, height=1).place(x=0, y=0, relwidth=1.0)
        self._status_lbl = tk.Label(self._status_bar, text="● READY", bg=BG2,
                                     fg=EMERALD, font=FT_TINY, anchor="w")
        self._status_lbl.pack(side="left", padx=12, pady=4)
        self._status_right = tk.Label(self._status_bar, text="", bg=BG2,
                                       fg=TEXT_DIM, font=FT_TINY, anchor="e")
        self._status_right.pack(side="right", padx=12)

    def set_status(self, msg, right="", color=EMERALD):
        self._status_lbl.configure(text=msg, fg=color)
        self._status_right.configure(text=right)

    # ── KEY BINDINGS ──────────────────────────────────────────

    def _bind_keys(self):
        self.root.bind("<Control-l>", lambda e: self._clear_content())
        self.root.bind("<Control-k>", lambda e: self._cmd.focus_set())
        self.root.bind("<F1>",        lambda e: self._show_tab("overview"))
        self.root.bind("<F5>",        lambda e: self._refresh_tab())

    def _refresh_tab(self):
        if self._active_nav:
            self._show_tab(self._active_nav)

    # ── METRICS LOOP ──────────────────────────────────────────

    def _start_metrics(self):
        self._cpu_prev = get_cpu_stat()
        self.root.after(1500, self._poll_metrics)

    def _poll_metrics(self):
        def fetch():
            try:
                cur = get_cpu_stat()
                pt, pi = self._cpu_prev
                ct, ci = cur
                dT, dI = ct - pt, ci - pi
                cpu_pct = 0 if dT == 0 else round(100 * (1 - dI / dT), 1)
                self._cpu_prev = cur

                mem = shell("cat /proc/meminfo | grep -E '^(MemTotal|MemAvailable)'")
                d = {}
                for line in mem.splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        parts = v.strip().split()
                        if parts:
                            d[k.strip()] = int(parts[0])
                mt = d.get("MemTotal", 1)
                ma = d.get("MemAvailable", mt)
                mem_pct = round(100 * (1 - ma / mt), 1)
                mem_used_gb = round((mt - ma) / 1024 / 1024, 1)
                mem_total_gb = round(mt / 1024 / 1024, 1)

                disk = shell("df / | tail -1").split()
                disk_pct = int(disk[4].replace("%", "")) if len(disk) >= 5 else 0

                procs = shell("ps -e --no-headers | wc -l").strip()

                def update():
                    self._sc_cpu.update(f"{cpu_pct}%", cpu_pct,
                                        sub=f"{'▰' * int(cpu_pct // 10)}{'▱' * (10 - int(cpu_pct // 10))}")
                    self._sc_mem.update(f"{mem_pct}%", mem_pct,
                                        sub=f"{mem_used_gb} / {mem_total_gb} GB")
                    self._sc_disk.update(f"{disk_pct}%", disk_pct,
                                         sub=f"used: {disk[2] if len(disk)>2 else '?'}K")
                    self._sc_proc.update(procs or "—", 30, sub="running")
                    self.set_status(
                        f"  ◉ CPU {cpu_pct}%  ▣ RAM {mem_pct}%  ◌ Disk {disk_pct}%",
                        right=f"{datetime.now().strftime('%H:%M:%S')}  ")

                self.root.after(0, update)
            except Exception:
                pass

        threading.Thread(target=fetch, daemon=True).start()
        self.root.after(4000, self._poll_metrics)

    # ── NAVIGATION ────────────────────────────────────────────

    def _show_tab(self, tab_id):
        self._rt_running = False
        if self._active_nav and self._active_nav in self._nav_btns:
            self._nav_btns[self._active_nav].deactivate()
        self._active_nav = tab_id
        if tab_id in self._nav_btns:
            self._nav_btns[tab_id].activate()
        self._bc_lbl.configure(text=tab_id.replace("_", " "))
        self._clear_content()

        dispatch = {
            "overview":  self._show_overview,
            "sysinfo":   lambda: self._run_feature(1,  "System Information"),
            "process":   lambda: self._run_feature(2,  "Process Monitor"),
            "realtime":  self._show_realtime,
            "hardware":  lambda: self._run_feature(12, "Hardware Info"),
            "network":   lambda: self._run_feature(4,  "Network Interfaces"),
            "bandwidth": lambda: self._run_feature(5,  "Bandwidth Statistics"),
            "ports":     lambda: self._run_feature(6,  "Port Scanner"),
            "services":  lambda: self._run_feature(7,  "Service Manager"),
            "disk":      lambda: self._run_feature(8,  "Disk Analysis"),
            "cleanup":   lambda: self._run_feature(9,  "Cleanup Tools"),
            "security":  lambda: self._run_feature(10, "Security Audit"),
            "updates":   lambda: self._run_feature(11, "Package Updates"),
            "files":     self._show_files,
            "search":    self._show_search,
            "organizer": self._show_organizer,
            "bootable":  self._show_bootable,
            "format":    self._show_format,
        }
        fn = dispatch.get(tab_id)
        if fn:
            fn()

    def _clear_content(self):
        for w in self._content.winfo_children():
            w.destroy()

    # ── OVERVIEW ──────────────────────────────────────────────

    def _show_overview(self):
        sf = ScrollFrame(self._content, bg=BG)
        sf.pack(fill="both", expand=True)
        f = sf.inner

        # Hero banner
        hero = tk.Frame(f, bg=BG_CARD, highlightbackground=BORDER2, highlightthickness=1)
        hero.pack(fill="x", padx=16, pady=(16, 0))
        tk.Label(hero,
            text="  KALI SMARTOPS MANAGER PRO",
            bg=BG_CARD, fg=NEON,
            font=(self._font, 20, "bold")).pack(side="left", padx=20, pady=18)
        tk.Label(hero, text="OBSIDIAN EDITION",
                 bg=BG_CARD, fg=TEXT_DIM,
                 font=(self._font, 9)).pack(side="left")
        tk.Label(hero,
            text=f"  {platform.system()} · {shell('uname -r') or 'kernel'}  ",
            bg=NEON_DIM, fg=NEON,
            font=(self._font, 9), padx=10, pady=4).pack(side="right", padx=16)

        # Meters
        make_section(f, "LIVE METRICS", bg=BG)
        meters_f = tk.Frame(f, bg=BG)
        meters_f.pack(fill="x", padx=16, pady=(0, 8))
        self._meters = {}
        for label, color in [("CPU", NEON), ("Memory", EMERALD), ("Disk /", WARN), ("Swap", PURPLE)]:
            mf = tk.Frame(meters_f, bg=BG_CARD,
                          highlightbackground=BORDER, highlightthickness=1)
            mf.pack(side="left", expand=True, fill="both", padx=4, pady=4)
            m = ArcMeter(mf, label=label, size=120, color=color)
            m.pack(pady=14, padx=14)
            self._meters[label] = m
        self._update_meters()

        # Snapshot
        make_section(f, "SYSTEM SNAPSHOT", bg=BG)
        tbl = DataTable(f, ["Property", "Value"])
        tbl.pack(fill="x", padx=16, pady=(0, 8))
        tbl.col_width("Property", 200)
        tbl.col_width("Value", 500)

        def load_snapshot():
            rows = [
                ("Hostname",    shell("hostname") or "—"),
                ("OS",          shell("lsb_release -d 2>/dev/null | cut -f2") or platform.system()),
                ("Kernel",      shell("uname -r") or "—"),
                ("Uptime",      shell("uptime -p") or shell("uptime") or "—"),
                ("CPU Model",   shell("lscpu | grep 'Model name' | cut -d: -f2 | xargs") or "—"),
                ("CPU Cores",   shell("nproc") or "—"),
                ("Architecture",shell("uname -m") or "—"),
            ]
            mem = shell("free -h | grep '^Mem'").split()
            if len(mem) >= 4:
                rows += [
                    ("Memory Total", mem[1]),
                    ("Memory Used",  mem[2]),
                    ("Memory Free",  mem[3]),
                ]
            rows += [
                ("Python",   platform.python_version()),
                ("Shell",    shell("echo $SHELL") or "—"),
                ("Timezone", shell("date +%Z") or "—"),
            ]
            for row in rows:
                self.root.after(0, lambda r=row: tbl.insert(r))
        threading.Thread(target=load_snapshot, daemon=True).start()

        # Quick access cards
        make_section(f, "QUICK ACCESS", bg=BG)
        cards_f = tk.Frame(f, bg=BG)
        cards_f.pack(fill="x", padx=16, pady=(0, 20))
        cards = [
            ("⬡", "System Info",      "sysinfo",   "OS · CPU · Memory · Uptime", NEON),
            ("▶", "Realtime Monitor", "realtime",  "Live CPU · RAM · Disk metrics", EMERALD),
            ("◎", "Network",          "network",   "Interfaces · Connections · IPs", CYAN),
            ("⬡", "Security Audit",   "security",  "Processes · Logins · Firewall", DANGER),
            ("⊞", "File Organizer",   "organizer", "Auto-sort files by type", PURPLE),
            ("◉", "Disk Analysis",    "disk",      "Usage · Directories · Types", WARN),
        ]
        for i, (ico, title, tab, desc, col) in enumerate(cards):
            c, r = i % 3, i // 3
            card = tk.Frame(cards_f, bg=BG_CARD,
                            highlightbackground=BORDER, highlightthickness=1,
                            cursor="hand2")
            card.grid(row=r, column=c, padx=5, pady=5, sticky="ew")
            cards_f.columnconfigure(c, weight=1)

            accent = tk.Frame(card, bg=col, height=2)
            accent.pack(fill="x")

            inner = tk.Frame(card, bg=BG_CARD)
            inner.pack(fill="both", padx=14, pady=10)
            tk.Label(inner, text=ico, bg=BG_CARD, fg=col,
                     font=(self._font, 20)).pack(anchor="w")
            tk.Label(inner, text=title, bg=BG_CARD, fg=TEXT,
                     font=(self._font, 10, "bold")).pack(anchor="w", pady=(2, 1))
            tk.Label(inner, text=desc, bg=BG_CARD, fg=TEXT_DIM,
                     font=FT_TINY).pack(anchor="w")

            def bind_card(card, inner, col, tab):
                def enter(_):
                    card.configure(highlightbackground=col)
                    inner.configure(bg=BG_HOVER)
                    for w in inner.winfo_children():
                        try: w.configure(bg=BG_HOVER)
                        except: pass
                def leave(_):
                    card.configure(highlightbackground=BORDER)
                    inner.configure(bg=BG_CARD)
                    for w in inner.winfo_children():
                        try: w.configure(bg=BG_CARD)
                        except: pass
                for w in [card, inner] + list(inner.winfo_children()) + [accent]:
                    w.bind("<Button-1>", lambda e, t=tab: self._show_tab(t))
                    w.bind("<Enter>", enter)
                    w.bind("<Leave>", leave)
            bind_card(card, inner, col, tab)

    def _update_meters(self):
        if not hasattr(self, "_meters"):
            return
        def fetch():
            try:
                cur = get_cpu_stat()
                pt, pi = self._cpu_prev
                ct, ci = cur
                dT, dI = ct - pt, ci - pi
                cpu_p = 0 if dT == 0 else round(100 * (1 - dI / dT), 1)
                self._cpu_prev = cur

                mem = shell("cat /proc/meminfo | grep -E '^(MemTotal|MemAvailable|SwapTotal|SwapFree)'")
                d = {}
                for line in mem.splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        parts = v.strip().split()
                        if parts:
                            d[k.strip()] = int(parts[0])
                mt = d.get("MemTotal", 1)
                ma = d.get("MemAvailable", mt)
                mem_p = round(100 * (1 - ma / mt), 1)
                st = d.get("SwapTotal", 1)
                sf = d.get("SwapFree", st)
                swap_p = round(100 * (1 - sf / st), 1) if st > 0 else 0.0
                disk = shell("df / | tail -1").split()
                disk_p = int(disk[4].replace("%", "")) if len(disk) >= 5 else 0

                def update():
                    try:
                        self._meters.get("CPU")     and self._meters["CPU"].set(cpu_p)
                        self._meters.get("Memory")  and self._meters["Memory"].set(mem_p)
                        self._meters.get("Disk /")  and self._meters["Disk /"].set(disk_p)
                        self._meters.get("Swap")    and self._meters["Swap"].set(swap_p)
                    except Exception:
                        pass
                self.root.after(0, update)
            except Exception:
                pass
        threading.Thread(target=fetch, daemon=True).start()
        self.root.after(5000, self._update_meters)

    # ── REALTIME MONITOR ──────────────────────────────────────

    def _show_realtime(self):
        self._rt_running = True
        f = self._content

        make_section(f, "REAL-TIME MONITOR", bg=BG)

        # Meters row
        meters_row = tk.Frame(f, bg=BG)
        meters_row.pack(fill="x", padx=16, pady=(0, 8))
        self._rt_meters = {}
        for label, color in [("CPU", NEON), ("Memory", EMERALD), ("Disk /", WARN), ("Swap", PURPLE)]:
            mf = tk.Frame(meters_row, bg=BG_CARD,
                          highlightbackground=BORDER, highlightthickness=1)
            mf.pack(side="left", expand=True, fill="both", padx=4)
            m = ArcMeter(mf, label=label, size=130, color=color)
            m.pack(pady=14, padx=14)
            self._rt_meters[label] = m

        # Bars panel
        bars_panel = tk.Frame(f, bg=BG_CARD,
                              highlightbackground=BORDER, highlightthickness=1)
        bars_panel.pack(fill="x", padx=16, pady=(0, 8))
        hdr = tk.Frame(bars_panel, bg=BG_CARD)
        hdr.pack(fill="x", padx=12, pady=(10, 6))
        tk.Label(hdr, text="RESOURCE BARS", bg=BG_CARD, fg=NEON,
                 font=(self._font, 9, "bold")).pack(side="left")
        self._rt_bars = {}
        for label, col in [("CPU", NEON), ("Memory", EMERALD), ("Disk /", WARN),
                            ("Swap", PURPLE), ("Net RX", CYAN), ("Net TX", PINK)]:
            bar = MiniBar(bars_panel, label)
            bar.pack(fill="x", padx=12, pady=3)
            self._rt_bars[label] = bar
        tk.Frame(bars_panel, bg=BG_CARD, height=8).pack()

        # Table
        make_section(f, "METRICS TABLE", bg=BG)
        tbl_f = tk.Frame(f, bg=BG)
        tbl_f.pack(fill="both", expand=True, padx=16, pady=(0, 12))
        self._rt_table = DataTable(tbl_f, ["Metric", "Value", "Status"])
        self._rt_table.pack(fill="both", expand=True)
        self._rt_table.col_width("Metric", 180)
        self._rt_table.col_width("Value", 220)
        self._rt_table.col_width("Status", 120)

        self._rt_update()

    def _rt_update(self):
        if not self._rt_running:
            return
        try:
            if not self._rt_meters.get("CPU"):
                return
            self._rt_meters["CPU"].winfo_exists()
        except Exception:
            return

        def fetch():
            try:
                cur = get_cpu_stat()
                pt, pi = self._cpu_prev
                ct, ci = cur
                dT, dI = ct - pt, ci - pi
                cpu_p = 0 if dT == 0 else round(100 * (1 - dI / dT), 1)
                self._cpu_prev = cur

                mem = shell("cat /proc/meminfo | grep -E '^(MemTotal|MemAvailable|SwapTotal|SwapFree)'")
                d = {}
                for line in mem.splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        parts = v.strip().split()
                        if parts:
                            d[k.strip()] = int(parts[0])
                mt = d.get("MemTotal", 1); ma = d.get("MemAvailable", mt)
                mem_p = round(100 * (1 - ma / mt), 1)
                st = d.get("SwapTotal", 1); sf = d.get("SwapFree", st)
                swap_p = round(100 * (1 - sf / st), 1) if st > 0 else 0.0

                disk = shell("df / | tail -1").split()
                disk_p  = int(disk[4].replace("%", "")) if len(disk) >= 5 else 0
                disk_u  = disk[2] if len(disk) > 2 else "?"
                disk_av = disk[3] if len(disk) > 3 else "?"

                load = shell("cat /proc/loadavg").split()[:3]
                load_str = "  ".join(load) if load else "—"

                procs   = shell("ps -e --no-headers | wc -l").strip()
                threads = shell("ps -eLf --no-headers | wc -l").strip()

                net_rx = shell("cat /proc/net/dev | awk 'NR>2{sum+=$2} END{printf \"%.1f\", sum/1024/1024}'")
                net_tx = shell("cat /proc/net/dev | awk 'NR>2{sum+=$10} END{printf \"%.1f\", sum/1024/1024}'")

                cpu_status  = "CRITICAL" if cpu_p > 85 else "HIGH" if cpu_p > 65 else "NORMAL"
                mem_status  = "CRITICAL" if mem_p > 90 else "HIGH" if mem_p > 75 else "NORMAL"
                disk_status = "CRITICAL" if disk_p > 90 else "WARNING" if disk_p > 80 else "GOOD"

                rows = [
                    ("CPU Usage",        f"{cpu_p}%",                      cpu_status),
                    ("Memory Usage",     f"{mem_p}% ({human_size((mt-ma)*1024)})", mem_status),
                    ("Memory Free",      human_size(ma * 1024),             ""),
                    ("Swap Usage",       f"{swap_p}%",                     ""),
                    ("Disk Usage (/)",   f"{disk_p}% (used {disk_u}K)",    disk_status),
                    ("Disk Free (/)",    f"{disk_av}K",                    ""),
                    ("Load Average",     load_str,                          ""),
                    ("Processes",        procs,                             ""),
                    ("Threads",          threads,                           ""),
                    ("Net RX Total",     f"{net_rx} MB",                   ""),
                    ("Net TX Total",     f"{net_tx} MB",                   ""),
                ]

                def update():
                    try:
                        self._rt_meters["CPU"].set(cpu_p)
                        self._rt_meters["Memory"].set(mem_p)
                        self._rt_meters["Disk /"].set(disk_p)
                        self._rt_meters["Swap"].set(swap_p)
                        for label, val in [("CPU", cpu_p), ("Memory", mem_p),
                                           ("Disk /", disk_p), ("Swap", swap_p)]:
                            self._rt_bars[label].set(val)
                        try:
                            rx_f = float(net_rx or "0")
                            tx_f = float(net_tx or "0")
                            mx   = max(rx_f, tx_f, 1)
                            self._rt_bars["Net RX"].set(min(rx_f / mx * 100, 100), CYAN)
                            self._rt_bars["Net TX"].set(min(tx_f / mx * 100, 100), PINK)
                        except Exception:
                            pass
                        self._rt_table.clear()
                        for row in rows:
                            tag = ("danger" if "CRITICAL" in row[2] else
                                   "warn"   if row[2] in ("HIGH", "WARNING") else
                                   "good"   if row[2] in ("NORMAL", "GOOD") else "")
                            self._rt_table.insert(row, tag)
                    except Exception:
                        pass
                self.root.after(0, update)
            except Exception:
                pass

        threading.Thread(target=fetch, daemon=True).start()
        self.root.after(3000, self._rt_update)

    # ── GENERIC FEATURE RUNNER ────────────────────────────────

    def _run_feature(self, feature_num, title, params=""):
        f = self._content
        hdr = tk.Frame(f, bg=BG2, highlightbackground=BORDER, highlightthickness=1)
        hdr.pack(fill="x", padx=16, pady=(12, 0))
        tk.Label(hdr, text=f"  {title.upper()}", bg=BG2, fg=NEON,
                 font=FT_HEADER).pack(side="left", pady=10)

        btn_f = tk.Frame(hdr, bg=BG2)
        btn_f.pack(side="right", padx=10, pady=8)
        run_btn = tk.Button(btn_f, text="▶  Run Again", bg=NEON, fg=BG,
                             font=(self._font, 9, "bold"), relief="flat",
                             padx=14, pady=4, cursor="hand2")
        run_btn.pack(side="right")

        out = TermOutput(f)
        out.pack(fill="both", expand=True, padx=16, pady=(6, 12))
        run_btn.configure(command=lambda: self._exec_feature(feature_num, params, out))
        self._exec_feature(feature_num, params, out)

    def _exec_feature(self, num, params, out_widget):
        out_widget.clear()
        out_widget.append(f"$ pwsh smartops.ps1 -Feature {num}{params}", "cmd")
        out_widget.append("", "dim")
        self.set_status(f"  ◉ Running feature {num}…", color=WARN)

        def run():
            try:
                result = subprocess.run(
                    ["pwsh", "-File", "smartops.ps1", "-Feature", str(num)]
                    + shlex.split(params),
                    capture_output=True, text=True, timeout=60
                )
                lines = (result.stdout + ("\n" + result.stderr if result.stderr else "")).splitlines()
                self.root.after(0, lambda: [out_widget.append_raw(l) for l in lines]
                                or self.set_status("  ✅ Done.", color=EMERALD))
            except FileNotFoundError:
                self.root.after(0, lambda: self._mock_output(num, out_widget))
                self.root.after(0, lambda: self.set_status(
                    "  ⚠ pwsh not found — simulated output", color=WARN))
            except Exception as e:
                self.root.after(0, lambda: [
                    out_widget.append(f"❌ Error: {e}", "danger"),
                    self.set_status("  ❌ Error.", color=DANGER)
                ])
        threading.Thread(target=run, daemon=True).start()

    def _mock_output(self, feature_num, out):
        def a(t, tag="text"): out.append(t, tag)
        sep = "─" * 54

        if feature_num == 1:
            a(f"╔══ SYSTEM INFORMATION {'═' * 32}╗", "section")
            a(f"  OS       › {shell('lsb_release -d 2>/dev/null | cut -f2') or platform.system()}", "neon")
            a(f"  Kernel   › {shell('uname -r') or '—'}", "neon")
            a(f"  Uptime   › {shell('uptime -p') or '—'}", "neon")
            a(f"  CPU      › {shell('lscpu | grep Model | cut -d: -f2 | xargs') or platform.processor()}", "neon")
            a(f"  Cores    › {shell('nproc') or '?'}")
            mem = shell("free -h | grep '^Mem'").split()
            if mem:
                a(f"  Memory   › Total={mem[1]}  Used={mem[2]}  Free={mem[3]}", "neon")
            a(f"  Disk     › {shell('df -h / | tail -1')}", "neon")
            a(f"  Users    › {shell('who') or '—'}")
            a(f"╚{'═' * 54}╝", "section")

        elif feature_num == 2:
            a(f"╔══ PROCESS MONITOR {'═' * 35}╗", "section")
            a(f"  {'PID':<8} {'PROCESS':<25} {'CPU%':<8} {'MEM%':<8}", "neon")
            a(f"  {sep}", "dim")
            procs = shell_lines("ps -eo pid,comm,%cpu,%mem --sort=-%cpu | head -20")[1:]
            for p in procs:
                a(f"  {p}")

        elif feature_num == 4:
            a(f"╔══ NETWORK INTERFACES {'═' * 31}╗", "section")
            for line in shell_lines("ip -br addr show"):
                tag = "emerald" if "UP" in line else "dim"
                ico = "✅" if "UP" in line else "❌"
                a(f"  {ico} {line}", tag)
            a(f"\n  ── Open Connections ──", "neon")
            for line in shell_lines("ss -tuln | head -20"):
                a(f"  {line}")

        elif feature_num == 5:
            a(f"╔══ BANDWIDTH STATS {'═' * 34}╗", "section")
            ifaces = shell_lines("ip -br link | grep -v LOOPBACK | awk '{print $1}'")
            for iface in ifaces:
                rx = shell(f"cat /sys/class/net/{iface}/statistics/rx_bytes 2>/dev/null")
                tx = shell(f"cat /sys/class/net/{iface}/statistics/tx_bytes 2>/dev/null")
                if rx and tx:
                    a(f"  ▶ {iface}", "neon")
                    a(f"    RX: {human_size(int(rx))}")
                    a(f"    TX: {human_size(int(tx))}")

        elif feature_num == 6:
            a(f"╔══ OPEN PORTS {'═' * 39}╗", "section")
            for line in shell_lines("ss -tuln | grep LISTEN"):
                a(f"  🔌 {line}", "emerald")

        elif feature_num == 7:
            a(f"╔══ SERVICE MANAGER {'═' * 34}╗", "section")
            a("  ▶ Running Services:", "neon")
            for line in shell_lines("systemctl list-units --type=service --state=running 2>/dev/null | head -20"):
                a(f"  ✅ {line}", "emerald")
            a("  ▶ Failed Services:", "neon")
            failed = shell_lines("systemctl --failed 2>/dev/null | grep '^●' | head -10")
            for line in failed:
                a(f"  ❌ {line}", "danger")
            if not failed:
                a("  ✅ No failed services", "emerald")

        elif feature_num == 8:
            a(f"╔══ DISK ANALYSIS {'═' * 36}╗", "section")
            for line in shell_lines("df -h | grep '^/dev'"):
                a(f"  {line}")
            a("  ▶ Top Directories:", "neon")
            for line in shell_lines("du -sh /* 2>/dev/null | sort -rh | head -12"):
                a(f"  📁 {line}")

        elif feature_num == 9:
            a(f"╔══ CLEANUP TOOLS {'═' * 36}╗", "section")
            cache = shell("du -sh /var/cache/apt/archives 2>/dev/null | awk '{print $1}'") or "N/A"
            a(f"  APT Cache:        {cache}", "warn" if cache != "N/A" else "neon")
            old_logs = shell("find /var/log -name '*.log' -mtime +30 2>/dev/null | wc -l") or "0"
            a(f"  Old Logs (>30d):  {old_logs}", "warn" if int(old_logs) > 5 else "neon")
            tmp = shell("du -sh /tmp 2>/dev/null | awk '{print $1}'") or "N/A"
            a(f"  /tmp size:        {tmp}")

        elif feature_num == 10:
            a(f"╔══ SECURITY AUDIT {'═' * 35}╗", "section")
            a("  ▶ Recent Logins:", "neon")
            for line in shell_lines("last -n 10 2>/dev/null"):
                a(f"  {line}")
            a("  ▶ SUID Files:", "warn")
            for line in shell_lines("find /usr/bin /usr/sbin -perm -4000 2>/dev/null | head -10"):
                a(f"  ⚠ {line}", "warn")
            a("  ▶ Open Ports:", "neon")
            for line in shell_lines("ss -tuln | grep LISTEN | head -10"):
                a(f"  🔌 {line}")

        elif feature_num == 11:
            a(f"╔══ PACKAGE UPDATES {'═' * 34}╗", "section")
            a("  Checking upgradable packages…", "neon")
            updates = shell_lines("apt list --upgradable 2>/dev/null | grep -v Listing | head -20")
            if updates:
                for u in updates:
                    a(f"  📦 {u}")
                a(f"\n  Total upgradable: {len(updates)}", "emerald")
            else:
                a("  ✅ System is up to date!", "emerald")

        elif feature_num == 12:
            a(f"╔══ HARDWARE INFO {'═' * 36}╗", "section")
            for line in shell_lines("lscpu | grep -E '^(Model name|Architecture|CPU|Thread|Core|Socket|Virt)'"):
                a(f"  {line}")
            a("  ▶ Memory:", "neon")
            for line in shell_lines("free -h | head -2"):
                a(f"  {line}")
            a("  ▶ Block Devices:", "neon")
            for line in shell_lines("lsblk | grep -v loop | head -15"):
                a(f"  💾 {line}")
            a("  ▶ GPU:", "neon")
            for line in shell_lines("lspci | grep -i vga"):
                a(f"  🖥️  {line}")

        elif feature_num == 22:
            a(f"╔══ STORAGE DEVICES {'═' * 34}╗", "section")
            for line in shell_lines("lsblk -o NAME,SIZE,TYPE,MOUNTPOINT,FSTYPE | grep -v loop"):
                a(f"  💾 {line}")

    # ── FILE MANAGER ──────────────────────────────────────────

    def _show_files(self):
        f = self._content
        cwd   = [Path.home()]
        hist  = [Path.home()]
        hist_pos = [0]

        # Toolbar
        tb = tk.Frame(f, bg=BG2, highlightbackground=BORDER, highlightthickness=1)
        tb.pack(fill="x", padx=16, pady=(12, 0))

        nav_f = tk.Frame(tb, bg=BG2)
        nav_f.pack(side="left", padx=8, pady=6)
        path_var = tk.StringVar(value=str(Path.home()))

        def load(path):
            path = Path(path)
            if not path.is_dir():
                messagebox.showerror("Error", f"Not a directory:\n{path}")
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
            if hist_pos[0] < len(hist) - 1:
                hist_pos[0] += 1
                load(hist[hist_pos[0]])
        def go_up():
            p = cwd[0].parent
            if p != cwd[0]:
                hist.append(p); hist_pos[0] = len(hist) - 1
                load(p)

        for icon, tip, cmd in [("←","Back",go_back),("→","Fwd",go_fwd),
                                ("⌂","Home",lambda: load(Path.home())),
                                ("↑","Up",go_up),
                                ("⟳","Refresh",lambda: load(cwd[0]))]:
            b = tk.Button(nav_f, text=icon, bg=BG2, fg=NEON,
                           font=(self._font, 11), relief="flat", cursor="hand2",
                           command=cmd, padx=8, pady=2,
                           activebackground=BG_HOVER, activeforeground=NEON)
            b.pack(side="left", padx=2)
            Tooltip(b, tip)

        pf = tk.Frame(tb, bg=BG3, highlightbackground=BORDER2, highlightthickness=1)
        pf.pack(side="left", fill="x", expand=True, padx=8, pady=8)
        pe = tk.Entry(pf, textvariable=path_var, bg=BG3, fg=TEXT,
                      font=FT_MONO, insertbackground=NEON, relief="flat", bd=6)
        pe.pack(fill="x")
        pe.bind("<Return>", lambda _: load(path_var.get()))

        sf = tk.Frame(tb, bg=BG3, highlightbackground=BORDER2, highlightthickness=1)
        sf.pack(side="right", padx=8, pady=8)
        tk.Label(sf, text="⌕", bg=BG3, fg=TEXT_DIM, font=(self._font, 11)).pack(
            side="left", padx=(6, 2))
        search_var = tk.StringVar()
        sk = tk.Entry(sf, textvariable=search_var, bg=BG3, fg=TEXT,
                      font=FT_MONO, insertbackground=NEON, relief="flat", bd=4, width=16)
        sk.pack(side="left")

        # Breadcrumb
        bread_f = tk.Frame(f, bg=BG1)
        bread_f.pack(fill="x", padx=16, pady=2)

        def update_bread():
            for w in bread_f.winfo_children():
                w.destroy()
            parts = list(cwd[0].parts)
            for i, part in enumerate(parts):
                p = Path(*parts[:i + 1])
                is_last = i == len(parts) - 1
                lbl = tk.Label(bread_f, text=part or "/", bg=BG1,
                               fg=NEON if is_last else TEXT_DIM,
                               font=(self._font, 8, "bold" if is_last else ""),
                               cursor="hand2")
                lbl.pack(side="left")
                lbl.bind("<Button-1>", lambda e, p_=p: load(p_))
                if not is_last:
                    tk.Label(bread_f, text=" › ", bg=BG1, fg=DIM,
                             font=FT_TINY).pack(side="left")

        # Action bar
        ab = tk.Frame(f, bg=BG1)
        ab.pack(fill="x", padx=16, pady=4)
        for label, icon, cmd_fn, color in [
            ("New Folder", "📁", lambda: new_folder(), NEON),
            ("Copy",       "⎘",  lambda: copy_sel(),   EMERALD),
            ("Move",       "✂",  lambda: move_sel(),   WARN),
            ("Delete",     "🗑", lambda: del_sel(),    DANGER),
            ("Select All", "☑",  lambda: sel_all(),    TEXT_DIM),
        ]:
            btn = tk.Button(ab, text=f"{icon}  {label}", bg=BG_CARD, fg=color,
                             font=(self._font, 8), relief="flat", cursor="hand2",
                             command=cmd_fn, padx=10, pady=4,
                             activebackground=BG_HOVER, activeforeground=color)
            btn.pack(side="left", padx=3)

        # Table
        tbl = DataTable(f, ["Type", "Name", "Size", "Modified", "Permissions"])
        tbl.pack(fill="both", expand=True, padx=16, pady=(4, 4))
        tbl.col_width("Type", 70)
        tbl.col_width("Name", 320)
        tbl.col_width("Size", 100)
        tbl.col_width("Modified", 160)
        tbl.col_width("Permissions", 110)

        def on_double(e):
            sel = tbl._tree.selection()
            if not sel:
                return
            vals = tbl._tree.item(sel[0])["values"]
            if vals[0] == "📁 DIR":
                p = cwd[0] / vals[1]
                hist.append(p); hist_pos[0] = len(hist) - 1
                load(p)
            else:
                try:
                    subprocess.Popen(["xdg-open", str(cwd[0] / vals[1])],
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except Exception:
                    pass
        tbl._tree.bind("<Double-1>", on_double)

        # Status
        file_status = tk.Label(f, text="", bg=BG1, fg=TEXT_DIM, font=FT_TINY, anchor="w")
        file_status.pack(fill="x", padx=16, pady=(0, 8))

        def refresh():
            tbl.clear()
            try:
                items = []
                for entry in os.scandir(cwd[0]):
                    try:
                        st = entry.stat(follow_symlinks=False)
                        items.append({
                            "name":  entry.name,
                            "isdir": entry.is_dir(follow_symlinks=False),
                            "size":  st.st_size,
                            "mtime": st.st_mtime,
                            "mode":  st.st_mode,
                        })
                    except Exception:
                        items.append({"name": entry.name, "isdir": False,
                                      "size": 0, "mtime": 0, "mode": 0})

                items.sort(key=lambda x: (0 if x["isdir"] else 1, x["name"].lower()))
                q = search_var.get().lower()
                if q:
                    items = [i for i in items if q in i["name"].lower()]

                for item in items:
                    typ = "📁 DIR" if item["isdir"] else "📄 FILE"
                    sz  = "—" if item["isdir"] else human_size(item["size"])
                    mt  = datetime.fromtimestamp(item["mtime"]).strftime("%Y-%m-%d  %H:%M") if item["mtime"] else "—"
                    pm  = stat.filemode(item["mode"]) if item["mode"] else "—"
                    tbl.insert((typ, item["name"], sz, mt, pm))

                file_status.configure(text=f"  {len(items)} items  ·  {cwd[0]}")
            except PermissionError:
                file_status.configure(text="  ⚠ Permission denied", fg=WARN)

        search_var.trace("w", lambda *_: refresh())

        def _get_sel():
            sel = tbl._tree.selection()
            return [cwd[0] / tbl._tree.item(s)["values"][1] for s in sel] if sel else []

        def sel_all():
            tbl._tree.selection_set(tbl._tree.get_children())

        def new_folder():
            d = tk.Toplevel(f)
            d.configure(bg=BG_CARD); d.title("New Folder"); d.geometry("360x140")
            d.resizable(False, False)
            tk.Frame(d, bg=NEON, height=2).pack(fill="x")
            tk.Label(d, text="Create New Folder", bg=BG_CARD, fg=TEXT,
                     font=(self._font, 10, "bold")).pack(padx=20, pady=(16, 6), anchor="w")
            var = tk.StringVar()
            e = tk.Entry(d, textvariable=var, bg=BG3, fg=TEXT, font=FT_MONO,
                         insertbackground=NEON, relief="flat", bd=8)
            e.pack(fill="x", padx=20); e.focus()
            def create():
                name = var.get().strip()
                if name:
                    try: (cwd[0] / name).mkdir(parents=False, exist_ok=False)
                    except Exception as ex: messagebox.showerror("Error", str(ex))
                d.destroy(); refresh()
            tk.Button(d, text="Create Folder", command=create, bg=NEON, fg=BG,
                      font=(self._font, 9, "bold"), relief="flat", pady=6).pack(
                fill="x", padx=20, pady=12)
            e.bind("<Return>", lambda _: create())

        def copy_sel():
            paths = _get_sel()
            if not paths: messagebox.showinfo("Copy", "Select items first"); return
            dest = filedialog.askdirectory(title="Copy To", initialdir=str(cwd[0]))
            if dest:
                for src in paths:
                    subprocess.run(f"cp -r '{src}' '{dest}'", shell=True)
                refresh()

        def move_sel():
            paths = _get_sel()
            if not paths: messagebox.showinfo("Move", "Select items first"); return
            dest = filedialog.askdirectory(title="Move To", initialdir=str(cwd[0]))
            if dest:
                for src in paths:
                    subprocess.run(f"mv -n '{src}' '{dest}'", shell=True)
                refresh()

        def del_sel():
            paths = _get_sel()
            if not paths: messagebox.showinfo("Delete", "Select items first"); return
            if messagebox.askyesno("Confirm Delete",
                                   f"Permanently delete {len(paths)} item(s)?"):
                for p in paths:
                    subprocess.run(f"rm -rf '{p}'", shell=True)
                refresh()

        update_bread()
        refresh()

    # ── FILE SEARCH ───────────────────────────────────────────

    def _show_search(self):
        f = self._content
        make_section(f, "FILE SEARCH", bg=BG)

        ctrl = tk.Frame(f, bg=BG_CARD, highlightbackground=BORDER, highlightthickness=1)
        ctrl.pack(fill="x", padx=16, pady=(0, 8))
        tk.Frame(ctrl, bg=NEON, height=2).pack(fill="x")

        pat_var = tk.StringVar()
        dir_var = tk.StringVar(value=str(Path.home()))

        for label, var, do_browse in [("Pattern", pat_var, False), ("Directory", dir_var, True)]:
            row = tk.Frame(ctrl, bg=BG_CARD)
            row.pack(fill="x", padx=14, pady=8)
            tk.Label(row, text=label, bg=BG_CARD, fg=TEXT_DIM,
                     font=FT_SMALL, width=10, anchor="w").pack(side="left")
            tk.Entry(row, textvariable=var, bg=BG3, fg=TEXT,
                     font=FT_MONO, insertbackground=NEON, relief="flat", bd=6).pack(
                side="left", fill="x", expand=True, padx=(8, 0))
            if do_browse:
                tk.Button(row, text="Browse", bg=BG3, fg=NEON,
                          font=FT_SMALL, relief="flat", cursor="hand2",
                          command=lambda: dir_var.set(
                              filedialog.askdirectory(initialdir=dir_var.get()) or dir_var.get()
                          )).pack(side="right", padx=6)

        btn_row = tk.Frame(ctrl, bg=BG_CARD)
        btn_row.pack(fill="x", padx=14, pady=(0, 12))
        tk.Button(btn_row, text="▶  Search", command=lambda: run_search(),
                  bg=NEON, fg=BG, font=(self._font, 9, "bold"),
                  relief="flat", padx=16, pady=5, cursor="hand2").pack(side="right")

        tbl = DataTable(f, ["Path", "Size", "Modified"])
        tbl.pack(fill="both", expand=True, padx=16, pady=(0, 4))
        tbl.col_width("Path", 520)
        tbl.col_width("Size", 100)
        tbl.col_width("Modified", 160)

        status_lbl = tk.Label(f, text="", bg=BG, fg=TEXT_DIM, font=FT_TINY, anchor="w")
        status_lbl.pack(fill="x", padx=16, pady=(0, 8))

        def run_search():
            pat = pat_var.get().strip()
            d   = dir_var.get().strip() or "."
            if not pat:
                messagebox.showinfo("Search", "Enter a search pattern")
                return
            tbl.clear()
            status_lbl.configure(text="  Searching…")
            self.set_status("  Searching…", color=WARN)

            def search():
                results = []
                try:
                    for root_d, dirs, files in os.walk(d):
                        dirs[:] = [dd for dd in dirs if not dd.startswith(".")]
                        for fname in files:
                            if pat.lower() in fname.lower():
                                fp = Path(root_d) / fname
                                try:
                                    st = fp.stat()
                                    results.append((str(fp), human_size(st.st_size),
                                                    datetime.fromtimestamp(st.st_mtime).strftime(
                                                        "%Y-%m-%d  %H:%M")))
                                except Exception:
                                    results.append((str(fp), "—", "—"))
                        if len(results) >= 300:
                            break
                except Exception as e:
                    self.root.after(0, lambda: status_lbl.configure(text=f"  ❌ {e}"))
                    return

                def update():
                    for r in results[:300]:
                        tbl.insert(r)
                    status_lbl.configure(text=f"  ✅ Found {len(results)} matches")
                    self.set_status(f"  ✅ Found {len(results)} matches", color=EMERALD)
                self.root.after(0, update)

            threading.Thread(target=search, daemon=True).start()

    # ── FILE ORGANIZER ────────────────────────────────────────

    def _show_organizer(self):
        f = self._content
        make_section(f, "AUTOMATED FILE ORGANIZER", bg=BG)
        tk.Label(f, text="  Sorts files by extension → Images · Documents · Videos · Music · Archives",
                 bg=BG, fg=TEXT_DIM, font=FT_TINY).pack(anchor="w", padx=16, pady=(0, 8))

        ctrl = tk.Frame(f, bg=BG_CARD, highlightbackground=BORDER, highlightthickness=1)
        ctrl.pack(fill="x", padx=16, pady=(0, 8))
        tk.Frame(ctrl, bg=EMERALD, height=2).pack(fill="x")

        row = tk.Frame(ctrl, bg=BG_CARD)
        row.pack(fill="x", padx=14, pady=12)
        tk.Label(row, text="Directory", bg=BG_CARD, fg=TEXT_DIM,
                 font=FT_SMALL, width=10, anchor="w").pack(side="left")
        dir_var = tk.StringVar(value=str(Path.home() / "Downloads"))
        tk.Entry(row, textvariable=dir_var, bg=BG3, fg=TEXT, font=FT_MONO,
                 insertbackground=NEON, relief="flat", bd=6).pack(
            side="left", fill="x", expand=True, padx=(8, 0))
        tk.Button(row, text="Browse", bg=BG3, fg=NEON, font=FT_SMALL, relief="flat",
                  cursor="hand2",
                  command=lambda: dir_var.set(
                      filedialog.askdirectory(initialdir=dir_var.get()) or dir_var.get()
                  )).pack(side="right", padx=6)

        dry_var = tk.BooleanVar(value=True)
        dr = tk.Frame(ctrl, bg=BG_CARD)
        dr.pack(fill="x", padx=14, pady=(0, 8))
        tk.Checkbutton(dr, text="  Dry Run (preview only — no files moved)",
                       variable=dry_var, bg=BG_CARD, fg=WARN,
                       selectcolor=BG3, activebackground=BG_CARD,
                       font=FT_SMALL).pack(side="left")

        btn_row = tk.Frame(ctrl, bg=BG_CARD)
        btn_row.pack(fill="x", padx=14, pady=(0, 12))
        tk.Button(btn_row, text="▶  Organize Now", command=lambda: run(),
                  bg=EMERALD, fg=BG, font=(self._font, 9, "bold"),
                  relief="flat", padx=14, pady=5, cursor="hand2").pack(side="right")

        # Summary cards
        summary_f = tk.Frame(f, bg=BG)
        summary_f.pack(fill="x", padx=16, pady=(0, 8))
        self._org_cnts = {}
        for folder, icon, color in [
            ("Images", "🖼️", CYAN), ("Documents", "📄", NEON),
            ("Videos", "🎬", PURPLE), ("Music", "🎵", EMERALD),
            ("Archives", "📦", WARN), ("Other", "⏭", TEXT_DIM),
        ]:
            sf2 = tk.Frame(summary_f, bg=BG_CARD,
                           highlightbackground=BORDER, highlightthickness=1)
            sf2.pack(side="left", expand=True, fill="both", padx=3)
            tk.Frame(sf2, bg=color, height=2).pack(fill="x")
            tk.Label(sf2, text=icon, bg=BG_CARD, fg=color,
                     font=(self._font, 16)).pack(pady=(8, 2))
            tk.Label(sf2, text=folder, bg=BG_CARD, fg=TEXT_DIM, font=FT_TINY).pack()
            cnt = tk.Label(sf2, text="0", bg=BG_CARD, fg=color,
                           font=(self._font, 18, "bold"))
            cnt.pack(pady=(0, 8))
            self._org_cnts[folder] = cnt

        out = TermOutput(f)
        out.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        CATEGORIES = {
            "Images":    ["jpg","jpeg","png","gif","svg","webp","bmp","ico","tiff","raw","heic"],
            "Documents": ["pdf","doc","docx","txt","ppt","pptx","xls","xlsx","odt","rtf","md","csv","epub"],
            "Videos":    ["mp4","mkv","mov","avi","webm","flv","wmv","ts","m4v"],
            "Music":     ["mp3","wav","flac","aac","ogg","m4a","wma","opus"],
            "Archives":  ["zip","rar","tar","gz","7z","bz2","xz","deb","rpm"],
        }
        ext_map = {e: cat for cat, exts in CATEGORIES.items() for e in exts}

        def run():
            d = dir_var.get().strip()
            if not d or not Path(d).is_dir():
                messagebox.showerror("Error", "Invalid directory")
                return
            dry = dry_var.get()
            out.clear()
            if dry:
                out.append("  ⚠ DRY RUN — no files will be moved", "warn")
            out.append(f"  ▶ Organizing: {d}", "neon")
            out.append("", "dim")

            def organize():
                counts = {k: 0 for k in list(CATEGORIES.keys()) + ["Other"]}
                base = Path(d)
                if not dry:
                    for cat in CATEGORIES:
                        (base / cat).mkdir(exist_ok=True)

                for item in base.iterdir():
                    if item.is_dir(): continue
                    ext = item.suffix.lstrip(".").lower()
                    cat = ext_map.get(ext)
                    if not cat:
                        counts["Other"] += 1
                        self.root.after(0, lambda n=item.name: out.append(
                            f"  [OTHER    ] {n}", "dim"))
                        continue
                    color_map = {"Images":"neon","Documents":"neon","Videos":"purple",
                                 "Music":"emerald","Archives":"warn"}
                    counts[cat] += 1
                    self.root.after(0, lambda n=item.name, c=cat, tg=color_map.get(cat,"text"):
                        out.append(f"  [{c.upper():<10}] {n}  →  {c}/", tg))
                    if not dry:
                        try:
                            item.rename(base / cat / item.name)
                        except Exception as e:
                            self.root.after(0, lambda err=e: out.append(f"    ❌ {err}", "danger"))

                def finish():
                    out.append("", "dim")
                    out.append("  ══════════ SUMMARY ══════════", "section")
                    for k, v in counts.items():
                        out.append(f"  {k:<14} {v:>4} file(s)",
                                   "emerald" if v > 0 else "dim")
                    out.append("", "dim")
                    out.append(
                        "  ✅ Complete!" if not dry else "  ✅ Dry run complete — review above",
                        "emerald")
                    for k, lbl in self._org_cnts.items():
                        lbl.configure(text=str(counts.get(k, 0)))
                    self.set_status("  ✅ Organization complete", color=EMERALD)
                self.root.after(100, finish)

            threading.Thread(target=organize, daemon=True).start()
            self.set_status("  Organizing…", color=WARN)

    # ── BOOTABLE CREATOR ──────────────────────────────────────

    def _show_bootable(self):
        f = self._content
        make_section(f, "BOOTABLE DRIVE CREATOR", bg=BG)

        warn_banner = tk.Frame(f, bg=DANGER_DIM, highlightbackground=DANGER,
                               highlightthickness=1)
        warn_banner.pack(fill="x", padx=16, pady=(0, 8))
        tk.Label(warn_banner,
                 text="  ⚠  WARNING: This will DESTROY ALL DATA on the target device!",
                 bg=DANGER_DIM, fg=DANGER,
                 font=(self._font, 9, "bold")).pack(anchor="w", padx=12, pady=8)

        ctrl = tk.Frame(f, bg=BG_CARD, highlightbackground=BORDER, highlightthickness=1)
        ctrl.pack(fill="x", padx=16, pady=(0, 8))
        tk.Frame(ctrl, bg=DANGER, height=2).pack(fill="x")

        dev_var = tk.StringVar(value="/dev/sdb")
        iso_var = tk.StringVar()

        for label, var, do_browse in [("Target Device", dev_var, False), ("ISO File", iso_var, True)]:
            row = tk.Frame(ctrl, bg=BG_CARD)
            row.pack(fill="x", padx=14, pady=8)
            tk.Label(row, text=label, bg=BG_CARD, fg=TEXT_DIM,
                     font=FT_SMALL, width=14, anchor="w").pack(side="left")
            tk.Entry(row, textvariable=var, bg=BG3, fg=TEXT, font=FT_MONO,
                     insertbackground=NEON, relief="flat", bd=6).pack(
                side="left", fill="x", expand=True, padx=(8, 0))
            if do_browse:
                tk.Button(row, text="Browse", bg=BG3, fg=NEON, font=FT_SMALL,
                          relief="flat", cursor="hand2",
                          command=lambda: iso_var.set(
                              filedialog.askopenfilename(
                                  filetypes=[("ISO Files", "*.iso"), ("All", "*.*")]
                              ) or iso_var.get()
                          )).pack(side="right", padx=6)

        btn_row = tk.Frame(ctrl, bg=BG_CARD)
        btn_row.pack(fill="x", padx=14, pady=(0, 12))
        tk.Button(btn_row, text="List Devices", bg=BG3, fg=NEON,
                  font=FT_SMALL, relief="flat", cursor="hand2",
                  command=lambda: self._exec_feature(22, "", out)
                  ).pack(side="right", padx=(0, 8))
        tk.Button(btn_row, text="🚀  Create Bootable USB", command=lambda: run(),
                  bg=DANGER, fg="white", font=(self._font, 9, "bold"),
                  relief="flat", padx=14, pady=7, cursor="hand2").pack(side="right")

        out = TermOutput(f)
        out.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        def run():
            dev = dev_var.get().strip(); iso = iso_var.get().strip()
            if not dev or not iso:
                messagebox.showwarning("Missing", "Set both device and ISO path"); return
            if not messagebox.askyesno("⚠ CONFIRM — DATA DESTRUCTION",
                f"Write:\n  {iso}\n\nTo device:\n  {dev}\n\nALL DATA ON {dev} WILL BE PERMANENTLY ERASED!\n\nAre you sure?"):
                return
            out.clear()
            out.append(f"  ⚠️  Destroying {dev}…", "danger")
            out.append(f"  📀 ISO: {iso}", "neon")

            def run_cmd():
                try:
                    result = subprocess.run(
                        f"pwsh smartops.ps1 -Feature 21 -Device '{dev}' -IsoPath '{iso}'",
                        shell=True, capture_output=True, text=True, timeout=600)
                    lines = (result.stdout + result.stderr).splitlines()
                    self.root.after(0, lambda: [out.append_raw(l) for l in lines])
                except FileNotFoundError:
                    self.root.after(0, lambda: out.append(
                        f"  pwsh not found. Native equivalent:\n"
                        f"  sudo dd if=\"{iso}\" of=\"{dev}\" bs=4M status=progress", "warn"))
                except Exception as e:
                    self.root.after(0, lambda: out.append(f"  ❌ {e}", "danger"))
            threading.Thread(target=run_cmd, daemon=True).start()

    # ── FORMAT DRIVE ──────────────────────────────────────────

    def _show_format(self):
        f = self._content
        make_section(f, "STORAGE FORMAT", bg=BG)

        warn_banner = tk.Frame(f, bg=WARN_DIM, highlightbackground=WARN,
                               highlightthickness=1)
        warn_banner.pack(fill="x", padx=16, pady=(0, 8))
        tk.Label(warn_banner,
                 text="  ⚠  WARNING: This will ERASE all data on the selected partition!",
                 bg=WARN_DIM, fg=WARN,
                 font=(self._font, 9, "bold")).pack(anchor="w", padx=12, pady=8)

        ctrl = tk.Frame(f, bg=BG_CARD, highlightbackground=BORDER, highlightthickness=1)
        ctrl.pack(fill="x", padx=16, pady=(0, 8))
        tk.Frame(ctrl, bg=WARN, height=2).pack(fill="x")

        dev_var = tk.StringVar(value="/dev/sdb1")
        fs_var  = tk.StringVar(value="ext4")
        lbl_var = tk.StringVar()

        for label, var, widget_fn in [
            ("Device",      dev_var, lambda r: tk.Entry(r, textvariable=dev_var, bg=BG3, fg=TEXT,
                                                        font=FT_MONO, insertbackground=NEON,
                                                        relief="flat", bd=6)),
            ("Filesystem",  fs_var,  None),
            ("Label (opt)", lbl_var, lambda r: tk.Entry(r, textvariable=lbl_var, bg=BG3, fg=TEXT,
                                                         font=FT_MONO, insertbackground=NEON,
                                                         relief="flat", bd=6)),
        ]:
            row = tk.Frame(ctrl, bg=BG_CARD)
            row.pack(fill="x", padx=14, pady=8)
            tk.Label(row, text=label, bg=BG_CARD, fg=TEXT_DIM,
                     font=FT_SMALL, width=12, anchor="w").pack(side="left")
            if widget_fn:
                widget_fn(row).pack(side="left", fill="x", expand=True, padx=(8, 0))
            else:
                style = ttk.Style()
                style.configure("Dark.TCombobox",
                    fieldbackground=BG3, background=BG3, foreground=TEXT,
                    selectbackground=BG_ACTIVE, selectforeground=NEON)
                cb = ttk.Combobox(row, textvariable=fs_var,
                                  values=["ext4", "ntfs", "fat32", "exfat", "btrfs"],
                                  state="readonly", width=14, style="Dark.TCombobox")
                cb.pack(side="left", padx=(8, 0))

        btn_row = tk.Frame(ctrl, bg=BG_CARD)
        btn_row.pack(fill="x", padx=14, pady=(0, 12))
        tk.Button(btn_row, text="List Devices", bg=BG3, fg=NEON,
                  font=FT_SMALL, relief="flat", cursor="hand2",
                  command=lambda: self._exec_feature(22, "", out)
                  ).pack(side="right", padx=(0, 8))
        tk.Button(btn_row, text="⚡  Format Device", command=lambda: run(),
                  bg=WARN, fg=BG, font=(self._font, 9, "bold"),
                  relief="flat", padx=14, pady=7, cursor="hand2").pack(side="right")

        out = TermOutput(f)
        out.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        def run():
            dev = dev_var.get().strip(); fs = fs_var.get(); lbl = lbl_var.get().strip()
            if not dev:
                messagebox.showwarning("Missing", "Set device path"); return
            if not messagebox.askyesno("⚠ CONFIRM FORMAT",
                f"Format {dev} as {fs}?\nALL DATA WILL BE ERASED!"):
                return
            out.clear()
            out.append(f"  ⚠️  Formatting {dev} as {fs}…", "warn")
            args = f" -Device '{dev}' -Filesystem '{fs}'"
            if lbl: args += f" -Label '{lbl}'"
            def run_cmd():
                try:
                    result = subprocess.run(
                        f"pwsh smartops.ps1 -Feature 23{args}",
                        shell=True, capture_output=True, text=True, timeout=120)
                    lines = (result.stdout + result.stderr).splitlines()
                    self.root.after(0, lambda: [out.append_raw(l) for l in lines])
                except FileNotFoundError:
                    native = (f"sudo umount {dev} 2>/dev/null; "
                              f"sudo mkfs.{fs} "
                              f"{'-F ' if fs in ('ext4','ntfs') else ''}"
                              f"{'-L '+lbl+' ' if lbl else ''}{dev}")
                    self.root.after(0, lambda: out.append(
                        f"  pwsh not found.\n  Native:\n  {native}", "warn"))
                except Exception as e:
                    self.root.after(0, lambda: out.append(f"  ❌ {e}", "danger"))
            threading.Thread(target=run_cmd, daemon=True).start()

    # ── COMMAND INPUT ─────────────────────────────────────────

    def _handle_cmd(self, _):
        val = self._cmd.get().strip()
        if not val: return
        self._history.insert(0, val)
        self._hist_idx = -1
        self._cmd.delete(0, "end")

        tab_map = {
            "1": "sysinfo", "2": "process", "3": "realtime", "4": "network",
            "5": "bandwidth", "6": "ports", "7": "services", "8": "disk",
            "9": "cleanup", "10": "security", "11": "updates", "12": "hardware",
            "13": "files", "16": "search", "17": "organizer",
        }
        if val in tab_map:
            self._show_tab(tab_map[val])
        elif val in ("help", "?", "h"):
            self._show_tab("overview")
        elif val in ("clear", "cls", "c"):
            self._clear_content()
        elif val.startswith("cd "):
            try:
                p = Path(val[3:].strip()).expanduser()
                if p.is_dir():
                    os.chdir(p)
                    self.set_status(f"  cd → {p}", color=EMERALD)
                else:
                    self.set_status(f"  ❌ Not a directory: {p}", color=DANGER)
            except Exception as e:
                self.set_status(f"  ❌ {e}", color=DANGER)
        else:
            self._clear_content()
            out = TermOutput(self._content)
            out.pack(fill="both", expand=True, padx=16, pady=12)
            out.append(f"$ {val}", "cmd")
            self.set_status(f"  Running: {val[:40]}…", color=WARN)
            def run():
                result = subprocess.run(val, shell=True, capture_output=True,
                                        text=True, timeout=30)
                lines = (result.stdout + result.stderr).splitlines()
                self.root.after(0, lambda: [
                    out.append_raw(l) for l in (lines or ["(no output)"])
                ])
                self.root.after(0, lambda: self.set_status("  ✅ Done", color=EMERALD))
            threading.Thread(target=run, daemon=True).start()

    def _hist_up(self, _):
        if self._history:
            self._hist_idx = min(self._hist_idx + 1, len(self._history) - 1)
            self._cmd.delete(0, "end")
            self._cmd.insert(0, self._history[self._hist_idx])

    def _hist_dn(self, _):
        self._hist_idx = max(self._hist_idx - 1, -1)
        self._cmd.delete(0, "end")
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
        style.configure("TScrollbar",
            background=BG1, troughcolor=BG,
            bordercolor=BG, arrowcolor=TEXT_DIM, relief="flat")
        style.configure("TCombobox",
            fieldbackground=BG3, background=BG3, foreground=TEXT,
            selectbackground=BG_ACTIVE, selectforeground=NEON,
            arrowcolor=NEON)
        style.map("TCombobox",
            fieldbackground=[("readonly", BG3)],
            selectbackground=[("readonly", BG_ACTIVE)])
    except Exception:
        pass

    app = SmartOpsPro(root)
    root.mainloop()


if __name__ == "__main__":
    main()