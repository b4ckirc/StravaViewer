# ── ui/tab_map.py ─────────────────────────────────────────────────────────────
"""
Tab map: generates interactive Folium HTML and opens it in the browser.
Features:
A – Layer switcher: Dark / OpenStreetMap / Satellite (Esri) / Light
B – Track colored by pace per km (green=fast → red=slow)
C – Clickable kilometer markers with popup (pace, HR, elevation)
D – FullScreen button
E – MiniMap in the corner
F – Rich Start/End popup + overlay statistics at top of map
"""

import colorsys
import os
import tempfile
import tkinter as tk
import webbrowser

from config import C
from models import fmt_dist, fmt_time, fmt_pace, speed_to_pace, pace_label
from ui.widgets import clear
from i18n import t

try:
    import folium
    import folium.plugins
    HAS_FOLIUM = True
except ImportError:
    HAS_FOLIUM = False


# ── Helpers ────────────────────────────────────────────────────────────────────

def _val_to_color(t: float) -> str:
    """t: 0.0 (fast/excellent) → 1.0 (slow/poor) → green→yellow→red."""
    hue = (1.0 - max(0.0, min(1.0, t))) * 0.333
    r, g, b = colorsys.hls_to_rgb(hue, 0.45, 1.0)
    return f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"


def _distribute_pts(pts: list, splits: list) -> list[list]:
    """
    Distributes the GPS points among the splits proportionally to the distance.
    Returns a list of segments (each is a list of GPS points).
    The segments overlap by 1 point to eliminate visual gaps.
    """
    if not splits:
        return [pts]
    total_dist = sum(s.get("distance", 0) for s in splits)
    if total_dist <= 0:
        return [pts]
    n = len(pts)
    segments = []
    prev_idx = 0
    cumulative = 0.0
    for i, split in enumerate(splits):
        cumulative += split.get("distance", 0) / total_dist
        end_idx = n - 1 if i == len(splits) - 1 else min(round(cumulative * n), n - 1)
        seg = pts[prev_idx: end_idx + 1]
        if len(seg) >= 2:
            segments.append(seg)
        prev_idx = end_idx  # overlap of 1 point → no gap between segments
    return segments if segments else [pts]


def _gps_pos_at_dist(pts: list, target_m: float, total_dist: float):
    """Returns the GPS coordinate at the target_m distance along the route."""
    if target_m >= total_dist or total_dist <= 0:
        return None
    idx = min(round(target_m / total_dist * len(pts)), len(pts) - 1)
    return pts[idx]


# ── Render ─────────────────────────────────────────────────────────────────────

