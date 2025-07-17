from datetime import date, datetime, timedelta

def date_vars() -> dict:
    """
    Return a dictionary of template variables for date injection.
    Keys are token placeholders, values are formatted date strings.
    """
    today = date.today()

    # ISO week starts on Monday = 1
    week_start = today - timedelta(days=today.isoweekday() - 1)
    week_end   = week_start + timedelta(days=6)

    return {
        '{{DATE_TODAY}}': date.today().strftime('%d-%m-%Y'),
        '{{DATE_WEEK}}': date.today().strftime('%G-W%V'),
        '{{DATE_WEEK_RANGE}}' : f'{week_start:%d %b} → {week_end:%d %b}',  # 14 Jul → 20  Jul
        '{{DATE_MONTH}}': date.today().strftime('%B %Y'),
        '{{LAST_UPDATED}}': datetime.now().strftime('%d-%m-%Y %H:%M'),
    }

def anchored_date_lines() -> dict:
    """
    Return a dictionary mapping HTML anchor comments (e.g. <!--DATE-TODAY-->) 
    to their updated <sub><em>...</em></sub> values.
    These are used to update date blocks in-place, without relying on {{TAGS}}.
    templates:
    1. <!--DATE-LAST_UPDATED-->
    2. <!--DATE-TODAY-->
    3. <!--DATE-WEEK-->
    4. <!--DATE-MONTH-->
    """
    today = date.today()
    week_start = today - timedelta(days=today.isoweekday() - 1)
    week_end   = week_start + timedelta(days=6)

    return {
        'DATE-LAST_UPDATED': f'<sub><em>Last updated: {datetime.now().strftime("%d-%m-%Y %H:%M")}</em></sub>',
        'DATE-TODAY': f'<sub><em>{today.strftime("%d-%m-%Y")}</em></sub>',
        'DATE-WEEK': f'<sub><em>{today.strftime("%G-W%V")}: {week_start:%d %b} → {week_end:%d %b}</em></sub>',
        'DATE-MONTH': f'<sub><em>{today.strftime("%B %Y")}</em></sub>',
    }
