# ── ui/tab_best.py ────────────────────────────────────────────────────────────
import tkinter as tk
from config import C
from models import fmt_time, fmt_pace
from ui.widgets import no_data, clear
from i18n import t


def render(tab, activity):
    clear(tab)
    a = activity
    if not a.best_efforts:
        no_data(tab, t("no_best_efforts"))
        return
    tk.Label(tab, text=t("best_title"),
             font=("Segoe UI", 11, "bold"), fg=C["accent"],
             bg=C["surface"], pady=12).pack(fill="x")
    # pixel widths: name, time, pace  (badge is flexible)
    col_pwidths = [200, 85, 110]

    for i, be in enumerate(a.best_efforts):
        name    = be.get("name", "")
        elapsed = be.get("elapsed_time", 0)
        dist    = be.get("distance", 0)
        pr_rank = be.get("pr_rank")
        pace    = fmt_pace(dist / elapsed) if elapsed else "--:--"
        badge, bc = "", C["text_dim"]
        if pr_rank == 1: badge, bc = t("pr_badge"), C["yellow"]
        elif pr_rank:    badge, bc = f"  {t('pr_rank').format(n=pr_rank)}", C["text_dim"]
        bg  = C["surface2"] if i % 2 == 0 else C["surface"]
        row = tk.Frame(tab, bg=bg, padx=24, pady=10)
        row.pack(fill="x")
        for text, fg, pw, anc, bold in [
            (name,              C["blue"],  col_pwidths[0], "w",      True),
            (fmt_time(elapsed), C["text"],  col_pwidths[1], "center", False),
            (f"{pace} /km",     C["green"], col_pwidths[2], "center", False),
        ]:
            cf = tk.Frame(row, width=pw, height=24, bg=bg)
            cf.pack_propagate(False)
            cf.pack(side="left")
            tk.Label(cf, text=text, font=("Segoe UI", 10, "bold") if bold else ("Segoe UI", 10),
                     fg=fg, bg=bg, anchor=anc).pack(fill="both", expand=True)
        tk.Label(row, text=badge, font=("Segoe UI", 9, "bold"),
                 fg=bc, bg=bg).pack(side="left")
