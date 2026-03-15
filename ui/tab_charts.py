# ── ui/tab_charts.py ──────────────────────────────────────────────────────────
import tkinter as tk
from config import C
from models import speed_to_pace, pace_label
from ui.widgets import embed_mpl, style_ax, no_data, clear
from i18n import t

try:
    import matplotlib.pyplot as plt
    import matplotlib.gridspec as gridspec
    import matplotlib.patches as mpatches
    from matplotlib.ticker import FuncFormatter
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

# Colori passo — ben distinguibili tra loro
PACE_FAST   = "#3fb950"   # verde  → più veloce della media
PACE_AVG    = "#58a6ff"   # blu    → in media  (era arancione, troppo simile al rosso)
PACE_SLOW   = "#f85149"   # rosso  → più lento della media


def render(tab, activity):
    clear(tab)
    if not HAS_MPL:
        no_data(tab, t("install_matplotlib"))
        return
    a = activity
    if not a.splits:
        no_data(tab, t("chart_no_splits"))
        return

    splits   = a.splits
    kms      = [s.get("split", i+1) for i, s in enumerate(splits)]
    speeds   = [s.get("average_speed", 0) for s in splits]
    paces    = [speed_to_pace(sp) or 0 for sp in speeds]
    hrs      = [s.get("average_heartrate") for s in splits]
    elevs    = [s.get("elevation_difference", 0) for s in splits]
    cadences = [s.get("average_cadence") for s in splits]
    has_hr   = any(h for h in hrs)
    has_cad  = any(c for c in cadences)
    has_extra = has_hr or has_cad

    rows = 3 if has_extra else 2
    fig  = plt.Figure(figsize=(14, 9.5), facecolor=C["bg"])
    gs   = gridspec.GridSpec(rows, 2, figure=fig,
                             hspace=0.48, wspace=0.32,
                             left=0.07, right=0.97, top=0.93, bottom=0.06)

    avg_pace = speed_to_pace(a.avg_speed)

    # ── Passo per km ──────────────────────────────────────────────────────────
    ax1 = fig.add_subplot(gs[0, :])
    bar_colors = [
        PACE_FAST if p and avg_pace and p < avg_pace * 0.97 else
        PACE_SLOW if p and avg_pace and p > avg_pace * 1.03 else
        PACE_AVG
        for p in paces
    ]
    bars = ax1.bar(kms, paces, color=bar_colors, alpha=0.88, width=0.7)
    ax1.invert_yaxis()
    ax1.set_ylabel("min/km", fontsize=7)
    ax1.set_xlabel("Km", fontsize=7)
    style_ax(ax1, t("chart_pace_per_km"))
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda y, _: pace_label(y) if y > 0 else ""))
    for bar, pace in zip(bars, paces):
        if pace > 0:
            ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
                     pace_label(pace), ha="center", va="bottom",
                     fontsize=6, color=C["text"], fontfamily="monospace")
    if avg_pace:
        ax1.axhline(avg_pace, color=C["yellow"], linestyle="--", lw=1.4,
                    label=f"{t('chart_pace_avg_line')} {pace_label(avg_pace)}")

    patches = [
        mpatches.Patch(color=PACE_FAST, label=t("chart_pace_faster")),
        mpatches.Patch(color=PACE_AVG,  label=t("chart_pace_avg")),
        mpatches.Patch(color=PACE_SLOW, label=t("chart_pace_slower")),
    ]
    ax1.legend(handles=patches, fontsize=6.5, facecolor=C["surface2"],
               edgecolor=C["border"], labelcolor=C["text"], loc="upper right")

    # ── Velocità ──────────────────────────────────────────────────────────────
    ax2 = fig.add_subplot(gs[1, 0])
    spd = [s * 3.6 for s in speeds]
    ax2.plot(kms, spd, color=C["blue"], lw=2, marker="o", ms=3, alpha=0.9)
    ax2.fill_between(kms, spd, alpha=0.12, color=C["blue"])
    ax2.set_ylabel("km/h", fontsize=7)
    ax2.set_xlabel("Km", fontsize=7)
    style_ax(ax2, t("chart_speed"))

    # ── Dislivello ────────────────────────────────────────────────────────────
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.bar(kms, elevs,
            color=[C["green"] if e >= 0 else C["red"] for e in elevs],
            alpha=0.85, width=0.7)
    ax3.axhline(0, color=C["border"], lw=0.8)
    ax3.set_ylabel("m", fontsize=7)
    ax3.set_xlabel("Km", fontsize=7)
    style_ax(ax3, t("chart_elev_per_km"))

    # ── HR ────────────────────────────────────────────────────────────────────
    if has_hr and has_extra:
        ax4 = fig.add_subplot(gs[2, 0])
        hv = [h or 0 for h in hrs]
        ax4.plot(kms, hv, color=C["red"], lw=2, marker="o", ms=3)
        ax4.fill_between(kms, hv, alpha=0.12, color=C["red"])
        ax4.set_ylabel("bpm", fontsize=7)
        ax4.set_xlabel("Km", fontsize=7)
        style_ax(ax4, t("chart_hr"))
        if a.avg_hr:
            ax4.axhline(a.avg_hr, color=C["accent2"], linestyle="--",
                        lw=1, label=f"{t('chart_pace_avg_line')} {a.avg_hr:.0f}")
            ax4.legend(fontsize=7, facecolor=C["surface2"],
                       edgecolor=C["border"], labelcolor=C["text"])

    # ── Cadenza ───────────────────────────────────────────────────────────────
    if has_cad and has_extra:
        ax5 = fig.add_subplot(gs[2, 1])
        cv = [c * 2 if c else 0 for c in cadences]
        ax5.plot(kms, cv, color=C["purple"], lw=2, marker="o", ms=3)
        ax5.fill_between(kms, cv, alpha=0.12, color=C["purple"])
        ax5.set_ylabel("spm", fontsize=7)
        ax5.set_xlabel("Km", fontsize=7)
        style_ax(ax5, t("chart_cadence"))

    fig.suptitle(f"{a.name}  •  {a.date_str}",
                 color=C["text"], fontsize=10, fontweight="bold", fontfamily="monospace")
    embed_mpl(tab, fig)


