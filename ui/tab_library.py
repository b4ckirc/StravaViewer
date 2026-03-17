# ── ui/tab_library.py ─────────────────────────────────────────────────────────
import tkinter as tk
import webbrowser
from tkinter import ttk, messagebox
from datetime import datetime
from config import C, COMPARE_EMOJIS, MAX_COMPARE
from models import fmt_time, fmt_pace
from i18n import t

PAGE_SIZE = 100


def _pace_chip_color(speed_ms: float) -> str:
    """Semantic color for pace: green < 5:00, yellow < 6:30, red beyond."""
    if speed_ms <= 0:
        return C["text_dim"]
    pace_sec = 1000 / speed_ms          # seconds per km
    if pace_sec < 300:                  # < 5:00/km
        return C["green"]
    if pace_sec < 390:                  # < 6:30/km
        return C["yellow"]
    return C["red"]


def render(tab, storage_mgr, on_open, on_compare_add, on_compare_clear, app_ref):
    for w in tab.winfo_children():
        w.destroy()

    # ── Data source ───────────────────────────────────────────────────────────
    def get_summaries(filters=None):
        return storage_mgr.list_all(filters)

    # Pagination state
    state = {"page": 0, "summaries": []}

    # ── Filters ────────────────────────────────────────────────────────────────
    fbar = tk.Frame(tab, bg=C["surface"], pady=10)
    fbar.pack(fill="x")

    tk.Label(fbar, text=t("filter_label"), font=("Segoe UI", 9, "bold"),
             fg=C["text_dim"], bg=C["surface"]).pack(side="left", padx=(16, 8))

    tk.Label(fbar, text=t("filter_name"), font=("Segoe UI", 8),
             fg=C["text_dim"], bg=C["surface"]).pack(side="left")
    name_var = tk.StringVar()
    tk.Entry(fbar, textvariable=name_var, font=("Segoe UI", 9),
             bg=C["surface2"], fg=C["text"], width=18, bd=0,
             insertbackground=C["text"],
             highlightthickness=1, highlightbackground=C["border"]
             ).pack(side="left", padx=(4, 14))

    tk.Label(fbar, text=t("filter_dist_km"), font=("Segoe UI", 8),
             fg=C["text_dim"], bg=C["surface"]).pack(side="left")
    dist_min_var = tk.StringVar()
    dist_max_var = tk.StringVar()
    tk.Entry(fbar, textvariable=dist_min_var, font=("Segoe UI", 9),
             bg=C["surface2"], fg=C["text"], width=6, bd=0,
             insertbackground=C["text"],
             highlightthickness=1, highlightbackground=C["border"]
             ).pack(side="left", padx=(4, 2))
    tk.Label(fbar, text="–", fg=C["text_dim"], bg=C["surface"],
             font=("Segoe UI", 9)).pack(side="left")
    tk.Entry(fbar, textvariable=dist_max_var, font=("Segoe UI", 9),
             bg=C["surface2"], fg=C["text"], width=6, bd=0,
             insertbackground=C["text"],
             highlightthickness=1, highlightbackground=C["border"]
             ).pack(side="left", padx=(2, 14))

    tk.Label(fbar, text=t("filter_elev_m"), font=("Segoe UI", 8),
             fg=C["text_dim"], bg=C["surface"]).pack(side="left")
    elev_min_var = tk.StringVar()
    elev_max_var = tk.StringVar()
    tk.Entry(fbar, textvariable=elev_min_var, font=("Segoe UI", 9),
             bg=C["surface2"], fg=C["text"], width=6, bd=0,
             insertbackground=C["text"],
             highlightthickness=1, highlightbackground=C["border"]
             ).pack(side="left", padx=(4, 2))
    tk.Label(fbar, text="–", fg=C["text_dim"], bg=C["surface"],
             font=("Segoe UI", 9)).pack(side="left")
    tk.Entry(fbar, textvariable=elev_max_var, font=("Segoe UI", 9),
             bg=C["surface2"], fg=C["text"], width=6, bd=0,
             insertbackground=C["text"],
             highlightthickness=1, highlightbackground=C["border"]
             ).pack(side="left", padx=(2, 14))

    tk.Label(fbar, text=t("filter_date_from"), font=("Segoe UI", 8),
             fg=C["text_dim"], bg=C["surface"]).pack(side="left")
    date_from_var = tk.StringVar()
    date_to_var   = tk.StringVar()
    tk.Entry(fbar, textvariable=date_from_var, font=("Segoe UI", 9),
             bg=C["surface2"], fg=C["text"], width=11, bd=0,
             insertbackground=C["text"],
             highlightthickness=1, highlightbackground=C["border"]
             ).pack(side="left", padx=(4, 2))
    tk.Label(fbar, text=t("filter_date_to"), fg=C["text_dim"], bg=C["surface"],
             font=("Segoe UI", 8)).pack(side="left", padx=(6, 0))
    tk.Entry(fbar, textvariable=date_to_var, font=("Segoe UI", 9),
             bg=C["surface2"], fg=C["text"], width=11, bd=0,
             insertbackground=C["text"],
             highlightthickness=1, highlightbackground=C["border"]
             ).pack(side="left", padx=(4, 2))
    tk.Label(fbar, text="(YYYY-MM-DD)", font=("Segoe UI", 7),
             fg=C["text_dim"], bg=C["surface"]).pack(side="left", padx=(4, 12))

    races_var = tk.BooleanVar(value=False)
    tk.Checkbutton(
        fbar, text=t("filter_races_only"), variable=races_var,
        font=("Segoe UI", 8), fg=C["text"], bg=C["surface"],
        selectcolor=C["surface2"], activebackground=C["surface"],
        activeforeground=C["text"],
    ).pack(side="left", padx=(4, 8))

    count_var = tk.StringVar(value="")
    tk.Label(fbar, textvariable=count_var, font=("Segoe UI", 8),
             fg=C["green"], bg=C["surface"]).pack(side="right", padx=12)

    src_text = "● MongoDB" if (storage_mgr.mongo_ok and storage_mgr.mongo_storage) else "○ File JSON"
    src_col  = C["green"] if (storage_mgr.mongo_ok and storage_mgr.mongo_storage) else C["yellow"]
    tk.Label(fbar, text=src_text, font=("Segoe UI", 7, "bold"),
             fg=src_col, bg=C["surface"]).pack(side="right", padx=8)

    tk.Button(fbar, text="🔍", font=("Segoe UI", 10), bg=C["accent"],
              fg="white", bd=0, padx=10, pady=4, cursor="hand2",
              command=lambda: _search()).pack(side="left", padx=4)

    # ── Comparison bar ───────────────────────────────────────────────────────
    cbar = tk.Frame(tab, bg=C["surface2"], pady=8)
    cbar.pack(fill="x")
    cmp_label = tk.Label(cbar, text=t("compare_none"),
                         font=("Segoe UI", 9), fg=C["text_dim"], bg=C["surface2"])
    cmp_label.pack(side="left", padx=16)

    def refresh_cmp_label():
        n = len(app_ref.cmp_list)
        if n == 0:
            cmp_label.config(text=t("compare_none"), fg=C["text_dim"])
        else:
            names = "  ".join(f"{COMPARE_EMOJIS[i+1]} {app_ref.cmp_list[i].name[:20]}"
                              for i in range(n))
            cmp_label.config(text=f"{t('compare_count').format(n=n)} {names}", fg=C["accent"])

    tk.Button(cbar, text=t("btn_clear_compare"), font=("Segoe UI", 8, "bold"),
              bg=C["surface2"], fg=C["text_dim"], bd=0, padx=10, cursor="hand2",
              command=lambda: [on_compare_clear(), refresh_cmp_label(), _render_page()]
              ).pack(side="right", padx=8)
    tk.Button(cbar, text=t("btn_run_compare"), font=("Segoe UI", 8, "bold"),
              bg=C["accent"], fg="white", bd=0, padx=10, cursor="hand2",
              command=lambda: app_ref._run_compare()
              ).pack(side="right", padx=4)

    # ── Table header ─────────────────────────────────────────────────────────
    cols   = [t("col_date"), t("col_name"), t("col_dist"), t("col_time"), t("col_pace"), t("col_hr"), t("col_elev"), t("col_actions")]
    widths = [12,       32,     9,       8,       8,       6,     8,       18]

    hdr_f = tk.Frame(tab, bg=C["surface"])
    hdr_f.pack(fill="x")
    for col, w in zip(cols, widths):
        tk.Label(hdr_f, text=col, font=("Segoe UI", 10, "bold"),
                 fg=C["text_dim"], bg=C["surface"],
                 width=w, anchor="w" if col == "NOME" else "center",
                 pady=8, padx=4).pack(side="left")

    # ── Scrollable list ─────────────────────────────────────────────────────
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

    # ── Pagination bar (in the bottom) ───────────────────────────────────────
    pag_f = tk.Frame(tab, bg=C["surface"], pady=8)
    pag_f.pack(fill="x", side="bottom")

    page_var = tk.StringVar(value="")
    tk.Label(pag_f, textvariable=page_var, font=("Segoe UI", 9),
             fg=C["text_dim"], bg=C["surface"]).pack(side="left", padx=16)

    btn_next = tk.Button(pag_f, text=t("page_next"), font=("Segoe UI", 9, "bold"),
                         bg=C["surface2"], fg=C["text"], bd=0, padx=12, pady=4,
                         cursor="hand2", command=lambda: _go_page(state["page"] + 1))
    btn_next.pack(side="right", padx=8)

    btn_prev = tk.Button(pag_f, text=t("page_prev"), font=("Segoe UI", 9, "bold"),
                         bg=C["surface2"], fg=C["text"], bd=0, padx=12, pady=4,
                         cursor="hand2", command=lambda: _go_page(state["page"] - 1))
    btn_prev.pack(side="right", padx=4)

    # ── Logic ────────────────────────────────────────────────────────────────

    def _search():
        """Load all filtered summaries, then go to page 0."""
        filters = {}
        if name_var.get().strip():
            filters["name"] = name_var.get().strip()
        def _to_float(s):
            return float(s.strip().replace(",", ".")) if s.strip() else None
        try:
            v = _to_float(dist_min_var.get())
            if v is not None: filters["dist_min"] = v
            v = _to_float(dist_max_var.get())
            if v is not None: filters["dist_max"] = v
        except ValueError:
            pass
        try:
            v = _to_float(elev_min_var.get())
            if v is not None: filters["elev_min"] = v
            v = _to_float(elev_max_var.get())
            if v is not None: filters["elev_max"] = v
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
        count_var.set(t("runs_total").format(n=len(state["summaries"])))
        _render_page()

    def _go_page(n):
        total_pages = max(1, (len(state["summaries"]) + PAGE_SIZE - 1) // PAGE_SIZE)
        if n < 0 or n >= total_pages:
            return
        state["page"] = n
        _render_page()
        sc.yview_moveto(0)   # go to top of the list on page change

    def _render_page():
        for w in list_frame.winfo_children():
            w.destroy()

        summaries   = state["summaries"]
        page        = state["page"]
        total_pages = max(1, (len(summaries) + PAGE_SIZE - 1) // PAGE_SIZE)
        start       = page * PAGE_SIZE
        end         = start + PAGE_SIZE
        page_items  = summaries[start:end]

        page_var.set(t("page_info").format(
            cur=page + 1, tot=total_pages,
            **{"from": start + 1}, to=min(end, len(summaries)),
            all=len(summaries)))
        btn_prev.config(state="normal" if page > 0             else "disabled")
        btn_next.config(state="normal" if page < total_pages-1 else "disabled")

        if not summaries:
            tk.Label(list_frame,
                     text=t("library_empty"),
                     font=("Segoe UI", 11), fg=C["text_dim"], bg=C["bg"],
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
                lbl = tk.Label(row, text=v, font=("Segoe UI", 10), fg=col, bg=bg,
                               width=w, anchor=anc, pady=7, padx=4)
                lbl.pack(side="left")
                cells.append(lbl)

            act_f = tk.Frame(row, bg=bg)
            act_f.pack(side="left", padx=4)
            cells.append(act_f)
            summary = s

            btn_open = tk.Button(act_f, text=t("btn_open"), font=("Segoe UI", 8, "bold"),
                      bg=C["surface"], fg=C["text"], bd=0, padx=6, pady=2,
                      cursor="hand2",
                      command=lambda s=summary: on_open(s))
            btn_open.pack(side="left", padx=2)
            btn_cmp = tk.Button(act_f, text=t("btn_compare_add"), font=("Segoe UI", 8, "bold"),
                      bg=C["surface"], fg=C["accent"], bd=0, padx=6, pady=2,
                      cursor="hand2",
                      command=lambda s=summary: _add_to_compare(s))
            btn_cmp.pack(side="left", padx=2)
            if summary.get("strava_id"):
                tk.Button(act_f, text=t("btn_open_strava"), font=("Segoe UI", 8, "bold"),
                          bg=C["surface"], fg="#FC4C02", bd=0, padx=6, pady=2,
                          cursor="hand2",
                          command=lambda sid=summary["strava_id"]:
                              webbrowser.open(f"https://www.strava.com/activities/{sid}")
                          ).pack(side="left", padx=2)
            btn_del = tk.Button(act_f, text=t("btn_delete"), font=("Segoe UI", 8, "bold"),
                      bg=C["surface"], fg=C["red"], bd=0, padx=6, pady=2,
                      cursor="hand2",
                      command=lambda s=summary: _delete(s))
            btn_del.pack(side="left", padx=2)

            # Hover effect on the entire row (including action buttons)
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
            messagebox.showwarning(t("msg_limit"),
                                   t("compare_limit").format(n=MAX_COMPARE))
            return
        act = storage_mgr.load_activity(summary)
        if act:
            on_compare_add(act)
            refresh_cmp_label()

    def _delete(summary):
        name = summary.get("name", "")
        if not messagebox.askyesno(t("msg_delete"), t("msg_delete_confirm").format(name=name)):
            return
        try:
            storage_mgr.delete(summary)
        except Exception as e:
            messagebox.showerror(t("msg_error"), str(e))
            return
        _search()

    # Init: load first page
    _search()
