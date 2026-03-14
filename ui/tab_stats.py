# ── ui/tab_stats.py ───────────────────────────────────────────────────────────
"""
Tab statistiche globali su tutte le corse in libreria.
"""

import tkinter as tk
import json, math, os
from datetime import date, timedelta
from config import C
from models import fmt_time, fmt_pace
from ui.widgets import StatCard, make_scrollable, section_label, no_data, clear, info_btn

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib.gridspec as gridspec
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

SETTINGS_FILE = "settings.json"
MONTHS_IT = ["", "Gen", "Feb", "Mar", "Apr", "Mag", "Giu",
             "Lug", "Ago", "Set", "Ott", "Nov", "Dic"]


def _load_settings() -> dict:
    try:
        with open(SETTINGS_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_settings(s: dict):
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(s, f, indent=2)
    except Exception:
        pass


def render(tab, storage_mgr, on_open=None):
    clear(tab)

    tk.Label(tab, text="STATISTICHE GLOBALI",
             font=("Courier", 12, "bold"), fg=C["accent"],
             bg=C["surface"], pady=12).pack(fill="x")

    # Carica tutti i summary
    try:
        all_summaries = storage_mgr.list_all()
    except Exception as e:
        no_data(tab, f"Errore caricamento dati:\n{e}")
        return

    if not all_summaries:
        no_data(tab, "Nessuna corsa in libreria.\n\nScarica o importa delle attività prima.")
        return

    _, body = make_scrollable(tab)

    # ── Calcola aggregati ──────────────────────────────────────────────────────
    n_runs     = len(all_summaries)
    total_dist = sum(s.get("distance", 0) for s in all_summaries) / 1000
    total_time = sum(s.get("moving_time", 0) for s in all_summaries)
    total_elev = sum(s.get("elev_gain", 0) for s in all_summaries)
    avg_speeds = [s.get("avg_speed", 0) for s in all_summaries if s.get("avg_speed", 0) > 0]
    avg_speed  = sum(avg_speeds) / len(avg_speeds) if avg_speeds else 0
    hrs        = [s.get("avg_hr") for s in all_summaries if s.get("avg_hr")]
    avg_hr     = sum(hrs) / len(hrs) if hrs else None
    dists      = [s.get("distance", 0) / 1000 for s in all_summaries]
    avg_dist   = sum(dists) / len(dists) if dists else 0
    max_dist   = max(dists) if dists else 0
    cals       = [s.get("calories", 0) or 0 for s in all_summaries]
    total_cals = sum(cals)

    # ── Stat principali ────────────────────────────────────────────────────────
    section_label(body, "RIEPILOGO COMPLESSIVO")
    g = tk.Frame(body, bg=C["bg"])
    g.pack(fill="x", padx=20, pady=(0, 4))
    cards = [
        ("Corse totali",    f"{n_runs}",           "",          C["accent"]),
        ("Km totali",       f"{total_dist:.1f}",   "km",        C["blue"]),
        ("Ore totali",      fmt_time(total_time),  "",          C["green"]),
        ("Dislivello tot.", f"{total_elev:.0f}",   "m",         C["yellow"]),
        ("Passo medio",     fmt_pace(avg_speed),   "min/km",    C["accent2"]),
        ("HR media",        f"{avg_hr:.0f}" if avg_hr else "–", "bpm", C["red"]),
    ]
    for i, (l, v, u, col) in enumerate(cards):
        StatCard(g, l, v, u, col).grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
        g.columnconfigure(i, weight=1)

    section_label(body, "DETTAGLI")
    g2 = tk.Frame(body, bg=C["bg"])
    g2.pack(fill="x", padx=20, pady=(0, 4))
    extra = [
        ("Dist. media",   f"{avg_dist:.1f}",     "km",   C["text"]),
        ("Corsa più lunga", f"{max_dist:.1f}",   "km",   C["green"]),
        ("Calorie totali",  f"{total_cals:.0f}", "kcal", C["orange"]),
        ("Media km/sett.", _avg_km_per_week(all_summaries), "km", C["purple"]),
    ]
    for i, (l, v, u, col) in enumerate(extra):
        StatCard(g2, l, v, u, col).grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
        g2.columnconfigure(i, weight=1)

    # ── Obiettivo annuale ──────────────────────────────────────────────────────
    _render_annual_goal(body, all_summaries)

    # ── Statistiche per anno ───────────────────────────────────────────────────
    by_year = _group_by_year(all_summaries)
    if by_year:
        section_label(body, "STATISTICHE PER ANNO")
        tbl = tk.Frame(body, bg=C["surface2"],
                       highlightthickness=1, highlightbackground=C["border"])
        tbl.pack(fill="x", padx=20, pady=(0, 10))
        yr_cols   = ["ANNO", "CORSE", "KM TOT.", "TEMPO TOT.", "PASSO MEDIO", "↑ ELEV."]
        yr_widths = [8, 7, 10, 11, 12, 10]
        hrow = tk.Frame(tbl, bg=C["surface"])
        hrow.pack(fill="x")
        for col, w in zip(yr_cols, yr_widths):
            tk.Label(hrow, text=col, font=("Courier", 8, "bold"),
                     fg=C["text_dim"], bg=C["surface"],
                     width=w, anchor="center", pady=8).pack(side="left", padx=3)
        for i, (year, data) in enumerate(sorted(by_year.items(), reverse=True)):
            bg = C["surface2"] if i % 2 == 0 else C["surface"]
            row = tk.Frame(tbl, bg=bg)
            row.pack(fill="x")
            yr_vals = [
                (str(year),                          C["accent"]),
                (str(data["count"]),                 C["text"]),
                (f"{data['dist_km']:.1f} km",        C["blue"]),
                (fmt_time(data["time_sec"]),          C["text"]),
                (fmt_pace(data["avg_speed"]),         C["green"]),
                (f"{data['elev_gain']:.0f} m",        C["yellow"]),
            ]
            for (v, col), w in zip(yr_vals, yr_widths):
                tk.Label(row, text=v, font=("Courier", 9), fg=col, bg=bg,
                         width=w, anchor="center", pady=7).pack(side="left", padx=3)

        # ── Grafico km per anno ────────────────────────────────────────────────
        if HAS_MPL and len(by_year) > 1:
            section_label(body, "KM PER ANNO")
            cf = tk.Frame(body, bg=C["bg"])
            cf.pack(fill="x", padx=20, pady=(0, 20))

            years   = sorted(by_year.keys())
            km_vals = [by_year[y]["dist_km"] for y in years]
            n_vals  = [by_year[y]["count"]   for y in years]

            fig = plt.Figure(figsize=(12, 4), facecolor=C["bg"])
            gs  = gridspec.GridSpec(1, 2, figure=fig,
                                    left=0.07, right=0.97, top=0.85, bottom=0.15, wspace=0.35)

            ax1 = fig.add_subplot(gs[0, 0])
            bars = ax1.bar(years, km_vals, color=C["accent"], alpha=0.85, width=0.6)
            ax1.set_facecolor(C["surface"])
            ax1.set_title("KM PER ANNO", color=C["text"], fontsize=9,
                          fontweight="bold", fontfamily="monospace", pad=6)
            ax1.tick_params(colors=C["text_dim"], labelsize=7)
            ax1.set_ylabel("km", fontsize=7, color=C["text_dim"])
            for sp in ax1.spines.values(): sp.set_edgecolor(C["border"])
            ax1.grid(axis="y", color=C["border"], linestyle="--", linewidth=0.4, alpha=0.6)
            for bar, v in zip(bars, km_vals):
                ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10,
                         f"{v:.0f}", ha="center", fontsize=6.5, color=C["text"],
                         fontfamily="monospace")

            ax2 = fig.add_subplot(gs[0, 1])
            bars2 = ax2.bar(years, n_vals, color=C["blue"], alpha=0.85, width=0.6)
            ax2.set_facecolor(C["surface"])
            ax2.set_title("CORSE PER ANNO", color=C["text"], fontsize=9,
                          fontweight="bold", fontfamily="monospace", pad=6)
            ax2.tick_params(colors=C["text_dim"], labelsize=7)
            ax2.set_ylabel("n. corse", fontsize=7, color=C["text_dim"])
            for sp in ax2.spines.values(): sp.set_edgecolor(C["border"])
            ax2.grid(axis="y", color=C["border"], linestyle="--", linewidth=0.4, alpha=0.6)
            for bar, v in zip(bars2, n_vals):
                ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                         str(v), ha="center", fontsize=6.5, color=C["text"],
                         fontfamily="monospace")

            cnv = FigureCanvasTkAgg(fig, master=cf)
            cnv.draw()
            cnv.get_tk_widget().pack(fill="x")

    # ── Statistiche per mese (ultimi 12 mesi) ────────────────────────────────
    _render_monthly_stats(body, all_summaries)

    # ── Carico di allenamento (ATL / CTL / TSB) ───────────────────────────────
    if HAS_MPL:
        _render_training_load(body, all_summaries)

    # ── Analisi pendenza ──────────────────────────────────────────────────────
    if HAS_MPL:
        _render_grade_analysis(body, storage_mgr)

    # ── Curva di performance ──────────────────────────────────────────────────
    if HAS_MPL:
        _render_performance_curve(body, storage_mgr)

    # ── Previsione prestazioni ─────────────────────────────────────────────────
    if HAS_MPL:
        _render_race_prediction(body, storage_mgr)

    # ── Distribuzione distanze ─────────────────────────────────────────────────
    if HAS_MPL and dists:
        section_label(body, "DISTRIBUZIONE DISTANZE")
        cf3 = tk.Frame(body, bg=C["bg"])
        cf3.pack(fill="x", padx=20, pady=(0, 20))

        buckets = {"< 5 km": 0, "5–10 km": 0, "10–15 km": 0,
                   "15–21 km": 0, "21–42 km": 0, "> 42 km": 0}
        for d in dists:
            if   d < 5:   buckets["< 5 km"]    += 1
            elif d < 10:  buckets["5–10 km"]   += 1
            elif d < 15:  buckets["10–15 km"]  += 1
            elif d < 21:  buckets["15–21 km"]  += 1
            elif d < 42:  buckets["21–42 km"]  += 1
            else:         buckets["> 42 km"]   += 1

        labels = list(buckets.keys())
        values = list(buckets.values())
        colors_pie = [C["blue"], C["green"], C["yellow"],
                      C["accent"], C["red"], C["purple"]]

        fig3 = plt.Figure(figsize=(7, 4), facecolor=C["bg"])
        ax3  = fig3.add_subplot(111)
        ax3.set_facecolor(C["bg"])
        wedges, texts, autotexts = ax3.pie(
            values, labels=labels, colors=colors_pie,
            autopct=lambda p: f"{p:.1f}%" if p > 1 else "",
            startangle=90, textprops={"color": C["text"], "fontsize": 8,
                                       "fontfamily": "monospace"},
            wedgeprops={"edgecolor": C["border"], "linewidth": 1.2},
        )
        for at in autotexts:
            at.set_fontsize(7)
        ax3.set_title("DISTRIBUZIONE DISTANZE", color=C["text"], fontsize=9,
                      fontweight="bold", fontfamily="monospace", pad=10)

        cnv3 = FigureCanvasTkAgg(fig3, master=cf3)
        cnv3.draw()
        cnv3.get_tk_widget().pack()

    # ── Record personali ──────────────────────────────────────────────────────
    section_label(body, "RECORD PERSONALI")
    rec_outer = tk.Frame(body, bg=C["surface2"],
                         highlightthickness=1, highlightbackground=C["border"])
    rec_outer.pack(fill="x", padx=20, pady=(0, 24))

    hrow = tk.Frame(rec_outer, bg=C["surface"])
    hrow.pack(fill="x")
    for col_text, w in [("DISTANZA", 18), ("TEMPO", 10), ("ATTIVITÀ", 34), ("DATA", 14)]:
        tk.Label(hrow, text=col_text, font=("Courier", 8, "bold"),
                 fg=C["text_dim"], bg=C["surface"],
                 width=w, anchor="center", pady=8).pack(side="left", padx=3)

    try:
        records = storage_mgr.get_personal_records()
    except Exception:
        records = {}

    DIST_ORDER = [
        ("1k",            "🏃 1 km"),
        ("5k",            "🏃 5 km"),
        ("10k",           "🏃 10 km"),
        ("Half-Marathon", "🏃 Mezza Maratona"),
        ("Marathon",      "🏃 Maratona"),
    ]
    found_any = False
    for i, (key, label) in enumerate(DIST_ORDER):
        r = records.get(key)
        bg = C["surface2"] if i % 2 == 0 else C["surface"]
        row = tk.Frame(rec_outer, bg=bg)
        row.pack(fill="x")
        if r:
            found_any = True
            label_txt = label.replace("🏃", "🏆")
            time_str  = fmt_time(r["elapsed_time"])
            act_name  = (r["activity_name"] or "–")[:33]
            date_str  = r["date"]
            act_id    = r.get("activity_id")
        else:
            label_txt = label.replace("🏃", "  ")
            time_str  = "–"
            act_name  = "nessun dato"
            date_str  = "–"
            act_id    = None

        widgets = []
        for v, col, w, anc in [
            (label_txt, C["accent"],   18, "w"),
            (time_str,  C["green"],    10, "center"),
            (act_name,  C["text"],     34, "w"),
            (date_str,  C["text_dim"], 14, "center"),
        ]:
            lbl = tk.Label(row, text=v, font=("Courier", 9), fg=col, bg=bg,
                           width=w, anchor=anc, pady=7, padx=4)
            lbl.pack(side="left")
            widgets.append(lbl)

        if act_id and on_open:
            def _open(e, _id=act_id):
                for s in storage_mgr.list_all():
                    if s.get("strava_id") == _id:
                        on_open(s)
                        return
            for w in [row] + widgets:
                w.config(cursor="hand2")
                w.bind("<Button-1>", _open)

    if not found_any:
        try:
            found_names = storage_mgr.scan_effort_names()
        except Exception:
            found_names = set()
        if found_names:
            sample = ", ".join(f'"{n}"' for n in sorted(found_names)[:8])
            hint = (f"  Nomi trovati nel database: {sample}\n"
                    f"  I nomi attesi sono: \"1k\", \"5k\", \"10k\", "
                    f"\"Half-Marathon\", \"Marathon\".\n"
                    f"  Segnala i nomi trovati per aggiornare il riconoscimento.")
        else:
            hint = ("  Nessun best effort trovato. Le corse scaricate con activity:read_all\n"
                    "  includono automaticamente i best efforts.")
        tk.Label(rec_outer, text=hint,
                 font=("Courier", 8), fg=C["text_dim"], bg=C["surface2"],
                 pady=10, wraplength=760, justify="left").pack(anchor="w", padx=16)

    # ── Percorsi ricorrenti ────────────────────────────────────────────────────
    _render_route_analysis(body, storage_mgr, on_open)


