# ── storage_manager.py ────────────────────────────────────────────────────────
"""
StorageManager: facade over MongoStorage.
Exposes list_all(), load_activity(), delete(), exists() for the MongoDB backend.
"""

from models import ActivityData
from storage import MongoStorage, start_mongo_container
from config import MONGO_HOST, MONGO_PORT, DOCKER_COMPOSE, MONGO_DB, MONGO_SETTINGS_COLL


def load_settings_sync(timeout_ms: int = 800) -> dict:
    """Quick synchronous read of app settings before the UI is built.

    Used at startup to restore language preference. Returns an empty dict
    if MongoDB is not reachable within *timeout_ms* milliseconds.
    """
    try:
        import pymongo
        client = pymongo.MongoClient(MONGO_HOST, MONGO_PORT,
                                     serverSelectionTimeoutMS=timeout_ms)
        client.server_info()
        doc = client[MONGO_DB][MONGO_SETTINGS_COLL].find_one({"_id": "settings"}) or {}
        client.close()
        doc.pop("_id", None)
        return doc
    except Exception:
        return {}


class StorageManager:
    def __init__(self, auto_start_mongo: bool = False):
        self.mongo_storage = None
        self.mongo_ok      = False

        if auto_start_mongo:
            self.connect_mongo(auto_start=True)

    # ── MongoDB ───────────────────────────────────────────────────────────────

    def connect_mongo(self, auto_start: bool = False) -> tuple[bool, str]:
        """
        Attempts to connect to MongoDB.
        If auto_start=True and it fails, starts the Docker container and retries.
        Returns (success, message).
        """
        try:
            self.mongo_storage = MongoStorage(MONGO_HOST, MONGO_PORT)
            self.mongo_ok = True
            return True, "Connesso a MongoDB."
        except Exception as first_err:
            if not auto_start:
                self.mongo_storage = None
                self.mongo_ok = False
                return False, str(first_err)

        # Start the Docker container
        ok, msg = start_mongo_container(DOCKER_COMPOSE)
        if not ok:
            self.mongo_ok = False
            return False, f"Impossibile avviare MongoDB: {msg}"

        # Wait and retry (max 15s)
        import time
        for _ in range(5):
            time.sleep(3)
            try:
                self.mongo_storage = MongoStorage(MONGO_HOST, MONGO_PORT)
                self.mongo_ok = True
                return True, "Container MongoDB avviato e connesso."
            except Exception:
                pass

        self.mongo_ok = False
        return False, "MongoDB avviato ma non raggiungibile. Riprova tra qualche secondo."

    def disconnect_mongo(self):
        if self.mongo_storage:
            try:
                self.mongo_storage.close()
            except Exception:
                pass
        self.mongo_storage = None
        self.mongo_ok = False

    # ── Unified interface ─────────────────────────────────────────────────────

    def list_all(self, filters: dict = None) -> list[dict]:
        if self.mongo_ok and self.mongo_storage:
            try:
                return self.mongo_storage.list_all(filters)
            except Exception:
                pass
        return []

    def load_activity(self, summary: dict) -> ActivityData | None:
        """Loads the complete activity from MongoDB."""
        if not (self.mongo_ok and self.mongo_storage):
            return None
        try:
            data = self.mongo_storage.load(summary["ref"])
            return ActivityData(data) if data else None
        except Exception as e:
            print(f"[StorageManager] Errore caricamento: {e}")
            return None

    def delete(self, summary: dict):
        if self.mongo_ok and self.mongo_storage:
            self.mongo_storage.delete(summary["ref"])

    def exists(self, strava_id) -> bool:
        if self.mongo_ok and self.mongo_storage:
            return self.mongo_storage.exists(strava_id)
        return False

    def global_stats(self) -> dict | None:
        if self.mongo_ok and self.mongo_storage:
            return self.mongo_storage.global_stats()
        return None

    def stats_per_year(self) -> list[dict]:
        if self.mongo_ok and self.mongo_storage:
            return self.mongo_storage.stats_per_year()
        return []

    def get_personal_records(self) -> dict:
        if self.mongo_ok and self.mongo_storage:
            try:
                return self.mongo_storage.get_best_efforts_records()
            except Exception:
                pass
        return {}

    def get_grade_splits(self, races_only: bool = False) -> list[dict]:
        if self.mongo_ok and self.mongo_storage:
            try:
                return self.mongo_storage.get_grade_splits(races_only)
            except Exception:
                pass
        return []

    def get_all_best_efforts(self, races_only: bool = False) -> list[dict]:
        if self.mongo_ok and self.mongo_storage:
            try:
                return self.mongo_storage.get_all_best_efforts(races_only)
            except Exception:
                pass
        return []

    def load_app_settings(self) -> dict:
        if self.mongo_ok and self.mongo_storage:
            try:
                return self.mongo_storage.load_app_settings()
            except Exception:
                pass
        return {}

    def save_app_setting(self, key: str, value):
        if self.mongo_ok and self.mongo_storage:
            try:
                self.mongo_storage.save_app_setting(key, value)
            except Exception:
                pass

    def load_gear_settings(self) -> dict:
        if self.mongo_ok and self.mongo_storage:
            try:
                return self.mongo_storage.load_gear_settings()
            except Exception:
                pass
        return {}

    def save_gear_threshold(self, gear_name: str, km: float):
        if self.mongo_ok and self.mongo_storage:
            try:
                self.mongo_storage.save_gear_threshold(gear_name, km)
            except Exception:
                pass

    def save_gear_dismissed(self, gear_name: str, dismissed: bool):
        if self.mongo_ok and self.mongo_storage:
            try:
                self.mongo_storage.save_gear_dismissed(gear_name, dismissed)
            except Exception:
                pass

    def gear_stats(self) -> list[dict]:
        if self.mongo_ok and self.mongo_storage:
            try:
                return self.mongo_storage.gear_stats()
            except Exception:
                pass
        return []

    def gear_monthly_km(self) -> list[dict]:
        if self.mongo_ok and self.mongo_storage:
            try:
                return self.mongo_storage.gear_monthly_km()
            except Exception:
                pass
        return []

    def scan_effort_names(self) -> set:
        if self.mongo_ok and self.mongo_storage:
            try:
                return self.mongo_storage.scan_effort_names()
            except Exception:
                pass
        return set()

    _GEOCODE_COLL = "geocode_cache"

    def get_geocode(self, lat: float, lon: float) -> str | None:
        key = f"{lat:.3f},{lon:.3f}"
        if self.mongo_ok and self.mongo_storage:
            try:
                coll = self.mongo_storage._client[MONGO_DB][self._GEOCODE_COLL]
                doc = coll.find_one({"_id": key}, {"city": 1})
                if doc is not None:
                    return doc.get("city", "")
            except Exception:
                pass
        return None

    def set_geocode(self, lat: float, lon: float, city: str):
        key = f"{lat:.3f},{lon:.3f}"
        if self.mongo_ok and self.mongo_storage:
            try:
                coll = self.mongo_storage._client[MONGO_DB][self._GEOCODE_COLL]
                coll.update_one({"_id": key}, {"$set": {"city": city}}, upsert=True)
            except Exception:
                pass

    def get_route_groups(self, min_runs: int = 3) -> list[list[dict]]:
        from collections import defaultdict
        _RUN_TYPES = {"Run", "Trail Run", "VirtualRun", "Hike", "Walk"}
        GRID = 0.003
        summaries = self.list_all()
        groups: dict = defaultdict(list)
        for s in summaries:
            lat = s.get("start_lat")
            lon = s.get("start_lon")
            dist = s.get("distance", 0)
            if not lat or not lon or dist < 500:
                continue
            if s.get("sport_type", "Run") not in _RUN_TYPES:
                continue
            grid_lat = round(round(lat / GRID) * GRID, 6)
            grid_lon = round(round(lon / GRID) * GRID, 6)
            dist_bucket = round(dist / 1000)
            groups[(grid_lat, grid_lon, dist_bucket)].append(s)
        result = [
            sorted(v, key=lambda x: x.get("start_date", ""))
            for v in groups.values()
            if len(v) >= min_runs
        ]
        result.sort(key=len, reverse=True)
        return result

    def get_group_polylines(self, group: list) -> list:
        from models import decode_polyline
        if not (self.mongo_ok and self.mongo_storage):
            return []
        try:
            ids = [s["strava_id"] for s in group if s.get("strava_id")]
            cursor = self.mongo_storage._coll.find(
                {"id": {"$in": ids}},
                {"name": 1, "start_date_local": 1,
                 "map.polyline": 1, "map.summary_polyline": 1}
            )
            result = []
            for doc in cursor:
                m = doc.get("map") or {}
                poly_str = m.get("polyline") or m.get("summary_polyline", "")
                if poly_str:
                    pts = decode_polyline(poly_str)
                    if pts:
                        result.append((
                            doc.get("name", ""),
                            (doc.get("start_date_local") or "")[:10],
                            pts,
                        ))
            return result
        except Exception:
            return []

    def list_polylines(self) -> list:
        from models import decode_polyline
        if not (self.mongo_ok and self.mongo_storage):
            return []
        try:
            cursor = self.mongo_storage._coll.find(
                {"map.summary_polyline": {"$exists": True, "$ne": ""}},
                {"name": 1, "start_date_local": 1,
                 "map.polyline": 1, "map.summary_polyline": 1}
            )
            result = []
            for doc in cursor:
                m = doc.get("map") or {}
                poly_str = m.get("polyline") or m.get("summary_polyline", "")
                if poly_str:
                    pts = decode_polyline(poly_str)
                    if pts:
                        result.append((
                            doc.get("name", ""),
                            (doc.get("start_date_local") or "")[:10],
                            pts,
                        ))
            return result
        except Exception:
            return []

    def stats_per_month(self, year: int = None) -> list:
        from collections import defaultdict
        summaries = self.list_all()
        by_month = defaultdict(lambda: {
            "count": 0, "dist_km": 0.0, "time_sec": 0,
            "elev_gain": 0.0, "speed_sum": 0.0, "speed_n": 0,
        })
        for s in summaries:
            ym = (s.get("start_date") or "")[:7]
            if len(ym) < 7 or not ym[:4].isdigit():
                continue
            if year and int(ym[:4]) != year:
                continue
            by_month[ym]["count"]    += 1
            by_month[ym]["dist_km"]  += s.get("distance", 0) / 1000
            by_month[ym]["time_sec"] += s.get("moving_time", 0)
            by_month[ym]["elev_gain"]+= s.get("elev_gain", 0)
            sp = s.get("avg_speed", 0)
            if sp > 0:
                by_month[ym]["speed_sum"] += sp
                by_month[ym]["speed_n"]   += 1

        result = []
        for ym, d in sorted(by_month.items()):
            n = d["speed_n"]
            result.append({
                "month":     ym,
                "count":     d["count"],
                "dist_km":   d["dist_km"],
                "time_sec":  d["time_sec"],
                "elev_gain": d["elev_gain"],
                "avg_speed": d["speed_sum"] / n if n else 0,
            })
        return result
