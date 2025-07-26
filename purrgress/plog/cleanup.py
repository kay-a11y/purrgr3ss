from copy import deepcopy
from datetime import datetime
from logging import getLogger

from purrgress.utils import log_call

log = getLogger("plog")

@log_call()
def _span_key(span: str) -> datetime:
    """
    Given a string like "14:20-18:30",
    it returns a datetime object representing the start time (14:20)
    """
    try:
        start_time = span.split("-")[0]
        dt = datetime.strptime(start_time, "%H:%M")
        log.debug("[_span_key] Parsed start_time=%s, result=%s", start_time, dt)
        return dt
    except Exception as e:
        log.error("[_span_key] Failed to parse span=%s: %s", span, e)
        raise

@log_call()
def tidy_day(node: dict) -> dict:
    """
    Clean and normalize a day's session data for plog.

    Steps performed:
    1. Deep-copies input data to avoid side effects.
    2. Ensures all session dicts have the keys: 'task', 'tags', 'moods', 'spans'.
    3. Deduplicates and sorts each session's 'spans' chronologically.
    4. Merges sessions with the same task and tags, combining spans and moods.
    5. Rebuilds a normalized session list and sorts by the first span (empty sessions pushed to the end).
    6. Returns an ordered dict with optional 'wake'/'sleep' at the top, followed by cleaned 'sessions'.

    Args:
        node (dict): The raw session data for a single day (as loaded from YAML/JSON).

    Returns:
        dict: A cleaned, normalized dict for the day, ready to be written back to disk.

    Example:
        >>> tidy_day({
        ...     'wake': '08:00',
        ...     'sessions': [
        ...         {'task': 'code', 'tags': ['python'], 'moods': ['💪'], 'spans': ['09:00-10:00']},
        ...         {'task': 'code', 'tags': ['python'], 'moods': ['🔥'], 'spans': ['14:00-15:00']}
        ...     ]
        ... })
        {
            'wake': '08:00',
            'sessions': [
                {'task': 'code', 'tags': ['python'], 'moods': ['💪', '🔥'], 'spans': ['09:00-10:00', '14:00-15:00']}
            ]
        }
    """
    node = deepcopy(node)
    sessions = node.get("sessions", [])
    log.debug("[tidy_day] Sessions count: %d", len(sessions))

    log.debug("[tidy_day] Normalizing missing keys in sessions...")
    for sess in sessions:
        sess.setdefault("task", "")
        sess.setdefault("tags", [])
        sess.setdefault("moods", [])
        sess.setdefault("spans", [])

    log.debug("[tidy_day] Deduping and sorting spans for each session...")
    for sess in sessions:
        spans = sess.get("spans") or []
        sess["spans"] = sorted(set(spans), key=_span_key) if spans else []

    log.debug("[tidy_day] Merging sessions with same task+tags...")
    merged = {}
    for sess in sessions:
        key = (sess["task"], tuple(sess["tags"]))
        bucket = merged.setdefault(key, {"spans": [], "moods": set()})
        bucket["spans"].extend(sess["spans"])
        bucket["moods"].update(sess.get("moods", []))

    log.debug("[tidy_day] Rebuilding sessions list...")
    clean_sessions = []
    for (task, tags), payload in merged.items():
        spans = sorted(set(payload["spans"]), key=_span_key)
        moods = sorted(payload["moods"]) if payload["moods"] else []
        clean_sessions.append(
            {"task": task, "tags": list(tags), "moods": moods, "spans": spans}
        )

    log.debug("[tidy_day] Sorting sessions by first span...")
    def first_span_dt(s):
        return _span_key(s["spans"][0]) if s["spans"] else datetime.max
    clean_sessions.sort(key=first_span_dt)

    log.debug("[tidy_day] Ordering keys in output...")
    ordered = {}
    for k in ("wake", "sleep"):
        if k in node:
            ordered[k] = node[k]
    ordered["sessions"] = clean_sessions

    log.debug("[tidy_day] Tidy complete. Final sessions count: %d", len(clean_sessions))
    return ordered

def tidy_month(data: dict) -> dict:
    """Clean and normalize a month's session data for plog."""
    return {day: tidy_day(node) for day, node in sorted(data.items())}