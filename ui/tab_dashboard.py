# ── ui/tab_dashboard.py ───────────────────────────────────────────────────────
import tkinter as tk
import tkinter.filedialog as fd
import tkinter.messagebox as mb
import webbrowser
from datetime import datetime, timedelta
from config import C
from models import fmt_dist, fmt_time
from ui.widgets import StatCard, make_scrollable, section_label, clear
from i18n import t


def _save_gpx(a):
    path = fd.asksaveasfilename(
        defaultextension=".gpx",
        filetypes=[("GPX files", "*.gpx"), ("All files", "*.*")],
        initialfile=f"{a.name.replace(' ', '_')}.gpx",
    )
    if not path:
        return

    try:
        start_dt = datetime.fromisoformat(a.start_date.replace("Z", ""))
    except Exception:
        start_dt = datetime.utcnow()

    pts = a.gps_points
    n = len(pts)
    elapsed = a.elapsed_time or 0

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<gpx version="1.1" creator="StravaViewer"',
        '  xmlns="http://www.topografix.com/GPX/1/1">',
        f'  <metadata><name>{a.name}</name></metadata>',
        "  <trk>",
        f"    <name>{a.name}</name>",
        f"    <type>{a.sport_type}</type>",
        "    <trkseg>",
    ]

    for i, (lat, lon) in enumerate(pts):
        if n > 1:
            pt_dt = start_dt + timedelta(seconds=elapsed * i / (n - 1))
        else:
            pt_dt = start_dt
        ts = pt_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        lines.append(f'      <trkpt lat="{lat:.6f}" lon="{lon:.6f}">')
        lines.append(f"        <time>{ts}</time>")
        lines.append("      </trkpt>")

    lines += ["    </trkseg>", "  </trk>", "</gpx>"]

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    mb.showinfo("GPX", f"Saved: {path}")