# ── Geocoding helpers ─────────────────────────────────────────────────────────

def _reverse_geocode(lat: float, lon: float, storage_mgr) -> str:
    """Reverse geocoding con Nominatim. Cache su MongoDB o file JSON."""
    cached = storage_mgr.get_geocode(lat, lon)
    if cached is not None:
        return cached
    try:
        import urllib.request, json as _json
        url = (f"https://nominatim.openstreetmap.org/reverse"
               f"?lat={lat}&lon={lon}&format=json&zoom=10")
        req = urllib.request.Request(url, headers={"User-Agent": "StravaViewer/1.0"})
        with urllib.request.urlopen(req, timeout=5) as r:
            resp = r.read()
            print(f"[geocode] {lat:.3f},{lon:.3f} → HTTP {r.status}")
            addr = _json.loads(resp).get("address", {})
        city = (addr.get("city") or addr.get("town") or
                addr.get("village") or addr.get("municipality") or "")
        print(f"[geocode] città trovata: '{city}'")
    except Exception as e:
        print(f"[geocode] ERRORE {lat:.3f},{lon:.3f}: {type(e).__name__}: {e}")
        city = ""
    if city:  # salva solo se trovata, così i fallimenti vengono ritentati
        storage_mgr.set_geocode(lat, lon, city)
    return city


def _get_group_location(group: list, storage_mgr) -> str:
    """Restituisce la città del gruppo: prima dai metadati Strava, poi via Nominatim."""
    from collections import Counter
    cities = Counter(s.get("city", "") for s in group if s.get("city"))
    if cities:
        return cities.most_common(1)[0][0]
    for s in group:
        lat, lon = s.get("start_lat"), s.get("start_lon")
        if lat and lon:
            return _reverse_geocode(lat, lon, storage_mgr)
    return ""


def _group_immediate_location(group: list, storage_mgr) -> tuple[str, bool]:
    """
    Ritorna (testo_localizzazione, è_definitiva).
    Definitiva=True → nessun thread necessario.
    Definitiva=False → mostra placeholder e avvia geocoding in background.
    """
    from collections import Counter

    # 1. Città dai metadati Strava
    cities = Counter(s.get("city", "") for s in group if s.get("city"))
    if cities:
        return cities.most_common(1)[0][0], True

    # 2. Trova prime coordinate valide
    lat, lon = None, None
    for s in group:
        slat, slon = s.get("start_lat"), s.get("start_lon")
        if slat and slon:
            lat, lon = slat, slon
            break

    if lat is None:
        return "", True

    ew = "E" if lon >= 0 else "O"
    coord_str = f"{lat:.2f}°N  {abs(lon):.2f}°{ew}"

    # 3. Controlla cache persistente
    cached = storage_mgr.get_geocode(lat, lon)
    if cached:          # stringa non vuota → città trovata
        return cached, True

    # 4. Non in cache (o vecchio fallimento vuoto) → coordinate come placeholder, avvia thread
    return coord_str, False


# ── Percorsi ricorrenti ───────────────────────────────────────────────────────

def _render_route_analysis(body, storage_mgr, on_open):
    section_label(body, "PERCORSI RICORRENTI")

    try:
        groups = storage_mgr.get_route_groups(min_runs=3)
    except Exception:
        groups = []

    if not groups:
        tk.Label(body, text="  Nessun percorso ricorrente trovato (minimo 3 corse sullo stesso tracciato).",
                 font=("Courier", 9), fg=C["text_dim"], bg=C["bg"],
                 pady=12).pack(anchor="w", padx=20)
        return

    outer = tk.Frame(body, bg=C["bg"])
    outer.pack(fill="x", padx=20, pady=(0, 24))

    # ── Lista sinistra ────────────────────────────────────────────────────────
    list_panel = tk.Frame(outer, bg=C["surface2"],
                          highlightthickness=1, highlightbackground=C["border"],
                          width=230)
    list_panel.pack(side="left", fill="y", padx=(0, 10))
    list_panel.pack_propagate(False)

    tk.Label(list_panel, text=f"  {len(groups)} percorsi  (min. 3 corse)",
             font=("Courier", 8), fg=C["text_dim"], bg=C["surface2"],
             pady=6, anchor="w").pack(fill="x")
    tk.Frame(list_panel, bg=C["border"], height=1).pack(fill="x")

    list_canvas = tk.Canvas(list_panel, bg=C["surface2"], bd=0,
                            highlightthickness=0)
    list_sb = tk.Scrollbar(list_panel, orient="vertical",
                            command=list_canvas.yview)
    list_canvas.configure(yscrollcommand=list_sb.set)
    list_sb.pack(side="right", fill="y")
    list_canvas.pack(fill="both", expand=True)
    list_inner = tk.Frame(list_canvas, bg=C["surface2"])
    _lwid = list_canvas.create_window((0, 0), window=list_inner, anchor="nw")
    list_inner.bind("<Configure>",
                    lambda e: list_canvas.configure(
                        scrollregion=list_canvas.bbox("all")))
    list_canvas.bind("<Configure>",
                     lambda e: list_canvas.itemconfig(_lwid, width=e.width))

    # ── Pannello destro: grafico ───────────────────────────────────────────────
    chart_panel = tk.Frame(outer, bg=C["surface2"],
                           highlightthickness=1, highlightbackground=C["border"])
    chart_panel.pack(side="left", fill="both", expand=True)

    tk.Label(chart_panel,
             text="← Seleziona un percorso per vedere l'andamento del passo",
             font=("Courier", 10), fg=C["text_dim"], bg=C["surface2"],
             pady=60).pack(expand=True)

    # ── Coda tkinter-safe per aggiornamenti da thread ─────────────────────────
    import queue, threading
    loc_queue: queue.Queue = queue.Queue()

    def _poll_queue():
        try:
            while True:
                btn_ref, new_text = loc_queue.get_nowait()
                try:
                    btn_ref.config(text=new_text)
                except Exception:
                    pass
        except queue.Empty:
            pass
        try:
            list_inner.after(300, _poll_queue)
        except Exception:
            pass

    list_inner.after(300, _poll_queue)

    # ── Bottoni lista ─────────────────────────────────────────────────────────
    selected = {"btn": None}

    def _select(group, btn):
        if selected["btn"]:
            selected["btn"].config(bg=C["surface2"], fg=C["text"])
        btn.config(bg=C["accent"], fg="white")
        selected["btn"] = btn
        for w in chart_panel.winfo_children():
            w.destroy()
        _draw_route_chart(chart_panel, group, on_open, storage_mgr)

    pending = []   # gruppi che necessitano geocoding
    for i, group in enumerate(groups):
        from collections import Counter
        dist_km  = group[0].get("distance", 0) / 1000
        n        = len(group)
        names    = Counter(s.get("name", "") for s in group)
        top_name = names.most_common(1)[0][0] or f"{dist_km:.1f} km"
        dates    = [s.get("start_date", "")[:10] for s in group if s.get("start_date")]
        span     = f"{min(dates)[:7]} → {max(dates)[:7]}" if dates else ""

        location, is_final = _group_immediate_location(group, storage_mgr)
        loc_line = f"\n   📍 {location}" if location else ""
        label    = f"🔁 {top_name[:24]}\n   {dist_km:.1f} km · {n} corse\n   {span}{loc_line}"

        bg = C["surface"] if i % 2 == 0 else C["surface2"]
        btn = tk.Button(list_inner, text=label, font=("Courier", 8),
                        bg=bg, fg=C["text"], bd=0, padx=8, pady=6,
                        anchor="w", justify="left", cursor="hand2",
                        wraplength=200)
        btn.pack(fill="x", pady=1)
        btn.config(command=lambda g=group, b=btn: _select(g, b))

        # Accoda i gruppi che necessitano geocoding
        if not is_final:
            pending.append((btn, group, top_name, dist_km, n, span))

    # Un unico thread sequenziale — rispetta il rate limit di Nominatim (1 req/sec)
    if pending:
        def _geocode_all(items, q, sm):
            import time
            for b, g, top, dkm, n, sp in items:
                loc = _get_group_location(g, sm)
                if loc:  # aggiorna solo se trovata, altrimenti le coordinate restano
                    ll = f"\n   📍 {loc}"
                    q.put((b, f"🔁 {top[:24]}\n   {dkm:.1f} km · {n} corse\n   {sp}{ll}"))
                time.sleep(1.1)  # rispetta rate limit Nominatim
        threading.Thread(target=_geocode_all,
                         args=(pending, loc_queue, storage_mgr),
                         daemon=True).start()

    # Auto-seleziona il primo gruppo
    if list_inner.winfo_children():
        first_btn = list_inner.winfo_children()[0]
        first_btn.after(100, lambda: _select(groups[0], first_btn))


