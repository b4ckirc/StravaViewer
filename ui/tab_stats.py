# ── ui/tab_stats.py ───────────────────────────────────────────────────────────
"""
Tab statistiche globali su tutte le corse in libreria.
"""

import tkinter as tk
import json, math, os
from datetime import date, timedelta
from config import C
from models import fmt_time, fmt_pace
from ui.widgets import StatCard, make_scrollable, section_label, no_data, clear, info_btn

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib.gridspec as gridspec
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

SETTINGS_FILE = "settings.json"
MONTHS_IT = ["", "Gen", "Feb", "Mar", "Apr", "Mag", "Giu",
             "Lug", "Ago", "Set", "Ott", "Nov", "Dic"]


def _load_settings() -> dict:
    try:
        with open(SETTINGS_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_settings(s: dict):
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(s, f, indent=2)
    except Exception:
        pass


def render(tab, storage_mgr):
    clear(tab)

    tk.Label(tab, text="STATISTICHE GLOBALI",
             font=("Courier", 12, "bold"), fg=C["accent"],
             bg=C["surface"], pady=12).pack(fill="x")

    # Carica tutti i summary
    try:
        all_summaries = storage_mgr.list_all()
    except Exception as e:
        no_data(tab, f"Errore caricamento dati:\n{e}")
        return

    if not all_summaries:
        no_data(tab, "Nessuna corsa in libreria.\n\nScarica o importa delle attività prima.")
        return

    _, body = make_scrollable(tab)

    # ── Calcola aggregati ──────────────────────────────────────────────────────
    n_runs     = len(all_summaries)
    total_dist = sum(s.get("distance", 0) for s in all_summaries) / 1000
    total_time = sum(s.get("moving_time", 0) for s in all_summaries)
    total_elev = sum(s.get("elev_gain", 0) for s in all_summaries)
    avg_speeds = [s.get("avg_speed", 0) for s in all_summaries if s.get("avg_speed", 0) > 0]
    avg_speed  = sum(avg_speeds) / len(avg_speeds) if avg_speeds else 0
    hrs        = [s.get("avg_hr") for s in all_summaries if s.get("avg_hr")]
    avg_hr     = sum(hrs) / len(hrs) if hrs else None
    dists      = [s.get("distance", 0) / 1000 for s in all_summaries]
    avg_dist   = sum(dists) / len(dists) if dists else 0
    max_dist   = max(dists) if dists else 0
    cals       = [s.get("calories", 0) or 0 for s in all_summaries]
    total_cals = sum(cals)

    # ── Stat principali ────────────────────────────────────────────────────────
    section_label(body, "RIEPILOGO COMPLESSIVO")
    g = tk.Frame(body, bg=C["bg"])
    g.pack(fill="x", padx=20, pady=(0, 4))
    cards = [
        ("Corse totali",    f"{n_runs}",           "",          C["accent"]),
        ("Km totali",       f"{total_dist:.1f}",   "km",        C["blue"]),
        ("Ore totali",      fmt_time(total_time),  "",          C["green"]),
        ("Dislivello tot.", f"{total_elev:.0f}",   "m",         C["yellow"]),
        ("Passo medio",     fmt_pace(avg_speed),   "min/km",    C["accent2"]),
        ("HR media",        f"{avg_hr:.0f}" if avg_hr else "–", "bpm", C["red"]),
    ]
    for i, (l, v, u, col) in enumerate(cards):
        StatCard(g, l, v, u, col).grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
        g.columnconfigure(i, weight=1)

    section_label(body, "DETTAGLI")
    g2 = tk.Frame(body, bg=C["bg"])
    g2.pack(fill="x", padx=20, pady=(0, 4))
    extra = [
        ("Dist. media",   f"{avg_dist:.1f}",     "km",   C["text"]),
        ("Corsa più lunga", f"{max_dist:.1f}",   "km",   C["green"]),
        ("Calorie totali",  f"{total_cals:.0f}", "kcal", C["orange"]),
        ("Media km/sett.", _avg_km_per_week(all_summaries), "km", C["purple"]),
    ]
    for i, (l, v, u, col) in enumerate(extra):
        StatCard(g2, l, v, u, col).grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
        g2.columnconfigure(i, weight=1)

    # ── Obiettivo annuale ──────────────────────────────────────────────────────
    _render_annual_goal(body, all_summaries)

    # ── Statistiche per anno ───────────────────────────────────────────────────
    by_year = _group_by_year(all_summaries)
    if by_year:
        section_label(body, "STATISTICHE PER ANNO")
        tbl = tk.Frame(body, bg=C["surface2"],
                       highlightthickness=1, highlightbackground=C["border"])
        tbl.pack(fill="x", padx=20, pady=(0, 10))
        yr_cols   = ["ANNO", "CORSE", "KM TOT.", "TEMPO TOT.", "PASSO MEDIO", "↑ ELEV."]
        yr_widths = [8, 7, 10, 11, 12, 10]
        hrow = tk.Frame(tbl, bg=C["surface"])
        hrow.pack(fill="x")
        for col, w in zip(yr_cols, yr_widths):
            tk.Label(hrow, text=col, font=("Courier", 8, "bold"),
                     fg=C["text_dim"], bg=C["surface"],
                     width=w, anchor="center", pady=8).pack(side="left", padx=3)
        for i, (year, data) in enumerate(sorted(by_year.items(), reverse=True)):
            bg = C["surface2"] if i % 2 == 0 else C["surface"]
            row = tk.Frame(tbl, bg=bg)
            row.pack(fill="x")
            yr_vals = [
                (str(year),                          C["accent"]),
                (str(data["count"]),                 C["text"]),
                (f"{data['dist_km']:.1f} km",        C["blue"]),
                (fmt_time(data["time_sec"]),          C["text"]),
                (fmt_pace(data["avg_speed"]),         C["green"]),
                (f"{data['elev_gain']:.0f} m",        C["yellow"]),
            ]
            for (v, col), w in zip(yr_vals, yr_widths):
                tk.Label(row, text=v, font=("Courier", 9), fg=col, bg=bg,
                         width=w, anchor="center", pady=7).pack(side="left", padx=3)

        # ── Grafico km per anno ────────────────────────────────────────────────
        if HAS_MPL and len(by_year) > 1:
            section_label(body, "KM PER ANNO")
            cf = tk.Frame(body, bg=C["bg"])
            cf.pack(fill="x", padx=20, pady=(0, 20))

            years   = sorted(by_year.keys())
            km_vals = [by_year[y]["dist_km"] for y in years]
            n_vals  = [by_year[y]["count"]   for y in years]

            fig = plt.Figure(figsize=(12, 4), facecolor=C["bg"])
            gs  = gridspec.GridSpec(1, 2, figure=fig,
                                    left=0.07, right=0.97, top=0.85, bottom=0.15, wspace=0.35)

            ax1 = fig.add_subplot(gs[0, 0])
            bars = ax1.bar(years, km_vals, color=C["accent"], alpha=0.85, width=0.6)
            ax1.set_facecolor(C["surface"])
            ax1.set_title("KM PER ANNO", color=C["text"], fontsize=9,
                          fontweight="bold", fontfamily="monospace", pad=6)
            ax1.tick_params(colors=C["text_dim"], labelsize=7)
            ax1.set_ylabel("km", fontsize=7, color=C["text_dim"])
            for sp in ax1.spines.values(): sp.set_edgecolor(C["border"])
            ax1.grid(axis="y", color=C["border"], linestyle="--", linewidth=0.4, alpha=0.6)
            for bar, v in zip(bars, km_vals):
                ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10,
                         f"{v:.0f}", ha="center", fontsize=6.5, color=C["text"],
                         fontfamily="monospace")

            ax2 = fig.add_subplot(gs[0, 1])
            bars2 = ax2.bar(years, n_vals, color=C["blue"], alpha=0.85, width=0.6)
            ax2.set_facecolor(C["surface"])
            ax2.set_title("CORSE PER ANNO", color=C["text"], fontsize=9,
                          fontweight="bold", fontfamily="monospace", pad=6)
            ax2.tick_params(colors=C["text_dim"], labelsize=7)
            ax2.set_ylabel("n. corse", fontsize=7, color=C["text_dim"])
            for sp in ax2.spines.values(): sp.set_edgecolor(C["border"])
            ax2.grid(axis="y", color=C["border"], linestyle="--", linewidth=0.4, alpha=0.6)
            for bar, v in zip(bars2, n_vals):
                ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                         str(v), ha="center", fontsize=6.5, color=C["text"],
                         fontfamily="monospace")

            cnv = FigureCanvasTkAgg(fig, master=cf)
            cnv.draw()
            cnv.get_tk_widget().pack(fill="x")

    # ── Statistiche per mese (ultimi 12 mesi) ────────────────────────────────
    _render_monthly_stats(body, all_summaries)

    # ── Carico di allenamento (ATL / CTL / TSB) ───────────────────────────────
    if HAS_MPL:
        _render_training_load(body, all_summaries)

    # ── Distribuzione distanze ─────────────────────────────────────────────────
    if HAS_MPL and dists:
        section_label(body, "DISTRIBUZIONE DISTANZE")
        cf3 = tk.Frame(body, bg=C["bg"])
        cf3.pack(fill="x", padx=20, pady=(0, 20))

        buckets = {"< 5 km": 0, "5–10 km": 0, "10–15 km": 0,
                   "15–21 km": 0, "21–42 km": 0, "> 42 km": 0}
        for d in dists:
            if   d < 5:   buckets["< 5 km"]    += 1
            elif d < 10:  buckets["5–10 km"]   += 1
            elif d < 15:  buckets["10–15 km"]  += 1
            elif d < 21:  buckets["15–21 km"]  += 1
            elif d < 42:  buckets["21–42 km"]  += 1
            else:         buckets["> 42 km"]   += 1

        labels = list(buckets.keys())
        values = list(buckets.values())
        colors_pie = [C["blue"], C["green"], C["yellow"],
                      C["accent"], C["red"], C["purple"]]

        fig3 = plt.Figure(figsize=(7, 4), facecolor=C["bg"])
        ax3  = fig3.add_subplot(111)
        ax3.set_facecolor(C["bg"])
        wedges, texts, autotexts = ax3.pie(
            values, labels=labels, colors=colors_pie,
            autopct=lambda p: f"{p:.1f}%" if p > 1 else "",
            startangle=90, textprops={"color": C["text"], "fontsize": 8,
                                       "fontfamily": "monospace"},
            wedgeprops={"edgecolor": C["border"], "linewidth": 1.2},
        )
        for at in autotexts:
            at.set_fontsize(7)
        ax3.set_title("DISTRIBUZIONE DISTANZE", color=C["text"], fontsize=9,
                      fontweight="bold", fontfamily="monospace", pad=10)

        cnv3 = FigureCanvasTkAgg(fig3, master=cf3)
        cnv3.draw()
        cnv3.get_tk_widget().pack()

    # ── Record personali ──────────────────────────────────────────────────────
    section_label(body, "RECORD PERSONALI")
    rec_outer = tk.Frame(body, bg=C["surface2"],
                         highlightthickness=1, highlightbackground=C["border"])
    rec_outer.pack(fill="x", padx=20, pady=(0, 24))

    hrow = tk.Frame(rec_outer, bg=C["surface"])
    hrow.pack(fill="x")
    for col_text, w in [("DISTANZA", 18), ("TEMPO", 10), ("ATTIVITÀ", 34), ("DATA", 14)]:
        tk.Label(hrow, text=col_text, font=("Courier", 8, "bold"),
                 fg=C["text_dim"], bg=C["surface"],
                 width=w, anchor="center", pady=8).pack(side="left", padx=3)

    try:
        records = storage_mgr.get_personal_records()
    except Exception:
        records = {}

    DIST_ORDER = [
        ("1k",            "🏃 1 km"),
        ("5k",            "🏃 5 km"),
        ("10k",           "🏃 10 km"),
        ("Half-Marathon", "🏃 Mezza Maratona"),
        ("Marathon",      "🏃 Maratona"),
    ]
    found_any = False
    for i, (key, label) in enumerate(DIST_ORDER):
        r = records.get(key)
        bg = C["surface2"] if i % 2 == 0 else C["surface"]
        row = tk.Frame(rec_outer, bg=bg)
        row.pack(fill="x")
        if r:
            found_any = True
            label_txt = label.replace("🏃", "🏆")
            time_str  = fmt_time(r["elapsed_time"])
            act_name  = (r["activity_name"] or "–")[:33]
            date_str  = r["date"]
        else:
            label_txt = label.replace("🏃", "  ")
            time_str  = "–"
            act_name  = "nessun dato"
            date_str  = "–"
        for v, col, w, anc in [
            (label_txt, C["accent"],   18, "w"),
            (time_str,  C["green"],    10, "center"),
            (act_name,  C["text"],     34, "w"),
            (date_str,  C["text_dim"], 14, "center"),
        ]:
            tk.Label(row, text=v, font=("Courier", 9), fg=col, bg=bg,
                     width=w, anchor=anc, pady=7, padx=4).pack(side="left")

    if not found_any:
        try:
            found_names = storage_mgr.scan_effort_names()
        except Exception:
            found_names = set()
        if found_names:
            sample = ", ".join(f'"{n}"' for n in sorted(found_names)[:8])
            hint = (f"  Nomi trovati nel database: {sample}\n"
                    f"  I nomi attesi sono: \"1k\", \"5k\", \"10k\", "
                    f"\"Half-Marathon\", \"Marathon\".\n"
                    f"  Segnala i nomi trovati per aggiornare il riconoscimento.")
        else:
            hint = ("  Nessun best effort trovato. Le corse scaricate con activity:read_all\n"
                    "  includono automaticamente i best efforts.")
        tk.Label(rec_outer, text=hint,
                 font=("Courier", 8), fg=C["text_dim"], bg=C["surface2"],
                 pady=10, wraplength=760, justify="left").pack(anchor="w", padx=16)