def render(tab, activity):
    clear(tab)
    a = activity

    # ── Activity header ───────────────────────────────────────────────────────
    # Outer frame: accent strip on the left + full-width content row
    hdr = tk.Frame(tab, bg=C["surface"])
    hdr.pack(fill="x")

    # Vertical accent strip (4 px, same visual language as StatCard stripes)
    tk.Frame(hdr, bg=C["accent"], width=4).pack(side="left", fill="y")

    # Inner content frame
    inner = tk.Frame(hdr, bg=C["surface"])
    inner.pack(side="left", fill="both", expand=True, padx=(20, 16), pady=18)

    # Top row: activity name (left) + Strava link button (right)
    top_row = tk.Frame(inner, bg=C["surface"])
    top_row.pack(fill="x")
    tk.Label(top_row, text=a.name, font=("Segoe UI", 17, "bold"),
             fg=C["text"], bg=C["surface"]).pack(side="left")
    if a.gps_points:
        tk.Button(top_row, text=t("stat_save_gpx"), font=("Segoe UI", 8, "bold"),
                  bg=C["surface2"], fg=C["green"], bd=0, padx=10, pady=4,
                  cursor="hand2", activebackground=C["border"], relief="flat",
                  command=lambda: _save_gpx(a)
                  ).pack(side="right", padx=(0, 6))
    if a.strava_id:
        tk.Button(top_row, text=t("stat_open_strava"), font=("Segoe UI", 8, "bold"),
                  bg=C["surface2"], fg=C["accent"], bd=0, padx=10, pady=4,
                  cursor="hand2", activebackground=C["border"], relief="flat",
                  command=lambda: webbrowser.open(
                      f"https://www.strava.com/activities/{a.strava_id}")
                  ).pack(side="right")

    # Bottom row: sport type, date, optional location
    loc = f"   📍 {a.city} {a.country}".strip() if (a.city or a.country) else ""
    tk.Label(inner, text=f"🏃  {a.sport_type.upper()}    📅  {a.date_str}{loc}",
             font=("Segoe UI", 9), fg=C["text_dim"], bg=C["surface"]).pack(anchor="w", pady=(4, 0))

    if a.description:
        tk.Label(inner, text=f'💬  "{a.description}"',
                 font=("Segoe UI", 9, "italic"), fg=C["text_dim"], bg=C["surface"],
                 wraplength=1100, justify="left").pack(anchor="w", pady=(4, 0))

    # Thin separator line below the header
    tk.Frame(tab, bg=C["border"], height=1).pack(fill="x")

    _, body = make_scrollable(tab)

    # ── Main statistics — 2×3 grid with semantic stripe ───────────────────────
    # Row 0: running metrics (distance, time, pace)
    # Row 1: effort/technique metrics (elevation, total time, best pace)
    section_label(body, t("section_main_stats"))
    g = tk.Frame(body, bg=C["bg"])
    g.pack(fill="x", padx=20, pady=(0, 4))

    # (row, col, label, value, unit, color, stripe)
    main_stats = [
        (0, 0, t("stat_distance"),    fmt_dist(a.distance),    "",        C["accent"],  C["accent"]),
        (0, 1, t("stat_moving_time"), fmt_time(a.moving_time), "",        C["blue"],    C["blue"]),
        (0, 2, t("stat_avg_pace"),    a.avg_pace_str,           "min/km",  C["green"],   C["green"]),
        (1, 0, t("stat_elev_gain"),   f"{a.elev_gain:.0f}",    "m",       C["yellow"],  C["yellow"]),
        (1, 1, t("stat_total_time"),  fmt_time(a.elapsed_time),"",        C["text"],    C["border"]),
        (1, 2, t("stat_best_pace"),   a.max_pace_str,           "min/km",  C["accent2"], C["accent2"]),
    ]
    for row, col, l, v, u, color, stripe in main_stats:
        StatCard(g, l, v, u, color, stripe=stripe).grid(
            row=row, column=col, padx=5, pady=5, sticky="nsew")
        g.columnconfigure(col, weight=1)

    # ── Heart rate ────────────────────────────────────────────────────────────
    if a.avg_hr or a.max_hr:
        section_label(body, t("section_heart_rate"))
        g2 = tk.Frame(body, bg=C["bg"])
        g2.pack(fill="x", padx=20, pady=(0, 4))
        cards = []
        if a.avg_hr:      cards.append((t("stat_avg_hr"),  f"{a.avg_hr:.0f}",        "bpm", C["red"],    C["red"]))
        if a.max_hr:      cards.append((t("stat_max_hr"),  f"{a.max_hr:.0f}",        "bpm", C["red"],    C["red"]))
        if a.avg_cadence: cards.append((t("stat_cadence"), f"{a.avg_cadence*2:.0f}", "spm", C["purple"], C["purple"]))
        for i, (l, v, u, col, stripe) in enumerate(cards):
            StatCard(g2, l, v, u, col, stripe=stripe).grid(
                row=0, column=i, padx=5, pady=5, sticky="nsew")
            g2.columnconfigure(i, weight=1)

    # ── Other details ────────────────────────────────────────────────────
    extra = []
    if a.calories:     extra.append((t("stat_calories"),     f"{a.calories:.0f}",  "kcal", C["yellow"],  C["yellow"]))
    if a.suffer_score: extra.append((t("stat_suffer_score"), f"{a.suffer_score}",  "",     C["red"],     C["red"]))
    if a.achievements: extra.append((t("stat_achievements"), f"{a.achievements}",  "",     C["accent"],  C["accent"]))
    if a.pr_count:     extra.append((t("stat_pr_count"),     f"{a.pr_count}",      "PR",   C["green"],   C["green"]))
    if a.avg_watts:    extra.append((t("stat_power"),        f"{a.avg_watts:.0f}", "W",    C["purple"],  C["purple"]))
    if a.elev_high:    extra.append((t("stat_elev_high"),    f"{a.elev_high:.0f}", "m",    C["text_dim"],C["border"]))
    if a.elev_low:     extra.append((t("stat_elev_low"),     f"{a.elev_low:.0f}",  "m",    C["text_dim"],C["border"]))
    if a.device:       extra.append((t("stat_device"),       a.device,             "",     C["text_dim"],C["border"]))
    if a.gear:         extra.append((t("stat_gear"),         a.gear,               "",     C["text_dim"],C["border"]))
    if extra:
        section_label(body, t("section_extra_details"))
        g3 = tk.Frame(body, bg=C["bg"])
        g3.pack(fill="x", padx=20, pady=(0, 4))
        for i, (l, v, u, col, stripe) in enumerate(extra):
            r, c_ = divmod(i, 3)
            StatCard(g3, l, v, u, col, stripe=stripe).grid(
                row=r, column=c_, padx=5, pady=5, sticky="nsew")
            g3.columnconfigure(c_, weight=1)

    # ── Performance indices ───────────────────────────────────────────────────
    section_label(body, t("section_perf_indices"))
    g4 = tk.Frame(body, bg=C["bg"])
    g4.pack(fill="x", padx=20, pady=(0, 20))
    perf = []
    if a.avg_hr and a.avg_speed:
        eff = (a.avg_speed * 3.6) / a.avg_hr * 100
        perf.append((t("stat_eff_index"),  f"{eff:.1f}",             "",          C["blue"],    C["blue"]))
    if a.avg_speed:
        vmpm = a.avg_speed * 60
        vo2  = (0.000104 * vmpm**2 + 0.182258 * vmpm - 4.602796) / 0.80
        if vo2 > 0:
            perf.append((t("stat_vo2max"), f"{vo2:.1f}",             "ml/kg/min", C["green"],   C["green"]))
    perf.append((t("stat_avg_speed"),      f"{a.avg_speed * 3.6:.1f}", "km/h",   C["accent"],  C["accent"]))
    lost = a.elapsed_time - a.moving_time
    if lost > 0:
        perf.append((t("stat_stops"),      fmt_time(lost),           "",          C["text_dim"],C["border"]))
    for i, (l, v, u, col, stripe) in enumerate(perf):
        StatCard(g4, l, v, u, col, stripe=stripe).grid(
            row=0, column=i, padx=5, pady=5, sticky="nsew")
        g4.columnconfigure(i, weight=1)
