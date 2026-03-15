# ── ui/export_pdf.py ──────────────────────────────────────────────────────────
from config import C
from models import fmt_dist, fmt_time, fmt_pace, speed_to_pace, pace_label
from i18n import t as tr

try:
    import matplotlib.pyplot as plt
    import matplotlib.gridspec as gridspec
    from matplotlib.backends.backend_pdf import PdfPages
    from matplotlib.ticker import FuncFormatter
    HAS_MPL = True
except ImportError:
    HAS_MPL = False


def export_pdf(activity, path: str):
    if not HAS_MPL:
        raise RuntimeError("matplotlib non disponibile.")
    a = activity
    with PdfPages(path) as pdf:
        # Pagina 1 — Riepilogo testuale
        fig1 = plt.Figure(figsize=(11.69, 8.27), facecolor=C["bg"])
        ax   = fig1.add_axes([0, 0, 1, 1])
        ax.set_facecolor(C["bg"])
        ax.axis("off")

        def t(x, y, s, **kw):
            ax.text(x, y, s, transform=ax.transAxes,
                    fontfamily="monospace", **kw)

        t(0.05, 0.93, "⬡ STRAVA ACTIVITY REPORT",
          fontsize=18, fontweight="bold", color=C["accent"])
        t(0.05, 0.87, a.name,     fontsize=13, color=C["text"])
        t(0.05, 0.83, a.date_str, fontsize=9,  color=C["text_dim"])

        _left_labels  = tr("pdf_left_stats")
        _right_labels = tr("pdf_right_stats")
        left_stats = list(zip(_left_labels, [
            fmt_dist(a.distance),
            fmt_time(a.moving_time),
            f"{a.avg_pace_str} /km",
            f"{a.max_pace_str} /km",
            f"{a.avg_speed*3.6:.1f} km/h",
            f"{a.elev_gain:.0f} m",
        ]))
        right_stats = list(zip(_right_labels, [
            f"{a.avg_hr:.0f} bpm"        if a.avg_hr       else "–",
            f"{a.max_hr:.0f} bpm"        if a.max_hr       else "–",
            f"{a.calories:.0f} kcal"     if a.calories     else "–",
            f"{a.avg_cadence*2:.0f} spm" if a.avg_cadence  else "–",
            str(a.suffer_score)          if a.suffer_score else "–",
            a.device or "–",
        ]))
        for i, (lbl, val) in enumerate(left_stats):
            y = 0.74 - i * 0.07
            t(0.05, y,       lbl.upper(), fontsize=7,  color=C["text_dim"])
            t(0.05, y-0.033, val,          fontsize=11, fontweight="bold", color=C["text"])
        for i, (lbl, val) in enumerate(right_stats):
            y = 0.74 - i * 0.07
            t(0.38, y,       lbl.upper(), fontsize=7,  color=C["text_dim"])
            t(0.38, y-0.033, val,          fontsize=11, fontweight="bold", color=C["text"])

        if a.splits:
            t(0.05, 0.27, tr("pdf_splits_header"),
              fontsize=8, fontweight="bold", color=C["accent"])
            hdr = f"{'KM':>3}  {'DIST':>7}  {'TEMPO':>7}  {'PASSO':>7}  {'KM/H':>6}  {'HR':>5}  {'ELEV':>7}"
            t(0.05, 0.23, hdr, fontsize=6.5, color=C["text_dim"])
            for i, s in enumerate(a.splits[:20]):
                sp = s.get("average_speed", 0)
                hr = s.get("average_heartrate")
                el = s.get("elevation_difference", 0)
                line = (f"{s.get('split',i+1):>3}  "
                        f"{s.get('distance',0)/1000:>7.3f}  "
                        f"{fmt_time(s.get('moving_time',0)):>7}  "
                        f"{fmt_pace(sp):>7}  "
                        f"{sp*3.6:>6.1f}  "
                        f"{'–':>5}" if not hr else
                        f"{s.get('split',i+1):>3}  "
                        f"{s.get('distance',0)/1000:>7.3f}  "
                        f"{fmt_time(s.get('moving_time',0)):>7}  "
                        f"{fmt_pace(sp):>7}  "
                        f"{sp*3.6:>6.1f}  "
                        f"{hr:>5.0f}  "
                        f"{el:>+7.1f}")
                t(0.05, 0.20 - i * 0.011, line, fontsize=5.8, color=C["text"])

        t(0.05, 0.02, tr("pdf_generated_by"),
          fontsize=6, color=C["text_dim"])
        pdf.savefig(fig1, bbox_inches="tight", facecolor=C["bg"])
        plt.close(fig1)

        # Pagina 2 — Grafici
        if a.splits:
            from ui.tab_charts import _build_export_fig
            fig2 = _build_export_fig(a)
            pdf.savefig(fig2, bbox_inches="tight", facecolor=C["bg"])
            plt.close(fig2)

        d = pdf.infodict()
        d["Title"]   = a.name
        d["Subject"] = "Strava Activity Report"
        d["Creator"] = "Strava Viewer v3.0"
