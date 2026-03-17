# ── ui/tab_stats.py ───────────────────────────────────────────────────────────
"""
Global statistics tab for all runs in the library.
"""

import tkinter as tk
import math, os
from datetime import date, timedelta
from config import C
from models import fmt_time, fmt_pace
from ui.widgets import StatCard, make_scrollable, section_label, no_data, clear, info_btn
from i18n import t

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib.gridspec as gridspec
    HAS_MPL = True
except ImportError:
    HAS_MPL = False


def render(tab, storage_mgr, on_open=None):
    clear(tab)

    tk.Label(tab, text=t("stats_global_title"),
             font=("Segoe UI", 12, "bold"), fg=C["accent"],
             bg=C["surface"], pady=12).pack(fill="x")

    # Load all summaries
    try:
        all_summaries = storage_mgr.list_all()
    except Exception as e:
        no_data(tab, f"{t('error_loading_data')}\n{e}")
        return

    if not all_summaries:
        no_data(tab, t("no_runs_library"))
        return

    _, body = make_scrollable(tab)

    # ── Calculate aggregates ──────────────────────────────────────────────────
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

    # ── Main statistics ────────────────────────────────────────────────────────
    section_label(body, t("section_overview"))
    g = tk.Frame(body, bg=C["bg"])
    g.pack(fill="x", padx=20, pady=(0, 4))
    cards = [
        (t("stat_total_runs"),    f"{n_runs}",           "",          C["accent"]),
        (t("stat_total_km"),      f"{total_dist:.1f}",   "km",        C["blue"]),
        (t("stat_total_hours"),   fmt_time(total_time),  "",          C["green"]),
        (t("stat_total_elev"),    f"{total_elev:.0f}",   "m",         C["yellow"]),
        (t("stat_avg_pace_label"),fmt_pace(avg_speed),   "min/km",    C["accent2"]),
        (t("stat_hr_avg"),        f"{avg_hr:.0f}" if avg_hr else "–", "bpm", C["red"]),
    ]
    for i, (l, v, u, col) in enumerate(cards):
        StatCard(g, l, v, u, col).grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
        g.columnconfigure(i, weight=1)

    section_label(body, t("section_details"))
    g2 = tk.Frame(body, bg=C["bg"])
    g2.pack(fill="x", padx=20, pady=(0, 4))
    extra = [
        (t("stat_avg_dist"),    f"{avg_dist:.1f}",     "km",   C["text"]),
        (t("stat_longest_run"), f"{max_dist:.1f}",     "km",   C["green"]),
        (t("stat_total_calories"), f"{total_cals:.0f}","kcal", C["orange"]),
        (t("stat_km_per_week"), _avg_km_per_week(all_summaries), "km", C["purple"]),
    ]
    for i, (l, v, u, col) in enumerate(extra):
        StatCard(g2, l, v, u, col).grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
        g2.columnconfigure(i, weight=1)

    # ── Activity heatmap ──────────────────────────────────────────────────────
    if HAS_MPL:
        _render_activity_heatmap(body, all_summaries)

    # ── Athletic profile ──────────────────────────────────────────────────────
    if HAS_MPL:
        _render_athlete_radar(body, all_summaries)

    # ── Annual goal ────────────────────────────────────────────────────────────
    _render_annual_goal(body, all_summaries, storage_mgr)

    # ── Statistics per year ───────────────────────────────────────────────────
    by_year = _group_by_year(all_summaries)
    if by_year:
        section_label(body, t("section_by_year"))
        tbl = tk.Frame(body, bg=C["surface2"],
                       highlightthickness=1, highlightbackground=C["border"])
        tbl.pack(fill="x", padx=20, pady=(0, 10))
        yr_cols   = [t("col_year"), t("col_runs"), t("col_km_total"), t("col_time_total"), t("col_avg_pace"), t("col_elev")]
        yr_widths = [8, 7, 10, 11, 12, 10]
        hrow = tk.Frame(tbl, bg=C["surface"])
        hrow.pack(fill="x")
        for col, w in zip(yr_cols, yr_widths):
            tk.Label(hrow, text=col, font=("Segoe UI", 8, "bold"),
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
                tk.Label(row, text=v, font=("Segoe UI", 9), fg=col, bg=bg,
                         width=w, anchor="center", pady=7).pack(side="left", padx=3)

        # ── km per year chart ─────────────────────────────────────────────────
        if HAS_MPL and len(by_year) > 1:
            section_label(body, t("section_km_per_year"))
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
            ax1.set_title(t("chart_km_per_year"), color=C["text"], fontsize=9,
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
            ax2.set_title(t("chart_runs_per_year"), color=C["text"], fontsize=9,
                          fontweight="bold", fontfamily="monospace", pad=6)
            ax2.tick_params(colors=C["text_dim"], labelsize=7)
            ax2.set_ylabel(t("axis_n_runs"), fontsize=7, color=C["text_dim"])
            for sp in ax2.spines.values(): sp.set_edgecolor(C["border"])
            ax2.grid(axis="y", color=C["border"], linestyle="--", linewidth=0.4, alpha=0.6)
            for bar, v in zip(bars2, n_vals):
                ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                         str(v), ha="center", fontsize=6.5, color=C["text"],
                         fontfamily="monospace")

            cnv = FigureCanvasTkAgg(fig, master=cf)
            cnv.draw()
            cnv.get_tk_widget().pack(fill="x")

    # ── Statistics per month (last 12 months) ────────────────────────────────
    _render_monthly_stats(body, all_summaries)

    # ── Training load (ATL / CTL / TSB) ───────────────────────────────────────
    if HAS_MPL:
        _render_training_load(body, all_summaries)

    # ── Grade analysis ────────────────────────────────────────────────────────
    if HAS_MPL:
        _render_grade_analysis(body, storage_mgr)

    # ── Performance curve ─────────────────────────────────────────────────────
    if HAS_MPL:
        _render_performance_curve(body, storage_mgr)

    # ── Performance prediction ────────────────────────────────────────────────
    if HAS_MPL:
        _render_race_prediction(body, storage_mgr)

    # ── Distance distribution ─────────────────────────────────────────────────
    if HAS_MPL and dists:
        section_label(body, t("section_dist_distrib"))
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
        ax3.set_title(t("section_dist_distrib"), color=C["text"], fontsize=9,
                      fontweight="bold", fontfamily="monospace", pad=10)

        cnv3 = FigureCanvasTkAgg(fig3, master=cf3)
        cnv3.draw()
        cnv3.get_tk_widget().pack()

    # ── Personal records ──────────────────────────────────────────────────────
    section_label(body, t("section_personal_records"))
    rec_outer = tk.Frame(body, bg=C["surface2"],
                         highlightthickness=1, highlightbackground=C["border"])
    rec_outer.pack(fill="x", padx=20, pady=(0, 24))

    hrow = tk.Frame(rec_outer, bg=C["surface"])
    hrow.pack(fill="x")
    for col_text, w in [(t("col_distance_label"), 18), (t("col_time_label"), 10), (t("col_activity"), 34), (t("col_date_label"), 14)]:
        tk.Label(hrow, text=col_text, font=("Segoe UI", 8, "bold"),
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
        ("Half-Marathon", f"🏃 {t('pr_half_marathon')}"),
        ("Marathon",      f"🏃 {t('pr_marathon')}"),
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
            act_id    = r.get("activity_id")
        else:
            label_txt = label.replace("🏃", "  ")
            time_str  = "–"
            act_name  = t("no_data_label")
            date_str  = "–"
            act_id    = None

        widgets = []
        for v, col, w, anc in [
            (label_txt, C["accent"],   18, "w"),
            (time_str,  C["green"],    10, "center"),
            (act_name,  C["text"],     34, "w"),
            (date_str,  C["text_dim"], 14, "center"),
        ]:
            lbl = tk.Label(row, text=v, font=("Segoe UI", 9), fg=col, bg=bg,
                           width=w, anchor=anc, pady=7, padx=4)
            lbl.pack(side="left")
            widgets.append(lbl)

        if act_id and on_open:
            def _open(e, _id=act_id):
                for s in storage_mgr.list_all():
                    if s.get("strava_id") == _id:
                        on_open(s)
                        return
            for w in [row] + widgets:
                w.config(cursor="hand2")
                w.bind("<Button-1>", _open)

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
            hint = t("hint_no_efforts")
        tk.Label(rec_outer, text=hint,
                 font=("Segoe UI", 8), fg=C["text_dim"], bg=C["surface2"],
                 pady=10, wraplength=760, justify="left").pack(anchor="w", padx=16)

    # ── Race analysis and VDOT ────────────────────────────────────────────────
    if HAS_MPL:
        _render_vdot_analysis(body, all_summaries, on_open)

    # ── Recurring routes ──────────────────────────────────────────────────────
    _render_route_analysis(body, storage_mgr, on_open)


# ── Activity heatmap ──────────────────────────────────────────────────────────

def _render_activity_heatmap(body: tk.Frame, all_summaries: list):
    """GitHub-style calendar heatmap: last 52 weeks, intensity = km."""
    if not HAS_MPL:
        return
    import numpy as np
    from datetime import date as _date, timedelta
    from matplotlib.colors import LinearSegmentedColormap
    from matplotlib.patches import Rectangle

    # Build day → total km dictionary
    day_km: dict = {}
    for s in all_summaries:
        d_str = s.get("start_date", "")[:10]
        try:
            d = _date.fromisoformat(d_str)
            day_km[d] = day_km.get(d, 0) + s.get("distance", 0) / 1000
        except Exception:
            pass

    today   = _date.today()
    # Start from Monday 52 weeks ago
    start   = today - timedelta(weeks=52)
    start  -= timedelta(days=start.weekday())   # align to Monday
    N_WEEKS = 53

    max_km  = max((v for v in day_km.values()), default=1)
    cmap    = LinearSegmentedColormap.from_list(
        "hm", [C["surface"], C["accent"]], N=256)

    CELL = 1.0
    GAP  = 0.18

    section_label(body, t("section_heatmap"))
    cf = tk.Frame(body, bg=C["bg"])
    cf.pack(fill="x", padx=20, pady=(0, 20))

    fig = plt.Figure(figsize=(13, 2.4), facecolor=C["bg"])
    ax  = fig.add_subplot(111)
    ax.set_facecolor(C["bg"])
    ax.set_aspect("equal")

    month_ticks, month_labels = [], []
    prev_month = None

    for w in range(N_WEEKS):
        for d in range(7):                         # 0=Mon … 6=Sun
            day = start + timedelta(weeks=w, days=d)
            if day > today:
                continue
            km    = day_km.get(day, 0)
            intensity = min(km / max_km, 1.0) if km > 0 else 0
            color = cmap(intensity) if km > 0 else C["surface"]
            x = w * (CELL + GAP)
            y = (6 - d) * (CELL + GAP)
            ax.add_patch(Rectangle((x, y), CELL, CELL,
                                   color=color, linewidth=0, zorder=2))
        # month label on the first day of the week (Monday)
        first_day = start + timedelta(weeks=w)
        if first_day.month != prev_month and first_day <= today:
            month_ticks.append(w * (CELL + GAP) + CELL / 2)
            month_labels.append(t("months_short")[first_day.month])
            prev_month = first_day.month

    # Axes
    ax.set_xlim(-0.5, N_WEEKS * (CELL + GAP) + 0.5)
    ax.set_ylim(-0.5, 7 * (CELL + GAP) + 0.5)
    ax.set_xticks(month_ticks)
    ax.set_xticklabels(month_labels, fontsize=7, color=C["text_dim"],
                       fontfamily="monospace")
    ax.set_yticks([(6 - d) * (CELL + GAP) + CELL / 2 for d in range(7)])
    ax.set_yticklabels(t("days_short"), fontsize=6, color=C["text_dim"],
                       fontfamily="monospace")
    ax.tick_params(length=0)
    for sp in ax.spines.values():
        sp.set_visible(False)

    # Color scale legend
    sm = plt.cm.ScalarMappable(cmap=cmap,
                               norm=plt.Normalize(vmin=0, vmax=max_km))
    sm.set_array([])
    cb = fig.colorbar(sm, ax=ax, orientation="horizontal",
                      fraction=0.02, pad=0.18, aspect=40)
    cb.ax.tick_params(labelsize=6, colors=C["text_dim"])
    cb.set_label("km", fontsize=6, color=C["text_dim"])
    cb.outline.set_edgecolor(C["border"])

    # Tooltip hover
    annot = ax.annotate("", xy=(0, 0), xytext=(6, 6),
                        textcoords="offset points",
                        bbox=dict(boxstyle="round,pad=0.3", fc=C["surface"],
                                  ec=C["border"], alpha=0.92),
                        fontsize=7, color=C["text"],
                        fontfamily="monospace")
    annot.set_visible(False)

    def _on_hover(event):
        if event.inaxes != ax:
            annot.set_visible(False)
            canvas_hm.draw_idle()
            return
        col = int(event.xdata / (CELL + GAP) + 0.5) if event.xdata is not None else -1
        row = int(event.ydata / (CELL + GAP) + 0.5) if event.ydata is not None else -1
        d_idx = 6 - row
        if 0 <= col < N_WEEKS and 0 <= d_idx <= 6:
            day = start + timedelta(weeks=col, days=d_idx)
            if day <= today:
                km = day_km.get(day, 0)
                annot.xy = (col * (CELL + GAP) + CELL / 2,
                            (6 - d_idx) * (CELL + GAP) + CELL)
                km_str = f"{km:.1f} km" if km > 0 else t("heatmap_rest")
                annot.set_text(f"{day.strftime('%d %b %Y')}  {km_str}")
                annot.set_visible(True)
                canvas_hm.draw_idle()
                return
        annot.set_visible(False)
        canvas_hm.draw_idle()

    fig.subplots_adjust(left=0.05, right=0.97, top=0.88, bottom=0.18)
    canvas_hm = FigureCanvasTkAgg(fig, master=cf)
    canvas_hm.draw()
    canvas_hm.get_tk_widget().pack(fill="x")
    canvas_hm.mpl_connect("motion_notify_event", _on_hover)


# ── Athletic radar profile ────────────────────────────────────────────────────

def _render_athlete_radar(body: tk.Frame, all_summaries: list):
    """Hexagonal radar chart of the athletic profile with 6 dimensions."""
    if not HAS_MPL or not all_summaries:
        return
    from datetime import date as _date, timedelta
    import statistics

    today    = _date.today()
    cut_52w  = today - timedelta(weeks=52)
    cut_3m   = today - timedelta(days=90)
    cut_6m   = today - timedelta(days=180)

    runs = [s for s in all_summaries if s.get("distance", 0) > 0]

    # ── 1. Speed: avg pace, scale 2.0–5.0 m/s ────────────────────────────
    speeds = [s["avg_speed"] for s in runs if s.get("avg_speed", 0) > 0]
    score_speed = min(100, max(0, (sum(speeds)/len(speeds) - 2.0) / 3.0 * 100)) \
                  if speeds else 0

    # ── 2. Endurance: median distance, scale 3–42 km ─────────────────────
    dists = [s["distance"] / 1000 for s in runs]
    score_endurance = min(100, max(0,
        (statistics.median(dists) - 3) / 39 * 100)) if dists else 0

    # ── 3. Elevation: avg m↑ per km, scale 0–40 m/km ─────────────────────
    ep_km = [s["elev_gain"] / max(s["distance"] / 1000, 0.1)
             for s in runs if s.get("elev_gain", 0) > 0]
    score_elev = min(100, (sum(ep_km)/len(ep_km)) / 40 * 100) if ep_km else 0

    # ── 4. Consistency: % weeks with a run in the last 52 ────────────────
    weeks_run = {((_date.fromisoformat(s["start_date"][:10]) - cut_52w).days // 7)
                 for s in runs
                 if s.get("start_date", "")[:10] >= cut_52w.isoformat()
                 and _date.fromisoformat(s["start_date"][:10]) <= today}
    score_consistency = min(100, len(weeks_run) / 52 * 100)

    # ── 5. Volume: avg km/week in the last 52 weeks, scale 0–70 ──────────
    recent_runs = [s for s in runs
                   if s.get("start_date", "")[:10] >= cut_52w.isoformat()]
    avg_km_w = sum(s["distance"]/1000 for s in recent_runs) / 52 if recent_runs else 0
    score_volume = min(100, avg_km_w / 70 * 100)

    # ── 6. Progression: avg pace last 3m vs previous 3m ─────────────────
    sp_rec  = [s["avg_speed"] for s in runs
               if s.get("start_date", "")[:10] >= cut_3m.isoformat()
               and s.get("avg_speed", 0) > 0]
    sp_prev = [s["avg_speed"] for s in runs
               if cut_6m.isoformat() <= s.get("start_date","")[:10] < cut_3m.isoformat()
               and s.get("avg_speed", 0) > 0]
    if sp_rec and sp_prev:
        ratio = (sum(sp_rec)/len(sp_rec)) / (sum(sp_prev)/len(sp_prev))
        score_progress = min(100, max(0, (ratio - 0.9) / 0.2 * 100))
    else:
        score_progress = 50   # insufficient data → neutral

    labels  = [t("radar_speed"), t("radar_endurance"), t("radar_elevation"),
               t("radar_consistency"), t("radar_volume"), t("radar_progress")]
    scores  = [score_speed, score_endurance, score_elev,
               score_consistency, score_volume, score_progress]
    N = len(labels)
    angles  = [n / N * 2 * math.pi for n in range(N)]
    angles += [angles[0]]
    vals    = scores + [scores[0]]

    section_label(body, t("section_athlete_profile"))
    outer = tk.Frame(body, bg=C["bg"])
    outer.pack(fill="x", padx=20, pady=(0, 20))
    outer.columnconfigure(0, weight=2)
    outer.columnconfigure(1, weight=3)

    # ── Polar chart ───────────────────────────────────────────────────────
    cf = tk.Frame(outer, bg=C["bg"])
    cf.grid(row=0, column=0, sticky="nsew")

    fig = plt.Figure(figsize=(5, 4.2), facecolor=C["bg"])
    ax  = fig.add_subplot(111, polar=True)
    ax.set_facecolor(C["surface"])

    ax.plot(angles, vals, color=C["accent"], linewidth=2, zorder=3)
    ax.fill(angles, vals, color=C["accent"], alpha=0.20)

    ax.set_ylim(0, 100)
    ax.set_yticks([25, 50, 75, 100])
    ax.set_yticklabels(["25", "50", "75", "100"],
                       fontsize=5.5, color=C["text_dim"])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=8, color=C["text"],
                       fontfamily="monospace")
    ax.grid(color=C["border"], linestyle="--", linewidth=0.5, alpha=0.6)
    ax.spines["polar"].set_color(C["border"])
    ax.tick_params(pad=6)
    fig.subplots_adjust(left=0.08, right=0.92, top=0.92, bottom=0.08)

    cnv = FigureCanvasTkAgg(fig, master=cf)
    cnv.draw()
    cnv.get_tk_widget().pack(fill="both", expand=True)

    # ── Dimension legend ──────────────────────────────────────────────────
    leg = tk.Frame(outer, bg=C["surface2"],
                   highlightthickness=1, highlightbackground=C["border"])
    leg.grid(row=0, column=1, sticky="nsew", padx=(12, 0))

    tk.Label(leg, text=t("radar_how_calculated"),
             font=("Segoe UI", 8, "bold"), fg=C["text_dim"],
             bg=C["surface"], pady=8).pack(fill="x")

    DESCRIPTIONS = [
        (t("radar_speed"),       C["accent"],  t("radar_desc_speed")),
        (t("radar_endurance"),   C["blue"],    t("radar_desc_endurance")),
        (t("radar_elevation"),   C["yellow"],  t("radar_desc_elevation")),
        (t("radar_consistency"), C["green"],   t("radar_desc_consistency")),
        (t("radar_volume"),      C["purple"],  t("radar_desc_volume")),
        (t("radar_progress"),    C["blue"],    t("radar_desc_progress")),
    ]
    for i, (name, col, desc) in enumerate(DESCRIPTIONS):
        bg = C["surface2"] if i % 2 == 0 else C["surface"]
        row = tk.Frame(leg, bg=bg)
        row.pack(fill="x")
        score_val = scores[i]
        bar_w = max(2, int(score_val / 100 * 18))
        bar_str = "█" * bar_w + "░" * (18 - bar_w)
        tk.Label(row, text=f"  {name:<13}", font=("Segoe UI", 8, "bold"),
                 fg=col, bg=bg, anchor="w", pady=6).pack(side="left")
        tk.Label(row, text=f"{score_val:5.0f}  ", font=("Segoe UI", 8),
                 fg=C["text"], bg=bg).pack(side="left")
        tk.Label(row, text=bar_str, font=("Courier", 7),  # monospace for █░ block-char alignment
                 fg=col, bg=bg).pack(side="left")

    # Extended descriptions
    detail = tk.Frame(leg, bg=C["surface2"])
    detail.pack(fill="x", padx=8, pady=(4, 8))
    for name, col, desc in DESCRIPTIONS:
        tk.Label(detail, text=f"▸ {name}: {desc}",
                 font=("Segoe UI", 7), fg=C["text_dim"], bg=C["surface2"],
                 anchor="w", justify="left", wraplength=380).pack(
                     fill="x", pady=1)


# ── VDOT helpers ──────────────────────────────────────────────────────────────

def _calc_vdot(distance_m: float, time_s: float) -> float:
    """Calculates VDOT (Jack Daniels formula) from distance (m) and time (s)."""
    t_min = time_s / 60          # minutes
    v = distance_m / t_min       # m/min
    vo2  = -4.60 + 0.182258 * v + 0.000104 * v * v
    pct  = (0.8 + 0.1894393 * math.exp(-0.012778 * t_min)
                + 0.2989558 * math.exp(-0.1932605 * t_min))
    return vo2 / pct if pct > 0 else 0.0


def _predict_time(vdot: float, distance_m: float) -> float:
    """Predicts the time (seconds) for a given distance given the VDOT."""
    lo, hi = distance_m / 10.0, distance_m * 3.0
    for _ in range(64):
        mid = (lo + hi) / 2
        if _calc_vdot(distance_m, mid) > vdot:
            lo = mid   # too fast → extend
        else:
            hi = mid   # too slow → shorten
    return (lo + hi) / 2


def _render_vdot_analysis(body: tk.Frame, all_summaries: list, on_open=None):
    """'Race Analysis and VDOT' section with evolution chart and predictions table."""
    import datetime as dt

    races = [s for s in all_summaries
             if s.get("workout_type") == 1
             and s.get("distance", 0) >= 1000
             and s.get("moving_time", 0) > 60]
    if not races:
        return

    races.sort(key=lambda s: s.get("start_date", ""))

    race_data = []
    for s in races:
        v = _calc_vdot(s["distance"], s["moving_time"])
        if v > 20:   # discard implausible values
            race_data.append({**s, "vdot": round(v, 1)})
    if not race_data:
        return

    section_label(body, t("section_vdot"))

    hdr_f = tk.Frame(body, bg=C["bg"])
    hdr_f.pack(fill="x", padx=20, pady=(0, 4))
    info_btn(hdr_f, t("section_vdot"),
             t("info_vdot")).pack(side="right", padx=4)

    best   = max(race_data, key=lambda r: r["vdot"])
    latest = race_data[-1]

    # ── Stat card ─────────────────────────────────────────────────────────────
    g = tk.Frame(body, bg=C["bg"])
    g.pack(fill="x", padx=20, pady=(0, 4))
    cards = [
        (t("vdot_total_races"), str(len(race_data)),     "",   C["accent"]),
        (t("vdot_best"),        f"{best['vdot']:.1f}",   "",   C["green"]),
        (t("vdot_recent"),      f"{latest['vdot']:.1f}", "",   C["blue"]),
    ]
    for i, (l, v, u, col) in enumerate(cards):
        StatCard(g, l, v, u, col).grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
        g.columnconfigure(i, weight=1)

    # ── VDOT over time chart ──────────────────────────────────────────────
    if len(race_data) >= 2:
        cf = tk.Frame(body, bg=C["bg"])
        cf.pack(fill="x", padx=20, pady=(0, 8))

        dates = [dt.datetime.fromisoformat(r["start_date"][:10]) for r in race_data]
        vdots = [r["vdot"] for r in race_data]

        fig = plt.Figure(figsize=(12, 3), facecolor=C["bg"])
        ax  = fig.add_subplot(111)
        ax.set_facecolor(C["surface"])
        ax.plot(dates, vdots, color=C["blue"], linewidth=1.4,
                marker="o", markersize=5, zorder=3)
        ax.axhline(best["vdot"], color=C["green"], linewidth=0.8,
                   linestyle="--", alpha=0.55, label=f"Best {best['vdot']:.1f}")
        ax.set_title(t("vdot_evolution"), color=C["text"], fontsize=9,
                     fontweight="bold", fontfamily="monospace", pad=6)
        ax.tick_params(colors=C["text_dim"], labelsize=7)
        ax.set_ylabel("VDOT", fontsize=7, color=C["text_dim"])
        for sp in ax.spines.values():
            sp.set_edgecolor(C["border"])
        ax.grid(axis="y", color=C["border"], linestyle="--", linewidth=0.4, alpha=0.6)
        fig.autofmt_xdate(rotation=30, ha="right")

        cnv = FigureCanvasTkAgg(fig, master=cf)
        cnv.draw()
        cnv.get_tk_widget().pack(fill="x")

    # ── Two-column layout: race table | predictions ────────────────────────
    two = tk.Frame(body, bg=C["bg"])
    two.pack(fill="x", padx=20, pady=(0, 20))
    two.columnconfigure(0, weight=3)
    two.columnconfigure(1, weight=2)

    # Race table (left) with pagination
    PAGE_SIZE = 10
    races_rev = list(reversed(race_data))
    n_pages   = max(1, math.ceil(len(races_rev) / PAGE_SIZE))
    page_var  = [0]   # current page index (mutable via list)

    tbl_outer = tk.Frame(two, bg=C["surface2"],
                         highlightthickness=1, highlightbackground=C["border"])
    tbl_outer.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

    # Fixed column header
    hrow = tk.Frame(tbl_outer, bg=C["surface"])
    hrow.pack(fill="x")
    for col_text, w in [(t("col_date_label"), 12), ("KM", 9), (t("col_time_label"), 10), ("VDOT", 7), (t("col_race"), 22)]:
        tk.Label(hrow, text=col_text, font=("Segoe UI", 8, "bold"),
                 fg=C["text_dim"], bg=C["surface"],
                 width=w, anchor="center", pady=6).pack(side="left", padx=2)

    # Row area (recreated on each page change)
    rows_frame = tk.Frame(tbl_outer, bg=C["surface2"])
    rows_frame.pack(fill="x")

    # Pagination bar at the bottom
    nav = tk.Frame(tbl_outer, bg=C["surface"])
    nav.pack(fill="x")
    lbl_page = tk.Label(nav, text="", font=("Segoe UI", 8), fg=C["text_dim"],
                        bg=C["surface"])
    lbl_page.pack(side="left", padx=8)
    btn_next = tk.Button(nav, text="▶", font=("Segoe UI", 8),
                         fg=C["text"], bg=C["surface2"], relief="flat",
                         bd=0, padx=6, pady=3)
    btn_next.pack(side="right", padx=4)
    btn_prev = tk.Button(nav, text="◀", font=("Segoe UI", 8),
                         fg=C["text"], bg=C["surface2"], relief="flat",
                         bd=0, padx=6, pady=3)
    btn_prev.pack(side="right", padx=2)

    def _draw_page():
        for w in rows_frame.winfo_children():
            w.destroy()
        p   = page_var[0]
        sub = races_rev[p * PAGE_SIZE : (p + 1) * PAGE_SIZE]
        for i, r in enumerate(sub):
            bg = C["surface2"] if i % 2 == 0 else C["surface"]
            row = tk.Frame(rows_frame, bg=bg)
            row.pack(fill="x")
            dist_km = r["distance"] / 1000
            for v, col, w, anc in [
                (r["start_date"][:10],       C["text_dim"], 12, "center"),
                (f"{dist_km:.1f}",           C["blue"],      9, "center"),
                (fmt_time(r["moving_time"]), C["text"],     10, "center"),
                (str(r["vdot"]),             C["green"],     7, "center"),
                ((r["name"] or "–")[:22],    C["text"],     22, "w"),
            ]:
                tk.Label(row, text=v, font=("Segoe UI", 9), fg=col, bg=bg,
                         width=w, anchor=anc, pady=5, padx=2).pack(side="left")
            if on_open:
                def _open(e, s=r):
                    on_open(s)
                row.bind("<Button-1>", _open)
                for child in row.winfo_children():
                    child.config(cursor="hand2")
                    child.bind("<Button-1>", _open)
        lbl_page.config(text=t("page_label").format(cur=p + 1, tot=n_pages))
        btn_prev.config(state="normal" if p > 0 else "disabled")
        btn_next.config(state="normal" if p < n_pages - 1 else "disabled")

    def _prev():
        page_var[0] -= 1
        _draw_page()

    def _next():
        page_var[0] += 1
        _draw_page()

    btn_prev.config(command=_prev)
    btn_next.config(command=_next)
    _draw_page()

    # Predictions table (right) based on most recent VDOT
    pred_vdot = latest["vdot"]
    prd = tk.Frame(two, bg=C["surface2"],
                   highlightthickness=1, highlightbackground=C["border"])
    prd.grid(row=0, column=1, sticky="nsew")

    tk.Label(prd, text=f"{t('vdot_predictions')}  (VDOT {pred_vdot:.1f})",
             font=("Segoe UI", 8, "bold"), fg=C["text_dim"], bg=C["surface"],
             pady=6).pack(fill="x")
    tk.Label(prd, text=f"  {t('vdot_from')} {latest['name'][:30]}",
             font=("Segoe UI", 7), fg=C["text_dim"], bg=C["surface"],
             pady=2).pack(fill="x")

    PRED_DIST = [
        ("1 km",               1000),
        ("5 km",               5000),
        ("10 km",             10000),
        (t("vdot_half"),      21097),
        (t("vdot_marathon"),  42195),
    ]
    for i, (label, dist) in enumerate(PRED_DIST):
        bg = C["surface2"] if i % 2 == 0 else C["surface"]
        pred_t = int(_predict_time(pred_vdot, dist))
        ms = dist / pred_t if pred_t > 0 else 0
        row = tk.Frame(prd, bg=bg)
        row.pack(fill="x", padx=4)
        tk.Label(row, text=label, font=("Segoe UI", 9), fg=C["accent"],
                 bg=bg, width=10, anchor="w", pady=5, padx=4).pack(side="left")
        tk.Label(row, text=fmt_time(pred_t), font=("Segoe UI", 9, "bold"),
                 fg=C["green"], bg=bg, width=9, anchor="center").pack(side="left")
        tk.Label(row, text=f"{fmt_pace(ms)}/km", font=("Segoe UI", 8),
                 fg=C["text_dim"], bg=bg, anchor="w").pack(side="left")


# ── Geocoding helpers ─────────────────────────────────────────────────────────

def _reverse_geocode(lat: float, lon: float, storage_mgr) -> str:
    """Reverse geocoding with Nominatim. Cache on MongoDB or JSON file."""
    cached = storage_mgr.get_geocode(lat, lon)
    if cached is not None:
        return cached
    try:
        import urllib.request, json as _json
        url = (f"https://nominatim.openstreetmap.org/reverse"
               f"?lat={lat}&lon={lon}&format=json&zoom=10")
        req = urllib.request.Request(url, headers={"User-Agent": "StravaViewer/1.0"})
        with urllib.request.urlopen(req, timeout=5) as r:
            resp = r.read()
            print(f"[geocode] {lat:.3f},{lon:.3f} → HTTP {r.status}")
            addr = _json.loads(resp).get("address", {})
        city = (addr.get("city") or addr.get("town") or
                addr.get("village") or addr.get("municipality") or "")
        print(f"[geocode] city found: '{city}'")
    except Exception as e:
        print(f"[geocode] ERRORE {lat:.3f},{lon:.3f}: {type(e).__name__}: {e}")
        city = ""
    if city:  # save only if found, so failures can be retried
        storage_mgr.set_geocode(lat, lon, city)
    return city


def _get_group_location(group: list, storage_mgr) -> str:
    """Returns the city for the group: first from Strava metadata, then via Nominatim."""
    from collections import Counter
    cities = Counter(s.get("city", "") for s in group if s.get("city"))
    if cities:
        return cities.most_common(1)[0][0]
    for s in group:
        lat, lon = s.get("start_lat"), s.get("start_lon")
        if lat and lon:
            return _reverse_geocode(lat, lon, storage_mgr)
    return ""


def _group_immediate_location(group: list, storage_mgr) -> tuple[str, bool]:
    """
    Returns (location_text, is_definitive).
    Definitive=True → no thread needed.
    Definitive=False → show placeholder and start geocoding in background.
    """
    from collections import Counter

    # 1. City from Strava metadata
    cities = Counter(s.get("city", "") for s in group if s.get("city"))
    if cities:
        return cities.most_common(1)[0][0], True

    # 2. Find first valid coordinates
    lat, lon = None, None
    for s in group:
        slat, slon = s.get("start_lat"), s.get("start_lon")
        if slat and slon:
            lat, lon = slat, slon
            break

    if lat is None:
        return "", True

    ew = "E" if lon >= 0 else "O"
    coord_str = f"{lat:.2f}°N  {abs(lon):.2f}°{ew}"

    # 3. Check persistent cache
    cached = storage_mgr.get_geocode(lat, lon)
    if cached:          # non-empty string → city found
        return cached, True

    # 4. Not in cache (or old empty failure) → coordinates as placeholder, start thread
    return coord_str, False


# ── Recurring routes ──────────────────────────────────────────────────────────

def _render_route_analysis(body, storage_mgr, on_open):
    section_label(body, t("section_recurring_routes"))

    try:
        groups = storage_mgr.get_route_groups(min_runs=3)
    except Exception:
        groups = []

    if not groups:
        tk.Label(body, text=t("recurring_none"),
                 font=("Segoe UI", 9), fg=C["text_dim"], bg=C["bg"],
                 pady=12).pack(anchor="w", padx=20)
        return

    outer = tk.Frame(body, bg=C["bg"])
    outer.pack(fill="x", padx=20, pady=(0, 24))

    # ── Left list panel ───────────────────────────────────────────────────────
    list_panel = tk.Frame(outer, bg=C["surface2"],
                          highlightthickness=1, highlightbackground=C["border"],
                          width=230)
    list_panel.pack(side="left", fill="y", padx=(0, 10))
    list_panel.pack_propagate(False)

    tk.Label(list_panel, text=f"  {t('recurring_routes_count').format(n=len(groups))}",
             font=("Segoe UI", 8), fg=C["text_dim"], bg=C["surface2"],
             pady=6, anchor="w").pack(fill="x")
    tk.Frame(list_panel, bg=C["border"], height=1).pack(fill="x")

    list_canvas = tk.Canvas(list_panel, bg=C["surface2"], bd=0,
                            highlightthickness=0)
    list_sb = tk.Scrollbar(list_panel, orient="vertical",
                            command=list_canvas.yview)
    list_canvas.configure(yscrollcommand=list_sb.set)
    list_sb.pack(side="right", fill="y")
    list_canvas.pack(fill="both", expand=True)
    list_inner = tk.Frame(list_canvas, bg=C["surface2"])
    _lwid = list_canvas.create_window((0, 0), window=list_inner, anchor="nw")
    list_inner.bind("<Configure>",
                    lambda e: list_canvas.configure(
                        scrollregion=list_canvas.bbox("all")))
    list_canvas.bind("<Configure>",
                     lambda e: list_canvas.itemconfig(_lwid, width=e.width))

    # ── Right panel: chart ────────────────────────────────────────────────────
    chart_panel = tk.Frame(outer, bg=C["surface2"],
                           highlightthickness=1, highlightbackground=C["border"])
    chart_panel.pack(side="left", fill="both", expand=True)

    tk.Label(chart_panel,
             text=t("recurring_select_hint"),
             font=("Segoe UI", 10), fg=C["text_dim"], bg=C["surface2"],
             pady=60).pack(expand=True)

    # ── tkinter-safe queue for thread updates ─────────────────────────────────
    import queue, threading
    loc_queue: queue.Queue = queue.Queue()

    def _poll_queue():
        try:
            while True:
                btn_ref, new_text = loc_queue.get_nowait()
                try:
                    btn_ref.config(text=new_text)
                except Exception:
                    pass
        except queue.Empty:
            pass
        try:
            list_inner.after(300, _poll_queue)
        except Exception:
            pass

    list_inner.after(300, _poll_queue)

    # ── List buttons ──────────────────────────────────────────────────────────
    selected = {"btn": None}

    def _select(group, btn):
        if selected["btn"]:
            selected["btn"].config(bg=C["surface2"], fg=C["text"])
        btn.config(bg=C["accent"], fg="white")
        selected["btn"] = btn
        for w in chart_panel.winfo_children():
            w.destroy()
        _draw_route_chart(chart_panel, group, on_open, storage_mgr)

    pending = []   # groups that need geocoding
    for i, group in enumerate(groups):
        from collections import Counter
        dist_km  = group[0].get("distance", 0) / 1000
        n        = len(group)
        names    = Counter(s.get("name", "") for s in group)
        top_name = names.most_common(1)[0][0] or f"{dist_km:.1f} km"
        dates    = [s.get("start_date", "")[:10] for s in group if s.get("start_date")]
        span     = f"{min(dates)[:7]} → {max(dates)[:7]}" if dates else ""

        location, is_final = _group_immediate_location(group, storage_mgr)
        loc_line = f"\n   📍 {location}" if location else ""
        label    = f"🔁 {top_name[:24]}\n   {dist_km:.1f} km · {n} {t('unit_runs')}\n   {span}{loc_line}"

        bg = C["surface"] if i % 2 == 0 else C["surface2"]
        btn = tk.Button(list_inner, text=label, font=("Segoe UI", 8),
                        bg=bg, fg=C["text"], bd=0, padx=8, pady=6,
                        anchor="w", justify="left", cursor="hand2",
                        wraplength=200)
        btn.pack(fill="x", pady=1)
        btn.config(command=lambda g=group, b=btn: _select(g, b))

        # Queue groups that need geocoding
        if not is_final:
            pending.append((btn, group, top_name, dist_km, n, span))

    # Single sequential thread — respects Nominatim rate limit (1 req/sec)
    if pending:
        def _geocode_all(items, q, sm):
            import time
            for b, g, top, dkm, n, sp in items:
                loc = _get_group_location(g, sm)
                if loc:  # update only if found, otherwise coordinates remain
                    ll = f"\n   📍 {loc}"
                    q.put((b, f"🔁 {top[:24]}\n   {dkm:.1f} km · {n} {t('unit_runs')}\n   {sp}{ll}"))
                time.sleep(1.1)  # respect Nominatim rate limit
        threading.Thread(target=_geocode_all,
                         args=(pending, loc_queue, storage_mgr),
                         daemon=True).start()

    # Auto-select the first group
    if list_inner.winfo_children():
        first_btn = list_inner.winfo_children()[0]
        first_btn.after(100, lambda: _select(groups[0], first_btn))


def _draw_route_chart(frame, group, on_open, storage_mgr=None):
    from collections import Counter
    import datetime as dt

    dist_km  = group[0].get("distance", 0) / 1000
    names    = Counter(s.get("name", "") for s in group)
    top_name = names.most_common(1)[0][0] or f"{dist_km:.1f} km"
    location = _get_group_location(group, storage_mgr) if storage_mgr else ""

    # Data for the chart
    dates, paces, hrs, runs = [], [], [], []
    for s in group:
        spd = s.get("avg_speed", 0)
        if spd <= 0:
            continue
        pace_min = (1000 / spd) / 60           # min/km
        date_str = s.get("start_date", "")[:10]
        try:
            d = dt.date.fromisoformat(date_str)
        except Exception:
            continue
        dates.append(d)
        paces.append(pace_min)
        hrs.append(s.get("avg_hr") or 0)
        runs.append(s)

    if not dates or not HAS_MPL:
        tk.Label(frame, text=t("insufficient_data"),
                 font=("Segoe UI", 9), fg=C["text_dim"], bg=C["surface2"]).pack(pady=20)
        return

    # ── Stats header ──────────────────────────────────────────────────────────
    hdr = tk.Frame(frame, bg=C["surface"])
    hdr.pack(fill="x", padx=0)

    best_pace  = min(paces)
    avg_pace   = sum(paces) / len(paces)
    first_pace = paces[0]
    last_pace  = paces[-1]
    trend_sec  = (first_pace - last_pace) * 60   # positive = improved

    def _fmt_p(p):
        m = int(p); s = int((p - m) * 60)
        return f"{m}:{s:02d}"

    trend_txt = (t("trend_improved").format(sec=f"{abs(trend_sec):.0f}")
                 if trend_sec > 5 else
                 t("trend_worsened").format(sec=f"{abs(trend_sec):.0f}")
                 if trend_sec < -5 else t("trend_stable"))
    trend_col = C["green"] if trend_sec > 5 else C["red"] if trend_sec < -5 else C["text_dim"]

    loc_txt = f"  📍 {location}" if location else ""
    for txt, col, side in [
        (f"  {top_name[:40]}  —  {dist_km:.1f} km  ·  {len(dates)} {t('unit_runs')}{loc_txt}",
         C["text"], "left"),
        (f"{t('best_pace_label')} {_fmt_p(best_pace)}/km    "
         f"{t('avg_pace_label')} {_fmt_p(avg_pace)}/km    {trend_txt}  ",
         trend_col, "right"),
    ]:
        tk.Label(hdr, text=txt, font=("Segoe UI", 9), fg=col,
                 bg=C["surface"], pady=6).pack(side=side, padx=12)

    if storage_mgr:
        map_btn = tk.Button(
            hdr, text=t("btn_map"), font=("Segoe UI", 10),
            fg=C["accent"], bg=C["surface"], relief="flat",
            cursor="hand2", bd=0,
            command=lambda g=group, sm=storage_mgr: _open_group_map(g, sm),
        )
        map_btn.pack(side="right", padx=6)

    # ── Matplotlib chart ──────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(7, 3.2), facecolor=C["surface2"])
    ax.set_facecolor(C["surface2"])

    # Colored scatter: green=fast, red=slow
    norm_paces = [(p - best_pace) / (max(paces) - best_pace + 0.001) for p in paces]
    colors = [plt.cm.RdYlGn(1 - v) for v in norm_paces]  # type: ignore

    scatter_pts = ax.scatter(dates, paces, c=colors, s=60, zorder=3, edgecolors="none")

    # Trend line (simple linear regression)
    if len(dates) >= 3:
        x_num = [(d - dates[0]).days for d in dates]
        n = len(x_num)
        sx, sy = sum(x_num), sum(paces)
        sxy = sum(xi * yi for xi, yi in zip(x_num, paces))
        sxx = sum(xi ** 2 for xi in x_num)
        denom = n * sxx - sx ** 2
        if denom:
            m_coef = (n * sxy - sx * sy) / denom
            b_coef = (sy - m_coef * sx) / n
            x0, x1 = x_num[0], x_num[-1]
            ax.plot([dates[0], dates[-1]],
                    [m_coef * x0 + b_coef, m_coef * x1 + b_coef],
                    color=C["accent"], linewidth=1.5, linestyle="--",
                    alpha=0.7, zorder=2)

    # Highlight best and last
    best_idx = paces.index(best_pace)
    ax.scatter([dates[best_idx]], [best_pace], s=120, color=C["green"],
               zorder=4, edgecolors="white", linewidths=1.2, label=t("best_run"))
    ax.scatter([dates[-1]], [paces[-1]], s=100, color=C["accent"],
               zorder=4, edgecolors="white", linewidths=1.2, label=t("last_run"))

    # Inverted Y axis: lower pace = faster = at top
    ax.invert_yaxis()

    def _ytick(p, _):
        m = int(p); s = int((p - m) * 60)
        return f"{m}:{s:02d}"

    import matplotlib.ticker as mticker
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(_ytick))
    ax.set_ylabel(t("axis_pace_minkm"), color=C["text_dim"], fontsize=8)
    ax.tick_params(colors=C["text_dim"], labelsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor(C["border"])
    ax.grid(axis="y", color=C["border"], linewidth=0.5, alpha=0.6)
    ax.legend(fontsize=7, facecolor=C["surface"], edgecolor=C["border"],
              labelcolor=C["text_dim"])
    fig.autofmt_xdate(rotation=30, ha="right")
    fig.tight_layout(pad=1.2)

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=0, pady=0)

    # ── Hover tooltip on data points ──────────────────────────────────────────
    annot = ax.annotate(
        "", xy=(0, 0), xytext=(12, 12), textcoords="offset points",
        bbox=dict(boxstyle="round,pad=0.45", fc=C["surface"], ec=C["border"],
                  alpha=0.95, linewidth=1),
        fontsize=8, color=C["text"],
        arrowprops=dict(arrowstyle="->", color=C["border"], lw=0.8),
        zorder=10,
    )
    annot.set_visible(False)

    # additional scatter to highlight hovered point
    highlight, = ax.plot([], [], "o", ms=11, color="white", alpha=0.5,
                         zorder=5, markeredgewidth=0)

    def _on_hover(event):
        if event.inaxes != ax:
            if annot.get_visible():
                annot.set_visible(False)
                highlight.set_data([], [])
                canvas.draw_idle()
            return
        cont, ind = scatter_pts.contains(event)
        if cont:
            idx  = ind["ind"][0]
            run  = runs[idx]
            x, y = scatter_pts.get_offsets()[idx]
            annot.xy = (x, y)
            name  = run.get("name", "")
            date  = (run.get("start_date") or "")[:10]
            dist  = f"{run.get('distance', 0) / 1000:.1f} km"
            elev  = run.get("elev_gain", 0)
            pace_s = _fmt_p(paces[idx])
            lines = [f"{date}  {name[:32]}" if name else date,
                     f"{dist}   \u2191{elev:.0f} m   {pace_s}/km"]
            annot.set_text("\n".join(lines))
            annot.set_visible(True)
            highlight.set_data([x], [y])
            canvas.draw_idle()
        else:
            if annot.get_visible():
                annot.set_visible(False)
                highlight.set_data([], [])
                canvas.draw_idle()

    canvas.mpl_connect("motion_notify_event", _on_hover)

    plt.close(fig)

    # ── Group run list (clickable if on_open) ─────────────────────────────────
    runs_frame = tk.Frame(frame, bg=C["surface2"], height=130)
    runs_frame.pack(fill="x", padx=0)
    runs_frame.pack_propagate(False)
    tk.Frame(runs_frame, bg=C["border"], height=1).pack(fill="x")

    sc = tk.Canvas(runs_frame, bg=C["surface2"], bd=0, highlightthickness=0)
    sb = tk.Scrollbar(runs_frame, orient="vertical", command=sc.yview)
    sc.configure(yscrollcommand=sb.set)
    sb.pack(side="right", fill="y")
    sc.pack(fill="both", expand=True)
    sub = tk.Frame(sc, bg=C["surface2"])
    wid = sc.create_window((0, 0), window=sub, anchor="nw")
    sub.bind("<Configure>", lambda e: sc.configure(scrollregion=sc.bbox("all")))
    sc.bind("<Configure>", lambda e: sc.itemconfig(wid, width=e.width))
    sc.bind("<MouseWheel>", lambda e: sc.yview_scroll(int(-1*(e.delta/120)), "units"))

    for s, pace in sorted(zip(runs, paces), key=lambda x: x[0].get("start_date", ""), reverse=True):
        date_s = s.get("start_date", "")[:10]
        dist_s = f"{s.get('distance', 0) / 1000:.2f} km"
        hr_s   = f"  ❤ {s['avg_hr']:.0f}" if s.get("avg_hr") else ""
        line   = f"{date_s}   {dist_s}   {_fmt_p(pace)}/km{hr_s}   {s.get('name','')[:35]}"
        fg_col = C["green"] if pace == best_pace else C["text_dim"]
        lbl = tk.Label(sub, text=line, font=("Segoe UI", 8), fg=fg_col,
                       bg=C["surface2"], anchor="w", cursor="hand2" if on_open else "")
        lbl.pack(fill="x", padx=12, pady=1)
        if on_open:
            lbl.bind("<Button-1>", lambda e, _s=s: _open_run(on_open, _s))


def _open_run(on_open, summary):
    on_open(summary)


def _open_group_map(group: list, storage_mgr):
    """Opens a Folium map in the browser with all group tracks overlaid."""
    try:
        import folium
        from folium.plugins import Fullscreen
        import tempfile, webbrowser, os
    except ImportError:
        import tkinter.messagebox as mb
        mb.showerror("Folium not found",
                     "Please install folium with: pip install folium")
        return

    tracks = storage_mgr.get_group_polylines(group)
    if not tracks:
        import tkinter.messagebox as mb
        mb.showinfo("GPS", t("msg_no_gps_tracks"))
        return

    # Map center = average of all points
    all_pts = [pt for _, _, pts in tracks for pt in pts]
    center_lat = sum(p[0] for p in all_pts) / len(all_pts)
    center_lon = sum(p[1] for p in all_pts) / len(all_pts)

    m = folium.Map(location=[center_lat, center_lon], zoom_start=13, tiles=None)

    # ── Layer tiles ───────────────────────────────────────────────────────────
    folium.TileLayer("CartoDB positron", name=t("map_tile_light"), show=True).add_to(m)
    folium.TileLayer("OpenStreetMap",    name="OpenStreetMap", show=False).add_to(m)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri World Imagery", name="Satellite", show=False,
    ).add_to(m)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}",
        attr="Esri World Topo", name=t("map_tile_topo"), show=False,
    ).add_to(m)

    # ── Fullscreen plugin ─────────────────────────────────────────────────────
    Fullscreen(position="topleft", title=t("map_fullscreen"), title_cancel=t("map_fullscreen_exit")).add_to(m)

    # ── Group statistics lookup (match by date) ───────────────────────────────
    stats_by_date = {}
    for s in group:
        d = (s.get("start_date") or s.get("start_date_local") or "")[:10]
        if d:
            stats_by_date[d] = s

    def _fmt_time(sec):
        sec = int(sec or 0)
        h, m = divmod(sec, 3600)
        m, s = divmod(m, 60)
        return f"{h}h {m:02d}m" if h else f"{m}m {s:02d}s"

    def _fmt_pace(spd):
        if not spd or spd <= 0:
            return "—"
        p = (1000 / spd) / 60
        return f"{int(p)}:{int((p % 1) * 60):02d}/km"

    def _build_tooltip(name, date_s, stats):
        dist  = stats.get("distance", 0) / 1000
        time  = _fmt_time(stats.get("moving_time", 0))
        elev  = stats.get("elev_gain", 0)
        pace  = _fmt_pace(stats.get("avg_speed", 0))
        title = f"<b>{date_s}</b>" + (f" · {name[:40]}" if name else "")
        rows  = (f"📏 {dist:.2f} km&nbsp;&nbsp;&nbsp;"
                 f"⏱ {time}&nbsp;&nbsp;&nbsp;"
                 f"📈 +{elev:.0f} m&nbsp;&nbsp;&nbsp;"
                 f"🏃 {pace}")
        return f'{title}<br><span style="font-size:12px">{rows}</span>'

    # ── Tracks sorted by date: one FeatureGroup per run ───────────────────────
    colors = ["#e63946", "#457b9d", "#2a9d8f", "#e9c46a", "#f4a261",
              "#264653", "#8ecae6", "#c77dff", "#ffb703", "#fb8500"]

    sorted_tracks = sorted(tracks, key=lambda t: t[1])   # chronological order
    for i, (name, date_s, pts) in enumerate(sorted_tracks):
        col   = colors[i % len(colors)]
        label = f"{date_s} · {name[:35]}" if name else date_s
        stats    = stats_by_date.get(date_s, {})
        tip_html = _build_tooltip(name, date_s, stats)
        fg = folium.FeatureGroup(
            name=f'<span style="color:{col};font-size:16px;line-height:1">■</span>'
                 f'&nbsp;<span style="font-size:12px">{label}</span>',
            show=True,
        )
        folium.PolyLine(pts, color=col, weight=3, opacity=0.85,
                        tooltip=folium.Tooltip(tip_html, sticky=True)).add_to(fg)
        if pts:
            folium.CircleMarker(pts[0], radius=5, color=col,
                                fill=True, fill_opacity=1,
                                tooltip=folium.Tooltip(tip_html, sticky=True)).add_to(fg)
        fg.add_to(m)

    # LayerControl with HTML support (for inline colors)
    folium.LayerControl(collapsed=False, position="topright").add_to(m)

    # ── "Select all / Deselect all" checkbox ─────────────────────────────────
    master_toggle_js = """
<script>
document.addEventListener('DOMContentLoaded', function () {
    setTimeout(function () {
        var overlaysDiv = document.querySelector('.leaflet-control-layers-overlays');
        if (!overlaysDiv) return;

        // Contenitore master
        var masterDiv = document.createElement('div');
        masterDiv.style.cssText = [
            'padding:5px 8px 7px 8px',
            'margin-bottom:5px',
            'border-bottom:2px solid #bbb',
            'display:flex',
            'align-items:center',
            'gap:6px',
        ].join(';');

        var masterChk = document.createElement('input');
        masterChk.type    = 'checkbox';
        masterChk.checked = true;
        masterChk.id      = 'sv-master-toggle';
        masterChk.style.cssText = 'width:14px;height:14px;cursor:pointer;accent-color:#457b9d';

        var masterLbl = document.createElement('label');
        masterLbl.htmlFor = 'sv-master-toggle';
        masterLbl.style.cssText = 'font-weight:bold;font-size:12px;cursor:pointer;user-select:none';
        masterLbl.textContent = '__DESELECT_ALL__';

        function refreshLabel() {
            masterLbl.textContent = masterChk.checked ? '__DESELECT_ALL__' : '__SELECT_ALL__';
        }

        var isBulkToggling = false;

        masterChk.addEventListener('change', function () {
            isBulkToggling = true;
            var target = masterChk.checked;
            var boxes = overlaysDiv.querySelectorAll('input[type=checkbox]');
            boxes.forEach(function (inp) {
                if (inp !== masterChk && inp.checked !== target) inp.click();
            });
            isBulkToggling = false;
            refreshLabel();
        });

        // Update the master table if the user clicks the individual checkboxes
        overlaysDiv.addEventListener('change', function (e) {
            if (e.target === masterChk || isBulkToggling) return;
            var boxes   = overlaysDiv.querySelectorAll('input[type=checkbox]');
            var checked = Array.from(boxes).filter(function(b){ return b !== masterChk && b.checked; }).length;
            var total   = boxes.length - 1; // exclude master
            masterChk.indeterminate = (checked > 0 && checked < total);
            masterChk.checked = (checked === total);
            refreshLabel();
        });

        masterDiv.appendChild(masterChk);
        masterDiv.appendChild(masterLbl);
        overlaysDiv.insertBefore(masterDiv, overlaysDiv.firstChild);
    }, 400);
});
</script>
"""
    master_toggle_js = master_toggle_js.replace(
        "__DESELECT_ALL__", t("map_deselect_all")
    ).replace(
        "__SELECT_ALL__", t("map_select_all")
    )
    m.get_root().html.add_child(folium.Element(master_toggle_js))

    with tempfile.NamedTemporaryFile(suffix=".html", delete=False,
                                     mode="w", encoding="utf-8") as f:
        m.save(f.name)
        tmp_path = f.name

    webbrowser.open(f"file:///{tmp_path.replace(os.sep, '/')}")


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


