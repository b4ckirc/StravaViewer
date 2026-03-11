# ── ui/tab_map.py ─────────────────────────────────────────────────────────────
"""
Tab mappa: genera HTML folium e lo apre nel browser di sistema.
Nessun widget embedded — zero interferenze con tkinter.
"""

import os, tempfile, tkinter as tk, webbrowser
from config import C
from models import fmt_dist, fmt_time
from ui.widgets import no_data, clear

try:
    import folium
    HAS_FOLIUM = True
except ImportError:
    HAS_FOLIUM = False


def render(tab, activity):
    clear(tab)

    # Contenuto statico: solo label e pulsante, nessun canvas/frame espandibile
    if not HAS_FOLIUM:
        tk.Label(tab,
                 text="⚠️  Installa folium per la mappa:\n  pip install folium",
                 font=("Courier", 11), fg=C["yellow"], bg=C["bg"],
                 justify="center").place(relx=0.5, rely=0.5, anchor="center")
        return

    if not activity or not activity.gps_points:
        tk.Label(tab,
                 text="⚠️  Nessun dato GPS disponibile.\n\n"
                      "La polyline richiede il permesso Strava «activity:read_all».",
                 font=("Courier", 11), fg=C["text_dim"], bg=C["bg"],
                 justify="center").place(relx=0.5, rely=0.5, anchor="center")
        return

    a = activity

    # Titolo
    tk.Label(tab,
             text=f"🗺  {a.name}",
             font=("Courier", 14, "bold"), fg=C["text"], bg=C["bg"]
             ).place(relx=0.5, rely=0.30, anchor="center")

    tk.Label(tab,
             text=(f"📏 {fmt_dist(a.distance)}    "
                   f"⏱ {fmt_time(a.moving_time)}    "
                   f"👟 {a.avg_pace_str} /km    "
                   f"⛰ +{a.elev_gain:.0f} m    "
                   f"📍 {len(a.gps_points)} punti GPS"),
             font=("Courier", 9), fg=C["text_dim"], bg=C["bg"]
             ).place(relx=0.5, rely=0.38, anchor="center")

    status_var = tk.StringVar(value="")
    status_lbl = tk.Label(tab, textvariable=status_var,
                          font=("Courier", 9), fg=C["text_dim"], bg=C["bg"],
                          justify="center")
    status_lbl.place(relx=0.5, rely=0.62, anchor="center")

    def _open_map():
        status_var.set("⏳ Generazione mappa…")
        tab.update_idletasks()
        try:
            pts    = a.gps_points
            center = pts[len(pts) // 2]
            m = folium.Map(location=center, zoom_start=14,
                           tiles="CartoDB dark_matter")
            folium.PolyLine(pts, color="#fc4c02", weight=4.5,
                            opacity=0.9, tooltip=a.name).add_to(m)
            folium.Marker(pts[0],
                          popup=f"🏁 Inizio — {a.date_str}",
                          icon=folium.Icon(color="green", icon="play")).add_to(m)
            folium.Marker(pts[-1],
                          popup=f"🏁 Fine — {fmt_dist(a.distance)}",
                          icon=folium.Icon(color="red",   icon="stop")).add_to(m)

            tmp = tempfile.NamedTemporaryFile(
                suffix=".html", prefix="strava_map_", delete=False)
            map_path = tmp.name
            tmp.close()
            m.save(map_path)

            webbrowser.open(f"file:///{map_path.replace(os.sep, '/')}")
            status_var.set(f"✅ Mappa aperta nel browser.")
            btn.config(text="🗺  Riapri nel browser")
        except Exception as e:
            status_var.set(f"❌ Errore: {e}")

    btn = tk.Button(
        tab,
        text="🗺  Apri mappa nel browser",
        font=("Courier", 12, "bold"),
        bg=C["accent"], fg="white",
        activebackground="#d43d00", activeforeground="white",
        bd=0, padx=28, pady=14,
        cursor="hand2", relief="flat",
        command=_open_map,
    )
    btn.place(relx=0.5, rely=0.50, anchor="center")

    tk.Label(tab,
             text="La mappa viene aperta nel browser predefinito",
             font=("Courier", 8), fg=C["text_dim"], bg=C["bg"]
             ).place(relx=0.5, rely=0.70, anchor="center")
