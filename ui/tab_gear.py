# ── ui/tab_gear.py ─────────────────────────────────────────────────────────────
"""
Gear / Shoe Mileage Tracker — global tab.

Features:
  - Active gear cards with progress bar, status badge, editable threshold,
    dismiss button
  - Collapsible "Dismissed Gear" section for retired shoes
  - Monthly grouped-bar chart (last 12 months) with per-gear toggle buttons
"""

import tkinter as tk
from tkinter import ttk
from config import C
from models import pace_label, speed_to_pace
from ui.widgets import clear, no_data, section_label, info_btn, make_scrollable, FONT
from i18n import t

try:
    import matplotlib.pyplot as plt
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

_DEFAULT_THRESHOLD_KM = 700
_GEAR_COLORS = ["#fc4c02", "#58a6ff", "#3fb950", "#bc8cff", "#d29922"]


def _color_for(gear_name: str, active_names: list) -> str:
    """Stable color assignment by position in active list."""
    try:
        idx = active_names.index(gear_name)
    except ValueError:
        idx = 0
    return _GEAR_COLORS[idx % len(_GEAR_COLORS)]


# ── Public entry point ────────────────────────────────────────────────────────

def render(tab, storage_mgr):
    clear(tab)

    gear_list    = storage_mgr.gear_stats()
    monthly_raw  = storage_mgr.gear_monthly_km()
    gear_cfg     = storage_mgr.load_gear_settings()   # {name: {threshold, dismissed}}

    active       = [g for g in gear_list if not gear_cfg.get(g["name"], {}).get("dismissed", False)]
    retired      = [g for g in gear_list if     gear_cfg.get(g["name"], {}).get("dismissed", False)]
    active_names = [g["name"] for g in active]

    _render_header(tab, active)

    if not gear_list:
        no_data(tab, t("gear_no_data"))
        return

    def _refresh():
        render(tab, storage_mgr)

    _, scrollable = make_scrollable(tab)

    # ── Active gear ───────────────────────────────────────────────────────────
    section_label(scrollable, t("gear_section_gear"))
    if active:
        _render_gear_cards(scrollable, active, active_names, gear_cfg, storage_mgr, _refresh)
    else:
        tk.Label(scrollable, text=t("gear_no_active"),
                 font=FONT["body"], fg=C["text_dim"],
                 bg=C["bg"]).pack(anchor="w", padx=24, pady=8)

    # ── Dismissed gear (collapsible) ──────────────────────────────────────────
    if retired:
        _render_dismissed_section(scrollable, retired, active_names, storage_mgr, _refresh)

    # ── Monthly chart with toggles ────────────────────────────────────────────
    if HAS_MPL and monthly_raw and active:
        section_label(scrollable, t("gear_section_monthly"))
        _render_chart_section(scrollable, monthly_raw, active, active_names)


# ── Header ────────────────────────────────────────────────────────────────────

def _render_header(tab, active):
    hdr = tk.Frame(tab, bg=C["surface"])
    hdr.pack(fill="x")

    title_frame = tk.Frame(hdr, bg=C["surface"])
    title_frame.pack(side="left", padx=20, pady=10)
    tk.Label(title_frame, text=f"👟  {t('gear_title')}",
             font=FONT["section"], fg=C["accent"], bg=C["surface"]).pack(side="left")

    ib = info_btn(hdr, t("gear_info_title"), t("gear_info_body"))
    ib.pack(side="right", padx=16, pady=10)

    if active:
        total_km = sum(g["total_km"] for g in active)
        badge    = (f"{len(active)} {t('gear_badge_items')}  •  "
                    f"{total_km:.0f} km {t('gear_badge_tracked')}")
        tk.Label(hdr, text=badge, font=FONT["caption"], fg=C["yellow"],
                 bg=C["surface"], pady=4).pack(anchor="w", padx=20)


# ── Active gear cards ─────────────────────────────────────────────────────────

