import logging
from logging import getLogger
import sys

import click
import yaml
from questionary import checkbox
from rich import print
from rich.console import Console
from rich.traceback import Traceback

from purrgress.plog import core, log_setup
from purrgress.plog.cleanup import tidy_month
from purrgress.plog.config import CFG
from purrgress.plog.core import DRAFT_FILE
from purrgress.plog.reports import make_heatmap
from purrgress.utils import log_call
from purrgress.utils.date import now, today_iso
from purrgress.utils.path import resolve_pathish
from purrgress.utils.yaml_tools import dump_no_wrap

log = getLogger("plog")

@click.group(help="Life-log commands")
@click.option("--tz", metavar="TZ", default=None,
              help="IANA timezone (e.g. Europe/Paris). Overrides PLOG_TZ env.")
@click.option("-v", "--verbose", count=True, help="-v = INFO, -vv = DEBUG")
@click.pass_context
def log_group(ctx, tz: str | None = None, verbose: int = 0) -> None:
    """
    Root CLI group for life-log commands.

    Sets up logging and shared context:

    - Determines log level from the `-v/--verbose` count.
      - 0 (default): WARNING
      - 1 (-v): INFO
      - 2+ (-vv): DEBUG
    - Saves the chosen timezone (`tz`) and the logger in `ctx.obj`
      for use by all subcommands without extra parameters.

    Args:
        ctx (click.Context): Click context object.
        tz (str|None): Timezone string (IANA format) or None.
        verbose (int): Verbosity level from `-v` flags.
    """
    level = "WARNING"
    if verbose == 1:
        level = "INFO"
    elif verbose >= 2:
        level = "DEBUG"

    log.debug("[log_group] Setting log level to %s", level)
    log.debug("[log_group] Setting tz to %s", tz)

    ctx.obj = {"tz": tz}
    ctx.obj["log"] = logger = log_setup.init(level)
    log.debug("[log_group] Logger initialized and stored in context.")

@log_call()
def _tz(ctx) -> (str | None):
    """
    Get the timezone stored in the Click context (`ctx.obj`).

    Args:
        ctx (click.Context): Click context object.

    Returns:
        str|None: Timezone string if set, otherwise None.
    """
    tz = ctx.obj.get("tz") if ctx.obj else None
    return tz

# ----------- start / stop ----------
@log_group.command()
@log_call(logging.INFO)
@click.argument("task")
@click.option("-t", "--tags",  multiple=True, help="Repeatable tag option")
@click.option("-m", "--moods", multiple=True, help="Repeatable mood option")
@click.pass_context
def start(ctx, task: str, tags: tuple[str], moods: tuple[str]) -> None:
    """
    Begin a study/work span. If you omit --tags or --moods,
    an interactive checklist appears (arrow keys + space).

    Args:
        ctx (click.Context): Click context object.
        task (str): The task name.
        tags (tuple[str]): The tag names (repeatable option).
        moods (tuple[str]): The mood names (repeatable option).
    """
    try:
        cfg = CFG()
    except Exception as e:
        log.error("[start] Failed to load config file: %s", e)
        raise
    else:
        if not tags:
            tag_choices = [
                {"name": k, "checked": False} for k in cfg["tags"].keys()
            ]
            tags = checkbox(
                "Select tag(s)  (space = toggle, enter = accept)",
                choices=tag_choices,
            ).unsafe_ask()

        if not moods:
            mood_choices = [
                {"name": k, "checked": False} for k in cfg["moods"].keys()
            ]
            moods = checkbox(
                "Select mood(s) (space = toggle, enter = accept)",
                choices=mood_choices,
            ).unsafe_ask()

        tags  = list(tags)
        moods = list(moods)

        sess = core.start_session(task, tags, moods, tz=_tz(ctx))
        print(f"[bold green]⏳  Started[/bold green] {task} at {sess['start']}")

@log_group.command()
@log_call(logging.INFO)
@click.pass_context
def stop(ctx) -> None:
    """End current span."""
    sess = core.stop_session(tz=_tz(ctx))
    print(f"[bold cyan]✔ Stopped[/] {sess['task']} {sess['start']}-{sess['end']}")

# ----------- status ----------
@log_group.command()
@log_call(logging.INFO)
@click.pass_context
def status(ctx) -> None:
    """
    Show current status: open draft (if any) and today's total logged minutes.
    """
    tz = _tz(ctx)
    iso = today_iso(tz)

    try:
        if DRAFT_FILE.exists():
            draft = yaml.safe_load(DRAFT_FILE.read_text())
            print(f"[yellow]OPEN[/] {draft['task']} since {draft['start']}")
            total = core.minutes_for_day(iso)
            h, m = divmod(total, 60)
            click.echo(f"Today so far: {h}h{m:02d}m")
        else:
            print("[cyan]No open session![/cyan]")
    except Exception as e:
        log.error("[status] Failed to read draft file: %s", e)
        raise
    
# ----------- wake / sleep ----------
@log_group.command()
@log_call(logging.INFO)
@click.argument("time_hm")
@click.pass_context
def wake(ctx, time_hm) -> None:
    """Record wake-up time (HH:MM, optional +1 for after midnight)."""
    core.set_wake(time_hm, tz=_tz(ctx))
    print(f"[bold green]🌅  Wake[/bold green] set to {time_hm}")

