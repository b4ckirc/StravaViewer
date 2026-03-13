# ── storage_manager.py ────────────────────────────────────────────────────────
"""
StorageManager: facade unificata su JSONStorage + MongoStorage.
Espone list_all(), load_activity(), delete(), exists() indipendentemente
da quale/quali backend sono attivi.
"""

import os
from models import ActivityData
from storage import JSONStorage, MongoStorage, start_mongo_container
from config import MONGO_HOST, MONGO_PORT, DOCKER_COMPOSE

DEFAULT_JSON_DIR = "strava_activities"


class StorageManager:
    def __init__(self, json_dir: str = DEFAULT_JSON_DIR,
                 auto_start_mongo: bool = False):
        self.json_storage  = JSONStorage(json_dir)
        self.mongo_storage = None
        self.mongo_ok      = False

        if auto_start_mongo:
            self.connect_mongo(auto_start=True)

    # ── MongoDB ───────────────────────────────────────────────────────────────

    def connect_mongo(self, auto_start: bool = False) -> tuple[bool, str]:
        """
        Tenta di connettersi a MongoDB.
        Se auto_start=True e fallisce, avvia il container Docker e riprova.
        Ritorna (success, message).
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

        # Avvia il container Docker
        ok, msg = start_mongo_container(DOCKER_COMPOSE)
        if not ok:
            self.mongo_ok = False
            return False, f"Impossibile avviare MongoDB: {msg}"

        # Attendi e riprova (max 15s)
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

    # ── Interfaccia unificata ─────────────────────────────────────────────────

    def list_all(self, filters: dict = None) -> list[dict]:
        """
        Lista sommari da tutti i backend attivi, deduplicata per strava_id.
        I record MongoDB hanno priorità su quelli JSON in caso di duplicati.
        """
        seen_ids = set()
        results  = []

        # MongoDB prima (più completo)
        if self.mongo_ok and self.mongo_storage:
            try:
                for s in self.mongo_storage.list_all(filters):
                    sid = s.get("strava_id")
                    if sid:
                        seen_ids.add(sid)
                    results.append(s)
            except Exception:
                pass

        # JSON (solo se non già presenti in Mongo)
        for s in self.json_storage.list_all(filters):
            sid = s.get("strava_id")
            if sid and sid in seen_ids:
                continue
            results.append(s)

        # Ordina per data decrescente
        results.sort(key=lambda x: x.get("start_date", ""), reverse=True)
        return results

    def load_activity(self, summary: dict) -> ActivityData | None:
        """Carica l'attività completa dal backend corretto."""
        try:
            if summary["source"] == "mongo" and self.mongo_ok:
                data = self.mongo_storage.load(summary["ref"])
            else:
                data = self.json_storage.load(summary["ref"])
            return ActivityData(data) if data else None
        except Exception as e:
            print(f"[StorageManager] Errore caricamento: {e}")
            return None

    def delete(self, summary: dict):
        """Elimina dal backend corretto."""
        if summary["source"] == "mongo" and self.mongo_ok:
            self.mongo_storage.delete(summary["ref"])
        else:
            self.json_storage.delete(summary["ref"])

    def exists(self, strava_id) -> bool:
        """Controlla se l'attività esiste in almeno un backend."""
        if self.json_storage.exists(strava_id):
            return True
        if self.mongo_ok and self.mongo_storage:
            return self.mongo_storage.exists(strava_id)
        return False

    def global_stats(self) -> dict | None:
        """Statistiche aggregate (solo se MongoDB disponibile)."""
        if self.mongo_ok and self.mongo_storage:
            return self.mongo_storage.global_stats()
        return None

    def stats_per_year(self) -> list[dict]:
        if self.mongo_ok and self.mongo_storage:
            return self.mongo_storage.stats_per_year()
        return []

    def get_personal_records(self) -> dict:
        """Miglior tempo per le principali distanze su tutto il database."""
        if self.mongo_ok and self.mongo_storage:
            try:
                return self.mongo_storage.get_best_efforts_records()
            except Exception:
                pass
        return self.json_storage.get_best_efforts_records()

    def get_grade_splits(self, races_only: bool = False) -> list[dict]:
        """Dati pendenza/passo per grade analysis (da tutti gli split)."""
        if self.mongo_ok and self.mongo_storage:
            try:
                return self.mongo_storage.get_grade_splits(races_only)
            except Exception:
                pass
        return self.json_storage.get_grade_splits(races_only)

    def get_all_best_efforts(self, races_only: bool = False) -> list[dict]:
        """Tutti i best effort per la curva di performance."""
        if self.mongo_ok and self.mongo_storage:
            try:
                return self.mongo_storage.get_all_best_efforts(races_only)
            except Exception:
                pass
        return self.json_storage.get_all_best_efforts(races_only)

    def scan_effort_names(self) -> set:
        """Diagnostica: ritorna tutti i nomi di best effort presenti nel database."""
        if self.mongo_ok and self.mongo_storage:
            try:
                return self.mongo_storage.scan_effort_names()
            except Exception:
                pass
        return self.json_storage.scan_effort_names()

    def list_polylines(self) -> list:
        """
        Ritorna [(name, date_str, [(lat, lon), ...])] per tutte le attività con GPS.
        Legge solo i campi necessari (lightweight).
        """
        from models import decode_polyline
        result = []

        if self.mongo_ok and self.mongo_storage:
            try:
                cursor = self.mongo_storage._coll.find(
                    {"map.summary_polyline": {"$exists": True, "$ne": ""}},
                    {"name": 1, "start_date_local": 1,
                     "map.polyline": 1, "map.summary_polyline": 1}
                )
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
            except Exception:
                pass
        else:
            import os as _os, json as _json
            json_dir = self.json_storage.directory
            if _os.path.isdir(json_dir):
                for fname in sorted(_os.listdir(json_dir)):
                    if not fname.endswith(".json"):
                        continue
                    try:
                        with open(_os.path.join(json_dir, fname), encoding="utf-8") as f:
                            data = _json.load(f)
                        m = data.get("map") or {}
                        poly_str = m.get("polyline") or m.get("summary_polyline", "")
                        if poly_str:
                            pts = decode_polyline(poly_str)
                            if pts:
                                result.append((
                                    data.get("name", ""),
                                    (data.get("start_date_local") or "")[:10],
                                    pts,
                                ))
                    except Exception:
                        pass

        return result

    def stats_per_month(self, year: int = None) -> list:
        """
        Statistiche aggregate per mese (YYYY-MM), opzionalmente filtrate per anno.
        Ritorna lista di dict ordinata cronologicamente.
        """
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