def _draw_route_chart(frame, group, on_open, storage_mgr=None):
    from collections import Counter
    import datetime as dt

    dist_km  = group[0].get("distance", 0) / 1000
    names    = Counter(s.get("name", "") for s in group)
    top_name = names.most_common(1)[0][0] or f"{dist_km:.1f} km"
    location = _get_group_location(group, storage_mgr) if storage_mgr else ""

    # Dati per il grafico
    dates, paces, hrs, runs = [], [], [], []
    for s in group:
        spd = s.get("avg_speed", 0)
        if spd <= 0:
            continue
        pace_min = (1000 / spd) / 60           # min/km
        date_str = s.get("start_date", "")[:10]
        try:
            d = dt.date.fromisoformat(date_str)
        except Exception:
            continue
        dates.append(d)
        paces.append(pace_min)
        hrs.append(s.get("avg_hr") or 0)
        runs.append(s)

    if not dates or not HAS_MPL:
        tk.Label(frame, text="Dati insufficienti per il grafico.",
                 font=("Courier", 9), fg=C["text_dim"], bg=C["surface2"]).pack(pady=20)
        return

    # ── Stats header ──────────────────────────────────────────────────────────
    hdr = tk.Frame(frame, bg=C["surface"])
    hdr.pack(fill="x", padx=0)

    best_pace  = min(paces)
    avg_pace   = sum(paces) / len(paces)
    first_pace = paces[0]
    last_pace  = paces[-1]
    trend_sec  = (first_pace - last_pace) * 60   # positivo = migliorato

    def _fmt_p(p):
        m = int(p); s = int((p - m) * 60)
        return f"{m}:{s:02d}"

    trend_txt = (f"↑ migliorato di {abs(trend_sec):.0f}s/km"
                 if trend_sec > 5 else
                 f"↓ peggiorato di {abs(trend_sec):.0f}s/km"
                 if trend_sec < -5 else "→ stabile")
    trend_col = C["green"] if trend_sec > 5 else C["red"] if trend_sec < -5 else C["text_dim"]

    loc_txt = f"  📍 {location}" if location else ""
    for txt, col, side in [
        (f"  {top_name[:40]}  —  {dist_km:.1f} km  ·  {len(dates)} corse{loc_txt}",
         C["text"], "left"),
        (f"miglior passo {_fmt_p(best_pace)}/km    "
         f"media {_fmt_p(avg_pace)}/km    {trend_txt}  ",
         trend_col, "right"),
    ]:
        tk.Label(hdr, text=txt, font=("Courier", 9), fg=col,
                 bg=C["surface"], pady=6).pack(side=side, padx=12)

    if storage_mgr:
        map_btn = tk.Button(
            hdr, text="📍 Mappa", font=("Courier", 10),
            fg=C["accent"], bg=C["surface"], relief="flat",
            cursor="hand2", bd=0,
            command=lambda g=group, sm=storage_mgr: _open_group_map(g, sm),
        )
        map_btn.pack(side="right", padx=6)

    # ── Grafico matplotlib ────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(7, 3.2), facecolor=C["surface2"])
    ax.set_facecolor(C["surface2"])

    # Scatter colorato: verde=veloce, rosso=lento
    norm_paces = [(p - best_pace) / (max(paces) - best_pace + 0.001) for p in paces]
    colors = [plt.cm.RdYlGn(1 - v) for v in norm_paces]  # type: ignore

    sc = ax.scatter(dates, paces, c=colors, s=60, zorder=3, edgecolors="none")

    # Trend line (regressione lineare semplice)
    if len(dates) >= 3:
        x_num = [(d - dates[0]).days for d in dates]
        n = len(x_num)
        sx, sy = sum(x_num), sum(paces)
        sxy = sum(xi * yi for xi, yi in zip(x_num, paces))
        sxx = sum(xi ** 2 for xi in x_num)
        denom = n * sxx - sx ** 2
        if denom:
            m_coef = (n * sxy - sx * sy) / denom
            b_coef = (sy - m_coef * sx) / n
            x0, x1 = x_num[0], x_num[-1]
            ax.plot([dates[0], dates[-1]],
                    [m_coef * x0 + b_coef, m_coef * x1 + b_coef],
                    color=C["accent"], linewidth=1.5, linestyle="--",
                    alpha=0.7, zorder=2)

    # Evidenzia best e last
    best_idx = paces.index(best_pace)
    ax.scatter([dates[best_idx]], [best_pace], s=120, color=C["green"],
               zorder=4, edgecolors="white", linewidths=1.2, label="Miglior corsa")
    ax.scatter([dates[-1]], [paces[-1]], s=100, color=C["accent"],
               zorder=4, edgecolors="white", linewidths=1.2, label="Ultima corsa")

    # Asse Y invertito: passo più basso = più veloce = in cima
    ax.invert_yaxis()

    def _ytick(p, _):
        m = int(p); s = int((p - m) * 60)
        return f"{m}:{s:02d}"

    import matplotlib.ticker as mticker
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(_ytick))
    ax.set_ylabel("Passo (min/km)", color=C["text_dim"], fontsize=8)
    ax.tick_params(colors=C["text_dim"], labelsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor(C["border"])
    ax.grid(axis="y", color=C["border"], linewidth=0.5, alpha=0.6)
    ax.legend(fontsize=7, facecolor=C["surface"], edgecolor=C["border"],
              labelcolor=C["text_dim"])
    fig.autofmt_xdate(rotation=30, ha="right")
    fig.tight_layout(pad=1.2)

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=0, pady=0)
    plt.close(fig)

    # ── Lista corse del gruppo (cliccabile se on_open) ────────────────────────
    runs_frame = tk.Frame(frame, bg=C["surface2"], height=130)
    runs_frame.pack(fill="x", padx=0)
    runs_frame.pack_propagate(False)
    tk.Frame(runs_frame, bg=C["border"], height=1).pack(fill="x")

    sc = tk.Canvas(runs_frame, bg=C["surface2"], bd=0, highlightthickness=0)
    sb = tk.Scrollbar(runs_frame, orient="vertical", command=sc.yview)
    sc.configure(yscrollcommand=sb.set)
    sb.pack(side="right", fill="y")
    sc.pack(fill="both", expand=True)
    sub = tk.Frame(sc, bg=C["surface2"])
    wid = sc.create_window((0, 0), window=sub, anchor="nw")
    sub.bind("<Configure>", lambda e: sc.configure(scrollregion=sc.bbox("all")))
    sc.bind("<Configure>", lambda e: sc.itemconfig(wid, width=e.width))
    sc.bind("<MouseWheel>", lambda e: sc.yview_scroll(int(-1*(e.delta/120)), "units"))

    for s, pace in sorted(zip(runs, paces), key=lambda x: x[0].get("start_date", ""), reverse=True):
        date_s = s.get("start_date", "")[:10]
        dist_s = f"{s.get('distance', 0) / 1000:.2f} km"
        hr_s   = f"  ❤ {s['avg_hr']:.0f}" if s.get("avg_hr") else ""
        line   = f"{date_s}   {dist_s}   {_fmt_p(pace)}/km{hr_s}   {s.get('name','')[:35]}"
        fg_col = C["green"] if pace == best_pace else C["text_dim"]
        lbl = tk.Label(sub, text=line, font=("Courier", 8), fg=fg_col,
                       bg=C["surface2"], anchor="w", cursor="hand2" if on_open else "")
        lbl.pack(fill="x", padx=12, pady=1)
        if on_open:
            lbl.bind("<Button-1>", lambda e, _s=s: _open_run(on_open, _s))


def _open_run(on_open, summary):
    on_open(summary)


def _open_group_map(group: list, storage_mgr):
    """Apre una mappa Folium nel browser con tutte le tracce del gruppo sovrapposte."""
    try:
        import folium
        from folium.plugins import Fullscreen
        import tempfile, webbrowser, os
    except ImportError:
        import tkinter.messagebox as mb
        mb.showerror("Folium non disponibile",
                     "Installa folium con: pip install folium")
        return

    tracks = storage_mgr.get_group_polylines(group)
    if not tracks:
        import tkinter.messagebox as mb
        mb.showinfo("Nessuna traccia", "Nessuna traccia GPS disponibile per questo gruppo.")
        return

    # Centro della mappa = media di tutti i punti
    all_pts = [pt for _, _, pts in tracks for pt in pts]
    center_lat = sum(p[0] for p in all_pts) / len(all_pts)
    center_lon = sum(p[1] for p in all_pts) / len(all_pts)

    m = folium.Map(location=[center_lat, center_lon], zoom_start=13, tiles=None)

    # ── Layer tiles ───────────────────────────────────────────────────────────
    folium.TileLayer("CartoDB positron", name="Mappa chiara", show=True).add_to(m)
    folium.TileLayer("OpenStreetMap",    name="OpenStreetMap", show=False).add_to(m)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri World Imagery", name="Satellite", show=False,
    ).add_to(m)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}",
        attr="Esri World Topo", name="Topografica", show=False,
    ).add_to(m)

    # ── Plugin fullscreen ─────────────────────────────────────────────────────
    Fullscreen(position="topleft", title="Schermo intero", title_cancel="Esci").add_to(m)

    # ── Lookup statistiche dal gruppo (match per data) ───────────────────────
    stats_by_date = {}
    for s in group:
        d = (s.get("start_date") or s.get("start_date_local") or "")[:10]
        if d:
            stats_by_date[d] = s

    def _fmt_time(sec):
        sec = int(sec or 0)
        h, m = divmod(sec, 3600)
        m, s = divmod(m, 60)
        return f"{h}h {m:02d}m" if h else f"{m}m {s:02d}s"

    def _fmt_pace(spd):
        if not spd or spd <= 0:
            return "—"
        p = (1000 / spd) / 60
        return f"{int(p)}:{int((p % 1) * 60):02d}/km"

    def _build_tooltip(name, date_s, stats):
        dist  = stats.get("distance", 0) / 1000
        time  = _fmt_time(stats.get("moving_time", 0))
        elev  = stats.get("elev_gain", 0)
        pace  = _fmt_pace(stats.get("avg_speed", 0))
        title = f"<b>{date_s}</b>" + (f" · {name[:40]}" if name else "")
        rows  = (f"📏 {dist:.2f} km&nbsp;&nbsp;&nbsp;"
                 f"⏱ {time}&nbsp;&nbsp;&nbsp;"
                 f"📈 +{elev:.0f} m&nbsp;&nbsp;&nbsp;"
                 f"🏃 {pace}")
        return f'{title}<br><span style="font-size:12px">{rows}</span>'

    # ── Tracce ordinate per data: un FeatureGroup per corsa ───────────────────
    colors = ["#e63946", "#457b9d", "#2a9d8f", "#e9c46a", "#f4a261",
              "#264653", "#8ecae6", "#c77dff", "#ffb703", "#fb8500"]

    sorted_tracks = sorted(tracks, key=lambda t: t[1])   # ordine cronologico
    for i, (name, date_s, pts) in enumerate(sorted_tracks):
        col   = colors[i % len(colors)]
        label = f"{date_s} · {name[:35]}" if name else date_s
        stats    = stats_by_date.get(date_s, {})
        tip_html = _build_tooltip(name, date_s, stats)
        fg = folium.FeatureGroup(
            name=f'<span style="color:{col};font-size:16px;line-height:1">■</span>'
                 f'&nbsp;<span style="font-size:12px">{label}</span>',
            show=True,
        )
        folium.PolyLine(pts, color=col, weight=3, opacity=0.85,
                        tooltip=folium.Tooltip(tip_html, sticky=True)).add_to(fg)
        if pts:
            folium.CircleMarker(pts[0], radius=5, color=col,
                                fill=True, fill_opacity=1,
                                tooltip=folium.Tooltip(tip_html, sticky=True)).add_to(fg)
        fg.add_to(m)

    # LayerControl con supporto HTML (per i colori inline)
    folium.LayerControl(collapsed=False, position="topright").add_to(m)

    # ── Checkbox "Seleziona tutti / Deseleziona tutti" ────────────────────────
    master_toggle_js = """
<script>
document.addEventListener('DOMContentLoaded', function () {
    setTimeout(function () {
        var overlaysDiv = document.querySelector('.leaflet-control-layers-overlays');
        if (!overlaysDiv) return;

        // Contenitore master
        var masterDiv = document.createElement('div');
        masterDiv.style.cssText = [
            'padding:5px 8px 7px 8px',
            'margin-bottom:5px',
            'border-bottom:2px solid #bbb',
            'display:flex',
            'align-items:center',
            'gap:6px',
        ].join(';');

        var masterChk = document.createElement('input');
        masterChk.type    = 'checkbox';
        masterChk.checked = true;
        masterChk.id      = 'sv-master-toggle';
        masterChk.style.cssText = 'width:14px;height:14px;cursor:pointer;accent-color:#457b9d';

        var masterLbl = document.createElement('label');
        masterLbl.htmlFor = 'sv-master-toggle';
        masterLbl.style.cssText = 'font-weight:bold;font-size:12px;cursor:pointer;user-select:none';
        masterLbl.textContent = 'Deseleziona tutti';

        function refreshLabel() {
            masterLbl.textContent = masterChk.checked ? 'Deseleziona tutti' : 'Seleziona tutti';
        }

        var isBulkToggling = false;

        masterChk.addEventListener('change', function () {
            isBulkToggling = true;
            var target = masterChk.checked;
            var boxes = overlaysDiv.querySelectorAll('input[type=checkbox]');
            boxes.forEach(function (inp) {
                if (inp !== masterChk && inp.checked !== target) inp.click();
            });
            isBulkToggling = false;
            refreshLabel();
        });

        // Aggiorna master se l'utente clicca le singole checkbox
        overlaysDiv.addEventListener('change', function (e) {
            if (e.target === masterChk || isBulkToggling) return;
            var boxes   = overlaysDiv.querySelectorAll('input[type=checkbox]');
            var checked = Array.from(boxes).filter(function(b){ return b !== masterChk && b.checked; }).length;
            var total   = boxes.length - 1; // escludi master
            masterChk.indeterminate = (checked > 0 && checked < total);
            masterChk.checked = (checked === total);
            refreshLabel();
        });

        masterDiv.appendChild(masterChk);
        masterDiv.appendChild(masterLbl);
        overlaysDiv.insertBefore(masterDiv, overlaysDiv.firstChild);
    }, 400);
});
</script>
"""
    m.get_root().html.add_child(folium.Element(master_toggle_js))

    with tempfile.NamedTemporaryFile(suffix=".html", delete=False,
                                     mode="w", encoding="utf-8") as f:
        m.save(f.name)
        tmp_path = f.name

    webbrowser.open(f"file:///{tmp_path.replace(os.sep, '/')}")


