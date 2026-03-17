# ── interval_detector.py ──────────────────────────────────────────────────────
"""
Pure-logic module: detects interval / structured workouts from per-km splits.

No UI imports — only stdlib. All tuning constants are at the top.
"""

import math
import statistics
from dataclasses import dataclass, field

# ── Tuning constants ──────────────────────────────────────────────────────────
MIN_SPLITS          = 4    # minimum km splits to attempt detection
MIN_INTERVAL_COUNT  = 3    # minimum "work" (fast) segments required
THRESHOLD_RATIO     = 0.5  # std-dev multiplier for fast/slow labelling
CV_THRESHOLD        = 0.06 # coefficient of variation floor (6 %)


# ── Data structures ───────────────────────────────────────────────────────────

@dataclass
class Segment:
    type: str            # "fast" | "slow"
    km_indices: list
    paces: list          # min/km floats
    avg_pace: float
    avg_hr: float        # None if no HR data
    total_time: int      # seconds
    total_dist: float    # metres


@dataclass
class IntervalResult:
    is_interval: bool
    reason: str          = ""
    workout_type: str    = ""
    segments: list       = field(default_factory=list)
    fast_segs: list      = field(default_factory=list)
    slow_segs: list      = field(default_factory=list)
    avg_work_pace: float = 0.0
    avg_recovery_pace: float = 0.0
    fade_rate: float     = 0.0
    consistency_score: int = 0
    avg_pace: float      = 0.0
    std_pace: float      = 0.0
    cv: float            = 0.0
    paces: list          = field(default_factory=list)
    labels: list         = field(default_factory=list)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _build_segment(seg_type, indices, paces, splits):
    seg_paces  = [paces[i] for i in indices]
    seg_splits = [splits[i] for i in indices]
    hrs = [s.get("average_heartrate") for s in seg_splits
           if s.get("average_heartrate")]
    return Segment(
        type       = seg_type,
        km_indices = list(indices),
        paces      = seg_paces,
        avg_pace   = statistics.mean(seg_paces),
        avg_hr     = statistics.mean(hrs) if hrs else None,
        total_time = sum(s.get("moving_time", 0) for s in seg_splits),
        total_dist = sum(s.get("distance", 0)    for s in seg_splits),
    )


def _group_consecutive(labels, paces, splits):
    """Group consecutive same-label km into Segment objects.
    Neutral km are absorbed into the previous segment (or skipped if leading).
    """
    segments     = []
    current_type = None
    current_idxs = []

    for i, label in enumerate(labels):
        effective = label if label != "neutral" else current_type
        if effective is None:
            continue  # leading neutrals skipped

        if effective != current_type and current_idxs:
            segments.append(_build_segment(current_type, current_idxs, paces, splits))
            current_idxs = []

        current_type = effective
        current_idxs.append(i)

    if current_idxs and current_type:
        segments.append(_build_segment(current_type, current_idxs, paces, splits))

    return segments


def _is_monotone_block(types_seq):
    """Return True if all fast segments come before all slow (or vice-versa)."""
    seen = set()
    for t in types_seq:
        if t in seen:
            return False
        # Once we have seen both, it's alternating
    # Only triggered for 1–2 unique values; single type = monotone
    return len(set(types_seq)) == 1


def _classify_workout(avg_work_pace, pace_ratio, num_intervals,
                      avg_interval_dist_m):
    """Return a workout type string based on segment characteristics."""
    if avg_interval_dist_m < 600 and pace_ratio < 0.88:
        return "vo2max"
    if pace_ratio < 0.92 and num_intervals >= 3:
        return "threshold"
    if pace_ratio < 0.96 and num_intervals >= 4:
        return "tempo"
    if num_intervals <= 3 and pace_ratio < 0.97:
        return "fartlek"
    return "easy_strides"


# ── Public API ────────────────────────────────────────────────────────────────

