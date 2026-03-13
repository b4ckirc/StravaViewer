# ── ui/tab_calendar.py ────────────────────────────────────────────────────────
"""
Tab Calendario: vista mensile delle corse con navigazione mese per mese.
"""

import tkinter as tk
from tkinter import ttk
import calendar
from datetime import date
from config import C
from models import fmt_pace
from ui.widgets import clear

MONTHS_IT = [
    "", "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno",
    "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre",
]
DAYS_IT = ["LUN", "MAR", "MER", "GIO", "VEN", "SAB", "DOM"]

CELL_W = 130
CELL_H = 90


def render(tab, storage_mgr, on_open):
    clear(tab)

    # ── Carica e indicizza tutti i summary per data ────────────────────────────
    try:
        all_summaries = storage_mgr.list_all()
    except Exception:
        all_summaries = []

    from collections import defaultdict
    by_date = defaultdict(list)
    for s in all_summaries:
        d = (s.get("start_date") or "")[:10]
        if d:
            by_date[d].append(s)

    today = date.today()
    state = {"year": today.year, "month": today.month}

    # ── Topbar con navigazione ─────────────────────────────────────────────────
    nav = tk.Frame(tab, bg=C["surface"], pady=10)
    nav.pack(fill="x")

    month_var = tk.StringVar()
    tk.Label(nav, textvariable=month_var,
             font=("Courier", 13, "bold"), fg=C["accent"],
             bg=C["surface"]).pack(side="left", padx=20)

    # Totali mese
    month_total_var = tk.StringVar()
    tk.Label(nav, textvariable=month_total_var,
             font=("Courier", 9), fg=C["text_dim"],
             bg=C["surface"]).pack(side="left", padx=16)

    tk.Button(nav, text="▶", font=("Courier", 11, "bold"),
              bg=C["surface2"], fg=C["text"], bd=0, padx=14, pady=4,
              cursor="hand2",
              command=lambda: _go_month(1)).pack(side="right", padx=8)
    tk.Button(nav, text="◀", font=("Courier", 11, "bold"),
              bg=C["surface2"], fg=C["text"], bd=0, padx=14, pady=4,
              cursor="hand2",
              command=lambda: _go_month(-1)).pack(side="right", padx=4)
    tk.Button(nav, text="Oggi", font=("Courier", 9, "bold"),
              bg=C["accent"], fg="white", bd=0, padx=10, pady=4,
              cursor="hand2",
              command=lambda: _go_today()).pack(side="right", padx=8)

    # ── Intestazione giorni ────────────────────────────────────────────────────
    hdr = tk.Frame(tab, bg=C["surface"])
    hdr.pack(fill="x", padx=4)
    for i, day_name in enumerate(DAYS_IT):
        col = C["red"] if i >= 5 else C["text_dim"]
        tk.Label(hdr, text=day_name, font=("Courier", 8, "bold"),
                 fg=col, bg=C["surface"],
                 width=17, anchor="center", pady=6).grid(
            row=0, column=i, padx=2, sticky="ew")
        hdr.columnconfigure(i, weight=1)

    # ── Area scrollabile per la griglia ───────────────────────────────────────
    sc = tk.Canvas(tab, bg=C["bg"], bd=0, highlightthickness=0)
    sb = ttk.Scrollbar(tab, orient="vertical", command=sc.yview)
    sc.configure(yscrollcommand=sb.set)
    sb.pack(side="right", fill="y")
    sc.pack(fill="both", expand=True)

    cal_frame = tk.Frame(sc, bg=C["bg"])
    wid = sc.create_window((0, 0), window=cal_frame, anchor="nw")
    cal_frame.bind("<Configure>",
                   lambda e: sc.configure(scrollregion=sc.bbox("all")))
    sc.bind("<Configure>", lambda e: sc.itemconfig(wid, width=e.width))
    sc.bind_all("<MouseWheel>",
                lambda e: sc.yview_scroll(int(-1 * (e.delta / 120)), "units"))

    # ── Logica navigazione ─────────────────────────────────────────────────────

    def _go_month(delta):
        m = state["month"] + delta
        y = state["year"]
        if m > 12: m = 1;  y += 1
        if m < 1:  m = 12; y -= 1
        state["month"] = m
        state["year"]  = y
        _render_month()

    def _go_today():
        state["year"]  = today.year
        state["month"] = today.month
        _render_month()

    # ── Rendering griglia mensile ──────────────────────────────────────────────

    def _render_month():
        for w in cal_frame.winfo_children():
            w.destroy()

        y, m = state["year"], state["month"]
        month_var.set(f"{MONTHS_IT[m]}  {y}")

        weeks = calendar.monthcalendar(y, m)

        # Statistiche totali del mese
        month_km   = 0.0
        month_runs = 0
        for day_num in range(1, calendar.monthrange(y, m)[1] + 1):
            d_str = f"{y:04d}-{m:02d}-{day_num:02d}"
            for s in by_date.get(d_str, []):
                month_km   += s.get("distance", 0) / 1000
                month_runs += 1
        if month_runs:
            month_total_var.set(
                f"  {month_runs} cors{'a' if month_runs == 1 else 'e'}  •  {month_km:.1f} km")
        else:
            month_total_var.set("  —")

        for week_i, week in enumerate(weeks):
            for day_i, day_num in enumerate(week):
                _build_cell(week_i, day_i, day_num, y, m)

        for i in range(7):
            cal_frame.columnconfigure(i, weight=1)

    def _build_cell(row, col, day_num, y, m):
        if day_num == 0:
            tk.Frame(cal_frame, bg=C["bg"],
                     width=CELL_W, height=CELL_H
                     ).grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
            return

        d_str = f"{y:04d}-{m:02d}-{day_num:02d}"
        runs  = by_date.get(d_str, [])
        is_today   = (date(y, m, day_num) == date.today())
        is_weekend = col >= 5

        if runs:
            bg_cell    = C["surface"]
            border_col = C["accent"]
            border_w   = 2
        elif is_today:
            bg_cell    = C["surface2"]
            border_col = C["blue"]
            border_w   = 2
        else:
            bg_cell    = C["surface2"] if is_weekend else C["bg"]
            border_col = C["border"]
            border_w   = 1

        cell = tk.Frame(cal_frame, bg=bg_cell,
                        width=CELL_W, height=CELL_H,
                        highlightthickness=border_w,
                        highlightbackground=border_col)
        cell.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
        cell.grid_propagate(False)

        # Numero giorno
        day_col = (C["blue"]   if is_today   else
                   C["red"]    if is_weekend  else
                   C["text_dim"])
        tk.Label(cell, text=str(day_num),
                 font=("Courier", 8, "bold"),
                 fg=day_col, bg=bg_cell,
                 anchor="nw").pack(anchor="nw", padx=5, pady=3)

        if not runs:
            return

        run  = runs[0]
        dist = run.get("distance", 0) / 1000
        pace = fmt_pace(run.get("avg_speed", 0))

        tk.Label(cell, text=f"{dist:.1f} km",
                 font=("Courier", 9, "bold"),
                 fg=C["accent"], bg=bg_cell,
                 anchor="w").pack(anchor="w", padx=5)
        tk.Label(cell, text=f"{pace} /km",
                 font=("Courier", 8),
                 fg=C["green"], bg=bg_cell,
                 anchor="w").pack(anchor="w", padx=5)

        if len(runs) > 1:
            tk.Label(cell, text=f"+{len(runs) - 1} altre",
                     font=("Courier", 7),
                     fg=C["text_dim"], bg=bg_cell,
                     anchor="w").pack(anchor="w", padx=5)

        # Click apre la prima corsa del giorno
        summary = run
        for widget in cell.winfo_children():
            widget.bind("<Button-1>", lambda e, s=summary: on_open(s))
            widget.config(cursor="hand2")
        cell.bind("<Button-1>", lambda e, s=summary: on_open(s))
        cell.config(cursor="hand2")

    _render_month()