def _render_gear_cards(parent, gear_list, active_names, gear_cfg, storage_mgr, refresh_cb):
    for gear in gear_list:
        gear_name = gear["name"]
        color     = _color_for(gear_name, active_names)
        km        = gear["total_km"]
        threshold = float(gear_cfg.get(gear_name, {}).get("threshold", _DEFAULT_THRESHOLD_KM))
        pct       = km / threshold if threshold > 0 else 0.0

        card = tk.Frame(parent, bg=C["surface2"],
                        highlightthickness=1, highlightbackground=C["border"])
        card.pack(fill="x", padx=20, pady=6)

        tk.Frame(card, bg=color, width=5).pack(side="left", fill="y")
        body = tk.Frame(card, bg=C["surface2"])
        body.pack(side="left", fill="both", expand=True, padx=16, pady=12)

        # Row 1: name + status + dismiss button
        row1 = tk.Frame(body, bg=C["surface2"])
        row1.pack(fill="x")

        tk.Label(row1, text=f"👟  {gear_name}",
                 font=("Segoe UI", 11, "bold"), fg=C["text"],
                 bg=C["surface2"]).pack(side="left")

        if pct >= 1.0:
            badge_text, badge_color = f"  ⚠  {t('gear_status_replace')}", C["red"]
        elif pct >= 0.8:
            badge_text, badge_color = f"  →  {t('gear_status_warn')}", C["yellow"]
        else:
            badge_text, badge_color = f"  ✓  {t('gear_status_ok')}", C["green"]

        tk.Label(row1, text=badge_text, font=("Segoe UI", 9, "bold"),
                 fg=badge_color, bg=C["surface2"]).pack(side="left", padx=8)

        def _dismiss(gname=gear_name):
            storage_mgr.save_gear_dismissed(gname, True)
            refresh_cb()

        tk.Button(row1, text=t("gear_btn_dismiss"),
                  font=FONT["caption"], bg=C["surface"], fg=C["text_dim"],
                  activebackground=C["border"], activeforeground=C["text"],
                  bd=0, padx=8, pady=2, cursor="hand2", relief="flat",
                  command=_dismiss).pack(side="right")

        # Row 2: progress bar
        bar_outer = tk.Frame(body, bg=C["border"], height=10)
        bar_outer.pack(fill="x", pady=(8, 4))
        bar_outer.pack_propagate(False)
        fill_pct  = min(1.0, pct)
        bar_color = C["red"] if pct >= 1.0 else C["yellow"] if pct >= 0.8 else color
        tk.Frame(bar_outer, bg=bar_color, height=10).place(relwidth=fill_pct, relheight=1.0)

        pct_row = tk.Frame(body, bg=C["surface2"])
        pct_row.pack(fill="x")
        tk.Label(pct_row, text=f"{km:.1f} / {threshold:.0f} km  ({pct * 100:.0f}%)",
                 font=FONT["caption"], fg=C["text_dim"], bg=C["surface2"]).pack(side="left")

        # Row 3: stats strip
        stats_row = tk.Frame(body, bg=C["surface2"])
        stats_row.pack(fill="x", pady=(6, 4))
        avg_pace = pace_label(speed_to_pace(gear["avg_speed"])) if gear["avg_speed"] else "--:--"
        period   = f"{gear['first_used']} → {gear['last_used']}" if gear['first_used'] else "–"
        for piece, fg in [
            (f"{gear['run_count']} {t('gear_stat_runs')}", C["blue"]),
            (f"{t('gear_stat_avg_pace')}: {avg_pace}/km",  C["accent"]),
            (period,                                        C["text_dim"]),
        ]:
            tk.Label(stats_row, text=piece, font=FONT["caption"],
                     fg=fg, bg=C["surface2"]).pack(side="left", padx=(0, 20))

        # Row 4: threshold editor
        thresh_row = tk.Frame(body, bg=C["surface2"])
        thresh_row.pack(fill="x", pady=(4, 0))
        tk.Label(thresh_row, text=t("gear_threshold_label"), font=FONT["caption"],
                 fg=C["text_dim"], bg=C["surface2"]).pack(side="left")
        tvar = tk.StringVar(value=str(int(threshold)))
        tk.Entry(thresh_row, textvariable=tvar, width=6, font=FONT["caption"],
                 bg=C["surface"], fg=C["text"], insertbackground=C["text"],
                 relief="flat", bd=1, highlightthickness=1,
                 highlightbackground=C["border"],
                 highlightcolor=C["accent"]).pack(side="left", padx=(6, 4))
        tk.Label(thresh_row, text="km", font=FONT["caption"],
                 fg=C["text_dim"], bg=C["surface2"]).pack(side="left")

        def _on_save(gname=gear_name, var=tvar):
            try:
                val = float(var.get().replace(",", "."))
                if val > 0:
                    storage_mgr.save_gear_threshold(gname, val)
            except ValueError:
                pass

        tk.Button(thresh_row, text=t("gear_btn_save"), font=FONT["caption"],
                  bg=C["surface"], fg=C["accent"],
                  activebackground=C["surface2"], activeforeground=C["accent2"],
                  bd=0, padx=10, pady=2, cursor="hand2", relief="flat",
                  command=_on_save).pack(side="left", padx=(6, 0))


