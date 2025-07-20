from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo 
import os

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

def _choose_tz(tz_arg: str | None = None):
    if tz_arg:  
        return ZoneInfo(tz_arg)
    env = os.getenv("PLOG_TZ")  
    if env:
        return ZoneInfo(env)
    return datetime.now().astimezone().tzinfo

def now(tz_arg: str | None = None):
    return datetime.now(tz=_choose_tz(tz_arg))

def today_iso(tz_arg: str | None = None):
    return now(tz_arg).date().isoformat()

def minutes_between(start_hm: str, end_hm: str) -> int:
    s = datetime.strptime(start_hm, "%H:%M")
    e = datetime.strptime(end_hm, "%H:%M")
    if e < s:
        e += timedelta(days=1)
    return int((e - s).total_seconds() // 60)