# ── Helper ────────────────────────────────────────────────────────────────────

def _group_by_year(summaries):
    from collections import defaultdict
    by_year = defaultdict(lambda: {"count": 0, "dist_km": 0.0,
                                   "time_sec": 0, "elev_gain": 0.0,
                                   "speed_sum": 0.0, "speed_n": 0})
    for s in summaries:
        y = (s.get("start_date") or "")[:4]
        if not y.isdigit():
            continue
        y = int(y)
        by_year[y]["count"]    += 1
        by_year[y]["dist_km"]  += s.get("distance", 0) / 1000
        by_year[y]["time_sec"] += s.get("moving_time", 0)
        by_year[y]["elev_gain"]+= s.get("elev_gain", 0)
        sp = s.get("avg_speed", 0)
        if sp > 0:
            by_year[y]["speed_sum"] += sp
            by_year[y]["speed_n"]   += 1
    for y in by_year:
        n = by_year[y]["speed_n"]
        by_year[y]["avg_speed"] = by_year[y]["speed_sum"] / n if n else 0
    return dict(by_year)

def _avg_km_per_week(summaries):
    if len(summaries) < 2:
        return "–"
    from datetime import datetime
    dates = []
    for s in summaries:
        try:
            dates.append(datetime.fromisoformat(s.get("start_date","").replace("Z","")))
        except Exception:
            pass
    if not dates:
        return "–"
    span_days = (max(dates) - min(dates)).days or 1
    weeks     = span_days / 7
    total_km  = sum(s.get("distance", 0) for s in summaries) / 1000
    return f"{total_km / weeks:.1f}"


# ── Sezione obiettivo annuale ──────────────────────────────────────────────────

def _render_annual_goal(body, all_summaries):
    section_label(body, "OBIETTIVO ANNUALE")
    settings    = _load_settings()
    current_year = date.today().year

    year_km = sum(
        s.get("distance", 0) for s in all_summaries
        if (s.get("start_date") or "")[:4] == str(current_year)
    ) / 1000

    target_km = settings.get("annual_km_goal", 1000.0)
    pct       = min(1.0, year_km / target_km) if target_km > 0 else 0.0

    outer = tk.Frame(body, bg=C["surface2"],
                     highlightthickness=1, highlightbackground=C["border"])
    outer.pack(fill="x", padx=20, pady=(0, 12))

    row_f = tk.Frame(outer, bg=C["surface2"])
    row_f.pack(fill="x", padx=16, pady=10)

    tk.Label(row_f, text=f"Obiettivo {current_year}:",
             font=("Courier", 9), fg=C["text_dim"],
             bg=C["surface2"]).pack(side="left")

    goal_var = tk.StringVar(value=str(int(target_km)))
    tk.Entry(row_f, textvariable=goal_var, font=("Courier", 10),
             bg=C["surface"], fg=C["text"], width=7, bd=0,
             insertbackground=C["text"],
             highlightthickness=1, highlightbackground=C["border"]
             ).pack(side="left", padx=6)
    tk.Label(row_f, text="km", font=("Courier", 9), fg=C["text_dim"],
             bg=C["surface2"]).pack(side="left")

    def _save():
        try:
            val = float(goal_var.get())
            settings["annual_km_goal"] = val
            _save_settings(settings)
        except Exception:
            pass

    tk.Button(row_f, text="✓ Salva", font=("Courier", 8, "bold"),
              bg=C["accent"], fg="white", bd=0, padx=8, pady=3,
              cursor="hand2", command=_save).pack(side="left", padx=10)

    # Testo riepilogo
    col_txt = C["green"] if pct >= 1.0 else C["accent"]
    tk.Label(row_f,
             text=f"{year_km:.0f} / {target_km:.0f} km  ({pct * 100:.1f}%)",
             font=("Courier", 10, "bold"), fg=col_txt,
             bg=C["surface2"]).pack(side="right", padx=8)

    # Barra di avanzamento (Canvas)
    bar_frame = tk.Frame(outer, bg=C["surface2"])
    bar_frame.pack(fill="x", padx=16, pady=(0, 12))

    bar_cv = tk.Canvas(bar_frame, height=16, bg=C["surface"],
                       bd=0, highlightthickness=0)
    bar_cv.pack(fill="x")

    def _draw(e=None):
        w = bar_cv.winfo_width()
        if w < 2:
            return
        bar_cv.delete("all")
        bar_cv.create_rectangle(0, 0, w, 16, fill=C["surface"], outline="")
        filled_w = int(w * pct)
        fill_col = C["green"] if pct >= 1.0 else C["accent"]
        if filled_w > 0:
            bar_cv.create_rectangle(0, 0, filled_w, 16,
                                    fill=fill_col, outline="")

    bar_cv.bind("<Configure>", _draw)
    body.after(120, _draw)


# ── Sezione statistiche mensili ────────────────────────────────────────────────

def _render_monthly_stats(body, all_summaries):
    """Tabella + grafico degli ultimi 12 mesi."""
    from collections import defaultdict
    by_month = defaultdict(lambda: {
        "count": 0, "dist_km": 0.0, "time_sec": 0,
        "elev_gain": 0.0, "speed_sum": 0.0, "speed_n": 0,
    })
    for s in all_summaries:
        ym = (s.get("start_date") or "")[:7]
        if len(ym) < 7 or not ym[:4].isdigit():
            continue
        by_month[ym]["count"]    += 1
        by_month[ym]["dist_km"]  += s.get("distance", 0) / 1000
        by_month[ym]["time_sec"] += s.get("moving_time", 0)
        by_month[ym]["elev_gain"]+= s.get("elev_gain", 0)
        sp = s.get("avg_speed", 0)
        if sp > 0:
            by_month[ym]["speed_sum"] += sp
            by_month[ym]["speed_n"]   += 1

    if not by_month:
        return

    # Calcola avg_speed per mese
    months_sorted = sorted(by_month.keys(), reverse=True)[:12]  # ultimi 12 mesi
    months_sorted.sort()  # ora in ordine cronologico

    section_label(body, "STATISTICHE PER MESE  (ultimi 12 mesi)")
    tbl = tk.Frame(body, bg=C["surface2"],
                   highlightthickness=1, highlightbackground=C["border"])
    tbl.pack(fill="x", padx=20, pady=(0, 8))

    mo_cols   = ["MESE", "CORSE", "KM TOT.", "TEMPO TOT.", "PASSO MEDIO", "↑ ELEV."]
    mo_widths = [9, 7, 10, 11, 12, 10]

    hrow = tk.Frame(tbl, bg=C["surface"])
    hrow.pack(fill="x")
    for col, w in zip(mo_cols, mo_widths):
        tk.Label(hrow, text=col, font=("Courier", 8, "bold"),
                 fg=C["text_dim"], bg=C["surface"],
                 width=w, anchor="center", pady=8).pack(side="left", padx=3)

    for i, ym in enumerate(reversed(months_sorted)):
        d   = by_month[ym]
        n   = d["speed_n"]
        avg = d["speed_sum"] / n if n else 0
        bg  = C["surface2"] if i % 2 == 0 else C["surface"]
        row = tk.Frame(tbl, bg=bg)
        row.pack(fill="x")
        yr, mo = int(ym[:4]), int(ym[5:7])
        mo_vals = [
            (f"{MONTHS_IT[mo]} {yr}",          C["accent"]),
            (str(d["count"]),                   C["text"]),
            (f"{d['dist_km']:.1f} km",          C["blue"]),
            (fmt_time(d["time_sec"]),            C["text"]),
            (fmt_pace(avg),                      C["green"]),
            (f"{d['elev_gain']:.0f} m",          C["yellow"]),
        ]
        for (v, col), w in zip(mo_vals, mo_widths):
            tk.Label(row, text=v, font=("Courier", 9), fg=col, bg=bg,
                     width=w, anchor="center", pady=7).pack(side="left", padx=3)

    # Grafico km per mese
    if HAS_MPL and len(months_sorted) > 1:
        cf = tk.Frame(body, bg=C["bg"])
        cf.pack(fill="x", padx=20, pady=(0, 20))

        labels   = []
        km_vals  = []
        n_vals   = []
        for ym in months_sorted:
            yr, mo = int(ym[:4]), int(ym[5:7])
            labels.append(f"{MONTHS_IT[mo]}\n{yr}")
            km_vals.append(by_month[ym]["dist_km"])
            n_vals.append(by_month[ym]["count"])

        fig = plt.Figure(figsize=(12, 3.5), facecolor=C["bg"])
        gs  = gridspec.GridSpec(1, 1, figure=fig,
                                left=0.05, right=0.98, top=0.82, bottom=0.18)
        ax  = fig.add_subplot(gs[0, 0])
        bars = ax.bar(range(len(labels)), km_vals, color=C["blue"],
                      alpha=0.85, width=0.6)
        ax.set_facecolor(C["surface"])
        ax.set_title("KM PER MESE", color=C["text"], fontsize=9,
                     fontweight="bold", fontfamily="monospace", pad=6)
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, fontsize=6)
        ax.tick_params(colors=C["text_dim"], labelsize=7)
        ax.set_ylabel("km", fontsize=7, color=C["text_dim"])
        for sp in ax.spines.values():
            sp.set_edgecolor(C["border"])
        ax.grid(axis="y", color=C["border"], linestyle="--",
                linewidth=0.4, alpha=0.6)
        for bar, v in zip(bars, km_vals):
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.5,
                    f"{v:.0f}", ha="center", fontsize=6, color=C["text"],
                    fontfamily="monospace")

        cnv = FigureCanvasTkAgg(fig, master=cf)
        cnv.draw()
        cnv.get_tk_widget().pack(fill="x")


# ── Sezione carico di allenamento (ATL / CTL / TSB) ───────────────────────────

def _trimp(s: dict) -> float:
    """TRIMP semplificato per una sessione."""
    t_min = s.get("moving_time", 0) / 60.0
    hr    = s.get("avg_hr")
    if hr and hr > 0:
        # Banister TRIMP con hrRest=60, hrMax=190
        hr_ratio = max(0.0, min(1.0, (hr - 60) / (190 - 60)))
        return t_min * hr_ratio * 0.64 * math.exp(1.92 * hr_ratio)
    # Fallback senza FC: distanza in km come proxy
    return s.get("distance", 0) / 1000.0


def _compute_training_load(summaries):
    """Ritorna (dates, atl_list, ctl_list, tsb_list) per l'ultimo anno."""
    from collections import defaultdict
    daily = defaultdict(float)
    for s in summaries:
        d = (s.get("start_date") or "")[:10]
        if len(d) == 10:
            daily[d] += _trimp(s)

    if not daily:
        return [], [], [], []

    d_end   = date.today()
    d_start = d_end - timedelta(days=364)

    k_atl = math.exp(-1 / 7)
    k_ctl = math.exp(-1 / 42)

    # Inizializza ATL/CTL sullo storico precedente (tutto il database)
    all_dates = sorted(daily.keys())
    atl = ctl = 0.0
    if all_dates and all_dates[0] < d_start.isoformat():
        cur = date.fromisoformat(all_dates[0])
        while cur < d_start:
            load = daily.get(cur.isoformat(), 0.0)
            atl  = atl * k_atl + load * (1 - k_atl)
            ctl  = ctl * k_ctl + load * (1 - k_ctl)
            cur += timedelta(days=1)

    dates_out, atl_out, ctl_out, tsb_out = [], [], [], []
    cur = d_start
    while cur <= d_end:
        load = daily.get(cur.isoformat(), 0.0)
        atl  = atl * k_atl + load * (1 - k_atl)
        ctl  = ctl * k_ctl + load * (1 - k_ctl)
        dates_out.append(cur)
        atl_out.append(atl)
        ctl_out.append(ctl)
        tsb_out.append(ctl - atl)
        cur += timedelta(days=1)

    return dates_out, atl_out, ctl_out, tsb_out


