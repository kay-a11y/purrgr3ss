import click
import yaml
from rich import print
from purrgress.plog.core import (
    start_session, stop_session, calc_today_total, set_wake, set_sleep
)

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
    sess = start_session(task, list(tags), tz=_tz(ctx))
    print(f"[bold green]⏳ Started[/] {task} at {sess['start']}")

@log_group.command()
@click.pass_context
def stop(ctx):
    sess = stop_session(tz=_tz(ctx))
    print(f"[bold cyan]✔ Stopped[/] {sess['task']} {sess['start']}-{sess['end']}")

# ----------- status ----------
@log_group.command()
def status():
    from purrgress.plog.core import DRAFT_FILE
    if DRAFT_FILE.exists():
        draft = yaml.safe_load(DRAFT_FILE.read_text())
        print(f"[yellow]OPEN[/] {draft['task']} since {draft['start']}")
    total = calc_today_total()
    h, m = divmod(total, 60)
    click.echo(f"Today so far: {h}h{m:02d}m")

# ----------- wake / sleep ----------
@log_group.command()
@click.argument("time_hm")
@click.pass_context
def wake(ctx, time_hm):
    set_wake(time_hm, tz=_tz(ctx))
    print(f"[bold green]🌅 Wake[/bold green] set to {time_hm}")

@log_group.command()
@click.argument("time_hm")
@click.pass_context
def sleep(ctx, time_hm):
    set_sleep(time_hm, tz=_tz(ctx))
    print(f"[bold magenta]🌙 Sleep[/bold magenta] set to {time_hm}")
