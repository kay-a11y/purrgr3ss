from copy import deepcopy
from datetime import datetime

def _span_key(span: str) -> datetime:
    return datetime.strptime(span.split("-")[0], "%H:%M")

def tidy_day(node: dict) -> dict:
    node = deepcopy(node)
    sessions = node.get("sessions", [])

    for sess in sessions:
        sess.setdefault("task", "")
        sess.setdefault("tags", [])
        sess.setdefault("moods", [])
        sess.setdefault("spans", [])

    for sess in sessions:
        spans = sess.get("spans") or []
        sess["spans"] = sorted(set(spans), key=_span_key) if spans else []

    merged = {}
    for sess in sessions:
        key = (sess["task"], tuple(sess["tags"]))
        bucket = merged.setdefault(key, {"spans": [], "moods": set()})
        bucket["spans"].extend(sess["spans"])
        bucket["moods"].update(sess.get("moods", []))

    clean_sessions = []
    for (task, tags), payload in merged.items():
        spans = sorted(set(payload["spans"]), key=_span_key)
        moods = sorted(payload["moods"]) if payload["moods"] else []
        clean_sessions.append(
            {"task": task, "tags": list(tags), "moods": moods, "spans": spans}
        )

    def first_span_dt(s):
        return _span_key(s["spans"][0]) if s["spans"] else datetime.max
    clean_sessions.sort(key=first_span_dt)

    ordered = {}
    for k in ("wake", "sleep"):
        if k in node:
            ordered[k] = node[k]
    ordered["sessions"] = clean_sessions
    return ordered

def tidy_month(data: dict) -> dict:
    return {day: tidy_day(node) for day, node in sorted(data.items())}
