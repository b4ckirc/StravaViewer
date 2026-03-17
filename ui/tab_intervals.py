# ── ui/tab_intervals.py ────────────────────────────────────────────────────────
"""
Interval / Workout Detection tab.

Detects structured interval sessions from per-km splits and shows:
  - Session classification badge (VO2max, Threshold, Tempo, Fartlek, …)
  - Analytics strip (work pace, recovery pace, fade rate, consistency)
  - Scrollable segment table (work vs recovery intervals)
  - Pace-per-segment bar chart + HR-per-segment line chart
"""

import tkinter as tk
from tkinter import ttk
from config import C
from models import pace_label, speed_to_pace
from interval_detector import detect_intervals
from ui.widgets import (
    clear, no_data, section_label, StatCard,
    embed_mpl, style_ax, info_btn, FONT,
)
from i18n import t

try:
    import matplotlib.pyplot as plt
    import matplotlib.gridspec as gridspec
    from matplotlib.ticker import FuncFormatter
    HAS_MPL = True
except ImportError:
    HAS_MPL = False


# ── Public entry point ────────────────────────────────────────────────────────

def render(tab, activity):
    clear(tab)
    a = activity

    if not a.splits or len(a.splits) < 4:
        no_data(tab, t("intervals_no_splits"))
        return

    result = detect_intervals(a.splits)
    _render_header(tab, result)

    if not result.is_interval:
        _render_not_interval(tab, result)
    else:
        _render_stats_strip(tab, result)
        _render_table(tab, result)
        _render_charts(tab, result)


# ── Header ────────────────────────────────────────────────────────────────────

def _render_header(tab, result):
    hdr = tk.Frame(tab, bg=C["surface"])
    hdr.pack(fill="x")

    icon = "⚡" if result.is_interval else "◈"
    title_frame = tk.Frame(hdr, bg=C["surface"])
    title_frame.pack(side="left", padx=20, pady=10)

    tk.Label(title_frame,
             text=f"{icon}  {t('intervals_title')}",
             font=FONT["section"], fg=C["accent"],
             bg=C["surface"]).pack(side="left")

    # Info button
    ib = info_btn(hdr, t("intervals_info_title"), t("intervals_info_body"))
    ib.pack(side="right", padx=16, pady=10)

    if result.is_interval:
        wtype_label = t(f"intervals_wtype_{result.workout_type}")
        badge_text  = (f"{wtype_label}  •  "
                       f"{t('intervals_badge_reps').format(n=len(result.fast_segs))}  •  "
                       f"{t('intervals_stat_consistency')}: {result.consistency_score}/100")
        tk.Label(hdr, text=badge_text,
                 font=FONT["caption"], fg=C["yellow"],
                 bg=C["surface"], pady=4).pack(anchor="w", padx=20)


# ── Not-an-interval panel ─────────────────────────────────────────────────────

def _render_not_interval(tab, result):
    body = tk.Frame(tab, bg=C["bg"])
    body.pack(fill="both", expand=True, padx=20, pady=20)

    tk.Label(body,
             text=t("intervals_not_detected"),
             font=FONT["title"], fg=C["text_dim"],
             bg=C["bg"]).pack(pady=(40, 16))

    # Summary stats row
    cards = tk.Frame(body, bg=C["bg"])
    cards.pack(pady=8)

    avg_str = pace_label(result.avg_pace) if result.avg_pace else "--:--"
    std_str = _fmt_pace_delta(result.std_pace)
    cv_str  = f"{result.cv * 100:.1f} %"

    StatCard(cards, t("stat_avg_pace"),    avg_str, "min/km",
             stripe=C["accent"]).pack(side="left", padx=8, ipadx=4)
    StatCard(cards, t("intervals_std_label"), std_str, "min/km",
             stripe=C["blue"]).pack(side="left", padx=8, ipadx=4)
    StatCard(cards, t("intervals_cv_label"),  cv_str,
             stripe=C["text_dim"]).pack(side="left", padx=8, ipadx=4)

    reason_key = f"intervals_reason_{result.reason}" if result.reason else ""
    reason_msg = t(reason_key) if reason_key else ""
    if reason_msg and reason_msg != reason_key:
        tk.Label(body, text=reason_msg,
                 font=FONT["body"], fg=C["text_dim"],
                 bg=C["bg"]).pack(pady=(16, 0))


# ── Analytics strip ───────────────────────────────────────────────────────────

