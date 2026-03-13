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


def _blend_color(c1: str, c2: str, t: float) -> str:
    """Interpola tra due colori hex. t=0 → c1, t=1 → c2."""
    def h2rgb(h): return int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)
    r1, g1, b1 = h2rgb(c1)
    r2, g2, b2 = h2rgb(c2)
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return f"#{r:02x}{g:02x}{b:02x}"


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

        # Statistiche totali del mese + massimo km per heatmap
        month_km   = 0.0
        month_runs = 0
        day_km     = {}   # d_str → km totali quel giorno
        for day_num in range(1, calendar.monthrange(y, m)[1] + 1):
            d_str = f"{y:04d}-{m:02d}-{day_num:02d}"
            km_day = sum(s.get("distance", 0) / 1000 for s in by_date.get(d_str, []))
            n_day  = len(by_date.get(d_str, []))
            day_km[d_str]  = km_day
            month_km      += km_day
            month_runs    += n_day

        max_km = max(day_km.values(), default=0.0)

        if month_runs:
            month_total_var.set(
                f"  {month_runs} cors{'a' if month_runs == 1 else 'e'}  •  {month_km:.1f} km")
        else:
            month_total_var.set("  —")

        for week_i, week in enumerate(weeks):
            for day_i, day_num in enumerate(week):
                _build_cell(week_i, day_i, day_num, y, m, day_km, max_km)

        for i in range(7):
            cal_frame.columnconfigure(i, weight=1)
        for i in range(len(weeks)):
            cal_frame.rowconfigure(i, uniform="calrow", minsize=CELL_H + 2)

    def _build_cell(row, col, day_num, y, m, day_km, max_km):
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
            # Heatmap: intensità proporzionale ai km del giorno vs massimo mese
            km     = day_km.get(d_str, 0.0)
            t      = min(km / max_km, 1.0) if max_km > 0 else 0.0
            # Blend da surface verso accent con intensità [15%–55%]
            t_scaled   = 0.15 + t * 0.40
            bg_cell    = _blend_color(C["surface"], C["accent"], t_scaled)
            border_col = C["accent"]
        elif is_today:
            bg_cell    = C["surface2"]
            border_col = C["blue"]
        else:
            bg_cell    = C["surface2"] if is_weekend else C["bg"]
            border_col = C["border"]

        cell = tk.Frame(cal_frame, bg=bg_cell,
                        width=CELL_W, height=CELL_H,
                        highlightthickness=1,
                        highlightbackground=border_col)
        cell.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
        cell.grid_propagate(False)

        # Riga superiore: numero giorno + contatore (se più corse)
        day_col = (C["blue"]   if is_today   else
                   C["red"]    if is_weekend  else
                   C["text_dim"])
        top_f = tk.Frame(cell, bg=bg_cell)
        top_f.pack(fill="x", padx=5, pady=(3, 0))
        tk.Label(top_f, text=str(day_num),
                 font=("Courier", 8, "bold"),
                 fg=day_col, bg=bg_cell).pack(side="left")

        if not runs:
            return

        idx = [0]  # indice corrente (mutabile in closure)
        n   = len(runs)

        counter_var = tk.StringVar(value=f"1/{n}" if n > 1 else "")
        if n > 1:
            tk.Label(top_f, textvariable=counter_var,
                     font=("Courier", 7), fg=C["text_dim"],
                     bg=bg_cell).pack(side="right")

        # Etichette contenuto (aggiornate dalla navigazione)
        dist_var = tk.StringVar()
        pace_var = tk.StringVar()
        hr_var   = tk.StringVar()

        dist_lbl = tk.Label(cell, textvariable=dist_var,
                            font=("Courier", 10, "bold"),
                            fg=C["text"], bg=bg_cell, anchor="w")
        dist_lbl.pack(anchor="w", padx=6, pady=(1, 0))
        pace_lbl = tk.Label(cell, textvariable=pace_var,
                            font=("Courier", 8),
                            fg=C["text_dim"], bg=bg_cell, anchor="w")
        pace_lbl.pack(anchor="w", padx=6)
        hr_lbl = tk.Label(cell, textvariable=hr_var,
                          font=("Courier", 8),
                          fg=C["text_dim"], bg=bg_cell, anchor="w")
        hr_lbl.pack(anchor="w", padx=6)

        def _refresh():
            run = runs[idx[0]]
            dist_var.set(f"{run.get('distance', 0) / 1000:.1f} km")
            pace_var.set(f"⚡ {fmt_pace(run.get('avg_speed', 0))} /km")
            hr = run.get("avg_hr")
            hr_var.set(f"♥ {hr:.0f} bpm" if hr else "")
            counter_var.set(f"{idx[0] + 1}/{n}")
            _rebind(run)

        def _rebind(run):
            for w in [cell, top_f, dist_lbl, pace_lbl, hr_lbl]:
                w.bind("<Button-1>", lambda e, s=run: on_open(s))
                w.config(cursor="hand2")

        _refresh()

        # Frecce di navigazione (solo se più corse)
        if n > 1:
            nav_f = tk.Frame(cell, bg=bg_cell)
            nav_f.pack(side="bottom", fill="x", padx=4, pady=(0, 3))

            def _prev():
                idx[0] = (idx[0] - 1) % n
                _refresh()

            def _next():
                idx[0] = (idx[0] + 1) % n
                _refresh()

            btn_cfg = dict(font=("Courier", 8, "bold"), bg=C["surface2"],
                           fg=C["text"], bd=0, padx=6, pady=1, cursor="hand2")
            tk.Button(nav_f, text="◀", command=_prev, **btn_cfg).pack(side="left")
            tk.Button(nav_f, text="▶", command=_next, **btn_cfg).pack(side="right")

    _render_month()
