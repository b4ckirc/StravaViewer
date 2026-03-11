# ── ui/widgets.py ─────────────────────────────────────────────────────────────
"""Widget e helper grafici condivisi tra tutti i tab."""

import tkinter as tk
from tkinter import ttk
from config import C

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
    HAS_MPL = True
except ImportError:
    HAS_MPL = False


class StatCard(tk.Frame):
    def __init__(self, parent, label, value, unit="", color=None, **kw):
        super().__init__(parent, bg=C["surface2"], bd=0,
                         highlightthickness=1, highlightbackground=C["border"], **kw)
        self.config(padx=16, pady=12)
        color = color or C["text"]
        tk.Label(self, text=label.upper(), font=("Courier", 8, "bold"),
                 fg=C["text_dim"], bg=C["surface2"]).pack(anchor="w")
        vf = tk.Frame(self, bg=C["surface2"])
        vf.pack(anchor="w", pady=(2, 0))
        tk.Label(vf, text=str(value), font=("Courier", 20, "bold"),
                 fg=color, bg=C["surface2"]).pack(side="left")
        if unit:
            tk.Label(vf, text=f" {unit}", font=("Courier", 9),
                     fg=C["text_dim"], bg=C["surface2"]).pack(side="left", pady=(7, 0))


def make_scrollable(parent):
    """Ritorna (canvas, inner_frame) con scrollbar verticale."""
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
    """Incorpora figura matplotlib in un frame tkinter con toolbar."""
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
    f.pack(fill="x", padx=20, pady=(18, 6))
    tk.Label(f, text=f"▸ {text}", font=("Courier", 9, "bold"),
             fg=C["accent"], bg=C["bg"]).pack(side="left")
    tk.Frame(f, bg=C["border"], height=1).pack(
        side="left", fill="x", expand=True, padx=(10, 0), pady=8)


def no_data(parent, msg="Nessun dato disponibile."):
    tk.Label(parent, text=msg, font=("Courier", 12),
             fg=C["text_dim"], bg=C["bg"], justify="center").pack(expand=True)


def clear(widget):
    for w in widget.winfo_children():
        w.destroy()


def topbar_btn(parent, text, command, primary=False):
    bg = C["accent"] if primary else C["surface2"]
    fg = "white"     if primary else C["text"]
    return tk.Button(parent, text=text, bg=bg, fg=fg,
                     font=("Courier", 9, "bold"), bd=0,
                     padx=14, pady=6, cursor="hand2", relief="flat",
                     command=command)