# ── Helper ────────────────────────────────────────────────────────────────────

def _group_by_year(summaries):
    from collections import defaultdict
    by_year = defaultdict(lambda: {"count": 0, "dist_km": 0.0,
                                   "time_sec": 0, "elev_gain": 0.0,
                                   "speed_sum": 0.0, "speed_n": 0})
    for s in summaries:
        y = (s.get("start_date") or "")[:4]
        if not y.isdigit():
            continue
        y = int(y)
        by_year[y]["count"]    += 1
        by_year[y]["dist_km"]  += s.get("distance", 0) / 1000
        by_year[y]["time_sec"] += s.get("moving_time", 0)
        by_year[y]["elev_gain"]+= s.get("elev_gain", 0)
        sp = s.get("avg_speed", 0)
        if sp > 0:
            by_year[y]["speed_sum"] += sp
            by_year[y]["speed_n"]   += 1
    for y in by_year:
        n = by_year[y]["speed_n"]
        by_year[y]["avg_speed"] = by_year[y]["speed_sum"] / n if n else 0
    return dict(by_year)

def _avg_km_per_week(summaries):
    if len(summaries) < 2:
        return "–"
    from datetime import datetime
    dates = []
    for s in summaries:
        try:
            dates.append(datetime.fromisoformat(s.get("start_date","").replace("Z","")))
        except Exception:
            pass
    if not dates:
        return "–"
    span_days = (max(dates) - min(dates)).days or 1
    weeks     = span_days / 7
    total_km  = sum(s.get("distance", 0) for s in summaries) / 1000
    return f"{total_km / weeks:.1f}"