# ── Annual goal section ───────────────────────────────────────────────────────

def _render_annual_goal(body, all_summaries, storage_mgr):
    section_label(body, t("section_annual_goal"))
    app_settings = storage_mgr.load_app_settings()
    current_year = date.today().year

    year_km = sum(
        s.get("distance", 0) for s in all_summaries
        if (s.get("start_date") or "")[:4] == str(current_year)
    ) / 1000

    target_km = app_settings.get("annual_km_goal", 1000.0)
    pct       = min(1.0, year_km / target_km) if target_km > 0 else 0.0

    outer = tk.Frame(body, bg=C["surface2"],
                     highlightthickness=1, highlightbackground=C["border"])
    outer.pack(fill="x", padx=20, pady=(0, 12))

    row_f = tk.Frame(outer, bg=C["surface2"])
    row_f.pack(fill="x", padx=16, pady=10)

    tk.Label(row_f, text=f"{t('annual_goal_label')} {current_year}:",
             font=("Segoe UI", 9), fg=C["text_dim"],
             bg=C["surface2"]).pack(side="left")

    goal_var = tk.StringVar(value=str(int(target_km)))
    tk.Entry(row_f, textvariable=goal_var, font=("Segoe UI", 10),
             bg=C["surface"], fg=C["text"], width=7, bd=0,
             insertbackground=C["text"],
             highlightthickness=1, highlightbackground=C["border"]
             ).pack(side="left", padx=6)
    tk.Label(row_f, text="km", font=("Segoe UI", 9), fg=C["text_dim"],
             bg=C["surface2"]).pack(side="left")

    def _save():
        try:
            val = float(goal_var.get())
            storage_mgr.save_app_setting("annual_km_goal", val)
        except Exception:
            pass

    tk.Button(row_f, text=t("btn_save"), font=("Segoe UI", 8, "bold"),
              bg=C["accent"], fg="white", bd=0, padx=8, pady=3,
              cursor="hand2", command=_save).pack(side="left", padx=10)

    # Summary text
    col_txt = C["green"] if pct >= 1.0 else C["accent"]
    tk.Label(row_f,
             text=f"{year_km:.0f} / {target_km:.0f} km  ({pct * 100:.1f}%)",
             font=("Segoe UI", 10, "bold"), fg=col_txt,
             bg=C["surface2"]).pack(side="right", padx=8)

    # Progress bar (Canvas)
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


