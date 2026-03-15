# ── ui/widgets.py ─────────────────────────────────────────────────────────────
"""Widget e helper grafici condivisi tra tutti i tab."""

import tkinter as tk
from tkinter import ttk
from config import C
from i18n import t

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
    HAS_MPL = True
except ImportError:
    HAS_MPL = False


# ── Fonts ──────────────────────────────────────────────────────────
FONT = {
    "title":    ("Courier", 18, "bold"),    # titles tabs sections
    "section":  ("Courier", 10, "bold"),    # group labels, section headers
    "body":     ("Courier", 10),            # current text
    "caption":  ("Courier", 8),             # notes, tooltip
    "metric":   ("Courier", 26, "bold"),    # big numbers in stat cards
    "label":    ("Courier", 9, "bold"),     # uppercase labels in stat cards, buttons
    "mono_sm":  ("Courier", 8, "bold"),     # monospace small, used in coach tab for code snippets
}


class Tooltip:
    """Simple tooltip that appears after 500 ms of hover."""
    _delay_ms = 500

    def __init__(self, widget, text: str):
        self._widget = widget
        self._text   = text
        self._job    = None
        self._win    = None
        widget.bind("<Enter>",    self._schedule, add="+")
        widget.bind("<Leave>",    self._cancel,   add="+")
        widget.bind("<Button>",   self._cancel,   add="+")

    def _schedule(self, event=None):
        self._cancel()
        self._job = self._widget.after(self._delay_ms, self._show)

    def _cancel(self, event=None):
        if self._job:
            self._widget.after_cancel(self._job)
            self._job = None
        if self._win:
            self._win.destroy()
            self._win = None

    def _show(self):
        x = self._widget.winfo_rootx() + 10
        y = self._widget.winfo_rooty() + self._widget.winfo_height() + 4
        self._win = tw = tk.Toplevel(self._widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tk.Label(tw, text=self._text,
                 font=FONT["caption"], fg=C["text"], bg=C["surface2"],
                 relief="flat", bd=0, padx=10, pady=5,
                 highlightthickness=1, highlightbackground=C["border"]
                 ).pack()


class StatCard(tk.Frame):
    def __init__(self, parent, label, value, unit="", color=None, stripe=None, **kw):
        """
        stripe: Optional hex color for the colored left border (4px).
                If None, no colored side border.
        """
        super().__init__(parent, bg=C["surface2"], bd=0,
                         highlightthickness=1, highlightbackground=C["border"], **kw)
        color = color or C["text"]

        # Left colored stripe (4px)
        if stripe:
            tk.Frame(self, bg=stripe, width=4).pack(side="left", fill="y")

        # Content
        inner = tk.Frame(self, bg=C["surface2"])
        inner.pack(side="left", fill="both", expand=True,
                   padx=(10 if stripe else 18, 14), pady=14)

        tk.Label(inner, text=label.upper(), font=FONT["label"],
                 fg=C["text_dim"], bg=C["surface2"]).pack(anchor="w")
        vf = tk.Frame(inner, bg=C["surface2"])
        vf.pack(anchor="w", pady=(4, 0))
        tk.Label(vf, text=str(value), font=FONT["metric"],
                 fg=color, bg=C["surface2"]).pack(side="left")
        if unit:
            tk.Label(vf, text=f" {unit}", font=FONT["body"],
                     fg=C["text_dim"], bg=C["surface2"]).pack(side="left", pady=(10, 0))


def make_scrollable(parent):
    """Returns (canvas, inner_frame) with a vertical scrollbar."""
    c = tk.Canvas(parent, bg=C["bg"], bd=0, highlightthickness=0)
    sb = ttk.Scrollbar(parent, orient="vertical", command=c.yview)
    c.configure(yscrollcommand=sb.set)
    sb.pack(side="right", fill="y")
    c.pack(fill="both", expand=True)
    inner = tk.Frame(c, bg=C["bg"])
    wid   = c.create_window((0, 0), window=inner, anchor="nw")
    inner.bind("<Configure>", lambda e: c.configure(scrollregion=c.bbox("all")))
    c.bind("<Configure>", lambda e: c.itemconfig(wid, width=e.width))
    c.bind_all("<MouseWheel>",
               lambda e: c.yview_scroll(int(-1 * (e.delta / 120)), "units"))
    return c, inner


def embed_mpl(parent, fig):
    """Includes matplotlib figure in frame tkinter with toolbar."""
    cf = tk.Frame(parent, bg=C["bg"])
    cf.pack(fill="both", expand=True)
    cnv = FigureCanvasTkAgg(fig, master=cf)
    cnv.draw()
    cnv.get_tk_widget().pack(fill="both", expand=True)
    tf = tk.Frame(parent, bg=C["surface"])
    tf.pack(fill="x")
    NavigationToolbar2Tk(cnv, tf)
    return cnv


def style_ax(ax, title):
    ax.set_facecolor(C["surface"])
    ax.set_title(title, color=C["text"], fontsize=8.5, fontweight="bold",
                 fontfamily="monospace", pad=7)
    ax.tick_params(colors=C["text_dim"], labelsize=7)
    for sp in ax.spines.values():
        sp.set_edgecolor(C["border"])
    ax.xaxis.label.set_color(C["text_dim"])
    ax.yaxis.label.set_color(C["text_dim"])
    ax.grid(color=C["border"], linestyle="--", linewidth=0.4, alpha=0.6)


def section_label(parent, text):
    f = tk.Frame(parent, bg=C["bg"])
    f.pack(fill="x", padx=20, pady=(20, 6))
    tk.Label(f, text=f"▸ {text}", font=FONT["section"],
             fg=C["accent"], bg=C["bg"]).pack(side="left")
    tk.Frame(f, bg=C["border"], height=1).pack(
        side="left", fill="x", expand=True, padx=(12, 0), pady=8)


def no_data(parent, msg=None):
    if msg is None:
        msg = t("msg_no_data")
    tk.Label(parent, text=msg, font=FONT["body"],
             fg=C["text_dim"], bg=C["bg"], justify="center").pack(expand=True)


def clear(widget):
    for w in widget.winfo_children():
        w.destroy()


def topbar_btn(parent, text, command, primary=False, tooltip: str = ""):
    bg       = C["accent"]  if primary else C["surface2"]
    fg       = "white"      if primary else C["text"]
    bg_hover = C["accent2"] if primary else C["border"]

    btn = tk.Button(parent, text=text, bg=bg, fg=fg,
                    font=FONT["label"], bd=0,
                    padx=14, pady=6, cursor="hand2", relief="flat",
                    activebackground=bg_hover, activeforeground=fg,
                    command=command)

    btn.bind("<Enter>", lambda e: btn.config(bg=bg_hover))
    btn.bind("<Leave>", lambda e: btn.config(bg=bg))

    if tooltip:
        Tooltip(btn, tooltip)

    return btn


def info_btn(parent, title: str, body: str):
    """
    Small ℹ button that opens a modal window with formatted text.
    Used to explain charts with a coach-style approach.
    """
    def _open():
        win = tk.Toplevel()
        win.title(title)
        win.configure(bg=C["bg"])
        win.geometry("680x560")
        win.resizable(True, True)

        # Header
        tk.Label(win, text=title,
                 font=("Courier", 11, "bold"), fg=C["accent"],
                 bg=C["bg"], pady=14).pack(fill="x")
        tk.Frame(win, bg=C["border"], height=1).pack(fill="x", padx=20)

        # Scrollable text area
        frame = tk.Frame(win, bg=C["bg"])
        frame.pack(fill="both", expand=True, padx=20, pady=12)

        sb = ttk.Scrollbar(frame, orient="vertical")
        sb.pack(side="right", fill="y")

        txt = tk.Text(frame, wrap="word",
                      font=("Courier", 9), fg=C["text"], bg=C["surface2"],
                      bd=0, padx=16, pady=14, relief="flat",
                      yscrollcommand=sb.set,
                      highlightthickness=1,
                      highlightbackground=C["border"],
                      cursor="arrow", state="normal")
        txt.pack(fill="both", expand=True)
        sb.config(command=txt.yview)

        # Formatting tags
        txt.tag_configure("title",   font=("Courier", 10, "bold"),
                          foreground=C["accent"])
        txt.tag_configure("section", font=("Courier", 9, "bold"),
                          foreground=C["blue"])
        txt.tag_configure("note",    font=("Courier", 8, "italic"),
                          foreground=C["text_dim"])
        txt.tag_configure("bullet",  font=("Courier", 9),
                          foreground=C["green"])

        # Text formatting based on simple markdown-like syntax:
        for line in body.splitlines():
            stripped = line.strip()
            if stripped.startswith("##"):
                txt.insert("end", stripped[2:].strip() + "\n", "title")
            elif stripped.startswith("#"):
                txt.insert("end", "\n" + stripped[1:].strip() + "\n", "section")
            elif stripped.startswith("•") or stripped.startswith("-"):
                txt.insert("end", "  " + stripped + "\n", "bullet")
            elif stripped.startswith("NOTE") or stripped.startswith("NOTA"):
                txt.insert("end", stripped + "\n", "note")
            else:
                txt.insert("end", stripped + "\n" if stripped else "\n")

        txt.config(state="disabled")

        tk.Button(win, text=t("btn_info_close"),
                  font=("Courier", 9, "bold"), bg=C["surface2"], fg=C["text"],
                  bd=0, padx=16, pady=8, cursor="hand2",
                  command=win.destroy).pack(pady=(0, 16))

    return tk.Button(parent, text=t("btn_info"),
                     font=("Courier", 8, "bold"),
                     bg=C["surface2"], fg=C["blue"],
                     bd=0, padx=8, pady=3,
                     cursor="hand2", relief="flat",
                     command=_open)