# ── Sezione obiettivo annuale ──────────────────────────────────────────────────

def _render_annual_goal(body, all_summaries):
    section_label(body, "OBIETTIVO ANNUALE")
    settings    = _load_settings()
    current_year = date.today().year

    year_km = sum(
        s.get("distance", 0) for s in all_summaries
        if (s.get("start_date") or "")[:4] == str(current_year)
    ) / 1000

    target_km = settings.get("annual_km_goal", 1000.0)
    pct       = min(1.0, year_km / target_km) if target_km > 0 else 0.0

    outer = tk.Frame(body, bg=C["surface2"],
                     highlightthickness=1, highlightbackground=C["border"])
    outer.pack(fill="x", padx=20, pady=(0, 12))

    row_f = tk.Frame(outer, bg=C["surface2"])
    row_f.pack(fill="x", padx=16, pady=10)

    tk.Label(row_f, text=f"Obiettivo {current_year}:",
             font=("Courier", 9), fg=C["text_dim"],
             bg=C["surface2"]).pack(side="left")

    goal_var = tk.StringVar(value=str(int(target_km)))
    tk.Entry(row_f, textvariable=goal_var, font=("Courier", 10),
             bg=C["surface"], fg=C["text"], width=7, bd=0,
             insertbackground=C["text"],
             highlightthickness=1, highlightbackground=C["border"]
             ).pack(side="left", padx=6)
    tk.Label(row_f, text="km", font=("Courier", 9), fg=C["text_dim"],
             bg=C["surface2"]).pack(side="left")

    def _save():
        try:
            val = float(goal_var.get())
            settings["annual_km_goal"] = val
            _save_settings(settings)
        except Exception:
            pass

    tk.Button(row_f, text="✓ Salva", font=("Courier", 8, "bold"),
              bg=C["accent"], fg="white", bd=0, padx=8, pady=3,
              cursor="hand2", command=_save).pack(side="left", padx=10)

    # Testo riepilogo
    col_txt = C["green"] if pct >= 1.0 else C["accent"]
    tk.Label(row_f,
             text=f"{year_km:.0f} / {target_km:.0f} km  ({pct * 100:.1f}%)",
             font=("Courier", 10, "bold"), fg=col_txt,
             bg=C["surface2"]).pack(side="right", padx=8)

    # Barra di avanzamento (Canvas)
    bar_frame = tk.Frame(outer, bg=C["surface2"])
    bar_frame.pack(fill="x", padx=16, pady=(0, 12))

    bar_cv = tk.Canvas(bar_frame, height=16, bg=C["surface"],
                       bd=0, highlightthickness=0)
    bar_cv.pack(fill="x")

    def _draw(e=None):
        w = bar_cv.winfo_width()
        if w < 2:
            return
        bar_cv.delete("all")
        bar_cv.create_rectangle(0, 0, w, 16, fill=C["surface"], outline="")
        filled_w = int(w * pct)
        fill_col = C["green"] if pct >= 1.0 else C["accent"]
        if filled_w > 0:
            bar_cv.create_rectangle(0, 0, filled_w, 16,
                                    fill=fill_col, outline="")

    bar_cv.bind("<Configure>", _draw)
    body.after(120, _draw)


