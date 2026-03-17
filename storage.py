# ── storage.py ────────────────────────────────────────────────────────────────
"""
Run storage management:
  - MongoStorage  → MongoDB collection (via pymongo)
"""

import os, json, subprocess, re
from datetime import datetime
from config import (MONGO_HOST, MONGO_PORT, MONGO_DB, MONGO_COLL, DOCKER_COMPOSE)

try:
    import pymongo
    HAS_MONGO = True
except ImportError:
    HAS_MONGO = False


# ══════════════════════════════════════════════════════════════════════════════
#  MONGODB STORAGE
# ══════════════════════════════════════════════════════════════════════════════

class MongoStorage:
    def __init__(self, host=MONGO_HOST, port=MONGO_PORT,
                 db=MONGO_DB, coll=MONGO_COLL):
        if not HAS_MONGO:
            raise RuntimeError("pymongo not installed: pip install pymongo")
        self._client = pymongo.MongoClient(host, port, serverSelectionTimeoutMS=3000)
        # Test connection
        self._client.server_info()
        self._coll = self._client[db][coll]
        self._coll.create_index("id", unique=True, sparse=True)

    def save(self, data: dict) -> str:
        """Activity upsert. Returns the MongoDB _id as a string."""
        doc = dict(data)
        sid = doc.get("id")
        if sid:
            self._coll.update_one({"id": sid}, {"$set": doc}, upsert=True)
            return str(self._coll.find_one({"id": sid}, {"_id": 1})["_id"])
        else:
            result = self._coll.insert_one(doc)
            return str(result.inserted_id)

    def list_all(self, filters: dict = None) -> list[dict]:
        query = _mongo_query(filters)
        cursor = self._coll.find(query, {
            "id": 1, "name": 1, "sport_type": 1, "type": 1,
            "start_date_local": 1, "distance": 1, "moving_time": 1,
            "elapsed_time": 1, "total_elevation_gain": 1,
            "average_speed": 1, "average_heartrate": 1,
            "calories": 1, "description": 1, "workout_type": 1,
            "start_latlng": 1, "location_city": 1, "location_country": 1, "_id": 1,
        }).sort("start_date_local", -1)
        results = []
        for doc in cursor:
            mid = str(doc.pop("_id"))
            summary = _make_summary(doc, source="mongo", ref=mid)
            if _passes(summary, filters):
                results.append(summary)
        return results

    def load(self, ref: str) -> dict:
        """Loads complete activity by MongoDB _id."""
        from bson import ObjectId
        doc = self._coll.find_one({"_id": ObjectId(ref)})
        if doc:
            doc.pop("_id", None)
        return doc

    def delete(self, ref: str):
        from bson import ObjectId
        self._coll.delete_one({"_id": ObjectId(ref)})

    def exists(self, strava_id) -> bool:
        if strava_id is None:
            return False
        return self._coll.count_documents({"id": strava_id}, limit=1) > 0

    def global_stats(self) -> dict:
        """Aggregate statistics on all runs."""
        pipeline = [
            {"$group": {
                "_id": None,
                "total_runs":     {"$sum": 1},
                "total_distance": {"$sum": "$distance"},
                "total_time":     {"$sum": "$moving_time"},
                "total_elev":     {"$sum": "$total_elevation_gain"},
                "avg_hr":         {"$avg": "$average_heartrate"},
                "avg_speed":      {"$avg": "$average_speed"},
            }}
        ]
        r = list(self._coll.aggregate(pipeline))
        return r[0] if r else {}

    def stats_per_year(self) -> list[dict]:
        pipeline = [
            {"$addFields": {"year": {"$substr": ["$start_date_local", 0, 4]}}},
            {"$group": {
                "_id":            "$year",
                "runs":           {"$sum": 1},
                "distance_km":    {"$sum": {"$divide": ["$distance", 1000]}},
                "time_sec":       {"$sum": "$moving_time"},
                "elev_gain":      {"$sum": "$total_elevation_gain"},
            }},
            {"$sort": {"_id": 1}},
        ]
        return list(self._coll.aggregate(pipeline))

    def close(self):
        self._client.close()

    def scan_effort_names(self) -> set:
        """Returns all unique best effort names in the database (diagnostics)."""
        pipeline = [
            {"$unwind": "$best_efforts"},
            {"$group": {"_id": "$best_efforts.name"}},
        ]
        return {doc["_id"] for doc in self._coll.aggregate(pipeline) if doc.get("_id")}

    def get_grade_splits(self, races_only: bool = False) -> list[dict]:
        """Returns list of {grade_pct, pace_ms, date} from all splits via MongoDB aggregation."""
        match_q: dict = {}
        if races_only:
            match_q["workout_type"] = 1
        pipeline = [
            {"$match": match_q},
            {"$project": {"splits_metric": 1, "start_date_local": 1, "_id": 0}},
            {"$unwind": "$splits_metric"},
            {"$match": {
                "splits_metric.distance": {"$gt": 100},
                "splits_metric.elevation_difference": {"$exists": True, "$ne": None},
                "splits_metric.average_speed": {"$gt": 0},
            }},
            {"$project": {
                "grade_pct": {"$multiply": [
                    {"$divide": ["$splits_metric.elevation_difference",
                                 "$splits_metric.distance"]},
                    100,
                ]},
                "pace_ms": "$splits_metric.average_speed",
                "date":    {"$substr": ["$start_date_local", 0, 10]},
            }},
            {"$limit": 100000},
        ]
        return [
            {"grade_pct": d.get("grade_pct", 0),
             "pace_ms":   d.get("pace_ms", 0),
             "date":      d.get("date", "")}
            for d in self._coll.aggregate(pipeline)
        ]

    def get_all_best_efforts(self, races_only: bool = False) -> list[dict]:
        """Returns all best efforts for the performance curve via MongoDB."""
        target_map    = _build_effort_target()
        all_raw_names = list(target_map.keys())
        match_q: dict = {"best_efforts.name": {"$in": all_raw_names}}
        if races_only:
            match_q["workout_type"] = 1
        pipeline = [
            {"$match": match_q},
            {"$unwind": "$best_efforts"},
            {"$match": {
                "best_efforts.name": {"$in": all_raw_names},
                "$or": [
                    {"best_efforts.moving_time": {"$gt": 0}},
                    {"best_efforts.elapsed_time": {"$gt": 0}},
                ],
            }},
            {"$project": {
                "raw_name":        "$best_efforts.name",
                "elapsed_time":    {"$ifNull": ["$best_efforts.moving_time",
                                               "$best_efforts.elapsed_time"]},
                "activity_name":   "$name",
                "date":            {"$substr": ["$start_date_local", 0, 10]},
                "activity_dist_km": {"$divide": [{"$ifNull": ["$distance", 0]}, 1000.0]},
            }},
        ]
        results = []
        for doc in self._coll.aggregate(pipeline):
            canonical = target_map.get(doc.get("raw_name", ""))
            if canonical:
                results.append({
                    "canonical":        canonical,
                    "elapsed_time":     doc["elapsed_time"],
                    "activity_name":    doc.get("activity_name", "–"),
                    "date":             doc.get("date", ""),
                    "activity_dist_km": doc.get("activity_dist_km", 0.0),
                })
        return results

    def get_best_efforts_records(self) -> dict:
        """Returns the best time for the main distances via MongoDB aggregation."""
        target_map = _build_effort_target()
        all_raw_names = list(target_map.keys())
        pipeline = [
            {"$unwind": "$best_efforts"},
            {"$match": {"best_efforts.name": {"$in": all_raw_names}}},
            {"$addFields": {
                "best_efforts._time": {"$ifNull": ["$best_efforts.moving_time",
                                                   "$best_efforts.elapsed_time"]},
            }},
            {"$sort": {"best_efforts._time": 1}},
            {"$group": {
                "_id": "$best_efforts.name",
                "elapsed_time": {"$first": "$best_efforts._time"},
                "activity_name": {"$first": "$name"},
                "date": {"$first": "$start_date_local"},
                "activity_id": {"$first": "$id"},
            }},
        ]
        result = {}
        for doc in self._coll.aggregate(pipeline):
            canonical = target_map.get(doc["_id"])
            if not canonical:
                continue
            existing = result.get(canonical)
            if not existing or doc["elapsed_time"] < existing["elapsed_time"]:
                result[canonical] = {
                    "elapsed_time": doc["elapsed_time"],
                    "activity_name": doc.get("activity_name", "–"),
                    "date": (doc.get("date") or "")[:10],
                    "activity_id": doc.get("activity_id"),
                }
        return result