def _render_stats_strip(tab, result):
    row = tk.Frame(tab, bg=C["bg"])
    row.pack(fill="x", padx=20, pady=(12, 4))

    work_str     = pace_label(result.avg_work_pace)
    rec_str      = pace_label(result.avg_recovery_pace)
    fade_str     = (("+" if result.fade_rate >= 0 else "") +
                    _fmt_pace_delta(abs(result.fade_rate)) +
                    (" ▲" if result.fade_rate > 0 else " ▼" if result.fade_rate < 0 else ""))
    fade_color   = C["red"] if result.fade_rate > 0.1 else \
                   C["green"] if result.fade_rate < -0.05 else C["text"]
    cons_str     = str(result.consistency_score)
    cons_color   = C["green"] if result.consistency_score >= 80 else \
                   C["yellow"] if result.consistency_score >= 60 else C["red"]

    StatCard(row, t("intervals_stat_work_pace"),     work_str, "min/km",
             stripe=C["accent"]).pack(side="left", padx=6, pady=4)
    StatCard(row, t("intervals_stat_recovery_pace"), rec_str,  "min/km",
             stripe=C["blue"]).pack(side="left", padx=6, pady=4)
    StatCard(row, t("intervals_stat_fade_rate"),     fade_str, "min/km",
             color=fade_color, stripe=fade_color).pack(side="left", padx=6, pady=4)
    StatCard(row, t("intervals_stat_consistency"),   cons_str, "/ 100",
             color=cons_color, stripe=cons_color).pack(side="left", padx=6, pady=4)


# ── Segment table ─────────────────────────────────────────────────────────────

def _render_table(tab, result):
    section_label(tab, t("intervals_section_table"))

    cols   = [t("intervals_col_num"), t("intervals_col_type"),
              t("intervals_col_dist"), t("intervals_col_time"),
              t("intervals_col_pace"), t("intervals_col_hr"),
              t("intervals_col_vs_avg")]
    widths = [4, 12, 9, 8, 9, 7, 9]

    outer = tk.Frame(tab, bg=C["bg"])
    outer.pack(fill="x", padx=20, pady=(0, 4))

    # Header row
    hdr = tk.Frame(outer, bg=C["surface2"])
    hdr.pack(fill="x")
    for col, w in zip(cols, widths):
        tk.Label(hdr, text=col,
                 font=("Segoe UI", 8, "bold"),
                 fg=C["text_dim"], bg=C["surface2"],
                 width=w, anchor="center", pady=8
                 ).pack(side="left", padx=2)

    # Scrollable body
    sc = tk.Canvas(outer, bg=C["bg"], bd=0, highlightthickness=0, height=220)
    sb = ttk.Scrollbar(outer, orient="vertical", command=sc.yview)
    sc.configure(yscrollcommand=sb.set)
    sb.pack(side="right", fill="y")
    sc.pack(fill="x", expand=False)
    inner = tk.Frame(sc, bg=C["bg"])
    sc.create_window((0, 0), window=inner, anchor="nw")
    inner.bind("<Configure>", lambda e: sc.configure(scrollregion=sc.bbox("all")))
    sc.bind("<MouseWheel>",
            lambda e: sc.yview_scroll(int(-1 * (e.delta / 120)), "units"))

    avg_pace = result.avg_pace
    work_num = rec_num = 0

    for seg in result.segments:
        is_work = seg.type == "fast"
        if is_work:
            work_num += 1
            seg_num   = work_num
            type_lbl  = f"⚡ {t('intervals_type_work')}"
            type_col  = C["accent"]
            bg_row    = C["surface2"] if work_num % 2 == 0 else C["bg"]
        else:
            rec_num  += 1
            seg_num   = rec_num
            type_lbl  = f"○ {t('intervals_type_rest')}"
            type_col  = C["blue"]
            bg_row    = C["surface2"] if rec_num % 2 == 0 else C["bg"]

        dist_km   = seg.total_dist / 1000.0
        mins_tot  = seg.total_time // 60
        secs_tot  = seg.total_time % 60
        time_str  = f"{mins_tot}:{secs_tot:02d}"
        pace_str  = pace_label(seg.avg_pace)
        hr_str    = f"{seg.avg_hr:.0f}" if seg.avg_hr else "–"
        delta     = seg.avg_pace - avg_pace
        delta_str = ("+" if delta >= 0 else "") + _fmt_pace_delta(abs(delta))
        delta_col = C["red"] if delta > 0.15 else \
                    C["green"] if delta < -0.15 else C["text"]

        row = tk.Frame(inner, bg=bg_row)
        row.pack(fill="x")

        # Colored left accent strip for work intervals
        if is_work:
            tk.Frame(row, bg=C["accent"], width=3).pack(side="left", fill="y")

        values = [
            (str(seg_num),      C["text_dim"]),
            (type_lbl,          type_col),
            (f"{dist_km:.2f}",  C["text"]),
            (time_str,          C["blue"]),
            (pace_str,          C["accent"] if is_work else C["text"]),
            (hr_str,            C["red"] if seg.avg_hr else C["text_dim"]),
            (delta_str,         delta_col),
        ]
        for (v, col), w in zip(values, widths):
            tk.Label(row, text=v,
                     font=("Segoe UI", 9), fg=col, bg=bg_row,
                     width=w, anchor="center", pady=6
                     ).pack(side="left", padx=2)