# ── Sezione statistiche mensili ────────────────────────────────────────────────

def _render_monthly_stats(body, all_summaries):
    """Tabella + grafico degli ultimi 12 mesi."""
    from collections import defaultdict
    by_month = defaultdict(lambda: {
        "count": 0, "dist_km": 0.0, "time_sec": 0,
        "elev_gain": 0.0, "speed_sum": 0.0, "speed_n": 0,
    })
    for s in all_summaries:
        ym = (s.get("start_date") or "")[:7]
        if len(ym) < 7 or not ym[:4].isdigit():
            continue
        by_month[ym]["count"]    += 1
        by_month[ym]["dist_km"]  += s.get("distance", 0) / 1000
        by_month[ym]["time_sec"] += s.get("moving_time", 0)
        by_month[ym]["elev_gain"]+= s.get("elev_gain", 0)
        sp = s.get("avg_speed", 0)
        if sp > 0:
            by_month[ym]["speed_sum"] += sp
            by_month[ym]["speed_n"]   += 1

    if not by_month:
        return

    # Calcola avg_speed per mese
    months_sorted = sorted(by_month.keys(), reverse=True)[:12]  # ultimi 12 mesi
    months_sorted.sort()  # ora in ordine cronologico

    section_label(body, "STATISTICHE PER MESE  (ultimi 12 mesi)")
    tbl = tk.Frame(body, bg=C["surface2"],
                   highlightthickness=1, highlightbackground=C["border"])
    tbl.pack(fill="x", padx=20, pady=(0, 8))

    mo_cols   = ["MESE", "CORSE", "KM TOT.", "TEMPO TOT.", "PASSO MEDIO", "↑ ELEV."]
    mo_widths = [9, 7, 10, 11, 12, 10]

    hrow = tk.Frame(tbl, bg=C["surface"])
    hrow.pack(fill="x")
    for col, w in zip(mo_cols, mo_widths):
        tk.Label(hrow, text=col, font=("Courier", 8, "bold"),
                 fg=C["text_dim"], bg=C["surface"],
                 width=w, anchor="center", pady=8).pack(side="left", padx=3)

    for i, ym in enumerate(reversed(months_sorted)):
        d   = by_month[ym]
        n   = d["speed_n"]
        avg = d["speed_sum"] / n if n else 0
        bg  = C["surface2"] if i % 2 == 0 else C["surface"]
        row = tk.Frame(tbl, bg=bg)
        row.pack(fill="x")
        yr, mo = int(ym[:4]), int(ym[5:7])
        mo_vals = [
            (f"{MONTHS_IT[mo]} {yr}",          C["accent"]),
            (str(d["count"]),                   C["text"]),
            (f"{d['dist_km']:.1f} km",          C["blue"]),
            (fmt_time(d["time_sec"]),            C["text"]),
            (fmt_pace(avg),                      C["green"]),
            (f"{d['elev_gain']:.0f} m",          C["yellow"]),
        ]
        for (v, col), w in zip(mo_vals, mo_widths):
            tk.Label(row, text=v, font=("Courier", 9), fg=col, bg=bg,
                     width=w, anchor="center", pady=7).pack(side="left", padx=3)

    # Grafico km per mese
    if HAS_MPL and len(months_sorted) > 1:
        cf = tk.Frame(body, bg=C["bg"])
        cf.pack(fill="x", padx=20, pady=(0, 20))

        labels   = []
        km_vals  = []
        n_vals   = []
        for ym in months_sorted:
            yr, mo = int(ym[:4]), int(ym[5:7])
            labels.append(f"{MONTHS_IT[mo]}\n{yr}")
            km_vals.append(by_month[ym]["dist_km"])
            n_vals.append(by_month[ym]["count"])

        fig = plt.Figure(figsize=(12, 3.5), facecolor=C["bg"])
        gs  = gridspec.GridSpec(1, 1, figure=fig,
                                left=0.05, right=0.98, top=0.82, bottom=0.18)
        ax  = fig.add_subplot(gs[0, 0])
        bars = ax.bar(range(len(labels)), km_vals, color=C["blue"],
                      alpha=0.85, width=0.6)
        ax.set_facecolor(C["surface"])
        ax.set_title("KM PER MESE", color=C["text"], fontsize=9,
                     fontweight="bold", fontfamily="monospace", pad=6)
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, fontsize=6)
        ax.tick_params(colors=C["text_dim"], labelsize=7)
        ax.set_ylabel("km", fontsize=7, color=C["text_dim"])
        for sp in ax.spines.values():
            sp.set_edgecolor(C["border"])
        ax.grid(axis="y", color=C["border"], linestyle="--",
                linewidth=0.4, alpha=0.6)
        for bar, v in zip(bars, km_vals):
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.5,
                    f"{v:.0f}", ha="center", fontsize=6, color=C["text"],
                    fontfamily="monospace")

        cnv = FigureCanvasTkAgg(fig, master=cf)
        cnv.draw()
        cnv.get_tk_widget().pack(fill="x")


