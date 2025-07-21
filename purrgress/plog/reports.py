from pathlib import Path
import yaml, pandas as pd, matplotlib.pyplot as plt
from datetime import datetime, timedelta
from purrgress.utils.path import resolve_pathish
from purrgress.utils.date import minutes_between, today_iso, now
from purrgress.plog.cleanup import tidy_month 

def _month_yaml(year: int, month: int) -> dict:
    src = Path(resolve_pathish(f"purrgress/data/{year}/{month:02}.yaml"))
    if not src.exists():
        raise FileNotFoundError(f"No data for {year}-{month:02}")
    data = yaml.safe_load(src.read_text()) or {}
    return tidy_month(data)

def _empty_df(year: int, month: int) -> pd.DataFrame:
    first = datetime(year, month, 1)
    if month == 12:
        next_month = datetime(year + 1, 1, 1)
    else:
        next_month = datetime(year, month + 1, 1)
    days = (next_month - first).days
    return pd.DataFrame(
        0,
        index=range(24),  
        columns=[d + 1 for d in range(days)]
    )

def _fill_df(df: pd.DataFrame, month_data: dict) -> pd.DataFrame:
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
                    col_day   = day_num + day_offset
                    if col_day in df.columns:
                        df.iat[hour, df.columns.get_loc(col_day)] += 1
                    cur += timedelta(minutes=1)

    return df

# ────────────────────────────────────────────────────────────
def make_heatmap(year: int, month: int, *, theme: str = "viridis", dark: bool = False, tz=None) -> Path:
    data  = _month_yaml(year, month)
    df    = _fill_df(_empty_df(year, month), data)

    out_dir = Path(resolve_pathish(f"purrgress/visuals/{year}"))
    out_dir.mkdir(parents=True, exist_ok=True)
    suffix  = "dark" if dark else "light"
    out_png = out_dir / f"{month:02}_heatmap_{theme}_{suffix}.png"

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

    return out_png
