# ── ui/tab_compare.py ─────────────────────────────────────────────────────────
import tkinter as tk
from config import C, COMPARE_COLORS, COMPARE_MARKERS, COMPARE_EMOJIS
from models import fmt_dist, fmt_time, speed_to_pace, pace_label
from ui.widgets import make_scrollable, section_label, no_data, clear
from i18n import t

try:
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_MPL = True
except ImportError:
    HAS_MPL = False


def render(tab, activities: list):
    clear(tab)
    if not activities:
        no_data(tab, t("compare_no_activities"))
        return

    n       = len(activities)
    colors  = COMPARE_COLORS[:n]
    markers = COMPARE_MARKERS[:n]
    emojis  = COMPARE_EMOJIS[:n]

    # ── Header ────────────────────────────────────────────────────────────────
    hdr = tk.Frame(tab, bg=C["surface"], pady=12)
    hdr.pack(fill="x")
    tk.Label(hdr, text=t("compare_title").format(n=n),
             font=("Courier", 12, "bold"), fg=C["accent"],
             bg=C["surface"]).pack(anchor="w", padx=20)
    for i, (act, col, em) in enumerate(zip(activities, colors, emojis)):
        tk.Label(hdr,
                 text=f"  {em}  {t('compare_main') if i == 0 else ''}{act.name[:70]}",
                 font=("Courier", 9, "bold" if i == 0 else "normal"),
                 fg=col, bg=C["surface"]).pack(anchor="w", padx=20)

    _, body = make_scrollable(tab)

    # ── Tabella comparative ────────────────────────────────────────────────────
    section_label(body, t("section_cmp_stats"))
    col_w = max(12, min(20, 76 // n))

    tbl = tk.Frame(body, bg=C["surface2"],
                   highlightthickness=1, highlightbackground=C["border"])
    tbl.pack(fill="x", padx=20, pady=(0, 10))

    hrow = tk.Frame(tbl, bg=C["surface"])
    hrow.pack(fill="x")
    tk.Label(hrow, text=t("cmp_metric"), font=("Courier", 8, "bold"),
             fg=C["text_dim"], bg=C["surface"],
             width=22, anchor="w", padx=12, pady=8).pack(side="left")
    for col, em in zip(colors, emojis):
        tk.Label(hrow, text=em, font=("Courier", 8, "bold"),
                 fg=col, bg=C["surface"],
                 width=col_w, anchor="center").pack(side="left")

    def cmp_row(label, values, better, idx):
        bg = C["surface2"] if idx % 2 == 0 else C["surface"]
        r  = tk.Frame(tbl, bg=bg)
        r.pack(fill="x")
        tk.Label(r, text=label, font=("Courier", 9), fg=C["text_dim"],
                 bg=bg, width=22, anchor="w", padx=12, pady=7).pack(side="left")
        nums = []
        for v in values:
            try:    nums.append(float(str(v).replace(":", "").split()[0]))
            except: nums.append(None)
        valid = [x for x in nums if x is not None]
        best  = (min(valid) if better == "low" else max(valid)) if len(valid) > 1 else None
        worst = (max(valid) if better == "low" else min(valid)) if len(valid) > 1 else None
        for v, col, num in zip(values, colors, nums):
            fg = C["green"] if num is not None and num == best  else \
                 C["red"]   if num is not None and num == worst else C["text"]
            tk.Label(r, text=str(v), font=("Courier", 9, "bold"),
                     fg=fg, bg=bg, width=col_w, anchor="center").pack(side="left")

    rows = [
        (t("cmp_distance"),    [fmt_dist(a.distance)           for a in activities], "high"),
        (t("cmp_moving_time"), [fmt_time(a.moving_time)        for a in activities], "low"),
        (t("cmp_total_time"),  [fmt_time(a.elapsed_time)       for a in activities], "low"),
        (t("cmp_avg_pace"),    [a.avg_pace_str                 for a in activities], "low"),
        (t("cmp_best_pace"),   [a.max_pace_str                 for a in activities], "low"),
        (t("cmp_avg_speed"),   [f"{a.avg_speed*3.6:.1f}"       for a in activities], "high"),
        (t("cmp_elev"),        [f"{a.elev_gain:.0f} m"         for a in activities], "low"),
    ]
    if any(a.avg_hr for a in activities):
        rows += [
            (t("cmp_avg_hr"), [f"{a.avg_hr:.0f}"  if a.avg_hr  else "–" for a in activities], "low"),
            (t("cmp_max_hr"), [f"{a.max_hr:.0f}"  if a.max_hr  else "–" for a in activities], "low"),
        ]
    if any(a.calories for a in activities):
        rows.append((t("cmp_calories"),
                     [f"{a.calories:.0f}" if a.calories else "–" for a in activities], "low"))
    if any(a.avg_cadence for a in activities):
        rows.append((t("cmp_cadence"),
                     [f"{a.avg_cadence*2:.0f}" if a.avg_cadence else "–" for a in activities], "high"))
    if any(a.suffer_score for a in activities):
        rows.append((t("cmp_suffer"),
                     [str(a.suffer_score) if a.suffer_score else "–" for a in activities], "low"))

    for idx, (label, values, better) in enumerate(rows):
        cmp_row(label, values, better, idx)

    if not HAS_MPL:
        return

    # ── Grafico passo ─────────────────────────────────────────────────────────
    acts_with_splits = [a for a in activities if a.splits]
    if acts_with_splits:
        section_label(body, t("section_pace_compare"))
        cf1 = tk.Frame(body, bg=C["bg"])
        cf1.pack(fill="x", padx=20, pady=(0, 8))

        fig1 = plt.Figure(figsize=(13, 4), facecolor=C["bg"])
        ax1  = fig1.add_subplot(111)
        ax1.set_facecolor(C["surface"])
        for act, col, mk, em in zip(activities, colors, markers, emojis):
            if not act.splits:
                continue
            kms   = [s.get("split", i+1) for i, s in enumerate(act.splits)]
            paces = [speed_to_pace(s.get("average_speed", 0)) or 0 for s in act.splits]
            ax1.plot(kms, paces, color=col, lw=2, marker=mk, ms=4,
                     label=f"{em} {act.name[:30]}")
        ax1.invert_yaxis()
        ax1.yaxis.set_major_formatter(
            FuncFormatter(lambda y, _: pace_label(y) if y > 0 else ""))
        ax1.set_xlabel("Km", fontsize=8, color=C["text_dim"])
        ax1.set_ylabel("min/km", fontsize=8, color=C["text_dim"])
        ax1.tick_params(colors=C["text_dim"], labelsize=7)
        for sp in ax1.spines.values():
            sp.set_edgecolor(C["border"])
        ax1.grid(color=C["border"], linestyle="--", linewidth=0.4, alpha=0.6)
        ax1.legend(fontsize=7.5, facecolor=C["surface2"],
                   edgecolor=C["border"], labelcolor=C["text"])
        fig1.suptitle(t("chart_pace_km"), color=C["text"], fontsize=9,
                      fontweight="bold", fontfamily="monospace")
        fig1.tight_layout()
        cnv1 = FigureCanvasTkAgg(fig1, master=cf1)
        cnv1.draw()
        cnv1.get_tk_widget().pack(fill="x")

    # ── Grafico HR ────────────────────────────────────────────────────────────
    acts_with_hr = [a for a in activities
                    if any(s.get("average_heartrate") for s in (a.splits or []))]
    if acts_with_hr:
        section_label(body, t("section_hr_compare"))
        cf2 = tk.Frame(body, bg=C["bg"])
        cf2.pack(fill="x", padx=20, pady=(0, 20))

        fig2 = plt.Figure(figsize=(13, 4), facecolor=C["bg"])
        ax2  = fig2.add_subplot(111)
        ax2.set_facecolor(C["surface"])
        for act, col, mk, em in zip(activities, colors, markers, emojis):
            if not act.splits:
                continue
            hrs = [s.get("average_heartrate") for s in act.splits]
            if not any(hrs):
                continue
            kms = [s.get("split", i+1) for i, s in enumerate(act.splits)]
            ax2.plot(kms, [h or 0 for h in hrs], color=col, lw=2, marker=mk, ms=4,
                     label=f"{em} {act.name[:30]}")
        ax2.set_xlabel("Km", fontsize=8, color=C["text_dim"])
        ax2.set_ylabel("bpm", fontsize=8, color=C["text_dim"])
        ax2.tick_params(colors=C["text_dim"], labelsize=7)
        for sp in ax2.spines.values():
            sp.set_edgecolor(C["border"])
        ax2.grid(color=C["border"], linestyle="--", linewidth=0.4, alpha=0.6)
        ax2.legend(fontsize=7.5, facecolor=C["surface2"],
                   edgecolor=C["border"], labelcolor=C["text"])
        fig2.suptitle(t("chart_hr_km"), color=C["text"], fontsize=9,
                      fontweight="bold", fontfamily="monospace")
        fig2.tight_layout()
        cnv2 = FigureCanvasTkAgg(fig2, master=cf2)
        cnv2.draw()
        cnv2.get_tk_widget().pack(fill="x")