# ── Monthly statistics section ────────────────────────────────────────────────

def _render_monthly_stats(body, all_summaries):
    """Table + chart of the last 12 months."""
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

    # Calculate avg_speed per month
    months_sorted = sorted(by_month.keys(), reverse=True)[:12]  # last 12 months
    months_sorted.sort()  # now in chronological order

    section_label(body, t("section_monthly"))
    tbl = tk.Frame(body, bg=C["surface2"],
                   highlightthickness=1, highlightbackground=C["border"])
    tbl.pack(fill="x", padx=20, pady=(0, 8))

    mo_cols   = [t("col_month"), t("col_runs"), t("col_km_total"), t("col_time_total"), t("col_avg_pace"), t("col_elev")]
    mo_widths = [9, 7, 10, 11, 12, 10]

    hrow = tk.Frame(tbl, bg=C["surface"])
    hrow.pack(fill="x")
    for col, w in zip(mo_cols, mo_widths):
        tk.Label(hrow, text=col, font=("Segoe UI", 8, "bold"),
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
            (f"{t('months_short')[mo]} {yr}",   C["accent"]),
            (str(d["count"]),                   C["text"]),
            (f"{d['dist_km']:.1f} km",          C["blue"]),
            (fmt_time(d["time_sec"]),            C["text"]),
            (fmt_pace(avg),                      C["green"]),
            (f"{d['elev_gain']:.0f} m",          C["yellow"]),
        ]
        for (v, col), w in zip(mo_vals, mo_widths):
            tk.Label(row, text=v, font=("Segoe UI", 9), fg=col, bg=bg,
                     width=w, anchor="center", pady=7).pack(side="left", padx=3)

    # km per month chart
    if HAS_MPL and len(months_sorted) > 1:
        cf = tk.Frame(body, bg=C["bg"])
        cf.pack(fill="x", padx=20, pady=(0, 20))

        labels   = []
        km_vals  = []
        n_vals   = []
        for ym in months_sorted:
            yr, mo = int(ym[:4]), int(ym[5:7])
            labels.append(f"{t('months_short')[mo]}\n{yr}")
            km_vals.append(by_month[ym]["dist_km"])
            n_vals.append(by_month[ym]["count"])

        fig = plt.Figure(figsize=(12, 3.5), facecolor=C["bg"])
        gs  = gridspec.GridSpec(1, 1, figure=fig,
                                left=0.05, right=0.98, top=0.82, bottom=0.18)
        ax  = fig.add_subplot(gs[0, 0])
        bars = ax.bar(range(len(labels)), km_vals, color=C["blue"],
                      alpha=0.85, width=0.6)
        ax.set_facecolor(C["surface"])
        ax.set_title(t("chart_km_per_month"), color=C["text"], fontsize=9,
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


# ── Training load section (ATL / CTL / TSB) ───────────────────────────────────

def _trimp(s: dict) -> float:
    """Simplified TRIMP for a session."""
    t_min = s.get("moving_time", 0) / 60.0
    hr    = s.get("avg_hr")
    if hr and hr > 0:
        # Banister TRIMP with hrRest=60, hrMax=190
        hr_ratio = max(0.0, min(1.0, (hr - 60) / (190 - 60)))
        return t_min * hr_ratio * 0.64 * math.exp(1.92 * hr_ratio)
    # Fallback without HR: distance in km as proxy
    return s.get("distance", 0) / 1000.0


def _compute_training_load(summaries):
    """Returns (dates, atl_list, ctl_list, tsb_list) for the last year."""
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

    # Initialize ATL/CTL on prior history (entire database)
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

    section_label(body, t("section_training_load"))

    # Text legend + info button
    leg_f = tk.Frame(body, bg=C["bg"])
    leg_f.pack(fill="x", padx=20, pady=(0, 4))
    for txt, col in [
        (f"■ {t('training_load_ctl')}", C["blue"]),
        (f"■ {t('training_load_atl')}", C["red"]),
        (f"■ {t('training_load_tsb')}", C["green"]),
    ]:
        tk.Label(leg_f, text=txt, font=("Segoe UI", 8), fg=col,
                 bg=C["bg"]).pack(side="left", padx=10)
    info_btn(leg_f, t("info_training_load_title"),
             t("info_training_load")).pack(side="right", padx=8)

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

# ── Grade Analysis section ────────────────────────────────────────────────────

_GRADE_BINS = [
    ("< −8%",    -1e9, -8,  "#4477cc"),
    ("−8 a −3%", -8,   -3,  "#66aadd"),
    ("−3 a 0%",  -3,    0,  "#55aa55"),
    ("0 a 3%",    0,    3,  "#ddaa33"),
    ("3 a 8%",    3,    8,  "#dd7722"),
    ("> 8%",      8,   1e9, "#cc3333"),
]


def _render_grade_analysis(body, storage_mgr):
    section_label(body, t("section_grade"))

    ctrl_f = tk.Frame(body, bg=C["bg"])
    ctrl_f.pack(fill="x", padx=20, pady=(0, 4))
    for label, _, _, col in _GRADE_BINS:
        tk.Label(ctrl_f, text=f"■ {label}", font=("Segoe UI", 7),
                 fg=col, bg=C["bg"]).pack(side="left", padx=6)

    def _refresh():
        try:
            db = int(days_var.get())
        except ValueError:
            db = 0
        _redraw_grade(chart_f, storage_mgr, races_var.get(), db)

    races_var = tk.BooleanVar(value=False)
    info_btn(ctrl_f, t("section_grade"),
             t("info_grade")).pack(side="right", padx=4)
    tk.Checkbutton(ctrl_f, text=t("filter_races_only"), font=("Segoe UI", 8),
                   variable=races_var, fg=C["text"], bg=C["bg"],
                   selectcolor=C["surface2"], activebackground=C["bg"],
                   command=_refresh).pack(side="right", padx=8)

    days_var = tk.StringVar(value="365")
    tk.Entry(ctrl_f, textvariable=days_var, width=5,
             font=("Segoe UI", 8), bg=C["surface2"], fg=C["text"],
             insertbackground=C["text"], relief="flat",
             highlightthickness=1, highlightbackground=C["border"]
             ).pack(side="right", padx=(0, 2))
    tk.Label(ctrl_f, text="Ultimi giorni:", font=("Segoe UI", 8),
             fg=C["text_dim"], bg=C["bg"]).pack(side="right", padx=(8, 0))
    tk.Button(ctrl_f, text="↻", font=("Segoe UI", 9, "bold"),
              bg=C["surface2"], fg=C["accent"], bd=0, padx=6, pady=2,
              cursor="hand2", command=_refresh).pack(side="right", padx=4)

    chart_f = tk.Frame(body, bg=C["bg"])
    chart_f.pack(fill="x", padx=20, pady=(0, 20))
    _redraw_grade(chart_f, storage_mgr, False, 365)


def _redraw_grade(chart_f, storage_mgr, races_only: bool, days_back: int = 0):
    for w in chart_f.winfo_children():
        w.destroy()

    from datetime import date, timedelta
    splits = storage_mgr.get_grade_splits(races_only=races_only)
    if days_back > 0:
        cutoff = (date.today() - timedelta(days=days_back)).isoformat()
        splits = [s for s in splits if (s.get("date") or "") >= cutoff]
    if not splits:
        tk.Label(chart_f, text="Nessun dato splits disponibile.",
                 font=("Segoe UI", 9), fg=C["text_dim"], bg=C["bg"]).pack(pady=20)
        return

    bin_paces: dict[str, list] = {b[0]: [] for b in _GRADE_BINS}
    for sp in splits:
        g = sp.get("grade_pct", 0)
        pace_ms = sp.get("pace_ms", 0)
        if pace_ms <= 0:
            continue
        pace_mkm = (1000.0 / pace_ms) / 60.0   # min/km
        for label, lo, hi, _ in _GRADE_BINS:
            if lo <= g < hi:
                bin_paces[label].append(pace_mkm)
                break

    valid = [(b[0], b[3], bin_paces[b[0]])
             for b in _GRADE_BINS if bin_paces[b[0]]]
    if not valid:
        tk.Label(chart_f, text="Dati insufficienti.",
                 font=("Segoe UI", 9), fg=C["text_dim"], bg=C["bg"]).pack(pady=20)
        return

    labels_v  = [v[0] for v in valid]
    colors_v  = [v[1] for v in valid]
    medians_v = [sorted(v[2])[len(v[2]) // 2] for v in valid]
    counts_v  = [len(v[2]) for v in valid]

    fig = plt.Figure(figsize=(12, 3.5), facecolor=C["bg"])
    ax  = fig.add_subplot(111)
    ax.set_facecolor(C["surface"])

    bars = ax.bar(range(len(labels_v)), medians_v,
                  color=colors_v, alpha=0.85, width=0.6)
    ax.set_xticks(range(len(labels_v)))
    ax.set_xticklabels(labels_v, fontsize=8, fontfamily="monospace")
    ax.tick_params(colors=C["text_dim"], labelsize=7)
    ax.set_ylabel(t("axis_pace_minkm"), fontsize=7, color=C["text_dim"])
    ax.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda v, _: f"{int(v)}:{int((v - int(v)) * 60):02d}"))
    period_lbl = t("period_last_days").format(n=days_back) if days_back > 0 else t("period_all_history")
    ax.set_title(f"{t('chart_grade_pace')}  [{period_lbl}]",
                 color=C["text"], fontsize=9, fontweight="bold",
                 fontfamily="monospace", pad=6)
    for sp in ax.spines.values():
        sp.set_edgecolor(C["border"])
    ax.grid(axis="y", color=C["border"], linestyle="--", linewidth=0.4, alpha=0.6)
    ax.set_ylim(0, max(medians_v) * 1.28)

    for bar, v, c in zip(bars, medians_v, counts_v):
        mn = int(v)
        sc = int((v - mn) * 60)
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.03,
                f"{mn}:{sc:02d}\n(n={c})", ha="center", fontsize=6,
                color=C["text"], fontfamily="monospace")

    fig.subplots_adjust(left=0.07, right=0.98, top=0.88, bottom=0.15)
    cnv = FigureCanvasTkAgg(fig, master=chart_f)
    cnv.draw()
    cnv.get_tk_widget().pack(fill="x")

