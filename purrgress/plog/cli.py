from rich import print
from rich.console import Console
from rich.traceback import Traceback
from questionary import checkbox
from purrgress.plog import core
from purrgress.plog import log_setup
from purrgress.plog.config import CFG
from purrgress.plog.cleanup import tidy_month
from purrgress.utils.date import now, today_iso
from purrgress.utils.path import resolve_pathish
from purrgress.plog.reports import make_heatmap
from purrgress.utils.yaml_tools import dump_no_wrap
import click, yaml, sys

@click.group(help="Life-log commands")
@click.option("--tz", metavar="TZ", default=None,
              help="IANA timezone (e.g. Europe/Paris). Overrides PLOG_TZ env.")
@click.option("-v", "--verbose", count=True, help="-v = INFO, -vv = DEBUG")
@click.pass_context
def log_group(ctx, tz, verbose):
    level = "WARNING"
    if verbose == 1:
        level = "INFO"
    elif verbose >= 2:
        level = "DEBUG"

    ctx.obj = {"tz": tz}
    ctx.obj["log"] = logger = log_setup.init(level)

# ----------- start / stop ----------
@log_group.command()
@click.argument("task")
@click.option("-t", "--tags",  multiple=True, help="Repeatable tag option")
@click.option("-m", "--moods", multiple=True, help="Repeatable mood option")
@click.pass_context
def start(ctx, task, tags, moods):
    cfg = CFG()

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
    print(f"[bold green]⏳ Started[/bold green] {task} at {sess['start']}")

@log_group.command()
@click.pass_context
def stop(ctx):
    sess = core.stop_session(tz=_tz(ctx))
    print(f"[bold cyan]✔ Stopped[/] {sess['task']} {sess['start']}-{sess['end']}")

# ----------- status ----------
@log_group.command()
def status():
    from purrgress.plog.core import DRAFT_FILE
    if DRAFT_FILE.exists():
        draft = yaml.safe_load(DRAFT_FILE.read_text())
        print(f"[yellow]OPEN[/] {draft['task']} since {draft['start']}")
    total = core.calc_today_total()
    h, m = divmod(total, 60)
    click.echo(f"Today so far: {h}h{m:02d}m")

# ----------- wake / sleep ----------
@log_group.command()
@click.argument("time_hm")
@click.pass_context
def wake(ctx, time_hm):
    core.set_wake(time_hm, tz=_tz(ctx))
    print(f"[bold green]🌅 Wake[/bold green] set to {time_hm}")

@log_group.command()
@click.argument("time_hm")
@click.pass_context
def sleep(ctx, time_hm):
    core.set_sleep(time_hm, tz=_tz(ctx))
    print(f"[bold magenta]🌙 Sleep[/bold magenta] set to {time_hm}")
    
# ----------- day / month total export ----------
@log_group.command()
@click.pass_context
def day(ctx):
    tz = _tz(ctx)
    iso = today_iso(tz)
    minutes = core.minutes_for_day(iso)
    h, m = divmod(minutes, 60)
    pretty = f"{iso} TOTAL: {minutes} mins, {h}h{m:02d}m"
    print(f"[bold cyan]{pretty}[/bold cyan]")

@log_group.command()
@click.option("--year",  type=int, default=None, 
              help="Year, default this year")
@click.option("--month", type=int, default=None, 
              help="Month 1-12, default this month")
def month(year, month):
    today = now()
    y = year  or today.year
    m = month or today.month
    minutes = core.minutes_for_month(y, m)
    h, mm = divmod(minutes, 60)
    print(f"[bold green]{y}-{m:02} total:[/bold green] {h}h{mm:02d}m ({minutes} mins)")

# ----------- tidy ----------
@log_group.command()
@click.option("--year",  type=int, default=None)
@click.option("--month", type=int, default=None)
def tidy(year, month):
    today = now()
    y = year  or today.year
    m = month or today.month
    month_path = resolve_pathish(f"purrgress/data/{y}/{m:02}.yaml")
    if not month_path.exists():
        click.echo("Nothing to tidy.")
        return
    data = yaml.safe_load(month_path.read_text()) or {}
    cleaned = tidy_month(data)
    month_path.write_text(dump_no_wrap(cleaned))
    click.echo(f"✨ Tidied {month_path.relative_to(resolve_pathish('purrgress'))}")


# ----------- heatmap ----------
@log_group.command()
@click.option("--year",  type=int, 
              help="Year (default: this year)")
@click.option("--month", type=int, 
              help="Month 1-12 (default: this month)")
@click.option("--theme", default="viridis",
              help="Matplotlib colormap (viridis, magma, plasma, turbo, etc.)")
@click.option("--dark/--light", default=False, 
              help="Dark background")
@click.pass_context
def heatmap(ctx, year, month, theme, dark):
    """Generate an hour-by-day heat-map PNG."""
    dt   = now()
    y    = year  or dt.year
    m    = month or dt.month
    path = make_heatmap(y, m, theme=theme, dark=dark, tz=_tz(ctx))
    print(f"🖼  Heat-map saved to {path}")

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