# ── Sezione carico di allenamento (ATL / CTL / TSB) ───────────────────────────

def _trimp(s: dict) -> float:
    """TRIMP semplificato per una sessione."""
    t_min = s.get("moving_time", 0) / 60.0
    hr    = s.get("avg_hr")
    if hr and hr > 0:
        # Banister TRIMP con hrRest=60, hrMax=190
        hr_ratio = max(0.0, min(1.0, (hr - 60) / (190 - 60)))
        return t_min * hr_ratio * 0.64 * math.exp(1.92 * hr_ratio)
    # Fallback senza FC: distanza in km come proxy
    return s.get("distance", 0) / 1000.0


def _compute_training_load(summaries):
    """Ritorna (dates, atl_list, ctl_list, tsb_list) per l'ultimo anno."""
    from collections import defaultdict
    daily = defaultdict(float)
    for s in summaries:
        d = (s.get("start_date") or "")[:10]
        if len(d) == 10:
            daily[d] += _trimp(s)

    if not daily:
        return [], [], [], []

    d_end   = date.today()
    d_start = d_end - timedelta(days=364)

    k_atl = math.exp(-1 / 7)
    k_ctl = math.exp(-1 / 42)

    # Inizializza ATL/CTL sullo storico precedente (tutto il database)
    all_dates = sorted(daily.keys())
    atl = ctl = 0.0
    if all_dates and all_dates[0] < d_start.isoformat():
        cur = date.fromisoformat(all_dates[0])
        while cur < d_start:
            load = daily.get(cur.isoformat(), 0.0)
            atl  = atl * k_atl + load * (1 - k_atl)
            ctl  = ctl * k_ctl + load * (1 - k_ctl)
            cur += timedelta(days=1)

    dates_out, atl_out, ctl_out, tsb_out = [], [], [], []
    cur = d_start
    while cur <= d_end:
        load = daily.get(cur.isoformat(), 0.0)
        atl  = atl * k_atl + load * (1 - k_atl)
        ctl  = ctl * k_ctl + load * (1 - k_ctl)
        dates_out.append(cur)
        atl_out.append(atl)
        ctl_out.append(ctl)
        tsb_out.append(ctl - atl)
        cur += timedelta(days=1)

    return dates_out, atl_out, ctl_out, tsb_out


