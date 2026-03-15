# ── ui/downloader_ui.py ───────────────────────────────────────────────────────
import base64
import hashlib
import os
import socket
import threading
import tkinter as tk
import webbrowser
from tkinter import ttk, messagebox
from config import C, MONGO_DB
from i18n import t

_STRAVA_API_URL  = "https://www.strava.com/settings/api"
_CREDS_DOC_ID    = "strava_credentials"
_CONFIG_COLL     = "app_config"

# ── Cifratura ─────────────────────────────────────────────────────────────────

def _fernet_key() -> bytes:
    """Chiave Fernet derivata deterministicamente dall'identità della macchina."""
    try:
        user = os.getlogin()
    except Exception:
        user = os.environ.get("USERNAME", os.environ.get("USER", "user"))
    raw = f"{socket.gethostname()}:{user}:strava_viewer_v1"
    digest = hashlib.sha256(raw.encode()).digest()
    return base64.urlsafe_b64encode(digest)


def _encrypt(plaintext: str) -> str:
    try:
        from cryptography.fernet import Fernet
        return Fernet(_fernet_key()).encrypt(plaintext.encode()).decode()
    except ImportError:
        return plaintext          # fallback: testo in chiaro se lib non installata


def _decrypt(ciphertext: str) -> str:
    try:
        from cryptography.fernet import Fernet
        return Fernet(_fernet_key()).decrypt(ciphertext.encode()).decode()
    except (ImportError, Exception):
        return ciphertext         # fallback: restituisce così com'è

# ── Persistenza credenziali ───────────────────────────────────────────────────

def _load_creds(storage_mgr) -> tuple[str, str]:
    if storage_mgr.mongo_ok and storage_mgr.mongo_storage:
        try:
            coll = storage_mgr.mongo_storage._client[MONGO_DB][_CONFIG_COLL]
            doc  = coll.find_one({"_id": _CREDS_DOC_ID})
            if doc:
                return doc.get("client_id", ""), _decrypt(doc.get("client_secret", ""))
        except Exception:
            pass
    return "", ""


def _save_creds(storage_mgr, client_id: str, client_secret: str):
    if storage_mgr.mongo_ok and storage_mgr.mongo_storage:
        try:
            coll = storage_mgr.mongo_storage._client[MONGO_DB][_CONFIG_COLL]
            coll.update_one(
                {"_id": _CREDS_DOC_ID},
                {"$set": {"client_id": client_id, "client_secret": _encrypt(client_secret)}},
                upsert=True,
            )
        except Exception:
            pass


