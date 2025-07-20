from copy import deepcopy
from datetime import datetime

def _span_key(span: str) -> datetime:
    return datetime.strptime(span.split("-")[0], "%H:%M")

def tidy_day(node: dict) -> dict:
    node = deepcopy(node)

    for sess in node.get("sessions", []):
        unique = sorted({s for s in sess["spans"]}, key=_span_key)
        sess["spans"] = unique

    merged = {}
    for sess in node.get("sessions", []):
        k = (sess["task"], tuple(sess["tags"]))
        merged.setdefault(k, []).extend(sess["spans"])
    node["sessions"] = [
        dict(task=k[0], tags=list(k[1]), spans=sorted(v, key=_span_key))
        for k, v in merged.items()
    ]

    node["sessions"].sort(key=lambda s: _span_key(s["spans"][0]))

    ordered = {}
    for k in ("wake", "sleep", "sessions"):
        if k in node:
            ordered[k] = node[k]
    return ordered

def tidy_month(data: dict) -> dict:
    return {day: tidy_day(node) for day, node in sorted(data.items())}