# ── Performance curve section ─────────────────────────────────────────────────

def _render_performance_curve(body, storage_mgr):
    section_label(body, t("section_perf_curve"))

    ctrl_f = tk.Frame(body, bg=C["bg"])
    ctrl_f.pack(fill="x", padx=20, pady=(0, 4))
    tk.Label(ctrl_f, text=t("perf_curve_legend"),
             font=("Segoe UI", 8), fg=C["text_dim"], bg=C["bg"]).pack(side="left")

    def _refresh():
        try:
            db = int(days_var.get())
        except ValueError:
            db = 0
        _redraw_perf_curve(chart_f, storage_mgr, races_var.get(), db)

    races_var = tk.BooleanVar(value=False)
    info_btn(ctrl_f, t("section_perf_curve"),
             t("info_perf_curve")).pack(side="right", padx=4)
    tk.Checkbutton(ctrl_f, text=t("filter_races_only"), font=("Segoe UI", 8),
                   variable=races_var, fg=C["text"], bg=C["bg"],
                   selectcolor=C["surface2"], activebackground=C["bg"],
                   command=_refresh).pack(side="right", padx=8)

    days_var = tk.StringVar(value="365")
    tk.Entry(ctrl_f, textvariable=days_var, width=5,
             font=("Segoe UI", 8), bg=C["surface2"], fg=C["text"],
             insertbackground=C["text"], relief="flat",
             highlightthickness=1, highlightbackground=C["border"]
             ).pack(side="right", padx=(0, 2))
    tk.Label(ctrl_f, text="Ultimi giorni:", font=("Segoe UI", 8),
             fg=C["text_dim"], bg=C["bg"]).pack(side="right", padx=(8, 0))
    tk.Button(ctrl_f, text="↻", font=("Segoe UI", 9, "bold"),
              bg=C["surface2"], fg=C["accent"], bd=0, padx=6, pady=2,
              cursor="hand2", command=_refresh).pack(side="right", padx=4)

    chart_f = tk.Frame(body, bg=C["bg"])
    chart_f.pack(fill="x", padx=20, pady=(0, 20))
    _redraw_perf_curve(chart_f, storage_mgr, False, 365)


