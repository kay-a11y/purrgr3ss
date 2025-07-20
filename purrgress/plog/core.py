from pathlib import Path
import yaml
from purrgress.utils.date import now, today_iso, minutes_between
from purrgress.utils.path import resolve_pathish

DATA_ROOT = resolve_pathish("purrgress/data")
DRAFT_FILE = DATA_ROOT / ".draft.yaml"

def _month_file(day_iso: str) -> Path:
    y, m, _ = day_iso.split("-")
    p = DATA_ROOT / f"{y}/{m}.yaml"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p

# ---------- Open/close session helpers ----------
def start_session(task: str, tags: list[str], *, tz=None):
    if DRAFT_FILE.exists():
        raise RuntimeError("A session is already running. Stop it first.")
    draft = dict(task=task, tags=tags, start=now(tz).strftime("%H:%M"))
    DRAFT_FILE.parent.mkdir(parents=True, exist_ok=True)
    DRAFT_FILE.write_text(yaml.dump(draft))
    return draft

def stop_session(*, tz=None):
    if not DRAFT_FILE.exists():
        raise RuntimeError("No open session.")
    draft = yaml.safe_load(DRAFT_FILE.read_text()) or {}
    draft["end"] = now(tz).strftime("%H:%M")
    _store_span(draft)
    DRAFT_FILE.unlink()
    return draft

def _store_span(draft: dict, *, tz=None):
    day_iso = today_iso(tz)
    month_path = _month_file(day_iso)
    data = yaml.safe_load(month_path.read_text()) if month_path.exists() else {}
    node = data.setdefault(day_iso, {"sessions": []})
    node["sessions"].append(
        dict(task=draft["task"], tags=draft["tags"],
             spans=[f'{draft["start"]}-{draft["end"]}'])
    )
    month_path.write_text(yaml.dump(data, sort_keys=False))

# ---------- Wake/sleep session helpers ----------
def _store_key(key: str, value: str, *, tz=None):
    """
    Set wake: or sleep: for today.  If it already exists, overwrite.
    """
    day_iso = today_iso(tz)
    month_path = _month_file(day_iso)
    data = yaml.safe_load(month_path.read_text()) if month_path.exists() else {}
    node = data.setdefault(day_iso, {"sessions": []})
    node[key] = value
    month_path.write_text(yaml.dump(data, sort_keys=False))

def set_wake(time_hm: str, *, tz=None):
    _store_key("wake", time_hm, tz=tz)

def set_sleep(time_hm: str, *, tz=None):
    _store_key("sleep", time_hm, tz=tz)

# ---------- Utilities ----------
def calc_today_total():
    node = load_day(today_iso())
    total = 0
    for sess in node.get("sessions", []):
        for span in sess["spans"]:
            s, e = span.split("-")
            total += minutes_between(s, e)
    return total  # minutes

def load_day(day_iso: str) -> dict:
    path = _month_file(day_iso)
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text()).get(day_iso, {})

