from logging import getLogger
from pathlib import Path
from purrgress.plog.cleanup import tidy_month
from purrgress.utils import log_call
from purrgress.utils.date import now, today_iso, minutes_between
from purrgress.utils.path import resolve_pathish
from purrgress.utils.yaml_tools import dump_no_wrap
import yaml

DATA_ROOT = resolve_pathish("purrgress/data")
DRAFT_FILE = DATA_ROOT / ".draft.yaml"
log = getLogger("plog")

@log_call()
def _month_file(day_iso: str) -> Path:
    try:
        y, m, _ = day_iso.split("-")
        p = DATA_ROOT / f"{y}/{m}.yaml"
        log.debug("[_month_file] Month file path resolved: %s", p)
        p.parent.mkdir(parents=True, exist_ok=True)
        return p
    except Exception as e:
        log.error("[_month_file] Failed to create month file path for %s: %s", day_iso, e)
        raise

@log_call()
def _write_month(path: Path, data: dict) -> None:
    try:
        log.debug("[_write_month] Cleaning data...")
        clean = tidy_month(data)
    except Exception as e:
        log.error("[_write_month] Error cleaning data: %s", e)
        raise

    try:
        log.debug("[_write_month] Writing cleaned data to file...")
        path.write_text(dump_no_wrap(clean))
        log.debug("[_write_month] Data written successfully.")
    except Exception as e:
        log.error("[_write_month] Failed to write to file %s: %s", path, e)
        raise

# ---------- Open/close session helpers ----------
@log_call()
def start_session(task: str, tags: list[str], moods: list[str], *, tz: str | None = None) -> dict:
    if DRAFT_FILE.exists():
        raise RuntimeError("A session is already running. Run `plog stop` to stop it first.")

    draft = {
        "date": today_iso(tz),
        "task": task,
        "tags": tags,
        "moods": moods,
        "start": now(tz).strftime("%H:%M"),
    }

    try:
        log.debug("[start_session] Draft file path resolved: %s", DRAFT_FILE)
        DRAFT_FILE.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        log.error("[start_session] Failed to create draft file path for %s: %s", DRAFT_FILE, e)
        raise
    
    try:
        DRAFT_FILE.write_text(yaml.dump(draft))
    except Exception as e:
        log.error("[start_session] Failed to write to file %s: %s", DRAFT_FILE, e)
        raise

    log.info("[start_session] Draft saved to %s", DRAFT_FILE)
    return draft

@log_call()
def stop_session(*, tz: str | None = None) -> dict:
    if not DRAFT_FILE.exists():
        log.error("[stop_session] No open session to stop.")
        raise RuntimeError("No open session.")
    
    try:
        draft = yaml.safe_load(DRAFT_FILE.read_text()) or {}
    except Exception as e:
        log.error("[stop_session] Failed to read draft file: %s", e)
        raise
    draft["end"] = now(tz).strftime("%H:%M")

    try:
        _store_span(draft)
        DRAFT_FILE.unlink()
        log.info("[stop_session] Session stored and draft file deleted.")
    except Exception as e:
        log.error("[stop_session] Error storing session or deleting draft: %s", e)
        raise
    return draft

@log_call()
def _store_span(draft: dict, *, tz: str | None = None) -> None:
    day_iso = draft.get("date") or today_iso(tz)

    try:
        month_path = _month_file(day_iso)
    except Exception as e:
        log.error("[_store_span] Failed to resolve month path for day %s: %s", day_iso, e)
        raise

    try:
        if month_path.exists():
            data = yaml.safe_load(month_path.read_text())
        else:
            data = {}
    except Exception as e:
        log.error("[_store_span] Failed to read month file %s: %s", month_path, e)
        raise

    node = data.setdefault(day_iso, {"sessions": []})
    node["sessions"].append(
        dict(
            task=draft["task"],
            tags=draft.get("tags", []),
            moods=draft.get("moods", []), 
            spans=[f'{draft["start"]}-{draft["end"]}'],
        )
    )
    log.info("[_store_span] Appended session to day %s in file %s", day_iso, month_path)

    try:
        _write_month(month_path, data)
        log.info("[_store_span] Month file updated successfully.")
    except Exception as e:
        log.error("[_store_span] Failed to write updated month file %s: %s", month_path, e)
        raise

# ---------- Wake/sleep session helpers ----------
def _store_key(key: str, value: str, *, tz: str | None = None):
    day_iso = today_iso(tz)
    month_path = _month_file(day_iso)
    data = yaml.safe_load(month_path.read_text()) if month_path.exists() else {}
    node = data.setdefault(day_iso, {"sessions": []})
    node[key] = value
    _write_month(month_path, data)

def set_wake(time_hm: str, *, tz: str | None = None):
    _store_key("wake", time_hm, tz=tz)

def set_sleep(time_hm: str, *, tz: str | None = None):
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

# ---------- Aggregates ----------
def minutes_for_day(day_iso: str) -> int:
    node = load_day(day_iso)
    total = 0
    for sess in node.get("sessions", []):
        for span in sess["spans"]:
            s, e = span.split("-")
            total += minutes_between(s, e)
    return total

def minutes_for_month(year: int, month: int) -> int:
    month_path = DATA_ROOT / f"{year}/{month:02}.yaml"
    if not month_path.exists():
        return 0
    data = yaml.safe_load(month_path.read_text()) or {}
    return sum(minutes_for_day(day) for day in data)
