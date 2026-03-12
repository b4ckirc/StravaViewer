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
import ui.tab_raw        as tab_raw
from ui.downloader_ui    import open_download_window
from ui.widgets          import topbar_btn, clear


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
        # Topbar
        topbar = tk.Frame(self, bg=C["surface"], height=56)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)

        tk.Label(topbar, text=f"⬡ STRAVA VIEWER {APP_VERSION}",
                 font=("Courier", 13, "bold"), fg=C["accent"],
                 bg=C["surface"]).pack(side="left", padx=20, pady=14)

        # Status MongoDB (destra)
        self._mongo_status_var = tk.StringVar(value="MongoDB: …")
        self._mongo_status_lbl = tk.Label(
            topbar, textvariable=self._mongo_status_var,
            font=("Courier", 8), fg=C["text_dim"], bg=C["surface"],
            cursor="hand2")
        self._mongo_status_lbl.pack(side="right", padx=20)
        self._mongo_status_lbl.bind("<Button-1>", lambda e: self._toggle_mongo())

        # Bottoni destra → sinistra
        topbar_btn(topbar, "📂  APRI FILE",
                   self._open_file).pack(side="right", padx=4, pady=10)
        topbar_btn(topbar, "⬇  SCARICA DA STRAVA",
                   self._open_downloader, primary=True).pack(side="right", padx=4, pady=10)
        topbar_btn(topbar, "💾  ESPORTA",
                   self._export_menu).pack(side="right", padx=4, pady=10)
        topbar_btn(topbar, "📦  DATABASE",
                   self._database_menu).pack(side="right", padx=4, pady=10)

        # Toggle tema
        theme_lbl = "🌙  SCURO" if _cfg._current_theme[0] == "light" else "☀  CHIARO"
        topbar_btn(topbar, theme_lbl,
                   self._toggle_theme).pack(side="right", padx=4, pady=10)

        # Notebook
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Dark.TNotebook", background=C["bg"], borderwidth=0)
        style.configure("Dark.TNotebook.Tab", background=C["surface2"],
                        foreground=C["text_dim"],
                        font=("Courier", 9, "bold"), padding=[12, 7])
        style.map("Dark.TNotebook.Tab",
                  background=[("selected", C["bg"])],
                  foreground=[("selected", C["accent"])])

        self.nb = ttk.Notebook(self, style="Dark.TNotebook")
        self.nb.pack(fill="both", expand=True)

        tab_defs = [
            ("tab_dash",    "  DASHBOARD  "),
            ("tab_chart",   "  GRAFICI  "),
            ("tab_hrzone",  "  ZONE HR  "),
            ("tab_map",     "  MAPPA  "),
            ("tab_split",   "  SPLITS  "),
            ("tab_best",    "  BEST EFFORTS  "),
            ("tab_compare", "  CONFRONTO  "),
            ("tab_library", "  📚 LIBRERIA  "),
            ("tab_stats",   "  📊 STATISTICHE  "),
            ("tab_raw",     "  JSON  "),
        ]
        for attr, label in tab_defs:
            frame = tk.Frame(self.nb, bg=C["bg"])
            setattr(self, attr, frame)
            self.nb.add(frame, text=label)

        self.nb.bind("<<NotebookTabChanged>>", self._on_tab_changed)

    def _on_tab_changed(self, event):
        tab = self.nb.tab(self.nb.select(), "text").strip()
        if "LIBRERIA" in tab:
            self._render_library()
        elif "STATISTICHE" in tab:
            tab_stats.render(self.tab_stats, self.storage)

    # ── Welcome ───────────────────────────────────────────────────────────────

    def _show_welcome(self):
        for attr in ("tab_dash","tab_chart","tab_hrzone","tab_map",
                     "tab_split","tab_best","tab_compare","tab_raw"):
            clear(getattr(self, attr))
        tk.Label(self.tab_dash,
                 text="⬡\n\nBenvenuto in Strava Viewer 3.0\n\n"
                      "• Apri un file JSON con «APRI FILE»\n"
                      "• Scarica le corse direttamente da Strava con «SCARICA DA STRAVA»\n"
                      "• Sfoglia la libreria nel tab «LIBRERIA»",
                 font=("Courier", 12), fg=C["text_dim"], bg=C["bg"],
                 justify="center").pack(expand=True)
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
        act = self.activity
        cmp = list(self.cmp_list)
        for w in self.winfo_children():
            w.destroy()
        self.configure(bg=C["bg"])
        self._build_ui()
        self.cmp_list = cmp
        if act:
            self._load_activity(act)
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
        self.nb.select(self.tab_dash)

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
        self.nb.select(self.tab_compare)

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
        if not self.activity:
            messagebox.showinfo("Info", "Apri prima un'attività da analizzare.")
            return
        win = tk.Toplevel(self)
        win.title("Esporta attività")
        win.configure(bg=C["bg"])
        win.geometry("340x250")
        win.resizable(False, False)
        tk.Label(win, text="SCEGLI FORMATO",
                 font=("Courier", 10, "bold"), fg=C["accent"],
                 bg=C["bg"]).pack(pady=(20, 12))
        b = dict(font=("Courier", 10, "bold"), bd=0, pady=10,
                 cursor="hand2", relief="flat", width=28)
        tk.Button(win, text="📊  PNG — Grafici",  bg=C["surface2"], fg=C["text"],
                  command=lambda: [win.destroy(), self._export_png()], **b).pack(pady=4)
        tk.Button(win, text="📄  PDF — Report",   bg=C["surface2"], fg=C["text"],
                  command=lambda: [win.destroy(), self._export_pdf()], **b).pack(pady=4)
        tk.Button(win, text="📋  CSV — Splits",   bg=C["surface2"], fg=C["text"],
                  command=lambda: [win.destroy(), self._export_csv()], **b).pack(pady=4)
        tk.Button(win, text="✕  Annulla",         bg=C["bg"],       fg=C["text_dim"],
                  command=win.destroy, **b).pack(pady=(8, 0))

    # ── Database backup/restore ────────────────────────────────────────────────

    def _database_menu(self):
        win = tk.Toplevel(self)
        win.title("Database")
        win.configure(bg=C["bg"])
        win.geometry("340x220")
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
