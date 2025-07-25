from copy import deepcopy
from datetime import datetime
from logging import getLogger
from purrgress.utils import log_call

log = getLogger("plog")

@log_call()
def _span_key(span: str) -> datetime:
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
    return {day: tidy_day(node) for day, node in sorted(data.items())}