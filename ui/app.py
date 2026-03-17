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
from i18n import t, set_language, get_language, SUPPORTED_LANGUAGES

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
from ui.widgets          import topbar_btn, clear, Tooltip

# Tab definition: (attribute, icon, i18n_key, group)
_TAB_DEFS = [
    ("tab_dash",     "⬡",  "tab_dashboard", "activity"),
    ("tab_chart",    "▤",  "tab_charts",    "activity"),
    ("tab_hrzone",   "♥",  "tab_hr",        "activity"),
    ("tab_map",      "◈",  "tab_map",       "activity"),
    ("tab_split",    "≡",  "tab_splits",    "activity"),
    ("tab_best",     "★",  "tab_best",      "activity"),
    ("tab_compare",  "⇄",  "tab_compare",   "activity"),
    ("tab_raw",      "{ }","tab_raw",       "activity"),
    ("tab_library",  "▣",  "tab_library",   "global"),
    ("tab_calendar", "▦",  "tab_calendar",  "global"),
    ("tab_stats",    "≈",  "tab_stats",     "global"),
]


class StravaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        # Load language from settings before building UI
        try:
            with open("settings.json", encoding="utf-8") as _f:
                _s = json.load(_f)
            set_language(_s.get("language", "it"))
        except Exception:
            set_language("it")

        self.title(f"{APP_NAME}  v{APP_VERSION}")
        self.configure(bg=C["bg"])
        self.geometry("1500x940")
        self.minsize(1200, 720)

        self.activity   = None        # main activity being analyzed
        self.cmp_list   = []          # ActivityData list for compare (max 4 extra)
        self.storage    = StorageManager()

        self._apply_scrollbar_style()
        self._build_ui()
        self._show_welcome()
        self._try_connect_mongo()

    # ── Scrollbar style ───────────────────────────────────────────────────────

    def _apply_scrollbar_style(self):
        """Override the default ttk scrollbar to match the app's color theme.

        Applied once at startup; affects all ttk Scrollbar instances globally.
        Re-called after theme toggles so the colors stay in sync.
        """
        style = ttk.Style(self)
        style.theme_use("default")
        style.configure(
            "Vertical.TScrollbar",
            background=C["surface2"],
            troughcolor=C["bg"],
            bordercolor=C["bg"],
            arrowcolor=C["border"],
            relief="flat",
            arrowsize=12,
        )
        style.configure(
            "Horizontal.TScrollbar",
            background=C["surface2"],
            troughcolor=C["bg"],
            bordercolor=C["bg"],
            arrowcolor=C["border"],
            relief="flat",
            arrowsize=12,
        )
        # Hover state: slightly lighter thumb
        style.map("Vertical.TScrollbar",
                  background=[("active", C["border"])])
        style.map("Horizontal.TScrollbar",
                  background=[("active", C["border"])])

    # ── MongoDB connection (background) ──────────────────────────────────────

    def _try_connect_mongo(self):
        import threading
        def _connect():
            ok, msg = self.storage.connect_mongo(auto_start=True)
            self.after(0, lambda: self._on_mongo_result(ok, msg))
        threading.Thread(target=_connect, daemon=True).start()
        self._mongo_status_var.set(t("mongo_connecting"))

    def _on_mongo_result(self, ok, msg):
        if ok:
            self._mongo_status_var.set(t("mongo_online"))
            self._mongo_status_lbl.config(fg=C["green"])
        else:
            self._mongo_status_var.set(t("mongo_offline"))
            self._mongo_status_lbl.config(fg=C["text_dim"])

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build_ui(self):
        self._tab_frames   = {}   # attr → tk.Frame (content)
        self._tab_buttons  = {}   # attr → (container, strip, icon_lbl, text_lbl)
        self._active_tab   = None

        # ── Topbar ────────────────────────────────────────────────────────────
        topbar = tk.Frame(self, bg=C["surface"], height=52)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)

        tk.Label(topbar, text=f"⬡  STRAVA VIEWER",
                 font=("Segoe UI", 12, "bold"), fg=C["accent"],
                 bg=C["surface"]).pack(side="left", padx=20, pady=14)

        # Status MongoDB (right)
        self._mongo_status_var = tk.StringVar(value="MongoDB: …")
        self._mongo_status_lbl = tk.Label(
            topbar, textvariable=self._mongo_status_var,
            font=("Segoe UI", 8), fg=C["text_dim"], bg=C["surface"],
            cursor="hand2")
        self._mongo_status_lbl.pack(side="right", padx=16)
        self._mongo_status_lbl.bind("<Button-1>", lambda e: self._toggle_mongo())

        # Vertical separator
        tk.Frame(topbar, bg=C["border"], width=1).pack(
            side="right", fill="y", pady=12)

        # Language selector
        lang_frame = tk.Frame(topbar, bg=C["surface"])
        lang_frame.pack(side="right", padx=6, pady=10)
        tk.Label(lang_frame, text=t("language_label"),
                 font=("Segoe UI", 8), fg=C["text_dim"],
                 bg=C["surface"]).pack(side="left")
        lang_options = list(SUPPORTED_LANGUAGES.values())
        lang_keys    = list(SUPPORTED_LANGUAGES.keys())
        cur_idx      = lang_keys.index(get_language()) if get_language() in lang_keys else 0
        self._lang_var = tk.StringVar(value=lang_options[cur_idx])
        lang_menu = ttk.Combobox(lang_frame, textvariable=self._lang_var,
                                  values=lang_options, state="readonly", width=14,
                                  font=("Segoe UI", 8))
        lang_menu.pack(side="left", padx=(4, 0))
        lang_menu.bind("<<ComboboxSelected>>", self._on_language_change)

        # Separator
        tk.Frame(topbar, bg=C["border"], width=1).pack(
            side="right", fill="y", pady=12)

        # Buttons right → left
        topbar_btn(topbar, t("btn_download"),
                   self._open_downloader, primary=True,
                   tooltip=t("tooltip_download")
                   ).pack(side="right", padx=4, pady=10)
        topbar_btn(topbar, t("btn_export"),
                   self._export_menu,
                   tooltip=t("tooltip_export")
                   ).pack(side="right", padx=4, pady=10)
        topbar_btn(topbar, t("btn_database"),
                   self._database_menu,
                   tooltip=t("tooltip_database")
                   ).pack(side="right", padx=4, pady=10)

        # Toggle theme
        theme_lbl = t("btn_theme_dark") if _cfg._current_theme[0] == "light" else t("btn_theme_light")
        topbar_btn(topbar, theme_lbl,
                   self._toggle_theme,
                   tooltip=t("tooltip_theme")
                   ).pack(side="right", padx=4, pady=10)

        # ── Separator topbar / body ──────────────────────────────────────────
        tk.Frame(self, bg=C["border"], height=1).pack(fill="x")

        # ── Body: sidebar + content ───────────────────────────────────────────
        body = tk.Frame(self, bg=C["bg"])
        body.pack(fill="both", expand=True)

        # ── Sidebar ───────────────────────────────────────────────────────────
        sidebar = tk.Frame(body, bg=C["surface"], width=180)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # ── Donation button (packed bottom-first so it stays at the bottom) ──
        self._build_donate_widget(sidebar)

        # Logo sidebar
        tk.Label(sidebar, text="⬡", font=("Courier", 20, "bold"),
                 fg=C["accent"], bg=C["surface"]).pack(pady=(18, 2))
        tk.Label(sidebar, text=f"v{APP_VERSION}",
                 font=("Segoe UI", 7), fg=C["text_dim"],
                 bg=C["surface"]).pack()
        tk.Frame(sidebar, bg=C["border"], height=1).pack(
            fill="x", padx=16, pady=(10, 6))

        # Groups tab
        def _section(text):
            tk.Label(sidebar, text=text.upper(),
                     font=("Segoe UI", 7, "bold"), fg=C["text_dim"],
                     bg=C["surface"]).pack(anchor="w", padx=16, pady=(8, 2))

        _section(t("sidebar_analysis"))
        activity_tabs = [td for td in _TAB_DEFS if td[3] == "activity"]
        global_tabs   = [td for td in _TAB_DEFS if td[3] == "global"]

        for attr, icon, label_key, _ in activity_tabs:
            self._make_nav_item(sidebar, attr, icon, t(label_key))

        tk.Frame(sidebar, bg=C["border"], height=1).pack(
            fill="x", padx=16, pady=(8, 4))
        _section(t("sidebar_database"))
        for attr, icon, label_key, _ in global_tabs:
            self._make_nav_item(sidebar, attr, icon, t(label_key))

        # Separator sidebar / content
        tk.Frame(body, bg=C["border"], width=1).pack(side="left", fill="y")

        # ── Content area ────────────────────────────────────────────────────
        content = tk.Frame(body, bg=C["bg"])
        content.pack(side="left", fill="both", expand=True)
        self._content = content

        # Create all frames of tab in content area
        for attr, icon, label, _ in _TAB_DEFS:
            frame = tk.Frame(content, bg=C["bg"])
            setattr(self, attr, frame)
            self._tab_frames[attr] = frame

        # Show the first tab
        self._show_tab("tab_dash")

    def _make_nav_item(self, parent, attr, icon, label):
        """Create a navigation item in the sidebar and save the links."""
        container = tk.Frame(parent, bg=C["surface"], cursor="hand2")
        container.pack(fill="x", pady=1)

        # Left color strip (active indicator)
        strip = tk.Frame(container, bg=C["surface"], width=3)
        strip.pack(side="left", fill="y")

        icon_lbl = tk.Label(container, text=icon, font=("Courier", 11),
                            bg=C["surface"], fg=C["text_dim"], width=3)
        icon_lbl.pack(side="left", padx=(8, 4), pady=8)

        text_lbl = tk.Label(container, text=label, font=("Segoe UI", 9, "bold"),
                            bg=C["surface"], fg=C["text_dim"], anchor="w")
        text_lbl.pack(side="left", pady=8)

        # Click and hover
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

    def _build_donate_widget(self, sidebar):
        """Donation button pinned at the bottom of the sidebar."""
        import webbrowser
        _PAYPAL_URL = "https://paypal.me/TeoVr81"

        # Outer frame pinned to the bottom
        outer = tk.Frame(sidebar, bg=C["surface"])
        outer.pack(side="bottom", fill="x", pady=(0, 12))

        tk.Frame(outer, bg=C["border"], height=1).pack(fill="x", padx=12, pady=(0, 8))

        btn_frame = tk.Frame(outer, bg=C["surface2"], cursor="hand2")
        btn_frame.pack(fill="x", padx=10, pady=2)

        lbl_main = tk.Label(btn_frame, text=t("donate_label"),
                            font=("Segoe UI", 8, "bold"),
                            fg=C["accent"], bg=C["surface2"],
                            cursor="hand2")
        lbl_main.pack(pady=(6, 1))

        lbl_sub = tk.Label(btn_frame, text=t("donate_sub"),
                           font=("Segoe UI", 7),
                           fg=C["text_dim"], bg=C["surface2"],
                           cursor="hand2")
        lbl_sub.pack(pady=(0, 6))

        def _open(e=None):
            webbrowser.open(_PAYPAL_URL)

        def _enter(e=None):
            for w in (btn_frame, lbl_main, lbl_sub):
                w.config(bg=C["border"])

        def _leave(e=None):
            for w in (btn_frame, lbl_main, lbl_sub):
                w.config(bg=C["surface2"])

        for w in (btn_frame, lbl_main, lbl_sub):
            w.bind("<Button-1>", _open)
            w.bind("<Enter>",    _enter)
            w.bind("<Leave>",    _leave)
            Tooltip(w, t("tooltip_donate"))

    def _show_tab(self, attr):
        """Display the frame of the selected tab and refresh the sidebar."""
        # Deselect previous tab
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

        # Active new tab in the sidebar
        if attr in self._tab_buttons:
            container, strip, icon_lbl, text_lbl = self._tab_buttons[attr]
            container.config(bg=C["surface"])
            strip.config(bg=C["accent"])
            icon_lbl.config(fg=C["accent"], bg=C["surface"])
            text_lbl.config(fg=C["accent"], bg=C["surface"])

        # Show the frame
        if attr in self._tab_frames:
            self._tab_frames[attr].pack(fill="both", expand=True)

        # Render lazy for tabs that needs it
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
                 text=t("welcome_text"),
                 font=("Segoe UI", 12), fg=C["text_dim"], bg=C["bg"],
                 justify="center").pack(expand=True)
        self._show_tab("tab_dash")
        self._render_library()

    # ── Light/dark theme ─────────────────────────────────────────────────────

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
        self._apply_scrollbar_style()   # re-apply scrollbar colors for the new theme
        self._build_ui()
        self.cmp_list = cmp
        if act:
            self._load_activity(act)
            if prev_tab and prev_tab in self._tab_frames:
                self._show_tab(prev_tab)
        else:
            self._show_welcome()

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

    # ── Strava Downloader ─────────────────────────────────────────────────────

    def _open_downloader(self):
        open_download_window(self, self.storage,
                             on_done_cb=self._render_library)

    # ── Library ──────────────────────────────────────────────────────────────

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
            messagebox.showerror(t("msg_error"), t("msg_no_activity"))
            return
        self._load_activity(act)

    # ── Compare ─────────────────────────────────────────────────────────────

    def _compare_add(self, act: ActivityData):
        if len(self.cmp_list) >= MAX_COMPARE - 1:
            messagebox.showwarning(t("msg_limit"),
                                   t("msg_max_compare").format(n=MAX_COMPARE))
            return
        self.cmp_list.append(act)

    def _compare_clear(self):
        self.cmp_list.clear()

    def _run_compare(self):
        if not self.activity and not self.cmp_list:
            messagebox.showinfo(t("msg_info"), t("msg_select_activity"))
            return
        if self.activity:
            all_acts = [self.activity] + self.cmp_list
        else:
            all_acts = list(self.cmp_list)
        if len(all_acts) < 2:
            messagebox.showinfo(t("msg_info"), t("msg_add_two_for_compare"))
            return
        tab_compare.render(self.tab_compare, all_acts)
        self._show_tab("tab_compare")

    # ── MongoDB toggle ─────────────────────────────────────────────────────────

    def _toggle_mongo(self):
        if self.storage.mongo_ok:
            self.storage.disconnect_mongo()
            self._mongo_status_var.set(t("mongo_offline"))
            self._mongo_status_lbl.config(fg=C["text_dim"])
        else:
            self._mongo_status_var.set(t("mongo_connecting"))
            self._mongo_status_lbl.config(fg=C["text_dim"])
            import threading
            threading.Thread(target=self._try_connect_mongo, daemon=True).start()

    # ── Language change ────────────────────────────────────────────────────────

    def _on_language_change(self, event=None):
        lang_options = list(SUPPORTED_LANGUAGES.values())
        lang_keys    = list(SUPPORTED_LANGUAGES.keys())
        chosen = self._lang_var.get()
        if chosen in lang_options:
            lang_code = lang_keys[lang_options.index(chosen)]
            try:
                with open("settings.json", encoding="utf-8") as f:
                    s = json.load(f)
            except Exception:
                s = {}
            s["language"] = lang_code
            try:
                with open("settings.json", "w", encoding="utf-8") as f:
                    json.dump(s, f, indent=2)
            except Exception:
                pass
            messagebox.showinfo(t("msg_language_changed"), t("msg_language_restart"))

    # ── Export current activity ────────────────────────────────────────────────

    def _export_menu(self):
        win = tk.Toplevel(self)
        win.title(t("btn_export").strip())
        win.configure(bg=C["bg"])
        win.geometry("340x370")
        win.resizable(False, False)
        tk.Label(win, text=t("export_choose_format"),
                 font=("Segoe UI", 10, "bold"), fg=C["accent"],
                 bg=C["bg"]).pack(pady=(20, 4))
        tk.Label(win, text=t("export_current"),
                 font=("Segoe UI", 8), fg=C["text_dim"],
                 bg=C["bg"]).pack(pady=(0, 8))
        b = dict(font=("Segoe UI", 10, "bold"), bd=0, pady=10,
                 cursor="hand2", relief="flat", width=28)
        act_cmds = [
            (t("export_png"),        self._export_png),
            (t("export_pdf"),        self._export_pdf),
            (t("export_csv_splits"), self._export_csv),
            (t("export_gpx"),        self._export_gpx),
        ]
        for txt, cmd in act_cmds:
            tk.Button(win, text=txt, bg=C["surface2"], fg=C["text"],
                      command=lambda c=cmd: [win.destroy(),
                                             c() if self.activity else
                                             messagebox.showinfo(
                                                 t("msg_info"),
                                                 t("msg_open_activity_first"))],
                      **b).pack(pady=3)

        tk.Label(win, text=t("export_database"),
                 font=("Segoe UI", 8), fg=C["text_dim"],
                 bg=C["bg"]).pack(pady=(10, 4))
        tk.Button(win, text=t("export_csv_stats"),
                  bg=C["surface2"], fg=C["text"],
                  command=lambda: [win.destroy(), self._export_stats_csv()],
                  **b).pack(pady=3)
        tk.Button(win, text=t("btn_cancel"), bg=C["bg"], fg=C["text_dim"],
                  command=win.destroy, **b).pack(pady=(8, 0))

    # ── Database backup/restore ────────────────────────────────────────────────

    def _database_menu(self):
        win = tk.Toplevel(self)
        win.title(t("btn_database").strip())
        win.configure(bg=C["bg"])
        win.geometry("340x280")
        win.resizable(False, False)
        tk.Label(win, text=t("db_manage"),
                 font=("Segoe UI", 10, "bold"), fg=C["accent"],
                 bg=C["bg"]).pack(pady=(20, 12))
        b = dict(font=("Segoe UI", 10, "bold"), bd=0, pady=10,
                 cursor="hand2", relief="flat", width=28)
        tk.Button(win, text=t("db_export_zip"),  bg=C["surface2"], fg=C["text"],
                  command=lambda: [win.destroy(), self._export_zip()], **b).pack(pady=4)
        tk.Button(win, text=t("db_import_zip"),  bg=C["surface2"], fg=C["text"],
                  command=lambda: [win.destroy(), self._import_zip()], **b).pack(pady=4)
        tk.Button(win, text=t("db_heatmap"),     bg=C["surface2"], fg=C["text"],
                  command=lambda: [win.destroy(), self._open_heatmap()], **b).pack(pady=4)
        tk.Button(win, text=t("btn_cancel"),     bg=C["bg"],       fg=C["text_dim"],
                  command=win.destroy, **b).pack(pady=(8, 0))

    def _export_zip(self):
        import zipfile, re as _re
        if not (self.storage.mongo_ok and self.storage.mongo_storage):
            messagebox.showerror(t("msg_error"), t("mongo_offline"))
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".zip",
            initialfile="strava_backup.zip",
            filetypes=[("ZIP", "*.zip")])
        if not path:
            return
        try:
            count = 0
            with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
                cursor = self.storage.mongo_storage._coll.find({})
                for doc in cursor:
                    doc.pop("_id", None)
                    act_id   = doc.get("id", "unknown")
                    date_str = (doc.get("start_date_local", "")[:10]) or "nodate"
                    raw_name = doc.get("name", "activity")[:40]
                    safe_name = _re.sub(r'[<>:"/\\|?*\x00-\x1f]', '-', raw_name).strip()
                    fname = f"{date_str}_{act_id}_{safe_name}.json"
                    zf.writestr(fname, json.dumps(doc, ensure_ascii=False, indent=2))
                    count += 1
            messagebox.showinfo("Export ZIP",
                                f"{t('msg_backup_done')}\n{count} {t('msg_runs_exported')}\n{path}")
        except Exception as e:
            messagebox.showerror(t("msg_export_error"), str(e))

    def _import_zip(self):
        import zipfile
        if not (self.storage.mongo_ok and self.storage.mongo_storage):
            messagebox.showerror(t("msg_error"), t("mongo_offline"))
            return
        path = filedialog.askopenfilename(
            title=t("msg_select_backup"),
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
                        self.storage.mongo_storage.save(data)
                        new_count += 1
                    except Exception:
                        err_count += 1
            messagebox.showinfo("Import ZIP",
                                f"{t('msg_import_done')}\n"
                                f"• {new_count} {t('msg_imported')}\n"
                                f"• {skip_count} {t('msg_already_present')}\n"
                                f"• {err_count} {t('msg_errors')}")
            self._render_library()
        except Exception as e:
            messagebox.showerror(t("msg_error"), str(e))

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
            messagebox.showinfo(t("msg_export_saved"), f"{t('msg_png_saved')}\n{path}")
        except Exception as e:
            messagebox.showerror(t("msg_export_error"), str(e))

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
                messagebox.showinfo(t("msg_export_saved"), f"{t('msg_pdf_saved')}\n{path}")
        except Exception as e:
            messagebox.showerror(t("msg_export_error"), str(e))

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
        messagebox.showinfo(t("msg_export_saved"), f"{t('msg_csv_saved')}\n{path}")

    # ── Export GPX ────────────────────────────────────────────────────────────

    def _export_gpx(self):
        if not self.activity:
            return
        a = self.activity
        if not a.gps_points:
            messagebox.showinfo("GPX", t("msg_no_gps"))
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".gpx",
            initialfile=f"{a.name[:40].replace(' ', '_')}.gpx",
            filetypes=[("GPX", "*.gpx"), ("Tutti", "*.*")])
        if not path:
            return
        try:
            _write_gpx(a, path)
            messagebox.showinfo(t("msg_export_saved"), f"{t('msg_gpx_saved')}\n{path}")
        except Exception as e:
            messagebox.showerror(t("msg_gpx_error"), str(e))

    # ── Export CSV statistics ────────────────────────────────────────────────

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
            messagebox.showinfo(t("msg_export_saved"), f"{t('msg_stats_exported')}\n{path}")
        except Exception as e:
            messagebox.showerror(t("msg_csv_error"), str(e))

    # ── Heatmap ───────────────────────────────────────────────────────────────

    def _open_heatmap(self):
        import threading
        win = tk.Toplevel(self)
        win.title(t("heatmap_win_title"))
        win.configure(bg=C["bg"])
        win.geometry("320x120")
        lbl = tk.Label(win, text=t("msg_heatmap_loading"),
                       font=("Segoe UI", 10), fg=C["text_dim"],
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


# ── Helpers module ────────────────────────────────────────────────────────────

def _write_gpx(act, path: str):
    """Generates a GPX file from the activity's GPS track."""
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
    """It generates the Folium heatmap with all the polylines and opens it in the browser."""
    import tempfile, webbrowser
    progress_win.destroy()

    if not polys:
        from tkinter import messagebox
        messagebox.showinfo("Heatmap", t("msg_heatmap_no_gps"))
        return

    try:
        import folium
    except ImportError:
        from tkinter import messagebox
        messagebox.showerror("Heatmap", t("msg_folium_missing"))
        return

    # Map center = average of all points
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

    # Save temporary file and open it in the browser
    tmp = tempfile.NamedTemporaryFile(suffix=".html", delete=False)
    m.save(tmp.name)
    webbrowser.open(f"file:///{tmp.name.replace(chr(92), '/')}")