# ══════════════════════════════════════════════════════════════════════════════
#  DOCKER HELPERS
# ══════════════════════════════════════════════════════════════════════════════

COMPOSE_CONTENT = """\
version: "3.8"
services:
  mongodb:
    image: mongo:7
    container_name: strava_mongo
    restart: unless-stopped
    ports:
      - "27017:27017"
    volumes:
      - strava_mongo_data:/data/db
    environment:
      MONGO_INITDB_DATABASE: strava

volumes:
  strava_mongo_data:
"""

def ensure_docker_compose(path: str):
    if not os.path.exists(path):
        with open(path, "w") as f:
            f.write(COMPOSE_CONTENT)

def start_mongo_container(compose_path: str) -> tuple[bool, str]:
    """Starts the MongoDB container. Returns (success, message)."""
    ensure_docker_compose(compose_path)
    try:
        result = subprocess.run(
            ["docker", "compose", "-f", compose_path, "up", "-d"],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0:
            return True, "Container MongoDB avviato."
        # Fallback docker-compose (v1)
        result2 = subprocess.run(
            ["docker-compose", "-f", compose_path, "up", "-d"],
            capture_output=True, text=True, timeout=60
        )
        if result2.returncode == 0:
            return True, "Container MongoDB avviato."
        return False, result.stderr or result2.stderr
    except FileNotFoundError:
        return False, "Docker non trovato. Assicurati che Docker Desktop sia in esecuzione."
    except subprocess.TimeoutExpired:
        return False, "Timeout avvio container."
    except Exception as e:
        return False, str(e)

def stop_mongo_container(compose_path: str) -> tuple[bool, str]:
    ensure_docker_compose(compose_path)
    try:
        result = subprocess.run(
            ["docker", "compose", "-f", compose_path, "down"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            return True, "Container MongoDB fermato."
        return False, result.stderr
    except Exception as e:
        return False, str(e)


# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS INTERNI
# ══════════════════════════════════════════════════════════════════════════════

# Map raw_name → canonical_key for Strava best efforts.
# Covers known API variants (English, alternative formats).
_EFFORT_ALIASES: dict[str, str] = {
    # 400m
    "400m":          "400m",
    "400 m":         "400m",
    # 1/2 mile (~804m)
    "1/2 mile":      "half_mile",
    "Half Mile":     "half_mile",
    "half mile":     "half_mile",
    # 1 km — Strava API uses "1K" (uppercase K)
    "1K":            "1k",
    "1k":            "1k",
    "1 km":          "1k",
    "1 kilometer":   "1k",
    "1 Kilometer":   "1k",
    # 1 mile (~1609m)
    "1 mile":        "1_mile",
    "1 Mile":        "1_mile",
    "1mile":         "1_mile",
    # 2 miles (~3219m)
    "2 mile":        "2_mile",
    "2 miles":       "2_mile",
    "2 Mile":        "2_mile",
    # 5 km — Strava API uses "5K"
    "5K":            "5k",
    "5k":            "5k",
    "5 km":          "5k",
    "5 kilometers":  "5k",
    "5 Kilometers":  "5k",
    # 10 km — Strava API uses "10K"
    "10K":           "10k",
    "10k":           "10k",
    "10 km":         "10k",
    "10 kilometers": "10k",
    "10 Kilometers": "10k",
    # half marathon — Strava API uses "Half-Marathon"
    "Half-Marathon": "Half-Marathon",
    "Half Marathon": "Half-Marathon",
    "half-marathon": "Half-Marathon",
    "half marathon": "Half-Marathon",
    "1/2 Marathon":  "Half-Marathon",
    # marathon — Strava API uses "Marathon"
    "Marathon":      "Marathon",
    "marathon":      "Marathon",
}

# Distance in meters for each canonical key (used for performance curve fit).
_EFFORT_DISTANCES: dict[str, float] = {
    "400m":          400.0,
    "half_mile":     804.67,
    "1k":            1000.0,
    "1_mile":        1609.34,
    "2_mile":        3218.69,
    "5k":            5000.0,
    "10k":           10000.0,
    "Half-Marathon": 21097.5,
    "Marathon":      42195.0,
}

def _build_effort_target() -> dict[str, str]:
    """Returns the raw_name → canonical map (e.g. '1k' → '1k')."""
    return dict(_EFFORT_ALIASES)

def _make_summary(data: dict, source: str, ref: str) -> dict:
    latlng = data.get("start_latlng") or []
    return {
        "source":       source,        # "json" | "mongo"
        "ref":          ref,            # path file o ObjectId
        "strava_id":    data.get("id"),
        "name":         data.get("name", "–"),
        "sport_type":   data.get("sport_type", data.get("type", "Run")),
        "start_date":   data.get("start_date_local", ""),
        "distance":     data.get("distance", 0),
        "moving_time":  data.get("moving_time", 0),
        "elapsed_time": data.get("elapsed_time", 0),
        "elev_gain":    data.get("total_elevation_gain", 0),
        "avg_speed":    data.get("average_speed", 0),
        "avg_hr":       data.get("average_heartrate"),
        "calories":     data.get("calories"),
        "description":  data.get("description") or "",
        "workout_type": data.get("workout_type"),
        "start_lat":    latlng[0] if len(latlng) > 0 else None,
        "start_lon":    latlng[1] if len(latlng) > 1 else None,
        "city":         data.get("location_city") or "",
        "country":      data.get("location_country") or "",
    }

def _passes(summary: dict, filters: dict) -> bool:
    if not filters:
        return True
    date_from = filters.get("date_from")
    date_to   = filters.get("date_to")
    dist_min  = filters.get("dist_min")
    dist_max  = filters.get("dist_max")
    elev_min  = filters.get("elev_min")
    elev_max  = filters.get("elev_max")
    name_q    = (filters.get("name") or "").lower().strip()

    date_str = summary.get("start_date", "")
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", ""))
        # Date comparison (not time): extremes are included
        if date_from and dt.date() < date_from.date():
            return False
        if date_to   and dt.date() > date_to.date():
            return False
    except Exception:
        pass

    dist_km = (summary.get("distance") or 0) / 1000
    if dist_min is not None and dist_km < dist_min:
        return False
    if dist_max is not None and dist_km > dist_max:
        return False

    elev = summary.get("elev_gain", 0) or 0
    if elev_min is not None and elev < elev_min:
        return False
    if elev_max is not None and elev > elev_max:
        return False

    if name_q:
        combined = (summary.get("name", "") + " " + summary.get("description", "")).lower()
        if name_q not in combined:
            return False
    if filters.get("races_only") and summary.get("workout_type") != 1:
        return False
    return True

def _mongo_query(filters: dict) -> dict:
    """Converte i filtri in una query MongoDB base (i filtri fini li facciamo in Python)."""
    if not filters:
        return {}
    q = {}
    date_from = filters.get("date_from")
    date_to   = filters.get("date_to")
    if date_from or date_to:
        q["start_date_local"] = {}
        if date_from:
            q["start_date_local"]["$gte"] = date_from.date().isoformat()
        if date_to:
            # Inclusive upper bound: includes the entire selected day
            from datetime import timedelta
            q["start_date_local"]["$lt"] = (date_to + timedelta(days=1)).date().isoformat()
    if filters.get("races_only"):
        q["workout_type"] = 1
    dist_min = filters.get("dist_min")
    dist_max = filters.get("dist_max")
    if dist_min is not None or dist_max is not None:
        q["distance"] = {}
        if dist_min is not None:
            q["distance"]["$gte"] = dist_min * 1000
        if dist_max is not None:
            q["distance"]["$lte"] = dist_max * 1000
    elev_min = filters.get("elev_min")
    elev_max = filters.get("elev_max")
    if elev_min is not None or elev_max is not None:
        q["total_elevation_gain"] = {}
        if elev_min is not None:
            q["total_elevation_gain"]["$gte"] = elev_min
        if elev_max is not None:
            q["total_elevation_gain"]["$lte"] = elev_max
    return q