# ── Dismissed section (collapsible) ──────────────────────────────────────────

def _render_dismissed_section(parent, retired, active_names, storage_mgr, refresh_cb):
    # Header row with collapse toggle
    hdr_frame = tk.Frame(parent, bg=C["bg"])
    hdr_frame.pack(fill="x", padx=20, pady=(20, 0))

    collapsed_var = tk.BooleanVar(value=True)   # starts collapsed

    content_frame = tk.Frame(parent, bg=C["bg"])

    def _toggle():
        if collapsed_var.get():
            collapsed_var.set(False)
            toggle_btn.config(text="▼")
            content_frame.pack(fill="x", after=hdr_frame)
        else:
            collapsed_var.set(True)
            toggle_btn.config(text="▶")
            content_frame.pack_forget()

    toggle_btn = tk.Button(
        hdr_frame,
        text="▶",
        font=FONT["section"], fg=C["text_dim"], bg=C["bg"],
        activebackground=C["bg"], activeforeground=C["accent"],
        bd=0, cursor="hand2", relief="flat",
        command=_toggle,
    )
    toggle_btn.pack(side="left")

    section_text = f"  {t('gear_section_dismissed')}  ({len(retired)})"
    tk.Label(hdr_frame, text=section_text, font=FONT["section"],
             fg=C["text_dim"], bg=C["bg"]).pack(side="left")
    tk.Frame(hdr_frame, bg=C["border"], height=1).pack(
        side="left", fill="x", expand=True, padx=(12, 0), pady=8)

    # Retired cards (built now, shown only when expanded)
    for gear in retired:
        gear_name = gear["name"]
        km        = gear["total_km"]

        card = tk.Frame(content_frame, bg=C["surface2"],
                        highlightthickness=1, highlightbackground=C["border"])
        card.pack(fill="x", padx=20, pady=4)

        # Dim left stripe
        tk.Frame(card, bg=C["border"], width=5).pack(side="left", fill="y")
        body = tk.Frame(card, bg=C["surface2"])
        body.pack(side="left", fill="both", expand=True, padx=16, pady=10)

        row1 = tk.Frame(body, bg=C["surface2"])
        row1.pack(fill="x")

        tk.Label(row1, text=f"🗄  {gear_name}",
                 font=("Segoe UI", 10, "bold"), fg=C["text_dim"],
                 bg=C["surface2"]).pack(side="left")

        def _restore(gname=gear_name):
            storage_mgr.save_gear_dismissed(gname, False)
            refresh_cb()

        tk.Button(row1, text=t("gear_btn_restore"),
                  font=FONT["caption"], bg=C["surface"], fg=C["green"],
                  activebackground=C["border"], activeforeground=C["green"],
                  bd=0, padx=8, pady=2, cursor="hand2", relief="flat",
                  command=_restore).pack(side="right")

        stats_row = tk.Frame(body, bg=C["surface2"])
        stats_row.pack(fill="x", pady=(4, 0))
        period = f"{gear['first_used']} → {gear['last_used']}" if gear['first_used'] else "–"
        for piece, fg in [
            (f"{km:.0f} km",                                C["text_dim"]),
            (f"{gear['run_count']} {t('gear_stat_runs')}", C["text_dim"]),
            (period,                                        C["text_dim"]),
        ]:
            tk.Label(stats_row, text=piece, font=FONT["caption"],
                     fg=fg, bg=C["surface2"]).pack(side="left", padx=(0, 16))


# ── Chart section (toggles + grouped bars) ───────────────────────────────────

