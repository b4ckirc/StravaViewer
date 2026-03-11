# ── ui/tab_best.py ────────────────────────────────────────────────────────────
import tkinter as tk
from config import C
from models import fmt_time, fmt_pace
from ui.widgets import no_data, clear


def render(tab, activity):
    clear(tab)
    a = activity
    if not a.best_efforts:
        no_data(tab, "Nessun best effort registrato.")
        return
    tk.Label(tab, text="BEST EFFORTS",
             font=("Courier", 11, "bold"), fg=C["accent"],
             bg=C["surface"], pady=12).pack(fill="x")
    for i, be in enumerate(a.best_efforts):
        name    = be.get("name", "")
        elapsed = be.get("elapsed_time", 0)
        dist    = be.get("distance", 0)
        pr_rank = be.get("pr_rank")
        pace    = fmt_pace(dist / elapsed) if elapsed else "--:--"
        badge, bc = "", C["text_dim"]
        if pr_rank == 1: badge, bc = "🏆 RECORD PERSONALE", C["yellow"]
        elif pr_rank:    badge, bc = f"  #{pr_rank} personale", C["text_dim"]
        bg  = C["surface2"] if i % 2 == 0 else C["surface"]
        row = tk.Frame(tab, bg=bg, padx=24, pady=10)
        row.pack(fill="x")
        tk.Label(row, text=f"{name:<24}", font=("Courier", 10, "bold"),
                 fg=C["blue"], bg=bg).pack(side="left")
        tk.Label(row, text=fmt_time(elapsed), font=("Courier", 10),
                 fg=C["text"], bg=bg, width=10).pack(side="left")
        tk.Label(row, text=f"{pace} /km", font=("Courier", 10),
                 fg=C["green"], bg=bg, width=14).pack(side="left")
        tk.Label(row, text=badge, font=("Courier", 9, "bold"),
                 fg=bc, bg=bg).pack(side="left")