def _render_training_load(body, all_summaries):
    dates, atl, ctl, tsb = _compute_training_load(all_summaries)
    if not dates:
        return

    section_label(body, "CARICO DI ALLENAMENTO  (ultimi 12 mesi)")

    # Legenda testuale + bottone info
    leg_f = tk.Frame(body, bg=C["bg"])
    leg_f.pack(fill="x", padx=20, pady=(0, 4))
    for txt, col in [
        ("■ CTL – Fitness (42 gg)", C["blue"]),
        ("■ ATL – Fatica (7 gg)",   C["red"]),
        ("■ TSB – Forma (CTL-ATL)", C["green"]),
    ]:
        tk.Label(leg_f, text=txt, font=("Courier", 8), fg=col,
                 bg=C["bg"]).pack(side="left", padx=10)
    info_btn(leg_f, "Come leggere il grafico del Carico di Allenamento",
             _INFO_TRAINING_LOAD).pack(side="right", padx=8)

    cf = tk.Frame(body, bg=C["bg"])
    cf.pack(fill="x", padx=20, pady=(0, 20))

    import matplotlib.dates as mdates
    fig = plt.Figure(figsize=(12, 3.5), facecolor=C["bg"])
    ax  = fig.add_subplot(111)
    ax.set_facecolor(C["surface"])

    ax.plot(dates, ctl, color=C["blue"],  linewidth=1.4, label="CTL (Fitness)")
    ax.plot(dates, atl, color=C["red"],   linewidth=1.0,
            linestyle="--", label="ATL (Fatica)")
    ax.plot(dates, tsb, color=C["green"], linewidth=1.0,
            linestyle=":",  label="TSB (Forma)")
    ax.axhline(0, color=C["border"], linewidth=0.6)

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %y"))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    fig.autofmt_xdate(rotation=35, ha="right")
    ax.tick_params(colors=C["text_dim"], labelsize=7)
    ax.set_ylabel("TRIMP", fontsize=7, color=C["text_dim"])
    for sp in ax.spines.values():
        sp.set_edgecolor(C["border"])
    ax.grid(color=C["border"], linestyle="--", linewidth=0.4, alpha=0.5)
    fig.subplots_adjust(left=0.06, right=0.98, top=0.92, bottom=0.22)

    cnv = FigureCanvasTkAgg(fig, master=cf)
    cnv.draw()
    cnv.get_tk_widget().pack(fill="x")


# ── Testo informativo — Carico di allenamento ─────────────────────────────────

_INFO_TRAINING_LOAD = """
## IL MODELLO PMC — Performance Management Chart

Questo grafico usa il modello di Banister (1991), adottato da TrainingPeaks, Garmin, WKO e dai coach professionisti di tutto il mondo. Si basa sul calcolo del TRIMP (TRaining IMPulse) di ogni sessione, una misura che combina durata e intensità cardiaca.

# COME VIENE CALCOLATO IL TRIMP

Per ogni corsa:  TRIMP = durata (min) × (FC_media − FC_riposo) / (FC_max − FC_riposo) × fattore

Il fattore esponenziale (Banister) amplifica le sessioni ad alta FC: correre 30 minuti a frequenza cardiaca elevata vale più del doppio rispetto a correre 30 minuti a FC bassa. Quando la FC non è disponibile, viene usata la distanza in km come stima approssimativa.

---

# LE TRE LINEE DEL GRAFICO

# CTL — FITNESS (linea blu continua)

Chronic Training Load: media ponderata esponenziale degli ultimi 42 giorni. Rappresenta la tua forma fisica di base, il livello di adattamento accumulato nel tempo con la costanza negli allenamenti.

• Sale lentamente: servono settimane di lavoro regolare per alzarla.
• Scende lentamente: non crolla subito con qualche giorno di riposo.
• Un CTL alto significa che il tuo corpo è adattato a reggere grandi volumi.

# ATL — FATICA (linea rossa tratteggiata)

Acute Training Load: media ponderata esponenziale degli ultimi 7 giorni. Rappresenta la fatica accumulata di recente.

• Reagisce rapidamente: sale dopo sessioni intense, scende in pochi giorni di riposo.
• Dopo una settimana di allenamento intenso, ATL supera CTL: sei stanco ma stai costruendo.
• Dopo un tapering, ATL scende sotto CTL: sei fresco e pronto.

# TSB — FORMA (linea verde punteggiata)

Training Stress Balance = CTL − ATL. È l'indicatore chiave della tua prontezza a gareggiare o a dare il meglio.

• TSB positivo → sei riposato. Il corpo ha recuperato e puoi esprimere il potenziale accumulato.
• TSB negativo → stai accumulando fatica. Normale durante un blocco di allenamento intenso.
• TSB molto negativo (< −20) → rischio di sovrallenamento. Inserisci giorni di recupero.
• TSB molto positivo (> +20) → sei "de-allenato": se rimani fermo troppo a lungo perdi forma.

---

# COME USARLO IN PRATICA

# Prima di una gara importante

Pianifica un tapering di 10–14 giorni: riduci il volume del 30–40% mantenendo qualche stimolo di qualità. Vedrai ATL scendere e TSB salire progressivamente in territorio positivo.

Il "sweet spot" per gareggiare è TSB tra +5 e +15: abbastanza riposato da esprimersi al meglio, abbastanza allenato da avere CTL alto.

# Durante un blocco di carico

È normale avere TSB molto negativo. L'obiettivo è spingere CTL verso l'alto. Poi, con un breve recupero, ATL scende e TSB torna positivo: questo è il momento in cui si "raccoglie" il miglioramento.

# Per monitorare i progressi

Un CTL crescente nel tempo = stai migliorando la tua capacità di sopportare il lavoro. Un CTL stagnante o in calo = stai correndo troppo poco, troppo lento, o stai recuperando male.

---

NOTA DEL COACH: i valori assoluti di CTL, ATL e TSB dipendono dalla tua storia di allenamento e contano meno del trend. Non confrontare i tuoi numeri con quelli degli altri: confronta i tuoi numeri di oggi con quelli di 3, 6, 12 mesi fa. Se CTL è più alto della stessa settimana dell'anno scorso, stai progredendo.
"""


# ── Sezione analisi pendenza (Grade Analysis) ──────────────────────────────────

_GRADE_BINS = [
    ("< −8%",    -1e9, -8,  "#4477cc"),
    ("−8 a −3%", -8,   -3,  "#66aadd"),
    ("−3 a 0%",  -3,    0,  "#55aa55"),
    ("0 a 3%",    0,    3,  "#ddaa33"),
    ("3 a 8%",    3,    8,  "#dd7722"),
    ("> 8%",      8,   1e9, "#cc3333"),
]


def _render_grade_analysis(body, storage_mgr):
    section_label(body, "ANALISI PENDENZA  (passo mediano per gradiente)")

    ctrl_f = tk.Frame(body, bg=C["bg"])
    ctrl_f.pack(fill="x", padx=20, pady=(0, 4))
    for label, _, _, col in _GRADE_BINS:
        tk.Label(ctrl_f, text=f"■ {label}", font=("Courier", 7),
                 fg=col, bg=C["bg"]).pack(side="left", padx=6)

    def _refresh():
        try:
            db = int(days_var.get())
        except ValueError:
            db = 0
        _redraw_grade(chart_f, storage_mgr, races_var.get(), db)

    races_var = tk.BooleanVar(value=False)
    tk.Checkbutton(ctrl_f, text="Solo gare", font=("Courier", 8),
                   variable=races_var, fg=C["text"], bg=C["bg"],
                   selectcolor=C["surface2"], activebackground=C["bg"],
                   command=_refresh).pack(side="right", padx=8)
    info_btn(ctrl_f, "Analisi Pendenza — Come leggere il grafico",
             _INFO_GRADE).pack(side="right", padx=4)

    days_var = tk.StringVar(value="365")
    tk.Entry(ctrl_f, textvariable=days_var, width=5,
             font=("Courier", 8), bg=C["surface2"], fg=C["text"],
             insertbackground=C["text"], relief="flat",
             highlightthickness=1, highlightbackground=C["border"]
             ).pack(side="right", padx=(0, 2))
    tk.Label(ctrl_f, text="Ultimi giorni:", font=("Courier", 8),
             fg=C["text_dim"], bg=C["bg"]).pack(side="right", padx=(8, 0))
    tk.Button(ctrl_f, text="↻", font=("Courier", 9, "bold"),
              bg=C["surface2"], fg=C["accent"], bd=0, padx=6, pady=2,
              cursor="hand2", command=_refresh).pack(side="right", padx=4)

    chart_f = tk.Frame(body, bg=C["bg"])
    chart_f.pack(fill="x", padx=20, pady=(0, 20))
    _redraw_grade(chart_f, storage_mgr, False, 365)


def _redraw_grade(chart_f, storage_mgr, races_only: bool, days_back: int = 0):
    for w in chart_f.winfo_children():
        w.destroy()

    from datetime import date, timedelta
    splits = storage_mgr.get_grade_splits(races_only=races_only)
    if days_back > 0:
        cutoff = (date.today() - timedelta(days=days_back)).isoformat()
        splits = [s for s in splits if (s.get("date") or "") >= cutoff]
    if not splits:
        tk.Label(chart_f, text="Nessun dato splits disponibile.",
                 font=("Courier", 9), fg=C["text_dim"], bg=C["bg"]).pack(pady=20)
        return

    bin_paces: dict[str, list] = {b[0]: [] for b in _GRADE_BINS}
    for sp in splits:
        g = sp.get("grade_pct", 0)
        pace_ms = sp.get("pace_ms", 0)
        if pace_ms <= 0:
            continue
        pace_mkm = (1000.0 / pace_ms) / 60.0   # min/km
        for label, lo, hi, _ in _GRADE_BINS:
            if lo <= g < hi:
                bin_paces[label].append(pace_mkm)
                break

    valid = [(b[0], b[3], bin_paces[b[0]])
             for b in _GRADE_BINS if bin_paces[b[0]]]
    if not valid:
        tk.Label(chart_f, text="Dati insufficienti.",
                 font=("Courier", 9), fg=C["text_dim"], bg=C["bg"]).pack(pady=20)
        return

    labels_v  = [v[0] for v in valid]
    colors_v  = [v[1] for v in valid]
    medians_v = [sorted(v[2])[len(v[2]) // 2] for v in valid]
    counts_v  = [len(v[2]) for v in valid]

    fig = plt.Figure(figsize=(12, 3.5), facecolor=C["bg"])
    ax  = fig.add_subplot(111)
    ax.set_facecolor(C["surface"])

    bars = ax.bar(range(len(labels_v)), medians_v,
                  color=colors_v, alpha=0.85, width=0.6)
    ax.set_xticks(range(len(labels_v)))
    ax.set_xticklabels(labels_v, fontsize=8, fontfamily="monospace")
    ax.tick_params(colors=C["text_dim"], labelsize=7)
    ax.set_ylabel("Passo (min/km)", fontsize=7, color=C["text_dim"])
    ax.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda v, _: f"{int(v)}:{int((v - int(v)) * 60):02d}"))
    period_lbl = f"ultimi {days_back}gg" if days_back > 0 else "tutto lo storico"
    ax.set_title(f"PASSO MEDIANO PER PENDENZA  [{period_lbl}]",
                 color=C["text"], fontsize=9, fontweight="bold",
                 fontfamily="monospace", pad=6)
    for sp in ax.spines.values():
        sp.set_edgecolor(C["border"])
    ax.grid(axis="y", color=C["border"], linestyle="--", linewidth=0.4, alpha=0.6)
    ax.set_ylim(0, max(medians_v) * 1.28)

    for bar, v, c in zip(bars, medians_v, counts_v):
        mn = int(v)
        sc = int((v - mn) * 60)
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.03,
                f"{mn}:{sc:02d}\n(n={c})", ha="center", fontsize=6,
                color=C["text"], fontfamily="monospace")

    fig.subplots_adjust(left=0.07, right=0.98, top=0.88, bottom=0.15)
    cnv = FigureCanvasTkAgg(fig, master=chart_f)
    cnv.draw()
    cnv.get_tk_widget().pack(fill="x")