def _redraw_perf_curve(chart_f, storage_mgr, races_only: bool, days_back: int = 0):
    for w in chart_f.winfo_children():
        w.destroy()

    try:
        import numpy as np
    except ImportError:
        tk.Label(chart_f, text="numpy non installato (pip install numpy).",
                 font=("Segoe UI", 9), fg=C["text_dim"], bg=C["bg"]).pack(pady=10)
        return

    from storage import _EFFORT_DISTANCES
    from datetime import date, timedelta
    efforts = storage_mgr.get_all_best_efforts(races_only=races_only)
    if days_back > 0:
        cutoff = (date.today() - timedelta(days=days_back)).isoformat()
        efforts = [e for e in efforts if (e.get("date") or "") >= cutoff]
    if not efforts:
        tk.Label(chart_f, text="Nessun best effort trovato nel database.",
                 font=("Segoe UI", 9), fg=C["text_dim"], bg=C["bg"]).pack(pady=10)
        return

    # Best time for each canonical distance
    best: dict[str, float] = {}
    for e in efforts:
        c = e["canonical"]
        elapsed = e["elapsed_time"]
        if c not in best or elapsed < best[c]:
            best[c] = elapsed

    pts = [(dist_m, best[key])
           for key, dist_m in _EFFORT_DISTANCES.items()
           if key in best]
    if len(pts) < 2:
        tk.Label(chart_f, text="Servono almeno 2 distanze per il fit. "
                               "Scarica attività con best_efforts.",
                 font=("Segoe UI", 9), fg=C["text_dim"], bg=C["bg"],
                 wraplength=700).pack(pady=10)
        return

    pts.sort(key=lambda x: x[0])
    xs = np.array([p[0] for p in pts])
    ys = np.array([p[1] for p in pts])

    # Fit log-log: log(t) = a + b*log(d)
    log_x = np.log(xs)
    log_y = np.log(ys)
    b, a  = np.polyfit(log_x, log_y, 1)   # slope, intercept
    A     = np.exp(a)

    # Continuous curve
    x_fit  = np.logspace(np.log10(xs.min() * 0.9), np.log10(xs.max() * 1.1), 200)
    y_fit  = A * x_fit ** b

    fig = plt.Figure(figsize=(12, 4), facecolor=C["bg"])
    ax  = fig.add_subplot(111)
    ax.set_facecolor(C["surface"])

    ax.loglog(x_fit, y_fit, color=C["accent"], linewidth=1.5,
              linestyle="--", label=f"fit: t = {A:.1f}·d^{b:.2f}")
    ax.scatter(xs, ys, color=C["blue"], s=60, zorder=5, label="Best effort effettivo")

    # Point labels
    dist_labels = {v: k for k, v in _EFFORT_DISTANCES.items()}
    nice = {"400m": "400m", "half_mile": "½ mile", "1k": "1K",
            "1_mile": "1 mi", "2_mile": "2 mi", "5k": "5K",
            "10k": "10K", "Half-Marathon": "½ Mar", "Marathon": "Mar"}
    for x, y in zip(xs, ys):
        key   = dist_labels.get(x, "")
        lbl   = nice.get(key, key)
        t_sec = int(y)
        h, rem = divmod(t_sec, 3600)
        m, s   = divmod(rem, 60)
        t_str  = f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"
        ax.annotate(f"{lbl}\n{t_str}", (x, y),
                    textcoords="offset points", xytext=(6, 4),
                    fontsize=6.5, color=C["text"], fontfamily="monospace")

    ax.set_xlabel(t("axis_dist_m"), fontsize=7, color=C["text_dim"])
    ax.set_ylabel(t("axis_time_s"), fontsize=7, color=C["text_dim"])
    period_lbl = t("period_last_days").format(n=days_back) if days_back > 0 else t("period_all_history")
    ax.set_title(f"{t('chart_perf_curve_ttl')}  [{period_lbl}]",
                 color=C["text"], fontsize=9, fontweight="bold",
                 fontfamily="monospace", pad=6)
    ax.tick_params(colors=C["text_dim"], labelsize=7)
    for sp in ax.spines.values():
        sp.set_edgecolor(C["border"])
    ax.grid(which="both", color=C["border"], linestyle="--",
            linewidth=0.4, alpha=0.5)
    ax.legend(fontsize=7, facecolor=C["surface2"], edgecolor=C["border"],
              labelcolor=C["text"])

    # Show exponent b below the title
    txt = (f"Esponente b = {b:.3f}  "
           f"({'resistenza ↑' if b > 1.06 else 'velocità ↑' if b < 1.03 else 'bilanciato'})")
    ax.text(0.5, 0.97, txt, ha="center", va="top",
            transform=ax.transAxes, fontsize=7.5,
            color=C["text_dim"], fontfamily="monospace")

    fig.subplots_adjust(left=0.07, right=0.97, top=0.88, bottom=0.14)
    cnv = FigureCanvasTkAgg(fig, master=chart_f)
    cnv.draw()
    cnv.get_tk_widget().pack(fill="x")

