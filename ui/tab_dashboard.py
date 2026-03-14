# ── ui/tab_dashboard.py ───────────────────────────────────────────────────────
import tkinter as tk
import webbrowser
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
    sub_row = tk.Frame(hdr, bg=C["surface"])
    sub_row.pack(anchor="w", padx=24)
    tk.Label(sub_row, text=f"🏃  {a.sport_type.upper()}    📅  {a.date_str}{loc}",
             font=("Courier", 9), fg=C["text_dim"], bg=C["surface"]).pack(side="left")
    if a.strava_id:
        tk.Button(sub_row, text="🟠 Apri su Strava", font=("Courier", 8, "bold"),
                  bg=C["surface"], fg="#FC4C02", bd=0, padx=10, pady=0,
                  cursor="hand2", activebackground=C["surface2"],
                  command=lambda: webbrowser.open(
                      f"https://www.strava.com/activities/{a.strava_id}")
                  ).pack(side="left", padx=(16, 0))
    if a.description:
        tk.Label(hdr, text=f'💬  "{a.description}"',
                 font=("Courier", 9, "italic"), fg=C["text_dim"], bg=C["surface"],
                 wraplength=1000, justify="left").pack(anchor="w", padx=24, pady=(4, 0))

    _, body = make_scrollable(tab)

    # ── Statistiche principali — griglia 2×3 con stripe semantica ─────────────
    # Riga 0: metriche di corsa (distanza, tempo, passo)
    # Riga 1: metriche di fatica/tecnica (dislivello, tempo totale, passo best)
    section_label(body, "STATISTICHE PRINCIPALI")
    g = tk.Frame(body, bg=C["bg"])
    g.pack(fill="x", padx=20, pady=(0, 4))

    # (row, col, label, value, unit, color, stripe)
    main_stats = [
        (0, 0, "Distanza",       fmt_dist(a.distance),    "",        C["accent"],  C["accent"]),
        (0, 1, "Tempo attivo",   fmt_time(a.moving_time), "",        C["blue"],    C["blue"]),
        (0, 2, "Passo medio",    a.avg_pace_str,           "min/km",  C["green"],   C["green"]),
        (1, 0, "Dislivello +",   f"{a.elev_gain:.0f}",    "m",       C["yellow"],  C["yellow"]),
        (1, 1, "Tempo totale",   fmt_time(a.elapsed_time),"",        C["text"],    C["border"]),
        (1, 2, "Passo migliore", a.max_pace_str,           "min/km",  C["accent2"], C["accent2"]),
    ]
    for row, col, l, v, u, color, stripe in main_stats:
        StatCard(g, l, v, u, color, stripe=stripe).grid(
            row=row, column=col, padx=5, pady=5, sticky="nsew")
        g.columnconfigure(col, weight=1)

    # ── Frequenza cardiaca ─────────────────────────────────────────────────────
    if a.avg_hr or a.max_hr:
        section_label(body, "FREQUENZA CARDIACA")
        g2 = tk.Frame(body, bg=C["bg"])
        g2.pack(fill="x", padx=20, pady=(0, 4))
        cards = []
        if a.avg_hr:      cards.append(("HR Media",   f"{a.avg_hr:.0f}",        "bpm", C["red"],    C["red"]))
        if a.max_hr:      cards.append(("HR Massima", f"{a.max_hr:.0f}",        "bpm", C["red"],    C["red"]))
        if a.avg_cadence: cards.append(("Cadenza",    f"{a.avg_cadence*2:.0f}", "spm", C["purple"], C["purple"]))
        for i, (l, v, u, col, stripe) in enumerate(cards):
            StatCard(g2, l, v, u, col, stripe=stripe).grid(
                row=0, column=i, padx=5, pady=5, sticky="nsew")
            g2.columnconfigure(i, weight=1)

    # ── Dettagli aggiuntivi ────────────────────────────────────────────────────
    extra = []
    if a.calories:     extra.append(("Calorie",      f"{a.calories:.0f}",  "kcal", C["yellow"],  C["yellow"]))
    if a.suffer_score: extra.append(("Suffer Score", f"{a.suffer_score}",  "",     C["red"],     C["red"]))
    if a.achievements: extra.append(("Achievement",  f"{a.achievements}",  "",     C["accent"],  C["accent"]))
    if a.pr_count:     extra.append(("Record pers.", f"{a.pr_count}",      "PR",   C["green"],   C["green"]))
    if a.avg_watts:    extra.append(("Potenza",      f"{a.avg_watts:.0f}", "W",    C["purple"],  C["purple"]))
    if a.elev_high:    extra.append(("Quota max",    f"{a.elev_high:.0f}", "m",    C["text_dim"],C["border"]))
    if a.elev_low:     extra.append(("Quota min",    f"{a.elev_low:.0f}",  "m",    C["text_dim"],C["border"]))
    if a.device:       extra.append(("Dispositivo",  a.device,             "",     C["text_dim"],C["border"]))
    if a.gear:         extra.append(("Gear",         a.gear,               "",     C["text_dim"],C["border"]))
    if extra:
        section_label(body, "DETTAGLI AGGIUNTIVI")
        g3 = tk.Frame(body, bg=C["bg"])
        g3.pack(fill="x", padx=20, pady=(0, 4))
        for i, (l, v, u, col, stripe) in enumerate(extra):
            r, c_ = divmod(i, 3)
            StatCard(g3, l, v, u, col, stripe=stripe).grid(
                row=r, column=c_, padx=5, pady=5, sticky="nsew")
            g3.columnconfigure(c_, weight=1)

    # ── Indici di performance ──────────────────────────────────────────────────
    section_label(body, "INDICI DI PERFORMANCE")
    g4 = tk.Frame(body, bg=C["bg"])
    g4.pack(fill="x", padx=20, pady=(0, 20))
    perf = []
    if a.avg_hr and a.avg_speed:
        eff = (a.avg_speed * 3.6) / a.avg_hr * 100
        perf.append(("Indice efficienza", f"{eff:.1f}",             "",          C["blue"],    C["blue"]))
    if a.avg_speed:
        vmpm = a.avg_speed * 60
        vo2  = (0.000104 * vmpm**2 + 0.182258 * vmpm - 4.602796) / 0.80
        if vo2 > 0:
            perf.append(("VO2max stimato",    f"{vo2:.1f}",         "ml/kg/min", C["green"],   C["green"]))
    perf.append(("Velocità media",        f"{a.avg_speed * 3.6:.1f}", "km/h",   C["accent"],  C["accent"]))
    lost = a.elapsed_time - a.moving_time
    if lost > 0:
        perf.append(("Soste totali",      fmt_time(lost),           "",          C["text_dim"],C["border"]))
    for i, (l, v, u, col, stripe) in enumerate(perf):
        StatCard(g4, l, v, u, col, stripe=stripe).grid(
            row=0, column=i, padx=5, pady=5, sticky="nsew")
        g4.columnconfigure(i, weight=1)
