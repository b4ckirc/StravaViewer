# ── models.py ─────────────────────────────────────────────────────────────────
from datetime import datetime
from config import HR_ZONES


def fmt_pace(speed_ms):
    if not speed_ms or speed_ms <= 0:
        return "--:--"
    sec = 1000 / speed_ms
    return f"{int(sec // 60)}:{int(sec % 60):02d}"

def fmt_time(seconds):
    if seconds is None:
        return "--"
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"

def fmt_dist(meters):
    return f"{meters / 1000:.2f} km"

def speed_to_pace(speed_ms):
    if not speed_ms or speed_ms <= 0:
        return None
    return 1000 / speed_ms / 60

def pace_label(val):
    if not val or val <= 0:
        return "--:--"
    return f"{int(val)}:{int((val - int(val)) * 60):02d}"

def decode_polyline(s):
    pts, idx, lat, lon = [], 0, 0, 0
    while idx < len(s):
        for coord in ("lat", "lon"):
            shift = result = 0
            while True:
                b = ord(s[idx]) - 63
                idx += 1
                result |= (b & 0x1f) << shift
                shift += 5
                if b < 0x20:
                    break
            delta = ~(result >> 1) if result & 1 else result >> 1
            if coord == "lat":
                lat += delta
            else:
                lon += delta
        pts.append((lat / 1e5, lon / 1e5))
    return pts

def hr_zone_for(hr, hr_max):
    pct = hr / hr_max * 100
    for name, lo, hi, col in HR_ZONES:
        if pct < hi:
            return name, col
    return HR_ZONES[-1][0], HR_ZONES[-1][3]


class ActivityData:
    def __init__(self, data: dict):
        self.raw = data
        self._parse()

    def _parse(self):
        d = self.raw
        self.name         = d.get("name", "Attività senza nome")
        self.sport_type   = d.get("sport_type", d.get("type", "Run"))
        self.distance     = d.get("distance", 0)
        self.moving_time  = d.get("moving_time", 0)
        self.elapsed_time = d.get("elapsed_time", 0)
        self.elev_gain    = d.get("total_elevation_gain", 0)
        self.elev_high    = d.get("elev_high")
        self.elev_low     = d.get("elev_low")
        self.avg_speed    = d.get("average_speed", 0)
        self.max_speed    = d.get("max_speed", 0)
        self.avg_hr       = d.get("average_heartrate")
        self.max_hr       = d.get("max_heartrate")
        self.avg_cadence  = d.get("average_cadence")
        self.calories     = d.get("calories")
        self.suffer_score = d.get("suffer_score")
        self.start_date   = d.get("start_date_local", "")
        self.city         = d.get("location_city") or ""
        self.country      = d.get("location_country") or ""
        self.device       = d.get("device_name") or ""
        self.gear         = (d.get("gear") or {}).get("name", "")
        self.achievements = d.get("achievement_count", 0)
        self.avg_watts    = d.get("average_watts")
        self.description  = d.get("description") or ""
        self.pr_count     = d.get("pr_count", 0)
        self.splits       = d.get("splits_metric", [])
        self.best_efforts = d.get("best_efforts", [])
        self.strava_id    = d.get("id")
        poly = (d.get("map") or {}).get("polyline") or \
               (d.get("map") or {}).get("summary_polyline", "")
        self.gps_points = decode_polyline(poly) if poly else []

    @property
    def avg_pace_str(self): return fmt_pace(self.avg_speed)
    @property
    def max_pace_str(self):  return fmt_pace(self.max_speed)

    @property
    def date_str(self):
        try:
            dt = datetime.fromisoformat(self.start_date.replace("Z", ""))
            return dt.strftime("%d %B %Y  •  %H:%M")
        except Exception:
            return self.start_date

    @property
    def date_obj(self):
        try:
            return datetime.fromisoformat(self.start_date.replace("Z", ""))
        except Exception:
            return None

    def hr_zone_seconds(self, hr_max=190):
        zone_secs = {z[0]: 0 for z in HR_ZONES}
        for s in self.splits:
            hr = s.get("average_heartrate")
            t  = s.get("moving_time", 0)
            if hr:
                name, _ = hr_zone_for(hr, hr_max)
                zone_secs[name] += t
        return zone_secs

    def to_summary_dict(self):
        """Dizionario leggero per la libreria (senza raw completo)."""
        return {
            "strava_id":    self.strava_id,
            "name":         self.name,
            "sport_type":   self.sport_type,
            "start_date":   self.start_date,
            "distance":     self.distance,
            "moving_time":  self.moving_time,
            "elapsed_time": self.elapsed_time,
            "elev_gain":    self.elev_gain,
            "avg_speed":    self.avg_speed,
            "avg_hr":       self.avg_hr,
            "calories":     self.calories,
            "description":  self.description,
        }
