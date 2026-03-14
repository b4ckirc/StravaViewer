# ── ui/app.py ─────────────────────────────────────────────────────────────────
"""
Finestra principale dell'applicazione Strava Viewer v3.0.
"""

import json, os, tkinter as tk
from tkinter import ttk, filedialog, messagebox
import config as _cfg
from config import C, MAX_COMPARE, APP_NAME, APP_VERSION
from models import ActivityData
from storage_manager import StorageManager

import ui.tab_dashboard  as tab_dashboard
import ui.tab_charts     as tab_charts
import ui.tab_hr         as tab_hr
import ui.tab_map        as tab_map
import ui.tab_splits     as tab_splits
import ui.tab_best       as tab_best
import ui.tab_compare    as tab_compare
import ui.tab_library    as tab_library
import ui.tab_stats      as tab_stats
import ui.tab_calendar   as tab_calendar
import ui.tab_raw        as tab_raw
from ui.downloader_ui    import open_download_window
from ui.widgets          import topbar_btn, clear

# Definizione tab: (attributo, icona, etichetta, gruppo)
_TAB_DEFS = [
    ("tab_dash",     "⬡",  "Dashboard",    "activity"),
    ("tab_chart",    "▤",  "Grafici",       "activity"),
    ("tab_hrzone",   "♥",  "Zone HR",       "activity"),
    ("tab_map",      "◈",  "Mappa",         "activity"),
    ("tab_split",    "≡",  "Splits",        "activity"),
    ("tab_best",     "★",  "Best Efforts",  "activity"),
    ("tab_compare",  "⇄",  "Confronto",     "activity"),
    ("tab_raw",      "{ }", "Raw JSON",     "activity"),
    ("tab_library",  "▣",  "Libreria",      "global"),
    ("tab_calendar", "▦",  "Calendario",    "global"),
    ("tab_stats",    "≈",  "Statistiche",   "global"),
]


class StravaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME}  v{APP_VERSION}")
        self.configure(bg=C["bg"])
        self.geometry("1500x940")
        self.minsize(1200, 720)

        self.activity   = None        # attività principale analizzata
        self.cmp_list   = []          # lista ActivityData per confronto (max 4 extra)
        self.storage    = StorageManager()

        self._build_ui()
        self._show_welcome()
        self._try_connect_mongo()

    # ── Connessione MongoDB (background) ──────────────────────────────────────

    def _try_connect_mongo(self):
        import threading
        def _connect():
            ok, msg = self.storage.connect_mongo(auto_start=True)
            self.after(0, lambda: self._on_mongo_result(ok, msg))
        threading.Thread(target=_connect, daemon=True).start()
        self._mongo_status_var.set("MongoDB: connessione…")

    def _on_mongo_result(self, ok, msg):
        if ok:
            self._mongo_status_var.set("● MongoDB")
            self._mongo_status_lbl.config(fg=C["green"])
        else:
            self._mongo_status_var.set("○ MongoDB offline")
            self._mongo_status_lbl.config(fg=C["text_dim"])

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build_ui(self):
        self._tab_frames   = {}   # attr → tk.Frame (contenuto)
        self._tab_buttons  = {}   # attr → (container, strip, icon_lbl, text_lbl)
        self._active_tab   = None

        # ── Topbar ────────────────────────────────────────────────────────────
        topbar = tk.Frame(self, bg=C["surface"], height=52)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)

        tk.Label(topbar, text=f"⬡  STRAVA VIEWER",
                 font=("Courier", 12, "bold"), fg=C["accent"],
                 bg=C["surface"]).pack(side="left", padx=20, pady=14)

        # Status MongoDB (destra)
        self._mongo_status_var = tk.StringVar(value="MongoDB: …")
        self._mongo_status_lbl = tk.Label(
            topbar, textvariable=self._mongo_status_var,
            font=("Courier", 8), fg=C["text_dim"], bg=C["surface"],
            cursor="hand2")
        self._mongo_status_lbl.pack(side="right", padx=16)
        self._mongo_status_lbl.bind("<Button-1>", lambda e: self._toggle_mongo())

        # Separatore verticale
        tk.Frame(topbar, bg=C["border"], width=1).pack(
            side="right", fill="y", pady=12)

        # Bottoni destra → sinistra
        topbar_btn(topbar, "📂  Apri File",
                   self._open_file,
                   tooltip="Apri un file JSON di attività Strava"
                   ).pack(side="right", padx=4, pady=10)
        topbar_btn(topbar, "⬇  Scarica da Strava",
                   self._open_downloader, primary=True,
                   tooltip="Autentica con Strava e scarica le tue attività"
                   ).pack(side="right", padx=4, pady=10)
        topbar_btn(topbar, "💾  Esporta",
                   self._export_menu,
                   tooltip="Esporta attività corrente in PNG, PDF, CSV o GPX"
                   ).pack(side="right", padx=4, pady=10)
        topbar_btn(topbar, "📦  Database",
                   self._database_menu,
                   tooltip="Backup ZIP, import e heatmap del database"
                   ).pack(side="right", padx=4, pady=10)

        # Toggle tema
        theme_lbl = "🌙  Scuro" if _cfg._current_theme[0] == "light" else "☀  Chiaro"
        topbar_btn(topbar, theme_lbl,
                   self._toggle_theme,
                   tooltip="Passa al tema scuro / chiaro"
                   ).pack(side="right", padx=4, pady=10)

        # ── Separatore topbar / body ──────────────────────────────────────────
        tk.Frame(self, bg=C["border"], height=1).pack(fill="x")

        # ── Body: sidebar + content ───────────────────────────────────────────
        body = tk.Frame(self, bg=C["bg"])
        body.pack(fill="both", expand=True)

        # ── Sidebar ───────────────────────────────────────────────────────────
        sidebar = tk.Frame(body, bg=C["surface"], width=180)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Logo sidebar
        tk.Label(sidebar, text="⬡", font=("Courier", 20, "bold"),
                 fg=C["accent"], bg=C["surface"]).pack(pady=(18, 2))
        tk.Label(sidebar, text=f"v{APP_VERSION}",
                 font=("Courier", 7), fg=C["text_dim"],
                 bg=C["surface"]).pack()
        tk.Frame(sidebar, bg=C["border"], height=1).pack(
            fill="x", padx=16, pady=(10, 6))

        # Gruppi tab
        def _section(text):
            tk.Label(sidebar, text=text.upper(),
                     font=("Courier", 7, "bold"), fg=C["text_dim"],
                     bg=C["surface"]).pack(anchor="w", padx=16, pady=(8, 2))

        _section("Analisi")
        activity_tabs = [t for t in _TAB_DEFS if t[3] == "activity"]
        global_tabs   = [t for t in _TAB_DEFS if t[3] == "global"]

        for attr, icon, label, _ in activity_tabs:
            self._make_nav_item(sidebar, attr, icon, label)

        tk.Frame(sidebar, bg=C["border"], height=1).pack(
            fill="x", padx=16, pady=(8, 4))
        _section("Database")
        for attr, icon, label, _ in global_tabs:
            self._make_nav_item(sidebar, attr, icon, label)

        # Separatore sidebar / content
        tk.Frame(body, bg=C["border"], width=1).pack(side="left", fill="y")

        # ── Area contenuto ────────────────────────────────────────────────────
        content = tk.Frame(body, bg=C["bg"])
        content.pack(side="left", fill="both", expand=True)
        self._content = content

        # Crea tutti i frame dei tab nell'area contenuto
        for attr, icon, label, _ in _TAB_DEFS:
            frame = tk.Frame(content, bg=C["bg"])
            setattr(self, attr, frame)
            self._tab_frames[attr] = frame

        # Mostra il primo tab
        self._show_tab("tab_dash")

    def _make_nav_item(self, parent, attr, icon, label):
        """Crea un elemento di navigazione nella sidebar e salva i riferimenti."""
        container = tk.Frame(parent, bg=C["surface"], cursor="hand2")
        container.pack(fill="x", pady=1)

        # Strip colorata sinistra (indicatore attivo)
        strip = tk.Frame(container, bg=C["surface"], width=3)
        strip.pack(side="left", fill="y")

        icon_lbl = tk.Label(container, text=icon, font=("Courier", 11),
                            bg=C["surface"], fg=C["text_dim"], width=3)
        icon_lbl.pack(side="left", padx=(8, 4), pady=8)

        text_lbl = tk.Label(container, text=label, font=("Courier", 9, "bold"),
                            bg=C["surface"], fg=C["text_dim"], anchor="w")
        text_lbl.pack(side="left", pady=8)

        # Click e hover
        def _click(e=None, a=attr):
            self._show_tab(a)

        def _enter(e=None, a=attr):
            if self._active_tab != a:
                for w in (container, strip, icon_lbl, text_lbl):
                    w.config(bg=C["surface2"])

        def _leave(e=None, a=attr):
            if self._active_tab != a:
                for w in (container, strip, icon_lbl, text_lbl):
                    w.config(bg=C["surface"])

        for w in (container, strip, icon_lbl, text_lbl):
            w.bind("<Button-1>", _click)
            w.bind("<Enter>",    _enter)
            w.bind("<Leave>",    _leave)

        self._tab_buttons[attr] = (container, strip, icon_lbl, text_lbl)

    def _show_tab(self, attr):
        """Mostra il frame del tab selezionato e aggiorna la sidebar."""
        # Deseleziona tab precedente
        if self._active_tab and self._active_tab in self._tab_buttons:
            prev = self._active_tab
            container, strip, icon_lbl, text_lbl = self._tab_buttons[prev]
            strip.config(bg=C["surface"])
            icon_lbl.config(fg=C["text_dim"], bg=C["surface"])
            text_lbl.config(fg=C["text_dim"], bg=C["surface"])
            container.config(bg=C["surface"])
            if prev in self._tab_frames:
                self._tab_frames[prev].pack_forget()

        self._active_tab = attr

        # Attiva nuovo tab nella sidebar
        if attr in self._tab_buttons:
            container, strip, icon_lbl, text_lbl = self._tab_buttons[attr]
            container.config(bg=C["surface"])
            strip.config(bg=C["accent"])
            icon_lbl.config(fg=C["accent"], bg=C["surface"])
            text_lbl.config(fg=C["accent"], bg=C["surface"])

        # Mostra il frame
        if attr in self._tab_frames:
            self._tab_frames[attr].pack(fill="both", expand=True)

        # Render lazy per tab che ne hanno bisogno
        self._on_tab_show(attr)

    def _on_tab_show(self, attr):
        if attr == "tab_library":
            self._render_library()
        elif attr == "tab_stats":
            tab_stats.render(self.tab_stats, self.storage, on_open=self._open_from_library)
        elif attr == "tab_calendar":
            tab_calendar.render(self.tab_calendar, self.storage,
                                on_open=self._open_from_library)

    # ── Welcome ───────────────────────────────────────────────────────────────

    def _show_welcome(self):
        for attr in ("tab_dash","tab_chart","tab_hrzone","tab_map",
                     "tab_split","tab_best","tab_compare","tab_raw"):
            clear(getattr(self, attr))
        tk.Label(self.tab_dash,
                 text="⬡\n\nBenvenuto in Strava Viewer\n\n"
                      "• Apri un file JSON con «Apri File»\n"
                      "• Scarica le corse da Strava con «Scarica da Strava»\n"
                      "• Sfoglia la libreria nel tab «Libreria»",
                 font=("Courier", 12), fg=C["text_dim"], bg=C["bg"],
                 justify="center").pack(expand=True)
        self._show_tab("tab_dash")
        self._render_library()

    # ── Tema chiaro/scuro ─────────────────────────────────────────────────────

    def _toggle_theme(self):
        if _cfg._current_theme[0] == "dark":
            C.update(_cfg.C_LIGHT)
            _cfg._current_theme[0] = "light"
        else:
            C.update(_cfg.C_DARK)
            _cfg._current_theme[0] = "dark"
        self._rebuild()

    def _rebuild(self):
        """Distrugge e ricostruisce tutta la UI con la palette C aggiornata."""
        act      = self.activity
        cmp      = list(self.cmp_list)
        prev_tab = getattr(self, "_active_tab", "tab_dash")
        for w in self.winfo_children():
            w.destroy()
        self.configure(bg=C["bg"])
        self._build_ui()
        self.cmp_list = cmp
        if act:
            self._load_activity(act)
            if prev_tab and prev_tab in self._tab_frames:
                self._show_tab(prev_tab)
        else:
            self._show_welcome()

    # ── Apertura file JSON singolo ────────────────────────────────────────────

    def _open_file(self):
        path = filedialog.askopenfilename(
            title="Seleziona attività Strava (JSON)",
            filetypes=[("JSON", "*.json"), ("Tutti", "*.*")])
        if not path:
            return
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            messagebox.showerror("Errore lettura", str(e))
            return
        self._load_activity(ActivityData(data))

    def _load_activity(self, act: ActivityData):
        self.activity = act
        self.title(f"{APP_NAME}  •  {act.name}")
        tab_dashboard.render(self.tab_dash,   act)
        tab_charts.render(self.tab_chart,     act)
        tab_hr.render(self.tab_hrzone,        act)
        tab_map.render(self.tab_map,          act)
        tab_splits.render(self.tab_split,     act)
        tab_best.render(self.tab_best,        act)
        tab_raw.render(self.tab_raw,          act)
        self._show_tab("tab_dash")

    # ── Downloader Strava ─────────────────────────────────────────────────────

    def _open_downloader(self):
        open_download_window(self, self.storage,
                             on_done_cb=self._render_library)

    # ── Libreria ──────────────────────────────────────────────────────────────

    def _render_library(self):
        tab_library.render(
            tab          = self.tab_library,
            storage_mgr  = self.storage,
            on_open      = self._open_from_library,
            on_compare_add   = self._compare_add,
            on_compare_clear = self._compare_clear,
            app_ref      = self,
        )

    def _open_from_library(self, summary: dict):
        act = self.storage.load_activity(summary)
        if not act:
            messagebox.showerror("Errore", "Impossibile caricare l'attività.")
            return
        self._load_activity(act)

    # ── Confronto ─────────────────────────────────────────────────────────────

    def _compare_add(self, act: ActivityData):
        if len(self.cmp_list) >= MAX_COMPARE - 1:
            messagebox.showwarning("Limite", f"Massimo {MAX_COMPARE} attività.")
            return
        self.cmp_list.append(act)

    def _compare_clear(self):
        self.cmp_list.clear()

    def _run_compare(self):
        if not self.activity and not self.cmp_list:
            messagebox.showinfo("Info", "Seleziona almeno un'attività.")
            return
        if self.activity:
            all_acts = [self.activity] + self.cmp_list
        else:
            all_acts = list(self.cmp_list)
        if len(all_acts) < 2:
            messagebox.showinfo("Info",
                                "Aggiungi almeno 2 attività per il confronto.\n\n"
                                "Prima apri un'attività principale, poi aggiungi "
                                "altre dal tab Libreria col pulsante ➕.")
            return
        tab_compare.render(self.tab_compare, all_acts)
        self._show_tab("tab_compare")

    # ── MongoDB toggle ─────────────────────────────────────────────────────────

    def _toggle_mongo(self):
        if self.storage.mongo_ok:
            self.storage.disconnect_mongo()
            self._mongo_status_var.set("○ MongoDB offline")
            self._mongo_status_lbl.config(fg=C["text_dim"])
        else:
            self._mongo_status_var.set("MongoDB: connessione…")
            self._mongo_status_lbl.config(fg=C["text_dim"])
            import threading
            threading.Thread(target=self._try_connect_mongo, daemon=True).start()

    # ── Export attività corrente ───────────────────────────────────────────────

    def _export_menu(self):
        win = tk.Toplevel(self)
        win.title("Esporta")
        win.configure(bg=C["bg"])
        win.geometry("340x370")
        win.resizable(False, False)
        tk.Label(win, text="SCEGLI FORMATO",
                 font=("Courier", 10, "bold"), fg=C["accent"],
                 bg=C["bg"]).pack(pady=(20, 4))
        tk.Label(win, text="— attività corrente —",
                 font=("Courier", 8), fg=C["text_dim"],
                 bg=C["bg"]).pack(pady=(0, 8))
        b = dict(font=("Courier", 10, "bold"), bd=0, pady=10,
                 cursor="hand2", relief="flat", width=28)
        act_cmds = [
            ("📊  PNG — Grafici",   self._export_png),
            ("📄  PDF — Report",    self._export_pdf),
            ("📋  CSV — Splits",    self._export_csv),
            ("📍  GPX — Tracciato", self._export_gpx),
        ]
        for txt, cmd in act_cmds:
            tk.Button(win, text=txt, bg=C["surface2"], fg=C["text"],
                      command=lambda c=cmd: [win.destroy(),
                                             c() if self.activity else
                                             messagebox.showinfo(
                                                 "Info",
                                                 "Apri prima un'attività.")],
                      **b).pack(pady=3)

        tk.Label(win, text="— database completo —",
                 font=("Courier", 8), fg=C["text_dim"],
                 bg=C["bg"]).pack(pady=(10, 4))
        tk.Button(win, text="📈  CSV — Statistiche",
                  bg=C["surface2"], fg=C["text"],
                  command=lambda: [win.destroy(), self._export_stats_csv()],
                  **b).pack(pady=3)
        tk.Button(win, text="✕  Annulla", bg=C["bg"], fg=C["text_dim"],
                  command=win.destroy, **b).pack(pady=(8, 0))

    # ── Database backup/restore ────────────────────────────────────────────────

    def _database_menu(self):
        win = tk.Toplevel(self)
        win.title("Database")
        win.configure(bg=C["bg"])
        win.geometry("340x280")
        win.resizable(False, False)
        tk.Label(win, text="GESTIONE DATABASE",
                 font=("Courier", 10, "bold"), fg=C["accent"],
                 bg=C["bg"]).pack(pady=(20, 12))
        b = dict(font=("Courier", 10, "bold"), bd=0, pady=10,
                 cursor="hand2", relief="flat", width=28)
        tk.Button(win, text="📦  Esporta tutto (ZIP)",  bg=C["surface2"], fg=C["text"],
                  command=lambda: [win.destroy(), self._export_zip()], **b).pack(pady=4)
        tk.Button(win, text="📥  Importa da ZIP",       bg=C["surface2"], fg=C["text"],
                  command=lambda: [win.destroy(), self._import_zip()], **b).pack(pady=4)
        tk.Button(win, text="🗺  Heatmap corse",        bg=C["surface2"], fg=C["text"],
                  command=lambda: [win.destroy(), self._open_heatmap()], **b).pack(pady=4)
        tk.Button(win, text="✕  Annulla",               bg=C["bg"],       fg=C["text_dim"],
                  command=win.destroy, **b).pack(pady=(8, 0))

    def _export_zip(self):
        import zipfile
        path = filedialog.asksaveasfilename(
            defaultextension=".zip",
            initialfile="strava_backup.zip",
            filetypes=[("ZIP", "*.zip")])
        if not path:
            return
        try:
            count = 0
            with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
                if self.storage.mongo_ok and self.storage.mongo_storage:
                    # Esporta da MongoDB
                    cursor = self.storage.mongo_storage._coll.find({})
                    for doc in cursor:
                        doc.pop("_id", None)
                        act_id   = doc.get("id", "unknown")
                        date_str = (doc.get("start_date_local", "")[:10]) or "nodate"
                        raw_name = doc.get("name", "activity")[:40]
                        import re as _re
                        safe_name = _re.sub(r'[<>:"/\\|?*\x00-\x1f]', '-', raw_name).strip()
                        fname = f"{date_str}_{act_id}_{safe_name}.json"
                        zf.writestr(fname,
                                    json.dumps(doc, ensure_ascii=False, indent=2))
                        count += 1
                else:
                    # Esporta da file JSON locali
                    json_dir = self.storage.json_storage.directory
                    for fname in os.listdir(json_dir):
                        if fname.endswith(".json"):
                            zf.write(os.path.join(json_dir, fname), fname)
                            count += 1
            messagebox.showinfo("Export ZIP",
                                f"Backup completato.\n{count} corse esportate in:\n{path}")
        except Exception as e:
            messagebox.showerror("Errore export ZIP", str(e))

    def _import_zip(self):
        import zipfile
        path = filedialog.askopenfilename(
            title="Seleziona backup ZIP",
            filetypes=[("ZIP", "*.zip"), ("Tutti", "*.*")])
        if not path:
            return
        try:
            new_count  = 0
            skip_count = 0
            err_count  = 0
            with zipfile.ZipFile(path, "r") as zf:
                names = [n for n in zf.namelist() if n.endswith(".json")]
                for name in names:
                    try:
                        data = json.loads(zf.read(name).decode("utf-8"))
                        sid  = data.get("id")
                        if sid and self.storage.exists(sid):
                            skip_count += 1
                            continue
                        self.storage.json_storage.save(data)
                        if self.storage.mongo_ok and self.storage.mongo_storage:
                            self.storage.mongo_storage.save(data)
                        new_count += 1
                    except Exception:
                        err_count += 1
            messagebox.showinfo("Import ZIP",
                                f"Importazione completata:\n"
                                f"• {new_count} corse importate\n"
                                f"• {skip_count} già presenti (saltate)\n"
                                f"• {err_count} errori")
            self._render_library()
        except Exception as e:
            messagebox.showerror("Errore import ZIP", str(e))

    def _export_png(self):
        if not self.activity:
            return
        try:
            import matplotlib.pyplot as plt
            from ui.tab_charts import _build_export_fig
            a    = self.activity
            path = filedialog.asksaveasfilename(
                defaultextension=".png",
                initialfile=f"{a.name[:40].replace(' ','_')}_grafici.png",
                filetypes=[("PNG", "*.png")])
            if not path:
                return
            fig = _build_export_fig(a)
            fig.savefig(path, dpi=180, bbox_inches="tight", facecolor=C["bg"])
            plt.close(fig)
            messagebox.showinfo("Export", f"PNG salvato:\n{path}")
        except Exception as e:
            messagebox.showerror("Errore export", str(e))

    def _export_pdf(self):
        if not self.activity:
            return
        try:
            from ui.export_pdf import export_pdf
            a    = self.activity
            path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                initialfile=f"{a.name[:40].replace(' ','_')}_report.pdf",
                filetypes=[("PDF", "*.pdf")])
            if path:
                export_pdf(a, path)
                messagebox.showinfo("Export", f"PDF salvato:\n{path}")
        except Exception as e:
            messagebox.showerror("Errore export", str(e))

    def _export_csv(self):
        import csv
        a    = self.activity
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile=f"{a.name[:40].replace(' ','_')}_splits.csv",
            filetypes=[("CSV", "*.csv")])
        if not path:
            return
        fields = ["split", "distance", "moving_time", "average_speed",
                  "average_heartrate", "elevation_difference", "average_cadence"]
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            w.writeheader()
            for row in a.splits:
                w.writerow({k: row.get(k, "") for k in fields})
        messagebox.showinfo("Export", f"CSV salvato:\n{path}")

    # ── Export GPX ────────────────────────────────────────────────────────────

    def _export_gpx(self):
        if not self.activity:
            return
        a = self.activity
        if not a.gps_points:
            messagebox.showinfo("GPX", "Nessun dato GPS disponibile per questa attività.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".gpx",
            initialfile=f"{a.name[:40].replace(' ', '_')}.gpx",
            filetypes=[("GPX", "*.gpx"), ("Tutti", "*.*")])
        if not path:
            return
        try:
            _write_gpx(a, path)
            messagebox.showinfo("Export GPX", f"GPX salvato:\n{path}")
        except Exception as e:
            messagebox.showerror("Errore GPX", str(e))

    # ── Export statistiche CSV ────────────────────────────────────────────────

    def _export_stats_csv(self):
        import csv
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile="strava_statistiche.csv",
            filetypes=[("CSV", "*.csv")])
        if not path:
            return
        try:
            monthly = self.storage.stats_per_month()
            fields  = ["mese", "corse", "km_totali", "tempo_sec",
                       "dislivello_m", "passo_medio"]
            with open(path, "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=fields)
                w.writeheader()
                for d in monthly:
                    from models import fmt_pace
                    w.writerow({
                        "mese":         d["month"],
                        "corse":        d["count"],
                        "km_totali":    f"{d['dist_km']:.2f}",
                        "tempo_sec":    d["time_sec"],
                        "dislivello_m": f"{d['elev_gain']:.0f}",
                        "passo_medio":  fmt_pace(d["avg_speed"]),
                    })
            messagebox.showinfo("Export CSV", f"Statistiche esportate:\n{path}")
        except Exception as e:
            messagebox.showerror("Errore CSV", str(e))

    # ── Heatmap ───────────────────────────────────────────────────────────────

    def _open_heatmap(self):
        import threading
        win = tk.Toplevel(self)
        win.title("Heatmap — caricamento…")
        win.configure(bg=C["bg"])
        win.geometry("320x120")
        lbl = tk.Label(win, text="Caricamento polyline in corso…",
                       font=("Courier", 10), fg=C["text_dim"],
                       bg=C["bg"])
        lbl.pack(expand=True)

        def _worker():
            try:
                polys = self.storage.list_polylines()
                self.after(0, lambda: _build_and_open(polys, win))
            except Exception as e:
                self.after(0, lambda: [win.destroy(),
                                       messagebox.showerror("Heatmap", str(e))])

        threading.Thread(target=_worker, daemon=True).start()


# ── Helpers modulo ────────────────────────────────────────────────────────────

def _write_gpx(act, path: str):
    """Genera un file GPX dal tracciato GPS dell'attività."""
    import xml.etree.ElementTree as ET
    gpx = ET.Element("gpx", {
        "version": "1.1",
        "creator": "StravaViewer",
        "xmlns":              "http://www.topografix.com/GPX/1/1",
        "xmlns:xsi":          "http://www.w3.org/2001/XMLSchema-instance",
        "xsi:schemaLocation": ("http://www.topografix.com/GPX/1/1 "
                               "http://www.topografix.com/GPX/1/1/gpx.xsd"),
    })
    meta = ET.SubElement(gpx, "metadata")
    ET.SubElement(meta, "name").text = act.name
    ET.SubElement(meta, "time").text = act.start_date

    trk  = ET.SubElement(gpx, "trk")
    ET.SubElement(trk, "name").text = act.name
    trkseg = ET.SubElement(trk, "trkseg")
    for lat, lon in act.gps_points:
        ET.SubElement(trkseg, "trkpt", {"lat": str(lat), "lon": str(lon)})

    tree = ET.ElementTree(gpx)
    ET.indent(tree, space="  ")
    with open(path, "wb") as f:
        tree.write(f, xml_declaration=True, encoding="utf-8")


def _build_and_open(polys: list, progress_win):
    """Costruisce la heatmap Folium con tutte le polyline e la apre nel browser."""
    import tempfile, webbrowser
    progress_win.destroy()

    if not polys:
        from tkinter import messagebox
        messagebox.showinfo("Heatmap", "Nessun tracciato GPS trovato nel database.")
        return

    try:
        import folium
    except ImportError:
        from tkinter import messagebox
        messagebox.showerror("Heatmap", "Libreria 'folium' non installata.\nEsegui: pip install folium")
        return

    # Centro mappa = media di tutti i punti
    all_pts  = [pt for _, _, pts in polys for pt in pts]
    avg_lat  = sum(p[0] for p in all_pts) / len(all_pts)
    avg_lon  = sum(p[1] for p in all_pts) / len(all_pts)

    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=10,
                   tiles="CartoDB dark_matter")

    for name, date_str, pts in polys:
        folium.PolyLine(
            pts,
            color="#fc4c02",
            weight=2,
            opacity=0.45,
            tooltip=f"{date_str}  {name}",
        ).add_to(m)

    # Salva in file temporaneo e apri nel browser
    tmp = tempfile.NamedTemporaryFile(suffix=".html", delete=False)
    m.save(tmp.name)
    webbrowser.open(f"file:///{tmp.name.replace(chr(92), '/')}")