def render(tab, activity):
    clear(tab)

    if not HAS_FOLIUM:
        tk.Label(tab,
                 text=t("map_no_folium"),
                 font=("Courier", 11), fg=C["yellow"], bg=C["bg"],
                 justify="center").place(relx=0.5, rely=0.5, anchor="center")
        return

    if not activity or not activity.gps_points:
        tk.Label(tab,
                 text=t("map_no_gps"),
                 font=("Courier", 11), fg=C["text_dim"], bg=C["bg"],
                 justify="center").place(relx=0.5, rely=0.5, anchor="center")
        return

    a = activity

    tk.Label(tab,
             text=f"🗺  {a.name}",
             font=("Courier", 14, "bold"), fg=C["text"], bg=C["bg"]
             ).place(relx=0.5, rely=0.30, anchor="center")

    tk.Label(tab,
             text=(f"📏 {fmt_dist(a.distance)}    "
                   f"⏱ {fmt_time(a.moving_time)}    "
                   f"👟 {a.avg_pace_str} /km    "
                   f"⛰ +{a.elev_gain:.0f} m    "
                   f"📍 {len(a.gps_points)} {t('map_gps_points')}"),
             font=("Courier", 9), fg=C["text_dim"], bg=C["bg"]
             ).place(relx=0.5, rely=0.38, anchor="center")

    status_var = tk.StringVar(value="")
    tk.Label(tab, textvariable=status_var,
             font=("Courier", 9), fg=C["text_dim"], bg=C["bg"],
             justify="center").place(relx=0.5, rely=0.62, anchor="center")

    def _open_map():
        status_var.set(t("map_generating"))
        tab.update_idletasks()
        try:
            pts    = a.gps_points
            center = pts[len(pts) // 2]

            # ── Base map (tiles=None → adding layers manually) ─────
            m = folium.Map(location=center, zoom_start=14, tiles=None)

            # ── A: Layer switcher ─────────────────────────────────────────────
            folium.TileLayer(
                "CartoDB dark_matter",
                name="Dark (default)", overlay=False, control=True
            ).add_to(m)
            folium.TileLayer(
                "OpenStreetMap",
                name="OpenStreetMap", overlay=False, control=True
            ).add_to(m)
            folium.TileLayer(
                tiles=("https://server.arcgisonline.com/ArcGIS/rest/services/"
                       "World_Imagery/MapServer/tile/{z}/{y}/{x}"),
                attr="Esri &mdash; Source: Esri, Maxar, GeoEye, Earthstar Geographics",
                name="Satellite", overlay=False, control=True
            ).add_to(m)
            folium.TileLayer(
                "CartoDB positron",
                name=t("map_light_tile"), overlay=False, control=True
            ).add_to(m)

            # ── B: Colored track by pace ──────────────────────────────────────
            splits = a.splits or []
            if splits:
                paces = [speed_to_pace(s.get("average_speed", 0))
                         for s in splits if (s.get("average_speed") or 0) > 0]
                pace_min = min(paces) if len(paces) > 1 else None
                pace_max = max(paces) if len(paces) > 1 else None
                segments = _distribute_pts(pts, splits)

                for i, (seg, split) in enumerate(zip(segments, splits)):
                    spd   = split.get("average_speed") or 0
                    pace  = speed_to_pace(spd)
                    hr    = split.get("average_heartrate")
                    elev  = split.get("elevation_difference") or 0

                    if pace and pace_min and pace_max and pace_max > pace_min:
                        ratio = (pace - pace_min) / (pace_max - pace_min)
                    else:
                        ratio = 0.5
                    color = _val_to_color(ratio)

                    parts = [f"Km {i + 1}", f"{t('map_pace_km')} {pace_label(pace)} /km"]
                    if hr:
                        parts.append(f"{t('map_fc')} {hr:.0f} bpm")
                    if elev:
                        parts.append(f"{t('map_elevation_delta')} {elev:+.0f} m")
                    tooltip = "  •  ".join(parts)

                    if len(seg) >= 2:
                        folium.PolyLine(seg, color=color, weight=5.5,
                                        opacity=0.95, tooltip=tooltip).add_to(m)
            else:
                # Fallback: polyline single color Strava
                folium.PolyLine(pts, color="#fc4c02", weight=5.0,
                                opacity=0.9, tooltip=a.name).add_to(m)

            # ── C: Km Markers ─────────────────────────────────────────
            for i, split in enumerate(splits):
                km_num   = i + 1
                spd      = split.get("average_speed") or 0
                pace     = speed_to_pace(spd)
                hr       = split.get("average_heartrate")
                elev     = split.get("elevation_difference") or 0
                dist_m   = km_num * 1000
                pos      = _gps_pos_at_dist(pts, dist_m, a.distance)
                if pos is None:
                    continue

                rows = [f"<b>Km {km_num}</b>",
                        f"{t('map_pace_km')} <b>{pace_label(pace)} /km</b>"]
                if hr:
                    rows.append(f"{t('map_fc')} <b>{hr:.0f} bpm</b>")
                if elev:
                    rows.append(f"{t('stat_elev_gain')}: <b>{elev:+.0f} m</b>")
                popup_html = (
                    "<div style='font-family:monospace;font-size:13px;"
                    "min-width:150px;padding:4px 6px;line-height:1.6'>"
                    + "<br>".join(rows) + "</div>"
                )
                folium.Marker(
                    pos,
                    popup=folium.Popup(popup_html, max_width=200),
                    icon=folium.DivIcon(
                        html=(
                            f"<div style='background:#1a1a2e;color:#fff;"
                            f"border:2px solid #fc4c02;border-radius:50%;"
                            f"width:22px;height:22px;line-height:18px;"
                            f"text-align:center;font-size:9px;"
                            f"font-weight:bold;font-family:monospace;"
                            f"box-shadow:0 1px 4px rgba(0,0,0,.6)'>{km_num}</div>"
                        ),
                        icon_size=(22, 22),
                        icon_anchor=(11, 11),
                    )
                ).add_to(m)

            # ── F: Marker Start/End ───────────────────────────
            start_rows = [
                f"<b style='color:#2a9d5c;font-size:14px'>{t('map_start')}</b>",
                f"📅 {a.date_str}",
                f"📏 {fmt_dist(a.distance)}",
                f"⏱ {fmt_time(a.moving_time)}",
                f"👟 {a.avg_pace_str} /km",
            ]
            if a.avg_hr:
                start_rows.append(f"❤️ {a.avg_hr:.0f} bpm {t('avg_pace_label')}")
            start_rows.append(f"⛰ +{a.elev_gain:.0f} m")
            if a.calories:
                start_rows.append(f"🔥 {a.calories} kcal")
            if a.suffer_score:
                start_rows.append(f"{t('map_suffer')} {a.suffer_score}")

            end_rows = [
                f"<b style='color:#e63946;font-size:14px'>{t('map_finish')}</b>",
                f"📏 {fmt_dist(a.distance)}",
                f"⏱ {t('map_total')} {fmt_time(a.elapsed_time)}",
            ]
            if a.max_speed:
                end_rows.append(f"👟 {t('map_max')} {a.max_pace_str} /km")
            if a.max_hr:
                end_rows.append(f"❤️ {t('map_max')} {a.max_hr:.0f} bpm")

            def _popup(rows):
                body = "<br>".join(rows)
                return folium.Popup(
                    f"<div style='font-family:monospace;font-size:12px;"
                    f"min-width:170px;padding:6px 8px;line-height:1.7'>"
                    f"{body}</div>",
                    max_width=220,
                )

            folium.Marker(pts[0],  popup=_popup(start_rows), tooltip=t("map_start"),
                          icon=folium.Icon(color="green", icon="play")).add_to(m)
            folium.Marker(pts[-1], popup=_popup(end_rows),   tooltip=t("map_finish"),
                          icon=folium.Icon(color="red",   icon="stop")).add_to(m)

            # ── F: Statistics overlay (bar at top) ────────────────────────────
            hr_part  = f"&nbsp;|&nbsp; ❤️ {a.avg_hr:.0f} bpm" if a.avg_hr else ""
            cal_part = f"&nbsp;|&nbsp; 🔥 {a.calories} kcal" if a.calories else ""
            overlay_html = (
                "<div style='"
                "position:fixed;top:10px;left:50%;transform:translateX(-50%);"
                "z-index:1000;background:rgba(13,17,23,0.88);color:#e6edf3;"
                "font-family:monospace;font-size:12px;padding:7px 18px;"
                "border-radius:6px;border:1px solid #fc4c02;"
                "pointer-events:none;white-space:nowrap;"
                "box-shadow:0 2px 8px rgba(0,0,0,.5)'>"
                f"<b style='color:#fc4c02'>{a.name}</b>"
                f"&nbsp;|&nbsp; 📏 {fmt_dist(a.distance)}"
                f"&nbsp;|&nbsp; ⏱ {fmt_time(a.moving_time)}"
                f"&nbsp;|&nbsp; 👟 {a.avg_pace_str}/km"
                f"{hr_part}"
                f"&nbsp;|&nbsp; ⛰ +{a.elev_gain:.0f} m"
                f"{cal_part}"
                "</div>"
            )
            m.get_root().html.add_child(folium.Element(overlay_html))

            # ── D: FullScreen ─────────────────────────────────────────────────
            folium.plugins.Fullscreen(
                position="topright",
                title=t("map_fullscreen"),
                title_cancel=t("map_exit_fullscreen"),
                force_separate_button=True,
            ).add_to(m)

            # ── E: MiniMap ────────────────────────────────────────────────────
            folium.plugins.MiniMap(
                toggle_display=True,
                position="bottomright",
                width=150, height=150,
            ).add_to(m)

            # ── Layer control (after D/E for correct position) ────────────────
            folium.LayerControl(collapsed=False, position="topright").add_to(m)

            # ── Save and open in the browser ──────────────────────────────────────
            tmp = tempfile.NamedTemporaryFile(
                suffix=".html", prefix="strava_map_", delete=False)
            map_path = tmp.name
            tmp.close()
            m.save(map_path)
            webbrowser.open(f"file:///{map_path.replace(os.sep, '/')}")
            status_var.set(t("map_opened"))
            btn.config(text=t("map_reopen"))

        except Exception as e:
            status_var.set(t("map_error").format(e=e))

    btn = tk.Button(
        tab,
        text=t("map_open_browser"),
        font=("Courier", 12, "bold"),
        bg=C["accent"], fg="white",
        activebackground="#d43d00", activeforeground="white",
        bd=0, padx=28, pady=14,
        cursor="hand2", relief="flat",
        command=_open_map,
    )
    btn.place(relx=0.5, rely=0.50, anchor="center")

    tk.Label(tab,
             text=t("map_hint"),
             font=("Courier", 8), fg=C["text_dim"], bg=C["bg"]
             ).place(relx=0.5, rely=0.70, anchor="center")
