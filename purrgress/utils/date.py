import os
from datetime import date, datetime, timedelta
from logging import getLogger
from zoneinfo import ZoneInfo

from purrgress.utils import log_call

log = getLogger("plog")

def date_vars() -> dict:
    today = date.today()

    week_start = today - timedelta(days=today.isoweekday() - 1)
    week_end   = week_start + timedelta(days=6)

    return {
        '{{DATE_TODAY}}': date.today().strftime('%d-%m-%Y'),
        '{{DATE_WEEK}}': date.today().strftime('%G-W%V'),
        '{{DATE_WEEK_RANGE}}' : f'{week_start:%d %b} → {week_end:%d %b}',
        '{{DATE_MONTH}}': date.today().strftime('%B %Y'),
        '{{LAST_UPDATED}}': datetime.now().strftime('%d-%m-%Y %H:%M'),
    }

def anchored_date_lines() -> dict:
    today = date.today()
    week_start = today - timedelta(days=today.isoweekday() - 1)
    week_end   = week_start + timedelta(days=6)

    return {
        'DATE-LAST_UPDATED': f'<sub><em>Last updated: {datetime.now().strftime("%d-%m-%Y %H:%M")}</em></sub>',
        'DATE-TODAY': f'<sub><em>{today.strftime("%d-%m-%Y")}</em></sub>',
        'DATE-WEEK': f'<sub><em>{today.strftime("%G-W%V")}: {week_start:%d %b} → {week_end:%d %b}</em></sub>',
        'DATE-MONTH': f'<sub><em>{today.strftime("%B %Y")}</em></sub>',
    }

@log_call()
def _choose_tz(tz_arg: str | None = None) -> datetime.tzinfo:
    """
    Selects the timezone to use, in this order:
    1. Explicit tz_arg provided by user
    2. PLOG_TZ environment variable
    3. System default timezone

    Args:
        tz_arg (str | None): Explicit timezone name (e.g., 'Asia/Shanghai').

    Returns:
        tzinfo: The chosen timezone object.
    """
    if tz_arg:
        log.debug("[_choose_tz] Use explicit timezone: %s", tz_arg)
        return ZoneInfo(tz_arg)
    env = os.getenv("PLOG_TZ")
    if env:
        log.debug("[_choose_tz] Use environment timezone: %s", env)
        return ZoneInfo(env)
    sys_tz = datetime.now().astimezone().tzinfo
    return sys_tz

@log_call()
def now(tz_arg: str | None = None) -> datetime:
    """Timezone-aware 'now' as datetime."""
    tz = _choose_tz(tz_arg)
    return datetime.now(tz=tz)

@log_call()
def today_iso(tz_arg: str | None = None) -> str:
    """Return YYYY-MM-DD of *today* in chosen tz."""
    today = now(tz_arg).date().isoformat()
    return today

@log_call()
def minutes_between(start_hm: str, end_hm: str) -> int:
    """
    Inclusive minutes between HH:MM strings, rolling past midnight if needed.
    """
    try:
        s = datetime.strptime(start_hm, "%H:%M")
        e = datetime.strptime(end_hm, "%H:%M")
    except ValueError as ex:
        log.error("[minutes_between] Time data must match format '%%H:%%M': %s", ex)
        raise
    if e < s:
        log.debug("[minutes_between] end_hm < start_hm; rolling over midnight")
        e += timedelta(days=1)
    mins = int((e - s).total_seconds() // 60)
    return mins