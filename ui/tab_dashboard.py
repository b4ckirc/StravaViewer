# ── ui/tab_dashboard.py ───────────────────────────────────────────────────────
import tkinter as tk
from config import C
from models import fmt_dist, fmt_time
from ui.widgets import StatCard, make_scrollable, section_label, clear


def render(tab, activity):
    clear(tab)
    a = activity

    # Header
    hdr = tk.Frame(tab, bg=C["surface"], pady=18)
    hdr.pack(fill="x")
    tk.Label(hdr, text=a.name, font=("Courier", 17, "bold"),
             fg=C["text"], bg=C["surface"]).pack(anchor="w", padx=24)
    loc = f"   📍 {a.city} {a.country}".strip() if (a.city or a.country) else ""
    tk.Label(hdr, text=f"🏃  {a.sport_type.upper()}    📅  {a.date_str}{loc}",
             font=("Courier", 9), fg=C["text_dim"], bg=C["surface"]).pack(anchor="w", padx=24)
    if a.description:
        tk.Label(hdr, text=f'💬  "{a.description}"',
                 font=("Courier", 9, "italic"), fg=C["text_dim"], bg=C["surface"],
                 wraplength=1000, justify="left").pack(anchor="w", padx=24, pady=(4, 0))

    _, body = make_scrollable(tab)

    # Statistiche principali
    section_label(body, "STATISTICHE PRINCIPALI")
    g = tk.Frame(body, bg=C["bg"])
    g.pack(fill="x", padx=20, pady=(0, 4))
    for i, (l, v, u, col) in enumerate([
        ("Distanza",       fmt_dist(a.distance),    "",        C["accent"]),
        ("Tempo attivo",   fmt_time(a.moving_time), "",        C["blue"]),
        ("Tempo totale",   fmt_time(a.elapsed_time),"",        C["text"]),
        ("Passo medio",    a.avg_pace_str,           "min/km", C["green"]),
        ("Passo migliore", a.max_pace_str,           "min/km", C["accent2"]),
        ("Dislivello +",   f"{a.elev_gain:.0f}",    "m",      C["yellow"]),
    ]):
        StatCard(g, l, v, u, col).grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
        g.columnconfigure(i, weight=1)

    # Cardiaca
    if a.avg_hr or a.max_hr:
        section_label(body, "FREQUENZA CARDIACA")
        g2 = tk.Frame(body, bg=C["bg"])
        g2.pack(fill="x", padx=20, pady=(0, 4))
        cards = []
        if a.avg_hr:      cards.append(("HR Media",   f"{a.avg_hr:.0f}",       "bpm", C["red"]))
        if a.max_hr:      cards.append(("HR Massima", f"{a.max_hr:.0f}",       "bpm", C["red"]))
        if a.avg_cadence: cards.append(("Cadenza",    f"{a.avg_cadence*2:.0f}","spm", C["purple"]))
        for i, (l, v, u, col) in enumerate(cards):
            StatCard(g2, l, v, u, col).grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
            g2.columnconfigure(i, weight=1)

    # Extra (senza kudos)
    extra = []
    if a.calories:     extra.append(("Calorie",      f"{a.calories:.0f}",  "kcal", C["yellow"]))
    if a.suffer_score: extra.append(("Suffer Score", f"{a.suffer_score}",  "",     C["red"]))
    if a.achievements: extra.append(("Achievement",  f"{a.achievements}",  "",     C["accent"]))
    if a.pr_count:     extra.append(("Record pers.", f"{a.pr_count}",      "PR",   C["green"]))
    if a.avg_watts:    extra.append(("Potenza",      f"{a.avg_watts:.0f}", "W",    C["purple"]))
    if a.elev_high:    extra.append(("Quota max",    f"{a.elev_high:.0f}", "m",    C["text_dim"]))
    if a.elev_low:     extra.append(("Quota min",    f"{a.elev_low:.0f}",  "m",    C["text_dim"]))
    if a.device:       extra.append(("Dispositivo",  a.device,             "",     C["text_dim"]))
    if a.gear:         extra.append(("Gear",         a.gear,               "",     C["text_dim"]))
    if extra:
        section_label(body, "DETTAGLI AGGIUNTIVI")
        g3 = tk.Frame(body, bg=C["bg"])
        g3.pack(fill="x", padx=20, pady=(0, 4))
        for i, (l, v, u, col) in enumerate(extra):
            r, c_ = divmod(i, 5)
            StatCard(g3, l, v, u, col).grid(row=r, column=c_, padx=5, pady=5, sticky="nsew")
            g3.columnconfigure(c_, weight=1)

    # Indici di performance
    section_label(body, "INDICI DI PERFORMANCE")
    g4 = tk.Frame(body, bg=C["bg"])
    g4.pack(fill="x", padx=20, pady=(0, 20))
    perf = []
    if a.avg_hr and a.avg_speed:
        eff = (a.avg_speed * 3.6) / a.avg_hr * 100
        perf.append(("Indice efficienza", f"{eff:.1f}", "", C["blue"]))
    if a.avg_speed:
        vmpm = a.avg_speed * 60
        vo2  = (0.000104 * vmpm**2 + 0.182258 * vmpm - 4.602796) / 0.80
        if vo2 > 0:
            perf.append(("VO2max stimato", f"{vo2:.1f}", "ml/kg/min", C["green"]))
    perf.append(("Velocità media", f"{a.avg_speed * 3.6:.1f}", "km/h", C["accent"]))
    lost = a.elapsed_time - a.moving_time
    if lost > 0:
        perf.append(("Soste totali", fmt_time(lost), "", C["text_dim"]))
    for i, (l, v, u, col) in enumerate(perf):
        StatCard(g4, l, v, u, col).grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
        g4.columnconfigure(i, weight=1)