@log_group.command()
@log_call(logging.INFO)
@click.argument("time_hm")
@click.pass_context
def sleep(ctx, time_hm) -> None:
    """Record sleep time (HH:MM, use '+1' suffix if after midnight)."""
    core.set_sleep(time_hm, tz=_tz(ctx))
    print(f"[bold magenta]🌙  Sleep[/bold magenta] set to {time_hm}")
    
@log_group.command()
@log_call(logging.INFO)
@click.option("-d", "--date", metavar="YYYY-MM-DD", 
              help="Date to show status for (YYYY-MM-DD, default: today)")
@click.pass_context
def day(ctx, date: str = None) -> None:
    """
    Show total minutes logged for a given day (default: today).

    Args:
        ctx (click.Context): Click context object.
        date (str, optional): The date in YYYY-MM-DD format (defaults to today in chosen timezone).
    """
    tz = _tz(ctx)
    iso = date if date else today_iso(tz)
    minutes = core.minutes_for_day(iso)
    h, m = divmod(minutes, 60)
    pretty = f"{iso} TOTAL: {minutes} mins, {h}h{m:02d}m"
    print(f"[bold cyan]{pretty}[/bold cyan]")

@log_group.command()
@log_call(logging.INFO)
@click.option("-y", "--year", type=int, default=None, 
              help="Year, default this year")
@click.option("-m", "--month", type=int, default=None, 
              help="Month 1-12, default this month")
def month(year: int, month: int) -> None:
    """
    Sum total minutes for an entire month.

    Args:
        year (int, optional): Year (defaults to current year)
        month (int, optional): Month 1-12 (defaults to current month)

    Example:
        >>> plog month --year 2025 --month 7
        2025-07 total: 149h15m (8955 mins)
    """
    today = now()
    y = year  or today.year
    m = month or today.month
    minutes = core.minutes_for_month(y, m)
    h, mm = divmod(minutes, 60)
    print(f"[bold green]{y}-{m:02} total:[/bold green] {h}h{mm:02d}m ({minutes} mins)")

# ----------- tidy ----------
@log_group.command()
@log_call(logging.INFO)
@click.option("-y","--year",  type=int, default=None, 
              help="Year, default this year")
@click.option("-m", "--month", type=int, default=None,
              help="Month 1-12, default this month")
def tidy(year: int, month: int) -> None:
    """
    Retro-tidy and normalize an entire month's log file in place.
    Cleans up formatting, deduplicates, and normalizes sessions.

    Args:
        year (int, optional): Year (defaults to current year)
        month (int, optional): Month 1-12 (defaults to current month)

    Example:
        >>> plog tidy --year 2025 --month 7
        ✨  Tidied data/2025/07.yaml
    """
    today = now()
    y = year  or today.year
    m = month or today.month
    month_path = resolve_pathish(f"purrgress/data/{y}/{m:02}.yaml")

    try:
        if month_path.exists():
            data = yaml.safe_load(month_path.read_text()) or {}
        else:
            print("[yellow]Nothing to tidy.[/yellow]")
            return
    except Exception as e:
        log.error("[tidy] Failed to read month file %s: %s", month_path, e)
        raise
    
    cleaned = tidy_month(data)

    try:
        month_path.write_text(dump_no_wrap(cleaned))
        print(f"[bold green]✨  Tidied[/bold green] {month_path.relative_to(resolve_pathish('purrgress'))}")
    except Exception as e:
        log.error("[tidy] Failed to write tidied month file %s: %s", month_path, e)
        print("[red]Failed to write tidied file![/red]")
        raise

@log_group.command()
@log_call(logging.INFO)
@click.option("-y", "--year",  type=int, 
              help="Year, default this year")
@click.option("-m", "--month", type=int, 
              help="Month 1-12, default this month")
@click.option("--theme", default="viridis",
              help="Matplotlib colormap (viridis, magma, plasma, turbo, etc.)")
@click.option("--dark/--light", default=False, 
              help="Dark background")
@click.pass_context
def heatmap(ctx, year: int, month: int, theme: str, dark: bool):
    """
    Generate an hour-by-day heat-map PNG.

    Args:
        ctx (click.Context): Click context object.
        year (int, optional): Year (defaults to current year)
        month (int, optional): Month 1-12 (defaults to current month)
        theme (str, optional): Heatmap color theme. Default is 'viridis'.
        dark (bool, optional): Use dark mode. Default is False.
    """
    dt   = now()
    y    = year  or dt.year
    m    = month or dt.month
    path = make_heatmap(y, m, theme=theme, dark=dark, tz=_tz(ctx))
    print(f"🖼  [bold green]Heat-map saved to[/bold green] {path}")

@log_group.result_callback()
def cli_finished(result, **kwargs):
    pass

def main():
    try:
        log_group()
    except Exception as exc:
        console = Console()
        console.print("[bold red]Uncaught error - see details below:[/bold red]")
        console.print(Traceback.from_exception(type(exc), exc, exc.__traceback__, show_locals=True))
        sys.exit(1)

if __name__ == "__main__":
    main()