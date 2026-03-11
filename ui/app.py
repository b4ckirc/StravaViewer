# ── ui/app.py ─────────────────────────────────────────────────────────────────
"""
Finestra principale dell'applicazione Strava Viewer v3.0.
"""

import json, tkinter as tk
from tkinter import ttk, filedialog, messagebox
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

        # Status MongoDB (destra, prima degli altri bottoni)
        self._mongo_status_var = tk.StringVar(value="MongoDB: …")
        self._mongo_status_lbl = tk.Label(
            topbar, textvariable=self._mongo_status_var,
            font=("Courier", 8), fg=C["text_dim"], bg=C["surface"],
            cursor="hand2")
        self._mongo_status_lbl.pack(side="right", padx=20)
        self._mongo_status_lbl.bind("<Button-1>", lambda e: self._toggle_mongo())

        topbar_btn(topbar, "📂  APRI FILE",
                   self._open_file).pack(side="right", padx=4, pady=10)
        topbar_btn(topbar, "⬇  SCARICA DA STRAVA",
                   self._open_downloader, primary=True).pack(side="right", padx=4, pady=10)
        topbar_btn(topbar, "💾  ESPORTA",
                   self._export_menu).pack(side="right", padx=4, pady=10)

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

        # Aggiorna libreria quando si clicca sulla tab
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
        # Se non c'è attività principale, usa la prima della lista
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

    # ── Export ────────────────────────────────────────────────────────────────

    def _export_menu(self):
        if not self.activity:
            messagebox.showinfo("Info", "Apri prima un'attività da analizzare.")
            return
        win = tk.Toplevel(self)
        win.title("Esporta")
        win.configure(bg=C["bg"])
        win.geometry("340x250")
        win.resizable(False, False)
        tk.Label(win, text="SCEGLI FORMATO",
                 font=("Courier", 10, "bold"), fg=C["accent"],
                 bg=C["bg"]).pack(pady=(20, 12))
        b = dict(font=("Courier", 10, "bold"), bd=0, pady=10,
                 cursor="hand2", relief="flat", width=28)
        tk.Button(win, text="📊  PNG — Grafici",     bg=C["surface2"], fg=C["text"],
                  command=lambda: [win.destroy(), self._export_png()], **b).pack(pady=4)
        tk.Button(win, text="📄  PDF — Report",      bg=C["surface2"], fg=C["text"],
                  command=lambda: [win.destroy(), self._export_pdf()], **b).pack(pady=4)
        tk.Button(win, text="📋  CSV — Splits",      bg=C["surface2"], fg=C["text"],
                  command=lambda: [win.destroy(), self._export_csv()], **b).pack(pady=4)
        tk.Button(win, text="✕  Annulla",            bg=C["bg"],       fg=C["text_dim"],
                  command=win.destroy, **b).pack(pady=(8, 0))

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
