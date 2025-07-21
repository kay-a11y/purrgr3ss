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
        key = (sess["task"], tuple(sess["tags"]))
        bucket = merged.setdefault(key, {"spans": [], "moods": set()})
        bucket["spans"].extend(sess["spans"])
        bucket["moods"].update(sess.get("moods", []))

    node["sessions"] = [
        dict(
            task=k[0],
            tags=list(k[1]),
            spans=sorted(set(v["spans"]), key=_span_key),
            moods=sorted(v["moods"]) if v["moods"] else []
        )
        for k, v in merged.items()
    ]

    node["sessions"].sort(key=lambda s: _span_key(s["spans"][0]))

    ordered = {k: node[k] for k in ("wake", "sleep") if k in node}
    ordered["sessions"] = node["sessions"]
    return ordered


def tidy_month(data: dict) -> dict:
    return {day: tidy_day(node) for day, node in sorted(data.items())}
