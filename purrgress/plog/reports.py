import logging
from datetime import datetime, timedelta
from logging import getLogger
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import yaml
from rich import print

from purrgress.plog.cleanup import tidy_month
from purrgress.utils import log_call
from purrgress.utils.date import minutes_between, now, today_iso
from purrgress.utils.path import resolve_pathish

log = getLogger("plog")

# ────────────────────── study log ───────────────────────────
@log_call()
def _month_yaml(year: int, month: int) -> dict:
    """
    Load the month yaml file.

    Args:
        year (int): Year as four digits, e.g., 2025.
        month (int): Month as integer, 1-12.

    Returns:
        dict: Tidied month file 
    """
    src = resolve_pathish(f"purrgress/data/{year}/{month:02}.yaml")
    try:
        if not src.exists():
            raise FileNotFoundError(f"No data for {year}-{month:02}")
        data = yaml.safe_load(src.read_text()) or {}
    except FileNotFoundError as e:
        log.error("No data for %d-%02d: %s", year, month, e)
        raise
    except Exception as e:
        log.error("Failed to load data file %s: %s", src, e)
        raise

    return tidy_month(data)

@log_call()
def _empty_df(year: int, month: int) -> pd.DataFrame:
    """
    Create an empty DataFrame for hourly data for the given month.

    Rows = hours 0-23, columns = days 1-N (N = number of days in month).
    Each cell is initialized to zero.

    Args:
        year (int): Year as four digits, e.g., 2025.
        month (int): Month as integer, 1-12.

    Returns:
        pd.DataFrame: DataFrame with shape (24, days_in_month) for storing hourly values.
    """
    first = datetime(year, month, 1)
    if month == 12:
        next_month = datetime(year + 1, 1, 1)
    else:
        next_month = datetime(year, month + 1, 1)
    days = (next_month - first).days

    return pd.DataFrame(
        0,
        index=range(24),
        columns=[day for day in range(1, days + 1)]
    )

@log_call()
def _fill_df(df: pd.DataFrame, month_data: dict) -> pd.DataFrame:
    """
    Populate an hourly DataFrame with minute-level session data.

    For each session in each day's data, every minute between
    span start and end is counted into the appropriate [hour, day] cell.

    - Handles multiple sessions and spans per day.
    - Spans that cross midnight are split across days/hours.
    - Ignores sessions with empty or malformed 'spans' lists.

    Args:
        df (pd.DataFrame): DataFrame to fill (hours as rows, days as columns).
        month_data (dict): Log data loaded from YAML for the target month.

    Returns:
        pd.DataFrame: The input DataFrame with cells incremented for every session minute tracked.

    Example:
        After calling _fill_df, df[hour][day] contains the number of minutes
        logged at that hour on that day.
    """
    for day_iso, node in month_data.items():
        day_num = int(day_iso.split("-")[2])
        day_col = df.columns.get_loc(day_num)

        for sess in node.get("sessions", []):
            for span in (sess.get("spans") or []):
                if not span or "-" not in span or ":" not in span:
                    continue

                try:
                    start_str, end_str = span.split("-")
                except ValueError:
                    continue

                if not start_str or not end_str or ":" not in start_str or ":" not in end_str:
                    continue

                try:
                    sdt = datetime.strptime(start_str, "%H:%M")
                    edt = datetime.strptime(end_str,   "%H:%M")
                except ValueError:
                    continue

                if edt < sdt:
                    edt += timedelta(days=1)

                cur = sdt
                while cur < edt:
                    hour = cur.hour
                    day_offset = (cur.date() - sdt.date()).days
                    col_day    = day_num + day_offset
                    if col_day in df.columns:
                        df.iat[hour, df.columns.get_loc(col_day)] += 1
                    cur += timedelta(minutes=1)

    return df

# ────────────────────────────────────────────────────────────
@log_call(logging.INFO)
def make_heatmap(year: int, month: int, *, theme: str = "viridis", dark: bool = False, tz: str | None = None) -> Path:
    """
    Generate and save an hour-by-day study heatmap as a PNG.

    The output image shows how many minutes were logged per hour for each day of the month.
    • `theme`: Any valid Matplotlib colormap (e.g., 'viridis', 'magma', 'turbo', ...)
    • `dark`:  If True, generates a dark mode plot with white ticks and labels.
    • `tz`:    Optional timezone (unused in current version; for future extension).

    Args:
        year (int): Year, e.g. 2025.
        month (int): Month, 1-12.
        theme (str, optional): Heatmap color theme. Default is 'viridis'.
        dark (bool, optional): Use dark mode. Default is False.
        tz (str | None, optional): Timezone name (future use). Default is None.

    Returns:
        Path: Filesystem path to the generated PNG file.

    Raises:
        Exception: If data loading or plotting fails.

    Example:
        >>> make_heatmap(2025, 7, theme="magma", dark=True)
        Path('purrgress/visuals/2025/07_heatmap_magma_dark.png')
    """
    try:
        data = _month_yaml(year, month)
        df   = _fill_df(_empty_df(year, month), data)
    except Exception as e:
        log.error("[make_heatmap] Failed to load/fill month data: %s", e)
        raise

    try:
        out_dir = resolve_pathish(f"purrgress/visuals/{year}")
        out_dir.mkdir(parents=True, exist_ok=True)
        suffix  = "dark" if dark else "light"
        out_png = out_dir / f"{month:02}_heatmap_{theme}_{suffix}.png"
    except Exception as e:
        log.error("[make_heatmap] Failed to prepare output directory: %s", e)
        raise

    try:
        fig, ax = plt.subplots(figsize=(12, 6))

        if dark:
            bg = "#121212"
            fig.patch.set_facecolor(bg)
            ax.set_facecolor(bg)
            ax.tick_params(colors="white")
            ax.xaxis.label.set_color("white")
            ax.yaxis.label.set_color("white")
            ax.title.set_color("white")

        img = ax.imshow(df, aspect="auto", origin="lower", cmap=theme)
        ax.set_yticks(range(24))
        ax.set_yticklabels(range(24))
        ax.set_xticks(range(len(df.columns)))
        ax.set_xticklabels(df.columns)
        ax.set_xlabel("Day")
        ax.set_ylabel("Hour")
        ax.set_title(f"Study Heat-map {year}-{month:02}")

        cbar = plt.colorbar(img, label="Minutes studied")
        if dark:
            cbar.ax.yaxis.set_tick_params(color="white")
            plt.setp(cbar.ax.get_yticklabels(), color="white")

        plt.tight_layout()
        plt.savefig(out_png, dpi=150)
        plt.close()
    except Exception as e:
        log.error("[make_heatmap] Failed during plotting/saving: %s", e)
        raise

    return out_png