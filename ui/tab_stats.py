# ── ui/tab_stats.py ───────────────────────────────────────────────────────────
"""
Tab statistiche globali su tutte le corse in libreria.
"""

import tkinter as tk
from config import C
from models import fmt_time, fmt_pace
from ui.widgets import StatCard, make_scrollable, section_label, no_data, clear

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib.gridspec as gridspec
    HAS_MPL = True
except ImportError:
    HAS_MPL = False


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