# ── Export helper (usato da export_pdf.py e app._export_png) ──────────────────

def _build_export_fig(a):
    """Figura matplotlib standalone (non embedded in tk) per PNG/PDF export."""
    if not a.splits:
        fig = plt.Figure(figsize=(12, 8), facecolor=C["bg"])
        return fig
    splits  = a.splits
    kms     = [s.get("split", i+1) for i, s in enumerate(splits)]
    speeds  = [s.get("average_speed", 0) for s in splits]
    paces   = [speed_to_pace(sp) or 0 for sp in speeds]
    hrs     = [s.get("average_heartrate") for s in splits]
    elevs   = [s.get("elevation_difference", 0) for s in splits]
    has_hr  = any(h for h in hrs)
    rows    = 3 if has_hr else 2
    fig     = plt.Figure(figsize=(14, 9), facecolor=C["bg"])
    gs      = gridspec.GridSpec(rows, 2, figure=fig,
                                hspace=0.5, wspace=0.35,
                                left=0.07, right=0.97, top=0.92, bottom=0.07)
    avg_pace = speed_to_pace(a.avg_speed)
    bar_cols = [PACE_FAST if p and avg_pace and p < avg_pace * 0.97 else
                PACE_SLOW if p and avg_pace and p > avg_pace * 1.03 else
                PACE_AVG for p in paces]
    ax1 = fig.add_subplot(gs[0, :])
    ax1.bar(kms, paces, color=bar_cols, alpha=0.85, width=0.7)
    ax1.invert_yaxis()
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda y, _: pace_label(y) if y > 0 else ""))
    if avg_pace:
        ax1.axhline(avg_pace, color=C["yellow"], linestyle="--", lw=1.2)
    ax1.set_ylabel("min/km", fontsize=7)
    style_ax(ax1, "PASSO PER KM")
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.plot(kms, [s * 3.6 for s in speeds], color=C["blue"], lw=1.8, marker="o", ms=3)
    ax2.fill_between(kms, [s * 3.6 for s in speeds], alpha=0.12, color=C["blue"])
    ax2.set_ylabel("km/h", fontsize=7)
    style_ax(ax2, "VELOCITÀ")
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.bar(kms, elevs, color=[C["green"] if e >= 0 else C["red"] for e in elevs],
            alpha=0.85, width=0.7)
    ax3.axhline(0, color=C["border"], lw=0.8)
    ax3.set_ylabel("m", fontsize=7)
    style_ax(ax3, "DISLIVELLO")
    if has_hr and rows == 3:
        ax4 = fig.add_subplot(gs[2, :])
        hv  = [h or 0 for h in hrs]
        ax4.plot(kms, hv, color=C["red"], lw=1.8, marker="o", ms=3)
        ax4.fill_between(kms, hv, alpha=0.12, color=C["red"])
        if a.avg_hr:
            ax4.axhline(a.avg_hr, color=C["accent2"], linestyle="--", lw=1)
        ax4.set_ylabel("bpm", fontsize=7)
        style_ax(ax4, "FREQUENZA CARDIACA")
    fig.suptitle(f"{a.name}  •  {a.date_str}",
                 color=C["text"], fontsize=10, fontweight="bold", fontfamily="monospace")
    return fig