def open_download_window(parent, storage_mgr, on_done_cb=None):
    win = tk.Toplevel(parent)
    win.title(t("downloader_win_title"))
    win.configure(bg=C["bg"])
    win.geometry("700x620")
    win.resizable(True, True)
    win.grab_set()
    win.lift()
    win.focus_force()

    # ── Header ────────────────────────────────────────────────────────────────
    tk.Label(win, text=t("downloader_title"),
             font=("Courier", 13, "bold"), fg=C["accent"],
             bg=C["surface"], pady=14).pack(fill="x")

    # ── Credenziali ───────────────────────────────────────────────────────────
    cred_f = tk.Frame(win, bg=C["bg"], pady=8)
    cred_f.pack(fill="x", padx=24)

    hint_f = tk.Frame(cred_f, bg=C["bg"])
    hint_f.pack(anchor="w", pady=(0, 6))
    hint_lines = t("downloader_creds_hint").split("\n")
    tk.Label(hint_f, text=hint_lines[0], font=("Courier", 8),
             fg=C["text_dim"], bg=C["bg"], justify="left").pack(anchor="w")
    if len(hint_lines) > 1:
        row2 = tk.Frame(hint_f, bg=C["bg"])
        row2.pack(anchor="w")
        url_pos = hint_lines[1].find(_STRAVA_API_URL)
        if url_pos >= 0:
            prefix = hint_lines[1][:url_pos]
            if prefix:
                tk.Label(row2, text=prefix, font=("Courier", 8),
                         fg=C["text_dim"], bg=C["bg"]).pack(side="left")
            lnk = tk.Label(row2, text=_STRAVA_API_URL,
                           font=("Courier", 8, "underline"),
                           fg=C["accent"], bg=C["bg"], cursor="hand2")
            lnk.pack(side="left")
            lnk.bind("<Button-1>", lambda e: webbrowser.open(_STRAVA_API_URL))
            suffix = hint_lines[1][url_pos + len(_STRAVA_API_URL):]
            if suffix:
                tk.Label(row2, text=suffix, font=("Courier", 8),
                         fg=C["text_dim"], bg=C["bg"]).pack(side="left")
        else:
            tk.Label(row2, text=hint_lines[1], font=("Courier", 8),
                     fg=C["text_dim"], bg=C["bg"]).pack(anchor="w")

    def entry_row(lbl_text, show=""):
        f = tk.Frame(cred_f, bg=C["bg"])
        f.pack(fill="x", pady=3)
        tk.Label(f, text=lbl_text, font=("Courier", 9),
                 fg=C["text_dim"], bg=C["bg"], width=16,
                 anchor="w").pack(side="left")
        var = tk.StringVar()
        tk.Entry(f, textvariable=var, font=("Courier", 10),
                 bg=C["surface2"], fg=C["text"], show=show, width=36,
                 bd=0, insertbackground=C["text"],
                 highlightthickness=1, highlightbackground=C["border"]
                 ).pack(side="left", padx=8)
        return var

    cid_var = entry_row("Client ID:")
    csc_var = entry_row("Client Secret:", show="*")

    _saved_cid, _saved_csc = _load_creds(storage_mgr)
    if _saved_cid:
        cid_var.set(_saved_cid)
    if _saved_csc:
        csc_var.set(_saved_csc)

    # ── Destinazione ──────────────────────────────────────────────────────────
    dst_f = tk.Frame(win, bg=C["surface2"],
                     highlightthickness=1, highlightbackground=C["border"])
    dst_f.pack(fill="x", padx=24, pady=(4, 0))
    tk.Label(dst_f, text=t("downloader_save_in"), font=("Courier", 8, "bold"),
             fg=C["text_dim"], bg=C["surface2"], pady=8).pack(side="left", padx=12)
    save_json_var  = tk.BooleanVar(value=True)
    save_mongo_var = tk.BooleanVar(value=storage_mgr.mongo_ok)
    tk.Checkbutton(dst_f, text="File JSON", variable=save_json_var,
                   font=("Courier", 9), fg=C["text"], bg=C["surface2"],
                   selectcolor=C["surface"], activebackground=C["surface2"],
                   activeforeground=C["text"]).pack(side="left", padx=10)
    mongo_cb = tk.Checkbutton(dst_f, text="MongoDB", variable=save_mongo_var,
                              font=("Courier", 9), fg=C["text"], bg=C["surface2"],
                              selectcolor=C["surface"], activebackground=C["surface2"],
                              activeforeground=C["text"])
    mongo_cb.pack(side="left", padx=10)
    if not storage_mgr.mongo_ok:
        mongo_cb.config(state="disabled")
        tk.Label(dst_f, text=t("downloader_mongo_off"), font=("Courier", 7),
                 fg=C["red"], bg=C["surface2"]).pack(side="left")

    # ── Contatori ─────────────────────────────────────────────────────────────
    stat_f = tk.Frame(win, bg=C["surface2"])
    stat_f.pack(fill="x", padx=24, pady=(6, 0))
    new_var  = tk.StringVar(value=t("downloader_new").format(n=0))
    skip_var = tk.StringVar(value=t("downloader_skip").format(n=0))
    err_var  = tk.StringVar(value=t("downloader_errors").format(n=0))
    for var, col in [(new_var, C["green"]), (skip_var, C["text_dim"]), (err_var, C["red"])]:
        tk.Label(stat_f, textvariable=var, font=("Courier", 9, "bold"),
                 fg=col, bg=C["surface2"], padx=16, pady=5).pack(side="left")

    # ── Pulsanti ──────────────────────────────────────────────────────────────
    # IMPORTANTE: pack PRIMA del log (expand=True), altrimenti viene schiacciato
    btn_f = tk.Frame(win, bg=C["bg"], pady=10)
    btn_f.pack(fill="x", padx=24)

    def log(msg: str):
        try:
            log_txt.config(state="normal")
            log_txt.insert("end", msg + "\n")
            log_txt.see("end")
            log_txt.config(state="disabled")
        except Exception:
            pass

    def _run():
        log("🟠 Avvio richiesto…")
        win.update_idletasks()

        cid = cid_var.get().strip()
        csc = csc_var.get().strip()
        if not cid:
            messagebox.showerror(t("msg_error"), t("downloader_err_no_cid"), parent=win)
            return
        if not csc:
            messagebox.showerror(t("msg_error"), t("downloader_err_no_csc"), parent=win)
            return
        if not save_json_var.get() and not save_mongo_var.get():
            messagebox.showerror(t("msg_error"), t("downloader_err_no_dst"), parent=win)
            return

        _save_creds(storage_mgr, cid, csc)

        start_btn.config(state="disabled", text=t("btn_downloading"))
        pbar.start(10)
        log("🔵 Thread worker avviato.")

        counters = {"new": 0, "skip": 0, "err": 0}

        def upd():
            new_var.set(t("downloader_new").format(n=counters['new']))
            skip_var.set(t("downloader_skip").format(n=counters['skip']))
            err_var.set(t("downloader_errors").format(n=counters['err']))

        def worker():
            try:
                from downloader import get_access_token, fetch_activity_list, fetch_activity_detail

                win.after(0, log, "🔑 Avvio autenticazione OAuth…")
                win.after(0, log, "   Il browser si aprirà a breve.")
                token = get_access_token(cid, csc,
                                         progress_cb=lambda m: win.after(0, log, m))

                win.after(0, log, "📋 Recupero lista corse da Strava…")
                runs = fetch_activity_list(token,
                                           progress_cb=lambda m: win.after(0, log, m))
                win.after(0, log, f"✅ {len(runs)} corse trovate su Strava.")

                for i, run in enumerate(runs, 1):
                    sid = run.get("id")
                    if storage_mgr.exists(sid):
                        counters["skip"] += 1
                        win.after(0, upd)
                        continue
                    win.after(0, log, f"⬇  [{i}/{len(runs)}] {run.get('name', '–')}")
                    try:
                        detail = fetch_activity_detail(sid, token)
                        if save_json_var.get():
                            storage_mgr.json_storage.save(detail)
                        if save_mongo_var.get() and storage_mgr.mongo_ok:
                            storage_mgr.mongo_storage.save(detail)
                        counters["new"] += 1
                    except Exception as e:
                        win.after(0, log, f"   ⚠ Errore: {e}")
                        counters["err"] += 1
                    win.after(0, upd)

                win.after(0, log,
                          f"\n🏁 Completato: {counters['new']} nuove, "
                          f"{counters['skip']} già presenti, {counters['err']} errori.")
                if on_done_cb:
                    win.after(0, on_done_cb)

            except Exception as e:
                import traceback
                win.after(0, log, f"❌ Errore critico: {e}")
                win.after(0, log, traceback.format_exc())
            finally:
                win.after(0, pbar.stop)
                win.after(0, lambda: start_btn.config(
                    state="normal", text=t("btn_start_download")))

        threading.Thread(target=worker, daemon=True).start()

    start_btn = tk.Button(
        btn_f,
        text=t("btn_start_download"),
        font=("Courier", 11, "bold"),
        bg=C["accent"], fg="white",
        activebackground="#d43d00", activeforeground="white",
        bd=0, padx=20, pady=10,
        cursor="hand2", relief="flat",
        width=24,
        command=_run,
    )
    start_btn.pack(side="left")

    tk.Button(
        btn_f, text=t("btn_close"),
        font=("Courier", 9), bg=C["surface2"],
        fg=C["text"], bd=0, padx=12, pady=10,
        cursor="hand2", command=win.destroy,
    ).pack(side="left", padx=12)

    # ── Progressbar ───────────────────────────────────────────────────────────
    pbar = ttk.Progressbar(win, mode="indeterminate")
    pbar.pack(fill="x", padx=24, pady=(0, 4))

    # ── Log (expand=True per ultimo, prende lo spazio rimanente) ──────────────
    log_outer = tk.Frame(win, bg=C["bg"])
    log_outer.pack(fill="both", expand=True, padx=24, pady=(0, 8))

    log_txt = tk.Text(log_outer, bg=C["surface"], fg=C["text"],
                      font=("Courier", 9), bd=0, relief="flat",
                      state="disabled", wrap="word")
    log_sb = ttk.Scrollbar(log_outer, orient="vertical", command=log_txt.yview)
    log_txt.configure(yscrollcommand=log_sb.set)
    log_sb.pack(side="right", fill="y")
    log_txt.pack(fill="both", expand=True)

    log(t("downloader_ready"))
