# ── ui/tab_splits.py ──────────────────────────────────────────────────────────
import tkinter as tk
from tkinter import ttk
from config import C
from models import fmt_dist, fmt_time, fmt_pace, speed_to_pace
from ui.widgets import no_data, clear


def render(tab, activity):
    clear(tab)
    a = activity
    if not a.splits:
        no_data(tab, "Nessun dato split disponibile.")
        return

    tk.Label(tab, text="SPLITS PER CHILOMETRO",
             font=("Courier", 11, "bold"), fg=C["accent"],
             bg=C["surface"], pady=12).pack(fill="x")

    cols   = ["KM", "DISTANZA", "TEMPO", "PASSO", "VELOCITÀ", "HR", "DISLIVELLO", "CADENZA"]
    widths = [4, 9, 8, 8, 9, 7, 10, 9]

    outer = tk.Frame(tab, bg=C["bg"])
    outer.pack(fill="both", expand=True, padx=16, pady=10)

    hdr = tk.Frame(outer, bg=C["surface2"])
    hdr.pack(fill="x")
    for col, w in zip(cols, widths):
        tk.Label(hdr, text=col, font=("Courier", 8, "bold"),
                 fg=C["text_dim"], bg=C["surface2"],
                 width=w, anchor="center", pady=8).pack(side="left", padx=2)

    sc = tk.Canvas(outer, bg=C["bg"], bd=0, highlightthickness=0)
    sb = ttk.Scrollbar(outer, orient="vertical", command=sc.yview)
    sc.configure(yscrollcommand=sb.set)
    sb.pack(side="right", fill="y")
    sc.pack(fill="both", expand=True)
    inner = tk.Frame(sc, bg=C["bg"])
    sc.create_window((0, 0), window=inner, anchor="nw")
    inner.bind("<Configure>", lambda e: sc.configure(scrollregion=sc.bbox("all")))

    avg_pace = speed_to_pace(a.avg_speed)
    for i, s in enumerate(a.splits):
        speed = s.get("average_speed", 0)
        pace  = speed_to_pace(speed)
        hr    = s.get("average_heartrate")
        elev  = s.get("elevation_difference", 0)
        cad   = s.get("average_cadence")
        if pace and avg_pace:
            pc = C["green"] if pace < avg_pace * 0.97 else \
                 C["red"]   if pace > avg_pace * 1.03 else C["text"]
        else:
            pc = C["text"]
        bg = C["surface2"] if i % 2 == 0 else C["bg"]
        row = tk.Frame(inner, bg=bg)
        row.pack(fill="x")
        for (v, col), w in zip([
            (str(s.get("split", i+1)),          C["accent"]),
            (f"{s.get('distance',0)/1000:.3f}",  C["text"]),
            (fmt_time(s.get("moving_time", 0)),  C["blue"]),
            (fmt_pace(speed),                    pc),
            (f"{speed*3.6:.1f}",                 C["text"]),
            (f"{hr:.0f}" if hr else "–",         C["red"] if hr else C["text_dim"]),
            (f"{elev:+.1f}m",                    C["green"] if elev >= 0 else C["red"]),
            (f"{cad*2:.0f}" if cad else "–",     C["purple"]),
        ], widths):
            tk.Label(row, text=v, font=("Courier", 9), fg=col, bg=bg,
                     width=w, anchor="center", pady=6).pack(side="left", padx=2)

    tot = tk.Frame(inner, bg=C["surface"])
    tot.pack(fill="x", pady=(4, 0))
    for (v, col), w in zip([
        ("TOT",                    C["accent"]),
        (f"{a.distance/1000:.2f}", C["text"]),
        (fmt_time(a.moving_time),  C["blue"]),
        (a.avg_pace_str,           C["green"]),
        (f"{a.avg_speed*3.6:.1f}", C["text"]),
        (f"{a.avg_hr:.0f}" if a.avg_hr else "–", C["red"]),
        (f"{a.elev_gain:+.0f}m",   C["yellow"]),
        ("",                        C["text"]),
    ], widths):
        tk.Label(tot, text=v, font=("Courier", 9, "bold"), fg=col,
                 bg=C["surface"], width=w, anchor="center", pady=8).pack(side="left", padx=2)
