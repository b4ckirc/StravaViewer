# ── ui/tab_library.py ─────────────────────────────────────────────────────────
import tkinter as tk
import webbrowser
from tkinter import ttk, messagebox
from datetime import datetime
from config import C, COMPARE_EMOJIS, MAX_COMPARE
from models import fmt_time, fmt_pace

PAGE_SIZE = 100


def _pace_chip_color(speed_ms: float) -> str:
    """Colore semantico per il passo: verde < 5:00, giallo < 6:30, rosso oltre."""
    if speed_ms <= 0:
        return C["text_dim"]
    pace_sec = 1000 / speed_ms          # secondi per km
    if pace_sec < 300:                  # < 5:00/km
        return C["green"]
    if pace_sec < 390:                  # < 6:30/km
        return C["yellow"]
    return C["red"]


def render(tab, storage_mgr, on_open, on_compare_add, on_compare_clear, app_ref):
    for w in tab.winfo_children():
        w.destroy()

    # ── Fonte dati ────────────────────────────────────────────────────────────
    def get_summaries(filters=None):
        if storage_mgr.mongo_ok and storage_mgr.mongo_storage:
            return storage_mgr.mongo_storage.list_all(filters)
        return storage_mgr.json_storage.list_all(filters)

    # Stato paginazione
    state = {"page": 0, "summaries": []}

    # ── Filtri ────────────────────────────────────────────────────────────────
    fbar = tk.Frame(tab, bg=C["surface"], pady=10)
    fbar.pack(fill="x")

    tk.Label(fbar, text="FILTRI:", font=("Courier", 9, "bold"),
             fg=C["text_dim"], bg=C["surface"]).pack(side="left", padx=(16, 8))

    tk.Label(fbar, text="Nome:", font=("Courier", 8),
             fg=C["text_dim"], bg=C["surface"]).pack(side="left")
    name_var = tk.StringVar()
    tk.Entry(fbar, textvariable=name_var, font=("Courier", 9),
             bg=C["surface2"], fg=C["text"], width=18, bd=0,
             insertbackground=C["text"],
             highlightthickness=1, highlightbackground=C["border"]
             ).pack(side="left", padx=(4, 14))

    tk.Label(fbar, text="Dist km:", font=("Courier", 8),
             fg=C["text_dim"], bg=C["surface"]).pack(side="left")
    dist_min_var = tk.StringVar()
    dist_max_var = tk.StringVar()
    tk.Entry(fbar, textvariable=dist_min_var, font=("Courier", 9),
             bg=C["surface2"], fg=C["text"], width=6, bd=0,
             insertbackground=C["text"],
             highlightthickness=1, highlightbackground=C["border"]
             ).pack(side="left", padx=(4, 2))
    tk.Label(fbar, text="–", fg=C["text_dim"], bg=C["surface"],
             font=("Courier", 9)).pack(side="left")
    tk.Entry(fbar, textvariable=dist_max_var, font=("Courier", 9),
             bg=C["surface2"], fg=C["text"], width=6, bd=0,
             insertbackground=C["text"],
             highlightthickness=1, highlightbackground=C["border"]
             ).pack(side="left", padx=(2, 14))

    tk.Label(fbar, text="Dal:", font=("Courier", 8),
             fg=C["text_dim"], bg=C["surface"]).pack(side="left")
    date_from_var = tk.StringVar()
    date_to_var   = tk.StringVar()
    tk.Entry(fbar, textvariable=date_from_var, font=("Courier", 9),
             bg=C["surface2"], fg=C["text"], width=11, bd=0,
             insertbackground=C["text"],
             highlightthickness=1, highlightbackground=C["border"]
             ).pack(side="left", padx=(4, 2))
    tk.Label(fbar, text="Al:", fg=C["text_dim"], bg=C["surface"],
             font=("Courier", 8)).pack(side="left", padx=(6, 0))
    tk.Entry(fbar, textvariable=date_to_var, font=("Courier", 9),
             bg=C["surface2"], fg=C["text"], width=11, bd=0,
             insertbackground=C["text"],
             highlightthickness=1, highlightbackground=C["border"]
             ).pack(side="left", padx=(4, 2))
    tk.Label(fbar, text="(YYYY-MM-DD)", font=("Courier", 7),
             fg=C["text_dim"], bg=C["surface"]).pack(side="left", padx=(4, 12))

    races_var = tk.BooleanVar(value=False)
    tk.Checkbutton(
        fbar, text="Solo gare", variable=races_var,
        font=("Courier", 8), fg=C["text"], bg=C["surface"],
        selectcolor=C["surface2"], activebackground=C["surface"],
        activeforeground=C["text"],
    ).pack(side="left", padx=(4, 8))

    count_var = tk.StringVar(value="")
    tk.Label(fbar, textvariable=count_var, font=("Courier", 8),
             fg=C["green"], bg=C["surface"]).pack(side="right", padx=12)

    src_text = "● MongoDB" if (storage_mgr.mongo_ok and storage_mgr.mongo_storage) else "○ File JSON"
    src_col  = C["green"] if (storage_mgr.mongo_ok and storage_mgr.mongo_storage) else C["yellow"]
    tk.Label(fbar, text=src_text, font=("Courier", 7, "bold"),
             fg=src_col, bg=C["surface"]).pack(side="right", padx=8)

    tk.Button(fbar, text="🔍", font=("Courier", 10), bg=C["accent"],
              fg="white", bd=0, padx=10, pady=4, cursor="hand2",
              command=lambda: _search()).pack(side="left", padx=4)

    # ── Barra confronto ───────────────────────────────────────────────────────
    cbar = tk.Frame(tab, bg=C["surface2"], pady=8)
    cbar.pack(fill="x")
    cmp_label = tk.Label(cbar, text="Confronto: nessuna selezione",
                         font=("Courier", 9), fg=C["text_dim"], bg=C["surface2"])
    cmp_label.pack(side="left", padx=16)

    def refresh_cmp_label():
        n = len(app_ref.cmp_list)
        if n == 0:
            cmp_label.config(text="Confronto: nessuna selezione", fg=C["text_dim"])
        else:
            names = "  ".join(f"{COMPARE_EMOJIS[i+1]} {app_ref.cmp_list[i].name[:20]}"
                              for i in range(n))
            cmp_label.config(text=f"Confronto [{n}/4]: {names}", fg=C["accent"])

    tk.Button(cbar, text="🗑 Svuota confronto", font=("Courier", 8, "bold"),
              bg=C["surface2"], fg=C["text_dim"], bd=0, padx=10, cursor="hand2",
              command=lambda: [on_compare_clear(), refresh_cmp_label(), _render_page()]
              ).pack(side="right", padx=8)
    tk.Button(cbar, text="▶ Avvia confronto", font=("Courier", 8, "bold"),
              bg=C["accent"], fg="white", bd=0, padx=10, cursor="hand2",
              command=lambda: app_ref._run_compare()
              ).pack(side="right", padx=4)

    # ── Intestazione tabella ──────────────────────────────────────────────────
    cols   = ["DATA",  "NOME", "DIST.", "TEMPO", "PASSO", "HR",  "↑ELEV", "AZIONI"]
    widths = [12,       32,     9,       8,       8,       6,     8,       18]

    hdr_f = tk.Frame(tab, bg=C["surface"])
    hdr_f.pack(fill="x")
    for col, w in zip(cols, widths):
        tk.Label(hdr_f, text=col, font=("Courier", 10, "bold"),
                 fg=C["text_dim"], bg=C["surface"],
                 width=w, anchor="w" if col == "NOME" else "center",
                 pady=8, padx=4).pack(side="left")

    # ── Lista scrollabile ─────────────────────────────────────────────────────
    sc = tk.Canvas(tab, bg=C["bg"], bd=0, highlightthickness=0)
    sb = ttk.Scrollbar(tab, orient="vertical", command=sc.yview)
    sc.configure(yscrollcommand=sb.set)
    sb.pack(side="right", fill="y")
    sc.pack(fill="both", expand=True)
    list_frame = tk.Frame(sc, bg=C["bg"])
    wid = sc.create_window((0, 0), window=list_frame, anchor="nw")
    list_frame.bind("<Configure>", lambda e: sc.configure(scrollregion=sc.bbox("all")))
    sc.bind("<Configure>",         lambda e: sc.itemconfig(wid, width=e.width))
    sc.bind_all("<MouseWheel>",    lambda e: sc.yview_scroll(int(-1*(e.delta/120)), "units"))

    # ── Barra di paginazione (in fondo) ───────────────────────────────────────
    pag_f = tk.Frame(tab, bg=C["surface"], pady=8)
    pag_f.pack(fill="x", side="bottom")

    page_var = tk.StringVar(value="")
    tk.Label(pag_f, textvariable=page_var, font=("Courier", 9),
             fg=C["text_dim"], bg=C["surface"]).pack(side="left", padx=16)

    btn_next = tk.Button(pag_f, text="▶  Pag. successiva", font=("Courier", 9, "bold"),
                         bg=C["surface2"], fg=C["text"], bd=0, padx=12, pady=4,
                         cursor="hand2", command=lambda: _go_page(state["page"] + 1))
    btn_next.pack(side="right", padx=8)

    btn_prev = tk.Button(pag_f, text="◀  Pag. precedente", font=("Courier", 9, "bold"),
                         bg=C["surface2"], fg=C["text"], bd=0, padx=12, pady=4,
                         cursor="hand2", command=lambda: _go_page(state["page"] - 1))
    btn_prev.pack(side="right", padx=4)

    # ── Logica ────────────────────────────────────────────────────────────────

    def _search():
        """Carica tutti i summary filtrati, poi va alla pagina 0."""
        filters = {}
        if name_var.get().strip():
            filters["name"] = name_var.get().strip()
        try:
            if dist_min_var.get(): filters["dist_min"] = float(dist_min_var.get())
            if dist_max_var.get(): filters["dist_max"] = float(dist_max_var.get())
        except ValueError:
            pass
        try:
            if date_from_var.get():
                filters["date_from"] = datetime.strptime(date_from_var.get(), "%Y-%m-%d")
            if date_to_var.get():
                filters["date_to"] = datetime.strptime(date_to_var.get(), "%Y-%m-%d")
        except ValueError:
            pass
        if races_var.get():
            filters["races_only"] = True

        state["summaries"] = get_summaries(filters)
        state["page"]      = 0
        count_var.set(f"{len(state['summaries'])} corse totali")
        _render_page()

    def _go_page(n):
        total_pages = max(1, (len(state["summaries"]) + PAGE_SIZE - 1) // PAGE_SIZE)
        if n < 0 or n >= total_pages:
            return
        state["page"] = n
        _render_page()
        sc.yview_moveto(0)   # torna in cima

    def _render_page():
        for w in list_frame.winfo_children():
            w.destroy()

        summaries   = state["summaries"]
        page        = state["page"]
        total_pages = max(1, (len(summaries) + PAGE_SIZE - 1) // PAGE_SIZE)
        start       = page * PAGE_SIZE
        end         = start + PAGE_SIZE
        page_items  = summaries[start:end]

        page_var.set(f"Pagina {page + 1} / {total_pages}  "
                     f"(righe {start + 1}–{min(end, len(summaries))} "
                     f"di {len(summaries)})")
        btn_prev.config(state="normal" if page > 0             else "disabled")
        btn_next.config(state="normal" if page < total_pages-1 else "disabled")

        if not summaries:
            tk.Label(list_frame,
                     text="Nessuna corsa trovata.\n\n"
                          "Scarica le attività da Strava oppure apri un file JSON.",
                     font=("Courier", 11), fg=C["text_dim"], bg=C["bg"],
                     pady=40, justify="center").pack()
            return

        for i, s in enumerate(page_items):
            bg_even = C["surface2"]
            bg_odd  = C["bg"]
            bg      = bg_even if i % 2 == 0 else bg_odd
            bg_hover = C["surface"] if i % 2 == 0 else C["surface2"]

            row = tk.Frame(list_frame, bg=bg)
            row.pack(fill="x")

            date_s  = s.get("start_date", "")[:10]
            name_s  = s.get("name", "–")
            dist_s  = f"{s.get('distance', 0) / 1000:.2f}"
            time_s  = fmt_time(s.get("moving_time", 0))
            pace_s  = fmt_pace(s.get("avg_speed", 0))
            pace_col = _pace_chip_color(s.get("avg_speed", 0))
            hr_s    = f"{s['avg_hr']:.0f}" if s.get("avg_hr") else "–"
            elev_s  = f"{s.get('elev_gain', 0):.0f}m"

            cells = []
            for v, col, w, anc in [
                (date_s, C["text_dim"], 12, "center"),
                (name_s, C["text"],     32, "w"),
                (dist_s, C["accent"],    9, "center"),
                (time_s, C["blue"],      8, "center"),
                (pace_s, pace_col,       8, "center"),
                (hr_s,   C["red"],       6, "center"),
                (elev_s, C["yellow"],    8, "center"),
            ]:
                lbl = tk.Label(row, text=v, font=("Courier", 10), fg=col, bg=bg,
                               width=w, anchor=anc, pady=7, padx=4)
                lbl.pack(side="left")
                cells.append(lbl)

            act_f = tk.Frame(row, bg=bg)
            act_f.pack(side="left", padx=4)
            cells.append(act_f)
            summary = s

            btn_open = tk.Button(act_f, text="📂 Apri", font=("Courier", 8, "bold"),
                      bg=C["surface"], fg=C["text"], bd=0, padx=6, pady=2,
                      cursor="hand2",
                      command=lambda s=summary: on_open(s))
            btn_open.pack(side="left", padx=2)
            btn_cmp = tk.Button(act_f, text="➕ Confronto", font=("Courier", 8, "bold"),
                      bg=C["surface"], fg=C["accent"], bd=0, padx=6, pady=2,
                      cursor="hand2",
                      command=lambda s=summary: _add_to_compare(s))
            btn_cmp.pack(side="left", padx=2)
            if summary.get("strava_id"):
                tk.Button(act_f, text="🟠 Strava", font=("Courier", 8, "bold"),
                          bg=C["surface"], fg="#FC4C02", bd=0, padx=6, pady=2,
                          cursor="hand2",
                          command=lambda sid=summary["strava_id"]:
                              webbrowser.open(f"https://www.strava.com/activities/{sid}")
                          ).pack(side="left", padx=2)
            btn_del = tk.Button(act_f, text="🗑", font=("Courier", 8, "bold"),
                      bg=C["surface"], fg=C["red"], bd=0, padx=6, pady=2,
                      cursor="hand2",
                      command=lambda s=summary: _delete(s))
            btn_del.pack(side="left", padx=2)

            # Hover effect sulla riga
            all_row_widgets = [row, act_f] + cells

            def _on_enter(e, widgets=all_row_widgets, hbg=bg_hover, lbgs=cells, rbg=bg):
                for w in widgets:
                    w.config(bg=hbg)

            def _on_leave(e, widgets=all_row_widgets, rbg=bg):
                for w in widgets:
                    w.config(bg=rbg)

            for w in [row] + cells:
                w.bind("<Enter>", _on_enter)
                w.bind("<Leave>", _on_leave)

        refresh_cmp_label()

    def _add_to_compare(summary):
        if len(app_ref.cmp_list) >= MAX_COMPARE - 1:
            messagebox.showwarning("Limite",
                                   f"Puoi confrontare al massimo {MAX_COMPARE} attività.")
            return
        act = storage_mgr.load_activity(summary)
        if act:
            on_compare_add(act)
            refresh_cmp_label()

    def _delete(summary):
        name = summary.get("name", "questa attività")
        if not messagebox.askyesno("Elimina", f"Eliminare '{name}'?"):
            return
        try:
            storage_mgr.delete(summary)
        except Exception as e:
            messagebox.showerror("Errore", str(e))
            return
        _search()

    # Caricamento iniziale
    _search()