# ── Race prediction section ───────────────────────────────────────────────────

_PREDICT_DISTS = {
    "1 km":           1000.0,
    "5 km":           5000.0,
    "10 km":         10000.0,
    "Mezza Maratona": 21097.5,
    "Maratona":       42195.0,
    "Personalizzata": -1.0,
}


def _render_race_prediction(body, storage_mgr):
    section_label(body, t("section_race_pred"))

    ctrl_f = tk.Frame(body, bg=C["bg"])
    ctrl_f.pack(fill="x", padx=20, pady=(0, 6))
    info_btn(ctrl_f, t("info_race_pred_title"),
             t("info_race_pred")).pack(side="right", padx=4)

    # Parameters panel (2 rows)
    param_f = tk.Frame(body, bg=C["surface2"],
                       highlightthickness=1, highlightbackground=C["border"])
    param_f.pack(fill="x", padx=20, pady=(0, 6))
    pf = tk.Frame(param_f, bg=C["surface2"])
    pf.pack(fill="x", padx=16, pady=10)

    # ── Row 1: Distance + custom km (conditional) + Elevation ────────────────
    r1 = tk.Frame(pf, bg=C["surface2"])
    r1.pack(fill="x", pady=(0, 6))

    tk.Label(r1, text="Distanza:", font=("Segoe UI", 9),
             fg=C["text_dim"], bg=C["surface2"]).pack(side="left")
    dist_var = tk.StringVar(value="10 km")
    dist_combo = tk.OptionMenu(r1, dist_var, *_PREDICT_DISTS.keys())
    dist_combo.config(font=("Segoe UI", 9), bg=C["surface"], fg=C["text"],
                      bd=0, highlightthickness=0, activebackground=C["surface2"])
    dist_combo["menu"].config(font=("Segoe UI", 9), bg=C["surface"], fg=C["text"])
    dist_combo.pack(side="left", padx=(4, 16))

    # Custom distance — visible only with "Personalizzata"
    custom_lbl = tk.Label(r1, text="km personalizzati:", font=("Segoe UI", 9),
                          fg=C["text_dim"], bg=C["surface2"])
    custom_var = tk.StringVar(value="15")
    custom_entry = tk.Entry(r1, textvariable=custom_var, font=("Segoe UI", 9),
                            bg=C["surface"], fg=C["text"], width=5, bd=0,
                            insertbackground=C["text"],
                            highlightthickness=1, highlightbackground=C["border"])

    def _on_dist_change(*_):
        if dist_var.get() == "Personalizzata":
            custom_lbl.pack(side="left")
            custom_entry.pack(side="left", padx=(4, 16))
        else:
            custom_lbl.pack_forget()
            custom_entry.pack_forget()

    dist_var.trace_add("write", _on_dist_change)
    _on_dist_change()  # initial state

    tk.Label(r1, text="Dislivello +  (m):", font=("Segoe UI", 9),
             fg=C["text_dim"], bg=C["surface2"]).pack(side="left")
    elev_var = tk.StringVar(value="0")
    tk.Entry(r1, textvariable=elev_var, font=("Segoe UI", 9),
             bg=C["surface"], fg=C["text"], width=6, bd=0,
             insertbackground=C["text"],
             highlightthickness=1, highlightbackground=C["border"]
             ).pack(side="left", padx=(4, 16))

    # ── Row 2: Time/length filters + Races only + CALCULATE ──────────────────
    r2 = tk.Frame(pf, bg=C["surface2"])
    r2.pack(fill="x")

    tk.Label(r2, text="Ultimi giorni:", font=("Segoe UI", 9),
             fg=C["text_dim"], bg=C["surface2"]).pack(side="left")
    days_var = tk.StringVar(value="365")
    tk.Entry(r2, textvariable=days_var, font=("Segoe UI", 9),
             bg=C["surface"], fg=C["text"], width=5, bd=0,
             insertbackground=C["text"],
             highlightthickness=1, highlightbackground=C["border"]
             ).pack(side="left", padx=(4, 4))
    tk.Label(r2, text="(0 = tutto)", font=("Segoe UI", 7),
             fg=C["text_dim"], bg=C["surface2"]).pack(side="left", padx=(0, 12))

    tk.Label(r2, text="km corsa min:", font=("Segoe UI", 9),
             fg=C["text_dim"], bg=C["surface2"]).pack(side="left")
    km_min_var = tk.StringVar(value="0")
    tk.Entry(r2, textvariable=km_min_var, font=("Segoe UI", 9),
             bg=C["surface"], fg=C["text"], width=5, bd=0,
             insertbackground=C["text"],
             highlightthickness=1, highlightbackground=C["border"]
             ).pack(side="left", padx=(4, 8))
    tk.Label(r2, text="max:", font=("Segoe UI", 9),
             fg=C["text_dim"], bg=C["surface2"]).pack(side="left")
    km_max_var = tk.StringVar(value="0")
    tk.Entry(r2, textvariable=km_max_var, font=("Segoe UI", 9),
             bg=C["surface"], fg=C["text"], width=5, bd=0,
             insertbackground=C["text"],
             highlightthickness=1, highlightbackground=C["border"]
             ).pack(side="left", padx=(4, 2))
    tk.Label(r2, text="(0 = nessun limite)", font=("Segoe UI", 7),
             fg=C["text_dim"], bg=C["surface2"]).pack(side="left", padx=(0, 12))

    races_var = tk.BooleanVar(value=False)
    tk.Checkbutton(r2, text=t("filter_races_only"), font=("Segoe UI", 8),
                   variable=races_var, fg=C["text"], bg=C["surface2"],
                   selectcolor=C["surface"], activebackground=C["surface2"]
                   ).pack(side="left", padx=8)

    # Calculate button
    chart_f = tk.Frame(body, bg=C["bg"])
    chart_f.pack(fill="x", padx=20, pady=(0, 20))

    def _calc():
        d_key = dist_var.get()
        dist_m = _PREDICT_DISTS[d_key]
        if dist_m < 0:   # custom
            try:
                dist_m = float(custom_var.get().replace(",", ".")) * 1000.0
            except Exception:
                dist_m = 10000.0
        try:
            elev_gain = float(elev_var.get())
        except Exception:
            elev_gain = 0.0
        try:
            days_back = int(days_var.get())
        except Exception:
            days_back = 365
        try:
            km_min = float(km_min_var.get())
        except Exception:
            km_min = 0.0
        try:
            km_max = float(km_max_var.get())
        except Exception:
            km_max = 0.0
        _redraw_race_pred(chart_f, storage_mgr,
                          dist_m, elev_gain, races_var.get(), days_back,
                          km_min, km_max)

    tk.Button(r2, text=t("btn_calculate"), font=("Segoe UI", 9, "bold"),
              bg=C["accent"], fg="white", bd=0, padx=12, pady=4,
              cursor="hand2", command=_calc).pack(side="left", padx=4)


