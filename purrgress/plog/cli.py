import click
import yaml
from rich import print
from purrgress.plog import core
from purrgress.plog.cleanup import tidy_month
from purrgress.utils.date import now, today_iso
from purrgress.utils.path import resolve_pathish

@click.group(help="Life-log commands")
@click.option("--tz", metavar="TZ", default=None,
              help="IANA timezone (e.g. Europe/Paris). Overrides PLOG_TZ env.")
@click.pass_context
def log_group(ctx, tz):
    ctx.obj = {"tz": tz}

def _tz(ctx):
    return ctx.obj.get("tz") if ctx.obj else None

# ----------- start / stop ----------
@log_group.command()
@click.argument("task")
@click.option("-t", "--tags", multiple=True)
@click.pass_context
def start(ctx, task, tags):
    sess = core.start_session(task, list(tags), tz=_tz(ctx))
    print(f"[bold green]⏳ Started[/] {task} at {sess['start']}")

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
    month_path.write_text(yaml.dump(tidy_month(data), sort_keys=False))
    click.echo(f"✨ Tidied {month_path.relative_to(resolve_pathish('purrgress'))}")
