import logging
from logging import getLogger
from pathlib import Path

import yaml

from purrgress.plog.cleanup import tidy_month
from purrgress.utils import log_call
from purrgress.utils.date import minutes_between, now, today_iso
from purrgress.utils.path import resolve_pathish
from purrgress.utils.yaml_tools import dump_no_wrap

DATA_ROOT = resolve_pathish("purrgress/data")
DRAFT_FILE = DATA_ROOT / ".draft.yaml"
log = getLogger("plog")

@log_call()
def _month_file(day_iso: str) -> Path:
    """
    Generate the path to the month YAML file for a given date.

    Args:
        day_iso (str): Date in YYYY-MM-DD format.

    Returns:
        Path: The Path object to the month's YAML file (e.g. DATA_ROOT/2025/07.yaml).
    """
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
    """
    Clean and write session data to the given month YAML file.

    Args:
        path (Path): Where to write the YAML.
        data (dict): The raw session data to tidy and write.
    """
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
    """
    Start a new session and save draft data to file.

    Args:
        task (str): The task name.
        tags (list[str]): List of tag strings.
        moods (list[str]): List of mood strings.
        tz (str | None): Optional timezone.

    Returns:
        dict: The draft session data saved to file.

    Raises:
        RuntimeError: If a session is already running.
        Exception: On file or directory errors.
    """
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
    """
    Stop the session, write the stop time and remove the draft file.

    Args:
        tz (str | None): Optional timezone.

    Returns:
        dict: The draft session data saved to file.
    """
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
    """
    store the session data from draft to month file

    Args:
        draft (dict): The draft session data saved to file.
        tz (str | None, optional): Optional timezone.
    """
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
@log_call()
def _store_key(key: str, value: str, *, tz: str | None = None):
    """
    Set wake: or sleep: for today.  If it already exists, overwrite.

    Args:
        key (str): The key to set ("wake" or "sleep").
        value (str): The time value in "HH:MM" format.
        tz (str | None, optional): Optional timezone for today.

    Raises:
        Exception: If reading or writing files fails.
    """
    day_iso = today_iso(tz)

    try:
        month_path = _month_file(day_iso)
    except Exception as e:
        log.error("[_store_key] Failed to resolve month path for day %s: %s", day_iso, e)
        raise

    try:
        if month_path.exists():
            data = yaml.safe_load(month_path.read_text())
        else:
            data = {}
    except Exception as e:
        log.error("[_store_key] Failed to read month file %s: %s", month_path, e)
        raise

    node = data.setdefault(day_iso, {"sessions": []})
    node[key] = value

    try:
        _write_month(month_path, data)
        log.info("[_store_key] Month file updated successfully.")
    except Exception as e:
        log.error("[_store_key] Failed to write updated month file %s: %s", month_path, e)
        raise

@log_call()
def set_wake(time_hm: str, *, tz: str | None = None):
    """
    Set today's wake time in "HH:MM" format.

    Args:
        time_hm (str): Wake time as "HH:MM".
        tz (str | None, optional): Optional timezone.
    """
    _store_key("wake", time_hm, tz=tz)

@log_call()
def set_sleep(time_hm: str, *, tz: str | None = None):
    """
    Set today's sleep time in "HH:MM" format.

    Args:
        time_hm (str): Sleep time as "HH:MM".
        tz (str | None, optional): Optional timezone.
    """
    _store_key("sleep", time_hm, tz=tz)

@log_call()
def load_day(day_iso: str) -> dict:
    """
    Load session data for a given date from the YAML log.

    Args:
        day_iso (str): Date in YYYY-MM-DD format.

    Returns:
        dict: Session data for the day (empty dict if not found).
    """
    try:
        month_path = _month_file(day_iso)
    except Exception as e:
        log.error("[load_day] Failed to resolve month path for day %s: %s", day_iso, e)
        raise

    try:
        if month_path.exists():
            month_data = yaml.safe_load(month_path.read_text()) or {}
            return month_data.get(day_iso, {})
        else:
            return {}
    except Exception as e:
        log.error("[load_day] Failed to read month file %s: %s", month_path, e)
        raise

# ---------- Aggregates ----------
@log_call()
def minutes_for_day(day_iso: str) -> int:
    """
    Calculate the total minutes tracked for the specified day (all sessions combined).

    Args:
        day_iso (str): Date in YYYY-MM-DD format.

    Returns:
        int: Total minutes spent (across all sessions and spans).
    """
    node = load_day(day_iso)
    total = 0
    for sess in node.get("sessions", []):
        for span in sess.get("spans", []):
            try:
                s, e = span.split("-")
                total += minutes_between(s, e)
            except Exception as ex:
                log.warning("[minutes_for_day] Failed to parse span '%s' in %s: %s", span, day_iso, ex)
    return total

@log_call()
def minutes_for_month(year: int, month: int) -> int:
    """
    Calculate the total minutes tracked for a given month.

    Args:
        year (int): Year as four digits, e.g., 2025.
        month (int): Month as integer, 1-12.

    Returns:
        int: Total minutes spent (across all days and sessions in the month).
    """
    month_path = DATA_ROOT / f"{year}/{month:02}.yaml"

    try:
        if month_path.exists():
            month_data = yaml.safe_load(month_path.read_text()) or {}
            log.debug("[minutes_for_month] Found %d days in month %04d-%02d", len(month_data), year, month)
            return sum(minutes_for_day(day) for day in month_data)
        else:
            return 0
    except Exception as e:
        log.error("[minutes_for_month] Failed to read month file %s: %s", month_path, e)
        raise