_INFO_GRADE = """
## ANALISI PENDENZA — PACE vs GRADIENTE

Questo grafico mostra il tuo passo mediano (min/km) suddiviso per fasce di pendenza, calcolato automaticamente dai tuoi split di 1 km. È uno strumento potente per capire come reagisce il tuo corpo alle variazioni di quota, e viene anche usato internamente dal grafico "Previsione Prestazioni" per stimare la tua correzione personale di dislivello.

---

# FILTRI DISPONIBILI

# Ultimi giorni
Limita l'analisi ai split delle attività degli ultimi N giorni. Usa un valore basso (90–180) per vedere la tua risposta attuale alla pendenza, utile se hai cambiato tipo di allenamento o terreno di recente. Usa 0 per includere tutto lo storico e avere più dati nelle fasce estreme (salita ripida, discesa ripida), che tendono ad avere meno split.

# Solo gare
Mostra solo i split provenienti da attività classificate come gara. Utile per vedere come gestisci le pendenze sotto pressione agonistica, spesso diverso dall'allenamento.

---

# COME SI CALCOLA

Per ogni split di 1 km, Strava registra la differenza di quota (elevation_difference) e la velocità media. La pendenza percentuale è: (Δquota / distanza) × 100. I valori sono raggruppati in 6 fasce e per ogni fascia viene mostrato il passo mediano (non la media, che è più sensibile agli outlier). Il conteggio (n=) indica quanti split cadono in quella fascia.

---

# COME LEGGERE LE BARRE

# Discesa ripida (< −8%) — blu scuro
Terreno tecnico o molto inclinato in discesa. Il passo accelera, ma le gambe assorbono impatti forti. Attenzione: spingere troppo qui aumenta il rischio di infortuni al quadricipite e alle ginocchia.

# Discesa media (−8 a −3%) — blu chiaro
Zona "confortevole" di discesa. Qui la maggior parte dei runner recupera energia. Se il tuo passo in questa fascia è sorprendentemente lento, potresti avere problemi di tecnica in discesa o scarsa forza eccentrica.

# Leggera discesa / piano (−3 a 0%) — verde
Il tuo terreno ideale. Il passo qui rappresenta il tuo "passo da gara su asfalto". Confronta questa barra con il tuo passo obiettivo nelle gare pianeggianti.

# Piano / leggera salita (0 a 3%) — giallo
La fascia più comune nelle corse su strada. Un degrado di passo eccessivo rispetto alla fascia precedente indica carenza di forza muscolare o capacità aerobica.

# Salita media (3 a 8%) — arancione
Richiede sforzo aerobico significativo. I runner da montagna tendono ad avere questa barra più "bassa" (passo migliore) rispetto ai runner da pianura. Un allenamento mirato di hill repeats migliora questa fascia.

# Salita ripida (> 8%) — rosso
Terreno di trail o cronoscalate. A queste pendenze molti runner camminano: è fisiologicamente più efficiente! Se corri sempre su questo terreno, considera workout di powerhiking e forza.

---

# COME USARLO IN PRATICA

• Confronta la barra "piano" con la barra "salita 3–8%": il differenziale di passo ti dice quanto perdi per ogni % di pendenza. Questo valore viene usato automaticamente dalla Previsione Prestazioni quando inserisci un dislivello.

• Se la barra "discesa media" è più lenta della barra "piano": stai frenando in discesa — lavora su tecnica e fiducia, c'è tempo da recuperare senza sforzo aggiuntivo.

• Usa questo grafico prima di una gara con dislivello: se il tuo passo in salita è molto lento, considera allenamenti specifici di hill run nelle 8–12 settimane precedenti.

NOTA DEL COACH: i dati di questo grafico alimentano direttamente la correzione dislivello della Previsione Prestazioni. Più split hai (specialmente su pendenze variabili), più accurata sarà la stima personalizzata.
"""


# ── Sezione curva di performance ───────────────────────────────────────────────

def _render_performance_curve(body, storage_mgr):
    section_label(body, "CURVA DI PERFORMANCE  (legge potenza su distanze standard)")

    ctrl_f = tk.Frame(body, bg=C["bg"])
    ctrl_f.pack(fill="x", padx=20, pady=(0, 4))
    tk.Label(ctrl_f, text="● best effort effettivo  — curva fit potenza",
             font=("Courier", 8), fg=C["text_dim"], bg=C["bg"]).pack(side="left")

    def _refresh():
        try:
            db = int(days_var.get())
        except ValueError:
            db = 0
        _redraw_perf_curve(chart_f, storage_mgr, races_var.get(), db)

    races_var = tk.BooleanVar(value=False)
    tk.Checkbutton(ctrl_f, text="Solo gare", font=("Courier", 8),
                   variable=races_var, fg=C["text"], bg=C["bg"],
                   selectcolor=C["surface2"], activebackground=C["bg"],
                   command=_refresh).pack(side="right", padx=8)
    info_btn(ctrl_f, "Curva di Performance — Come leggere il grafico",
             _INFO_PERF_CURVE).pack(side="right", padx=4)

    days_var = tk.StringVar(value="365")
    tk.Entry(ctrl_f, textvariable=days_var, width=5,
             font=("Courier", 8), bg=C["surface2"], fg=C["text"],
             insertbackground=C["text"], relief="flat",
             highlightthickness=1, highlightbackground=C["border"]
             ).pack(side="right", padx=(0, 2))
    tk.Label(ctrl_f, text="Ultimi giorni:", font=("Courier", 8),
             fg=C["text_dim"], bg=C["bg"]).pack(side="right", padx=(8, 0))
    tk.Button(ctrl_f, text="↻", font=("Courier", 9, "bold"),
              bg=C["surface2"], fg=C["accent"], bd=0, padx=6, pady=2,
              cursor="hand2", command=_refresh).pack(side="right", padx=4)

    chart_f = tk.Frame(body, bg=C["bg"])
    chart_f.pack(fill="x", padx=20, pady=(0, 20))
    _redraw_perf_curve(chart_f, storage_mgr, False, 365)


def _redraw_perf_curve(chart_f, storage_mgr, races_only: bool, days_back: int = 0):
    for w in chart_f.winfo_children():
        w.destroy()

    try:
        import numpy as np
    except ImportError:
        tk.Label(chart_f, text="numpy non installato (pip install numpy).",
                 font=("Courier", 9), fg=C["text_dim"], bg=C["bg"]).pack(pady=10)
        return

    from storage import _EFFORT_DISTANCES
    from datetime import date, timedelta
    efforts = storage_mgr.get_all_best_efforts(races_only=races_only)
    if days_back > 0:
        cutoff = (date.today() - timedelta(days=days_back)).isoformat()
        efforts = [e for e in efforts if (e.get("date") or "") >= cutoff]
    if not efforts:
        tk.Label(chart_f, text="Nessun best effort trovato nel database.",
                 font=("Courier", 9), fg=C["text_dim"], bg=C["bg"]).pack(pady=10)
        return

    # Migliore tempo per ogni canonical distance
    best: dict[str, float] = {}
    for e in efforts:
        c = e["canonical"]
        t = e["elapsed_time"]
        if c not in best or t < best[c]:
            best[c] = t

    pts = [(dist_m, best[key])
           for key, dist_m in _EFFORT_DISTANCES.items()
           if key in best]
    if len(pts) < 2:
        tk.Label(chart_f, text="Servono almeno 2 distanze per il fit. "
                               "Scarica attività con best_efforts.",
                 font=("Courier", 9), fg=C["text_dim"], bg=C["bg"],
                 wraplength=700).pack(pady=10)
        return

    pts.sort(key=lambda x: x[0])
    xs = np.array([p[0] for p in pts])
    ys = np.array([p[1] for p in pts])

    # Fit log-log: log(t) = a + b*log(d)
    log_x = np.log(xs)
    log_y = np.log(ys)
    b, a  = np.polyfit(log_x, log_y, 1)   # slope, intercept
    A     = np.exp(a)

    # Curva continua
    x_fit  = np.logspace(np.log10(xs.min() * 0.9), np.log10(xs.max() * 1.1), 200)
    y_fit  = A * x_fit ** b

    fig = plt.Figure(figsize=(12, 4), facecolor=C["bg"])
    ax  = fig.add_subplot(111)
    ax.set_facecolor(C["surface"])

    ax.loglog(x_fit, y_fit, color=C["accent"], linewidth=1.5,
              linestyle="--", label=f"fit: t = {A:.1f}·d^{b:.2f}")
    ax.scatter(xs, ys, color=C["blue"], s=60, zorder=5, label="Best effort effettivo")

    # Etichette punti
    dist_labels = {v: k for k, v in _EFFORT_DISTANCES.items()}
    nice = {"400m": "400m", "half_mile": "½ mile", "1k": "1K",
            "1_mile": "1 mi", "2_mile": "2 mi", "5k": "5K",
            "10k": "10K", "Half-Marathon": "½ Mar", "Marathon": "Mar"}
    for x, y in zip(xs, ys):
        key   = dist_labels.get(x, "")
        lbl   = nice.get(key, key)
        t_sec = int(y)
        h, rem = divmod(t_sec, 3600)
        m, s   = divmod(rem, 60)
        t_str  = f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"
        ax.annotate(f"{lbl}\n{t_str}", (x, y),
                    textcoords="offset points", xytext=(6, 4),
                    fontsize=6.5, color=C["text"], fontfamily="monospace")

    ax.set_xlabel("Distanza (m)", fontsize=7, color=C["text_dim"])
    ax.set_ylabel("Tempo (s)", fontsize=7, color=C["text_dim"])
    period_lbl = f"ultimi {days_back}gg" if days_back > 0 else "tutto lo storico"
    ax.set_title(f"CURVA DI PERFORMANCE — DISTANZA vs TEMPO  [{period_lbl}]",
                 color=C["text"], fontsize=9, fontweight="bold",
                 fontfamily="monospace", pad=6)
    ax.tick_params(colors=C["text_dim"], labelsize=7)
    for sp in ax.spines.values():
        sp.set_edgecolor(C["border"])
    ax.grid(which="both", color=C["border"], linestyle="--",
            linewidth=0.4, alpha=0.5)
    ax.legend(fontsize=7, facecolor=C["surface2"], edgecolor=C["border"],
              labelcolor=C["text"])

    # Mostra esponente b sotto il titolo
    txt = (f"Esponente b = {b:.3f}  "
           f"({'resistenza ↑' if b > 1.06 else 'velocità ↑' if b < 1.03 else 'bilanciato'})")
    ax.text(0.5, 0.97, txt, ha="center", va="top",
            transform=ax.transAxes, fontsize=7.5,
            color=C["text_dim"], fontfamily="monospace")

    fig.subplots_adjust(left=0.07, right=0.97, top=0.88, bottom=0.14)
    cnv = FigureCanvasTkAgg(fig, master=chart_f)
    cnv.draw()
    cnv.get_tk_widget().pack(fill="x")


