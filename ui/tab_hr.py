# ── ui/tab_hr.py ──────────────────────────────────────────────────────────────
import tkinter as tk
from config import C, HR_ZONES
from models import speed_to_pace, pace_label, hr_zone_for, fmt_time
from ui.widgets import embed_mpl, style_ax, no_data, clear, info_btn
from i18n import t

try:
    import matplotlib.pyplot as plt
    import matplotlib.gridspec as gridspec
    import matplotlib.patches as mpatches
    from matplotlib.ticker import FuncFormatter
    HAS_MPL = True
except ImportError:
    HAS_MPL = False


def render(tab, activity):
    clear(tab)
    if not HAS_MPL:
        no_data(tab, t("install_matplotlib"))
        return
    a = activity
    has_hr = a.avg_hr or any(s.get("average_heartrate") for s in a.splits)
    if not has_hr:
        no_data(tab, t("no_hr_data"))
        return

    ctrl = tk.Frame(tab, bg=C["surface"], pady=10)
    ctrl.pack(fill="x")
    tk.Label(ctrl, text=t("hr_max_label"), font=("Segoe UI", 9, "bold"),
             fg=C["text_dim"], bg=C["surface"]).pack(side="left", padx=20)
    hr_max_var = tk.StringVar(value=str(int(a.max_hr) if a.max_hr else 190))
    tk.Entry(ctrl, textvariable=hr_max_var, font=("Segoe UI", 10),
             bg=C["surface2"], fg=C["text"], width=6, bd=0,
             insertbackground=C["text"],
             highlightthickness=1, highlightbackground=C["border"]
             ).pack(side="left", padx=8)
    holder = tk.Frame(tab, bg=C["bg"])
    holder.pack(fill="both", expand=True)
    tk.Button(ctrl, text=t("btn_update"), font=("Segoe UI", 8, "bold"),
              bg=C["accent"], fg="white", bd=0, padx=10, pady=4, cursor="hand2",
              command=lambda: _draw(a, hr_max_var, holder)
              ).pack(side="left", padx=8)
    tk.Label(ctrl, text=t("hr_hint"),
             font=("Segoe UI", 8), fg=C["text_dim"], bg=C["surface"]).pack(side="left")
    info_btn(ctrl, t("hr_info_title"), t("info_hr")).pack(
        side="right", padx=16)
    _draw(a, hr_max_var, holder)


def _draw(a, hr_max_var, holder):
    clear(holder)
    try:
        hr_max = float(hr_max_var.get())
    except ValueError:
        hr_max = 190

    hrs    = [s.get("average_heartrate") for s in a.splits]
    speeds = [s.get("average_speed", 0)  for s in a.splits]
    paces  = [speed_to_pace(sp) for sp in speeds]

    fig = plt.Figure(figsize=(14, 7.5), facecolor=C["bg"])
    gs  = gridspec.GridSpec(1, 2, figure=fig,
                            left=0.07, right=0.97, top=0.88, bottom=0.12, wspace=0.35)

    # Zone distribution
    ax1 = fig.add_subplot(gs[0, 0])
    zone_secs  = a.hr_zone_seconds(hr_max)
    total_secs = sum(zone_secs.values()) or 1
    zone_keys = [z[0] for z in HR_ZONES]
    zone_labels = t("hr_zone_names")
    colors = [z[3] for z in HR_ZONES]
    pcts   = [zone_secs[n] / total_secs * 100 for n in zone_keys]
    times  = [fmt_time(int(zone_secs[n])) for n in zone_keys]
    bars = ax1.barh(zone_labels, pcts, color=colors, alpha=0.85, height=0.55)
    ax1.set_xlim(0, 108)
    ax1.set_xlabel(t("axis_pct_time"), fontsize=7)
    style_ax(ax1, t("chart_hr_zones"))
    ax1.invert_yaxis()
    for bar, pct, tm in zip(bars, pcts, times):
        if pct > 1:
            ax1.text(pct + 1, bar.get_y() + bar.get_height() / 2,
                     f"{pct:.1f}%  ({tm})", va="center",
                     fontsize=7, color=C["text"], fontfamily="monospace")
    ax1.text(0.99, 0.02, t("hr_max_annotation").format(val=f"{hr_max:.0f}"),
             transform=ax1.transAxes, ha="right", va="bottom",
             fontsize=7, color=C["text_dim"], fontfamily="monospace")

    # Scatter HR vs Pace
    ax2 = fig.add_subplot(gs[0, 1])
    valid = [(h, p) for h, p in zip(hrs, paces) if h and p]
    if valid:
        hv, pv = zip(*valid)
        ax2.scatter(hv, pv, c=[hr_zone_for(h, hr_max)[1] for h in hv],
                    alpha=0.85, s=60, edgecolors=C["border"], linewidths=0.5, zorder=3)
        ax2.invert_yaxis()
        if len(hv) >= 3:
            try:
                n   = len(hv); sx = sum(hv); sy = sum(pv)
                sxy = sum(x*y for x, y in zip(hv, pv))
                sxx = sum(x**2 for x in hv)
                d   = n * sxx - sx**2
                if d:
                    b  = (n * sxy - sx * sy) / d
                    aa = (sy - b * sx) / n
                    xr = [min(hv), max(hv)]
                    ax2.plot(xr, [aa + b*x for x in xr], color=C["yellow"],
                             lw=1.5, linestyle="--", label=t("hr_trend"), zorder=2)
                    ax2.legend(fontsize=7, facecolor=C["surface2"],
                               edgecolor=C["border"], labelcolor=C["text"])
            except Exception:
                pass
        for _, lo, hi, col in HR_ZONES:
            ax2.axvspan(hr_max * lo / 100, hr_max * hi / 100,
                        alpha=0.06, color=col, zorder=1)
        ax2.set_xlabel(t("axis_hr_bpm"), fontsize=7)
        ax2.set_ylabel(t("axis_pace_minkm"), fontsize=7)
        ax2.yaxis.set_major_formatter(FuncFormatter(
            lambda y, _: pace_label(y) if y > 0 else ""))
        handles = [mpatches.Patch(color=z[3], label=lbl) for z, lbl in zip(HR_ZONES, t("hr_zone_names"))]
        ax2.legend(handles=handles, fontsize=6.5, facecolor=C["surface2"],
                   edgecolor=C["border"], labelcolor=C["text"],
                   loc="upper left", title=t("hr_zones_label"), title_fontsize=6)
    else:
        ax2.text(0.5, 0.5, t("hr_insufficient"), ha="center", va="center",
                 color=C["text_dim"], transform=ax2.transAxes)
    style_ax(ax2, t("chart_hr_scatter"))

    fig.suptitle(t("chart_hr_analysis").format(name=a.name),
                 color=C["text"], fontsize=10, fontweight="bold", fontfamily="monospace")
    embed_mpl(holder, fig)