def _personal_grade_correction(storage_mgr, races_only: bool,
                               avg_grade: float) -> tuple[float, str]:
    """
    Estimates the personal gradient correction in sec/km per 1% of average grade,
    using linear regression on real grade splits.
    Returns (total_sec_per_km_correction, source_label).
    """
    if avg_grade <= 0:
        return 0.0, ""

    try:
        import numpy as np
        splits = storage_mgr.get_grade_splits(races_only=races_only)
        # Filter splits with plausible gradient and speed (excludes outliers and walking)
        pts = [
            (s["grade_pct"], 1000.0 / s["pace_ms"])   # (grade%, sec/km)
            for s in splits
            if -20.0 <= s.get("grade_pct", 0) <= 20.0
            and 1.5 < s.get("pace_ms", 0) < 7.0       # 2:23–11:07 min/km
        ]
        if len(pts) >= 30:
            grades = np.array([p[0] for p in pts])
            paces  = np.array([p[1] for p in pts])
            slope, _ = np.polyfit(grades, paces, 1)
            # slope = sec/km per 1% of grade; cap in reasonable range
            slope = float(np.clip(slope, 2.0, 15.0))
            return slope * avg_grade, f"regressione personale {slope:.1f}s/km per 1%"
    except Exception:
        pass

    # Fallback to Minetti empirical model
    return avg_grade * 6.0, "modello empirico 6s/km per 1%"