def detect_intervals(splits) -> IntervalResult:
    """Analyse per-km splits and return an IntervalResult."""

    # Guard: need enough splits
    if not splits or len(splits) < MIN_SPLITS:
        return IntervalResult(is_interval=False, reason="too_few_splits")

    # Extract valid paces (min/km)
    paces = []
    for s in splits:
        spd = s.get("average_speed", 0)
        if spd and spd > 0:
            paces.append(1000.0 / spd / 60.0)
        else:
            paces.append(None)

    valid_paces = [p for p in paces if p is not None]
    if len(valid_paces) < MIN_SPLITS:
        return IntervalResult(is_interval=False, reason="no_valid_paces")

    avg_pace = statistics.mean(valid_paces)
    std_pace = statistics.stdev(valid_paces) if len(valid_paces) > 1 else 0.0
    cv       = std_pace / avg_pace if avg_pace > 0 else 0.0

    # Check minimum variation (avoid misclassifying even-paced runs)
    if cv < CV_THRESHOLD:
        return IntervalResult(
            is_interval = False,
            reason      = "no_pattern",
            avg_pace    = avg_pace,
            std_pace    = std_pace,
            cv          = cv,
            paces       = [p or 0 for p in paces],
            labels      = ["neutral"] * len(splits),
        )

    # Label each km: fast / slow / neutral
    labels = []
    for p in paces:
        if p is None:
            labels.append("neutral")
        elif p < avg_pace - THRESHOLD_RATIO * std_pace:
            labels.append("fast")
        elif p > avg_pace + THRESHOLD_RATIO * std_pace:
            labels.append("slow")
        else:
            labels.append("neutral")

    fast_count = labels.count("fast")
    if fast_count < MIN_INTERVAL_COUNT:
        return IntervalResult(
            is_interval = False,
            reason      = "no_pattern",
            avg_pace    = avg_pace,
            std_pace    = std_pace,
            cv          = cv,
            paces       = [p or 0 for p in paces],
            labels      = labels,
        )

    # Group consecutive same-label km into segments
    valid_paces_list = [p or 0 for p in paces]
    segments  = _group_consecutive(labels, valid_paces_list, splits)
    fast_segs = [s for s in segments if s.type == "fast"]
    slow_segs = [s for s in segments if s.type == "slow"]

    # Need at least 2 work intervals and 1 recovery, alternating
    if len(fast_segs) < 2 or len(slow_segs) < 1:
        return IntervalResult(is_interval=False, reason="no_alternation",
                              paces=valid_paces_list, labels=labels,
                              avg_pace=avg_pace, std_pace=std_pace, cv=cv)

    types_seq = [s.type for s in segments]
    if _is_monotone_block(types_seq):
        return IntervalResult(is_interval=False, reason="no_alternation",
                              paces=valid_paces_list, labels=labels,
                              avg_pace=avg_pace, std_pace=std_pace, cv=cv)

    # ── Compute analytics ─────────────────────────────────────────────────────
    work_paces     = [s.avg_pace for s in fast_segs]
    recovery_paces = [s.avg_pace for s in slow_segs]

    avg_work_pace     = statistics.mean(work_paces)
    avg_recovery_pace = statistics.mean(recovery_paces)

    # Fade rate: last work interval pace minus first (positive = slowing down)
    fade_rate = work_paces[-1] - work_paces[0]

    # Consistency: 100 - CV-of-work-paces * 100, clamped 0–100
    work_cv = (statistics.stdev(work_paces) / avg_work_pace
               if len(work_paces) > 1 else 0.0)
    consistency_score = max(0, min(100, round(100 - work_cv * 100)))

    # Workout classification
    pace_ratio        = avg_work_pace / avg_pace if avg_pace > 0 else 1.0
    avg_interval_dist = statistics.mean(s.total_dist for s in fast_segs)
    workout_type      = _classify_workout(avg_work_pace, pace_ratio,
                                          len(fast_segs), avg_interval_dist)

    return IntervalResult(
        is_interval       = True,
        workout_type      = workout_type,
        segments          = segments,
        fast_segs         = fast_segs,
        slow_segs         = slow_segs,
        avg_work_pace     = avg_work_pace,
        avg_recovery_pace = avg_recovery_pace,
        fade_rate         = fade_rate,
        consistency_score = consistency_score,
        avg_pace          = avg_pace,
        std_pace          = std_pace,
        cv                = cv,
        paces             = valid_paces_list,
        labels            = labels,
    )