def _render_training_load(body, all_summaries):
    dates, atl, ctl, tsb = _compute_training_load(all_summaries)
    if not dates:
        return

    section_label(body, "CARICO DI ALLENAMENTO  (ultimi 12 mesi)")

    # Legenda testuale + bottone info
    leg_f = tk.Frame(body, bg=C["bg"])
    leg_f.pack(fill="x", padx=20, pady=(0, 4))
    for txt, col in [
        ("■ CTL – Fitness (42 gg)", C["blue"]),
        ("■ ATL – Fatica (7 gg)",   C["red"]),
        ("■ TSB – Forma (CTL-ATL)", C["green"]),
    ]:
        tk.Label(leg_f, text=txt, font=("Courier", 8), fg=col,
                 bg=C["bg"]).pack(side="left", padx=10)
    info_btn(leg_f, "Come leggere il grafico del Carico di Allenamento",
             _INFO_TRAINING_LOAD).pack(side="right", padx=8)

    cf = tk.Frame(body, bg=C["bg"])
    cf.pack(fill="x", padx=20, pady=(0, 20))

    import matplotlib.dates as mdates
    fig = plt.Figure(figsize=(12, 3.5), facecolor=C["bg"])
    ax  = fig.add_subplot(111)
    ax.set_facecolor(C["surface"])

    ax.plot(dates, ctl, color=C["blue"],  linewidth=1.4, label="CTL (Fitness)")
    ax.plot(dates, atl, color=C["red"],   linewidth=1.0,
            linestyle="--", label="ATL (Fatica)")
    ax.plot(dates, tsb, color=C["green"], linewidth=1.0,
            linestyle=":",  label="TSB (Forma)")
    ax.axhline(0, color=C["border"], linewidth=0.6)

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %y"))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    fig.autofmt_xdate(rotation=35, ha="right")
    ax.tick_params(colors=C["text_dim"], labelsize=7)
    ax.set_ylabel("TRIMP", fontsize=7, color=C["text_dim"])
    for sp in ax.spines.values():
        sp.set_edgecolor(C["border"])
    ax.grid(color=C["border"], linestyle="--", linewidth=0.4, alpha=0.5)
    fig.subplots_adjust(left=0.06, right=0.98, top=0.92, bottom=0.22)

    cnv = FigureCanvasTkAgg(fig, master=cf)
    cnv.draw()
    cnv.get_tk_widget().pack(fill="x")