_INFO_PERF_CURVE = """
## CURVA DI PERFORMANCE — LEGGE POTENZA

Questo grafico mostra i tuoi migliori tempi su distanze standard (da 400m alla maratona) in un piano log-log, dove viene fittata una curva della forma t = A × d^b (legge di potenza). È ispirato al modello di Peter Riegel (1977) e alimenta direttamente il grafico "Previsione Prestazioni".

---

# FILTRI DISPONIBILI

# Ultimi giorni
Limita il fit ai best effort delle attività degli ultimi N giorni. Usa un valore basso (90–180) per rispecchiare la forma attuale; usa 0 per includere tutto lo storico e avere più punti nel fit. Se il filtro lascia meno di 2 distanze disponibili, il grafico non viene mostrato: allarga la finestra temporale.

# Solo gare
Considera solo i best effort registrati durante attività classificate come gara. Produce un fit più rappresentativo dello sforzo massimale, ma richiede che le gare siano state correttamente etichettate come tali su Strava.

NOTA: i best effort vengono misurati in base al tempo di movimento (moving_time), escludendo le pause — questo li rende più comparabili tra attività diverse.

---

# IL MODELLO MATEMATICO

Riegel scoprì che il tempo di performance su diverse distanze segue la legge: T = A × D^b

• T = tempo in secondi
• D = distanza in metri
• A = costante individuale (dipende dalla tua velocità di base)
• b = esponente di fatica (tipicamente tra 1.03 e 1.15)

In scala logaritmica diventa una retta: log(T) = log(A) + b × log(D). Il fit viene calcolato su tutti i punti disponibili con regressione ai minimi quadrati in spazio log-log.

---

# L'ESPONENTE b — IL TUO PROFILO ATLETICO

L'esponente b è la chiave interpretativa. Riegel trovò b ≈ 1.06 per i runner élite.

# b < 1.03 — Profilo velocista
Più forte sulle distanze brevi. Buona capacità anaerobica e lattacida. Eccelle nei 5K.

# b ≈ 1.03–1.06 — Profilo bilanciato
Profilo completo, simile ai corridori élite. Competitivo su un ampio spettro di distanze.

# b > 1.06 — Profilo resistente (fondista)
Più forte sulle lunghe distanze. Ottima efficienza aerobica. Eccelle sulla maratona.

---

# COME USARLO IN PRATICA

# Scelta della gara obiettivo
Se i tuoi punti reali stanno sopra la curva su una distanza, quella non è il tuo punto di forza. Se stanno sotto, sei relativamente più forte lì.

# Predire tempi su distanze non ancora corse
La curva fittata stima il tempo atteso su qualsiasi distanza. Usa il grafico "Previsione Prestazioni" per il calcolo interattivo con incertezza.

# Monitorare i progressi
Ricontrolla ogni 2–3 mesi. Se A diminuisce (curva si abbassa) stai migliorando. Se b si avvicina a 1.06 stai diventando più completo.

---

# LIMITAZIONI

• Funziona meglio con best effort su almeno 3–4 distanze diverse.
• Il modello assume condizioni simili tra le distanze (pianura, buona condizione fisica). Gare con molto dislivello o sforzi subottimali distorcono il fit.
• Non considera lo stato di forma attuale: usa il grafico CTL/ATL per quello.

NOTA DEL COACH: confronta il fit con quello di 6 mesi fa. Se b è sceso avvicinandosi a 1.06 hai migliorato la versatilità. Se A è sceso mantenendo b costante, sei più veloce su tutte le distanze — il miglior scenario possibile.
"""


# ── Sezione previsione prestazioni ────────────────────────────────────────────

_PREDICT_DISTS = {
    "1 km":           1000.0,
    "5 km":           5000.0,
    "10 km":         10000.0,
    "Mezza Maratona": 21097.5,
    "Maratona":       42195.0,
    "Personalizzata": -1.0,
}


def _render_race_prediction(body, storage_mgr):
    section_label(body, "PREVISIONE PRESTAZIONI  (simulazione Monte Carlo)")

    ctrl_f = tk.Frame(body, bg=C["bg"])
    ctrl_f.pack(fill="x", padx=20, pady=(0, 6))
    info_btn(ctrl_f, "Previsione Prestazioni — Come funziona",
             _INFO_RACE_PRED).pack(side="right", padx=4)

    # Pannello parametri (2 righe)
    param_f = tk.Frame(body, bg=C["surface2"],
                       highlightthickness=1, highlightbackground=C["border"])
    param_f.pack(fill="x", padx=20, pady=(0, 6))
    pf = tk.Frame(param_f, bg=C["surface2"])
    pf.pack(fill="x", padx=16, pady=10)

    # ── Riga 1: Distanza + km personalizzati (condizionale) + Dislivello ──────
    r1 = tk.Frame(pf, bg=C["surface2"])
    r1.pack(fill="x", pady=(0, 6))

    tk.Label(r1, text="Distanza:", font=("Courier", 9),
             fg=C["text_dim"], bg=C["surface2"]).pack(side="left")
    dist_var = tk.StringVar(value="10 km")
    dist_combo = tk.OptionMenu(r1, dist_var, *_PREDICT_DISTS.keys())
    dist_combo.config(font=("Courier", 9), bg=C["surface"], fg=C["text"],
                      bd=0, highlightthickness=0, activebackground=C["surface2"])
    dist_combo["menu"].config(font=("Courier", 9), bg=C["surface"], fg=C["text"])
    dist_combo.pack(side="left", padx=(4, 16))

    # Distanza personalizzata — visibile solo con "Personalizzata"
    custom_lbl = tk.Label(r1, text="km personalizzati:", font=("Courier", 9),
                          fg=C["text_dim"], bg=C["surface2"])
    custom_var = tk.StringVar(value="15")
    custom_entry = tk.Entry(r1, textvariable=custom_var, font=("Courier", 9),
                            bg=C["surface"], fg=C["text"], width=5, bd=0,
                            insertbackground=C["text"],
                            highlightthickness=1, highlightbackground=C["border"])

    def _on_dist_change(*_):
        if dist_var.get() == "Personalizzata":
            custom_lbl.pack(side="left")
            custom_entry.pack(side="left", padx=(4, 16))
        else:
            custom_lbl.pack_forget()
            custom_entry.pack_forget()

    dist_var.trace_add("write", _on_dist_change)
    _on_dist_change()  # stato iniziale

    tk.Label(r1, text="Dislivello +  (m):", font=("Courier", 9),
             fg=C["text_dim"], bg=C["surface2"]).pack(side="left")
    elev_var = tk.StringVar(value="0")
    tk.Entry(r1, textvariable=elev_var, font=("Courier", 9),
             bg=C["surface"], fg=C["text"], width=6, bd=0,
             insertbackground=C["text"],
             highlightthickness=1, highlightbackground=C["border"]
             ).pack(side="left", padx=(4, 16))

    # ── Riga 2: Filtri temporali / lunghezza + Solo gare + CALCOLA ───────────
    r2 = tk.Frame(pf, bg=C["surface2"])
    r2.pack(fill="x")

    tk.Label(r2, text="Ultimi giorni:", font=("Courier", 9),
             fg=C["text_dim"], bg=C["surface2"]).pack(side="left")
    days_var = tk.StringVar(value="365")
    tk.Entry(r2, textvariable=days_var, font=("Courier", 9),
             bg=C["surface"], fg=C["text"], width=5, bd=0,
             insertbackground=C["text"],
             highlightthickness=1, highlightbackground=C["border"]
             ).pack(side="left", padx=(4, 4))
    tk.Label(r2, text="(0 = tutto)", font=("Courier", 7),
             fg=C["text_dim"], bg=C["surface2"]).pack(side="left", padx=(0, 12))

    tk.Label(r2, text="km corsa min:", font=("Courier", 9),
             fg=C["text_dim"], bg=C["surface2"]).pack(side="left")
    km_min_var = tk.StringVar(value="0")
    tk.Entry(r2, textvariable=km_min_var, font=("Courier", 9),
             bg=C["surface"], fg=C["text"], width=5, bd=0,
             insertbackground=C["text"],
             highlightthickness=1, highlightbackground=C["border"]
             ).pack(side="left", padx=(4, 8))
    tk.Label(r2, text="max:", font=("Courier", 9),
             fg=C["text_dim"], bg=C["surface2"]).pack(side="left")
    km_max_var = tk.StringVar(value="0")
    tk.Entry(r2, textvariable=km_max_var, font=("Courier", 9),
             bg=C["surface"], fg=C["text"], width=5, bd=0,
             insertbackground=C["text"],
             highlightthickness=1, highlightbackground=C["border"]
             ).pack(side="left", padx=(4, 2))
    tk.Label(r2, text="(0 = nessun limite)", font=("Courier", 7),
             fg=C["text_dim"], bg=C["surface2"]).pack(side="left", padx=(0, 12))

    races_var = tk.BooleanVar(value=False)
    tk.Checkbutton(r2, text="Solo gare", font=("Courier", 8),
                   variable=races_var, fg=C["text"], bg=C["surface2"],
                   selectcolor=C["surface"], activebackground=C["surface2"]
                   ).pack(side="left", padx=8)

    # Bottone calcola
    chart_f = tk.Frame(body, bg=C["bg"])
    chart_f.pack(fill="x", padx=20, pady=(0, 20))

    def _calc():
        d_key = dist_var.get()
        dist_m = _PREDICT_DISTS[d_key]
        if dist_m < 0:   # personalizzata
            try:
                dist_m = float(custom_var.get().replace(",", ".")) * 1000.0
            except Exception:
                dist_m = 10000.0
        try:
            elev_gain = float(elev_var.get())
        except Exception:
            elev_gain = 0.0
        try:
            days_back = int(days_var.get())
        except Exception:
            days_back = 365
        try:
            km_min = float(km_min_var.get())
        except Exception:
            km_min = 0.0
        try:
            km_max = float(km_max_var.get())
        except Exception:
            km_max = 0.0
        _redraw_race_pred(chart_f, storage_mgr,
                          dist_m, elev_gain, races_var.get(), days_back,
                          km_min, km_max)

    tk.Button(r2, text="▶  CALCOLA", font=("Courier", 9, "bold"),
              bg=C["accent"], fg="white", bd=0, padx=12, pady=4,
              cursor="hand2", command=_calc).pack(side="left", padx=4)


def _personal_grade_correction(storage_mgr, races_only: bool,
                               avg_grade: float) -> tuple[float, str]:
    """
    Stima la correzione personale del runner in sec/km per 1% di pendenza media,
    usando regressione lineare sui grade splits reali.
    Ritorna (sec_per_km_correction_totale, label_fonte).
    """
    if avg_grade <= 0:
        return 0.0, ""

    try:
        import numpy as np
        splits = storage_mgr.get_grade_splits(races_only=races_only)
        # Filtra split con pendenza e velocità plausibili (esclude outlier e camminata)
        pts = [
            (s["grade_pct"], 1000.0 / s["pace_ms"])   # (grade%, sec/km)
            for s in splits
            if -20.0 <= s.get("grade_pct", 0) <= 20.0
            and 1.5 < s.get("pace_ms", 0) < 7.0       # 2:23–11:07 min/km
        ]
        if len(pts) >= 30:
            grades = np.array([p[0] for p in pts])
            paces  = np.array([p[1] for p in pts])
            slope, _ = np.polyfit(grades, paces, 1)
            # slope = sec/km per 1% di grade; cap in range ragionevole
            slope = float(np.clip(slope, 2.0, 15.0))
            return slope * avg_grade, f"regressione personale {slope:.1f}s/km per 1%"
    except Exception:
        pass

    # Fallback al modello empirico di Minetti
    return avg_grade * 6.0, "modello empirico 6s/km per 1%"


