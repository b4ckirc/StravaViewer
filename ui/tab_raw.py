# ── ui/tab_raw.py ─────────────────────────────────────────────────────────────
import json, tkinter as tk
from tkinter import ttk
from config import C
from ui.widgets import clear


def render(tab, activity):
    clear(tab)
    tk.Label(tab, text="JSON GREZZO DELL'ATTIVITÀ",
             font=("Courier", 10, "bold"), fg=C["accent"],
             bg=C["surface"], pady=11).pack(fill="x")

    frame = tk.Frame(tab, bg=C["bg"])
    frame.pack(fill="both", expand=True, padx=14, pady=(10, 0))

    txt  = tk.Text(frame, bg=C["surface"], fg=C["text"],
                   font=("Courier", 9), bd=0, relief="flat",
                   insertbackground=C["text"], wrap="none", undo=False)
    sb_v = ttk.Scrollbar(frame, orient="vertical",   command=txt.yview)
    sb_h = ttk.Scrollbar(tab,   orient="horizontal", command=txt.xview)
    txt.configure(yscrollcommand=sb_v.set, xscrollcommand=sb_h.set)
    sb_v.pack(side="right", fill="y")
    txt.pack(side="left", fill="both", expand=True)
    sb_h.pack(fill="x", padx=14, pady=(0, 8))

    raw = json.dumps(activity.raw, indent=2, ensure_ascii=False)

    def _insert():
        txt.config(state="normal")
        txt.delete("1.0", "end")
        txt.insert("1.0", raw)
        txt.config(state="disabled")

    # Ritarda l'inserimento fino a dopo il primo render del widget
    tab.after(100, _insert)