# ── Testo informativo — Carico di allenamento ─────────────────────────────────

_INFO_TRAINING_LOAD = """
## IL MODELLO PMC — Performance Management Chart

Questo grafico usa il modello di Banister (1991), adottato da TrainingPeaks, Garmin, WKO e dai coach professionisti di tutto il mondo. Si basa sul calcolo del TRIMP (TRaining IMPulse) di ogni sessione, una misura che combina durata e intensità cardiaca.

# COME VIENE CALCOLATO IL TRIMP

Per ogni corsa:  TRIMP = durata (min) × (FC_media − FC_riposo) / (FC_max − FC_riposo) × fattore

Il fattore esponenziale (Banister) amplifica le sessioni ad alta FC: correre 30 minuti a frequenza cardiaca elevata vale più del doppio rispetto a correre 30 minuti a FC bassa. Quando la FC non è disponibile, viene usata la distanza in km come stima approssimativa.

---

# LE TRE LINEE DEL GRAFICO

# CTL — FITNESS (linea blu continua)

Chronic Training Load: media ponderata esponenziale degli ultimi 42 giorni. Rappresenta la tua forma fisica di base, il livello di adattamento accumulato nel tempo con la costanza negli allenamenti.

• Sale lentamente: servono settimane di lavoro regolare per alzarla.
• Scende lentamente: non crolla subito con qualche giorno di riposo.
• Un CTL alto significa che il tuo corpo è adattato a reggere grandi volumi.

# ATL — FATICA (linea rossa tratteggiata)

Acute Training Load: media ponderata esponenziale degli ultimi 7 giorni. Rappresenta la fatica accumulata di recente.

• Reagisce rapidamente: sale dopo sessioni intense, scende in pochi giorni di riposo.
• Dopo una settimana di allenamento intenso, ATL supera CTL: sei stanco ma stai costruendo.
• Dopo un tapering, ATL scende sotto CTL: sei fresco e pronto.

# TSB — FORMA (linea verde punteggiata)

Training Stress Balance = CTL − ATL. È l'indicatore chiave della tua prontezza a gareggiare o a dare il meglio.

• TSB positivo → sei riposato. Il corpo ha recuperato e puoi esprimere il potenziale accumulato.
• TSB negativo → stai accumulando fatica. Normale durante un blocco di allenamento intenso.
• TSB molto negativo (< −20) → rischio di sovrallenamento. Inserisci giorni di recupero.
• TSB molto positivo (> +20) → sei "de-allenato": se rimani fermo troppo a lungo perdi forma.

---

# COME USARLO IN PRATICA

# Prima di una gara importante

Pianifica un tapering di 10–14 giorni: riduci il volume del 30–40% mantenendo qualche stimolo di qualità. Vedrai ATL scendere e TSB salire progressivamente in territorio positivo.

Il "sweet spot" per gareggiare è TSB tra +5 e +15: abbastanza riposato da esprimersi al meglio, abbastanza allenato da avere CTL alto.

# Durante un blocco di carico

È normale avere TSB molto negativo. L'obiettivo è spingere CTL verso l'alto. Poi, con un breve recupero, ATL scende e TSB torna positivo: questo è il momento in cui si "raccoglie" il miglioramento.

# Per monitorare i progressi

Un CTL crescente nel tempo = stai migliorando la tua capacità di sopportare il lavoro. Un CTL stagnante o in calo = stai correndo troppo poco, troppo lento, o stai recuperando male.

---

NOTA DEL COACH: i valori assoluti di CTL, ATL e TSB dipendono dalla tua storia di allenamento e contano meno del trend. Non confrontare i tuoi numeri con quelli degli altri: confronta i tuoi numeri di oggi con quelli di 3, 6, 12 mesi fa. Se CTL è più alto della stessa settimana dell'anno scorso, stai progredendo.
"""
