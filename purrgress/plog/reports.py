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

def _fill_df(df: pd.DataFrame, month_data: dict):
    for day_iso, node in month_data.items():
        day = int(day_iso.split("-")[2])
        col = df.columns.get_loc(day)
        for sess in node.get("sessions", []):
            for span in sess["spans"]:
                start, end = span.split("-")
                sdt = datetime.strptime(start, "%H:%M")
                edt = datetime.strptime(end, "%H:%M")
                if edt < sdt:
                    edt += timedelta(days=1)
                cur = sdt
                while cur < edt:
                    hour = cur.hour
                    df.iat[hour, col] += 1
                    cur += timedelta(minutes=1)
    return df

# ────────────────────────────────────────────────────────────
def make_heatmap(year: int, month: int, *, theme: str = "viridis", tz=None) -> Path:
    data  = _month_yaml(year, month)
    df    = _fill_df(_empty_df(year, month), data)

    out_dir = Path(resolve_pathish(f"purrgress/visuals/{year}"))
    out_dir.mkdir(parents=True, exist_ok=True)
    out_png = out_dir / f"{month:02}_heatmap_{theme}.png"

    plt.figure(figsize=(12, 6))
    plt.imshow(df, aspect="auto", origin="lower", cmap=theme)
    plt.yticks(range(24), range(24))
    plt.xticks(range(len(df.columns)), df.columns)
    plt.xlabel("Day")
    plt.ylabel("Hour")
    plt.title(f"Study Heat-map {year}-{month:02}")
    plt.colorbar(label="Minutes")
    plt.tight_layout()
    plt.savefig(out_png, dpi=150)
    plt.close()

    return out_png