def _redraw_race_pred(chart_f, storage_mgr,
                      dist_m: float, elev_gain: float,
                      races_only: bool, days_back: int = 365,
                      km_min: float = 0.0, km_max: float = 0.0):
    for w in chart_f.winfo_children():
        w.destroy()

    try:
        import numpy as np
    except ImportError:
        tk.Label(chart_f, text="numpy non installato.",
                 font=("Courier", 9), fg=C["text_dim"], bg=C["bg"]).pack(pady=10)
        return

    from storage import _EFFORT_DISTANCES
    from datetime import date, timedelta
    efforts = storage_mgr.get_all_best_efforts(races_only=races_only)

    # Filtra per finestra temporale
    if days_back > 0:
        cutoff = (date.today() - timedelta(days=days_back)).isoformat()
        efforts = [e for e in efforts if (e.get("date") or "") >= cutoff]

    # Filtra per lunghezza dell'attività
    if km_min > 0:
        efforts = [e for e in efforts if e.get("activity_dist_km", 0) >= km_min]
    if km_max > 0:
        efforts = [e for e in efforts if e.get("activity_dist_km", 0) <= km_max]

    if not efforts:
        tk.Label(chart_f, text="Nessun best effort trovato.",
                 font=("Courier", 9), fg=C["text_dim"], bg=C["bg"]).pack(pady=10)
        return

    best: dict[str, float] = {}
    for e in efforts:
        c = e["canonical"]
        t = e["elapsed_time"]
        if c not in best or t < best[c]:
            best[c] = t

    pts = [(dm, best[key]) for key, dm in _EFFORT_DISTANCES.items() if key in best]
    if len(pts) < 2:
        tk.Label(chart_f, text="Servono almeno 2 distanze per la previsione.",
                 font=("Courier", 9), fg=C["text_dim"], bg=C["bg"],
                 wraplength=700).pack(pady=10)
        return

    pts.sort(key=lambda x: x[0])
    xs = np.array([p[0] for p in pts])
    ys = np.array([p[1] for p in pts])
    log_x = np.log(xs)
    log_y = np.log(ys)
    b, a  = np.polyfit(log_x, log_y, 1)
    A     = np.exp(a)

    # Residui → deviazione standard per il Monte Carlo
    y_pred_log = a + b * log_x
    residuals  = log_y - y_pred_log
    sigma_log  = float(np.std(residuals)) if len(residuals) > 2 else 0.04

    # Tempo base alla distanza target
    t_base = A * (dist_m ** b)
    dist_km = dist_m / 1000.0

    # Correzione gradiente personalizzata: regressione lineare sui grade splits del runner
    # avg_grade in % = (dislivello_m / distanza_m) × 100
    avg_grade = (elev_gain / dist_m * 100.0) if dist_m > 0 else 0.0
    sec_per_km_correction, grade_correction_source = _personal_grade_correction(
        storage_mgr, races_only, avg_grade
    )
    t_adjusted = t_base + sec_per_km_correction * dist_km

    # Monte Carlo: 5000 campioni
    np.random.seed(42)
    noise     = np.random.normal(0, sigma_log, 5000)
    samples   = t_adjusted * np.exp(noise)
    p10, p25, p50, p75, p90 = np.percentile(samples, [10, 25, 50, 75, 90])

    def _fmt(s):
        s = int(s)
        h, r = divmod(s, 3600)
        m, sec = divmod(r, 60)
        return f"{h}:{m:02d}:{sec:02d}" if h else f"{m}:{sec:02d}"

    fig = plt.Figure(figsize=(12, 3.8), facecolor=C["bg"])
    ax  = fig.add_subplot(111)
    ax.set_facecolor(C["surface"])

    ax.hist(samples / 60.0, bins=60, color=C["accent"], alpha=0.7, edgecolor="none")
    for val, col, lbl in [
        (p10 / 60, C["green"],  f"P10 {_fmt(p10)}  ← top"),
        (p25 / 60, C["blue"],   f"P25 {_fmt(p25)}"),
        (p50 / 60, C["yellow"], f"P50 {_fmt(p50)}"),
        (p75 / 60, C["orange"], f"P75 {_fmt(p75)}"),
        (p90 / 60, C["red"],    f"P90 {_fmt(p90)}  ← conservativo"),
    ]:
        ax.axvline(val, color=col, linewidth=1.4, linestyle="--", label=lbl)

    ax.set_xlabel("Tempo previsto (min)", fontsize=7, color=C["text_dim"])
    ax.set_ylabel("Frequenza (simulazioni)", fontsize=7, color=C["text_dim"])
    period_lbl = f"ultimi {days_back}gg" if days_back > 0 else "tutto lo storico"
    km_lbl = ""
    if km_min > 0 or km_max > 0:
        lo = f"{km_min:.0f}" if km_min > 0 else "0"
        hi = f"{km_max:.0f}" if km_max > 0 else "∞"
        km_lbl = f"  corse {lo}–{hi}km"
    dist_lbl = (f"{dist_km:.1f} km"
                + (f"  +{elev_gain:.0f}m ↑" if elev_gain > 0 else "")
                + f"  [{period_lbl}]{km_lbl}")
    ax.set_title(f"DISTRIBUZIONE TEMPI PREVISTI — {dist_lbl}",
                 color=C["text"], fontsize=9, fontweight="bold",
                 fontfamily="monospace", pad=6)
    ax.tick_params(colors=C["text_dim"], labelsize=7)
    for sp in ax.spines.values():
        sp.set_edgecolor(C["border"])
    ax.grid(axis="y", color=C["border"], linestyle="--", linewidth=0.4, alpha=0.5)
    ax.legend(fontsize=7, facecolor=C["surface2"], edgecolor=C["border"],
              labelcolor=C["text"], loc="upper right")

    fig.subplots_adjust(left=0.06, right=0.98, top=0.88, bottom=0.16)
    cnv = FigureCanvasTkAgg(fig, master=chart_f)
    cnv.draw()
    cnv.get_tk_widget().pack(fill="x")

    # Riepilogo testuale
    summary_f = tk.Frame(chart_f, bg=C["surface2"],
                         highlightthickness=1, highlightbackground=C["border"])
    summary_f.pack(fill="x", pady=(6, 0))
    sf = tk.Frame(summary_f, bg=C["surface2"])
    sf.pack(padx=16, pady=8)
    for lbl, val, col in [
        ("Top / ottimistica  (P10):", _fmt(p10), C["green"]),
        ("Buona giornata     (P25):", _fmt(p25), C["blue"]),
        ("Stima mediana      (P50):", _fmt(p50), C["yellow"]),
        ("Giornata normale   (P75):", _fmt(p75), C["orange"]),
        ("Conservativa       (P90):", _fmt(p90), C["red"]),
    ]:
        r = tk.Frame(sf, bg=C["surface2"])
        r.pack(anchor="w")
        tk.Label(r, text=lbl, font=("Courier", 8), fg=C["text_dim"],
                 bg=C["surface2"], width=28, anchor="w").pack(side="left")
        tk.Label(r, text=val, font=("Courier", 9, "bold"), fg=col,
                 bg=C["surface2"]).pack(side="left")
    if elev_gain > 0:
        corr_str = f"+{sec_per_km_correction * dist_km:.0f}s totali  [{grade_correction_source}]"
        tk.Label(sf, text=f"  (correzione dislivello: {corr_str})",
                 font=("Courier", 7), fg=C["text_dim"],
                 bg=C["surface2"]).pack(anchor="w")

    # Pannello diagnostico: dati usati nel fit
    tk.Frame(sf, bg=C["border"], height=1).pack(fill="x", pady=(8, 4))
    tk.Label(sf, text=f"  Fit: t = {A:.2f} · d^{b:.3f}   (Riegel teorico: b=1.060)   "
                      f"base {_fmt(t_base)} su {dist_km:.1f} km",
             font=("Courier", 7), fg=C["text_dim"], bg=C["surface2"]).pack(anchor="w")
    tk.Label(sf, text="  Dati usati nel fit:",
             font=("Courier", 7, "bold"), fg=C["text_dim"], bg=C["surface2"]).pack(anchor="w")
    nice = {"400m": "400m", "half_mile": "½ mi", "1k": "1K", "1_mile": "1 mi",
            "2_mile": "2 mi", "5k": "5K", "10k": "10K",
            "Half-Marathon": "½ Mar", "Marathon": "Mar"}
    for key, dm in sorted(_EFFORT_DISTANCES.items(), key=lambda x: x[1]):
        if key not in best:
            continue
        t_eff = best[key]
        pace_sec = t_eff / (dm / 1000.0)
        pace_str = f"{int(pace_sec // 60)}:{int(pace_sec % 60):02d}/km"
        tk.Label(sf,
                 text=f"    {nice.get(key, key):>6}  →  {_fmt(t_eff):>8}  ({pace_str})",
                 font=("Courier", 7), fg=C["accent"], bg=C["surface2"]).pack(anchor="w")


_INFO_RACE_PRED = """
## PREVISIONE PRESTAZIONI — SIMULAZIONE MONTE CARLO

Questo strumento stima il tuo tempo possibile su una distanza target, a partire dai tuoi best effort storici. Combina tre fasi: fit della curva di performance (Riegel), correzione personalizzata del dislivello, e simulazione Monte Carlo per quantificare l'incertezza.

---

# PARAMETRI DI INPUT

# Distanza
La distanza della gara da prevedere. Scegli tra le distanze standard (1 km, 5 km, 10 km, Mezza Maratona, Maratona) o seleziona "Personalizzata" per inserire qualsiasi valore.

# km personalizzati
Attivo solo con "Personalizzata". Inserisci la distanza in km (es. 8.5). Supporta decimali.

# Dislivello + (m)
Dislivello positivo totale del percorso obiettivo in metri. Lascia 0 per percorsi pianeggianti. La pendenza media viene calcolata come (dislivello_m / distanza_m) × 100 e usata per stimare il rallentamento. Trova questo valore nella scheda tecnica della gara.
• Esempi: 10K cittadino piatto → 0m. Mezza montagna → 400–800m. Trail KV → 1000m+

# Ultimi giorni
Finestra temporale dei best effort da considerare nel fit. 0 = tutto lo storico.
• 90 gg: forma attuale. Ideale se ti sei allenato in modo costante.
• 180–365 gg: stima stabile. Consigliato se hai pochi dati recenti.
• 0: massima copertura. Utile se hai poche gare o best effort registrati.
NOTA: se il filtro lascia meno di 2 distanze con dati, la previsione non può essere calcolata.

# km corsa min / max
Filtra i best effort in base alla lunghezza dell'attività che li contiene. Utile per considerare solo le corse simili per lunghezza alla gara obiettivo: se vuoi prevedere un 10K, impostare min=8 max=15 esclude best effort registrati durante maratone (paceati lentamente) o uscite brevissime.
• 0 = nessun limite (si considerano tutte le attività).

# Solo gare
Usa solo best effort da attività classificate come gara su Strava. Le gare rappresentano lo sforzo massimale e producono previsioni più accurate. Richiede che le attività siano state etichettate correttamente su Strava come "Gara".

---

# FASE 1 — FIT DELLA CURVA DI PERFORMANCE

Viene fittata la legge t = A × d^b sui tuoi migliori tempi di movimento (moving_time) per distanza, dopo aver applicato tutti i filtri impostati. Il pannello diagnostico in fondo al grafico mostra esattamente quali distanze e tempi vengono usati: verificare che siano coerenti con le tue prestazioni reali è il primo passo per valutare l'affidabilità della previsione.

---

# FASE 2 — CORREZIONE DISLIVELLO PERSONALIZZATA

Se il dislivello è > 0, il rallentamento viene stimato dai tuoi dati reali anziché da un modello fisso:
• Il grafico "Analisi Pendenza" calcola, tramite regressione lineare sui tuoi split di 1 km, quanti secondi/km perdi per ogni 1% di pendenza media.
• Questo coefficiente personale viene applicato alla pendenza media del percorso target.
• Se hai meno di 30 split su terreno variabile, si usa il modello empirico di Minetti come fallback (6 s/km per 1%).
• Il pannello diagnostico mostra quale fonte è stata usata e l'entità della correzione totale.

---

# FASE 3 — MONTE CARLO (5000 simulazioni)

Il tempo previsto non è un valore fisso: dipende dalla forma del giorno, dal meteo, dalla motivazione. Vengono generate 5000 simulazioni con rumore calibrato sui residui del fit (quanto i tuoi best effort si discostano dalla curva ideale). Il risultato è una distribuzione di tempi possibili.

---

# COME LEGGERE L'ISTOGRAMMA E I PERCENTILI

# P10 — Top / ottimistica
Solo il 10% delle simulazioni è più veloce. Potenziale massimo in condizioni ideali.

# P25 — Buona giornata
Il 25% delle simulazioni prevede un tempo migliore. Obiettivo ambizioso ma realistico.

# P50 — Stima mediana
Il tempo più probabile. 50% di probabilità di batterlo. Riferimento principale.

# P75 — Giornata normale
Il 75% delle simulazioni è più veloce. Raggiungibile anche senza condizioni eccezionali.

# P90 — Conservativa
Solo il 10% delle simulazioni è più lenta. Limite superiore utile per calibrare il ritmo di partenza in sicurezza.

---

# PANNELLO DIAGNOSTICO

In fondo al grafico trovi il riepilogo dei dati usati nel calcolo:
• Equazione del fit e confronto con b=1.060 (Riegel teorico)
• Tempo base grezzo prima delle correzioni
• Lista di ogni distanza usata con il tempo e il passo corrispondente
Verifica che questi tempi siano coerenti con le tue prestazioni: se un best effort è anomalo (es. una corsa lenta usata come 10K di riferimento), puoi escluderla usando i filtri "Ultimi giorni" o "km min/max".

---

# CONSIGLI PRATICI

• Parti al ritmo P50–P75 nei primi km. È meglio accelerare nel finale che esplodere.
• Se parti più veloce di P25, il rischio di crollo aumenta significativamente.
• Più best effort hai su distanze diverse, più il fit è preciso e l'incertezza si riduce.
• Per gare con molto dislivello, accumulare split su terreno simile nel grafico Analisi Pendenza migliora la correzione personalizzata.

---

NOTA DEL COACH: questo modello non conosce il tuo stato di forma attuale. Controlla il grafico CTL/TSB: se il TSB è positivo (+5 a +15) e il CTL è vicino al massimo storico, punta al P75. Se sei reduce da un blocco intenso o da riposo, punta al P25–P50.
"""