# ── Charts ────────────────────────────────────────────────────────────────────

def _render_charts(tab, result):
    if not HAS_MPL:
        no_data(tab, t("install_matplotlib"))
        return

    section_label(tab, t("intervals_section_charts"))

    has_hr = any(s.avg_hr for s in result.segments)
    rows   = 2 if has_hr else 1

    fig = plt.Figure(figsize=(13, 5.5 * rows), facecolor=C["bg"])
    gs  = gridspec.GridSpec(rows, 1, figure=fig,
                            hspace=0.45,
                            left=0.07, right=0.97,
                            top=0.92, bottom=0.10)

    # ── Build x-axis labels and data arrays ───────────────────────────────────
    x_labels  = []
    x_pos     = []
    bar_paces = []
    bar_cols  = []
    hr_vals   = []

    work_count = rec_count = 0
    for i, seg in enumerate(result.segments):
        if seg.type == "fast":
            work_count += 1
            x_labels.append(f"W{work_count}")
            bar_cols.append(C["accent"])
        else:
            rec_count += 1
            x_labels.append(f"R{rec_count}")
            bar_cols.append(C["blue"])
        x_pos.append(i)
        bar_paces.append(seg.avg_pace)
        hr_vals.append(seg.avg_hr or 0)

    fmt = FuncFormatter(lambda y, _: pace_label(y) if y > 0 else "")

    # ── Pace bar chart ────────────────────────────────────────────────────────
    ax1 = fig.add_subplot(gs[0, 0])
    bars = ax1.bar(x_pos, bar_paces, color=bar_cols, alpha=0.85, width=0.65)
    ax1.invert_yaxis()
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(x_labels, fontsize=7)
    ax1.set_ylabel("min/km", fontsize=7)
    ax1.yaxis.set_major_formatter(fmt)
    style_ax(ax1, t("intervals_chart_pace"))

    # Pace labels on top of bars
    for bar, pace in zip(bars, bar_paces):
        if pace > 0:
            ax1.text(bar.get_x() + bar.get_width() / 2,
                     bar.get_height() + 0.02,
                     pace_label(pace),
                     ha="center", va="bottom",
                     fontsize=6.5, color=C["text"],
                     fontfamily="monospace")

    # Reference lines
    ax1.axhline(result.avg_work_pace, color=C["accent"],
                linestyle="--", lw=1.2, alpha=0.7,
                label=f"{t('intervals_stat_work_pace')} {pace_label(result.avg_work_pace)}")
    ax1.axhline(result.avg_recovery_pace, color=C["blue"],
                linestyle="--", lw=1.0, alpha=0.6,
                label=f"{t('intervals_stat_recovery_pace')} {pace_label(result.avg_recovery_pace)}")
    ax1.legend(fontsize=7, facecolor=C["surface2"],
               edgecolor=C["border"], labelcolor=C["text"])

    # ── HR line chart ─────────────────────────────────────────────────────────
    if has_hr and rows == 2:
        ax2 = fig.add_subplot(gs[1, 0])
        hr_plot = [v for v in hr_vals]
        line_cols = [C["accent"] if result.segments[i].type == "fast"
                     else C["blue"]
                     for i in range(len(result.segments))]

        ax2.plot(x_pos, hr_plot, color=C["red"], lw=2, marker="o", ms=5,
                 zorder=3)
        # Color each segment marker individually
        for xi, yi, mc in zip(x_pos, hr_plot, line_cols):
            if yi:
                ax2.plot(xi, yi, "o", color=mc, ms=7, zorder=4)

        ax2.fill_between(x_pos, hr_plot, alpha=0.08, color=C["red"])
        ax2.set_xticks(x_pos)
        ax2.set_xticklabels(x_labels, fontsize=7)
        ax2.set_ylabel("bpm", fontsize=7)
        style_ax(ax2, t("intervals_chart_hr"))

        # Average HR reference
        avg_hr_all = [v for v in hr_vals if v]
        if avg_hr_all:
            import statistics as _st
            mean_hr = _st.mean(avg_hr_all)
            ax2.axhline(mean_hr, color=C["yellow"], linestyle="--", lw=1.0,
                        label=f"Avg {mean_hr:.0f} bpm")
            ax2.legend(fontsize=7, facecolor=C["surface2"],
                       edgecolor=C["border"], labelcolor=C["text"])

    embed_mpl(tab, fig)


# ── Formatting helpers ────────────────────────────────────────────────────────

def _fmt_pace_delta(delta_min_km: float) -> str:
    """Format a pace difference (float minutes) as M:SS."""
    if delta_min_km is None:
        return "--:--"
    total_sec = abs(delta_min_km) * 60
    return f"{int(total_sec // 60)}:{int(total_sec % 60):02d}"