def _render_chart_section(parent, monthly_raw, active_gear, active_names):
    from collections import defaultdict
    from datetime import date
    from ui.widgets import embed_mpl

    # ── Build months list ──────────────────────────────────────────────────────
    months_12 = []
    y, m = date.today().year, date.today().month
    for _ in range(12):
        months_12.insert(0, f"{y:04d}-{m:02d}")
        m -= 1
        if m == 0:
            m, y = 12, y - 1

    # gear → month → km
    gear_month: dict = defaultdict(lambda: defaultdict(float))
    for row in monthly_raw:
        gear_month[row["gear"]][row["month"]] += row["km"]

    # ── Toggle buttons ─────────────────────────────────────────────────────────
    toggle_frame = tk.Frame(parent, bg=C["bg"])
    toggle_frame.pack(fill="x", padx=20, pady=(4, 6))

    tk.Label(toggle_frame, text=t("gear_chart_toggle_label"),
             font=FONT["caption"], fg=C["text_dim"], bg=C["bg"]).pack(side="left", padx=(0, 10))

    # BooleanVar per gear, all active by default
    gear_vars: dict[str, tk.BooleanVar] = {}
    for gear in active_gear:
        gear_vars[gear["name"]] = tk.BooleanVar(value=True)

    # Chart container (redrawn on toggle)
    chart_frame = tk.Frame(parent, bg=C["bg"])
    chart_frame.pack(fill="both", expand=True)

    def _redraw(*_):
        clear(chart_frame)
        enabled = [g for g in active_gear if gear_vars[g["name"]].get()]
        if not enabled:
            tk.Label(chart_frame, text=t("gear_chart_none_selected"),
                     font=FONT["body"], fg=C["text_dim"], bg=C["bg"],
                     pady=30).pack()
            return
        _draw_chart(chart_frame, months_12, gear_month, enabled, active_names)

    # Build toggle buttons and wire them
    for gear in active_gear:
        gname = gear["name"]
        color = _color_for(gname, active_names)
        var   = gear_vars[gname]

        btn_ref = [None]  # mutable container for the button reference

        def _make_update(v=var, c=color, br=btn_ref):
            def _update(*_):
                if v.get():
                    br[0].config(bg=c, fg="white",
                                 highlightbackground=c)
                else:
                    br[0].config(bg=C["surface2"], fg=C["text_dim"],
                                 highlightbackground=C["border"])
                _redraw()
            return _update

        update_fn = _make_update()

        btn = tk.Button(
            toggle_frame,
            text=gname,
            font=FONT["caption"],
            bg=color, fg="white",
            activebackground=C["border"], activeforeground=C["text"],
            bd=0, padx=10, pady=4,
            cursor="hand2", relief="flat",
            highlightthickness=1, highlightbackground=color,
            command=lambda v=var, fn=update_fn: [v.set(not v.get()), fn()],
        )
        btn.pack(side="left", padx=(0, 6))
        btn_ref[0] = btn

    _redraw()  # initial render


def _draw_chart(parent, months_12, gear_month, enabled_gear, active_names):
    from ui.widgets import embed_mpl

    n       = len(enabled_gear)
    x       = list(range(len(months_12)))
    bw      = 0.65 / n        # bar width per gear
    spacing = bw * 0.08       # small gap between bars

    fig = plt.Figure(figsize=(13, 3.8), facecolor=C["bg"])
    ax  = fig.add_subplot(111)
    ax.set_facecolor(C["surface"])
    fig.patch.set_facecolor(C["bg"])

    for gi, gear in enumerate(enabled_gear):
        gname  = gear["name"]
        color  = _color_for(gname, active_names)
        values = [gear_month[gname].get(mo, 0.0) for mo in months_12]
        # Centre the group of bars around each integer x position
        offset = (gi - (n - 1) / 2) * (bw + spacing)
        x_pos  = [xi + offset for xi in x]
        ax.bar(x_pos, values, width=bw, color=color, alpha=0.88,
               label=gname, zorder=2)

    ax.set_xticks(x)
    ax.set_xticklabels([mo[5:] for mo in months_12], fontsize=7, rotation=45)
    ax.set_ylabel("km", fontsize=7)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(C["border"])
    ax.spines["bottom"].set_color(C["border"])
    ax.tick_params(colors=C["text_dim"], labelsize=7)
    ax.yaxis.label.set_color(C["text_dim"])
    ax.yaxis.grid(True, color=C["border"], linestyle="--", linewidth=0.4, alpha=0.5)
    ax.xaxis.grid(False)
    ax.set_axisbelow(True)
    ax.set_title(t("gear_chart_title"), color=C["text"], fontsize=8.5,
                 fontweight="bold", fontfamily="sans-serif", pad=8)

    if n > 1:
        ax.legend(fontsize=7, facecolor=C["surface2"],
                  edgecolor=C["border"], labelcolor=C["text"], loc="upper left")

    fig.tight_layout(pad=1.5)
    embed_mpl(parent, fig)