def _redraw_race_pred(chart_f, storage_mgr,
                      dist_m: float, elev_gain: float,
                      races_only: bool, days_back: int = 365,
                      km_min: float = 0.0, km_max: float = 0.0):
    for w in chart_f.winfo_children():
        w.destroy()

    try:
        import numpy as np
    except ImportError:
        tk.Label(chart_f, text="numpy non installato.",
                 font=("Segoe UI", 9), fg=C["text_dim"], bg=C["bg"]).pack(pady=10)
        return

    from storage import _EFFORT_DISTANCES
    from datetime import date, timedelta
    efforts = storage_mgr.get_all_best_efforts(races_only=races_only)

    # Filter by time window
    if days_back > 0:
        cutoff = (date.today() - timedelta(days=days_back)).isoformat()
        efforts = [e for e in efforts if (e.get("date") or "") >= cutoff]

    # Filter by activity length
    if km_min > 0:
        efforts = [e for e in efforts if e.get("activity_dist_km", 0) >= km_min]
    if km_max > 0:
        efforts = [e for e in efforts if e.get("activity_dist_km", 0) <= km_max]

    if not efforts:
        tk.Label(chart_f, text="Nessun best effort trovato.",
                 font=("Segoe UI", 9), fg=C["text_dim"], bg=C["bg"]).pack(pady=10)
        return

    best: dict[str, float] = {}
    for e in efforts:
        c = e["canonical"]
        elapsed = e["elapsed_time"]
        if c not in best or elapsed < best[c]:
            best[c] = elapsed

    pts = [(dm, best[key]) for key, dm in _EFFORT_DISTANCES.items() if key in best]
    if len(pts) < 2:
        tk.Label(chart_f, text="Servono almeno 2 distanze per la previsione.",
                 font=("Segoe UI", 9), fg=C["text_dim"], bg=C["bg"],
                 wraplength=700).pack(pady=10)
        return

    pts.sort(key=lambda x: x[0])
    xs = np.array([p[0] for p in pts])
    ys = np.array([p[1] for p in pts])
    log_x = np.log(xs)
    log_y = np.log(ys)
    b, a  = np.polyfit(log_x, log_y, 1)
    A     = np.exp(a)

    # Residuals → standard deviation for Monte Carlo
    y_pred_log = a + b * log_x
    residuals  = log_y - y_pred_log
    sigma_log  = float(np.std(residuals)) if len(residuals) > 2 else 0.04

    # Base time at target distance
    t_base = A * (dist_m ** b)
    dist_km = dist_m / 1000.0

    # Custom gradient correction: linear regression on runner's grade splits
    # avg_grade in % = (elevation_m / distance_m) × 100
    avg_grade = (elev_gain / dist_m * 100.0) if dist_m > 0 else 0.0
    sec_per_km_correction, grade_correction_source = _personal_grade_correction(
        storage_mgr, races_only, avg_grade
    )
    t_adjusted = t_base + sec_per_km_correction * dist_km

    # Monte Carlo: 5000 samples
    np.random.seed(42)
    noise     = np.random.normal(0, sigma_log, 5000)
    samples   = t_adjusted * np.exp(noise)
    p10, p25, p50, p75, p90 = np.percentile(samples, [10, 25, 50, 75, 90])

    def _fmt(s):
        s = int(s)
        h, r = divmod(s, 3600)
        m, sec = divmod(r, 60)
        return f"{h}:{m:02d}:{sec:02d}" if h else f"{m}:{sec:02d}"

    fig = plt.Figure(figsize=(12, 3.8), facecolor=C["bg"])
    ax  = fig.add_subplot(111)
    ax.set_facecolor(C["surface"])

    ax.hist(samples / 60.0, bins=60, color=C["accent"], alpha=0.7, edgecolor="none")
    for val, col, lbl in [
        (p10 / 60, C["green"],  f"P10 {_fmt(p10)}  ← top"),
        (p25 / 60, C["blue"],   f"P25 {_fmt(p25)}"),
        (p50 / 60, C["yellow"], f"P50 {_fmt(p50)}"),
        (p75 / 60, C["orange"], f"P75 {_fmt(p75)}"),
        (p90 / 60, C["red"],    f"P90 {_fmt(p90)}  ← conservativo"),
    ]:
        ax.axvline(val, color=col, linewidth=1.4, linestyle="--", label=lbl)

    ax.set_xlabel("Tempo previsto (min)", fontsize=7, color=C["text_dim"])
    ax.set_ylabel("Frequenza (simulazioni)", fontsize=7, color=C["text_dim"])
    period_lbl = t("period_last_days").format(n=days_back) if days_back > 0 else t("period_all_history")
    km_lbl = ""
    if km_min > 0 or km_max > 0:
        lo = f"{km_min:.0f}" if km_min > 0 else "0"
        hi = f"{km_max:.0f}" if km_max > 0 else "∞"
        km_lbl = f"  corse {lo}–{hi}km"
    dist_lbl = (f"{dist_km:.1f} km"
                + (f"  +{elev_gain:.0f}m ↑" if elev_gain > 0 else "")
                + f"  [{period_lbl}]{km_lbl}")
    ax.set_title(f"DISTRIBUZIONE TEMPI PREVISTI — {dist_lbl}",
                 color=C["text"], fontsize=9, fontweight="bold",
                 fontfamily="monospace", pad=6)
    ax.tick_params(colors=C["text_dim"], labelsize=7)
    for sp in ax.spines.values():
        sp.set_edgecolor(C["border"])
    ax.grid(axis="y", color=C["border"], linestyle="--", linewidth=0.4, alpha=0.5)
    ax.legend(fontsize=7, facecolor=C["surface2"], edgecolor=C["border"],
              labelcolor=C["text"], loc="upper right")

    fig.subplots_adjust(left=0.06, right=0.98, top=0.88, bottom=0.16)
    cnv = FigureCanvasTkAgg(fig, master=chart_f)
    cnv.draw()
    cnv.get_tk_widget().pack(fill="x")

    # Text summary
    summary_f = tk.Frame(chart_f, bg=C["surface2"],
                         highlightthickness=1, highlightbackground=C["border"])
    summary_f.pack(fill="x", pady=(6, 0))
    sf = tk.Frame(summary_f, bg=C["surface2"])
    sf.pack(padx=16, pady=8)
    for lbl, val, col in [
        ("Top / ottimistica  (P10):", _fmt(p10), C["green"]),
        ("Buona giornata     (P25):", _fmt(p25), C["blue"]),
        ("Stima mediana      (P50):", _fmt(p50), C["yellow"]),
        ("Giornata normale   (P75):", _fmt(p75), C["orange"]),
        ("Conservativa       (P90):", _fmt(p90), C["red"]),
    ]:
        r = tk.Frame(sf, bg=C["surface2"])
        r.pack(anchor="w")
        tk.Label(r, text=lbl, font=("Segoe UI", 8), fg=C["text_dim"],
                 bg=C["surface2"], width=28, anchor="w").pack(side="left")
        tk.Label(r, text=val, font=("Segoe UI", 9, "bold"), fg=col,
                 bg=C["surface2"]).pack(side="left")
    if elev_gain > 0:
        corr_str = f"+{sec_per_km_correction * dist_km:.0f}s totali  [{grade_correction_source}]"
        tk.Label(sf, text=f"  (correzione dislivello: {corr_str})",
                 font=("Segoe UI", 7), fg=C["text_dim"],
                 bg=C["surface2"]).pack(anchor="w")

    # Diagnostic panel: data used in the fit
    tk.Frame(sf, bg=C["border"], height=1).pack(fill="x", pady=(8, 4))
    tk.Label(sf, text=f"  Fit: t = {A:.2f} · d^{b:.3f}   (Riegel teorico: b=1.060)   "
                      f"base {_fmt(t_base)} su {dist_km:.1f} km",
             font=("Segoe UI", 7), fg=C["text_dim"], bg=C["surface2"]).pack(anchor="w")
    tk.Label(sf, text="  Dati usati nel fit:",
             font=("Segoe UI", 7, "bold"), fg=C["text_dim"], bg=C["surface2"]).pack(anchor="w")
    nice = {"400m": "400m", "half_mile": "½ mi", "1k": "1K", "1_mile": "1 mi",
            "2_mile": "2 mi", "5k": "5K", "10k": "10K",
            "Half-Marathon": "½ Mar", "Marathon": "Mar"}
    for key, dm in sorted(_EFFORT_DISTANCES.items(), key=lambda x: x[1]):
        if key not in best:
            continue
        t_eff = best[key]
        pace_sec = t_eff / (dm / 1000.0)
        pace_str = f"{int(pace_sec // 60)}:{int(pace_sec % 60):02d}/km"
        tk.Label(sf,
                 text=f"    {nice.get(key, key):>6}  →  {_fmt(t_eff):>8}  ({pace_str})",
                 font=("Segoe UI", 7), fg=C["accent"], bg=C["surface2"]).pack(anchor="w")


